from __future__ import annotations

import argparse
import json
import re
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = PROJECT_ROOT / "data" / "method1_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BENCHMARK_PATH = PROJECT_ROOT / "data" / "benchmarks" / "multi_agent_intel_service_queries.json"
FROZEN_CORPUS_PATH = (
    PROJECT_ROOT
    / "data"
    / "topic_runs"
    / "multi_agent_intel_service_20260410_114059"
    / "retrieved_papers_wave3.json"
)
ERR_PATH = OUTPUT_DIR / "errors.jsonl"
ROLE_TIMEOUT_SECONDS = 120


def _paper_id(paper: Dict[str, Any]) -> str:
    doi = (paper.get("doi") or "").strip().lower()
    if doi:
        return f"doi:{doi}"
    title = " ".join((paper.get("title") or "").lower().split())
    year = str(paper.get("year") or "").strip()
    return f"title:{title}|{year}"


def _compact(paper: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "title": paper.get("title", ""),
        "year": paper.get("year", ""),
        "journal": paper.get("journal", ""),
        "source": paper.get("source", ""),
        "doi": paper.get("doi", ""),
        "citations": paper.get("citations", 0) or 0,
        "abstract": (paper.get("abstract", "") or "")[:800],
    }


def _log_error(record: Dict[str, Any], err_path: Path = ERR_PATH) -> None:
    with err_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def _normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def _tokenize(text: str) -> List[str]:
    text = _normalize_text(text)
    text = re.sub(r"[^\w\u4e00-\u9fff]+", " ", text)
    return [tok for tok in text.split() if len(tok) >= 2]


def _load_frozen_corpus() -> List[Dict[str, Any]]:
    return json.loads(FROZEN_CORPUS_PATH.read_text(encoding="utf-8"))


def _rank_paper(query_tokens: List[str], paper: Dict[str, Any]) -> float:
    title = paper.get("title") or ""
    abstract = paper.get("abstract") or ""
    text = f"{title} {abstract}"
    text_tokens = set(_tokenize(text))
    title_tokens = set(_tokenize(title))
    overlap = len(set(query_tokens) & text_tokens)
    title_overlap = len(set(query_tokens) & title_tokens)
    citations = float(paper.get("citations") or 0)
    recency = max(0, int(paper.get("year") or 0) - 2018)
    has_abstract = 1.0 if abstract else 0.0
    return overlap * 2.0 + title_overlap * 2.5 + min(citations, 50) * 0.03 + recency * 0.2 + has_abstract


def _derive_search_query(query: str, provider: str, provider_key: str, model: Optional[str]) -> str:
    from modules.ai_provider import call_ai

    if len(query) <= 24 and "?" not in query and "？" not in query:
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
            timeout=45,
        )
        return (response or "").strip().splitlines()[0].strip() or query
    except Exception:
        return query


def role1_retrieval(query: str, provider: str, provider_key: str, model: Optional[str]) -> Tuple[List[Dict[str, Any]], str]:
    effective_query = _derive_search_query(query, provider, provider_key, model)
    query_tokens = _tokenize(effective_query)
    frozen = _load_frozen_corpus()
    ranked = sorted(
        (dict(paper, _retrieval_score=_rank_paper(query_tokens, paper)) for paper in frozen),
        key=lambda row: row["_retrieval_score"],
        reverse=True,
    )
    filtered = [row for row in ranked if row["_retrieval_score"] > 0][:15]
    if not filtered:
        filtered = ranked[:15]
    for row in filtered:
        row.pop("_retrieval_score", None)
    return filtered, effective_query


def role2_screening(
    query: str,
    papers: List[Dict[str, Any]],
    top_k: int,
    provider: str,
    provider_key: str,
    model: Optional[str],
) -> List[Dict[str, Any]]:
    from modules.ai_provider import call_ai

    if not papers:
        return []

    paper_list = []
    for idx, paper in enumerate(papers[:15], 1):
        paper_list.append(
            f"[{idx}] Title: {paper.get('title', '')}\n"
            f"    Year: {paper.get('year', '')}  Citations: {paper.get('citations', 0) or 0}\n"
            f"    Abstract: {(paper.get('abstract', '') or '')[:300]}"
        )

    prompt = (
        f"Research query: {query}\n\n"
        f"Below are {len(paper_list)} candidate papers from the frozen corpus.\n"
        "For each paper, assign a relevance score from 0 to 10 and give a one-sentence rationale.\n"
        "Return ONLY a JSON array in this exact format:\n"
        '[{"index": 1, "score": 8, "rationale": "..."}, ...]\n\n'
        + "\n\n".join(paper_list)
    )

    try:
        response = call_ai(
            prompt=prompt,
            system="You are a research screening agent. Output only valid JSON.",
            provider=provider,
            api_key=provider_key,
            model=model,
            task_type="analysis",
            max_tokens=1200,
            temperature=0.1,
            timeout=ROLE_TIMEOUT_SECONDS,
        )
        match = re.search(r"\[.*\]", response.strip(), re.S)
        scored = json.loads(match.group()) if match else json.loads(response.strip())
        score_map = {item["index"]: item for item in scored if "index" in item}

        ranked: List[Dict[str, Any]] = []
        for idx, paper in enumerate(papers[:15], 1):
            info = score_map.get(idx, {})
            row = dict(paper)
            row["_screen_score"] = float(info.get("score", 0))
            row["_screen_rationale"] = info.get("rationale", "")
            ranked.append(row)
        ranked.sort(key=lambda row: row["_screen_score"], reverse=True)
        return ranked[:top_k]
    except Exception:
        fallback = [dict(paper) for paper in papers[:top_k]]
        for paper in fallback:
            paper["_screen_score"] = 0.0
            paper["_screen_rationale"] = "Fallback lexical ranking only."
        return fallback


