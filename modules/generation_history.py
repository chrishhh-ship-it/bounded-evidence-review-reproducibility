"""
生成历史记录 — 进化学习层
记录每次报告/论文生成的完整经验，供下次参考，实现越用越聪明。

存储: data/generation_history_{user_id}.jsonl (append-only)

ARIS增强: Pipeline状态持久化，支持断点续跑。
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


class GenerationHistory:
    """生成历史记录与进化上下文提供器"""

    def __init__(self, user_id: int = 0):
        self.user_id = user_id
        self.filepath = os.path.join(DATA_DIR, f"generation_history_{user_id}.jsonl")
        os.makedirs(DATA_DIR, exist_ok=True)

    # ── 写入 ──────────────────────────────────────────────

    def _append(self, record: dict):
        record["timestamp"] = datetime.now().isoformat()
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        logger.info(f"[GenerationHistory] 记录: {record.get('type', '?')} / {record.get('field', '?')}")

    def record_report(self, field: str, directions: list):
        """记录 Phase 1 报告生成"""
        self._append({
            "type": "report",
            "field": field,
            "directions_count": len(directions),
            "direction_titles": [d.get("title", d) if isinstance(d, dict) else str(d) for d in directions],
        })

    def record_selection(self, field: str, selected_title: str, user_feedback: str = ""):
        """记录用户选择"""
        self._append({
            "type": "selection",
            "field": field,
            "selected_title": selected_title,
            "user_feedback": user_feedback,
        })

    def record_paper(self, field: str, word_count: int, citation_count: int,
                     integrity: bool, quality_notes: str = ""):
        """记录 Phase 2 论文生成"""
        self._append({
            "type": "paper",
            "field": field,
            "word_count": word_count,
            "citation_count": citation_count,
            "citation_integrity": integrity,
            "quality_notes": quality_notes,
        })

    # ── 读取 ──────────────────────────────────────────────

    def _load_all(self) -> List[dict]:
        if not os.path.exists(self.filepath):
            return []
        records = []
        with open(self.filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return records

    def get_field_history(self, field: str) -> List[dict]:
        """获取某领域的所有历史记录"""
        return [r for r in self._load_all() if r.get("field", "") == field]

    def get_all_fields(self) -> List[str]:
        """获取所有曾经生成过的领域"""
        return list({r.get("field", "") for r in self._load_all() if r.get("field")})

    # ── 进化上下文生成 ────────────────────────────────────

    def get_evolution_context(self, field: str) -> str:
        """
        生成进化上下文文本，注入到AI prompt中。
        包括: 过去推荐过的方向、用户选择偏好、论文质量反馈。
        """
        history = self.get_field_history(field)
        if not history:
            return ""

        lines = [f"## 历史经验 (领域: {field})\n"]

        # 统计
        reports = [r for r in history if r["type"] == "report"]
        selections = [r for r in history if r["type"] == "selection"]
        papers = [r for r in history if r["type"] == "paper"]

        if reports:
            all_past_titles = []
            for rpt in reports:
                all_past_titles.extend(rpt.get("direction_titles", []))
            lines.append(f"- 历史共生成 {len(reports)} 次方向报告")
            if all_past_titles:
                lines.append(f"- 曾推荐过的方向: {', '.join(all_past_titles[:15])}")
                lines.append("- **请避免重复推荐以上方向，或在其基础上提出更深入的变体**")

        if selections:
            selected = [s["selected_title"] for s in selections]
            lines.append(f"- 用户历史选择: {', '.join(selected)}")
            feedbacks = [s["user_feedback"] for s in selections if s.get("user_feedback")]
            if feedbacks:
                lines.append(f"- 用户反馈: {'; '.join(feedbacks)}")

        if papers:
            avg_wc = sum(p.get("word_count", 0) for p in papers) // len(papers)
            latest = papers[-1]
            lines.append(f"- 历史论文平均字数: {avg_wc}")
            if latest.get("quality_notes"):
                lines.append(f"- 最近一次质量反馈: {latest['quality_notes']}")
            lines.append(f"- **本次生成应改进以上问题**")

        return "\n".join(lines)

    def get_writing_lessons(self) -> str:
        """从历史论文生成中提取写作经验"""
        all_records = self._load_all()
        papers = [r for r in all_records if r["type"] == "paper"]
        if not papers:
            return ""

        lessons = ["## 写作经验总结\n"]
        for p in papers[-5:]:  # 最近5次
            field = p.get("field", "?")
            wc = p.get("word_count", 0)
            cc = p.get("citation_count", 0)
            notes = p.get("quality_notes", "")
            integrity = p.get("citation_integrity", True)
            lessons.append(f"- [{field}] 字数{wc}, 引用{cc}篇, 完整性{'通过' if integrity else '有问题'}")
            if notes:
                lessons.append(f"  反馈: {notes}")

        # 推导经验
        word_counts = [p.get("word_count", 0) for p in papers if p.get("word_count")]
        if word_counts:
            max_wc = max(word_counts)
            lessons.append(f"\n- 建议目标字数: ≥ {max(max_wc, 8000)} 词")
            lessons.append("- 每章节必须达到目标字数的 90% 以上")
            lessons.append("- 引用必须使用 CitationRegistry 统一管理，禁止编造引用")

        return "\n".join(lessons)

    # ── Pipeline状态持久化 (ARIS断点续跑) ──────────────────

    @property
    def _state_filepath(self) -> str:
        return os.path.join(DATA_DIR, f"pipeline_state_{self.user_id}.json")

    def save_pipeline_state(self, state: dict):
        """
        保存Pipeline运行状态，支持断点续跑。

        state示例:
        {
            "stage": "SEARCH",
            "status": "in_progress",
            "field": "数字人文",
            "completed_stages": ["INIT", "SEARCH"],
            "papers_count": 150,
            "last_score": 6.5,
            "config": {...},
            "artifacts": {
                "papers_file": "data/papers_cache.json",
                "report_file": "data/reports/xxx.md",
            }
        }
        """
        state["timestamp"] = datetime.now().isoformat()
        state["user_id"] = self.user_id

        with open(self._state_filepath, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        logger.info(f"[PipelineState] 已保存: stage={state.get('stage')}, status={state.get('status')}")

    def load_pipeline_state(self) -> Optional[dict]:
        """加载上次Pipeline状态。无状态文件时返回None。"""
        if not os.path.exists(self._state_filepath):
            return None
        try:
            with open(self._state_filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"[PipelineState] 读取失败: {e}")
            return None

    def can_resume(self) -> bool:
        """
        检查是否有可恢复的运行。
        条件: 24小时内 + status为in_progress
        """
        state = self.load_pipeline_state()
        if not state:
            return False
        if state.get("status") != "in_progress":
            return False

        ts = state.get("timestamp", "")
        try:
            saved_time = datetime.fromisoformat(ts)
            if datetime.now() - saved_time > timedelta(hours=24):
                logger.info("[PipelineState] 状态已过期(>24h)")
                return False
        except (ValueError, TypeError):
            return False

        return True

    def clear_pipeline_state(self):
        """清除Pipeline状态（完成或放弃时调用）。"""
        if os.path.exists(self._state_filepath):
            os.remove(self._state_filepath)
            logger.info("[PipelineState] 已清除")

    def record_review_round(self, field: str, round_num: int, score: float,
                            verdict: str, fixes_applied: int):
        """记录审稿改进轮次（ARIS Auto Review Loop追踪）。"""
        self._append({
            "type": "review_round",
            "field": field,
            "round": round_num,
            "score": score,
            "verdict": verdict,
            "fixes_applied": fixes_applied,
        })
