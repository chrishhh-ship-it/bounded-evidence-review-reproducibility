from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "baselines"
FROZEN_CORPUS_PATH = (
    PROJECT_ROOT
    / "data"
    / "topic_runs"
    / "multi_agent_intel_service_20260410_114059"
    / "retrieved_papers_wave3.json"
)

BASELINE_A_SECTIONS = [
    re.compile(r"(problem\s*fram|problem\s*definition|问题界定)", re.I),
    re.compile(r"(research\s*direction|theme|研究方向|主题)", re.I),
    re.compile(r"(risk|unknown|limitation|风险|局限)", re.I),
    re.compile(r"(conclusion|结论)", re.I),
]

BASELINE_B_SECTIONS = [
    re.compile(r"(corpus\s*overview|retrieved\s*papers|文献概览|语料概览)", re.I),
    re.compile(r"(main\s*theme|theme|核心主题|主题)", re.I),
    re.compile(r"(evidence.{0,12}direction|direction|evidence|证据|研究方向)", re.I),
    re.compile(r"(limitation|risk|局限|风险)", re.I),
    re.compile(r"(conclusion|结论)", re.I),
]

METHOD1_SECTIONS = [
    re.compile(r"(retrieval|语料|检索)", re.I),
    re.compile(r"(screening|priority|筛选|优先)", re.I),
    re.compile(r"(evidence|全文|证据)", re.I),
    re.compile(r"(synthesis|report|conclusion|综合|报告|结论)", re.I),
    re.compile(r"(limitation|risk|局限|风险)", re.I),
]

METHOD2_SECTIONS = [
    re.compile(r"(retrieval|语料|检索)", re.I),
    re.compile(r"(screening|priority|筛选|优先)", re.I),
    re.compile(r"(evidence|全文|证据)", re.I),
    re.compile(r"(review|critic|reviewer|审稿|审查)", re.I),
    re.compile(r"(revis|improv|修改|修订|改进)", re.I),
    re.compile(r"(conclusion|report|结论|报告)", re.I),
]

_BIB_HDR_RE = re.compile(r"^\s*#{1,3}\s*(参考文献|References)\s*$", re.I | re.M)
_BRACKET_BLOCK_RE = re.compile(r"\[([0-9,\-\s]+)\]")
_WENXIAN_CITE_RE = re.compile(r"文献\s*(\d+)")
_BIB_ENTRY_RE = re.compile(r"^\s*\[(\d+)\]\s+(.*)", re.M)
_RESULT_FILE_RE = re.compile(
    r"(?i)^(q|md)(\d+)_"
    r"(baseline_[ab]|schema_single_agent|autosurvey_native_nocheck|autosurvey_native|autosurvey|method2_same_model|method2[a-d]?_exp|method2|method1_exp|method1|method3|method4)_"
    r"(\d{8}_\d{6})$"
)


AUTOSURVEY_SECTIONS = [
    re.compile(r"^#\s+.+$", re.I | re.M),
    re.compile(r"^##\s+.+$", re.I | re.M),
    re.compile(r"^###\s+.+$", re.I | re.M),
    re.compile(r"\[\d+\]"),
    re.compile(r"(references|参考文献)", re.I),
]


def _section_map(tag: str) -> List[re.Pattern[str]]:
    if tag == "baseline_a":
        return BASELINE_A_SECTIONS
    if tag in {"autosurvey", "autosurvey_native", "autosurvey_native_nocheck"}:
        return AUTOSURVEY_SECTIONS
    if tag == "method1":
        return METHOD1_SECTIONS
    if tag == "schema_single_agent":
        return METHOD1_SECTIONS
    if tag in {
        "method2",
        "method2a",
        "method2b",
        "method2c",
        "method2d",
        "method2_same_model",
        "method3",
        "method4",
    }:
        return METHOD2_SECTIONS
    return BASELINE_B_SECTIONS


