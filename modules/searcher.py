# ==============================================================
# searcher.py
# ==============================================================

import requests
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time
import re
import json
import os
import logging

logger = logging.getLogger(__name__)


# ==============================================================
# Chinese-English bilingual research field dictionary
# ==============================================================
FIELD_TRANSLATIONS = {
    # ── 数字人文 / 交叉学科 ──────────────────────────────────
    "数字人文": "digital humanities",
    "人文计算": "digital humanities",
    "计算社会科学": "computational social science",
    "社会网络分析": "social network analysis",
    # ── 通用 AI / ML ─────────────────────────────────────────
    "人工智能": "artificial intelligence",
    "机器学习": "machine learning",
    "深度学习": "deep learning",
    "神经网络": "neural network",
    "强化学习": "reinforcement learning",
    "联邦学习": "federated learning",
    "迁移学习": "transfer learning",
    "元学习": "meta-learning",
    "对比学习": "contrastive learning",
    "自监督学习": "self-supervised learning",
    "表示学习": "representation learning",
    # ── 大语言模型 / NLP ─────────────────────────────────────
    "大语言模型": "large language model",
    "大模型": "large language model",
    "语言模型": "language model",
    "自然语言处理": "natural language processing",
    "文本生成": "text generation",
    "机器翻译": "machine translation",
    "问答系统": "question answering",
    "信息抽取": "information extraction",
    "文本分类": "text classification",
    "命名实体识别": "named entity recognition",
    "知识图谱": "knowledge graph",
    "文本挖掘": "text mining",
    "情感分析": "sentiment analysis",
    "语义理解": "semantic understanding",
    "Transformer": "transformer",
    "注意力机制": "attention mechanism",
    "提示工程": "prompt engineering",
    "思维链": "chain of thought",
    "检索增强生成": "retrieval augmented generation",
    # ── 多模态 / 视觉 ────────────────────────────────────────
    "多模态": "multimodal",
    "视觉语言模型": "vision language model",
    "计算机视觉": "computer vision",
    "图像分类": "image classification",
    "目标检测": "object detection",
    "图像分割": "image segmentation",
    "图像生成": "image generation",
    "扩散模型": "diffusion model",
    "生成对抗网络": "generative adversarial network",
    "视频理解": "video understanding",
    # ── Agent / 具身 ─────────────────────────────────────────
    "智能体": "agent",
    "具身智能": "embodied intelligence",
    "机器人": "robotics",
    "自动驾驶": "autonomous driving",
    # ── 推荐 / 搜索 ──────────────────────────────────────────
    "推荐系统": "recommender system",
    "信息检索": "information retrieval",
    "知识推理": "knowledge reasoning",
    "图神经网络": "graph neural network",
    # ── 可信 AI ──────────────────────────────────────────────
    "可解释性": "explainability",
    "可解释人工智能": "explainable artificial intelligence",
    "公平性": "fairness machine learning",
    "对抗攻击": "adversarial attack",
    "隐私保护": "privacy preserving",
    # ── 经济 / 管理 ──────────────────────────────────────────
    "博弈论": "game theory",
    "供应链管理": "supply chain management",
    "运筹学": "operations research",
    "数字经济": "digital economy",
    "平台经济": "platform economy",
    "创新管理": "innovation management",
    "金融": "finance",
    "计量经济学": "econometrics",
    "金融科技": "financial technology",
    # ── 人文社科 ────────────────────────────────────────────
    "文化遗产": "cultural heritage",
    "历史学": "history",
    "文学": "literature",
    "考古学": "archaeology",
    "档案学": "archival studies",
    "语言学": "linguistics",
    "哲学": "philosophy",
    "教育学": "education",
    "公共管理": "public administration",
}

ENGLISH_TO_FIELD = {}
for _cn_field, _en_field in FIELD_TRANSLATIONS.items():
    ENGLISH_TO_FIELD.setdefault(_en_field.lower(), _cn_field)

def _contains_chinese(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def _load_saved_search_config() -> dict:
    """加载搜索配置。优先级：环境变量(.env) > gs_config.json"""
    # 1. 尝试从 .env 加载环境变量
    try:
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        load_dotenv(env_path, override=False)
    except ImportError:
        pass

    # 2. 环境变量映射
    _ENV_MAP = {
        "serp_api_key":    "SERP_API_KEY",
        "scraper_api_key": "SCRAPER_API_KEY",
        "scopus_api_key":  "SCOPUS_API_KEY",
        "kimi_api_key":    "KIMI_API_KEY",
        "deepseek_api_key": "DEEPSEEK_API_KEY",
        "openai_api_key":  "OPENAI_API_KEY",
        "proxy":           "PROXY",
    }
    env_cfg = {}
    for cfg_key, env_key in _ENV_MAP.items():
        val = os.environ.get(env_key, "")
        if val:
            env_cfg[cfg_key] = val

    # 3. Fallback: gs_config.json
    cfg_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "gs_config.json",
    )
    file_cfg = {}
    try:
        if os.path.exists(cfg_path):
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                file_cfg = data if isinstance(data, dict) else {}
    except Exception as e:
        logger.warning(f"[Search] load gs_config.json failed: {e}")

    # 环境变量优先
    merged = dict(file_cfg)
    merged.update(env_cfg)
    return merged


def _merge_search_config(config: dict | None) -> dict:
    saved = _load_saved_search_config()
    merged = dict(saved)
    if config:
        merged.update({k: v for k, v in config.items() if v not in (None, "")})
    return merged


