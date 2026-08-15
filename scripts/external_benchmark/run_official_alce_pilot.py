"""Run a small, reproducible ALCE official-data pilot for the IPM ARL study.

This adapter does not alter the manuscript's frozen v2.2/v2.3 artifacts. It
uses the official ALCE ASQA/QAMPARI records and writes a separate manifest and
ALCE-compatible output for later scoring by ALCE's evaluator.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ALCE_DATA = PROJECT_ROOT / "external" / "github_learned_projects" / "ALCE" / "ALCE-data"
DEFAULT_OUT = PROJECT_ROOT / "data" / "external_benchmarks" / "alce_official_pilot"
sys.path.insert(0, str(PROJECT_ROOT))

from modules.ai_provider import call_provider  # noqa: E402


MODEL = "deepseek-v4-pro"
TEMPERATURE = 0.0
MAX_TOKENS = 24000


def load_json(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def evidence_block(docs: Iterable[Dict[str, Any]], top_k: int) -> str:
    chunks = []
    for idx, doc in enumerate(list(docs)[:top_k], start=1):
        chunks.append(f"[{idx}] {doc.get('title', '')}\n{doc.get('text', '')}")
    return "\n\n".join(chunks)


def call(messages: List[Dict[str, str]], key: str) -> tuple[str, Dict[str, Any] | None]:
    for attempt, budget in enumerate((MAX_TOKENS, 32000), start=1):
        started = time.perf_counter()
        text, usage = call_provider(
            "deepseek",
            key,
            messages,
            model=MODEL,
            max_tokens=budget,
            temperature=TEMPERATURE,
            timeout=180,
        )
        if text and text.strip():
            meta = dict(usage or {})
            meta["latency_ms"] = round((time.perf_counter() - started) * 1000)
            meta["attempt"] = attempt
            meta["max_tokens_requested"] = budget
            return text.strip(), meta
        time.sleep(2)
    raise RuntimeError("DeepSeek returned an empty completion after two attempts")


def base_messages(question: str, docs: str, answer_format: str) -> List[Dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You answer questions only from the supplied evidence. "
                "Every factual sentence must end with one or more source "
                "markers such as [1] or [2][3]. If the evidence is not enough, "
                "say that the evidence is insufficient rather than guessing."
            ),
        },
        {
            "role": "user",
            "content": f"Question:\n{question}\n\nEvidence:\n{docs}\n\n{answer_format}",
        },
    ]


def run_condition(condition: str, question: str, docs: str, answer_format: str, key: str) -> tuple[str, List[Dict[str, Any]]]:
    trace: List[Dict[str, Any]] = []
    draft, usage = call(base_messages(question, docs, answer_format), key)
    trace.append({"role": "generator", "usage": usage})
    if condition == "v0":
        return draft, trace

    if condition == "v1":
        review_prompt = (
            "Review the draft against the question and numbered evidence. "
            "Identify unsupported, contradicted, or uncited claims. Then "
            "rewrite the answer, retaining only evidence-supported claims and "
            "placing citations at the end of each factual sentence.\n\n"
            f"Question:\n{question}\n\nEvidence:\n{docs}\n\nRequired output format:\n{answer_format}\n\nDraft:\n{draft}"
        )
        revised, usage = call([{"role": "user", "content": review_prompt}], key)
        trace.append({"role": "self_critic_reviser", "usage": usage})
        return revised, trace

    if condition == "v2":
        review_prompt = (
            "Act as an independent citation reviewer. For each factual claim "
            "in the draft, classify it as SUPPORTED, PARTIAL, CONTRADICTED, or "
            "INSUFFICIENT using only the numbered evidence. Return a compact "
            "review with claim text and citation numbers. Do not rewrite yet.\n\n"
            f"Question:\n{question}\n\nEvidence:\n{docs}\n\nRequired output format:\n{answer_format}\n\nDraft:\n{draft}"
        )
        review, usage = call([{"role": "user", "content": review_prompt}], key)
        trace.append({"role": "reviewer", "usage": usage})
        revise_prompt = (
            "Revise the draft using the review below. Remove or soften claims "
            "classified as CONTRADICTED or INSUFFICIENT, retain only claims "
            "supported by the numbered evidence, and put inline citations at "
            "the end of every factual sentence. Return only the final answer.\n\n"
            f"Question:\n{question}\n\nEvidence:\n{docs}\n\nRequired output format:\n{answer_format}\n\nDraft:\n{draft}\n\nReview:\n{review}"
        )
        revised, usage = call([{"role": "user", "content": revise_prompt}], key)
        trace.append({"role": "reviser", "usage": usage})
        return revised, trace

    raise ValueError(condition)


def select_records(dataset: str, n: int) -> List[Dict[str, Any]]:
    path = ALCE_DATA / (
        "asqa_eval_gtr_top100.json" if dataset == "asqa" else "qampari_eval_gtr_top100.json"
    )
    records = load_json(path)
    # Fixed first-n selection is deliberate: it is auditable and avoids tuning
    # the sample after seeing system outputs.
    return records[:n]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-per-dataset", type=int, default=2)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not key:
        raise SystemExit("DEEPSEEK_API_KEY is not configured")

    args.out.mkdir(parents=True, exist_ok=True)
    manifest: Dict[str, Any] = {
        "benchmark": "ALCE official ASQA/QAMPARI data",
        "repo": "https://github.com/princeton-nlp/ALCE",
        "model": MODEL,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "top_k": args.top_k,
        "selection": "first n records in each official JSON file; frozen before generation",
        "conditions": ["v0", "v1", "v2"],
        "records": [],
    }
    output_path = args.out / "alce_official_pilot_outputs.json"
    manifest_path = args.out / "run_manifest.json"

    for dataset in ("asqa", "qampari"):
        for record in select_records(dataset, args.n_per_dataset):
            docs = evidence_block(record["docs"], args.top_k)
            question = record["question"]
            answer_format = (
                "Return only a comma-separated list of answers. Do not add an introduction, explanation, or bullet list. "
                "Place citation markers after the relevant list item."
                if dataset == "qampari" else
                "Answer all subquestions concisely in prose, preserving the question's distinctions and using inline citations."
            )
            for condition in ("v0", "v1", "v2"):
                output, trace = run_condition(condition, question, docs, answer_format, key)
                item = dict(record)
                item["output"] = output
                item["condition"] = condition
                item["dataset"] = dataset
                item["trace"] = trace
                item["generated_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                manifest["records"].append(item)
                output_path.write_text(json.dumps(manifest["records"], ensure_ascii=False, indent=2), encoding="utf-8")
                manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
                print(dataset, record.get("sample_id", record.get("id")), condition, "ok")

    print(f"WROTE {output_path}")
    print(f"WROTE {manifest_path}")


if __name__ == "__main__":
    main()
