from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import tiktoken
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUTO_SURVEY_ROOT = PROJECT_ROOT.parent / "AutoSurvey"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(AUTO_SURVEY_ROOT) not in sys.path:
    sys.path.insert(0, str(AUTO_SURVEY_ROOT))

from batch_run_method1 import _compact, _log_error, _paper_id  # noqa: E402
from modules.ai_provider import call_ai  # noqa: E402
from modules.searcher import _load_saved_search_config  # noqa: E402
from src.prompt import (  # noqa: E402
    CHECK_CITATION_PROMPT,
    EDIT_FINAL_OUTLINE_PROMPT,
    LCE_PROMPT,
    MERGING_OUTLINE_PROMPT,
    ROUGH_OUTLINE_PROMPT,
    SUBSECTION_OUTLINE_PROMPT,
    SUBSECTION_WRITING_PROMPT,
)


BENCHMARK_PATH = PROJECT_ROOT / "data" / "benchmarks" / "pilot_queries_v2.json"
FROZEN_CORPUS_PATH = (
    PROJECT_ROOT
    / "data"
    / "topic_runs"
    / "multi_agent_intel_service_20260410_114059"
    / "retrieved_papers_wave3.json"
)
OUTPUT_DIR = PROJECT_ROOT / "data" / "autosurvey_native_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ERR_PATH = OUTPUT_DIR / "errors.jsonl"


def _log(message: str) -> None:
    print(message, flush=True)


def _write_status(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _has_final_native_output(output_dir: Path, qid: str, tag: str = "autosurvey_native") -> bool:
    """
    Return True if a completed final output file exists for (qid, tag).
    Intermediate files (.outline.md, .raw.md, .nocheck.md) are ignored.
    """
    for path in output_dir.glob(f"{qid}_{tag}_*.md"):
        lower_name = path.name.lower()
        if any(lower_name.endswith(s) for s in (".outline.md", ".raw.md", ".nocheck.md")):
            continue
        return True
    return False


class TokenCounter:
    def __init__(self) -> None:
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    def num_tokens_from_string(self, text: str) -> int:
        return len(self.encoding.encode(text or "", disallowed_special=()))

    def num_tokens_from_list_string(self, values: List[str]) -> int:
        return sum(self.num_tokens_from_string(item) for item in values)


class NativeAutoSurveyCorpusDB:
    def __init__(self, papers: List[Dict[str, Any]]) -> None:
        self.records: List[Dict[str, Any]] = []
        self.by_id: Dict[str, Dict[str, Any]] = {}
        self.retrieval_log: List[str] = []
        self._ordered_seen: set[str] = set()

        for idx, paper in enumerate(papers, 1):
            pid = _paper_id(paper)
            record = {
                "id": pid,
                "title": paper.get("title", "") or "",
                "abs": paper.get("abstract", "") or "",
                "date": str(paper.get("published_date") or paper.get("year") or ""),
                "url": paper.get("url", "") or "",
                "authors": paper.get("authors", []) or [],
                "source": paper.get("source", "") or "",
                "journal": paper.get("journal", "") or "",
                "doi": paper.get("doi", "") or "",
                "_raw": paper,
                "_idx": idx,
            }
            self.records.append(record)
            self.by_id[pid] = record

        doc_texts = [self._doc_text(row) for row in self.records]
        title_texts = [self._title_text(row["title"]) for row in self.records]
        self.doc_vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=1)
        self.title_vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=1)
        self.doc_matrix = self.doc_vectorizer.fit_transform(doc_texts)
        self.title_matrix = self.title_vectorizer.fit_transform(title_texts)

    @staticmethod
    def _doc_text(row: Dict[str, Any]) -> str:
        return " \n ".join(
            [
                row.get("title", "") or "",
                row.get("abs", "") or "",
                " ".join(row.get("authors", []) or []),
                row.get("journal", "") or "",
                row.get("source", "") or "",
            ]
        )

    @staticmethod
    def _title_text(title: str) -> str:
        return re.sub(r"\s+", " ", title or "").strip()

    def _record_retrieval(self, ids: List[str]) -> None:
        for pid in ids:
            if pid not in self._ordered_seen:
                self.retrieval_log.append(pid)
                self._ordered_seen.add(pid)

    def get_ids_from_query(self, query: str, num: int, shuffle: bool = False) -> List[str]:
        query_vec = self.doc_vectorizer.transform([query])
        scores = linear_kernel(query_vec, self.doc_matrix).ravel()
        ranked = scores.argsort()[::-1]
        ids = [self.records[i]["id"] for i in ranked[: max(1, num)]]
        self._record_retrieval(ids)
        return ids

    def get_paper_info_from_ids(self, ids: List[str]) -> List[Dict[str, Any]]:
        return [self.by_id[pid] for pid in ids if pid in self.by_id]

    def get_titles_from_citations(self, citations: List[str]) -> List[str]:
        if not citations:
            return []
        query_vec = self.title_vectorizer.transform([self._title_text(cit) for cit in citations])
        scores = linear_kernel(query_vec, self.title_matrix)
        best_idx = scores.argmax(axis=1).tolist()
        ids = [self.records[int(i)]["id"] for i in best_idx]
        self._record_retrieval(ids)
        return ids

    def top_papers(self, limit: int = 15) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for pid in self.retrieval_log[:limit]:
            row = self.by_id.get(pid)
            if row:
                rows.append(row["_raw"])
        return rows


