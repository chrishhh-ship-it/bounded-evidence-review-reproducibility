"""SciFact cross-model ARL pilot: tests whether the accuracy decline observed
in the same-model pilot (deepseek draft -> deepseek reviewer -> deepseek
adjudicator) is a same-model artifact. Draft and adjudicator stay on
deepseek-v4-pro (so V0 is directly comparable to the same-model pilot);
the Reviewer role is switched to Kimi (moonshot-v1-32k), an independently
trained model with no access to the drafting model's reasoning trace.

Design mirrors the paper's own structural cross-model ARL condition (M2a):
different model reviews, same model (or a fixed adjudicator) repairs.
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
DEFAULT_OUT = PROJECT_ROOT / "data" / "external_benchmarks" / "scifact_cross_model_pilot"
sys.path.insert(0, str(PROJECT_ROOT))
from modules.ai_provider import call_provider  # noqa: E402

DRAFT_MODEL = ("deepseek", "deepseek-v4-pro")
REVIEWER_MODEL = ("kimi", "moonshot-v1-32k")
ADJUDICATOR_MODEL = ("deepseek", "deepseek-v4-pro")
TEMPERATURE = 0.0
LABELS = {"SUPPORT", "CONTRADICT", "NEI"}


def call(provider: str, model: str, messages: List[Dict[str, str]], key: str,
         max_tokens: int = 12000) -> tuple[str, Dict[str, Any]]:
    for attempt, budget in enumerate((max_tokens, max_tokens + 8000), start=1):
        started = time.perf_counter()
        text, usage = call_provider(
            provider, key, messages, model=model,
            max_tokens=budget, temperature=TEMPERATURE, timeout=180,
        )
        if text and text.strip():
            meta = dict(usage or {})
            meta.update({"provider": provider, "model": model, "attempt": attempt,
                         "max_tokens_requested": budget,
                         "latency_ms": round((time.perf_counter() - started) * 1000)})
            return text.strip(), meta
        time.sleep(2)
    raise RuntimeError(f"{provider}/{model} returned empty completion after retry")


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
        gold = ("SUPPORT" if "SUPPORT" in labels and "CONTRADICT" not in labels else
                "CONTRADICT" if "CONTRADICT" in labels and "SUPPORT" not in labels else
                "NEI" if not labels else "AMBIGUOUS")
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
    parser.add_argument("--n", type=int, default=40)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--reuse-v0-from", type=Path, default=None,
                         help="Path to an existing same-model pilot outputs.json to reuse v0_label/draft "
                              "from, instead of re-generating v0 (keeps V0 identical across pilots).")
    args = parser.parse_args()
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    deepseek_key = os.environ.get("DEEPSEEK_API_KEY", "")
    kimi_key = os.environ.get("KIMI_API_KEY", "")
    if not deepseek_key:
        raise SystemExit("DEEPSEEK_API_KEY is not configured")
    if not kimi_key:
        raise SystemExit("KIMI_API_KEY is not configured")
    args.out.mkdir(parents=True, exist_ok=True)

    records = load_records(args.n)

    reuse_v0 = {}
    if args.reuse_v0_from and args.reuse_v0_from.exists():
        prior = json.loads(args.reuse_v0_from.read_text(encoding="utf-8"))
        reuse_v0 = {row["id"]: row for row in prior}

    outputs: List[Dict[str, Any]] = []
    manifest = {
        "benchmark": "SciFact official dev -- cross-model ARL pilot",
        "repo": "https://github.com/allenai/scifact",
        "draft_model": DRAFT_MODEL, "reviewer_model": REVIEWER_MODEL,
        "adjudicator_model": ADJUDICATOR_MODEL,
        "reused_v0_from": str(args.reuse_v0_from) if args.reuse_v0_from else None,
        "records": outputs,
    }
    for record in records:
        prior = reuse_v0.get(record["id"])
        if prior and prior.get("draft"):
            draft, draft_usage = prior["draft"], {"reused_from": str(args.reuse_v0_from)}
            v0_label = prior.get("v0_label") or parse_label(draft)
        else:
            draft, draft_usage = call(*DRAFT_MODEL, [{"role": "user", "content": prompt(record)}], deepseek_key)
            v0_label = parse_label(draft)

        reviewer, reviewer_usage = call(
            *REVIEWER_MODEL,
            [{"role": "user", "content": prompt(
                record, "Independently verify the label. You have not seen any prior analysis of this claim.")}],
            kimi_key,
        )
        adjudicate = (
            "Adjudicate the two analyses of a scientific claim. The first analysis and the "
            "independent review were produced by different models. If they disagree, inspect the "
            "evidence yourself and select the label that is strictly justified by the evidence, not "
            "by which analysis you saw first. Return exactly one final label first, followed by one "
            "sentence.\n\n"
            f"Claim: {record['claim']}\nEvidence:\n{record['evidence']}\n\n"
            f"First analysis (Model A):\n{draft}\n\nIndependent review (Model B):\n{reviewer}"
        )
        final, final_usage = call(*ADJUDICATOR_MODEL, [{"role": "user", "content": adjudicate}], deepseek_key)

        item = dict(record)
        item.update({
            "v0_label": v0_label,
            "cross_reviewer_label": parse_label(reviewer),
            "cross_final_label": parse_label(final),
            "draft": draft, "reviewer": reviewer, "final": final,
            "usage": {"v0": draft_usage, "reviewer": reviewer_usage, "adjudicator": final_usage},
        })
        outputs.append(item)
        (args.out / "scifact_cross_model_pilot_outputs.json").write_text(
            json.dumps(outputs, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest["records"] = outputs
        (args.out / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(record["id"], record["gold"], v0_label, item["cross_final_label"], "ok")


if __name__ == "__main__":
    main()
