"""
batch_run_method4.py  —  Method 4: CoT-Citation Verification Baseline
-----------------------------------------------------------------------
Architecture: Single agent, same model throughout.
  Role 1-4: Identical to Method 1 (pipeline)
  Role 5:   CoT-Citation Verifier — same model goes through each [N]
            citation in the draft and removes/flags any it cannot verify
            against the evidence list. Single-pass, no role separation.

Represents the FLARE / chain-of-thought active verification principle:
  - The same agent that wrote the report now verifies its own citations
  - Explicit CoT reasoning per citation
  - No adversarial structure, no role separation

Usage:
  python scripts/batch_run_method4.py --start 1 --end 60
  python scripts/batch_run_method4.py --query-id Q05
  python scripts/batch_run_method4.py --start 31 --end 60 \\
      --benchmark-path data/benchmarks/pilot_queries_v2.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from batch_run_method1 import (  # noqa: E402
    BENCHMARK_PATH,
    _compact,
    _log_error,
    _paper_id,
    role1_retrieval,
    role2_screening,
    role3_evidence,
    role4_synthesis,
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "method4_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ROLE_TIMEOUT_SECONDS = 180

COT_VERIFY_SYSTEM = (
    "You are an academic citation verifier. "
    "Your task is to check every citation in a report against a provided evidence list, "
    "then rewrite the report with only verified citations retained. "
    "Think step-by-step about each citation before deciding to keep or remove it."
)


def _sanitize_citation_ranges(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        raw = match.group(1)
        parts: List[str] = []
        for block in raw.split(","):
            block = block.strip()
            if not block:
                continue
            if "-" in block:
                try:
                    start_s, end_s = [item.strip() for item in block.split("-", 1)]
                    start_i = int(start_s)
                    end_i = int(end_s)
                    if start_i <= end_i and end_i - start_i <= 30:
                        parts.extend([f"[{i}]" for i in range(start_i, end_i + 1)])
                        continue
                except ValueError:
                    pass
            try:
                parts.append(f"[{int(block)}]")
            except ValueError:
                return match.group(0)
        return "".join(parts) if parts else match.group(0)
    return re.sub(r"\[([0-9,\-\s]+)\]", repl, text)


def _build_evidence_blocks(papers: List[Dict[str, Any]]) -> tuple[str, str]:
    evidence_blocks: List[str] = []
    bib_lines: List[str] = []
    for idx, paper in enumerate(papers, 1):
        evidence = paper.get("evidence", {})
        evidence_blocks.append(
            f"[{idx}] {paper.get('title', '')} ({paper.get('year', '')})\n"
            f"    Source: {paper.get('source', '')}\n"
            f"    Journal: {paper.get('journal', '')}\n"
            f"    Key claim: {evidence.get('key_claim', 'N/A')}\n"
            f"    Methodology: {evidence.get('methodology', 'N/A')}\n"
            f"    Metrics: {', '.join(evidence.get('metrics_mentioned', [])) or 'N/A'}\n"
            f"    Limitation: {evidence.get('limitation', 'N/A')}"
        )
        bib_lines.append(
            f"[{idx}] {paper.get('title', 'N/A')}. "
            f"{paper.get('journal', '') or paper.get('source', '')}. "
            f"{paper.get('year', '')}."
        )
    return "\n\n".join(evidence_blocks), "\n".join(bib_lines)


def cot_citation_verify(
    query: str,
    draft: str,
    evidence_block: str,
    bib_lines: str,
    provider: str,
    provider_key: str,
    model: Optional[str],
) -> str:
    """
    CoT-Citation Verification:
    Single agent reasons step-by-step about each citation,
    then rewrites the report keeping only verified citations.
    No structural list-comparison by a separate reviewer model.
    """
    from modules.ai_provider import call_ai

    # Extract citation numbers from draft for explicit CoT
    cited_nums = sorted(set(int(m) for m in re.findall(r"\[(\d+)\]", draft)))
    max_evidence = len(re.findall(r"^\[(\d+)\]", evidence_block, re.M))

    cot_lines = []
    for n in cited_nums:
        if n <= max_evidence:
            cot_lines.append(f"  - Citation [{n}]: exists in evidence list → KEEP")
        else:
            cot_lines.append(f"  - Citation [{n}]: index {n} exceeds evidence list (max={max_evidence}) → REMOVE")

    verification_hint = "\n".join(cot_lines) if cot_lines else "  (no citations found in draft)"

    prompt = (
        f"Research query: {query}\n\n"
        "=== EVIDENCE LIST ===\n"
        f"{evidence_block}\n\n"
        "=== DRAFT REPORT ===\n"
        f"{draft}\n\n"
        "=== CITATION VERIFICATION (Chain-of-Thought) ===\n"
        "I will now verify each citation [N] in the draft against the evidence list above:\n"
        f"{verification_hint}\n\n"
        "=== TASK ===\n"
        "Rewrite the report in Chinese with these rules:\n"
        "1. REMOVE any citation [N] where N exceeds the number of papers in the evidence list.\n"
        "2. REMOVE any sentence whose ONLY citation is invalid; replace with an uncited general statement if needed.\n"
        "3. Keep all verified citations exactly as [N] format.\n"
        "4. Do not use citation ranges like [1-4]; write [1][2] instead.\n"
        "5. Maintain the same section structure:\n"
        "   1. 检索与筛选概览\n"
        "   2. 核心主题与证据\n"
        "   3. 引用验证说明\n"
        "   4. 结论\n"
        "   5. 局限性\n"
        "6. End with:\n\n## 参考文献\n"
        f"{bib_lines}\n\n"
        "Write the verified report now:"
    )

    result = call_ai(
        prompt=prompt,
        system=COT_VERIFY_SYSTEM,
        provider=provider,
        api_key=provider_key,
        model=model,
        task_type="analysis",
        max_tokens=3600,
        temperature=0.1,
        timeout=ROLE_TIMEOUT_SECONDS,
    )
    return _sanitize_citation_ranges(result)


def run_method4(
    query: str,
    qid: str,
    provider: str,
    model: Optional[str],
    output_dir: Path,
) -> None:
    from modules.searcher import _load_saved_search_config

    cfg = _load_saved_search_config()
    provider_key = cfg.get(f"{provider}_api_key", "") or ""
    model_arg = model or None
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"{qid}_method4_{stamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / f"{stem}.md"
    json_path = output_dir / f"{stem}.json"

    started = time.time()

    print(f"\n[{qid}] Method 4 (CoT-Citation Verification)")
    print("  [R1] Retrieval (frozen corpus)...")
    papers_raw, effective_query = role1_retrieval(query, provider, provider_key, model_arg)
    print(f"       Retrieved {len(papers_raw)} papers")

    print("  [R2] Screening (top 8)...")
    screened = role2_screening(
        query, papers_raw, top_k=8,
        provider=provider, provider_key=provider_key, model=model_arg
    )
    print(f"       Screened to {len(screened)} papers")

    print("  [R3] Evidence extraction...")
    enriched = role3_evidence(
        query, screened,
        provider=provider, provider_key=provider_key, model=model_arg
    )

    print("  [R4] Synthesis (single agent, draft)...")
    draft_md = role4_synthesis(
        query, enriched,
        provider=provider, provider_key=provider_key, model=model_arg
    )

    evidence_block, bib_lines = _build_evidence_blocks(enriched)

    print("  [R5] CoT-Citation verification (same agent)...")
    final_md = cot_citation_verify(
        query, draft_md, evidence_block, bib_lines,
        provider=provider, provider_key=provider_key, model=model_arg
    )

    md_path.write_text(final_md, encoding="utf-8")

    elapsed = round(time.time() - started, 3)
    sidecar = {
        "baseline": "method4_cot_citation",
        "query": query,
        "query_id": qid,
        "effective_search_query": effective_query,
        "provider": provider,
        "model": model,
        "retrieved_count": len(papers_raw),
        "screened_count": len(screened),
        "all_retrieved_ids": [_paper_id(p) for p in papers_raw],
        "top_papers": [_compact(p) for p in screened],
        "elapsed_seconds": elapsed,
        "output_markdown": str(md_path),
    }
    json_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Saved: {md_path.name}  ({elapsed:.1f}s)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Method 4: CoT-Citation Verification (single agent, FLARE-inspired)."
    )
    parser.add_argument("--provider", default="deepseek")
    parser.add_argument("--model", default="")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=60)
    parser.add_argument("--query-id", default=None)
    parser.add_argument("--benchmark-path", default=str(BENCHMARK_PATH))
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    parser.add_argument("--sleep", type=float, default=10.0)
    args = parser.parse_args()

    benchmark_path = Path(args.benchmark_path)
    output_dir = Path(args.output_dir)
    queries: List[Dict[str, Any]] = json.loads(
        benchmark_path.read_text(encoding="utf-8")
    )

    if args.query_id:
        targets = [q for q in queries if q["id"] == args.query_id]
    else:
        targets = [
            q for q in queries
            if args.start <= int(q["id"].lstrip("Q")) <= args.end
        ]

    print(f"Method 4 (CoT-Citation): {len(targets)} queries, provider={args.provider}")
    for i, q in enumerate(targets):
        run_method4(
            query=q["query"],
            qid=q["id"],
            provider=args.provider,
            model=args.model or None,
            output_dir=output_dir,
        )
        if i < len(targets) - 1:
            time.sleep(args.sleep)

    print(f"\nDone. Outputs in {output_dir}")


if __name__ == "__main__":
    main()