def _translate_query(query: str) -> tuple:
    """
    Resolve a query into bilingual search terms.

    Returns:
        (chinese_query, english_query)

    Behavior:
    - Chinese input: translate to English when possible.
    - English input: map back to a known Chinese field label when possible.
    - Unknown input: preserve the original query on its own side.
    """
    query = query.strip()

    if not _contains_chinese(query):
        lowered = query.lower()
        if lowered in ENGLISH_TO_FIELD:
            return (ENGLISH_TO_FIELD[lowered], query)

        best_cn = ""
        best_en = ""
        for en, cn in ENGLISH_TO_FIELD.items():
            if en in lowered and len(en) > len(best_en):
                best_en = en
                best_cn = cn
        if best_cn:
            return (best_cn, query)
        return (None, query)

    # Exact match
    if query in FIELD_TRANSLATIONS:
        return (query, FIELD_TRANSLATIONS[query])

    # Try partial match: find the longest matching substring
    best_match = ""
    best_en = ""
    for cn, en in FIELD_TRANSLATIONS.items():
        if cn in query and len(cn) > len(best_match):
            best_match = cn
            best_en = en

    if best_match:
        # Replace the matched part and keep the rest
        remaining = query.replace(best_match, "").strip()
        if remaining and _contains_chinese(remaining):
            # Try to translate remaining part too
            if remaining in FIELD_TRANSLATIONS:
                return (query, f"{best_en} {FIELD_TRANSLATIONS[remaining]}")
        return (query, best_en)

    # No translation found - preserve original query for Chinese-capable sources
    return (query, query)