def _canonical_query_id(prefix: str, digits: str) -> str:
    """Return a canonical query identifier insensitive to leading-zero padding.

    File naming in the released benchmark is inconsistent: Q01-Q60 use a
    2-digit width, Q061-Q099 were generated with a 3-digit zero-padded width,
    and Q100-Q251 use a natural 3-digit width. Canonicalising on the integer
    value (rather than the input string length) normalises Q077 -> Q77,
    keeping a single canonical form per logical query so that --query-ids
    range filters and file canonicals always agree.
    """
    n = int(digits)
    width = max(2, len(str(n)))
    return f"{prefix.upper()}{n:0{width}d}"


def _parse_result_stem(stem: str) -> Optional[Tuple[str, str, str]]:
    match = _RESULT_FILE_RE.match(stem)
    if not match:
        return None
    query_id = _canonical_query_id(match.group(1), match.group(2))
    tag = match.group(3).lower()
    stamp = match.group(4)
    return query_id, tag, stamp


def _parse_query_ids(raw: Optional[str]) -> Optional[set[str]]:
    if not raw:
        return None

    wanted: set[str] = set()
    for chunk in raw.split(","):
        token = chunk.strip()
        if not token:
            continue
        range_match = re.match(r"(?i)^([a-z]+)(\d+)-([a-z]+)?(\d+)$", token)
        if range_match:
            start_prefix = range_match.group(1).upper()
            start_num = int(range_match.group(2))
            end_prefix = (range_match.group(3) or range_match.group(1)).upper()
            end_num = int(range_match.group(4))
            if start_prefix != end_prefix:
                raise SystemExit(f"Invalid query-id range with mixed prefixes: {token}")
            if end_num < start_num:
                raise SystemExit(f"Invalid descending query-id range: {token}")
            # Per-element padding: file canonical IDs use width = max(2, len(digits)),
            # so Q01-Q99 stay 2-digit and Q100+ stay 3-digit. Force-padding the
            # whole range to a single uniform width (e.g., "Q001") would mismatch
            # the on-disk canonical IDs and silently drop Q01-Q99.
            for number in range(start_num, end_num + 1):
                wanted.add(_canonical_query_id(start_prefix, str(number)))
            continue

        single_match = re.match(r"(?i)^([a-z]+)(\d+)$", token)
        if not single_match:
            raise SystemExit(f"Invalid query id token: {token}")
        wanted.add(_canonical_query_id(single_match.group(1), single_match.group(2)))
    return wanted


def _infer_config_tag(path: Path, parsed_tag: Optional[str]) -> str:
    if parsed_tag in {"baseline_a", "baseline_b", "schema_single_agent", "autosurvey", "autosurvey_native", "autosurvey_native_nocheck", "method1", "method1_exp", "method3", "method4"}:
        if parsed_tag == "baseline_a":
            return "baseline_a"
        if parsed_tag == "autosurvey_native_nocheck":
            return "autosurvey_native_nocheck"
        if parsed_tag == "autosurvey_native":
            return "autosurvey_native"
        if parsed_tag == "autosurvey":
            return "autosurvey"
        if parsed_tag == "baseline_b":
            return "baseline_b"
        if parsed_tag == "schema_single_agent":
            return "schema_single_agent"
        if parsed_tag == "method3":
            return "method3"
        if parsed_tag == "method4":
            return "method4"
        return "method1"
    if parsed_tag in {"method2", "method2a_exp"}:
        return "method2"
    if parsed_tag in {"method2_same_model", "method2b_exp"}:
        return "method2_same_model"
    if parsed_tag == "method2c_exp":
        return "method2c"
    if parsed_tag == "method2d_exp":
        # The on-disk identifier method2d corresponds to the configuration
        # labelled M2c in the paper (weak-capacity ARL with GPT-4o-mini).
        # Public commands and the manifest both use --tag method2c; map the
        # legacy file token method2d_exp to the same logical tag here so the
        # filter accepts the directory data/expanded_outputs/method2d/ under
        # the public name.
        return "method2c"

    lower_name = path.name.lower()
    if "_baseline_a_" in lower_name:
        return "baseline_a"
    if "_autosurvey_native_nocheck_" in lower_name:
        return "autosurvey_native_nocheck"
    if "_autosurvey_native_" in lower_name:
        return "autosurvey_native"
    if "_autosurvey_" in lower_name:
        return "autosurvey"
    if "_baseline_b_" in lower_name:
        return "baseline_b"
    if "_method3_" in lower_name:
        return "method3"
    if "_method4_" in lower_name:
        return "method4"
    if "_method2_same_model_" in lower_name or "_method2b_exp_" in lower_name:
        return "method2_same_model"
    if "_method2c_exp_" in lower_name:
        return "method2c"
    if "_method2d_exp_" in lower_name:
        # On-disk method2d == paper M2c. Treat as the same tag.
        return "method2c"
    if any(token in lower_name for token in ("_method2_", "_method2a_exp_")):
        return "method2"
    return "method1"


