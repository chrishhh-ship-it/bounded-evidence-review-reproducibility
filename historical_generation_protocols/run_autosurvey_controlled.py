from __future__ import annotations

import argparse
import concurrent.futures
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
    _compact,
    _log_error,
    _paper_id,
    _rank_paper,
    _tokenize,
    role1_retrieval,
)


BENCHMARK_PATH = PROJECT_ROOT / "data" / "benchmarks" / "pilot_queries_v2.json"
OUTPUT_DIR = PROJECT_ROOT / "data" / "autosurvey_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ERR_PATH = OUTPUT_DIR / "errors.jsonl"


# Adapted from the AutoSurvey prompt structure to support a corpus-controlled comparison
# under the project's numeric-citation evaluation protocol.
ROUGH_OUTLINE_PROMPT = """
You are writing a comprehensive academic survey about "[TOPIC]".
You are provided with a chunk of candidate papers:
---
[PAPER LIST]
---
Draft a rough section-level outline for the survey.
The outline must contain one title and [SECTION NUM] sections.
Each section must be followed by one brief description sentence.

Return ONLY in this format:
Title: [TITLE]
Section 1: [SECTION NAME]
Description 1: [SECTION DESCRIPTION]
...
Section K: [SECTION NAME]
Description K: [SECTION DESCRIPTION]
"""

MERGING_OUTLINE_PROMPT = """
You are writing a comprehensive academic survey about [TOPIC].
Below are several candidate outlines:
---
[OUTLINE LIST]
---
Merge them into one coherent section-level outline.
Return ONLY in this format:
Title: [TITLE]
Section 1: [SECTION NAME]
Description 1: [SECTION DESCRIPTION]
...
Section K: [SECTION NAME]
Description K: [SECTION DESCRIPTION]
"""

SUBSECTION_OUTLINE_PROMPT = """
You are writing a comprehensive academic survey about [TOPIC].
Overall section-level outline:
---
[OVERALL OUTLINE]
---
Target section: [SECTION NAME]
Section description: [SECTION DESCRIPTION]

Candidate papers for this section:
---
[PAPER LIST]
---

Generate 2-4 subsection headings for this section.
Each subsection must have one brief description.

Return ONLY in this format:
Subsection 1: [SUBSECTION NAME]
Description 1: [SUBSECTION DESCRIPTION]
...
Subsection K: [SUBSECTION NAME]
Description K: [SUBSECTION DESCRIPTION]
"""

SUBSECTION_WRITING_PROMPT = """
You are writing one subsection of an academic survey about [TOPIC].
Overall outline:
---
[OVERALL OUTLINE]
---
Section: [SECTION NAME]
Subsection: [SUBSECTION NAME]
Subsection description:
---
[DESCRIPTION]
---

Available evidence papers:
---
[PAPER LIST]
---

Requirements:
1. Write in Chinese.
2. Write at least [WORD NUM] Chinese words.
3. Use only the papers listed above.
4. Cite using ONLY numeric citations like [1][3].
5. Do not cite papers not shown above.
6. Do not use citation ranges like [1-3].
7. Keep claims at abstract-level evidence only.

Return ONLY the subsection content.
"""

CHECK_CITATION_PROMPT = """
You are checking citation validity for a survey subsection about [TOPIC].

Available evidence papers:
---
[PAPER LIST]
---

Subsection:
---
[SUBSECTION]
---

Task:
1. Check whether each citation [N] is supported by the corresponding paper.
2. If a citation is unsupported, replace it with supported citations from the list above or remove it.
3. Do not change the substantive meaning unless needed to keep the subsection evidence-grounded.
4. Do not introduce any citation not listed above.
5. Keep numeric citations like [1][2].

Return ONLY the corrected subsection.
"""

LCE_PROMPT = """
You are refining one subsection of an academic survey about [TOPIC] for coherence.

Previous subsection:
---
[PREVIOUS]
---

Current subsection:
---
[SUBSECTION]
---

Following subsection:
---
[FOLLOWING]
---

Refine the current subsection so the transitions are smoother and redundancies are reduced.
Keep all citations unchanged.
Return ONLY the refined current subsection.
"""


ROLE_TIMEOUT_SECONDS = 180


