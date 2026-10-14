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
    ERR_PATH,
    FROZEN_CORPUS_PATH,
    OUTPUT_DIR as METHOD1_DIR,
    _compact,
    _log_error,
    _paper_id,
    role1_retrieval,
    role2_screening,
    role3_evidence,
    role4_synthesis,
)


DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "method2_outputs"
DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SAME_MODEL_OUTPUT_DIR = PROJECT_ROOT / "data" / "method2_same_model_outputs"
SAME_MODEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


REVIEW_SYSTEM = (
    "You are a strict reviewer for an academic intelligence report. "
    "Review the draft against the supplied evidence only. "
    "Output only valid JSON."
)

REVISE_SYSTEM = (
    "You are a reviser for an academic intelligence report. "
    "Rewrite in Chinese. Use only the supplied evidence. "
    "Do not invent facts. Do not use citation ranges like [1-4]; cite as [1][2] instead. "
    "Keep a structured report and end with a numbered bibliography section titled '## 参考文献'."
)


ROLE_TIMEOUT_SECONDS = 150
DEFAULT_REVIEW_MAX_TOKENS = 1200
DEFAULT_REVISE_MAX_TOKENS = 3400


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
            f"[{idx}] {paper.get('title', 'N/A')}. {paper.get('journal', '') or paper.get('source', '')}. {paper.get('year', '')}."
        )
    return "\n\n".join(evidence_blocks), "\n".join(bib_lines)


def review_draft(
    query: str,
    draft: str,
    evidence_block: str,
    review_provider: str,
    review_provider_key: str,
    review_model: Optional[str],
    reviewer_model: Optional[str],
    review_max_tokens: int = DEFAULT_REVIEW_MAX_TOKENS,
) -> Dict[str, Any]:
    from modules.ai_provider import call_ai

    prompt = (
        f"Research query: {query}\n\n"
        "Evidence set:\n"
        f"{evidence_block}\n\n"
        "Draft report:\n"
        f"{draft}\n\n"
        "Review this draft and return ONLY JSON with the following schema:\n"
        '{'
        '"overall_score": 0-10, '
        '"major_issues": ["..."], '
        '"citation_issues": ["..."], '
        '"revision_instructions": ["..."], '
        '"accept_without_revision": true/false'
        '}'
    )

    response = call_ai(
        prompt=prompt,
        system=REVIEW_SYSTEM,
        provider=review_provider,
        api_key=review_provider_key,
        model=reviewer_model or review_model,
        task_type="critic",
        max_tokens=review_max_tokens,
        temperature=0.1,
        timeout=ROLE_TIMEOUT_SECONDS,
    )
    match = re.search(r"\{.*\}", response.strip(), re.S)
    return json.loads(match.group(0) if match else response.strip())


def revise_draft(
    query: str,
    draft: str,
    evidence_block: str,
    bib_lines: str,
    review_json: Dict[str, Any],
    revise_provider: str,
    revise_provider_key: str,
    revise_model: Optional[str],
    reviser_model: Optional[str],
    revise_max_tokens: int = DEFAULT_REVISE_MAX_TOKENS,
) -> str:
    from modules.ai_provider import call_ai

    prompt = (
        f"Research query: {query}\n\n"
        "Evidence set:\n"
        f"{evidence_block}\n\n"
        "Current draft:\n"
        f"{draft}\n\n"
        f"Reviewer feedback JSON:\n{json.dumps(review_json, ensure_ascii=False, indent=2)}\n\n"
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
        "- In section 3, summarize only the reviewer issues that materially changed the draft.\n"
        "- End with:\n\n## 参考文献\n"
        f"{bib_lines}"
    )

    revised = call_ai(
        prompt=prompt,
        system=REVISE_SYSTEM,
        provider=revise_provider,
        api_key=revise_provider_key,
        model=reviser_model or revise_model,
        task_type="analysis",
        max_tokens=revise_max_tokens,
        temperature=0.2,
        timeout=ROLE_TIMEOUT_SECONDS,
    )
    return _sanitize_citation_ranges(revised)