def _normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def _normalize_title(text: str) -> str:
    text = _normalize_text(text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"doi[:\s]*\S+", " ", text)
    text = re.sub(r"[^\w\u4e00-\u9fff]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _title_tokens(text: str) -> List[str]:
    norm = _normalize_title(text)
    return [tok for tok in norm.split() if len(tok) >= 2]


def _paper_id(paper: Dict[str, Any]) -> str:
    doi = (paper.get("doi") or "").strip().lower()
    if doi:
        return f"doi:{doi}"
    title = " ".join((paper.get("title") or "").lower().split())
    year = str(paper.get("year") or "").strip()
    return f"title:{title}|{year}"


def _load_frozen_corpus() -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    corpus = json.loads(FROZEN_CORPUS_PATH.read_text(encoding="utf-8"))
    by_id: Dict[str, Dict[str, Any]] = {}
    for row in corpus:
        by_id[_paper_id(row)] = row
    return corpus, by_id


def _split_body_bib(content: str) -> Tuple[str, str]:
    parts = _BIB_HDR_RE.split(content, maxsplit=1)
    if len(parts) >= 3:
        return parts[0], parts[-1]
    return content, ""


def _expand_citation_block(raw: str) -> List[int]:
    nums: List[int] = []
    for part in re.split(r"\s*,\s*", raw.strip()):
        if not part:
            continue
        if "-" in part:
            try:
                start_s, end_s = [item.strip() for item in part.split("-", 1)]
                start_i = int(start_s)
                end_i = int(end_s)
                if start_i <= end_i and end_i - start_i <= 50:
                    nums.extend(range(start_i, end_i + 1))
                    continue
            except ValueError:
                pass
        try:
            nums.append(int(part))
        except ValueError:
            continue
    return nums


def _extract_citations_from_text(body: str) -> List[int]:
    nums = set()
    for match in _BRACKET_BLOCK_RE.finditer(body):
        for num in _expand_citation_block(match.group(1)):
            nums.add(num)
    for match in _WENXIAN_CITE_RE.finditer(body):
        nums.add(int(match.group(1)))
    return sorted(nums)


def _parse_bib_entries(bib_text: str) -> Dict[int, str]:
    entries: Dict[int, str] = {}
    for match in _BIB_ENTRY_RE.finditer(bib_text):
        entries[int(match.group(1))] = match.group(2).strip()
    return entries


def _match_title(
    ref_text: str,
    candidate_titles: Iterable[str],
    threshold: float = 0.72,
) -> Optional[str]:
    """
    Fuzzy-match ref_text against candidate_titles.

    threshold controls how strict the match is:
      0.72  — default, permissive (catches paraphrased/abbreviated titles)
      0.90  — strict (near-exact titles only; use to test genuine auditability)
      1.0   — exact normalised match only
    """
    ref_norm = _normalize_title(ref_text)
    ref_tokens = set(_title_tokens(ref_text))
    if not ref_norm:
        return None

    best: Optional[Tuple[float, str]] = None
    for cand in candidate_titles:
        cand_norm = _normalize_title(cand)
        if not cand_norm:
            continue

        if cand_norm in ref_norm or ref_norm in cand_norm:
            score = 1.0
        else:
            cand_tokens = set(_title_tokens(cand))
            overlap = len(ref_tokens & cand_tokens)
            token_ratio = overlap / max(1, min(len(ref_tokens), len(cand_tokens)))
            seq_ratio = SequenceMatcher(None, ref_norm, cand_norm).ratio()
            score = max(seq_ratio, token_ratio)

        if score >= threshold and (best is None or score > best[0]):
            best = (score, cand)

    return best[1] if best else None


def _select_latest_per_query(md_files: List[Path]) -> Dict[str, Path]:
    groups: Dict[str, Tuple[str, Path]] = {}
    for path in md_files:
        parsed = _parse_result_stem(path.stem)
        if not parsed:
            continue
        query_id, tag, stamp = parsed
        key = f"{query_id}_{tag}"
        if key not in groups or stamp > groups[key][0]:
            groups[key] = (stamp, path)
    return {key: value[1] for key, value in groups.items()}


def _filter_result_files(
    md_files: List[Path],
    target_tag: Optional[str],
    query_ids: Optional[set[str]],
) -> List[Path]:
    filtered: List[Path] = []
    for path in md_files:
        parsed = _parse_result_stem(path.stem)
        if not parsed:
            continue
        query_id, parsed_tag, _ = parsed
        config_tag = _infer_config_tag(path, parsed_tag)
        if target_tag and config_tag != target_tag:
            continue
        if query_ids is not None and query_id not in query_ids:
            continue
        filtered.append(path)
    return filtered


def _build_candidate_pool(sidecar: Dict[str, Any], frozen_by_id: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    seen: set[str] = set()

    for pid in sidecar.get("all_retrieved_ids", []) or []:
        if pid in frozen_by_id and pid not in seen:
            candidates.append(frozen_by_id[pid])
            seen.add(pid)

    rows = list(frozen_by_id.values())
    titles = [row.get("title", "") for row in rows]
    rows_by_normalized_title: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        normalized = _normalize_title(row.get("title", ""))
        if normalized and normalized not in rows_by_normalized_title:
            rows_by_normalized_title[normalized] = row

    for paper in sidecar.get("top_papers", []) or []:
        pid = _paper_id(paper)
        if pid in frozen_by_id and pid not in seen:
            candidates.append(frozen_by_id[pid])
            seen.add(pid)
            continue
        title = paper.get("title") or ""
        exact_row = rows_by_normalized_title.get(_normalize_title(title))
        if exact_row is not None:
            exact_id = _paper_id(exact_row)
            if exact_id not in seen:
                candidates.append(exact_row)
                seen.add(exact_id)
            continue
        match = _match_title(title, titles)
        if not match:
            continue
        match_row = next((row for row in frozen_by_id.values() if row.get("title", "") == match), None)
        if not match_row:
            continue
        match_id = _paper_id(match_row)
        if match_id not in seen:
            candidates.append(match_row)
            seen.add(match_id)

    return candidates


def evaluate_file(
    md_path: Path,
    config_tag: str,
    frozen_by_id: Dict[str, Dict[str, Any]],
    match_threshold: float = 0.72,
) -> Dict[str, Any]:
    content = md_path.read_text(encoding="utf-8")
    sidecar_path = md_path.with_suffix(".json")
    sidecar: Dict[str, Any] = {}
    if sidecar_path.exists():
        sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))

    body, bib_text = _split_body_bib(content)
    bib_entries = _parse_bib_entries(bib_text)
    cite_nums = _extract_citations_from_text(body)
    candidate_pool = _build_candidate_pool(sidecar, frozen_by_id)
    candidate_titles = [row.get("title", "") for row in candidate_pool]

    total_cites = len(cite_nums)
    valid_cites = 0
    text_orphans = 0
    uncited_bib = 0
    matched_bib_entries = 0
    abstract_coverage = 0.0

    top_papers = sidecar.get("top_papers", []) or []
    if top_papers:
        abstract_coverage = sum(
            1 for paper in top_papers if (paper.get("abstract") or "").strip()
        ) / len(top_papers)

    if config_tag == "baseline_a":
        citation_precision = None if total_cites == 0 else 0.0
        text_orphans = total_cites
    else:
        citation_precision = None
        if total_cites > 0:
            for num in cite_nums:
                ref_text = bib_entries.get(num, "")
                if not ref_text:
                    text_orphans += 1
                    continue
                match = _match_title(ref_text, candidate_titles, threshold=match_threshold)
                if match:
                    valid_cites += 1
                else:
                    text_orphans += 1
            citation_precision = valid_cites / total_cites

        if bib_entries:
            cited_set = set(cite_nums)
            uncited_bib = sum(1 for num in bib_entries if num not in cited_set)
            for ref_text in bib_entries.values():
                if _match_title(ref_text, candidate_titles, threshold=match_threshold):
                    matched_bib_entries += 1

    orphan_den = max(total_cites, len(bib_entries), 1)
    orphan_rate = (text_orphans + uncited_bib) / orphan_den
    bibliography_match_rate = matched_bib_entries / len(bib_entries) if bib_entries else 0.0

    patterns = _section_map(config_tag)
    hits = sum(1 for pattern in patterns if pattern.search(content))
    section_completeness = hits / len(patterns)

    return {
        "file": md_path.name,
        "config": config_tag,
        "match_threshold": match_threshold,
        "retrieved_count": int(sidecar.get("retrieved_count", 0) or 0),
        "n_top_papers": len(top_papers),
        "abstract_coverage": abstract_coverage,
        "candidate_pool_size": len(candidate_pool),
        "total_citations": total_cites,
        "valid_citations": valid_cites,
        "text_orphans": text_orphans,
        "uncited_bibliography_entries": uncited_bib,
        "has_bibliography": bool(bib_entries),
        "bibliography_entries": len(bib_entries),
        "bibliography_match_rate": bibliography_match_rate,
        "citation_precision": citation_precision,
        "orphan_rate": orphan_rate,
        "section_hits": hits,
        "section_total": len(patterns),
        "section_completeness": section_completeness,
    }


