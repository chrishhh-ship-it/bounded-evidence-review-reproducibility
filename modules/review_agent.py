"""
对抗式审稿Agent (Review Agent)
灵感: ARIS双模型对抗 — "Claude执行，GPT审稿，互不评自己的作业"

对生成的论文进行严格的学术审稿：
- 分数(1-10) + 弱点清单 + 修改建议
- AI写作痕迹检测 (De-AI Check)
- Claims-Evidence验证
- 审稿模型必须与写作模型不同
"""
import json
import logging
import os
import re
from dataclasses import dataclass, field, asdict
from typing import Optional

from modules.text_metrics import analyze_text_length, describe_text_length, estimate_pages

logger = logging.getLogger(__name__)

# AI写作痕迹词库
AI_ISMS = {
    'en': [
        'delve', 'pivotal', 'landscape', 'tapestry', 'underscore',
        'noteworthy', 'intriguingly', 'groundbreaking', 'revolutionary',
        'paradigm shift', 'cutting-edge', 'state-of-the-art',
        'it is worth noting', 'importantly,', 'notably,',
        'in this section, we', 'the rest of this paper',
        'in conclusion,', 'to summarize,',
    ],
    'cn': [
        '值得注意的是', '具有里程碑意义', '具有重要意义',
        '不言而喻', '毋庸置疑', '至关重要',
        '本文接下来', '综上所述', '由此可见',
        '令人瞩目', '引人注目', '不可忽视',
        '在本节中，我们', '如前所述',
    ],
}

# 意义膨胀词（应替换为更审慎的表达）
INFLATION_WORDS = {
    'groundbreaking': 'notable',
    'revolutionary': 'significant',
    'paradigm shift': 'methodological advance',
    'cutting-edge': 'recent',
    '令人瞩目': '值得关注',
    '具有里程碑意义': '具有一定意义',
    '不言而喻': '显而易见',
}


@dataclass
class SectionReview:
    """单章节审稿结果"""
    section_name: str
    score: float = 0.0
    issues: list = field(default_factory=list)
    suggestions: list = field(default_factory=list)
    ai_isms_found: list = field(default_factory=list)


@dataclass
class ReviewReport:
    """完整审稿报告"""
    overall_score: float = 0.0                # 1-10
    verdict: str = "NOT_READY"                # READY / ALMOST / NOT_READY
    strengths: list = field(default_factory=list)
    weaknesses: list = field(default_factory=list)      # [{issue, severity, suggested_fix}]
    claims_evidence_check: list = field(default_factory=list)  # [{claim, has_evidence, evidence_location}]
    writing_quality: dict = field(default_factory=dict)
    actionable_fixes: list = field(default_factory=list)  # [{priority, what_to_fix, how_to_fix}]
    section_reviews: list = field(default_factory=list)
    raw_review_text: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def to_markdown(self) -> str:
        score_bar = "█" * int(self.overall_score) + "░" * (10 - int(self.overall_score))
        verdict_emoji = {"READY": "✅", "ALMOST": "🟡", "NOT_READY": "🔴"}.get(self.verdict, "❓")

        md = f"# 审稿报告\n\n"
        md += f"**总分**: {self.overall_score:.1f}/10 [{score_bar}]\n"
        md += f"**判定**: {verdict_emoji} {self.verdict}\n\n"

        if self.strengths:
            md += "## 优点\n"
            for s in self.strengths:
                md += f"- {s}\n"
            md += "\n"

        if self.weaknesses:
            md += "## 问题\n"
            for w in self.weaknesses:
                severity = w.get('severity', 'MINOR')
                emoji = {"CRITICAL": "🔴", "MAJOR": "🟠", "MINOR": "🟡"}.get(severity, "⚪")
                md += f"{emoji} **[{severity}]** {w.get('issue', '')}\n"
                if w.get('suggested_fix'):
                    md += f"   → 建议: {w['suggested_fix']}\n"
            md += "\n"

        if self.actionable_fixes:
            md += "## 可执行修改清单\n"
            for i, fix in enumerate(self.actionable_fixes, 1):
                md += f"{i}. **[{fix.get('priority', 'P2')}]** {fix.get('what_to_fix', '')}\n"
                md += f"   如何修改: {fix.get('how_to_fix', '')}\n"
            md += "\n"

        wq = self.writing_quality
        if wq:
            md += "## 写作质量\n"
            ai_count = len(wq.get('ai_isms_found', []))
            md += f"- AI痕迹词: {ai_count}个\n"
            md += f"- 结构评分: {wq.get('structure_score', 'N/A')}\n"
            md += f"- 清晰度: {wq.get('clarity_score', 'N/A')}\n"
            if wq.get('ai_isms_found'):
                md += f"- 检测到: {', '.join(wq['ai_isms_found'][:10])}\n"

        return md