def _check_relevance(paper: dict, query_cn: str, query_en: str) -> bool:
    """
    Basic relevance check: does the paper's title or abstract
    contain any of the query keywords?

    """
    source = (paper.get("source", "") or "").lower()
    if source in ("scopus", "web of science", "wos") and query_en and " " in query_en.strip():
        return True
    if source in ("scopus", "web of science", "wos") and not any(
        paper.get(field) for field in ("title", "abstract", "keywords")
    ):
        return True

    title = (paper.get("title", "") or "").lower()
    abstract = (paper.get("abstract", "") or "").lower()
    keywords = " ".join(paper.get("keywords", []) or []).lower()
    text = f"{title} {abstract} {keywords}"

    # Build keyword list from both Chinese and English queries
    check_terms = []

    # English query terms (split by space, filter short words)
    if query_en:
        en_lower = query_en.lower()
        # Check full phrase first
        if en_lower in text:
            return True
        # Check individual significant words
        for word in en_lower.split():
            if len(word) >= 4:  # skip short words like "of", "the", "and"
                check_terms.append(word)

    # Chinese query (check as whole string)
    if query_cn and query_cn in text:
        return True

    if check_terms:
        matches = sum(1 for term in check_terms if term in text)
        if len(check_terms) <= 2:
            threshold = len(check_terms)
        else:
            threshold = max(2, (len(check_terms) * 3 + 4) // 5)
        return matches >= threshold

    return True  # If we can't determine, keep it


# ==============================================================
# HTTP helper
# ==============================================================
def _safe_get(url: str, params: dict = None, headers: dict = None, timeout: int = 15) -> requests.Response | None:
    for attempt in range(4):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                return resp
            if resp.status_code == 429:
                # Exponential-style backoff for rate-limited APIs.
                wait = [5, 10, 20, 30][attempt]
                print(f"[HTTP] 429 rate limit, wait {wait}s ({attempt + 1}/4)")
                time.sleep(wait)
                continue
            if resp.status_code in (401, 403):
                print(f"[HTTP] auth failed ({resp.status_code}), check API key")
                return None
            print(f"[HTTP] status {resp.status_code}, retry ({attempt + 1}/4)")
            time.sleep(2 * (attempt + 1))
        except requests.exceptions.Timeout:
            print(f"[HTTP] timeout, retry ({attempt + 1}/4)")
            time.sleep(3 * (attempt + 1))
        except requests.exceptions.ConnectionError:
            print(f"[HTTP] connection error, retry ({attempt + 1}/4)")
            time.sleep(3 * (attempt + 1))
        except Exception as e:
            print(f"[HTTP] error: {e}, retry ({attempt + 1}/4)")
            time.sleep(2)
    return None


# ==============================================================
# arXiv
# ==============================================================
def search_arxiv(query: str, max_results: int = 50, years_back: int = 5) -> list[dict]:
    base_url = "http://export.arxiv.org/api/query"
    date_from = (datetime.now() - timedelta(days=365 * years_back)).strftime("%Y%m%d")

    # ti+abs 鑱斿悎鏌ヨ锛屼娇鐢ㄦ墍鏈夊叧閿瘝
    words = query.strip().split()
    if len(words) <= 2:
        safe_query = f"all:{query}"
    else:
        # 鏍囬鐢ㄥ墠涓や釜鍏抽敭璇嶏紝鎽樿鐢ㄦ墍鏈夊叧閿瘝鐨?OR 缁勫悎
        abs_terms = " OR ".join(f"abs:{w}" for w in words)
        safe_query = f'ti:{words[0]} AND ti:{words[1]} AND ({abs_terms})'
    q = f"{safe_query} AND submittedDate:[{date_from} TO 99991231]"
    params = {
        "search_query": q,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }

    resp = _safe_get(base_url, params=params)
    if not resp:
        return []

    papers = []
    try:
        ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
        root = ET.fromstring(resp.text)

        for entry in root.findall("atom:entry", ns):
            title = (entry.find("atom:title", ns).text or "").replace("\n", " ").strip()
            abstract = (entry.find("atom:summary", ns).text or "").replace("\n", " ").strip()
            published = entry.find("atom:published", ns).text or ""
            year = published[:4] if published else ""

            authors = [
                a.find("atom:name", ns).text
                for a in entry.findall("atom:author", ns)
                if a.find("atom:name", ns) is not None
            ]

            arxiv_id_el = entry.find("atom:id", ns)
            url = arxiv_id_el.text if arxiv_id_el is not None else ""
            arxiv_id = url.split("/abs/")[-1] if "/abs/" in url else ""

            journal_ref_el = entry.find("arxiv:journal_ref", ns)
            journal = journal_ref_el.text if journal_ref_el is not None else "arXiv Preprint"

            categories = [
                c.get("term", "") for c in entry.findall("atom:category", ns)
            ]

            papers.append({
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "year": year,
                "published_date": published[:10],
                "journal": journal,
                "url": url,
                "arxiv_id": arxiv_id,
                "keywords": categories[:5],
                "citations": 0,
                "source": "arXiv",
                "doi": "",
            })
    except Exception as e:
        print(f"[arXiv] {e}")

    return papers


# ==============================================================
# Semantic Scholar
# ==============================================================
def search_semantic_scholar(query: str, max_results: int = 50, years_back: int = 5) -> list[dict]:
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    year_start = datetime.now().year - years_back
    fields = "title,authors,abstract,year,citationCount,externalIds,venue,fieldsOfStudy,publicationDate"

    params = {
        "query": query,
        "limit": min(max_results, 100),
        "fields": fields,
        "year": f"{year_start}-",
    }
    headers = {"User-Agent": "ResearchAssistant/2.0 (academic research tool)"}

    resp = _safe_get(base_url, params=params, headers=headers)
    if not resp:
        return []

    papers = []
    try:
        data = resp.json()
        for item in data.get("data", []):
            authors = [a.get("name", "") for a in item.get("authors", [])]
            year = item.get("year") or (item.get("publicationDate", "") or "")[:4] or ""
            doi = (item.get("externalIds") or {}).get("DOI", "")
            arxiv_id = (item.get("externalIds") or {}).get("ArXiv", "")
            url = f"https://www.semanticscholar.org/paper/{item.get('paperId', '')}"

            papers.append({
                "title": item.get("title", ""),
                "authors": authors,
                "abstract": item.get("abstract", "") or "",
                "year": str(year),
                "published_date": item.get("publicationDate", "") or "",
                "journal": item.get("venue", "") or "Semantic Scholar",
                "url": url,
                "arxiv_id": arxiv_id,
                "keywords": item.get("fieldsOfStudy", []) or [],
                "citations": item.get("citationCount", 0) or 0,
                "source": "Semantic Scholar",
                "doi": doi,
            })
    except Exception as e:
        print(f"[Semantic Scholar] {e}")

    return papers


# ==============================================================
# CrossRef
# ==============================================================
def search_crossref(query: str, max_results: int = 50, years_back: int = 5) -> list[dict]:
    base_url = "https://api.crossref.org/works"
    year_start = datetime.now().year - years_back

    params = {
        "query": query,
        "rows": min(max_results, 100),
        "sort": "relevance",
        "order": "desc",
        "filter": f"from-pub-date:{year_start}",
        "select": "title,author,abstract,published,DOI,URL,container-title,subject,is-referenced-by-count",
    }
    headers = {
        "User-Agent": "ResearchAssistant/2.0 (mailto:research@example.com)",
        "Accept": "application/json",
    }

    resp = _safe_get(base_url, params=params, headers=headers)
    if not resp:
        return []

    papers = []
    try:
        data = resp.json()
        for item in data.get("message", {}).get("items", []):
            title_list = item.get("title", [])
            title = title_list[0] if title_list else ""

            authors = []
            for a in item.get("author", []):
                name = f"{a.get('given', '')} {a.get('family', '')}".strip()
                if name:
                    authors.append(name)

            pub_date = item.get("published", {}).get("date-parts", [[None]])[0]
            year = str(pub_date[0]) if pub_date and pub_date[0] else ""
            published_date = "-".join(str(p) for p in pub_date if p) if pub_date else ""

            journal_list = item.get("container-title", [])
            journal = journal_list[0] if journal_list else "CrossRef"

            doi = item.get("DOI", "")
            url = item.get("URL", f"https://doi.org/{doi}" if doi else "")
            abstract_raw = item.get("abstract", "") or ""
            abstract = re.sub(r"<[^>]+>", "", abstract_raw).strip()

            papers.append({
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "year": year,
                "published_date": published_date,
                "journal": journal,
                "url": url,
                "arxiv_id": "",
                "keywords": item.get("subject", []) or [],
                "citations": item.get("is-referenced-by-count", 0) or 0,
                "source": "CrossRef",
                "doi": doi,
            })
    except Exception as e:
        print(f"[CrossRef] {e}")

    return papers


# ==============================================================
# PubMed
# ==============================================================
def search_pubmed(query: str, max_results: int = 50, years_back: int = 5) -> list[dict]:
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    year_start = datetime.now().year - years_back

    search_url = f"{base_url}/esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": f"{query} AND {year_start}:{datetime.now().year}[dp]",
        "retmax": min(max_results, 200),
        "sort": "relevance",
        "retmode": "json",
    }
    resp = _safe_get(search_url, params=search_params)
    if not resp:
        return []

    try:
        pmids = resp.json().get("esearchresult", {}).get("idlist", [])
    except Exception:
        return []

    if not pmids:
        return []

    fetch_url = f"{base_url}/efetch.fcgi"
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(pmids[:max_results]),
        "rettype": "xml",
        "retmode": "xml",
    }
    resp2 = _safe_get(fetch_url, params=fetch_params)
    if not resp2:
        return []

    papers = []
    try:
        root = ET.fromstring(resp2.text)
        for article in root.findall(".//PubmedArticle"):
            title_el = article.find(".//ArticleTitle")
            title = (title_el.text or "") if title_el is not None else ""
            title = re.sub(r"<[^>]+>", "", title).strip()

            abstract_els = article.findall(".//AbstractText")
            abstract = " ".join(
                re.sub(r"<[^>]+>", "", (el.text or ""))
                for el in abstract_els
            ).strip()

            authors = []
            for a in article.findall(".//Author"):
                last = a.find("LastName")
                fore = a.find("ForeName")
                if last is not None:
                    name = f"{fore.text if fore is not None else ''} {last.text}".strip()
                    authors.append(name)

            year_el = article.find(".//PubDate/Year")
            year = year_el.text if year_el is not None else ""

            journal_el = article.find(".//Journal/Title")
            journal = journal_el.text if journal_el is not None else "PubMed"

            pmid_el = article.find(".//PMID")
            pmid = pmid_el.text if pmid_el is not None else ""
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""

            doi_els = article.findall(".//ArticleId[@IdType='doi']")
            doi = doi_els[0].text if doi_els else ""

            mesh_terms = [
                m.text for m in article.findall(".//MeshHeading/DescriptorName")
                if m.text
            ]

            papers.append({
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "year": year,
                "published_date": year,
                "journal": journal,
                "url": url,
                "arxiv_id": "",
                "keywords": mesh_terms[:8],
                "citations": 0,
                "source": "PubMed",
                "doi": doi,
            })
    except Exception as e:
        print(f"[PubMed] {e}")

    return papers


