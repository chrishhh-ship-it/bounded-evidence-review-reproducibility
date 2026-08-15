from __future__ import annotations

import argparse
import hashlib
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SOURCE_DIR = PROJECT_ROOT / "data" / "expanded_outputs" / "method1"
DEFAULT_OUTPUT_DIR = (
    PROJECT_ROOT / "data" / "expanded_outputs" / "schema_single_agent_v1"
)
PRINT_LOCK = threading.Lock()


def _paper_id(paper: dict[str, Any]) -> str:
    doi = (paper.get("doi") or "").strip().lower()
    if doi:
        return f"doi:{doi}"
    title = " ".join((paper.get("title") or "").lower().split())
    year = str(paper.get("year") or "").strip()
    return f"title:{title}|{year}"


def _canonical_source_sidecars() -> dict[str, Path]:
    import evaluate_metrics as em

    latest = em._select_latest_per_query(list(SOURCE_DIR.glob("*.md")))
    result: dict[str, Path] = {}
    for path in latest.values():
        parsed = em._parse_result_stem(path.stem)
        if parsed:
            result[parsed[0]] = path.with_suffix(".json")
    return result


def _prompt_for(sidecar: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    papers = sidecar.get("top_papers") or []
    evidence_blocks: list[str] = []
    bibliography: list[str] = []
    for index, paper in enumerate(papers, start=1):
        title = paper.get("title") or "Untitled"
        venue = paper.get("journal") or paper.get("source") or ""
        year = paper.get("year") or ""
        abstract = (paper.get("abstract") or "").strip()
        evidence_blocks.append(
            f"[{index}] stable_id={_paper_id(paper)}\n"
            f"Title: {title}\n"
            f"Year: {year}\n"
            f"Venue: {venue}\n"
            f"Abstract-level evidence: {abstract}"
        )
        bibliography.append(f"[{index}] {title}. {venue}. {year}.")

    prompt = (
        f"Research query: {sidecar.get('query', '')}\n\n"
        "Query-specific bounded evidence set E_q follows. Each record has a fixed "
        "numeric citation identifier. Use only these records and identifiers.\n\n"
        + "\n\n".join(evidence_blocks)
        + "\n\n"
        "Write one Chinese academic intelligence synthesis with exactly these sections:\n"
        "1. 检索与筛选概览\n"
        "2. 核心主题与证据\n"
        "3. 证据支持的研究方向\n"
        "4. 摘要级证据的局限\n"
        "5. 谨慎结论\n\n"
        "Output constraints:\n"
        "- This is a single-agent baseline: perform synthesis in one pass.\n"
        "- Every factual claim must cite one or more supplied identifiers in [N] form.\n"
        "- Never cite an identifier outside the supplied E_q.\n"
        "- Do not invent titles, authors, findings, or full-text evidence.\n"
        "- End with exactly this bibliography, without adding or deleting entries:\n\n"
        "## 参考文献\n"
        + "\n".join(bibliography)
    )
    return prompt, papers


def _run_one(
    qid: str,
    source_json: Path,
    output_dir: Path,
    provider: str,
    model: str,
    provider_key: str,
    overwrite: bool,
) -> dict[str, Any]:
    from modules.ai_provider import call_ai

    existing = sorted(output_dir.glob(f"{qid}_schema_single_agent_*.md"))
    if existing and not overwrite:
        return {"qid": qid, "status": "skipped", "file": str(existing[-1])}

    source = json.loads(source_json.read_text(encoding="utf-8"))
    prompt, papers = _prompt_for(source)
    system = (
        "You are a single academic synthesis agent in a controlled RAG baseline. "
        "Follow the provided citation schema exactly and use only E_q."
    )
    started = time.time()
    response = call_ai(
        prompt=prompt,
        system=system,
        provider=provider,
        api_key=provider_key,
        model=model or None,
        task_type="analysis",
        max_tokens=3000,
        temperature=0.3,
        timeout=180,
    )
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"{qid}_schema_single_agent_{stamp}"
    md_path = output_dir / f"{stem}.md"
    json_path = output_dir / f"{stem}.json"
    md_path.write_text(response, encoding="utf-8")
    metadata = {
        "baseline": "schema_matched_single_agent_v1",
        "query_id": qid,
        "query": source.get("query", ""),
        "domain_id": source.get("domain_id", ""),
        "provider": provider,
        "model": model,
        "source_evidence_sidecar": str(source_json.relative_to(PROJECT_ROOT)),
        "same_query_evidence_ids": [_paper_id(paper) for paper in papers],
        "all_retrieved_ids": [_paper_id(paper) for paper in papers],
        "top_papers": papers,
        "evidence_records": len(papers),
        "max_tokens": 3000,
        "temperature": 0.3,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "elapsed_seconds": round(time.time() - started, 3),
        "output_markdown": str(md_path.relative_to(PROJECT_ROOT)),
        "scope_note": (
            "Same query-specific screened records and fixed numeric identifiers as "
            "the archived M1 evidence state; one synthesis call, no role decomposition "
            "and no reviewer/reviser."
        ),
    }
    json_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {"qid": qid, "status": "completed", "file": str(md_path)}


def main() -> None:
    from modules.searcher import _load_saved_search_config

    parser = argparse.ArgumentParser(
        description=(
            "Run the reviewer-requested schema-matched single-agent baseline over "
            "the preserved query-specific evidence states."
        )
    )
    parser.add_argument("--provider", default="deepseek")
    parser.add_argument("--model", default="deepseek-chat")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--query-id", default="")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=251)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    sidecars = _canonical_source_sidecars()
    selected: list[tuple[str, Path]] = []
    for qid, path in sorted(sidecars.items(), key=lambda item: int(item[0][1:])):
        number = int(qid[1:])
        if args.query_id and qid != args.query_id:
            continue
        if not args.query_id and not (args.start <= number <= args.end):
            continue
        selected.append((qid, path))

    config = _load_saved_search_config()
    provider_key = config.get(f"{args.provider}_api_key", "") or ""
    if not provider_key:
        raise SystemExit(f"Missing API key for provider={args.provider}")

    manifest = {
        "started_at": datetime.now().isoformat(),
        "provider": args.provider,
        "model": args.model,
        "workers": args.workers,
        "selected_qids": [qid for qid, _ in selected],
        "results": [],
    }
    manifest_path = output_dir / "run_manifest.json"

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {
            executor.submit(
                _run_one,
                qid,
                path,
                output_dir,
                args.provider,
                args.model,
                provider_key,
                args.overwrite,
            ): qid
            for qid, path in selected
        }
        for future in as_completed(futures):
            qid = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                result = {
                    "qid": qid,
                    "status": "failed",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            manifest["results"].append(result)
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            with PRINT_LOCK:
                print(json.dumps(result, ensure_ascii=False))

    manifest["finished_at"] = datetime.now().isoformat()
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