class NativeAutoSurveyEngine:
    def __init__(self, *, model: str, api_key: str, db: NativeAutoSurveyCorpusDB) -> None:
        self.model = model
        self.api_key = api_key
        self.db = db
        self.token_counter = TokenCounter()

    def _call_ai(self, prompt: str, temperature: float = 1.0, max_tokens: int = 1800) -> str:
        last_exc: Exception | None = None
        for attempt in range(3):
            try:
                return call_ai(
                    prompt=prompt,
                    system="You are a helpful academic writing assistant.",
                    provider="deepseek",
                    api_key=self.api_key,
                    model=self.model,
                    task_type="analysis",
                    max_tokens=max_tokens,
                    temperature=temperature,
                    timeout=180,
                )
            except Exception as exc:
                last_exc = exc
                wait_seconds = [5, 15, 30][attempt]
                _log(f"    [native retry {attempt + 1}/3] call failed: {exc}. waiting {wait_seconds}s...")
                time.sleep(wait_seconds)
        raise last_exc if last_exc else RuntimeError("AI call failed")

    def _batch_chat(self, prompts: List[str], temperature: float = 1.0, max_tokens: int = 1800) -> List[str]:
        results = [""] * len(prompts)
        max_workers = min(3, max(1, len(prompts)))
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {
                executor.submit(self._call_ai, prompt, temperature, max_tokens): idx
                for idx, prompt in enumerate(prompts)
            }
            completed = 0
            for future in concurrent.futures.as_completed(future_map):
                idx = future_map[future]
                results[idx] = future.result()
                completed += 1
                _log(f"    [native batch] {completed}/{len(prompts)} prompts finished")
        return results

    @staticmethod
    def _generate_prompt(template: str, paras: Dict[str, str]) -> str:
        prompt = template
        for key, value in paras.items():
            prompt = prompt.replace(f"[{key}]", value)
        return prompt

    @staticmethod
    def _extract_title_sections_descriptions(outline: str) -> Tuple[str, List[str], List[str]]:
        title = outline.split("Title: ", 1)[1].splitlines()[0] if "Title: " in outline else "Survey"
        sections: List[str] = []
        descriptions: List[str] = []
        for idx in range(1, 100):
            if f"Section {idx}: " not in outline:
                continue
            sections.append(outline.split(f"Section {idx}: ", 1)[1].splitlines()[0])
            descriptions.append(outline.split(f"Description {idx}: ", 1)[1].splitlines()[0])
        return title, sections, descriptions

    @staticmethod
    def _extract_subsections_subdescriptions(outline: str) -> Tuple[List[str], List[str]]:
        subsections: List[str] = []
        descriptions: List[str] = []
        for idx in range(1, 100):
            if f"Subsection {idx}: " not in outline:
                continue
            subsections.append(outline.split(f"Subsection {idx}: ", 1)[1].splitlines()[0])
            descriptions.append(outline.split(f"Description {idx}: ", 1)[1].splitlines()[0])
        return subsections, descriptions

    def _chunking(self, papers: List[str], titles: List[str], chunk_size: int = 14000) -> Tuple[List[List[str]], List[List[str]]]:
        paper_chunks: List[List[str]] = []
        title_chunks: List[List[str]] = []
        total_length = self.token_counter.num_tokens_from_list_string(papers)
        num_of_chunks = int(total_length / chunk_size) + 1
        avg_len = int(total_length / num_of_chunks) + 1
        split_points: List[int] = []
        cur_len = 0
        for idx, paper in enumerate(papers):
            cur_len += self.token_counter.num_tokens_from_string(paper)
            if cur_len > avg_len:
                cur_len = 0
                split_points.append(idx)
        start = 0
        for point in split_points:
            paper_chunks.append(papers[start:point])
            title_chunks.append(titles[start:point])
            start = point
        paper_chunks.append(papers[start:])
        title_chunks.append(titles[start:])
        return paper_chunks, title_chunks

    def _paper_list_text(self, titles: List[str], papers: List[str]) -> str:
        rows: List[str] = []
        for title, paper in zip(titles, papers):
            rows.append(f"---\npaper_title: {title}\n\npaper_content:\n\n{paper}\n")
        rows.append("---\n")
        return "".join(rows)

    def draft_outline(self, topic: str, reference_num: int, chunk_size: int, section_num: int, skip_outline_edit: bool = False) -> str:
        references_ids = self.db.get_ids_from_query(topic, num=reference_num, shuffle=True)
        references_infos = self.db.get_paper_info_from_ids(references_ids)
        references_titles = [row["title"] for row in references_infos]
        references_abs = [row["abs"] for row in references_infos]
        abs_chunks, title_chunks = self._chunking(references_abs, references_titles, chunk_size=chunk_size)

        rough_prompts: List[str] = []
        for titles, papers in zip(title_chunks, abs_chunks):
            prompt = self._generate_prompt(
                ROUGH_OUTLINE_PROMPT,
                {
                    "PAPER LIST": self._paper_list_text(titles, papers),
                    "TOPIC": topic,
                    "SECTION NUM": str(section_num),
                },
            )
            rough_prompts.append(prompt)
        rough_outlines = self._batch_chat(rough_prompts, temperature=1.0, max_tokens=900)

        outline_texts = ""
        for idx, outline in enumerate(rough_outlines):
            outline_texts += f"---\noutline_id: {idx}\n\noutline_content:\n\n{outline}\n"
        outline_texts += "---\n"
        _log("    [outline] merging rough outlines...")
        merged = self._call_ai(
            self._generate_prompt(MERGING_OUTLINE_PROMPT, {"OUTLINE LIST": outline_texts, "TOPIC": topic}),
            temperature=1.0,
            max_tokens=1000,
        )

        survey_title, survey_sections, survey_section_descriptions = self._extract_title_sections_descriptions(merged)
        sub_prompts: List[str] = []
        for section_name, section_description in zip(survey_sections, survey_section_descriptions):
            references_ids = self.db.get_ids_from_query(section_description, num=50, shuffle=True)
            references_infos = self.db.get_paper_info_from_ids(references_ids)
            references_titles = [row["title"] for row in references_infos]
            references_papers = [row["abs"] for row in references_infos]
            sub_prompts.append(
                self._generate_prompt(
                    SUBSECTION_OUTLINE_PROMPT,
                    {
                        "OVERALL OUTLINE": merged,
                        "SECTION NAME": section_name,
                        "SECTION DESCRIPTION": section_description,
                        "TOPIC": topic,
                        "PAPER LIST": self._paper_list_text(references_titles, references_papers),
                    },
                )
            )
        _log(f"    [outline] generating subsection structures for {len(sub_prompts)} sections...")
        sub_outlines = self._batch_chat(sub_prompts, temperature=1.0, max_tokens=900)

        draft_outline = self._process_outlines(merged, sub_outlines)
        if skip_outline_edit:
            _log("    [outline] skipping final outline edit by flag")
            return draft_outline.strip()

        _log("    [outline] editing final outline...")
        edited = self._call_ai(
            self._generate_prompt(EDIT_FINAL_OUTLINE_PROMPT, {"OVERALL OUTLINE": draft_outline}),
            temperature=1.0,
            max_tokens=1400,
        )
        return edited.replace("<format>\n", "").replace("</format>", "").strip()

    def _process_outlines(self, section_outline: str, sub_outlines: List[str]) -> str:
        res = ""
        survey_title, survey_sections, survey_section_descriptions = self._extract_title_sections_descriptions(section_outline)
        res += f"# {survey_title}\n\n"
        for idx, section in enumerate(survey_sections):
            res += f"## {idx + 1} {section}\nDescription: {survey_section_descriptions[idx]}\n\n"
            subsections, subsection_descriptions = self._extract_subsections_subdescriptions(sub_outlines[idx])
            for sub_idx, subsection in enumerate(subsections):
                res += f"### {idx + 1}.{sub_idx + 1} {subsection}\nDescription: {subsection_descriptions[sub_idx]}\n\n"
        return res

    def _parse_outline(self, outline: str) -> Dict[str, Any]:
        result = {
            "title": "",
            "sections": [],
            "section_descriptions": [],
            "subsections": [],
            "subsection_descriptions": [],
        }
        lines = outline.splitlines()
        for idx, line in enumerate(lines):
            if line.startswith("# "):
                result["title"] = line[2:].strip()
            elif line.startswith("## "):
                result["sections"].append(line[3:].strip())
                if idx + 1 < len(lines) and lines[idx + 1].startswith("Description:"):
                    result["section_descriptions"].append(lines[idx + 1].split("Description:", 1)[1].strip())
                    result["subsections"].append([])
                    result["subsection_descriptions"].append([])
            elif line.startswith("### "):
                if result["subsections"]:
                    result["subsections"][-1].append(line[4:].strip())
                    if idx + 1 < len(lines) and lines[idx + 1].startswith("Description:"):
                        result["subsection_descriptions"][-1].append(lines[idx + 1].split("Description:", 1)[1].strip())
        return result

    def _write_subsection_batch(
        self,
        topic: str,
        outline: str,
        section: str,
        subsections: List[str],
        descriptions: List[str],
        paper_texts_list: List[str],
        subsection_len: int,
        skip_check: bool = False,
    ) -> Tuple[List[str], List[str]]:
        """
        Returns (raw_contents, final_contents).
        raw_contents  — output immediately after writing, before CHECK_CITATION.
        final_contents — output after CHECK_CITATION (same as raw_contents when skip_check=True).
        """
        prompts: List[str] = []
        for subsection, description, paper_texts in zip(subsections, descriptions, paper_texts_list):
            prompts.append(
                self._generate_prompt(
                    SUBSECTION_WRITING_PROMPT,
                    {
                        "OVERALL OUTLINE": outline,
                        "SUBSECTION NAME": subsection,
                        "DESCRIPTION": description,
                        "TOPIC": topic,
                        "PAPER LIST": paper_texts,
                        "SECTION NAME": section,
                        "WORD NUM": str(subsection_len),
                        "CITATION NUM": "8",
                    },
                )
            )
        raw_contents = [c.replace("<format>", "").replace("</format>", "").strip() for c in self._batch_chat(prompts, temperature=1.0)]

        if skip_check:
            _log("    [native] CHECK_CITATION step skipped (ablation mode)")
            return raw_contents, raw_contents

        check_prompts = [
            self._generate_prompt(CHECK_CITATION_PROMPT, {"SUBSECTION": content, "TOPIC": topic, "PAPER LIST": paper_texts})
            for content, paper_texts in zip(raw_contents, paper_texts_list)
        ]
        checked = [c.replace("<format>", "").replace("</format>", "").strip() for c in self._batch_chat(check_prompts, temperature=1.0)]
        return raw_contents, checked

    def _lce(self, topic: str, previous: str, current: str, following: str) -> str:
        prompt = self._generate_prompt(
            LCE_PROMPT,
            {
                "PREVIOUS": previous,
                "FOLLOWING": following,
                "TOPIC": topic,
                "SUBSECTION": current,
            },
        )
        refined = self._call_ai(prompt, temperature=1.0, max_tokens=1800)
        return refined.replace("<format>", "").replace("</format>", "").replace("Here is the refined subsection:\n", "").strip()

    def _refine_subsections(self, topic: str, section_content: List[List[str]]) -> List[List[str]]:
        even_pass = [row[:] for row in section_content]
        for sec_idx, row in enumerate(section_content):
            for sub_idx in range(len(row)):
                if sub_idx % 2 != 0:
                    continue
                prev_text = row[sub_idx - 1] if sub_idx > 0 else ""
                next_text = row[sub_idx + 1] if sub_idx + 1 < len(row) else ""
                even_pass[sec_idx][sub_idx] = self._lce(topic, prev_text, row[sub_idx], next_text)

        final_pass = [row[:] for row in even_pass]
        for sec_idx, row in enumerate(even_pass):
            for sub_idx in range(len(row)):
                if sub_idx % 2 != 1:
                    continue
                prev_text = row[sub_idx - 1] if sub_idx > 0 else ""
                next_text = row[sub_idx + 1] if sub_idx + 1 < len(row) else ""
                final_pass[sec_idx][sub_idx] = self._lce(topic, prev_text, row[sub_idx], next_text)
        return final_pass

    def _generate_document(self, parsed_outline: Dict[str, Any], subsection_contents: List[List[str]]) -> str:
        lines: List[str] = [f"# {parsed_outline['title']}\n"]
        for sec_idx, section in enumerate(parsed_outline["sections"]):
            lines.append(f"## {section}\n")
            for sub_idx, subsection in enumerate(parsed_outline["subsections"][sec_idx]):
                lines.append(f"### {subsection}\n")
                if sub_idx < len(subsection_contents[sec_idx]):
                    lines.append(subsection_contents[sec_idx][sub_idx] + "\n")
        return "\n".join(lines)

    @staticmethod
    def _extract_citations(markdown_text: str) -> List[str]:
        citations: List[str] = []
        for match in re.findall(r"\[(.*?)\]", markdown_text):
            for part in match.split(";"):
                citation = part.strip()
                if citation and citation not in citations:
                    citations.append(citation)
        return citations

    def _replace_citations_with_numbers(self, citations: List[str], markdown_text: str) -> Tuple[str, Dict[int, str]]:
        ids = self.db.get_titles_from_citations(citations)
        citation_to_ids = {citation: idx for citation, idx in zip(citations, ids)}
        paper_infos = self.db.get_paper_info_from_ids(ids)
        title_by_id = {row["id"]: row["title"] for row in paper_infos}
        titles = [title_by_id.get(pid, self.db.by_id.get(pid, {}).get("title", "")) for pid in ids]

        ids_to_titles = {pid: title for pid, title in zip(ids, titles)}
        title_to_number = {title: num + 1 for num, title in enumerate(dict.fromkeys(titles))}
        number_to_title = {num: title for title, num in title_to_number.items()}

        def replace_match(match: re.Match[str]) -> str:
            citation_text = match.group(1)
            individual = [item.strip() for item in citation_text.split(";") if item.strip()]
            numbered = []
            for citation in individual:
                pid = citation_to_ids.get(citation)
                title = ids_to_titles.get(pid, "")
                if title in title_to_number:
                    numbered.append(str(title_to_number[title]))
            return "[" + "; ".join(numbered) + "]" if numbered else "[]"

        updated_text = re.sub(r"\[(.*?)\]", replace_match, markdown_text)
        references_section = "\n\n## References\n\n"
        references: Dict[int, str] = {}
        for num in sorted(number_to_title):
            title = number_to_title[num]
            pid = next((pid for pid, paper_title in ids_to_titles.items() if paper_title == title), "")
            references[num] = pid
            references_section += f"[{num}] {title.replace(chr(10), ' ')}\n\n"
        return updated_text + references_section, references

    def write(
        self,
        topic: str,
        outline: str,
        rag_num: int,
        subsection_len: int,
        refining: bool = True,
        skip_check: bool = False,
    ) -> Tuple[str, str, Dict[int, str], str, str, Dict[int, str], str, str]:
        """
        Returns 8-tuple:
          nocheck_survey, nocheck_survey_with_refs,
          raw_survey, raw_survey_with_refs, raw_references,
          refined_survey, refined_survey_with_refs, refined_references

        nocheck_* is the output before CHECK_CITATION (useful for ablation).
        raw_* is post-CHECK_CITATION but pre-refinement.
        refined_* is post-CHECK_CITATION + LCE refinement.
        When skip_check=True, nocheck_* == raw_*.
        """
        parsed_outline = self._parse_outline(outline)
        nocheck_content: List[List[str]] = [[] for _ in parsed_outline["sections"]]
        section_content: List[List[str]] = [[] for _ in parsed_outline["sections"]]

        for sec_idx in range(len(parsed_outline["sections"])):
            paper_texts_list: List[str] = []
            for description in parsed_outline["subsection_descriptions"][sec_idx]:
                references_ids = self.db.get_ids_from_query(description, num=rag_num, shuffle=False)
                references_infos = self.db.get_paper_info_from_ids(references_ids)
                references_titles = [row["title"] for row in references_infos]
                references_papers = [row["abs"] for row in references_infos]
                paper_texts_list.append(self._paper_list_text(references_titles, references_papers))
            raw_batch, checked_batch = self._write_subsection_batch(
                topic=topic,
                outline=outline,
                section=parsed_outline["sections"][sec_idx],
                subsections=parsed_outline["subsections"][sec_idx],
                descriptions=parsed_outline["subsection_descriptions"][sec_idx],
                paper_texts_list=paper_texts_list,
                subsection_len=subsection_len,
                skip_check=skip_check,
            )
            nocheck_content[sec_idx] = raw_batch
            section_content[sec_idx] = checked_batch

        # --- nocheck intermediate (before CHECK_CITATION) ---
        nocheck_survey = self._generate_document(parsed_outline, nocheck_content)
        nocheck_survey_with_refs, _ = self._replace_citations_with_numbers(
            self._extract_citations(nocheck_survey), nocheck_survey
        )

        # --- post-check (before LCE refinement) ---
        raw_survey = self._generate_document(parsed_outline, section_content)
        raw_survey_with_references, raw_references = self._replace_citations_with_numbers(
            self._extract_citations(raw_survey), raw_survey
        )

        # --- refined (LCE coherence pass) ---
        final_section_content = self._refine_subsections(topic, section_content) if refining else section_content
        refined_survey = self._generate_document(parsed_outline, final_section_content)
        refined_survey_with_references, refined_references = self._replace_citations_with_numbers(
            self._extract_citations(refined_survey), refined_survey
        )
        return (
            nocheck_survey + "\n",
            nocheck_survey_with_refs + "\n",
            raw_survey + "\n",
            raw_survey_with_references + "\n",
            raw_references,
            refined_survey + "\n",
            refined_survey_with_references + "\n",
            refined_references,
        )