def role3_evidence(
    query: str,
    papers: List[Dict[str, Any]],
    provider: str,
    provider_key: str,
    model: Optional[str],
) -> List[Dict[str, Any]]:
    from modules.ai_provider import call_ai

    if not papers:
        return []

    enriched: List[Dict[str, Any]] = []
    for paper in papers:
        abstract = (paper.get("abstract") or "").strip()
        if not abstract:
            row = dict(paper)
            row["evidence"] = {
                "key_claim": "",
                "methodology": "",
                "metrics_mentioned": [],
                "limitation": "",
            }
            enriched.append(row)
            continue

        prompt = (
            f"Research query: {query}\n\n"
            f"Paper title: {paper.get('title', '')}\n"
            f"Abstract: {abstract[:600]}\n\n"
            "Extract structured evidence from this abstract in relation to the research query.\n"
            "Return ONLY a JSON object in this format:\n"
            '{"key_claim": "...", "methodology": "...", "metrics_mentioned": ["..."], "limitation": "..."}\n'
            "If information is missing, use empty string or empty list."
        )

        try:
            response = call_ai(
                prompt=prompt,
                system="You are a research evidence extraction agent. Output only valid JSON.",
                provider=provider,
                api_key=provider_key,
                model=model,
                task_type="analysis",
                max_tokens=400,
                temperature=0.1,
                timeout=ROLE_TIMEOUT_SECONDS,
            )
            match = re.search(r"\{.*\}", response.strip(), re.S)
            evidence = json.loads(match.group()) if match else {}
        except Exception:
            evidence = {"key_claim": "", "methodology": "", "metrics_mentioned": [], "limitation": ""}

        row = dict(paper)
        row["evidence"] = evidence
        enriched.append(row)

    return enriched


SYNTHESIS_SYSTEM = (
    "You are an academic intelligence synthesis agent. "
    "Write in Chinese. Ground every factual claim in the supplied evidence. "
    "Do not invent facts beyond the provided evidence. "
    "Use numbered citations [N] that match the paper numbers in the evidence list. "
    "End the report with a '## 参考文献' section listing all cited papers."
)


def role4_synthesis(
    query: str,
    papers: List[Dict[str, Any]],
    provider: str,
    provider_key: str,
    model: Optional[str],
) -> str:
    from modules.ai_provider import call_ai

    evidence_blocks = []
    bib_lines = []
    for idx, paper in enumerate(papers, 1):
        evidence = paper.get("evidence", {})
        evidence_blocks.append(
            f"[{idx}] {paper.get('title', '')} ({paper.get('year', '')})\n"
            f"    Key claim: {evidence.get('key_claim', 'N/A')}\n"
            f"    Methodology: {evidence.get('methodology', 'N/A')}\n"
            f"    Metrics: {', '.join(evidence.get('metrics_mentioned', [])) or 'N/A'}\n"
            f"    Limitation: {evidence.get('limitation', 'N/A')}"
        )
        bib_lines.append(
            f"[{idx}] {paper.get('title', 'N/A')}. {paper.get('journal', '') or paper.get('source', '')}. {paper.get('year', '')}."
        )

    prompt = (
        f"Research query: {query}\n\n"
        f"You have {len(papers)} screened papers from the frozen pilot corpus:\n\n"
        + "\n\n".join(evidence_blocks)
        + "\n\n"
        "Write a structured intelligence report in Chinese with these sections:\n"
        "1. 检索与筛选概览\n"
        "2. 核心主题与证据\n"
        "3. 证据支持的研究方向\n"
        "4. 摘要级证据的局限\n"
        "5. 谨慎结论\n\n"
        "Important rules:\n"
        "- Every factual claim must include at least one [N] citation.\n"
        "- Do not claim conclusions beyond what the abstracts support.\n"
        "- Explicitly state that this Method 1 pilot still works at abstract-level evidence, not full-text reading.\n"
        "- After the main report, add a section:\n\n"
        "## 参考文献\n"
        + "\n".join(bib_lines)
    )

    return call_ai(
        prompt=prompt,
        system=SYNTHESIS_SYSTEM,
        provider=provider,
        api_key=provider_key,
        model=model,
        task_type="analysis",
        max_tokens=3000,
        temperature=0.3,
        timeout=ROLE_TIMEOUT_SECONDS,
    )