# ==============================================================
# OpenAlex (250M+ papers, supports Chinese metadata)
# ==============================================================
def _reconstruct_abstract(inverted_index: dict) -> str:
    if not inverted_index:
        return ""
    positions: dict[int, str] = {}
    for word, locs in inverted_index.items():
        for pos in locs:
            positions[pos] = word
    return " ".join(positions[k] for k in sorted(positions.keys()))


def search_openalex(query: str, max_results: int = 50, years_back: int = 5,
                    email: str = "") -> list[dict]:
    base_url = "https://api.openalex.org/works"
    year_start = datetime.now().year - years_back

    fields = (
        "id,title,authorships,abstract_inverted_index,"
        "publication_year,publication_date,primary_location,"
        "cited_by_count,keywords,concepts,doi,open_access"
    )
    params = {
        "search": query,
        "per-page": min(max_results, 200),
        "filter": f"publication_year:>{year_start - 1}",
        "sort": "relevance_score:desc",
        "select": fields,
    }
    headers = {
        "User-Agent": f"ResearchAssistant/2.0 ({email or 'research@example.com'})"
    }

    resp = _safe_get(base_url, params=params, headers=headers)
    if not resp:
        return []

    papers = []
    try:
        data = resp.json()
        for item in data.get("results", []):
            title = item.get("title", "") or ""
            if not title:
                continue

            abstract = _reconstruct_abstract(
                item.get("abstract_inverted_index") or {}
            )

            authors = [
                a.get("author", {}).get("display_name", "")
                for a in item.get("authorships", [])
                if a.get("author")
            ]

            primary = item.get("primary_location") or {}
            source = primary.get("source") or {}
            journal = source.get("display_name", "") or "OpenAlex"

            year = str(item.get("publication_year", "")) or ""
            pub_date = item.get("publication_date", "") or ""

            citations = item.get("cited_by_count", 0) or 0

            doi = (item.get("doi", "") or "").replace("https://doi.org/", "")
            url = item.get("doi", "") or ""

            kw_list = [k.get("display_name", "") for k in item.get("keywords", [])]
            if not kw_list:
                kw_list = [
                    c.get("display_name", "")
                    for c in (item.get("concepts") or [])
                    if c.get("score", 0) > 0.3
                ]

            papers.append({
                "title": title,
                "authors": [a for a in authors if a],
                "abstract": abstract,
                "year": year,
                "published_date": pub_date,
                "journal": journal,
                "url": url or (f"https://doi.org/{doi}" if doi else ""),
                "arxiv_id": "",
                "keywords": [k for k in kw_list if k][:8],
                "citations": citations,
                "source": "OpenAlex",
                "doi": doi,
                "open_access": primary.get("is_oa", False),
            })
    except Exception as e:
        print(f"[OpenAlex] {e}")

    return papers


