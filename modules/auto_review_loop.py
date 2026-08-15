"""
自动审稿改进循环 (Auto Review Loop)
灵感: ARIS /auto-review-loop — 审稿→修改→重审，最多N轮，达标自动停

流程:
  Phase A: 审稿 — review_agent.review_paper() → ReviewReport
  Phase B: 判断 — score >= target → 停止
  Phase C: 修改 — 根据actionable_fixes用LLM逐项修改
  Phase D: De-AI Polish
  Phase E: 记录 — 保存本轮状态
"""
import json
import logging
import os
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Callable

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


@dataclass
class LoopResult:
    """审稿改进循环结果"""
    final_latex: str = ""
    final_bib: str = ""
    final_score: float = 0.0
    rounds_completed: int = 0
    round_history: list = field(default_factory=list)
    status: str = "NOT_STARTED"  # PASSED / MAX_ROUNDS / STOPPED / ERROR
    improvement_log: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        # 不序列化大文本
        d.pop('final_latex', None)
        d.pop('final_bib', None)
        return d

    def to_markdown(self) -> str:
        status_emoji = {
            "PASSED": "✅", "MAX_ROUNDS": "🟡",
            "STOPPED": "⏹️", "ERROR": "❌",
        }.get(self.status, "❓")

        md = f"# 审稿改进循环报告\n\n"
        md += f"**状态**: {status_emoji} {self.status}\n"
        md += f"**最终得分**: {self.final_score:.1f}/10\n"
        md += f"**完成轮次**: {self.rounds_completed}\n\n"

        if self.round_history:
            md += "## 各轮详情\n\n"
            for rh in self.round_history:
                rd = rh.get('round', '?')
                score = rh.get('score', 0)
                verdict = rh.get('verdict', '?')
                fixes = rh.get('fixes_applied', 0)
                md += f"### Round {rd}\n"
                md += f"- 得分: {score:.1f}/10 ({verdict})\n"
                md += f"- 修复: {fixes} 项\n"
                if rh.get('key_issues'):
                    md += f"- 主要问题: {', '.join(rh['key_issues'][:3])}\n"
                md += "\n"

        if self.improvement_log:
            md += f"## 改进日志\n{self.improvement_log}\n"

        return md