class ReviewAgent:
    """对抗式审稿Agent"""

    def __init__(self, router=None, user_id: int = 0):
        self.router = router
        self.user_id = user_id

    def review_paper(
        self,
        latex_content: str,
        bib_content: str = "",
        direction=None,
        review_model: str = None,
        review_criteria: str = "",
        evidence_context: str = "",
    ) -> ReviewReport:
        """
        对完整论文进行审稿。

        Args:
            latex_content: LaTeX论文内容
            bib_content: BibTeX引用内容
            direction: ResearchDirection对象（可选）
            review_model: 指定审稿模型（默认auto）

        Returns:
            ReviewReport
        """
        report = ReviewReport()

        # Step 1: 静态检查（不需要LLM）
        static_issues = self._static_check(latex_content, bib_content)
        report.writing_quality = static_issues

        # Step 2: AI写作痕迹检测
        ai_isms = self._detect_ai_isms(latex_content)
        report.writing_quality['ai_isms_found'] = ai_isms

        # Step 3: LLM深度审稿
        if self.router:
            llm_review = self._llm_review(
                latex_content,
                bib_content,
                direction,
                review_criteria=review_criteria,
                evidence_context=evidence_context,
            )
            if llm_review:
                report.overall_score = llm_review.get('overall_score', 5.0)
                report.verdict = llm_review.get('verdict', 'NOT_READY')
                report.strengths = llm_review.get('strengths', [])
                report.weaknesses = llm_review.get('weaknesses', [])
                report.actionable_fixes = llm_review.get('actionable_fixes', [])
                report.claims_evidence_check = llm_review.get('claims_evidence_check', [])
                report.raw_review_text = llm_review.get('raw_text', '')
        else:
            # 无LLM时用静态分析打分
            report = self._static_scoring(report, static_issues, ai_isms)

        # 将静态问题补充到weaknesses
        for failure in static_issues.get('hard_failures', []):
            report.weaknesses.append({
                'issue': failure,
                'severity': 'CRITICAL',
                'suggested_fix': 'Resolve this blocking issue before treating the draft as submission-ready.',
            })

        for issue in static_issues.get('structural_issues', []):
            report.weaknesses.append({
                'issue': issue,
                'severity': self._classify_structural_issue(issue),
                'suggested_fix': '',
            })

        if static_issues.get('hard_failures'):
            report.overall_score = min(report.overall_score or 5.0, 4.9)

        # 根据分数设置verdict
        if report.overall_score >= 7.0:
            report.verdict = "READY"
        elif report.overall_score >= 5.5:
            report.verdict = "ALMOST"
        else:
            report.verdict = "NOT_READY"

        return report

    def review_section(
        self, section_name: str, section_content: str, context: str = ""
    ) -> SectionReview:
        """审稿单个章节。"""
        review = SectionReview(section_name=section_name)

        # AI痕迹
        review.ai_isms_found = self._detect_ai_isms(section_content)

        if self.router:
            prompt = f"""请对以下学术论文的「{section_name}」章节进行审稿。

{f'论文上下文: {context[:500]}' if context else ''}

## 章节内容:
{section_content[:3000]}

请以JSON格式输出:
{{
  "score": 1-10,
  "issues": ["问题1", "问题2"],
  "suggestions": ["建议1", "建议2"]
}}"""
            try:
                content, _, _ = self.router.call(
                    'critic',
                    [{'role': 'user', 'content': prompt}],
                    max_tokens=1500,
                    budget='fast',
                    temperature=0.3,
                )
                result = self._parse_json(content)
                review.score = float(result.get('score', 5.0))
                review.issues = result.get('issues', [])
                review.suggestions = result.get('suggestions', [])
            except Exception as e:
                logger.error(f"章节审稿失败: {e}")
                review.score = 5.0

        return review

    # ============ 静态检查 ============

    def _static_check(self, manuscript: str, bib: str) -> dict:
        """不依赖 LLM 的静态质量检查。同时支持 LaTeX 和 Markdown 格式稿件。"""
        result = {
            'structural_issues': [],
            'hard_failures': [],
            'structure_score': 'N/A',
            'clarity_score': 'N/A',
        }

        # ── 自动检测格式：LaTeX vs Markdown ──────────────────
        is_latex = bool(re.search(r'\\(?:section|begin|end|cite)\b', manuscript))

        # ── 1. 章节结构检测 ──────────────────────────────────
        is_chinese = bool(re.search(r'[\u4e00-\u9fff]', manuscript))
        if is_chinese:
            # 每组中任一匹配即视为存在
            required_sections = [
                ('引言', '导言', 'introduction'),
                ('文献', '相关工作', 'related work', 'literature'),
                ('方法', 'method'),
                ('结论', 'conclusion'),
            ]
        else:
            required_sections = [
                ('introduction',),
                ('literature', 'related work'),
                ('method',),
                ('conclusion',),
            ]

        if is_latex:
            found_sections = re.findall(r'\\section\{(.+?)\}', manuscript, re.IGNORECASE)
        else:
            # Markdown: 匹配 ## 或 ### 开头的标题行
            found_sections = re.findall(r'^#{1,3}\s+(?:\d+\.?\s*)?(.+)', manuscript, re.MULTILINE)
        found_lower = [s.strip().lower() for s in found_sections]

        missing = []
        for aliases in required_sections:
            if not any(alias in sec for alias in aliases for sec in found_lower):
                missing.append(aliases[0])
        if missing:
            issue = f"Missing required sections: {', '.join(missing)}"
            result['structural_issues'].append(issue)
            result['hard_failures'].append(issue)

        # ── 2. 引用完整性检查 ────────────────────────────────
        if is_latex:
            cite_keys = set()
            for ck in re.findall(r'\\cite[pt]?\{([^}]+)\}', manuscript):
                for key in ck.split(','):
                    cite_keys.add(key.strip())
            bib_keys = set(re.findall(r'@\w+\{(\w+)', bib))
            orphan_cites = cite_keys - bib_keys
            if orphan_cites:
                issue = f"Orphan citations (in text but not in bib): {', '.join(list(orphan_cites)[:5])}"
                result['structural_issues'].append(issue)
                result['hard_failures'].append(issue)
        else:
            # Markdown: 统计 [Key] 或 Author(Year) 引用
            bracket_cites = re.findall(r'\[([A-Z][A-Za-z0-9]+\d{4}[a-z]?)\]', manuscript)
            author_year_cites = re.findall(
                r'\b[A-Z][a-z]+(?:\s+et\s+al\.)?\s*\(\d{4}[a-z]?\)', manuscript
            )
            total_cites = len(bracket_cites) + len(author_year_cites)
            result['detected_citations'] = total_cites
            if total_cites == 0:
                result['structural_issues'].append(
                    "No citations detected in Markdown manuscript."
                )

        # ── 3. LaTeX 环境匹配（仅 LaTeX 格式）───────────────
        if is_latex:
            begin_count = len(re.findall(r'\\begin\{', manuscript))
            end_count = len(re.findall(r'\\end\{', manuscript))
            if begin_count != end_count:
                issue = f"LaTeX environment mismatch: {begin_count} begin vs {end_count} end"
                result['structural_issues'].append(issue)
                result['hard_failures'].append(issue)

        # ── 4. 字数检查 ─────────────────────────────────────
        metrics = analyze_text_length(manuscript)
        result['word_count'] = describe_text_length(manuscript)
        result['length_metrics'] = metrics
        # 原创论文最低 3000 词等效；综述/长文用 4500
        min_words = 3000 if not is_latex else 4500
        if metrics['word_equivalent'] < min_words:
            issue = (
                f"Manuscript too short: {metrics['word_equivalent']} word-equivalent "
                f"(minimum {min_words})."
            )
            result['structural_issues'].append(issue)
            result['hard_failures'].append(issue)

        # ── 5. 引用密度 ─────────────────────────────────────
        if is_latex:
            cite_count = len(re.findall(r'\\cite', manuscript))
        else:
            cite_count = (len(bracket_cites) + len(author_year_cites)
                          if not is_latex else 0)
        pages_est = estimate_pages(manuscript)
        if pages_est > 0:
            cite_density = cite_count / pages_est
            result['citation_density'] = round(cite_density, 2)
            if cite_density < 1.5:
                result['structural_issues'].append(
                    f"Citation density is low: {cite_density:.1f} per estimated page."
                )

        # ── 6. Prompt 残留检测 ───────────────────────────────
        prompt_residue_patterns = [
            r'the following is the',
            r'elaborate on the research methodology',
            r'output in json',
            r'请按以下json',
            r'以下是.*章节',
            r'write\s+the\s+\w+\s+section',
        ]
        text_lower = manuscript.lower()
        if any(re.search(pat, text_lower) for pat in prompt_residue_patterns):
            issue = "Prompt residue or template instructions leaked into manuscript text."
            result['structural_issues'].append(issue)
            result['hard_failures'].append(issue)

        # ── 7. 幽灵引用检测（Unknown* / 无效 BibTeX 键）────
        ghost_cites = re.findall(r'\[Unknown\d{4}[a-z]?\]', manuscript)
        if ghost_cites:
            issue = f"Ghost citations with placeholder keys: {', '.join(ghost_cites[:5])}"
            result['structural_issues'].append(issue)

        # ── 评分 ────────────────────────────────────────────
        issues_count = len(result['structural_issues'])
        if issues_count == 0:
            result['structure_score'] = 'Good'
        elif issues_count <= 2:
            result['structure_score'] = 'Fair'
        else:
            result['structure_score'] = 'Poor'

        return result

    def _classify_structural_issue(self, issue: str) -> str:
        issue_lower = issue.lower()
        if any(token in issue_lower for token in ('too short', 'orphan', 'missing required', 'prompt residue', 'mismatch')):
            return 'MAJOR'
        if 'citation density' in issue_lower:
            return 'MAJOR'
        return 'MINOR'

    def _detect_ai_isms(self, text: str) -> list:
        """检测AI写作痕迹词。"""
        found = []
        text_lower = text.lower()

        for lang_isms in AI_ISMS.values():
            for ism in lang_isms:
                if ism.lower() in text_lower:
                    # 计算出现次数
                    count = text_lower.count(ism.lower())
                    found.append(f"{ism} (x{count})")

        # 检查连续段落以相同词开头
        paragraphs = re.split(r'\n\s*\n', text)
        consecutive_this = 0
        consecutive_we = 0
        for para in paragraphs:
            para = para.strip()
            if para.lower().startswith('this ') or para.startswith('本文'):
                consecutive_this += 1
            else:
                if consecutive_this >= 3:
                    found.append(f'连续{consecutive_this}段以"This/本文"开头')
                consecutive_this = 0

            if para.lower().startswith('we ') or para.startswith('我们'):
                consecutive_we += 1
            else:
                if consecutive_we >= 3:
                    found.append(f'连续{consecutive_we}段以"We/我们"开头')
                consecutive_we = 0

        return found

    # ============ LLM深度审稿 ============

    def _llm_review(
        self,
        latex: str,
        bib: str,
        direction=None,
        review_criteria: str = "",
        evidence_context: str = "",
    ) -> dict:
        """用LLM进行深度审稿。"""
        # 提取纯文本（去LaTeX命令）
        clean_text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', latex)
        clean_text = re.sub(r'\\[a-zA-Z]+', '', clean_text)
        clean_text = clean_text[:8000]  # 截断

        direction_ctx = ""
        if direction:
            direction_ctx = f"""
## 研究方向
标题: {getattr(direction, 'title', '')}
创新点: {getattr(direction, 'innovation_point', '')}
"""

        criteria_ctx = self._load_review_criteria_context(review_criteria)
        evidence_block = ""
        if evidence_context:
            evidence_block = f"""
## 本地构念证据摘要
{evidence_context[:5000]}
"""

        reviewer_role = criteria_ctx.get("reviewer_role", "一位严格的学术审稿人（对标NeurIPS/ICML/CSSCI级别）")
        criteria_block = criteria_ctx.get("prompt_block", "")

        prompt = f"""你是{reviewer_role}。
请对以下论文进行全面审稿。

{direction_ctx}

{criteria_block}

{evidence_block}

## 论文内容（摘录）:
{clean_text}

## 引用数量: {len(re.findall(r'@article|@inproceedings|@book', bib))} 篇

## 请严格按以下JSON格式输出审稿意见:
{{
  "overall_score": 1-10的分数,
  "verdict": "READY/ALMOST/NOT_READY",
  "strengths": ["优点1", "优点2", "优点3"],
  "weaknesses": [
    {{"issue": "问题描述", "severity": "CRITICAL/MAJOR/MINOR", "suggested_fix": "修改建议"}},
    {{"issue": "问题描述", "severity": "CRITICAL/MAJOR/MINOR", "suggested_fix": "修改建议"}}
  ],
  "claims_evidence_check": [
    {{"claim": "论文中的主要论点", "has_evidence": true/false, "evidence_location": "在哪个章节"}}
  ],
  "actionable_fixes": [
    {{"priority": "P0/P1/P2", "what_to_fix": "需要修改什么", "how_to_fix": "具体如何修改"}}
  ]
}}

审稿维度:
1. Clarity(清晰度): 贡献是否一目了然？
2. Novelty(新颖性): 与已有工作的区别是否清晰？
3. Significance(重要性): 发现/结论有多大价值？
4. Technical Correctness(技术正确性): 方法论是否合理？
5. Rigor(严谨性): 数据、分析是否充分？
6. Presentation(呈现): 写作质量、结构、逻辑性

严格打分，不要客气。6分=勉强合格，7分=良好，8分=优秀。"""

        try:
            content, model_used, _ = self.router.call(
                'critic',
                [{'role': 'user', 'content': prompt}],
                max_tokens=3000,
                budget='balanced',
                temperature=0.3,
            )

            logger.info(f"审稿完成 (by {model_used})")

            result = self._parse_json(content)
            result['raw_text'] = content
            return result

        except Exception as e:
            logger.error(f"LLM审稿失败: {e}")
            return None

    def _load_review_criteria_context(self, review_criteria: str) -> dict:
        """加载可选领域审稿标准，失败时返回空上下文。"""
        if not review_criteria:
            return {}
        path = review_criteria
        if not os.path.isabs(path):
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), path)
        if not os.path.exists(path):
            logger.warning("review_criteria not found: %s", path)
            return {}
        try:
            data = json.loads(open(path, "r", encoding="utf-8").read())
        except Exception as exc:
            logger.warning("failed to load review_criteria %s: %s", path, exc)
            return {}

        dims = data.get("dimensions", [])
        rules = data.get("minimum_readiness_rules", [])
        hard = data.get("hard_fail_patterns", [])
        outputs = data.get("output_requirements", [])
        block = [
            "## 领域审稿标准",
            f"标准名称: {data.get('name', '')}",
            f"目标期刊: {', '.join(data.get('target_journals', []))}",
            "",
            "### Minimum readiness rules",
        ]
        block.extend(f"- {r}" for r in rules)
        block += ["", "### Review dimensions"]
        for dim in dims:
            block.append(f"- {dim.get('name')} (weight={dim.get('weight', 1)}): "
                         + "; ".join(dim.get("questions", [])[:4]))
        block += ["", "### Hard-fail patterns"]
        block.extend(f"- {h}" for h in hard)
        block += ["", "### Output requirements"]
        block.extend(f"- {o}" for o in outputs)
        return {
            "reviewer_role": data.get("reviewer_role", ""),
            "prompt_block": "\n".join(block),
        }

    # ============ 静态评分（无LLM降级）============

    def _static_scoring(self, report: ReviewReport, static: dict, ai_isms: list) -> ReviewReport:
        """无LLM时基于静态检查的简单打分。"""
        score = 6.0  # 基础分

        # 扣分项
        issues = static.get('structural_issues', [])
        score -= len(issues) * 0.5

        # AI痕迹扣分
        score -= min(len(ai_isms) * 0.2, 1.5)

        # 结构分
        if static.get('structure_score') == 'Good':
            score += 0.5
        elif static.get('structure_score') == 'Poor':
            score -= 1.0

        report.overall_score = max(1.0, min(10.0, score))
        return report

    # ============ 工具函数 ============

    def _parse_json(self, content: str) -> dict:
        """从LLM响应中解析JSON。"""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return {}