# ==============================================================
# Papers With Code (free, no auth required)
# ==============================================================
def search_paperswithcode(
    query: str,
    max_results: int = 20,
    days_back: int = 90,
) -> list[dict]:
    """
    Papers With Code 公开 API（无需认证）。
    返回带代码仓库链接的论文，补充 arXiv 中有开源实现的工作。
    API: https://paperswithcode.com/api/v1/papers/?q=<query>
    """
    base_url = "https://paperswithcode.com/api/v1/papers/"
    cutoff_year = datetime.now().year - max(1, days_back // 365)

    try:
        resp = _safe_get(base_url, params={"q": query, "items_per_page": min(max_results, 50)})
        if not resp:
            return []
        data = resp.json()
    except Exception as e:
        logger.debug(f"[PWC] {e}")
        return []

    papers = []
    for item in data.get("results", [])[:max_results]:
        title = (item.get("title") or "").strip()
        if not title:
            continue

        pub_date = item.get("published") or ""
        year_str = pub_date[:4] if pub_date else ""
        year = int(year_str) if year_str.isdigit() else 0
        if year and year < cutoff_year:
            continue

        arxiv_id = item.get("arxiv_id") or ""
        url = (
            f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id
            else item.get("url_abs") or item.get("url_pdf") or ""
        )

        # 代码仓库
        repo_url = ""
        repo_stars = 0
        repos = item.get("repositories") or []
        if repos:
            # 取 star 最多的那个
            best = max(repos, key=lambda r: r.get("stars") or 0, default={})
            repo_url   = best.get("url") or ""
            repo_stars = best.get("stars") or 0

        authors = item.get("authors") or []
        if isinstance(authors, list) and authors and isinstance(authors[0], dict):
            authors = [a.get("full_name", "") for a in authors]

        papers.append({
            "title":          title,
            "authors":        [a for a in authors if a],
            "abstract":       item.get("abstract") or "",
            "year":           year or datetime.now().year,
            "published_date": pub_date[:10] if pub_date else "",
            "journal":        "Papers With Code",
            "url":            url,
            "arxiv_id":       arxiv_id,
            "keywords":       [],
            "citations":      0,
            "source":         "paperswithcode",
            "doi":            "",
            "_extra": {
                "repo_url":   repo_url,
                "repo_stars": repo_stars,
                "pwc_url":    item.get("url_abs") or "",
            },
        })

    return papers


# ==============================================================
# CORE (requires free API key)
# ==============================================================
def search_core(query: str, max_results: int = 30, years_back: int = 5,
                api_key: str = "") -> list[dict]:
    if not api_key:
        return []

    base_url = "https://api.core.ac.uk/v3/search/works"
    year_start = datetime.now().year - years_back

    headers = {"Authorization": f"Bearer {api_key}"}
    params = {
        "q": f"{query} AND yearPublished>={year_start}",
        "limit": min(max_results, 100),
        "sort": "relevance",
    }

    resp = _safe_get(base_url, params=params, headers=headers)
    if not resp:
        return []

    papers = []
    try:
        data = resp.json()
        for item in data.get("results", []):
            title = item.get("title", "") or ""
            if not title:
                continue

            authors = [a.get("name", "") for a in item.get("authors", [])]
            year = str(item.get("yearPublished", ""))
            doi = item.get("doi", "") or ""
            url = item.get("downloadUrl", "") or item.get("sourceFulltextUrls", [""])[0]
            journals = item.get("journals", [])
            journal = journals[0].get("title", "CORE") if journals else "CORE"

            papers.append({
                "title": title,
                "authors": [a for a in authors if a],
                "abstract": item.get("abstract", "") or "",
                "year": year,
                "published_date": year,
                "journal": journal,
                "url": url,
                "arxiv_id": "",
                "keywords": [],
                "citations": 0,
                "source": "CORE",
                "doi": doi,
            })
    except Exception as e:
        print(f"[CORE] {e}")

    return papers


# ==============================================================
# Scopus  (Elsevier API)
# API Key 鍏嶈垂娉ㄥ唽: https://dev.elsevier.com
# 姣忎釜 API Key 姣忓懆 5 000 娆℃煡璇紝姣忔鏈€澶氳繑鍥?200 鏉?# 娉ㄦ剰: 鏃犳満鏋?Token 浠呰兘鑾峰彇鍏冩暟鎹?鏍囬/浣滆€?鎽樿/寮曠敤鏁?锛?#       鍏ㄦ枃閾炬帴闇€閫氳繃 DOI 鎴?Unpaywall 鑾峰彇
# ==============================================================

def search_scopus(
    query: str,
    max_results: int = 50,
    years_back: int = 5,
    api_key: str = "",
    inst_token: str = "",           # 鏈烘瀯 Token锛堝彲閫夛紝鎷ユ湁鑰呭彲浠ヨ闂洿澶氬瓧娈碉級
    sort: str = "citedby-count",    # citedby-count | relevance | pubyear
) -> list[dict]:
    """
    閫氳繃 Scopus Search API 妫€绱㈣鏂囧厓鏁版嵁銆?
    鍙傛暟:
        query      鈥?妫€绱㈠叧閿瘝锛屾敮鎸佽嚜鐒惰瑷€锛堜腑鑻辨枃鍧囧彲锛?        max_results鈥?鏈€澶ц繑鍥炶鏂囨暟锛堜笂闄?200锛屽缓璁?鈮?50锛?        years_back 鈥?妫€绱㈣繎 N 骞?        api_key    鈥?Elsevier API Key锛堝湪 dev.elsevier.com 鍏嶈垂娉ㄥ唽鑾峰彇锛?        inst_token 鈥?鏈烘瀯 Token锛堥€夊～锛屾棤鍒欎粎杩斿洖鍏紑鍏冩暟鎹級
        sort       鈥?鎺掑簭鏂瑰紡锛歝itedby-count / relevance / pubyear
    """
    if not api_key:
        return []

    BASE_URL = "https://api.elsevier.com/content/search/scopus"
    year_from = datetime.now().year - years_back

    # Scopus 楂樼骇鏌ヨ璇硶
    # TITLE-ABS-KEY 鍚屾椂妫€绱㈡爣棰樸€佹憳瑕併€佸叧閿瘝
    # 娉ㄦ剰锛氫笉鍔犲紩鍙?鈫?鍏抽敭璇嶅尮閰嶏紙缁撴灉涓板瘜锛夛紱鍔犲紩鍙?鈫?涓ユ牸鐭鍖归厤锛堢粨鏋滄瀬灏戯級
    # 澶氫釜璇嶇敤绌烘牸鍒嗛殧锛孲copus 鑷姩鎸?AND 閫昏緫澶勭悊
    _q_clean = query.strip().replace('"', '')   # Remove literal quotes from user input.
    if " " in _q_clean:
        scopus_term = f'"{_q_clean}"'
    else:
        scopus_term = _q_clean
    scopus_query = f"TITLE-ABS-KEY({scopus_term}) AND PUBYEAR > {year_from}"

    headers = {
        "Accept": "application/json",
        "X-ELS-APIKey": api_key,
    }
    if inst_token:
        headers["X-ELS-Insttoken"] = inst_token

    # 娉ㄦ剰锛氫笉浼?field 鍙傛暟锛岃 Scopus 杩斿洖榛樿瀛楁闆嗗悎
    # 浼犲叆 field 鍙傛暟鍚?dc:description/authkeywords 浼氬鑷村厤璐?key 杩斿洖 error entry
    params = {
        "query":  scopus_query,
        "count":  min(max_results, 200),
        "start":  0,
        "sort":   sort,
        # 涓嶅姞 field 鍙傛暟 鈫?鑾峰彇鍏ㄩ儴榛樿鍙敤瀛楁
    }

    resp = _safe_get(BASE_URL, params=params, headers=headers, timeout=30)
    if not resp:
        logger.warning(
            "[Scopus] 请求失败（已重试4次）。可能原因："
            "  1. 网络连接问题（检查代理/VPN/防火墙）"
            "  2. API Key 无效或已过期（登录 dev.elsevier.com 检查）"
            "  3. Scopus API 服务暂时不可用"
            "  查询: %s", scopus_query,
        )

    papers: list[dict] = []
    try:
        data = resp.json()
        entries = data.get("search-results", {}).get("entry", [])

        # 澶勭悊 API 閿欒鍝嶅簲
        if not entries:
            err = data.get("search-results", {}).get("error", "")
            if err:
                logger.warning("[Scopus] API error: %s", err)
            return []

        for item in entries:
            if "error" in item and "dc:title" not in item:
                continue

            title = (item.get("dc:title") or "").strip()
            if not title:
                continue

            # 鈹€鈹€ 浣滆€?鈹€鈹€
            # Search API 鍙繑鍥炵涓€浣滆€咃紙dc:creator锛夛紱Abstract API 鎵嶆湁瀹屾暣鍒楄〃
            first_author = item.get("dc:creator", "") or ""
            authors = [first_author] if first_author else []

            # 鈹€鈹€ 鏈熷垔/鏉ユ簮 鈹€鈹€
            journal = item.get("prism:publicationName", "") or ""

            # 鈹€鈹€ 鍙戣〃鏃ユ湡 鈹€鈹€
            cover_date = item.get("prism:coverDate", "") or ""
            year = cover_date[:4] if cover_date else ""

            doi = item.get("prism:doi", "") or ""
            eid = item.get("eid", "")
            scopus_url = item.get("prism:url", "") or ""
            if doi:
                url = f"https://doi.org/{doi}"
            elif eid:
                url = f"https://www.scopus.com/record/display.uri?eid={eid}&origin=inward"
            elif scopus_url:
                url = scopus_url
            else:
                url = ""

            # 鈹€鈹€ 寮曠敤鏁?鈹€鈹€
            try:
                citations = int(item.get("citedby-count", 0) or 0)
            except (ValueError, TypeError):
                citations = 0

            # 鈹€鈹€ 鎽樿 鈹€鈹€
            # 鍏嶈垂 API Key 鎼滅储鎺ュ彛涓嶈繑鍥炴憳瑕侊紱鏈烘瀯 Token 鍙€氳繃 Abstract API 鑾峰彇
            abstract = (item.get("dc:description") or "").strip()

            # 鈹€鈹€ 鍏抽敭璇?鈹€鈹€
            kw_raw = item.get("authkeywords") or ""
            keywords = [k.strip() for k in kw_raw.split("|") if k.strip()]

            # 鈹€鈹€ 鍗峰彿/椤电爜 鈹€鈹€
            volume = item.get("prism:volume", "") or ""
            pages  = item.get("prism:pageRange", "") or ""

            # 鈹€鈹€ 璁烘枃绫诲瀷 鈹€鈹€
            doc_type = item.get("subtypeDescription", "") or item.get("subtype", "")

            papers.append({
                "title":          title,
                "authors":        authors,
                "abstract":       abstract,
                "year":           year,
                "published_date": cover_date,
                "journal":        journal,
                "volume":         volume,
                "pages":          pages,
                "url":            url,
                "doi":            doi,
                "keywords":       keywords,
                "citations":      citations,
                "source":         "Scopus",
                "arxiv_id":       "",
                "eid":            eid,
                "scopus_id":      (item.get("dc:identifier", "") or "").replace("SCOPUS_ID:", ""),
                "pii":            item.get("pii", "") or "",
            })

    except Exception as e:
        logger.warning("[Scopus] Failed to parse response: %s", e)

    logger.info("[Scopus] Found %d papers", len(papers))
    return papers


def _unique_query_variants(query: str, translated_query: str = "") -> list[str]:
    variants: list[str] = []
    for candidate in (query, translated_query):
        candidate = (candidate or "").strip()
        if candidate and candidate not in variants:
            variants.append(candidate)

    if translated_query:
        normalized = translated_query.replace('"', "").strip()
        if normalized and normalized not in variants:
            variants.append(normalized)

        if translated_query.lower() == "digital humanities":
            for alias in ("humanities computing", "digital scholarship humanities"):
                if alias not in variants:
                    variants.append(alias)

    return variants


def _search_scopus_resilient(
    query: str,
    max_results: int,
    years_back: int,
    cfg: dict,
) -> list[dict]:
    """Best-effort Scopus search with multiple query variants and a class fallback."""
    api_key = cfg.get("scopus_api_key", "")
    if not api_key:
        return []

    query_cn, query_en = _translate_query(query)
    translated_query = query_en if query_en and query_en != query_cn else ""
    variants = _unique_query_variants(query, translated_query)

    collected: list[dict] = []
    seen_titles: set[str] = set()

    def _append(results: list[dict]):
        for paper in results or []:
            key = _title_key(paper.get("title", ""))
            if key and key not in seen_titles:
                seen_titles.add(key)
                collected.append(paper)

    for variant in variants[:4]:
        try:
            results = search_scopus(
                variant,
                max_results=max_results,
                years_back=years_back,
                api_key=api_key,
                inst_token=cfg.get("scopus_inst_token", ""),
                sort=cfg.get("scopus_sort", "citedby-count"),
            )
            _append(results)
            if collected:
                logger.info(
                    "[ScopusFallback] search_scopus succeeded for '%s': %d papers",
                    variant,
                    len(results),
                )
                break
        except Exception as e:
            logger.warning("[ScopusFallback] search_scopus failed for '%s': %s", variant, e)

    if not collected:
        try:
            from modules.chinese_searcher import ScopusSearcher

            fallback = ScopusSearcher(api_key=api_key)
            for variant in variants[:4]:
                try:
                    results = fallback.search(
                        variant,
                        max_results=min(max_results, 25),
                        years_back=years_back,
                        sort_by=cfg.get("scopus_sort", "citedby-count"),
                    )
                    _append(results)
                    if collected:
                        logger.info(
                            "[ScopusFallback] ChineseSearcher fallback succeeded for '%s': %d papers",
                            variant,
                            len(results),
                        )
                        break
                except Exception as e:
                    logger.warning(
                        "[ScopusFallback] ChineseSearcher fallback failed for '%s': %s",
                        variant,
                        e,
                    )
        except Exception as e:
            logger.warning("[ScopusFallback] Could not initialize ScopusSearcher fallback: %s", e)

    return deduplicate(collected)


# ==============================================================
# Deduplication
# ==============================================================
def _title_key(title: str) -> str:
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]", "", title.lower())[:80]


