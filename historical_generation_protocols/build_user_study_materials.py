# -*- coding: utf-8 -*-
"""
Build user study materials:
- Sample 10 questions (balanced across 4 domains)
- Extract 3 anonymized versions (M1 naive RAG / M2b same-model ARL / M2a cross-model ARL)
- Each version's order randomly permuted per question
- Output: Word questionnaire + mapping answer key + usage manual
"""
import json, os, random, re, sys, io
from collections import defaultdict
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

if sys.stdout.encoding and sys.stdout.encoding.lower() in ("gbk","cp936","gb2312"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "data", "user_study")
os.makedirs(OUT_DIR, exist_ok=True)

# Fixed seed for reproducibility
random.seed(42)

# ---- Method directory mapping -------------------------------------------
METHODS = {
    "A": ("method1",  "data/expanded_outputs/method1"),   # core CDMA without ARL
    "B": ("method2b", "data/expanded_outputs/method2b"),  # same-model ARL (middle, orphan ~1.0%)
    "C": ("method2a", "data/expanded_outputs/method2a"),  # cross-model ARL (best, orphan ~0.4%)
}

DOMAIN_CN = {
    "multi_agent_information_services": "多智能体情报服务",
    "digital_humanities":                "数字人文",
    "biomedical_evidence_synthesis":     "生物医学证据综合",
    "climate_policy_research":           "气候政策研究",
}

# ---- 1. Build Q_id → (domain, query_text) using method1 json ----
qmeta = {}
m1_jsons = sorted(f for f in os.listdir(os.path.join(ROOT, "data/expanded_outputs/method1")) if f.endswith(".json"))
for f in m1_jsons:
    with open(os.path.join(ROOT, "data/expanded_outputs/method1", f), "r", encoding="utf-8") as fp:
        d = json.load(fp)
    if not isinstance(d, dict) or "query_id" not in d:
        continue
    qid = d["query_id"]
    if qid not in qmeta:
        qmeta[qid] = {"domain": d["domain_id"], "query": d.get("query",""), "fname_base": f.replace(".json","")}

# ---- 2. Sample 10 questions balanced across domains ----
#   MAS:3, DH:3, bio:2, climate:2
per_domain_quota = {
    "multi_agent_information_services": 3,
    "digital_humanities": 3,
    "biomedical_evidence_synthesis": 2,
    "climate_policy_research": 2,
}
by_dom = defaultdict(list)
for qid, m in qmeta.items():
    by_dom[m["domain"]].append(qid)

sampled = []
for dom, n in per_domain_quota.items():
    cands = sorted(by_dom[dom])
    random.shuffle(cands)
    sampled.extend(cands[:n])

# Also shuffle final ordering to avoid domain clustering
random.shuffle(sampled)
print(f"[info] sampled Q IDs (N=10): {sampled}")

# ---- 3. For each Q, load the 3 versions' markdown and extract a ~200-word excerpt ----

def find_md_file(method_dir, qid):
    """Return latest .md file matching Qxx_method*."""
    full = os.path.join(ROOT, method_dir)
    cands = [f for f in os.listdir(full) if f.startswith(qid + "_") and f.endswith(".md")]
    if not cands: return None
    cands.sort()
    return os.path.join(full, cands[-1])

def extract_excerpt(md_text, max_chars=650):
    """
    Extract a clean mid-length excerpt that contains citation markers like [1]..[9].
    Strategy: find the first main body paragraph with at least 2 citation markers,
    take from there up to max_chars characters; if nothing found, fall back to
    first substantial paragraph (>120 chars) ignoring heading lines.
    """
    lines = md_text.split("\n")
    body = []
    for ln in lines:
        s = ln.strip()
        if not s: continue
        if s.startswith("#"): continue   # skip headings
        if s.startswith(">"): continue
        if s.startswith("|"): continue
        body.append(s)
    full = "\n".join(body)
    # Find first window with ≥2 citations
    cite_re = re.compile(r"\[\d+(?:[,\-–]\s*\d+)*\]")
    # find all matches and their positions
    matches = list(cite_re.finditer(full))
    if len(matches) >= 2:
        start = max(0, matches[0].start() - 40)
        end = min(len(full), start + max_chars)
        excerpt = full[start:end]
    else:
        excerpt = full[:max_chars]
    # Clean up
    excerpt = excerpt.strip()
    if not excerpt.endswith(("。","!","?",".","！","？")):
        # cut at last sentence boundary
        for sep in ["。","！","？","."]:
            idx = excerpt.rfind(sep)
            if idx > max_chars * 0.5:
                excerpt = excerpt[:idx+1]
                break
    return excerpt

