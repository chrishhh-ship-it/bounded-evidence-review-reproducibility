from __future__ import annotations

import csv
import json
import statistics
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import evaluate_metrics as em  # noqa: E402


CORPUS_PATH = PROJECT_ROOT / "data" / "frozen_corpus_multidomain_v1.json"
OUTPUT_DIR = PROJECT_ROOT / "data" / "expanded_outputs" / "schema_single_agent_v1"
RESULT_DIR = (
    PROJECT_ROOT
    / "data"
    / "reports"
    / "ipm_major_revision_20260721"
    / "repro"
    / "v3"
)


def main() -> None:
    corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    frozen_by_id = {em._paper_id(row): row for row in corpus}
    latest = em._select_latest_per_query(list(OUTPUT_DIR.glob("*.md")))

    rows: list[dict[str, Any]] = []
    elapsed: list[float] = []
    provider_models: set[tuple[str, str]] = set()
    prompt_hashes: set[str] = set()
    for path in latest.values():
        parsed = em._parse_result_stem(path.stem)
        if not parsed:
            continue
        qid = parsed[0]
        row = em.evaluate_file(
            path,
            "schema_single_agent",
            frozen_by_id,
            match_threshold=0.72,
        )
        reasons: list[str] = []
        if not row["has_bibliography"]:
            reasons.append("missing_bibliography")
        if row["text_orphans"] > 0:
            reasons.append("unresolved_in_text_citation")
        if row["uncited_bibliography_entries"] > 0:
            reasons.append("uncited_bibliography_entry")
        if row["bibliography_match_rate"] < 1:
            reasons.append("bibliography_outside_query_evidence")

        sidecar = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
        elapsed.append(float(sidecar["elapsed_seconds"]))
        provider_models.add((sidecar.get("provider", ""), sidecar.get("model", "")))
        prompt_hashes.add(sidecar.get("prompt_sha256", ""))
        rows.append(
            {
                "qid": qid,
                "citation_precision": row["citation_precision"],
                "bibliography_match_rate": row["bibliography_match_rate"],
                "orphan_rate": row["orphan_rate"],
                "text_orphans": row["text_orphans"],
                "uncited_bibliography_entries": row[
                    "uncited_bibliography_entries"
                ],
                "release": "pass" if not reasons else "block",
                "reasons": "|".join(reasons),
                "elapsed_seconds": sidecar["elapsed_seconds"],
                "path": str(path.relative_to(PROJECT_ROOT)),
            }
        )

    rows.sort(key=lambda item: int(item["qid"][1:]))
    pass_n = sum(row["release"] == "pass" for row in rows)
    summary = {
        "analysis_version": "2026-07-24-schema-baseline-v3",
        "n_queries": len(rows),
        "provider_models": [
            {"provider": provider, "model": model}
            for provider, model in sorted(provider_models)
        ],
        "decoding": {"max_tokens": 3000, "temperature": 0.3},
        "unique_prompt_hashes": len(prompt_hashes),
        "citation_precision_mean": statistics.fmean(
            float(row["citation_precision"] or 0) for row in rows
        ),
        "bibliography_match_rate_mean": statistics.fmean(
            float(row["bibliography_match_rate"]) for row in rows
        ),
        "orphan_rate_mean": statistics.fmean(
            float(row["orphan_rate"]) for row in rows
        ),
        "release_pass_n": pass_n,
        "release_pass_rate": pass_n / len(rows),
        "release_block_n": len(rows) - pass_n,
        "elapsed_seconds": {
            "mean": statistics.fmean(elapsed),
            "median": statistics.median(elapsed),
            "min": min(elapsed),
            "max": max(elapsed),
        },
        "scope_note": (
            "The source M1 query-specific top-paper sidecars and fixed identifiers "
            "were reused. Retrieval was not rerun. Provider-side immutable model "
            "snapshot identifiers were unavailable; the authors confirmed alias "
            "continuity, and alias, decoding parameters, dates, and prompt hashes "
            "are preserved."
        ),
    }

    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    with (RESULT_DIR / "schema_single_agent_per_query.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (RESULT_DIR / "schema_single_agent_run_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
