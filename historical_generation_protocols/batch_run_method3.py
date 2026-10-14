"""
batch_run_method3.py  —  Method 3: Self-Refine Baseline
---------------------------------------------------------
Architecture: Writer(DeepSeek) → SoftReviewer(DeepSeek, same model) → Reviser(DeepSeek)

Key difference from Method 2b (Same-Model ARL):
  Method 2b reviewer does STRUCTURAL list-comparison:
      "For each [N] in draft, verify it appears in the evidence list."
  Method 3 reviewer does GENERAL quality critique:
      "Check if claims are reasonable and citations seem appropriate."
  This isolates the value of STRUCTURAL constraint vs. any review step.
  Represents the Self-Refine / Self-RAG self-critique principle.

Usage:
  python scripts/batch_run_method3.py --start 1 --end 60
  python scripts/batch_run_method3.py --query-id Q05
  python scripts/batch_run_method3.py --start 31 --end 60 \\
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

OUTPUT_DIR = PROJECT_ROOT / "data" / "method3_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ROLE_TIMEOUT_SECONDS = 150

# ── Soft Reviewer System ─────────────────────────────────────────────────────
# Intentionally GENERAL quality critique — no structural list-comparison.
# This simulates Self-Refine / Self-RAG self-critique principle.
SOFT_REVIEW_SYSTEM = (
    "You are a general quality reviewer for an academic intelligence report. "
    "Your job is to assess overall writing quality, logical coherence, and "
    "whether citations seem reasonable and relevant to the claims made. "
    "You do NOT need to verify every citation against a reference list. "
    "Focus on content quality and readability. "
    "Output only valid JSON."
)

SOFT_REVISE_SYSTEM = (
    "You are a reviser for an academic intelligence report. "
    "Rewrite in Chinese based on the reviewer's feedback. "
    "Use only the supplied evidence. "
    "Do not invent facts. Do not use citation ranges like [1-4]; cite as [1][2] instead. "
    "Keep a structured report and end with a numbered bibliography section titled '## 参考文献'."
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


def soft_review_draft(
    query: str,
    draft: str,
    evidence_block: str,
    provider: str,
    provider_key: str,
    model: Optional[str],
) -> Dict[str, Any]:
    """
    SOFT review: general quality critique without structural list-comparison.
    Reviewer checks if claims seem reasonable and citations seem relevant,
    but does NOT verify each citation exists in the evidence list.
    """
    from modules.ai_provider import call_ai

    prompt = (
        f"Research query: {query}\n\n"
        "Evidence context (for reference only):\n"
        f"{evidence_block}\n\n"
        "Draft report to review:\n"
        f"{draft}\n\n"
        "Please review this draft for:\n"
        "1. Overall logical coherence and clarity\n"
        "2. Whether the key claims are well-argued\n"
        "3. Whether citations seem topically relevant to their associated claims\n"
        "4. Any major content gaps or unsupported assertions\n\n"
        "Return ONLY JSON with this schema:\n"
        '{"overall_score": 0-10, '
        '"content_issues": ["..."], '
        '"citation_quality_notes": ["..."], '
        '"revision_suggestions": ["..."], '
        '"accept_without_revision": true/false}'
    )

    response = call_ai(
        prompt=prompt,
        system=SOFT_REVIEW_SYSTEM,
        provider=provider,
        api_key=provider_key,
        model=model,
        task_type="critic",
        max_tokens=1200,
        temperature=0.1,
        timeout=ROLE_TIMEOUT_SECONDS,
    )
    match = re.search(r"\{.*\}", response.strip(), re.S)
    return json.loads(match.group(0) if match else response.strip())


def soft_revise_draft(
    query: str,
    draft: str,
    evidence_block: str,
    bib_lines: str,
    review_json: Dict[str, Any],
    provider: str,
    provider_key: str,
    model: Optional[str],
) -> str:
    from modules.ai_provider import call_ai

    prompt = (
        f"Research query: {query}\n\n"
        "Evidence set:\n"
        f"{evidence_block}\n\n"
        "Current draft:\n"
        f"{draft}\n\n"
        f"Reviewer feedback:\n{json.dumps(review_json, ensure_ascii=False, indent=2)}\n\n"
        "Rewrite the report in Chinese with these required sections:\n"
        "1. 检索与筛选概览\n"
        "2. 核心主题与证据\n"
        "3. 审稿发现\n"
        "4. 修订后结论\n"
        "5. 局限性\n\n"
        "Rules:\n"
        "- Every factual claim must cite specific numbered references like [1][2].\n"
        "- Do not use citation ranges.\n"
        "- Keep all claims at abstract-level evidence only.\n"
        "- End with:\n\n## 参考文献\n"
        f"{bib_lines}"
    )

    revised = call_ai(
        prompt=prompt,
        system=SOFT_REVISE_SYSTEM,
        provider=provider,
        api_key=provider_key,
        model=model,
        task_type="analysis",
        max_tokens=3400,
        temperature=0.2,
        timeout=ROLE_TIMEOUT_SECONDS,
    )
    return _sanitize_citation_ranges(revised)


def run_method3(
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
    stem = f"{qid}_method3_{stamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / f"{stem}.md"
    json_path = output_dir / f"{stem}.json"

    started = time.time()

    print(f"\n[{qid}] Method 3 (Self-Refine baseline)")
    print("  [R1] Retrieval (frozen corpus)...")
    papers_raw, effective_query = role1_retrieval(query, provider, provider_key, model_arg)
    print(f"       Retrieved {len(papers_raw)} papers")

    print("  [R2] Screening (top 8)...")
    screened = role2_screening(
        query, papers_raw, top_k=8, provider=provider,
        provider_key=provider_key, model=model_arg
    )
    print(f"       Screened to {len(screened)} papers")

    print("  [R3] Evidence extraction...")
    enriched = role3_evidence(
        query, screened, provider=provider,
        provider_key=provider_key, model=model_arg
    )

    print("  [R4] Synthesis (writer)...")
    draft_md = role4_synthesis(
        query, enriched, provider=provider,
        provider_key=provider_key, model=model_arg
    )

    evidence_block, bib_lines = _build_evidence_blocks(enriched)

    print("  [R5] Soft review (same model, general quality critique)...")
    try:
        review_json = soft_review_draft(
            query, draft_md, evidence_block,
            provider=provider, provider_key=provider_key, model=model_arg
        )
        accepted = review_json.get("accept_without_revision", False)
        score = review_json.get("overall_score", "?")
        print(f"       Review score: {score}/10, accept_without_revision={accepted}")
    except Exception as exc:
        print(f"       Review failed ({exc}), using draft as-is")
        review_json = {"error": str(exc), "accept_without_revision": True}
        accepted = True

    if accepted:
        final_md = draft_md
        print("  [R6] Revision skipped (accepted)")
    else:
        print("  [R6] Soft revision (same model)...")
        final_md = soft_revise_draft(
            query, draft_md, evidence_block, bib_lines,
            review_json, provider=provider,
            provider_key=provider_key, model=model_arg
        )

    md_path.write_text(final_md, encoding="utf-8")

    elapsed = round(time.time() - started, 3)
    sidecar = {
        "baseline": "method3_self_refine",
        "query": query,
        "query_id": qid,
        "effective_search_query": effective_query,
        "provider": provider,
        "model": model,
        "retrieved_count": len(papers_raw),
        "screened_count": len(screened),
        "review_score": review_json.get("overall_score"),
        "accepted_without_revision": accepted,
        "all_retrieved_ids": [_paper_id(p) for p in papers_raw],
        "top_papers": [_compact(p) for p in screened],
        "elapsed_seconds": elapsed,
        "output_markdown": str(md_path),
    }
    json_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Saved: {md_path.name}  ({elapsed:.1f}s)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Method 3: Self-Refine baseline (soft review, no structural list-comparison)."
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

    print(f"Method 3 (Self-Refine): {len(targets)} queries, provider={args.provider}")
    for i, q in enumerate(targets):
        run_method3(
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
