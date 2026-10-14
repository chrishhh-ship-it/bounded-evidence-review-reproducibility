"""
run_bilingual_retrieval_exp.py
──────────────────────────────────────────────────────────────
双语检索消融实验：比较 zh_only / en_only / zh_en_union 三种检索条件。

设计原则：
1. 预先使用 Kimi 对每条 query 做学术检索翻译，并缓存到 JSON。
2. zh_only 仅走中文侧来源；en_only 仅走英文侧来源；union 由两侧显式合并去重。
3. 结果写入采用单进程锁 + 原子覆盖，支持断点续跑。
4. 严格验证不变量：|union| >= max(|zh|, |en|)；若 en>0 则 union 不可为 0。
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

from modules.ai_engine import AIEngine
from modules.searcher import (
    _load_saved_search_config,
    search_arxiv,
    search_crossref,
    search_openalex,
    search_pubmed,
    search_semantic_scholar,
    search_scopus,
)

QUERY_FILE = PROJECT_ROOT / "data" / "benchmarks" / "benchmark_all_queries.json"
OUT_DIR = PROJECT_ROOT / "data" / "bilingual_exp"

ZH_MODE = "zh_only"
EN_MODE = "en_only"
UNION_MODE = "zh_en_union"
ALL_MODES = (ZH_MODE, EN_MODE, UNION_MODE)

ENGLISH_SOURCES = ("arxiv", "semantic_scholar", "crossref", "pubmed", "openalex", "scopus")
CHINESE_SOURCES = ("wanfang", "crossref_zh", "openalex_zh")

GENERIC_EN_STOPWORDS = {
    "what", "which", "how", "when", "where", "why", "should", "could", "would",
    "does", "do", "did", "can", "using", "used", "based", "study", "analysis",
    "design", "system", "systems", "agent", "agents", "query", "queries", "paper",
    "research", "effect", "role", "roles", "impact", "improve", "improves",
    "literature", "academic", "service", "services", "designing", "verify",
    "identifying", "identify", "ability", "tests", "test", "approach",
}
PRIORITY_EN_PARTIALS = (
    "citation", "review", "retriev", "ground", "evidence", "hallucin",
    "benchmark", "corpus", "synthes", "rerank", "screen", "query",
)
TITLE_BLACKLIST_PATTERNS = (
    re.compile(r"^reviewer\s*#?\d+", re.I),
    re.compile(r"public review", re.I),
    re.compile(r"retracted", re.I),
)
GENERIC_ZH_STOPWORDS = {
    "如何", "什么", "哪些", "怎样", "是否", "为什么", "应该", "通过", "以及",
    "对于", "进行", "影响", "作用", "设计", "系统", "场景", "问题", "研究",
    "方法", "智能体", "多智能体", "文献", "证据", "情报", "服务", "中的",
}


def atomic_write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def process_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def acquire_lock(lock_path: Path) -> None:
    if lock_path.exists():
        try:
            data = json.loads(lock_path.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        pid = int(data.get("pid", 0) or 0)
        if process_is_alive(pid):
            raise RuntimeError(f"Another bilingual retrieval process is active (pid={pid}).")
        lock_path.unlink(missing_ok=True)

    payload = {
        "pid": os.getpid(),
        "started_at": datetime.now().isoformat(timespec="seconds"),
    }
    atomic_write_json(lock_path, payload)


def release_lock(lock_path: Path) -> None:
    lock_path.unlink(missing_ok=True)


def log_progress(log_path: Path, event: Dict) -> None:
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")


def _contains_chinese(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in text or "")


def _normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def title_key(title: str) -> str:
    title = _normalize_text(title)
    title = re.sub(r"[^\w\u4e00-\u9fff]+", "", title)
    return title[:120]


def deduplicate(papers: List[Dict]) -> List[Dict]:
    seen_title: set[str] = set()
    seen_doi: set[str] = set()
    unique: List[Dict] = []
    for paper in papers:
        doi = (paper.get("doi") or "").strip().lower()
        title = title_key(paper.get("title", ""))
        if doi and doi in seen_doi:
            continue
        if title and title in seen_title:
            continue
        if doi:
            seen_doi.add(doi)
        if title:
            seen_title.add(title)
        unique.append(paper)
    unique.sort(
        key=lambda row: (
            int(row.get("citations", 0) or 0),
            str(row.get("year", "") or ""),
        ),
        reverse=True,
    )
    return unique


def guess_language(paper: Dict) -> str:
    raw = (paper.get("language") or "").strip().lower()
    if raw:
        return raw
    text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
    return "zh" if _contains_chinese(text) else "en"


def normalize_paper(paper: Dict, source: str) -> Dict:
    row = dict(paper)
    row["source"] = row.get("source") or source
    row["title"] = (row.get("title") or "").strip()
    row["abstract"] = row.get("abstract") or ""
    row["doi"] = (row.get("doi") or "").strip()
    row["language"] = guess_language(row)
    return row


def title_is_blacklisted(title: str) -> bool:
    return any(pattern.search(title or "") for pattern in TITLE_BLACKLIST_PATTERNS)


def extract_en_terms(query_en: str) -> List[str]:
    query_en = _normalize_text(query_en)
    tokens = re.findall(r"[a-z][a-z0-9\-]{2,}", query_en)
    terms = [tok for tok in tokens if tok not in GENERIC_EN_STOPWORDS]
    seen: set[str] = set()
    ordered: List[str] = []
    for term in terms:
        if term not in seen:
            seen.add(term)
            ordered.append(term)
    return ordered[:10]


def extract_zh_terms(query_zh: str) -> List[str]:
    chunks = re.findall(r"[\u4e00-\u9fff]{2,}", query_zh or "")
    candidates: List[str] = []
    for chunk in chunks:
        if chunk in GENERIC_ZH_STOPWORDS:
            continue
        candidates.append(chunk)
        if len(chunk) >= 4:
            for width in (4, 3, 2):
                for idx in range(0, len(chunk) - width + 1):
                    gram = chunk[idx: idx + width]
                    if gram not in GENERIC_ZH_STOPWORDS:
                        candidates.append(gram)
    seen: set[str] = set()
    ordered: List[str] = []
    for term in candidates:
        if term not in seen:
            seen.add(term)
            ordered.append(term)
    return ordered[:12]


def strict_match_en(text: str, query_en: str) -> bool:
    if not query_en.strip():
        return False
    text = _normalize_text(text)
    query_en = _normalize_text(query_en)
    if query_en in text:
        return True
    terms = extract_en_terms(query_en)
    if not terms:
        return False
    hits = sum(1 for term in terms if term in text)
    threshold = 1 if len(terms) <= 2 else 2
    priority_terms = [
        term for term in terms
        if any(partial in term for partial in PRIORITY_EN_PARTIALS)
    ]
    anchor_terms = priority_terms[:3] if priority_terms else sorted(terms, key=len, reverse=True)[: max(1, min(3, len(terms)))]
    return hits >= threshold and any(anchor in text for anchor in anchor_terms)


def strict_match_zh(text: str, query_zh: str) -> bool:
    if not query_zh.strip():
        return False
    text = _normalize_text(text)
    if _normalize_text(query_zh) in text:
        return True
    terms = extract_zh_terms(query_zh)
    if not terms:
        return False
    hits = sum(1 for term in terms if term in text)
    return hits >= 1


def filter_english_results(papers: List[Dict], query_en: str) -> List[Dict]:
    filtered: List[Dict] = []
    for paper in papers:
        if title_is_blacklisted(paper.get("title", "")):
            continue
        text = f"{paper.get('title', '')} {paper.get('abstract', '')} {' '.join(paper.get('keywords', []) or [])}"
        if strict_match_en(text, query_en):
            filtered.append(paper)
    return filtered


def filter_chinese_results(papers: List[Dict], query_zh: str) -> List[Dict]:
    filtered: List[Dict] = []
    for paper in papers:
        if title_is_blacklisted(paper.get("title", "")):
            continue
        text = f"{paper.get('title', '')} {paper.get('abstract', '')} {' '.join(paper.get('keywords', []) or [])}"
        if strict_match_zh(text, query_zh):
            filtered.append(paper)
    return filtered


def load_queries(n: int, seed: int = 42) -> List[Dict]:
    with QUERY_FILE.open(encoding="utf-8") as fh:
        all_queries = json.load(fh)

    chinese_queries = [
        row for row in all_queries
        if row.get("lang", "zh") == "zh" or _contains_chinese(row.get("query", ""))
    ]
    print(f"  (filtered to {len(chinese_queries)} Chinese queries)")
    if n >= len(chinese_queries):
        return chinese_queries

    buckets: Dict[Tuple[str, int], List[Dict]] = {}
    for row in chinese_queries:
        key = (row.get("domain_id", ""), int(row.get("difficulty", 2) or 2))
        buckets.setdefault(key, []).append(row)

    rng = random.Random(seed)
    for key in buckets:
        rng.shuffle(buckets[key])
    keys = list(buckets.keys())
    rng.shuffle(keys)

    selected: List[Dict] = []
    cursor = {key: 0 for key in keys}
    while len(selected) < n:
        progressed = False
        for key in keys:
            idx = cursor[key]
            if idx < len(buckets[key]) and len(selected) < n:
                selected.append(buckets[key][idx])
                cursor[key] = idx + 1
                progressed = True
        if not progressed:
            break
    return selected


def load_translation_cache(cache_path: Path) -> Dict[str, Dict]:
    if not cache_path.exists():
        return {}
    try:
        raw = json.loads(cache_path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    if not isinstance(raw, dict):
        return {}

    # Backward compatibility: old format was {query_text: translation}
    if raw and all(isinstance(v, str) for v in raw.values()):
        converted: Dict[str, Dict] = {}
        for idx, (query_text, translated_en) in enumerate(raw.items(), start=1):
            converted[f"legacy_{idx:03d}"] = {
                "query_id": f"legacy_{idx:03d}",
                "query_text": query_text,
                "translated_en": translated_en,
                "provider": "legacy",
                "updated_at": datetime.now().isoformat(timespec="seconds"),
            }
        return converted

    cache: Dict[str, Dict] = {}
    for key, value in raw.items():
        if isinstance(value, dict) and value.get("translated_en"):
            cache[key] = value
    return cache


def _kimi_translate(engine: AIEngine, query_zh: str) -> str:
    prompt = (
        "Translate the following Chinese academic query into English academic search keywords. "
        "Return one keyword string only, max 12 words, prioritize technical nouns/entities, "
        "avoid generic verbs and function words, no sentence, no explanation, no numbering:\n"
        f"{query_zh}"
    )
    result, _ = engine._call_api(
        [{"role": "user", "content": prompt}],
        max_tokens=48,
        temperature=0.1,
    )
    translated = (result or "").strip().splitlines()[0].strip()
    translated = translated.strip("`\"' ")
    if (not translated) or ("failed after" in translated.lower()) or _contains_chinese(translated):
        raise RuntimeError(f"Kimi translation failed for query: {query_zh}")
    keywords = extract_en_terms(translated)
    if keywords:
        return " ".join(keywords[:8])
    return translated


def preload_translations(queries: List[Dict], cache_path: Path) -> Dict[str, str]:
    cfg = _load_saved_search_config()
    kimi_key = cfg.get("kimi_api_key", "")
    if not kimi_key:
        raise RuntimeError("Kimi API key is required for bilingual retrieval experiment.")

    cache = load_translation_cache(cache_path)
    engine = AIEngine(provider="kimi", api_key=kimi_key, model="moonshot-v1-8k", rate_limit_delay=1.2)
    updated = False
    translations: Dict[str, str] = {}

    for index, query in enumerate(queries, start=1):
        query_id = query["id"]
        query_text = query["query"]
        cached = cache.get(query_id)
        if cached and cached.get("query_text") == query_text and cached.get("translated_en"):
            translated = cached["translated_en"]
        else:
            translated = _kimi_translate(engine, query_text)
            cache[query_id] = {
                "query_id": query_id,
                "query_text": query_text,
                "translated_en": translated,
                "provider": "kimi",
                "updated_at": datetime.now().isoformat(timespec="seconds"),
            }
            updated = True
            print(f"  [translate {index}/{len(queries)}] {query_id}: {translated}")
            time.sleep(0.3)
        translations[query_id] = translated

    if updated or not cache_path.exists():
        atomic_write_json(cache_path, cache)
    return translations


def build_cn_manager(cfg: Dict):
    from modules.chinese_searcher import ChineseSearchManager

    manager = ChineseSearchManager()
    serp_key = cfg.get("serp_api_key", "")
    scraper_key = cfg.get("scraper_api_key", "")
    proxy = cfg.get("proxy", "")
    if serp_key:
        manager.google_scholar.set_serp_api_key(serp_key)
    if scraper_key:
        manager.google_scholar.set_scraper_api_key(scraper_key)
    if proxy:
        manager.google_scholar.set_proxy(proxy)
    return manager


def search_zh_sources(query_zh: str, top_k: int, years_back: int, cfg: Dict, log_path: Path, query_id: str) -> List[Dict]:
    manager = build_cn_manager(cfg)
    papers: List[Dict] = []
    email = cfg.get("openalex_email", "")

    for source_name in CHINESE_SOURCES:
        started = time.time()
        try:
            if source_name == "wanfang":
                rows = manager.wanfang.search(query_zh, max_results=top_k, years_back=years_back)
            elif source_name == "crossref_zh":
                rows = search_crossref(query_zh, top_k, years_back)
            elif source_name == "openalex_zh":
                rows = search_openalex(query_zh, top_k, years_back, email=email)
            else:
                rows = []
            rows = [normalize_paper(row, source_name) for row in rows]
            rows = filter_chinese_results(rows, query_zh)
            papers.extend(rows)
            log_progress(log_path, {
                "ts": datetime.now().isoformat(timespec="seconds"),
                "query_id": query_id,
                "mode": ZH_MODE,
                "source": source_name,
                "count": len(rows),
                "elapsed_s": round(time.time() - started, 2),
            })
        except Exception as exc:
            log_progress(log_path, {
                "ts": datetime.now().isoformat(timespec="seconds"),
                "query_id": query_id,
                "mode": ZH_MODE,
                "source": source_name,
                "error": str(exc),
            })
        time.sleep(0.7)
    return deduplicate(papers)


def search_en_sources(query_en: str, top_k: int, years_back: int, cfg: Dict, log_path: Path, query_id: str) -> List[Dict]:
    papers: List[Dict] = []
    email = cfg.get("openalex_email", "")

    source_calls = [
        ("arxiv", lambda: search_arxiv(query_en, top_k, years_back)),
        ("semantic_scholar", lambda: search_semantic_scholar(query_en, top_k, years_back)),
        ("crossref", lambda: search_crossref(query_en, top_k, years_back)),
        ("pubmed", lambda: search_pubmed(query_en, top_k, years_back)),
        ("openalex", lambda: search_openalex(query_en, top_k, years_back, email=email)),
    ]
    if cfg.get("scopus_api_key"):
        source_calls.append((
            "scopus",
            lambda: search_scopus(
                query_en,
                max_results=top_k,
                years_back=years_back,
                api_key=cfg.get("scopus_api_key", ""),
                inst_token=cfg.get("scopus_inst_token", ""),
                sort=cfg.get("scopus_sort", "citedby-count"),
            ),
        ))

    for source_name, fn in source_calls:
        started = time.time()
        try:
            rows = fn() or []
            rows = [normalize_paper(row, source_name) for row in rows]
            rows = filter_english_results(rows, query_en)
            papers.extend(rows)
            log_progress(log_path, {
                "ts": datetime.now().isoformat(timespec="seconds"),
                "query_id": query_id,
                "mode": EN_MODE,
                "source": source_name,
                "count": len(rows),
                "elapsed_s": round(time.time() - started, 2),
            })
        except Exception as exc:
            log_progress(log_path, {
                "ts": datetime.now().isoformat(timespec="seconds"),
                "query_id": query_id,
                "mode": EN_MODE,
                "source": source_name,
                "error": str(exc),
            })
        time.sleep(0.8)
    return deduplicate(papers)


def serialize_corpus(papers: List[Dict]) -> List[Dict]:
    return [
        {
            "title": paper.get("title", ""),
            "source": paper.get("source", ""),
            "language": paper.get("language", ""),
            "doi": (paper.get("doi") or "").strip(),
            "has_abstract": bool((paper.get("abstract") or "").strip()),
            "year": paper.get("year", ""),
            "citations": int(paper.get("citations", 0) or 0),
        }
        for paper in papers
    ]


def validate_result(result: Dict) -> None:
    corpora = result["corpora"]
    zh_size = len(corpora[ZH_MODE])
    en_size = len(corpora[EN_MODE])
    union_size = len(corpora[UNION_MODE])
    if union_size < max(zh_size, en_size):
        raise ValueError(
            f"Invalid union size for {result['query_id']}: zh={zh_size}, en={en_size}, union={union_size}"
        )
    if en_size > 0 and union_size == 0:
        raise ValueError(
            f"Invalid union size for {result['query_id']}: en={en_size} but union=0"
        )


def run_query(query: Dict, top_k: int, years_back: int, translations: Dict[str, str], cfg: Dict, log_path: Path) -> Dict:
    query_id = query["id"]
    query_text = query["query"]
    query_en = (translations.get(query_id) or "").strip()
    if not query_en:
        raise RuntimeError(f"Missing English override for {query_id}")

    print(f"\n[{query_id}] {query_text}")
    print(f"  EN: {query_en}")

    zh_papers = search_zh_sources(query_text, top_k, years_back, cfg, log_path, query_id)
    print(f"  {ZH_MODE}: {len(zh_papers)} docs")
    en_papers = search_en_sources(query_en, top_k, years_back, cfg, log_path, query_id)
    print(f"  {EN_MODE}: {len(en_papers)} docs")
    union_papers = deduplicate(zh_papers + en_papers)
    print(f"  {UNION_MODE}: {len(union_papers)} docs")

    result = {
        "query_id": query_id,
        "domain_id": query.get("domain_id", ""),
        "difficulty": int(query.get("difficulty", 2) or 2),
        "query_text": query_text,
        "query_en": query_en,
        "corpora": {
            ZH_MODE: serialize_corpus(zh_papers),
            EN_MODE: serialize_corpus(en_papers),
            UNION_MODE: serialize_corpus(union_papers),
        },
        "completed_at": datetime.now().isoformat(timespec="seconds"),
    }
    validate_result(result)
    return result


def compute_metrics(result: Dict) -> Dict:
    corpora = result["corpora"]
    zh = corpora.get(ZH_MODE, [])
    en = corpora.get(EN_MODE, [])
    union = corpora.get(UNION_MODE, [])

    def coverage(corpus: List[Dict]) -> int:
        return len(corpus)

    def acr(corpus: List[Dict]) -> float:
        return sum(1 for row in corpus if row["has_abstract"]) / len(corpus) if corpus else 0.0

    def dcr(corpus: List[Dict]) -> float:
        return sum(1 for row in corpus if row["doi"]) / len(corpus) if corpus else 0.0

    def src_div(corpus: List[Dict]) -> int:
        return len({row["source"] for row in corpus if row["source"]})

    def cn_ratio(corpus: List[Dict]) -> float:
        return sum(1 for row in corpus if row.get("language", "").startswith("zh")) / len(corpus) if corpus else 0.0

    zh_titles = {title_key(row["title"]) for row in zh}
    en_titles = {title_key(row["title"]) for row in en}
    union_titles = {title_key(row["title"]) for row in union}
    en_exclusive = {key for key in union_titles if key and key not in zh_titles}
    zh_exclusive = {key for key in union_titles if key and key not in en_titles}
    best_single = max(coverage(zh), coverage(en))
    bcu = ((coverage(union) - best_single) / best_single * 100.0) if best_single else 0.0
    clg = (len(en_exclusive) / coverage(union) * 100.0) if union else 0.0
    zlg = (len(zh_exclusive) / coverage(union) * 100.0) if union else 0.0

    return {
        "query_id": result["query_id"],
        "domain_id": result["domain_id"],
        "difficulty": result["difficulty"],
        "size_zh": coverage(zh),
        "size_en": coverage(en),
        "size_union": coverage(union),
        "bcu_pct": round(bcu, 2),
        "clg_pct": round(clg, 2),
        "zlg_pct": round(zlg, 2),
        "acr_zh": round(acr(zh), 4),
        "acr_en": round(acr(en), 4),
        "acr_union": round(acr(union), 4),
        "dcr_zh": round(dcr(zh), 4),
        "dcr_en": round(dcr(en), 4),
        "dcr_union": round(dcr(union), 4),
        "src_div_zh": src_div(zh),
        "src_div_en": src_div(en),
        "src_div_union": src_div(union),
        "cn_ratio_union": round(cn_ratio(union), 4),
    }


def aggregate_metrics(all_metrics: List[Dict]) -> Dict:
    def avg(values: Iterable[float]) -> float:
        values = list(values)
        return round(sum(values) / len(values), 4) if values else 0.0

    fields = [
        "bcu_pct", "clg_pct", "zlg_pct",
        "size_zh", "size_en", "size_union",
        "acr_zh", "acr_en", "acr_union",
        "dcr_zh", "dcr_en", "dcr_union",
        "src_div_zh", "src_div_en", "src_div_union",
        "cn_ratio_union",
    ]
    agg = {"overall": {field: avg(item[field] for item in all_metrics) for field in fields}}
    agg["overall"]["n"] = len(all_metrics)

    by_domain: Dict[str, List[Dict]] = {}
    for item in all_metrics:
        by_domain.setdefault(item["domain_id"], []).append(item)
    for domain_id, rows in by_domain.items():
        agg[domain_id] = {field: avg(item[field] for item in rows) for field in fields}
        agg[domain_id]["n"] = len(rows)
    return agg


def print_summary(agg: Dict) -> None:
    overall = agg["overall"]
    print("\n" + "═" * 72)
    print(f"  双语检索实验汇总 (n={overall['n']} queries)")
    print("═" * 72)
    print(f"  {'Metric':<28} {'ZH-only':>10} {'EN-only':>10} {'ZH+EN':>10}")
    print(f"  {'Coverage C (avg)':<28} {overall['size_zh']:>10.1f} {overall['size_en']:>10.1f} {overall['size_union']:>10.1f}")
    print(f"  {'Abstract coverage (ACR)':<28} {overall['acr_zh']:>10.1%} {overall['acr_en']:>10.1%} {overall['acr_union']:>10.1%}")
    print(f"  {'DOI coverage (DCR)':<28} {overall['dcr_zh']:>10.1%} {overall['dcr_en']:>10.1%} {overall['dcr_union']:>10.1%}")
    print(f"  {'Source diversity':<28} {overall['src_div_zh']:>10.1f} {overall['src_div_en']:>10.1f} {overall['src_div_union']:>10.1f}")
    print("  " + "-" * 58)
    print(f"  {'BCU vs best single':<28} {'':>10} {'':>10} {overall['bcu_pct']:>9.1f}%")
    print(f"  {'CLG (EN-exclusive)':<28} {'':>10} {'':>10} {overall['clg_pct']:>9.1f}%")
    print(f"  {'ZLG (ZH-exclusive)':<28} {'':>10} {'':>10} {overall['zlg_pct']:>9.1f}%")
    print(f"  {'CN ratio in union':<28} {'':>10} {'':>10} {overall['cn_ratio_union']:>10.1%}")


def load_existing_results(results_path: Path) -> Dict[str, Dict]:
    existing: Dict[str, Dict] = {}

    query_dir = results_path.parent / "query_results"
    if query_dir.exists():
        for item in sorted(query_dir.glob("Q*.json")):
            try:
                row = json.loads(item.read_text(encoding="utf-8"))
                validate_result(row)
                existing[row["query_id"]] = row
            except Exception:
                continue

    if not results_path.exists():
        return existing
    try:
        rows = json.loads(results_path.read_text(encoding="utf-8"))
    except Exception:
        return existing
    if not isinstance(rows, list):
        return existing
    for row in rows:
        query_id = row.get("query_id")
        if not query_id:
            continue
        try:
            validate_result(row)
        except Exception:
            continue
        existing[query_id] = row
    return existing


def maybe_reset_output(out_dir: Path, resume: bool) -> None:
    if resume:
        return
    for name in (
        "retrieval_results.json",
        "retrieval_metrics.json",
        "retrieval_metrics_agg.json",
        "progress_log.jsonl",
        "latest_snapshot.json",
    ):
        (out_dir / name).unlink(missing_ok=True)
    query_dir = out_dir / "query_results"
    if query_dir.exists():
        for item in query_dir.glob("Q*.json"):
            item.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=30)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--years-back", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=str, default=str(OUT_DIR))
    parser.add_argument("--metrics-only", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    results_path = out_dir / "retrieval_results.json"
    metrics_path = out_dir / "retrieval_metrics.json"
    agg_path = out_dir / "retrieval_metrics_agg.json"
    cache_path = out_dir / "query_translations.json"
    log_path = out_dir / "progress_log.jsonl"
    lock_path = out_dir / ".run.lock"

    acquire_lock(lock_path)
    try:
        if not args.metrics_only:
            maybe_reset_output(out_dir, resume=args.resume)

        if not args.metrics_only:
            queries = load_queries(args.n, seed=args.seed)
            print(f"Loaded {len(queries)} queries.")
            print("Step 1: Pre-translating all queries via Kimi...")
            translations = preload_translations(queries, cache_path)
            print(f"  Translation cache ready: {len(translations)} entries")

            existing = load_existing_results(results_path) if args.resume else {}
            cfg = _load_saved_search_config()
            all_results = existing.copy()

            for index, query in enumerate(queries, start=1):
                query_id = query["id"]
                if query_id in all_results:
                    print(f"[{index}/{len(queries)}] {query_id} already complete; skip")
                    continue
                print(f"\n[{index}/{len(queries)}] running {query_id}")
                try:
                    result = run_query(query, args.top_k, args.years_back, translations, cfg, log_path)
                    all_results[query_id] = result
                    atomic_write_json(out_dir / "query_results" / f"{query_id}.json", result)
                    ordered = [all_results[q["id"]] for q in queries if q["id"] in all_results]
                    atomic_write_json(results_path, ordered)
                    atomic_write_json(out_dir / "latest_snapshot.json", {
                        "completed_queries": len(ordered),
                        "total_queries": len(queries),
                        "updated_at": datetime.now().isoformat(timespec="seconds"),
                    })
                except Exception as exc:
                    log_progress(log_path, {
                        "ts": datetime.now().isoformat(timespec="seconds"),
                        "query_id": query_id,
                        "fatal_error": str(exc),
                    })
                    raise

            ordered_results = [all_results[q["id"]] for q in queries if q["id"] in all_results]
            print(f"\n[done] retrieval complete: {len(ordered_results)} queries")
        else:
            ordered_results = list(load_existing_results(results_path).values())
            if not ordered_results:
                raise RuntimeError(f"No valid results found in {results_path}")

        all_metrics = [compute_metrics(item) for item in ordered_results]
        agg = aggregate_metrics(all_metrics)
        atomic_write_json(metrics_path, all_metrics)
        atomic_write_json(agg_path, agg)
        print_summary(agg)
        print(f"\n[done] metrics: {metrics_path}")
        print(f"[done] aggregate: {agg_path}")
    finally:
        release_lock(lock_path)


if __name__ == "__main__":
    main()