def _call_ai(
    *,
    prompt: str,
    system: str,
    provider: str,
    api_key: str,
    model: Optional[str],
    max_tokens: int,
    temperature: float,
) -> str:
    from modules.ai_provider import call_ai

    last_exc: Exception | None = None
    for attempt in range(3):
        try:
            return call_ai(
                prompt=prompt,
                system=system,
                provider=provider,
                api_key=api_key,
                model=model,
                task_type="analysis",
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=ROLE_TIMEOUT_SECONDS,
            )
        except Exception as exc:
            last_exc = exc
            if attempt == 2:
                break
            wait_seconds = [5, 15, 30][attempt]
            print(f"    [retry {attempt + 1}/3] AI call failed: {exc}. waiting {wait_seconds}s...")
            time.sleep(wait_seconds)
    raise last_exc if last_exc else RuntimeError("Unknown AI call failure")


def _chunk_list(rows: List[Any], chunk_count: int = 3) -> List[List[Any]]:
    if not rows:
        return []
    chunk_size = max(1, (len(rows) + chunk_count - 1) // chunk_count)
    return [rows[i : i + chunk_size] for i in range(0, len(rows), chunk_size)]


def _paper_list_text(papers: List[Dict[str, Any]], numeric_ids: Dict[str, int]) -> str:
    blocks: List[str] = []
    for paper in papers:
        pid = _paper_id(paper)
        idx = numeric_ids[pid]
        blocks.append(
            f"[{idx}] {paper.get('title', '')} ({paper.get('year', '')})\n"
            f"Source: {paper.get('source', '')}\n"
            f"Journal: {paper.get('journal', '')}\n"
            f"Abstract: {(paper.get('abstract', '') or '')[:900]}"
        )
    return "\n\n".join(blocks)


def _parse_numbered_outline(text: str, item_prefix: str) -> List[Dict[str, str]]:
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    items: List[Dict[str, str]] = []
    current: Dict[str, str] | None = None
    item_re = re.compile(rf"^{re.escape(item_prefix)}\s+(\d+)\s*:\s*(.+)$", re.I)
    desc_re = re.compile(r"^Description\s+(\d+)\s*:\s*(.+)$", re.I)
    for line in lines:
        match_item = item_re.match(line)
        if match_item:
            if current:
                items.append(current)
            current = {"name": match_item.group(2).strip(), "description": ""}
            continue
        match_desc = desc_re.match(line)
        if match_desc and current is not None:
            current["description"] = match_desc.group(2).strip()
    if current:
        items.append(current)
    return items


def _parse_section_outline(text: str) -> Dict[str, Any]:
    title_match = re.search(r"^Title\s*:\s*(.+)$", text or "", re.I | re.M)
    title = title_match.group(1).strip() if title_match else "AutoSurvey-Style Literature Survey"
    sections = _parse_numbered_outline(text, "Section")
    if not sections:
        sections = [
            {"name": "Background and Scope", "description": "Define the topic and explain the review scope."},
            {"name": "Main Research Themes", "description": "Synthesize the main clusters and representative approaches."},
            {"name": "Evaluation and Evidence", "description": "Summarize evaluation patterns, evidence types, and limitations."},
            {"name": "Challenges and Future Directions", "description": "Highlight unresolved issues and future opportunities."},
        ]
    return {"title": title, "sections": sections}


def _parse_subsection_outline(text: str) -> List[Dict[str, str]]:
    items = _parse_numbered_outline(text, "Subsection")
    if items:
        return items
    return [
        {"name": "Key Findings", "description": "Summarize the core evidence and representative studies."},
        {"name": "Limitations", "description": "Discuss evidence gaps and methodological cautions."},
    ]


def _outline_to_text(outline: Dict[str, Any]) -> str:
    lines: List[str] = [f"Title: {outline['title']}"]
    for idx, section in enumerate(outline["sections"], 1):
        lines.append(f"Section {idx}: {section['name']}")
        lines.append(f"Description {idx}: {section['description']}")
    return "\n".join(lines)


def _outline_to_markdown(outline: Dict[str, Any]) -> str:
    lines: List[str] = [f"# {outline['title']}", ""]
    for sec_idx, section in enumerate(outline["sections"], 1):
        lines.append(f"## {sec_idx}. {section['name']}")
        if section.get("description"):
            lines.append(f"*{section['description']}*")
        lines.append("")
        for sub_idx, subsection in enumerate(section.get("subsections", []), 1):
            lines.append(f"### {sec_idx}.{sub_idx} {subsection['name']}")
            if subsection.get("description"):
                lines.append(f"*{subsection['description']}*")
            lines.append("")
    return "\n".join(lines).strip()


def _select_local_packet(query_or_desc: str, candidates: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
    query_tokens = _tokenize(query_or_desc)
    ranked = sorted(
        (dict(paper, _local_score=_rank_paper(query_tokens, paper)) for paper in candidates),
        key=lambda row: row["_local_score"],
        reverse=True,
    )
    rows = [row for row in ranked if row["_local_score"] > 0][:top_k]
    if not rows:
        rows = ranked[:top_k]
    for row in rows:
        row.pop("_local_score", None)
    return rows


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


def _extract_citation_ids(text: str) -> List[int]:
    ids: set[int] = set()
    for match in re.finditer(r"\[(\d+)\]", text or ""):
        ids.add(int(match.group(1)))
    return sorted(ids)


def _build_bibliography(cited_ids: List[int], paper_by_num: Dict[int, Dict[str, Any]]) -> str:
    lines = ["## 参考文献"]
    for idx in cited_ids:
        paper = paper_by_num.get(idx, {})
        title = paper.get("title", "Unknown title")
        venue = paper.get("journal", "") or paper.get("source", "")
        year = paper.get("year", "")
        doi = paper.get("doi", "")
        doi_suffix = f" DOI: {doi}" if doi else ""
        lines.append(f"[{idx}] {title}. {venue}. {year}.{doi_suffix}".strip())
    return "\n".join(lines)


def _preview(text: str, limit: int = 56) -> str:
    clean = re.sub(r"\s+", " ", (text or "")).strip()
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3] + "..."


def _draft_and_check_subsection(
    *,
    query: str,
    outline_markdown: str,
    section_name: str,
    subsection: Dict[str, str],
    local_packet: List[Dict[str, Any]],
    numeric_ids: Dict[str, int],
    provider: str,
    provider_key: str,
    model: Optional[str],
    subsection_len: int,
) -> str:
    packet_text = _paper_list_text(local_packet, numeric_ids)
    prompt = SUBSECTION_WRITING_PROMPT.replace("[TOPIC]", query)
    prompt = prompt.replace("[OVERALL OUTLINE]", outline_markdown)
    prompt = prompt.replace("[SECTION NAME]", section_name)
    prompt = prompt.replace("[SUBSECTION NAME]", subsection["name"])
    prompt = prompt.replace("[DESCRIPTION]", subsection["description"])
    prompt = prompt.replace("[PAPER LIST]", packet_text)
    prompt = prompt.replace("[WORD NUM]", str(subsection_len))
    subsection_text = _call_ai(
        prompt=prompt,
        system="You write one subsection of a literature survey. Use only supplied papers and numeric citations.",
        provider=provider,
        api_key=provider_key,
        model=model,
        max_tokens=max(1200, subsection_len * 3),
        temperature=0.6,
    )
    check_prompt = CHECK_CITATION_PROMPT.replace("[TOPIC]", query)
    check_prompt = check_prompt.replace("[PAPER LIST]", packet_text)
    check_prompt = check_prompt.replace("[SUBSECTION]", subsection_text)
    subsection_text = _call_ai(
        prompt=check_prompt,
        system="You correct unsupported citations in a survey subsection and keep only evidence-grounded numeric citations.",
        provider=provider,
        api_key=provider_key,
        model=model,
        max_tokens=max(1200, subsection_len * 3),
        temperature=0.2,
    )
    return _sanitize_citation_ranges(subsection_text.strip())


def _refine_subsection(
    *,
    query: str,
    previous: str,
    current: str,
    following: str,
    provider: str,
    provider_key: str,
    model: Optional[str],
    subsection_len: int,
) -> str:
    prompt = LCE_PROMPT.replace("[TOPIC]", query)
    prompt = prompt.replace("[PREVIOUS]", previous)
    prompt = prompt.replace("[SUBSECTION]", current)
    prompt = prompt.replace("[FOLLOWING]", following)
    refined = _call_ai(
        prompt=prompt,
        system="You refine one subsection for coherence without changing any citations.",
        provider=provider,
        api_key=provider_key,
        model=model,
        max_tokens=max(1200, subsection_len * 3),
        temperature=0.3,
    )
    return _sanitize_citation_ranges(refined.strip())


def _compile_document(outline: Dict[str, Any], subsection_contents: List[List[str]], bibliography: str) -> str:
    lines: List[str] = [f"# {outline['title']}", ""]
    for sec_idx, section in enumerate(outline["sections"], 1):
        lines.append(f"## {sec_idx}. {section['name']}")
        lines.append("")
        for sub_idx, subsection in enumerate(section.get("subsections", []), 1):
            lines.append(f"### {sec_idx}.{sub_idx} {subsection['name']}")
            lines.append("")
            if sec_idx - 1 < len(subsection_contents) and sub_idx - 1 < len(subsection_contents[sec_idx - 1]):
                lines.append(subsection_contents[sec_idx - 1][sub_idx - 1].strip())
                lines.append("")
    lines.append(bibliography)
    return "\n".join(lines).strip() + "\n"


def _draft_autosurvey_outline(
    *,
    topic: str,
    candidates: List[Dict[str, Any]],
    numeric_ids: Dict[str, int],
    provider: str,
    provider_key: str,
    model: Optional[str],
    section_num: int,
    max_workers: int,
) -> Dict[str, Any]:
    chunks = _chunk_list(candidates, chunk_count=3)
    rough_outlines: List[str] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(max_workers, len(chunks) or 1)) as executor:
        future_map: Dict[concurrent.futures.Future[str], int] = {}
        for chunk_idx, chunk in enumerate(chunks, 1):
            prompt = ROUGH_OUTLINE_PROMPT.replace("[TOPIC]", topic).replace(
                "[PAPER LIST]", _paper_list_text(chunk, numeric_ids)
            ).replace("[SECTION NUM]", str(section_num))
            future = executor.submit(
                _call_ai,
                prompt=prompt,
                system="You draft section-level outlines for literature surveys. Return only the requested format.",
                provider=provider,
                api_key=provider_key,
                model=model,
                max_tokens=900,
                temperature=0.7,
            )
            future_map[future] = chunk_idx
        rough_outline_map: Dict[int, str] = {}
        for future in concurrent.futures.as_completed(future_map):
            chunk_idx = future_map[future]
            rough_outline_map[chunk_idx] = future.result().strip()
            print(f"    [outline] rough chunk {chunk_idx}/{len(chunks)} ready")
        rough_outlines = [rough_outline_map[idx] for idx in sorted(rough_outline_map)]

    outline_list = []
    for idx, outline in enumerate(rough_outlines, 1):
        outline_list.append(f"---\noutline_id: {idx}\n{outline}")
    prompt = MERGING_OUTLINE_PROMPT.replace("[TOPIC]", topic).replace(
        "[OUTLINE LIST]", "\n".join(outline_list)
    )
    merged = _call_ai(
        prompt=prompt,
        system="You merge candidate survey outlines into one coherent survey plan. Return only the requested format.",
        provider=provider,
        api_key=provider_key,
        model=model,
        max_tokens=1000,
        temperature=0.5,
    )
    outline = _parse_section_outline(merged)

    overall_outline_text = _outline_to_text(outline)
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=min(max_workers, len(outline["sections"]) or 1)
    ) as executor:
        future_map = {}
        for sec_idx, section in enumerate(outline["sections"]):
            section_packet = _select_local_packet(section["description"], candidates, top_k=6)
            prompt = SUBSECTION_OUTLINE_PROMPT.replace("[TOPIC]", topic)
            prompt = prompt.replace("[OVERALL OUTLINE]", overall_outline_text)
            prompt = prompt.replace("[SECTION NAME]", section["name"])
            prompt = prompt.replace("[SECTION DESCRIPTION]", section["description"])
            prompt = prompt.replace("[PAPER LIST]", _paper_list_text(section_packet, numeric_ids))
            future = executor.submit(
                _call_ai,
                prompt=prompt,
                system="You generate subsection structures for one survey section. Return only the requested format.",
                provider=provider,
                api_key=provider_key,
                model=model,
                max_tokens=900,
                temperature=0.7,
            )
            future_map[future] = sec_idx
        for future in concurrent.futures.as_completed(future_map):
            sec_idx = future_map[future]
            sub_outline = future.result()
            outline["sections"][sec_idx]["subsections"] = _parse_subsection_outline(sub_outline)
            section_name = outline["sections"][sec_idx]["name"]
            print(
                f"    [outline] section {sec_idx + 1}/{len(outline['sections'])} "
                f"sub-outline ready: {_preview(section_name)}"
            )

    return outline