def _run_native_autosurvey(
    *,
    query: str,
    qid: str,
    model: str,
    db: NativeAutoSurveyCorpusDB,
    api_key: str,
    output_dir: Path,
    section_num: int,
    subsection_len: int,
    outline_reference_num: int,
    rag_num: int,
    refining: bool,
    skip_outline_edit: bool,
    skip_check: bool = False,
) -> None:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Use a different tag when running the no-check ablation so outputs don't conflict
    tag = "autosurvey_native_nocheck" if skip_check else "autosurvey_native"
    stem = f"{qid}_{tag}_{stamp}"
    md_path = output_dir / f"{stem}.md"
    json_path = output_dir / f"{stem}.json"
    status_path = output_dir / f"{stem}.status.json"
    outline_path = output_dir / f"{stem}.outline.md"
    raw_md_path = output_dir / f"{stem}.raw.md"
    raw_json_path = output_dir / f"{stem}.raw.json"
    # Only saved when skip_check=False: the true pre-CHECK_CITATION intermediate
    nocheck_md_path = output_dir / f"{stem}.nocheck.md"

    engine = NativeAutoSurveyEngine(model=model, api_key=api_key, db=db)
    started = time.time()

    _write_status(
        status_path,
        {
            "query_id": qid,
            "query": query,
            "stage": "outline",
            "started_at": stamp,
            "model": model,
            "refining": refining,
        },
    )
    _log("  [N1] Native AutoSurvey outline generation...")
    outline = engine.draft_outline(
        topic=query,
        reference_num=outline_reference_num,
        chunk_size=22000,
        section_num=section_num,
        skip_outline_edit=skip_outline_edit,
    )
    outline_path.write_text(outline, encoding="utf-8")
    _write_status(
        status_path,
        {
            "query_id": qid,
            "query": query,
            "stage": "raw_writing",
            "outline_path": str(outline_path),
            "elapsed_seconds": round(time.time() - started, 3),
            "retrieved_so_far": len(db.retrieval_log),
        },
    )

    _log("  [N2] Native AutoSurvey subsection writing...")
    (
        nocheck_survey,
        nocheck_survey_with_refs,
        raw_survey,
        raw_survey_with_references,
        raw_references,
        refined_survey,
        refined_survey_with_references,
        refined_references,
    ) = engine.write(
        topic=query,
        outline=outline,
        rag_num=rag_num,
        subsection_len=subsection_len,
        refining=refining,
        skip_check=skip_check,
    )
    # Save pre-CHECK_CITATION intermediate (only meaningful when skip_check=False)
    if not skip_check:
        nocheck_md_path.write_text(nocheck_survey_with_refs, encoding="utf-8")
        _log(f"  Saved pre-check intermediate: {nocheck_md_path.name}")
    raw_md_path.write_text(raw_survey_with_references, encoding="utf-8")
    raw_json_path.write_text(
        json.dumps(
            {
                "baseline": "autosurvey_native_raw_intermediate",
                "query": query,
                "outline": outline,
                "references": raw_references,
                "all_retrieved_ids": db.retrieval_log,
                "top_papers": [_compact(paper) for paper in db.top_papers(15)],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    _write_status(
        status_path,
        {
            "query_id": qid,
            "query": query,
            "stage": "refined_output" if refining else "finalizing_raw",
            "outline_path": str(outline_path),
            "raw_markdown_path": str(raw_md_path),
            "elapsed_seconds": round(time.time() - started, 3),
            "retrieved_so_far": len(db.retrieval_log),
        },
    )

    final_markdown = refined_survey_with_references if refining else raw_survey_with_references
    final_references = refined_references if refining else raw_references
    md_path.write_text(final_markdown, encoding="utf-8")
    elapsed_seconds = round(time.time() - started, 3)
    sidecar = {
        "baseline": "autosurvey_native_nocheck_raw" if skip_check else "autosurvey_native_raw",
        "query": query,
        "provider": "deepseek",
        "model": model,
        "skip_check_citation": skip_check,
        "corpus_mode": "frozen_topic_run",
        "comparison_mode": "native_autosurvey_local_db",
        "retrieved_count": len(db.retrieval_log),
        "all_retrieved_ids": db.retrieval_log,
        "top_papers": [_compact(paper) for paper in db.top_papers(15)],
        "outline": outline,
        "raw_references": raw_references,
        "refined_references": final_references,
        "elapsed_seconds": elapsed_seconds,
        "output_markdown": str(md_path),
        "raw_markdown": str(raw_md_path),
        "outline_markdown": str(outline_path),
        "refining": refining,
    }
    json_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_status(
        status_path,
        {
            "query_id": qid,
            "query": query,
            "stage": "done",
            "output_markdown": str(md_path),
            "output_json": str(json_path),
            "elapsed_seconds": elapsed_seconds,
            "retrieved_total": len(db.retrieval_log),
        },
    )

    _log(f"  Saved markdown: {md_path.name}")
    _log(f"  Saved metadata: {json_path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a native AutoSurvey baseline with a local frozen-corpus adapter.")
    parser.add_argument("--benchmark-path", default=str(BENCHMARK_PATH))
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    parser.add_argument("--query-id", default=None)
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=30)
    parser.add_argument("--model", default="deepseek-chat")
    parser.add_argument("--section-num", type=int, default=4)
    parser.add_argument("--subsection-len", type=int, default=220)
    parser.add_argument("--outline-reference-num", type=int, default=40)
    parser.add_argument("--rag-num", type=int, default=8)
    parser.add_argument("--sleep", type=float, default=2.0)
    parser.add_argument("--skip-refine", action="store_true")
    parser.add_argument("--skip-outline-edit", action="store_true")
    parser.add_argument(
        "--no-check-citation",
        action="store_true",
        help=(
            "Ablation: skip the CHECK_CITATION step. "
            "Output tag changes to 'autosurvey_native_nocheck' to keep ablation "
            "outputs separate from the default 'autosurvey_native' runs."
        ),
    )
    args = parser.parse_args()

    cfg = _load_saved_search_config()
    api_key = cfg.get("deepseek_api_key", "") or ""
    if not api_key:
        raise SystemExit("deepseek_api_key is not configured")

    benchmark_path = Path(args.benchmark_path)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    queries = json.loads(benchmark_path.read_text(encoding="utf-8"))
    papers = json.loads(FROZEN_CORPUS_PATH.read_text(encoding="utf-8"))

    _log(f"Loaded {len(queries)} benchmark queries.")
    _log(f"Loaded {len(papers)} frozen-corpus papers.")
    _log(f"Output directory: {output_dir}")
    _log("-" * 60)

    success = 0
    failed = 0
    for row in queries:
        qid = row["id"]
        idx = int(qid[1:])
        query_text = row["query"]

        if args.query_id and qid != args.query_id:
            continue
        if not args.query_id and not (args.start <= idx <= args.end):
            continue

        expected_tag = "autosurvey_native_nocheck" if args.no_check_citation else "autosurvey_native"
        if _has_final_native_output(output_dir, qid, tag=expected_tag):
            _log(f"[{qid}] Already exists ({expected_tag}), skipping.")
            success += 1
            continue

        _log(f"\n[{qid}] {query_text}")
        try:
            db = NativeAutoSurveyCorpusDB(papers)
            _run_native_autosurvey(
                query=query_text,
                qid=qid,
                model=args.model,
                db=db,
                api_key=api_key,
                output_dir=output_dir,
                section_num=args.section_num,
                subsection_len=args.subsection_len,
                outline_reference_num=args.outline_reference_num,
                rag_num=args.rag_num,
                refining=not args.skip_refine,
                skip_outline_edit=args.skip_outline_edit,
                skip_check=args.no_check_citation,
            )
            success += 1
        except Exception as exc:
            failed += 1
            _log_error(
                {
                    "baseline": "autosurvey_native_raw",
                    "query_id": qid,
                    "query": query_text,
                    "provider": "deepseek",
                    "error": str(exc),
                    "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                },
                err_path=ERR_PATH,
            )
            _log(f"  FAILED: {exc}")
        time.sleep(args.sleep)

    _log("\n" + "=" * 60)
    _log(f"AutoSurvey-native finished. success={success}, failed={failed}")


if __name__ == "__main__":
    main()