def deduplicate(papers: list[dict]) -> list[dict]:
    seen_title: dict[str, dict] = {}
    seen_doi: dict[str, str] = {}   # doi -> title_key
    for p in papers:
        title_key = _title_key(p.get("title", ""))
        if not title_key:
            continue

        doi = (p.get("doi") or "").strip().lower()

        # DOI 鍘婚噸锛氬鏋?DOI 宸插瓨鍦紝鏄犲皠鍒板悓涓€涓?title_key
        if doi and doi in seen_doi:
            title_key = seen_doi[doi]
        elif doi:
            seen_doi[doi] = title_key

        if title_key not in seen_title:
            seen_title[title_key] = p
        else:
            # 淇濈暀寮曠敤鏇村鐨勯偅鏉?            if (p.get("citations", 0) or 0) > (seen_title[title_key].get("citations", 0) or 0):
                seen_title[title_key] = p
    return list(seen_title.values())


# ==============================================================
# Main aggregator with bilingual support
# ==============================================================
def search_all(
    query: str,
    max_results_per_source: int = 30,
    years_back: int = 5,
    sources: list[str] = None,
    extra_config: dict = None,
) -> list[dict]:
    """
    Aggregated search across all online sources with automatic
    Chinese-to-English translation for better accuracy.

    When user inputs Chinese (e.g. "鍗氬紙璁?), the system will:
    1. Translate to English ("game theory") for English-only APIs
    2. Search OpenAlex with BOTH Chinese and English queries
    3. Filter results for relevance
    4. Deduplicate and sort
    """
    cfg = _merge_search_config(extra_config)

    if sources is None:
        cfg_check = cfg
        sources = ["arxiv", "semantic_scholar", "crossref", "pubmed", "openalex", "paperswithcode"]
        if cfg_check.get("scopus_api_key"):          # 鏈?Scopus key 鑷姩鍔犲叆
            sources.append("scopus")
    all_papers: list[dict] = []

    # --- Bilingual query resolution ---
    query_cn, query_en = _translate_query(query)
    # query_cn is None if the input was already English
    # query_en is the English version (or original if already English)
    has_translated_english = bool(
        query_en and (not query_cn or query_en.strip().lower() != query_cn.strip().lower())
    )
    # 修复：即使没有翻译，只要 query_en 有内容就允许英文源搜索
    # 原逻辑：中文词未找到翻译 → english_only_query="" → arXiv/SS/PubMed 全跳过
    # 新逻辑：未翻译时直接用原词搜索（英文 API 能处理部分拼音/英文混合词）
    english_only_query = query_en if query_en else ""

    print(f"[Search] Original: '{query}'")
    if query_cn:
        print(f"[Search] Chinese: '{query_cn}' -> English: '{query_en}'"
              + ("" if has_translated_english else " [未找到翻译，使用原词]"))
    else:
        print(f"[Search] English query: '{query_en}'")

    # --- Search each source ---
    # English-only APIs: use English query
    if "arxiv" in sources and english_only_query:
        results = search_arxiv(english_only_query, max_results_per_source, years_back)
        all_papers.extend(results)
        time.sleep(0.5)

    if "semantic_scholar" in sources and english_only_query:
        results = search_semantic_scholar(english_only_query, max_results_per_source, years_back)
        all_papers.extend(results)
        time.sleep(0.5)

    if "crossref" in sources:
        crossref_queries = []
        if english_only_query:
            crossref_queries.append(english_only_query)
        if query_cn and query_cn not in crossref_queries:
            crossref_queries.append(query_cn)
        if not crossref_queries and query_en:
            crossref_queries.append(query_en)
        for crossref_query in crossref_queries:
            results = search_crossref(crossref_query, max_results_per_source, years_back)
            all_papers.extend(results)
            time.sleep(0.3)

    if "pubmed" in sources and english_only_query:
        results = search_pubmed(english_only_query, max_results_per_source, years_back)
        all_papers.extend(results)
        time.sleep(0.3)

    # OpenAlex: search BOTH Chinese and English for maximum coverage
    if "openalex" in sources:
        email = cfg.get("openalex_email", "")
        openalex_queries = []
        if english_only_query:
            openalex_queries.append(english_only_query)
        if query_cn and query_cn not in openalex_queries:
            openalex_queries.append(query_cn)
        if not openalex_queries and query_en:
            openalex_queries.append(query_en)
        for openalex_query in openalex_queries:
            results = search_openalex(
                openalex_query, max_results_per_source, years_back, email=email
            )
            all_papers.extend(results)
            time.sleep(0.3)

    if "paperswithcode" in sources and english_only_query:
        results = search_paperswithcode(
            english_only_query,
            max_results=min(max_results_per_source, 20),
            days_back=years_back * 365,
        )
        all_papers.extend(results)
        time.sleep(0.3)

    if "core" in sources and cfg.get("core_api_key") and english_only_query:
        results = search_core(
            english_only_query, max_results_per_source, years_back,
            api_key=cfg.get("core_api_key", "")
        )
        all_papers.extend(results)

    if "scopus" in sources and cfg.get("scopus_api_key") and english_only_query:
        results = _search_scopus_resilient(
            english_only_query,
            max_results=max_results_per_source,
            years_back=years_back,
            cfg=cfg,
        )
        all_papers.extend(results)
        time.sleep(0.5)

    # --- Relevance filtering ---
    if query_cn or " " in query_en:
        before_count = len(all_papers)
        all_papers = [
            p for p in all_papers
            if _check_relevance(p, query_cn or "", query_en)
        ]
        filtered = before_count - len(all_papers)
        if filtered > 0:
            print(f"[Search] Relevance filter: removed {filtered} unrelated papers")

    # --- Deduplicate and sort ---
    unique = deduplicate(all_papers)
    unique.sort(
        key=lambda x: (x.get("citations", 0) or 0),
        reverse=True,
    )

    print(f"[Search] Final: {len(unique)} papers (from {len(all_papers)} before dedup)")
    return unique