# ============ De-AI Polish功能 ============

def deai_polish(text: str) -> str:
    """
    去除AI写作痕迹。
    可用于论文生成后的后处理。
    """
    result = text

    # 替换意义膨胀词
    for old, new in INFLATION_WORDS.items():
        result = re.sub(re.escape(old), new, result, flags=re.IGNORECASE)

    # 移除模板化开头
    patterns_to_remove = [
        r'In this section, we ',
        r'在本节中，我们',
        r'It is worth noting that ',
        r'值得注意的是，',
    ]
    for pat in patterns_to_remove:
        result = re.sub(pat, '', result, flags=re.IGNORECASE)

    return result


def get_ai_ism_suggestions(text: str) -> list:
    """
    返回AI痕迹词的具体替换建议。
    """
    suggestions = []
    text_lower = text.lower()

    for old, new in INFLATION_WORDS.items():
        if old.lower() in text_lower:
            suggestions.append({
                'original': old,
                'replacement': new,
                'reason': '意义膨胀，建议使用更审慎的表达',
            })

    return suggestions


# ============ 便捷测试 ============
if __name__ == "__main__":
    agent = ReviewAgent()

    # 测试De-AI检测
    test_text = """
    This groundbreaking study delves into the pivotal landscape of digital humanities.
    It is worth noting that this revolutionary approach represents a paradigm shift.
    In this section, we discuss the noteworthy findings.
    本文具有里程碑意义的发现值得注意的是不言而喻的。
    """
    isms = agent._detect_ai_isms(test_text)
    print("AI痕迹检测:")
    for ism in isms:
        print(f"  - {ism}")

    print("\nDe-AI Polish:")
    polished = deai_polish(test_text)
    print(polished)