def _agg(values: List[Optional[float]]) -> Tuple[float, float, int]:
    non_none = [value for value in values if value is not None]
    total = len(values)
    mean = sum(non_none) / len(non_none) if non_none else 0.0
    missing_frac = (total - len(non_none)) / total if total else 0.0
    return mean, missing_frac, total


def _print_summary(tag: str, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    prec_mean, no_cite_frac, n = _agg([row["citation_precision"] for row in rows])
    orphan_mean, _, _ = _agg([row["orphan_rate"] for row in rows])
    section_mean, _, _ = _agg([row["section_completeness"] for row in rows])
    bib_match_mean, _, _ = _agg([row["bibliography_match_rate"] for row in rows])
    abstract_cov_mean, _, _ = _agg([row["abstract_coverage"] for row in rows])

    print(f"\n=== {tag.upper()} | n={n} ===")
    print(f"  Citation Precision     : {prec_mean * 100:5.1f}%")
    print(f"  Orphan Citation Rate   : {orphan_mean * 100:5.1f}%")
    print(f"  Section Completeness   : {section_mean * 100:5.1f}%")
    print(f"  Bibliography Match Rate: {bib_match_mean * 100:5.1f}%")
    if tag != "baseline_a":
        print(f"  Abstract Coverage      : {abstract_cov_mean * 100:5.1f}%")
    if no_cite_frac > 0:
        print(f"  No-formal-citation frac: {no_cite_frac * 100:5.1f}%")

    return {
        "config": tag,
        "n": n,
        "citation_precision_pct": round(prec_mean * 100, 1),
        "orphan_rate_pct": round(orphan_mean * 100, 1),
        "section_completeness_pct": round(section_mean * 100, 1),
        "bibliography_match_rate_pct": round(bib_match_mean * 100, 1),
        "abstract_coverage_pct": round(abstract_cov_mean * 100, 1),
        "no_formal_citation_frac_pct": round(no_cite_frac * 100, 1),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate baseline / method outputs against the frozen corpus."
    )
    parser.add_argument(
        "--dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory containing markdown / json output pairs.",
    )
    parser.add_argument(
        "--tag",
        default=None,
        help="Override config tag (baseline_a / baseline_b / schema_single_agent / autosurvey / autosurvey_native / method1 / method2 / method2_same_model / method2c / method2d).",
    )
    parser.add_argument("--out-json", default=None, help="Optional JSON path for aggregate metrics.")
    parser.add_argument(
        "--corpus",
        required=True,
        help=(
            "Path to the frozen corpus JSON. REQUIRED to prevent silent corpus "
            "mismatch. Use 'data/frozen_corpus_multidomain_v1.json' (3,011 papers) "
            "for the expanded multi-domain benchmark (Tables in Sections 4.3 / "
            "Expanded benchmark), or 'data/topic_runs/multi_agent_intel_service_"
            "20260410_114059/retrieved_papers_wave3.json' (513 papers) for the MAS-"
            "domain pilot (Sections 4.2 / Pilot benchmark). See README_REPRODUCE.md "
            "for the canonical command per configuration."
        ),
    )
    parser.add_argument(
        "--match-threshold",
        type=float,
        default=0.72,
        help=(
            "Fuzzy title-match threshold for ICP/BMR (default 0.72). "
            "Use 0.90 for a stricter 'near-exact' auditability test, "
            "which reveals whether citations are genuinely exact-title matches "
            "vs. fuzzy approximations."
        ),
    )
    parser.add_argument(
        "--query-ids",
        default=None,
        help=(
            "Optional query-id filter, e.g. Q01-Q30 or Q01,Q03,Q05. "
            "Filtering is applied before per-query deduplication."
        ),
    )
    args = parser.parse_args()

    target_dir = Path(args.dir)
    if not target_dir.exists():
        raise SystemExit(f"Directory not found: {target_dir}")

    corpus_path = Path(args.corpus)
    if not corpus_path.exists():
        raise SystemExit(f"Corpus not found: {corpus_path}")
    corpus_data = json.loads(corpus_path.read_text(encoding="utf-8"))
    frozen_by_id: Dict[str, Dict[str, Any]] = {}
    for row in corpus_data:
        frozen_by_id[_paper_id(row)] = row
    print(f"[Corpus] Loaded {len(corpus_data)} papers from {corpus_path.name}")

    query_ids = _parse_query_ids(args.query_ids)

    md_files = list(target_dir.glob("*.md"))
    if not md_files:
        raise SystemExit(f"No markdown files found in {target_dir}")

    filtered_files = _filter_result_files(md_files, args.tag, query_ids)
    if not filtered_files:
        details = []
        if args.tag:
            details.append(f"tag={args.tag}")
        if query_ids is not None:
            details.append(f"query_ids={len(query_ids)}")
        suffix = f" ({', '.join(details)})" if details else ""
        raise SystemExit(f"No recognized result markdown files found in {target_dir}{suffix}")

    latest = _select_latest_per_query(filtered_files)
    if not latest:
        raise SystemExit(f"No recognized result markdown files found in {target_dir}")
    print(
        f"Found {len(md_files)} markdown files -> filtered to {len(filtered_files)} "
        f"for evaluation -> deduplicated to {len(latest)} canonical files."
    )

    rows_by_config: Dict[str, List[Dict[str, Any]]] = {}
    for _, path in sorted(latest.items()):
        parsed = _parse_result_stem(path.stem)
        parsed_tag = parsed[1] if parsed else None
        config_tag = args.tag or _infer_config_tag(path, parsed_tag)
        row = evaluate_file(path, config_tag, frozen_by_id, match_threshold=args.match_threshold)
        rows_by_config.setdefault(config_tag, []).append(row)

    if args.match_threshold != 0.72:
        print(f"[match-threshold mode: {args.match_threshold}  — stricter auditability test]")

    summaries = [_print_summary(tag, rows) for tag, rows in sorted(rows_by_config.items())]

    if args.out_json:
        out_path = Path(args.out_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(summaries, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nSaved aggregate metrics to {out_path}")


if __name__ == "__main__":
    main()