def search_full(
    query: str,
    max_results_per_source: int = 20,
    years_back: int = 5,
    config: dict = None,
    search_guidelines=None,
) -> list[dict]:
    """Combined search across English and Chinese sources.

    Args:
        search_guidelines: WritingGuidelines object (from EvolutionTracker).
            If provided, uses learned effective keywords for query expansion
            and preferred_sources for source prioritization.
    """
    cfg = _merge_search_config(config)
    all_papers: list[dict] = []

    # ── 自学习：用历史经验扩展搜索策略 ──────────────────────
    extra_queries = []
    if search_guidelines and getattr(search_guidelines, "based_on_cycles", 0) > 0:
        effective_kw = getattr(search_guidelines, "search_keywords_effective", []) or []
        if effective_kw:
            # 用有效关键词扩展查询：每个关键词与原 query 组合
            for kw in effective_kw[:3]:
                expanded = f"{query} {kw}"
                if expanded.lower() != query.lower():
                    extra_queries.append(expanded)
            logger.info(
                "[search_full] Learned query expansions: %s",
                extra_queries,
            )

        # 用推荐语料量调整 max_results
        rec_size = getattr(search_guidelines, "min_corpus_size_recommendation", 0)
        if rec_size > 0 and max_results_per_source < rec_size:
            old_max = max_results_per_source
            max_results_per_source = min(rec_size, 50)
            logger.info(
                "[search_full] Adjusted max_results_per_source: %d → %d (learned)",
                old_max, max_results_per_source,
            )

    eng_papers = search_all(
        query=query,
        max_results_per_source=max_results_per_source,
        years_back=years_back,
        sources=None,
        extra_config=cfg,
    )
    all_papers.extend(eng_papers)
    logger.info("[search_full] English sources: %d papers", len(eng_papers))

    if cfg.get("scopus_api_key") and not any(
        (paper.get("source") or "").lower() == "scopus" for paper in eng_papers
    ):
        scopus_rescue = _search_scopus_resilient(
            query=query,
            max_results=max_results_per_source,
            years_back=years_back,
            cfg=cfg,
        )
        if scopus_rescue:
            all_papers.extend(scopus_rescue)
            logger.info(
                "[search_full] Scopus rescue added %d papers after primary aggregate miss",
                len(scopus_rescue),
            )
        else:
            logger.warning("[search_full] Scopus rescue failed for query '%s'", query)

    # 用扩展查询补充搜索（仅在主搜索结果不足时）
    if extra_queries and len(eng_papers) < max_results_per_source * 2:
        for eq in extra_queries:
            try:
                extra = search_all(
                    query=eq,
                    max_results_per_source=max(5, max_results_per_source // 3),
                    years_back=years_back,
                    sources=None,
                    extra_config=cfg,
                )
                all_papers.extend(extra)
                logger.info("[search_full] Expansion '%s': %d papers", eq[:30], len(extra))
            except Exception as e:
                logger.warning("[search_full] Expansion query failed: %s", e)

    try:
        from modules.chinese_searcher import ChineseSearchManager
        cn_manager = ChineseSearchManager()

        serp_key = cfg.get("serp_api_key", "")
        scraper_key = cfg.get("scraper_api_key", "")
        scholar_proxy = cfg.get("proxy", "")
        if serp_key:
            cn_manager.google_scholar.set_serp_api_key(serp_key)
        if scraper_key:
            cn_manager.google_scholar.set_scraper_api_key(scraper_key)
        if scholar_proxy:
            cn_manager.google_scholar.set_proxy(scholar_proxy)

        query_cn, query_en = _translate_query(query)
        wf_queries = []
        if query_cn:
            wf_queries.append(query_cn)
        if query and query not in wf_queries:
            wf_queries.append(query)
        if query_en and query_en not in wf_queries:
            wf_queries.append(query_en)

        wf_total = 0
        for wf_query in wf_queries[:2]:
            try:
                wf_papers = cn_manager.wanfang.search(
                    wf_query, max_results=max_results_per_source, years_back=years_back,
                )
                all_papers.extend(wf_papers)
                wf_total += len(wf_papers)
                logger.info("[search_full] Wanfang (%s): %d papers", wf_query[:20], len(wf_papers))
            except Exception as e:
                logger.warning("[search_full] Wanfang error (%s): %s", wf_query[:20], e)

        gs_queries = []
        if query:
            gs_queries.append(query)
        if query_en and query_en not in gs_queries:
            gs_queries.append(query_en)
        if query_cn and query_cn not in gs_queries:
            gs_queries.append(query_cn)

        gs_total = 0
        for gs_query in gs_queries[:2]:
            try:
                gs_papers = cn_manager.google_scholar.search(
                    gs_query, max_results=max_results_per_source, years_back=years_back,
                )
                all_papers.extend(gs_papers)
                gs_total += len(gs_papers)
                logger.info("[search_full] Google Scholar (%s): %d papers", gs_query[:20], len(gs_papers))
            except Exception as e:
                logger.warning("[search_full] Google Scholar error (%s): %s", gs_query[:20], e)

        if not gs_total:
            gs_last_error = getattr(cn_manager.google_scholar, "last_error", "")
            if gs_last_error:
                logger.warning("[search_full] Google Scholar all retries failed: %s", gs_last_error)
    except Exception as e:
        logger.warning("[search_full] Chinese source error: %s", e)

    unique = deduplicate(all_papers)
    unique.sort(key=lambda x: (x.get("citations", 0) or 0), reverse=True)
    logger.info("[search_full] Final: %d papers (before dedup: %d)", len(unique), len(all_papers))
    return unique