def run_autosurvey_controlled(
    *,
    query: str,
    qid: str,
    provider: str,
    model: str,
    output_dir: Path,
    section_num: int,
    subsection_len: int,
    candidate_num: int,
    subsection_rag_num: int,
    max_workers: int,
) -> None:
    from modules.meta_opt import sync_baseline_result
    from modules.research_wiki import ingest_baseline_result
    from modules.searcher import _load_saved_search_config

    cfg = _load_saved_search_config()
    provider_key = cfg.get(f"{provider}_api_key", "") or ""
    model_arg = model or None

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"{qid}_autosurvey_{stamp}"
    md_path = output_dir / f"{stem}.md"
    json_path = output_dir / f"{stem}.json"

    started = time.time()

    print("  [AS1] Retrieval (frozen corpus candidate packet)...")
    papers_raw, effective_query = role1_retrieval(query, provider, provider_key, model_arg)
    candidate_papers = papers_raw[:candidate_num]
    print(f"       Candidate papers: {len(candidate_papers)}")

    numeric_ids = {_paper_id(paper): idx for idx, paper in enumerate(candidate_papers, 1)}
    paper_by_num = {idx: paper for idx, paper in enumerate(candidate_papers, 1)}

    print("  [AS2] AutoSurvey-style outline generation...")
    outline = _draft_autosurvey_outline(
        topic=query,
        candidates=candidate_papers,
        numeric_ids=numeric_ids,
        provider=provider,
        provider_key=provider_key,
        model=model_arg,
        section_num=section_num,
        max_workers=max_workers,
    )
    outline_markdown = _outline_to_markdown(outline)

    print("  [AS3] Subsection drafting + citation checking...")
    section_contents: List[List[str]] = [
        ["" for _ in section.get("subsections", [])] for section in outline["sections"]
    ]
    total_subsections = sum(len(section.get("subsections", [])) for section in outline["sections"])
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map: Dict[concurrent.futures.Future[str], tuple[int, int]] = {}
        for sec_idx, section in enumerate(outline["sections"]):
            for sub_idx, subsection in enumerate(section.get("subsections", [])):
                local_packet = _select_local_packet(
                    f"{section['description']} {subsection['description']}",
                    candidate_papers,
                    top_k=subsection_rag_num,
                )
                future = executor.submit(
                    _draft_and_check_subsection,
                    query=query,
                    outline_markdown=outline_markdown,
                    section_name=section["name"],
                    subsection=subsection,
                    local_packet=local_packet,
                    numeric_ids=numeric_ids,
                    provider=provider,
                    provider_key=provider_key,
                    model=model_arg,
                    subsection_len=subsection_len,
                )
                future_map[future] = (sec_idx, sub_idx)
        completed_subsections = 0
        for future in concurrent.futures.as_completed(future_map):
            sec_idx, sub_idx = future_map[future]
            section_contents[sec_idx][sub_idx] = future.result()
            completed_subsections += 1
            print(
                f"    [draft] {completed_subsections}/{total_subsections} "
                f"section {sec_idx + 1}.{sub_idx + 1} ready"
            )

    print("  [AS4] Local coherence refinement...")
    original_contents = [row[:] for row in section_contents]
    refined_contents: List[List[str]] = [row[:] for row in section_contents]
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {}
        for sec_idx, contents in enumerate(original_contents):
            for idx, content in enumerate(contents):
                prev_text = contents[idx - 1] if idx > 0 else ""
                next_text = contents[idx + 1] if idx + 1 < len(contents) else ""
                future = executor.submit(
                    _refine_subsection,
                    query=query,
                    previous=prev_text,
                    current=content,
                    following=next_text,
                    provider=provider,
                    provider_key=provider_key,
                    model=model_arg,
                    subsection_len=subsection_len,
                )
                future_map[future] = (sec_idx, idx)
        completed_refines = 0
        for future in concurrent.futures.as_completed(future_map):
            sec_idx, idx = future_map[future]
            refined_contents[sec_idx][idx] = future.result()
            completed_refines += 1
            print(
                f"    [refine] {completed_refines}/{total_subsections} "
                f"section {sec_idx + 1}.{idx + 1} polished"
            )
    section_contents = refined_contents

    all_cited_ids: List[int] = []
    for row in section_contents:
        for content in row:
            all_cited_ids.extend(_extract_citation_ids(content))
    cited_ids = sorted(set(idx for idx in all_cited_ids if idx in paper_by_num))

    bibliography = _build_bibliography(cited_ids, paper_by_num)
    final_doc = _compile_document(outline, section_contents, bibliography)
    md_path.write_text(final_doc, encoding="utf-8")

    elapsed_seconds = round(time.time() - started, 3)
    sidecar = {
        "baseline": "autosurvey_corpus_controlled",
        "query": query,
        "effective_search_query": effective_query,
        "provider": provider,
        "model": model,
        "corpus_mode": "frozen_topic_run",
        "comparison_mode": "corpus_controlled_external_system",
        "retrieved_count": len(candidate_papers),
        "all_retrieved_ids": [_paper_id(paper) for paper in candidate_papers],
        "top_papers": [_compact(paper) for paper in candidate_papers],
        "outline": outline_markdown,
        "cited_ids": cited_ids,
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
                "baseline": "autosurvey_corpus_controlled",
                "query_id": qid,
                "query": query,
                "provider": provider,
                "error": f"sync_failed: {exc}",
                "timestamp": stamp,
            },
            err_path=ERR_PATH,
        )

    print(f"  Saved markdown: {md_path.name}")
    print(f"  Saved metadata: {json_path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run an AutoSurvey-style external comparison under a corpus-controlled evidence boundary."
    )
    parser.add_argument("--provider", default="deepseek")
    parser.add_argument("--model", default="deepseek-chat")
    parser.add_argument("--benchmark-path", default=str(BENCHMARK_PATH))
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    parser.add_argument("--query-id", default=None, help="Run a single query by ID, e.g. Q05")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=30)
    parser.add_argument("--section-num", type=int, default=4)
    parser.add_argument("--subsection-len", type=int, default=220)
    parser.add_argument("--candidate-num", type=int, default=15)
    parser.add_argument("--subsection-rag-num", type=int, default=6)
    parser.add_argument("--max-workers", type=int, default=3)
    parser.add_argument("--sleep", type=float, default=3.0)
    args = parser.parse_args()

    benchmark_path = Path(args.benchmark_path)
    queries = json.loads(benchmark_path.read_text(encoding="utf-8"))
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loaded {len(queries)} benchmark queries.")
    print(f"Benchmark path: {benchmark_path}")
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

        existing = list(output_dir.glob(f"{qid}_autosurvey_*.md"))
        if existing:
            print(f"[{qid}] Already exists, skipping.")
            success += 1
            continue

        print(f"\n[{qid}] {query_text}")
        try:
            run_autosurvey_controlled(
                query=query_text,
                qid=qid,
                provider=args.provider,
                model=args.model,
                output_dir=output_dir,
                section_num=args.section_num,
                subsection_len=args.subsection_len,
                candidate_num=args.candidate_num,
                subsection_rag_num=args.subsection_rag_num,
                max_workers=args.max_workers,
            )
            success += 1
        except Exception as exc:
            failed += 1
            _log_error(
                {
                    "baseline": "autosurvey_corpus_controlled",
                    "query_id": qid,
                    "query": query_text,
                    "provider": args.provider,
                    "error": str(exc),
                    "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                },
                err_path=ERR_PATH,
            )
            print(f"  FAILED: {exc}")
        time.sleep(args.sleep)

    print("\n" + "=" * 60)
    print(f"AutoSurvey-CC finished. success={success}, failed={failed}")


if __name__ == "__main__":
    main()