def run_method1(query: str, qid: str, provider: str, model: str, output_dir: Path = OUTPUT_DIR) -> None:
    from modules.ai_provider import call_ai  # noqa: F401  # imported to ensure provider wiring
    from modules.meta_opt import sync_baseline_result
    from modules.research_wiki import ingest_baseline_result
    from modules.searcher import _load_saved_search_config

    cfg = _load_saved_search_config()
    provider_key = cfg.get(f"{provider}_api_key", "") or ""
    model_arg = model or None
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"{qid}_method1_{stamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / f"{stem}.md"
    json_path = output_dir / f"{stem}.json"

    started = time.time()

    print("  [R1] Retrieval (frozen corpus)...")
    papers_raw, effective_query = role1_retrieval(query, provider, provider_key, model_arg)
    print(f"       Retrieved {len(papers_raw)} papers")

    print("  [R2] Screening (top 8)...")
    screened = role2_screening(query, papers_raw, top_k=8, provider=provider, provider_key=provider_key, model=model_arg)
    print(f"       Screened to {len(screened)} papers")

    print("  [R3] Evidence extraction...")
    enriched = role3_evidence(query, screened, provider=provider, provider_key=provider_key, model=model_arg)
    print(f"       Evidence extracted for {len(enriched)} papers")

    print("  [R4] Synthesis...")
    report_md = role4_synthesis(query, enriched, provider=provider, provider_key=provider_key, model=model_arg)
    md_path.write_text(report_md, encoding="utf-8")

    elapsed_seconds = round(time.time() - started, 3)
    sidecar = {
        "baseline": "method1_pipeline",
        "query": query,
        "effective_search_query": effective_query,
        "provider": provider,
        "model": model,
        "corpus_mode": "frozen_topic_run",
        "retrieved_count": len(papers_raw),
        "screened_count": len(screened),
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
                "baseline": "method1_pipeline",
                "query_id": qid,
                "query": query,
                "error": f"sync_failed: {exc}",
                "timestamp": stamp,
            },
            err_path=output_dir / "errors.jsonl",
        )

    print(f"  Saved markdown: {md_path.name}")
    print(f"  Saved metadata: {json_path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch run Method 1 (Pipeline-Multi-Agent, frozen corpus mode).")
    parser.add_argument("--provider", default="deepseek")
    parser.add_argument("--model", default="")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=30)
    parser.add_argument("--query-id", default=None, help="Run a single query by ID, e.g. Q05")
    parser.add_argument("--benchmark-path", default=str(BENCHMARK_PATH))
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    parser.add_argument("--sleep", type=float, default=12.0)
    args = parser.parse_args()

    benchmark_path = Path(args.benchmark_path)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    err_path = output_dir / "errors.jsonl"

    queries = json.loads(benchmark_path.read_text(encoding="utf-8"))
    print(f"Loaded {len(queries)} benchmark queries.")
    print(f"Benchmark path: {benchmark_path}")
    print(f"Frozen corpus: {FROZEN_CORPUS_PATH}")
    print(f"Output directory: {output_dir}")
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

        existing = list(output_dir.glob(f"{qid}_method1_*.md"))
        if existing:
            print(f"[{qid}] Already exists, skipping.")
            continue

        print(f"\n[{qid}] {query_text[:60]}...")
        try:
            run_method1(query_text, qid, args.provider, args.model, output_dir=output_dir)
            success += 1
        except Exception as exc:
            print(f"  ERROR: {exc}")
            _log_error(
                {
                    "baseline": "method1_pipeline",
                    "query_id": qid,
                    "query": query_text,
                    "error": str(exc),
                    "timestamp": datetime.now().isoformat(),
                },
                err_path=err_path,
            )
            failed += 1
        print(f"  Sleeping {args.sleep}s...")
        time.sleep(args.sleep)

    print("\n" + "=" * 60)
    print(f"Done. Success: {success}  Failed: {failed}")
    print("Run evaluate_metrics.py --dir data/method1_outputs to score Method 1.")


if __name__ == "__main__":
    main()
