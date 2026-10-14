"""E2 / R3-2 gap closure: a fresh, structured LLM Reviewer judges the same 251
frozen B0 drafts used by the deterministic validator, producing item-level
verdicts (orphan citations, uncited bibliography entries, suspect fabricated
entries, overall RELEASE/BLOCK) that can be compared against the
deterministic gate's actual release decision. See
data/reports/ipm_major_revision_20260721/repro/v3/E2_R3-2_REVIEWER_VS_GATE_PREREGISTRATION_20260727.md
for the frozen protocol. B0 drafts and the gate's release labels are NOT
regenerated -- only a new reviewer pass is added.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import evaluate_metrics as em  # noqa: E402
from modules.ai_provider import call_provider  # noqa: E402

CORPUS_PATH = PROJECT_ROOT / "data" / "frozen_corpus_multidomain_v1.json"
GATE_CSV = PROJECT_ROOT / "data" / "reports" / "ipm_major_revision_20260721" / "repro" / "v3" / "schema_single_agent_per_query.csv"
OUT_DIR = PROJECT_ROOT / "data" / "reports" / "ipm_major_revision_20260721" / "repro" / "v3" / "e2_r32_reviewer_vs_gate"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL = "deepseek-v4-pro"
TEMPERATURE = 0.0
MAX_TOKENS = 4000


def call(messages: List[Dict[str, str]], key: str) -> tuple[str, Dict[str, Any]]:
    for attempt, budget in enumerate((MAX_TOKENS, 8000), start=1):
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


def build_prompt(body: str, bib_text: str, candidate_titles: List[str]) -> str:
    titles_block = "\n".join(f"- {t}" for t in candidate_titles) or "(no candidate titles available)"
    return (
        "You are a strict structural reviewer for an academic synthesis report. "
        "You are given the report body (with numbered inline citations like [1]), "
        "its bibliography list, and a pool of candidate paper titles that were "
        "legitimately retrievable evidence for this query. Judge citation "
        "structure only by comparing text yourself -- do not assume any external "
        "tool or threshold.\n\n"
        "Identify:\n"
        "1. orphan_citation_numbers: inline citation numbers in the body that have "
        "no corresponding entry in the bibliography list.\n"
        "2. uncited_bibliography_numbers: bibliography entry numbers that are never "
        "cited anywhere in the body.\n"
        "3. suspect_fabricated_or_mismatched_numbers: bibliography entry numbers "
        "whose title does not clearly correspond to any title in the candidate pool "
        "(i.e., looks fabricated or mismatched).\n"
        "4. overall_verdict: \"RELEASE\" if none of the above problems exist, "
        "otherwise \"BLOCK\".\n\n"
        "Return ONLY valid JSON with exactly these keys: orphan_citation_numbers "
        "(array of ints), uncited_bibliography_numbers (array of ints), "
        "suspect_fabricated_or_mismatched_numbers (array of ints), overall_verdict "
        "(string), rationale (one sentence).\n\n"
        f"Candidate paper titles (legitimately retrievable evidence pool):\n{titles_block}\n\n"
        f"Report body:\n{body}\n\n"
        f"Bibliography:\n{bib_text}\n"
    )


def parse_json(text: str) -> Dict[str, Any]:
    match = re.search(r"\{.*\}", text.strip(), re.S)
    return json.loads(match.group(0) if match else text.strip())


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not key:
        raise SystemExit("DEEPSEEK_API_KEY is not configured")

    corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    frozen_by_id = {em._paper_id(row): row for row in corpus}

    with GATE_CSV.open(encoding="utf-8-sig") as f:
        gate_rows = {row["qid"]: row for row in csv.DictReader(f)}

    out_path = OUT_DIR / "reviewer_vs_gate_results.json"
    results: List[Dict[str, Any]] = []
    done_qids = set()
    if out_path.exists():
        results = json.loads(out_path.read_text(encoding="utf-8"))
        done_qids = {r["qid"] for r in results}
        print(f"resuming; already have {len(results)} results")

    for qid, gate_row in sorted(gate_rows.items(), key=lambda kv: int(kv[0][1:])):
        if qid in done_qids:
            continue
        md_path = PROJECT_ROOT / gate_row["path"]
        sidecar_path = md_path.with_suffix(".json")
        content = md_path.read_text(encoding="utf-8")
        sidecar = json.loads(sidecar_path.read_text(encoding="utf-8")) if sidecar_path.exists() else {}
        body, bib_text = em._split_body_bib(content)
        candidate_pool = em._build_candidate_pool(sidecar, frozen_by_id)
        candidate_titles = [row.get("title", "") for row in candidate_pool]

        prompt = build_prompt(body, bib_text, candidate_titles)
        raw, usage = call([{"role": "user", "content": prompt}], key)
        try:
            verdict = parse_json(raw)
        except Exception as exc:
            verdict = {"parse_error": str(exc), "raw": raw}

        gate_release = gate_row["release"]
        reviewer_verdict = str(verdict.get("overall_verdict", "")).strip().upper()
        results.append({
            "qid": qid,
            "gate_release": gate_release,
            "gate_reasons": gate_row["reasons"],
            "gate_text_orphans": int(gate_row["text_orphans"]),
            "gate_uncited_bibliography_entries": int(gate_row["uncited_bibliography_entries"]),
            "reviewer_verdict": verdict,
            "reviewer_overall": "BLOCK" if reviewer_verdict == "BLOCK" else ("RELEASE" if reviewer_verdict == "RELEASE" else "UNPARSEABLE"),
            "usage": usage,
        })
        out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(qid, "gate=" + gate_release, "reviewer=" + results[-1]["reviewer_overall"], "ok")

    print(f"DONE. total: {len(results)}")


if __name__ == "__main__":
    main()
