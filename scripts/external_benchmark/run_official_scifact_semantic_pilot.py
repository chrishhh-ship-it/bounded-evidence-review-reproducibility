"""Run a small SciFact semantic-verification pilot using the official data.

This is a semantic companion benchmark for the ARL paper. It uses only
SciFact's official dev claims/corpus and never changes the frozen manuscript
experiments. V0 is a one-pass judge; V2 uses judge -> independent reviewer ->
adjudicator with the same DeepSeek v4 model and temperature.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCIFACT_DATA = PROJECT_ROOT / "external" / "github_learned_projects" / "scifact" / "data"
DEFAULT_OUT = PROJECT_ROOT / "data" / "external_benchmarks" / "scifact_semantic_pilot_n10"
sys.path.insert(0, str(PROJECT_ROOT))
from modules.ai_provider import call_provider  # noqa: E402


MODEL = "deepseek-v4-pro"
TEMPERATURE = 0.0
MAX_TOKENS = 12000
LABELS = {"SUPPORT", "CONTRADICT", "NEI"}


def call(messages: List[Dict[str, str]], key: str) -> tuple[str, Dict[str, Any]]:
    for attempt, budget in enumerate((MAX_TOKENS, 20000), start=1):
        started = time.perf_counter()
        text, usage = call_provider(
            "deepseek", key, messages, model=MODEL,
            max_tokens=budget, temperature=TEMPERATURE, timeout=180,
        )
        if text and text.strip():
            meta = dict(usage or {})
            meta.update({"attempt": attempt, "max_tokens_requested": budget,
                         "latency_ms": round((time.perf_counter() - started) * 1000)})
            return text.strip(), meta
        time.sleep(2)
    raise RuntimeError("empty completion after retry")


def parse_label(text: str) -> str:
    upper = text.upper()
    for label in ("CONTRADICT", "SUPPORT", "NEI"):
        if re.search(rf"\b{label}\b", upper):
            return label
    return "UNPARSEABLE"


def load_records(n: int) -> List[Dict[str, Any]]:
    claims = [json.loads(line) for line in (SCIFACT_DATA / "claims_dev.jsonl").read_text(encoding="utf-8").splitlines()]
    corpus = {}
    for line in (SCIFACT_DATA / "corpus.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        corpus[str(row["doc_id"])] = row
    selected = []
    for row in claims:
        labels = [ev["label"] for groups in row.get("evidence", {}).values() for ev in groups]
        gold = "SUPPORT" if "SUPPORT" in labels and "CONTRADICT" not in labels else "CONTRADICT" if "CONTRADICT" in labels and "SUPPORT" not in labels else "NEI" if not labels else "AMBIGUOUS"
        if gold == "AMBIGUOUS":
            continue
        evidence_parts = []
        for doc_id, groups in row.get("evidence", {}).items():
            doc = corpus.get(str(doc_id), {})
            abstracts = doc.get("abstract", [])
            sentence_ids = sorted({sid for group in groups for sid in group.get("sentences", [])})
            text = " ".join(abstracts[sid] for sid in sentence_ids if sid < len(abstracts))
            evidence_parts.append(f"Document {doc_id}: {text}")
        selected.append({"id": row["id"], "claim": row["claim"], "gold": gold,
                         "evidence": "\n".join(evidence_parts) or "No annotated evidence is provided."})
        if len(selected) >= n:
            break
    return selected


def prompt(record: Dict[str, Any], extra: str = "") -> str:
    return (
        "Classify the scientific claim using only the provided evidence. "
        "Labels: SUPPORT (evidence entails the claim), CONTRADICT (evidence "
        "contradicts it), or NEI (the evidence is insufficient). Return the "
        "label first, then one short rationale.\n\n"
        f"Claim: {record['claim']}\nEvidence:\n{record['evidence']}\n\n{extra}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=10)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not key:
        raise SystemExit("DEEPSEEK_API_KEY is not configured")
    args.out.mkdir(parents=True, exist_ok=True)

    records = load_records(args.n)
    outputs: List[Dict[str, Any]] = []
    manifest = {"benchmark": "SciFact official dev", "repo": "https://github.com/allenai/scifact",
                "model": MODEL, "temperature": TEMPERATURE, "records": outputs}
    for record in records:
        draft, draft_usage = call([{"role": "user", "content": prompt(record)}], key)
        reviewer, reviewer_usage = call([{"role": "user", "content": prompt(record, "Independently verify the label; do not rely on another answer.")}], key)
        adjudicate = (
            "Adjudicate the two analyses. If they disagree, inspect the evidence and select the label that is strictly justified. "
            "Return exactly one final label first, followed by one sentence.\n\n"
            f"Claim: {record['claim']}\nEvidence:\n{record['evidence']}\n\nFirst analysis:\n{draft}\n\nIndependent review:\n{reviewer}"
        )
        final, final_usage = call([{"role": "user", "content": adjudicate}], key)
        item = dict(record)
        item.update({"v0_label": parse_label(draft), "v2_reviewer_label": parse_label(reviewer),
                     "v2_final_label": parse_label(final), "draft": draft,
                     "reviewer": reviewer, "final": final,
                     "usage": {"v0": draft_usage, "reviewer": reviewer_usage, "adjudicator": final_usage}})
        outputs.append(item)
        (args.out / "scifact_semantic_pilot_outputs.json").write_text(json.dumps(outputs, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest["records"] = outputs
        (args.out / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(record["id"], record["gold"], item["v0_label"], item["v2_final_label"], "ok")


if __name__ == "__main__":
    main()