def extract_references(md_text, max_refs=6):
    """Extract the reference list (last section), up to max_refs items."""
    # Look for lines like [1] xxx or 1. xxx  under '参考文献' heading
    lines = md_text.split("\n")
    refs = []
    in_ref = False
    for ln in lines:
        s = ln.strip()
        if not in_ref:
            if re.search(r"参考文献|References|引用文献", s):
                in_ref = True
            continue
        # Accept lines starting with [N] or N.
        m = re.match(r"^(\[\d+\]|\d+\.)\s*(.+)$", s)
        if m:
            refs.append(s)
        if len(refs) >= max_refs: break
    return refs

# ---- 4. Build question bundles ----
bundles = []
for qid in sampled:
    meta = qmeta[qid]
    versions = {}
    for code, (mname, mdir) in METHODS.items():
        path = find_md_file(mdir, qid)
        if path is None:
            versions[code] = {"excerpt": "[未找到]", "refs": []}
            continue
        with open(path, "r", encoding="utf-8") as fp:
            md = fp.read()
        versions[code] = {
            "method": mname,
            "excerpt": extract_excerpt(md),
            "refs":    extract_references(md),
        }
    # Random permutation: map labels ①②③ → which code
    codes = ["A","B","C"]
    random.shuffle(codes)
    label_map = {"①": codes[0], "②": codes[1], "③": codes[2]}
    bundles.append({
        "qid": qid,
        "domain_cn": DOMAIN_CN.get(meta["domain"], meta["domain"]),
        "query": meta["query"],
        "versions": versions,
        "label_map": label_map,   # e.g. {'①':'C','②':'A','③':'B'}  — for answer key
    })

# ---- 5. Build Word questionnaire ------------------------------------------
doc = Document()

# Page setup
for section in doc.sections:
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2.2)
    section.right_margin = Cm(2.2)

# Default font
style = doc.styles["Normal"]
style.font.name = "宋体"
style.font.size = Pt(10.5)

# Title
t = doc.add_heading("AI 综述片段可信度评估问卷", level=0)
t.alignment = WD_ALIGN_PARAGRAPH.CENTER

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("（研究生用户研究 / 约 25 分钟）")
run.italic = True

# Instructions
doc.add_heading("填写说明", level=1)
instr = [
    "1. 本问卷呈现 10 个研究问题，每题下方有 3 个片段（标记为 ①/②/③），由不同的 AI 系统生成。",
    "2. 您看不到系统名称，片段出现顺序已随机化。",
    "3. 对每一题，请完成三项任务：",
    "   ① 排序：按可信度从高到低给 3 个片段排序（例：③ > ① > ②）。",
    "   ② 挑错：指出哪一个片段的引用最可疑。",
    "   ③ 打分：对每个片段给出 1–7 分（1=完全不可信，7=完全可信）。",
    "4. 判断标准建议：",
    "   · 陈述是否有文献支持？引用是否与上下文语义一致？",
    "   · 参考文献是否真实存在（标题/作者看起来合理）？",
    "   · 内容是否显得空泛、缺乏具体信息？",
    "5. 请凭直觉作答，不需上网核实。若不确定仍请选择，但可在备注栏说明。",
]
for line in instr:
    p = doc.add_paragraph(line)
    p.paragraph_format.space_after = Pt(2)

doc.add_paragraph()

# Basic info
doc.add_heading("被试基本信息", level=1)
info_lines = [
    "姓名（或编号）： ____________________",
    "专业：                ____________________",
    "学位阶段：硕士 □   博士 □   博士后 □",
    "近两年读过的英文论文数：  ＜20 □   20–50 □   50–100 □   ＞100 □",
    "研究领域（可勾选多个）：多智能体 □   数字人文 □   生物医学 □   气候政策 □   其他 □",
]
for line in info_lines:
    doc.add_paragraph(line)

doc.add_page_break()