def run_method2(
    query: str,
    qid: str,
    writer_provider: str,
    writer_model: str,
    reviewer_provider: str,
    reviewer_model: str,
    reviser_provider: str,
    reviser_model: str,
    output_dir: Path,
    stem_tag: str,
    baseline_label: str,
    review_rounds: int = 1,
    stop_on_accept: bool = True,
    review_max_tokens: int = DEFAULT_REVIEW_MAX_TOKENS,
    revise_max_tokens: int = DEFAULT_REVISE_MAX_TOKENS,
) -> None:
    from modules.meta_opt import sync_baseline_result
    from modules.research_wiki import ingest_baseline_result
    from modules.searcher import _load_saved_search_config

    cfg = _load_saved_search_config()
    writer_provider_key = cfg.get(f"{writer_provider}_api_key", "") or ""
    reviewer_provider_key = cfg.get(f"{reviewer_provider}_api_key", "") or ""
    reviser_provider_key = cfg.get(f"{reviser_provider}_api_key", "") or ""
    writer_model_arg = writer_model or None
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"{qid}_{stem_tag}_{stamp}"
    md_path = output_dir / f"{stem}.md"
    json_path = output_dir / f"{stem}.json"

    started = time.time()

    print("  [R1] Retrieval (frozen corpus)...")
    papers_raw, effective_query = role1_retrieval(query, writer_provider, writer_provider_key, writer_model_arg)
    print(f"       Retrieved {len(papers_raw)} papers")

    print("  [R2] Screening (top 8)...")
    screened = role2_screening(
        query,
        papers_raw,
        top_k=8,
        provider=writer_provider,
        provider_key=writer_provider_key,
        model=writer_model_arg,
    )
    print(f"       Screened to {len(screened)} papers")

    print("  [R3] Evidence extraction...")
    enriched = role3_evidence(
        query,
        screened,
        provider=writer_provider,
        provider_key=writer_provider_key,
        model=writer_model_arg,
    )
    print(f"       Evidence extracted for {len(enriched)} papers")

    evidence_block, bib_lines = _build_evidence_blocks(enriched)

    print("  [R4] Writer synthesis...")
    draft = role4_synthesis(
        query,
        enriched,
        provider=writer_provider,
        provider_key=writer_provider_key,
        model=writer_model_arg,
    )
    current_report = _sanitize_citation_ranges(draft)
    review_history: List[Dict[str, Any]] = []

    for round_idx in range(1, max(1, review_rounds) + 1):
        print(f"  [R5.{round_idx}] Reviewer...")
        review_json = review_draft(
            query=query,
            draft=current_report,
            evidence_block=evidence_block,
            review_provider=reviewer_provider,
            review_provider_key=reviewer_provider_key,
            review_model=reviewer_model or None,
            reviewer_model=reviewer_model or None,
            review_max_tokens=review_max_tokens,
        )
        review_history.append({"round": round_idx, "review": review_json})

        if stop_on_accept and review_json.get("accept_without_revision"):
            print(f"       Reviewer accepted at round {round_idx}; stopping early.")
            break

        print(f"  [R6.{round_idx}] Reviser...")
        current_report = revise_draft(
            query=query,
            draft=current_report,
            evidence_block=evidence_block,
            bib_lines=bib_lines,
            review_json=review_json,
            revise_provider=reviser_provider,
            revise_provider_key=reviser_provider_key,
            revise_model=reviser_model or None,
            reviser_model=reviser_model or None,
            revise_max_tokens=revise_max_tokens,
        )

    final_report = current_report
    md_path.write_text(final_report, encoding="utf-8")

    elapsed_seconds = round(time.time() - started, 3)
    sidecar = {
        "baseline": baseline_label,
        "query": query,
        "effective_search_query": effective_query,
        "writer_provider": writer_provider,
        "reviewer_provider": reviewer_provider,
        "reviser_provider": reviser_provider,
        "writer_model": writer_model,
        "reviewer_model": reviewer_model,
        "reviser_model": reviser_model,
        "corpus_mode": "frozen_topic_run",
        "retrieved_count": len(papers_raw),
        "screened_count": len(screened),
        "review_rounds_requested": review_rounds,
        "review_rounds_completed": len(review_history),
        "review_max_tokens": review_max_tokens,
        "revise_max_tokens": revise_max_tokens,
        "review_feedback": review_history[-1]["review"] if review_history else {},
        "review_history": review_history,
        "all_retrieved_ids": [_paper_id(paper) for paper in papers_raw],
        "top_papers": [_compact(paper) for paper in screened],
        "elapsed_seconds": elapsed_seconds,
        "output_markdown": str(md_path),
    }
    json_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2), encoding="utf-8")

    try:
        ingest_baseline_result(json_path)
        sync_baseline_result(json_path)
    except Exception as exc:
        _log_error(
            {
                "baseline": baseline_label,
                "query_id": qid,
                "query": query,
                "writer_provider": writer_provider,
                "reviewer_provider": reviewer_provider,
                "reviser_provider": reviser_provider,
                "error": f"sync_failed: {exc}",
                "timestamp": stamp,
            }
        )

    print(f"  Saved markdown: {md_path.name}")
    print(f"  Saved metadata: {json_path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch run Method 2 (Adversarial Multi-Agent, frozen corpus mode).")
    parser.add_argument("--mode", choices=["cross_model", "same_model"], default="cross_model")
    parser.add_argument("--writer-provider", default="deepseek")
    parser.add_argument("--writer-model", default="deepseek-chat")
    parser.add_argument("--reviewer-provider", default="kimi")
    parser.add_argument("--reviewer-model", default="")
    parser.add_argument("--reviser-provider", default="deepseek")
    parser.add_argument("--reviser-model", default="deepseek-chat")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=30)
    parser.add_argument("--query-id", default=None, help="Run a single query by ID, e.g. Q05")
    parser.add_argument("--benchmark-path", default=str(BENCHMARK_PATH))
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--review-rounds", type=int, default=1)
    parser.add_argument("--review-max-tokens", type=int, default=DEFAULT_REVIEW_MAX_TOKENS)
    parser.add_argument("--revise-max-tokens", type=int, default=DEFAULT_REVISE_MAX_TOKENS)
    parser.add_argument("--no-stop-on-accept", action="store_true")
    parser.add_argument("--sleep", type=float, default=12.0)
    args = parser.parse_args()

    if args.mode == "same_model":
        args.reviewer_provider = args.writer_provider
        args.reviewer_model = args.writer_model
        args.reviser_provider = args.writer_provider
        args.reviser_model = args.writer_model
        output_dir = SAME_MODEL_OUTPUT_DIR
        stem_tag = "method2_same_model"
        baseline_label = "method2_adversarial_same_model"
    else:
        output_dir = DEFAULT_OUTPUT_DIR
        stem_tag = "method2"
        baseline_label = "method2_adversarial_multi_agent"

    if args.output_dir:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    benchmark_path = Path(args.benchmark_path)
    queries = json.loads(benchmark_path.read_text(encoding="utf-8"))
    print(f"Loaded {len(queries)} benchmark queries.")
    print(f"Benchmark path: {benchmark_path}")
    print(f"Frozen corpus: {FROZEN_CORPUS_PATH}")
    print(f"Method1 directory: {METHOD1_DIR}")
    print(f"Mode: {args.mode}")
    print(f"Output directory: {output_dir}")
    print(f"Review rounds: {args.review_rounds}")
    print(f"Review max tokens: {args.review_max_tokens}")
    print(f"Revise max tokens: {args.revise_max_tokens}")
    print("-" * 60)

    success = 0
    failed = 0

    for row in queries:
        qid = row["id"]
        query_text = row["query"]
        idx = int(qid[1:])

        if args.query_id and qid != args.query_id:
            continue
        if not args.query_id and not (args.start <= idx <= args.end):
            continue

        existing = list(output_dir.glob(f"{qid}_{stem_tag}_*.md"))
        if existing:
            print(f"[{qid}] Already exists, skipping.")
            continue

        print(f"\n[{qid}] {query_text[:60]}...")
        try:
            run_method2(
                query=query_text,
                qid=qid,
                writer_provider=args.writer_provider,
                writer_model=args.writer_model,
                reviewer_provider=args.reviewer_provider,
                reviewer_model=args.reviewer_model,
                reviser_provider=args.reviser_provider,
                reviser_model=args.reviser_model,
                output_dir=output_dir,
                stem_tag=stem_tag,
                baseline_label=baseline_label,
                review_rounds=args.review_rounds,
                stop_on_accept=not args.no_stop_on_accept,
                review_max_tokens=args.review_max_tokens,
                revise_max_tokens=args.revise_max_tokens,
            )
            success += 1
        except Exception as exc:
            print(f"  ERROR: {exc}")
            _log_error(
                {
                    "baseline": baseline_label,
                    "query_id": qid,
                    "query": query_text,
                    "writer_provider": args.writer_provider,
                    "reviewer_provider": args.reviewer_provider,
                    "reviser_provider": args.reviser_provider,
                    "error": str(exc),
                    "timestamp": datetime.now().isoformat(),
                }
            )
            failed += 1
        print(f"  Sleeping {args.sleep}s...")
        time.sleep(args.sleep)

    print("\n" + "=" * 60)
    print(f"Done. Success: {success}  Failed: {failed}")
    print(f"Run evaluate_metrics.py --dir {output_dir} to score this Method 2 variant.")


if __name__ == "__main__":
    main()
