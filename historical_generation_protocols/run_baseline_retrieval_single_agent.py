from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
DATA_DIR = PROJECT_ROOT / "data" / "baselines"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _compact_papers(papers: List[Dict[str, Any]], limit: int = 15) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for paper in papers[:limit]:
        rows.append(
            {
                "title": paper.get("title", ""),
                "year": paper.get("year", ""),
                "source": paper.get("source", ""),
                "journal": paper.get("journal", ""),
                "doi": paper.get("doi", ""),
                "citations": paper.get("citations", 0) or 0,
                "abstract": (paper.get("abstract", "") or "")[:800],
            }
        )
    return rows


def _paper_id(paper: Dict[str, Any]) -> str:
    doi = (paper.get("doi") or "").strip().lower()
    if doi:
        return f"doi:{doi}"
    title = " ".join((paper.get("title") or "").lower().split())
    year = str(paper.get("year") or "").strip()
    return f"title:{title}|{year}"


def _derive_search_query(query: str, provider: str, provider_key: str, model: str | None) -> str:
    from modules.ai_provider import call_ai

    if len(query) <= 24 and "？" not in query and "?" not in query:
        return query

    prompt = (
        "Convert the following research question into a concise academic search query.\n"
        "Rules:\n"
        "1. Keep only core topic terms.\n"
        "2. Remove polite wording and question wording.\n"
        "3. Return only one line.\n"
        "4. Prefer bilingual or keyword-style wording if useful.\n\n"
        f"Question: {query}"
    )
    try:
        response = call_ai(
            prompt=prompt,
            system="You rewrite long natural-language questions into concise academic search keywords.",
            provider=provider,
            api_key=provider_key,
            model=model,
            task_type="analysis",
            max_tokens=120,
            temperature=0.1,
        )
        return (response or "").strip().splitlines()[0].strip() or query
    except Exception:
        return query


def main() -> None:
    from modules.ai_provider import call_ai
    from modules.meta_opt import sync_baseline_result
    from modules.research_wiki import ingest_baseline_result
    from modules.searcher import _load_saved_search_config, search_full

    parser = argparse.ArgumentParser(description="Run Baseline B: retrieval + single-agent synthesis.")
    parser.add_argument("--query", required=True, help="Research topic or intelligence query.")
    parser.add_argument("--provider", default="deepseek", help="LLM provider, default deepseek.")
    parser.add_argument("--model", default="", help="Optional model override.")
    parser.add_argument("--years-back", type=int, default=10)
    parser.add_argument("--per-source", type=int, default=12)
    parser.add_argument("--out-prefix", default="retrieval_single_agent", help="Output file prefix.")
    args = parser.parse_args()

    cfg = _load_saved_search_config()
    provider_key = cfg.get(f"{args.provider}_api_key", "") or ""
    effective_query = _derive_search_query(args.query, args.provider, provider_key, args.model or None)

    papers = search_full(
        query=effective_query,
        max_results_per_source=args.per_source,
        years_back=args.years_back,
        config=cfg,
    )
    top_papers = _compact_papers(papers, limit=15)

    system = (
        "You are an academic intelligence analyst. "
        "Answer in Chinese using only the supplied retrieved-paper summaries. "
        "Do not invent references or claim full-text reading."
    )
    prompt = (
        f"Research topic: {args.query}\n"
        f"Retrieved papers: {len(papers)}\n\n"
        f"Top retrieved evidence (JSON):\n{json.dumps(top_papers, ensure_ascii=False, indent=2)}\n\n"
        "Please write a structured intelligence report with these sections:\n"
        "1. Corpus overview\n"
        "2. Main themes from retrieved papers\n"
        "3. Evidence-supported directions\n"
        "4. Risks and limitations of abstract-level evidence\n"
        "5. A cautious conclusion\n\n"
        "Important: explicitly mark that this baseline uses retrieval summaries rather than full-text reading."
    )

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"{args.out_prefix}_{stamp}"
    md_path = DATA_DIR / f"{stem}.md"
    json_path = DATA_DIR / f"{stem}.json"
    err_path = DATA_DIR / "errors.jsonl"

    try:
        response = call_ai(
            prompt=prompt,
            system=system,
            provider=args.provider,
            api_key=provider_key,
            model=args.model or None,
            task_type="analysis",
            max_tokens=2600,
            temperature=0.3,
        )
    except Exception as exc:
        err_path.write_text(
            err_path.read_text(encoding="utf-8") + json.dumps(
                {
                    "baseline": "retrieval_single_agent",
                    "query": args.query,
                    "provider": args.provider,
                    "error": str(exc),
                    "timestamp": stamp,
                },
                ensure_ascii=False,
            ) + "\n",
            encoding="utf-8",
        ) if err_path.exists() else err_path.write_text(
            json.dumps(
                {
                    "baseline": "retrieval_single_agent",
                    "query": args.query,
                    "provider": args.provider,
                    "error": str(exc),
                    "timestamp": stamp,
                },
                ensure_ascii=False,
            ) + "\n",
            encoding="utf-8",
        )
        raise

    md_path.write_text(response, encoding="utf-8")
    json_path.write_text(
        json.dumps(
            {
                "baseline": "retrieval_single_agent",
                "query": args.query,
                "effective_search_query": effective_query,
                "provider": args.provider,
                "model": args.model or "",
                "retrieved_count": len(papers),
                "all_retrieved_ids": [_paper_id(paper) for paper in papers],
                "top_papers": top_papers,
                "output_markdown": str(md_path),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    try:
        ingest_baseline_result(json_path)
        sync_baseline_result(json_path)
    except Exception as exc:
        err_row = {
            "baseline": "retrieval_single_agent",
            "query": args.query,
            "provider": args.provider,
            "error": f"sync_failed: {exc}",
            "timestamp": stamp,
        }
        with open(err_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(err_row, ensure_ascii=False) + "\n")

    print(f"[baseline] retrieved papers: {len(papers)}")
    print(f"[baseline] saved markdown: {md_path}")
    print(f"[baseline] saved metadata: {json_path}")


if __name__ == "__main__":
    main()