# --- Questions ---
for i, b in enumerate(bundles, 1):
    doc.add_heading(f"第 {i} 题（领域：{b['domain_cn']}）", level=1)
    p = doc.add_paragraph()
    r = p.add_run("问题：")
    r.bold = True
    p.add_run(b["query"])

    # 3 versions in randomized order
    for label in ["①", "②", "③"]:
        code = b["label_map"][label]
        v = b["versions"][code]
        doc.add_heading(f"片段 {label}", level=2)
        doc.add_paragraph(v["excerpt"])
        if v["refs"]:
            p = doc.add_paragraph()
            r = p.add_run("参考文献：")
            r.italic = True
            r.font.size = Pt(9)
            for ref in v["refs"]:
                rp = doc.add_paragraph(ref)
                rp.paragraph_format.left_indent = Cm(0.6)
                rp.paragraph_format.space_after = Pt(0)
                for run in rp.runs:
                    run.font.size = Pt(9)
                    run.font.color.rgb = RGBColor(0x55,0x55,0x55)

    # Answer area
    doc.add_paragraph()
    p = doc.add_paragraph()
    r = p.add_run("【任务 1】排序（从最可信到最不可信）：")
    r.bold = True
    doc.add_paragraph("答：  ____  >  ____  >  ____")

    p = doc.add_paragraph()
    r = p.add_run("【任务 2】哪一个片段的引用最可疑？")
    r.bold = True
    doc.add_paragraph("答：  □ ①     □ ②     □ ③")

    p = doc.add_paragraph()
    r = p.add_run("【任务 3】打分（1 = 完全不可信，7 = 完全可信）：")
    r.bold = True
    doc.add_paragraph("片段 ①：____     片段 ②：____     片段 ③：____")

    p = doc.add_paragraph()
    r = p.add_run("备注（可选）：")
    r.italic = True
    doc.add_paragraph("_" * 60)

    if i < len(bundles):
        doc.add_page_break()

# Final debriefing
doc.add_page_break()
doc.add_heading("最后几个问题", level=1)
doc.add_paragraph("A. 您在评判时最主要依赖了哪些线索？（可多选）")
for item in ["引用是否与论述对齐","文献标题是否真实","论述是否空泛","专业术语准确度","其他（请注明）"]:
    doc.add_paragraph(f"    □ {item}")

doc.add_paragraph()
doc.add_paragraph("B. 三个系统中，您是否感到有明显质量差异？")
doc.add_paragraph("   □ 差异明显   □ 略有差异   □ 差异不大   □ 几乎看不出来")

doc.add_paragraph()
doc.add_paragraph("C. 其他意见或建议：")
doc.add_paragraph("_" * 60)
doc.add_paragraph("_" * 60)

doc.add_paragraph()
p = doc.add_paragraph("—— 问卷结束，感谢您的参与 ——")
p.alignment = WD_ALIGN_PARAGRAPH.CENTER

out_q = os.path.join(OUT_DIR, "用户研究问卷.docx")
doc.save(out_q)
print(f"[ok] 问卷已生成: {out_q}")

# ---- 6. Answer key (for researcher use only) ------------------------------
keydoc = Document()
keydoc.add_heading("答案映射表（仅研究者使用，不对被试展示）", level=0)
keydoc.add_paragraph("说明：片段 ①②③ 的随机顺序对应的系统如下。A=朴素 RAG（基线，高 orphan）；"
                     "B=同模型 ARL（中间）；C=跨模型 CDMA+ARL（最优）。预期被试排序接近：C > B > A。")

table = keydoc.add_table(rows=1, cols=6)
table.style = "Light Grid Accent 1"
hdr = table.rows[0].cells
for j, col in enumerate(["题号","Q ID","领域","片段 ①","片段 ②","片段 ③"]):
    hdr[j].text = col

code_to_name = {"A":"A 朴素RAG","B":"B 同模型ARL","C":"C 跨模型ARL(预期最优)"}
for i, b in enumerate(bundles, 1):
    row = table.add_row().cells
    row[0].text = str(i)
    row[1].text = b["qid"]
    row[2].text = b["domain_cn"]
    for j, lab in enumerate(["①","②","③"]):
        row[3+j].text = code_to_name[b["label_map"][lab]]

out_k = os.path.join(OUT_DIR, "答案映射_仅研究者.docx")
keydoc.save(out_k)
print(f"[ok] 答案映射已生成: {out_k}")

# ---- 7. Save a JSON record for later scoring -------------------------------
rec = {
    "seed": 42,
    "sampled_qids": sampled,
    "bundles": [
        {
            "qid": b["qid"],
            "domain": b["domain_cn"],
            "query": b["query"],
            "label_to_system": b["label_map"],  # ①/②/③ → A/B/C
        } for b in bundles
    ],
    "system_legend": {
        "A": "naive_RAG_M1  (expected worst)",
        "B": "same_model_ARL_M2b (middle)",
        "C": "cross_model_CDMA_ARL_M2a (expected best)",
    },
}
with open(os.path.join(OUT_DIR, "answer_key.json"), "w", encoding="utf-8") as fp:
    json.dump(rec, fp, ensure_ascii=False, indent=2)
print(f"[ok] answer_key.json 已保存")
print("[done] 全部材料输出到", OUT_DIR)