class AutoReviewLoop:
    """自动审稿改进循环"""

    def __init__(self, router=None, review_agent=None, user_id: int = 0):
        """
        Args:
            router: ModelRouter实例
            review_agent: ReviewAgent实例（可选，None时自动创建）
            user_id: 用户ID
        """
        self.router = router
        self.review_agent = review_agent
        self.user_id = user_id

    def run_loop(
        self,
        latex_content: str,
        bib_content: str,
        direction=None,
        max_rounds: int = 3,
        target_score: float = 7.0,
        review_criteria: str = "",
        evidence_context: str = "",
        progress_callback: Optional[Callable] = None,
    ) -> LoopResult:
        """
        运行审稿→修改→重审循环。

        Args:
            latex_content: 初始LaTeX内容
            bib_content: 初始BibTeX内容
            direction: ResearchDirection对象
            max_rounds: 最大轮次（默认3，防止过度消耗API）
            target_score: 达标分数（默认7.0）
            review_criteria: 可选审稿标准 JSON 路径
            evidence_context: 可选构念证据摘要，注入审稿 prompt
            progress_callback: fn(round, max_rounds, msg)
        """
        result = LoopResult(
            final_latex=latex_content,
            final_bib=bib_content,
            status="IN_PROGRESS",
        )
        log_lines = []

        # 确保review_agent可用
        reviewer = self._get_reviewer()
        if not reviewer:
            result.status = "ERROR"
            result.improvement_log = "无可用的ReviewAgent"
            logger.error("[ReviewLoop] 无可用的ReviewAgent")
            return result

        current_latex = latex_content
        current_bib = bib_content

        for round_num in range(1, max_rounds + 1):
            log_lines.append(f"\n{'='*50}")
            log_lines.append(f"Round {round_num}/{max_rounds}")
            log_lines.append(f"{'='*50}")

            if progress_callback:
                progress_callback(round_num, max_rounds, f"审稿轮次 {round_num}...")

            # ── Phase A: 审稿 ──
            logger.info(f"[ReviewLoop] Round {round_num}: 开始审稿")
            try:
                review_report = reviewer.review_paper(
                    latex_content=current_latex,
                    bib_content=current_bib,
                    direction=direction,
                    review_criteria=review_criteria,
                    evidence_context=evidence_context,
                )
            except Exception as e:
                logger.error(f"[ReviewLoop] Round {round_num} 审稿失败: {e}")
                log_lines.append(f"审稿异常: {e}")
                result.status = "ERROR"
                break

            score = review_report.overall_score
            verdict = review_report.verdict
            weaknesses = review_report.weaknesses
            fixes = review_report.actionable_fixes

            log_lines.append(f"得分: {score:.1f}/10 | 判定: {verdict}")
            log_lines.append(f"弱点: {len(weaknesses)} 项 | 修复建议: {len(fixes)} 项")

            # 记录本轮
            round_record = {
                'round': round_num,
                'score': score,
                'verdict': verdict,
                'weaknesses_count': len(weaknesses),
                'fixes_applied': 0,
                'key_issues': [w.get('issue', '')[:60] for w in weaknesses[:5]],
            }

            # ── Phase B: 判断是否达标 ──
            if score >= target_score and verdict != "NOT_READY":
                log_lines.append(f"✅ 达标! (score={score:.1f} >= {target_score})")
                result.rounds_completed = round_num
                result.final_score = score
                result.final_latex = current_latex
                result.final_bib = current_bib
                result.round_history.append(round_record)
                result.status = "PASSED"
                break

            # ── Phase C: 修改 ──
            if fixes and self.router:
                logger.info(f"[ReviewLoop] Round {round_num}: 应用 {len(fixes)} 项修复")

                # 按优先级排序：CRITICAL > MAJOR > MINOR
                sorted_fixes = sorted(
                    fixes,
                    key=lambda f: self._priority_rank(f.get('priority', 'MINOR'))
                )

                # 只处理CRITICAL和MAJOR（节省API调用）
                important_fixes = [
                    f for f in sorted_fixes
                    if self._priority_rank(f.get('priority')) <= 1
                ]
                if not important_fixes:
                    important_fixes = sorted_fixes[:3]

                applied = self._apply_fixes(current_latex, important_fixes)
                if applied:
                    current_latex = applied
                    round_record['fixes_applied'] = len(important_fixes)
                    log_lines.append(f"已应用 {len(important_fixes)} 项修复")
                else:
                    log_lines.append("修复应用失败，保持原文")
            else:
                log_lines.append("无可用修复建议或无LLM路由")

            # ── Phase D: De-AI Polish ──
            try:
                from modules.review_agent import deai_polish
                current_latex = deai_polish(current_latex)
                log_lines.append("De-AI Polish完成")
            except ImportError:
                pass

            # ── Phase E: 记录 ──
            result.round_history.append(round_record)
            result.final_score = score
            self._save_round_state(round_num, score, verdict)

            # 保存Pipeline状态
            try:
                from modules.generation_history import GenerationHistory
                gh = GenerationHistory(self.user_id)
                gh.record_review_round(
                    field=getattr(direction, 'title', ''),
                    round_num=round_num,
                    score=score,
                    verdict=verdict,
                    fixes_applied=round_record['fixes_applied'],
                )
            except Exception:
                pass

        else:
            # 循环自然结束（未提前break）
            result.status = "MAX_ROUNDS"

        result.final_latex = current_latex
        result.final_bib = current_bib
        result.rounds_completed = len(result.round_history)
        result.improvement_log = "\n".join(log_lines)

        logger.info(
            f"[ReviewLoop] 完成: status={result.status}, "
            f"score={result.final_score:.1f}, rounds={result.rounds_completed}"
        )
        return result

    def _get_reviewer(self):
        """获取ReviewAgent实例。"""
        if self.review_agent:
            return self.review_agent
        try:
            from modules.review_agent import ReviewAgent
            return ReviewAgent(router=self.router, user_id=self.user_id)
        except ImportError:
            logger.error("无法导入ReviewAgent")
            return None

    def _priority_rank(self, priority: Optional[str]) -> int:
        mapping = {
            'P0': 0,
            'CRITICAL': 0,
            'P1': 1,
            'MAJOR': 1,
            'P2': 2,
            'MINOR': 2,
        }
        return mapping.get(str(priority or '').upper(), 3)

    def _apply_fixes(self, latex_content: str, fixes: list) -> Optional[str]:
        """用LLM应用修复建议。"""
        if not self.router:
            return None

        fixes_text = ""
        for i, fix in enumerate(fixes, 1):
            priority = fix.get('priority', 'MINOR')
            what = fix.get('what_to_fix', '')
            how = fix.get('how_to_fix', '')
            fixes_text += f"\n{i}. [{priority}] {what}\n   修改方法: {how}\n"

        prompt = f"""你是论文修改专家。请根据以下审稿意见修改LaTeX论文。

## 需要修复的问题:
{fixes_text}

## 当前论文内容:
{latex_content[:8000]}

## 要求:
1. 针对每个问题进行修改，保持学术语言风格
2. 不要改变论文整体结构
3. 不要编造新引用
4. 只输出修改后的完整LaTeX内容（从\\begin{{document}}到\\end{{document}}之间的内容）
5. 确保所有LaTeX命令正确闭合"""

        try:
            content, _, _ = self.router.call(
                'writing',
                [{'role': 'user', 'content': prompt}],
                max_tokens=6000,
                budget='balanced',
                temperature=0.4,
            )

            # 验证返回内容是否合理（至少包含一些LaTeX标记）
            if len(content) > 500 and ('\\' in content or '\\cite' in content):
                # 如果LLM只返回了document body，需要重组
                if '\\documentclass' not in content and '\\begin{document}' not in content:
                    # 提取原始文档的头尾
                    head_match = re.search(r'(.*?\\begin\{document\})', latex_content, re.DOTALL)
                    tail_match = re.search(r'(\\end\{document\}.*)', latex_content, re.DOTALL)
                    if head_match and tail_match:
                        return head_match.group(1) + "\n" + content + "\n" + tail_match.group(1)
                return content

            logger.warning("[ReviewLoop] LLM返回内容过短或格式不正确")
            return None

        except Exception as e:
            logger.error(f"[ReviewLoop] LLM修复失败: {e}")
            return None

    def _save_round_state(self, round_num: int, score: float, verdict: str):
        """保存轮次状态到JSON文件。"""
        state_file = os.path.join(DATA_DIR, f"review_state_{self.user_id}.json")
        os.makedirs(DATA_DIR, exist_ok=True)

        state = {
            "round": round_num,
            "status": "in_progress",
            "last_score": score,
            "last_verdict": verdict,
            "timestamp": datetime.now().isoformat(),
        }

        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except IOError as e:
            logger.debug(f"保存审稿状态失败: {e}")


# ============ 便捷测试 ============
if __name__ == "__main__":
    loop = AutoReviewLoop()

    test_latex = r"""
    \documentclass{ctexart}
    \begin{document}
    \title{测试论文}
    \maketitle
    \section{引言}
    This groundbreaking study delves into a pivotal research area.
    值得注意的是，这项研究具有里程碑意义。
    \section{结论}
    综上所述，本研究具有重要意义。
    \end{document}
    """

    result = loop.run_loop(
        latex_content=test_latex,
        bib_content="",
        max_rounds=1,
    )
    print(result.to_markdown())
