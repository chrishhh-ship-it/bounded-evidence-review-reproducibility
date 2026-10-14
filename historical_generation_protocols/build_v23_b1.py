"""v2.3 B1: deterministic structural repair applied to the NEW V0 baseline
(deepseek-v4-pro), not the old schema_single_agent_v1 (deepseek-chat). Same
repair logic as scripts/build_semantic_arl_b1.py, retargeted. No model call.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
import evaluate_metrics as em  # noqa: E402

SOURCE_DIR = PROJECT_ROOT / "data" / "expanded_outputs" / "semantic_v23_v0_baseline"
OUTPUT_DIR = PROJECT_ROOT / "data" / "expanded_outputs" / "semantic_v23_b1"
PILOT_QIDS = [f"Q{n:02d}" for n in range(31, 61)]

BIB_LINE_RE = re.compile(r"^\[(\d+)\]\s*(.*)$", re.M)
INTEXT_RE = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")


def split_body_bib(text: str) -> tuple[str, str, str]:
    for marker in ("## 参考文献", "参考文献", "## References", "References"):
        if marker in text:
            body, _, bib = text.partition(marker)
            return body, marker, bib
    return text, "", ""


def latest_for_qid(qid: str) -> Path | None:
    cands = sorted(SOURCE_DIR.glob(f"{qid}_v23v0_*.md"))
    return cands[-1] if cands else None


def build_b1(qid: str, md_path: Path) -> dict[str, Any]:
    sidecar = json.loads(md_path.with_suffix(".json").read_text(encoding="utf-8"))
    papers = sidecar.get("top_papers") or []
    eq_ids = {em._paper_id(p) for p in papers}
    idx_to_paper = {i + 1: p for i, p in enumerate(papers)}

    text = md_path.read_text(encoding="utf-8")
    body, marker, bib = split_body_bib(text)

    bib_entries = {int(m.group(1)): m.group(2) for m in BIB_LINE_RE.finditer(bib)}
    valid_idx = set()
    for idx, paper in idx_to_paper.items():
        pid = em._paper_id(paper)
        if idx in bib_entries and pid in eq_ids:
            valid_idx.add(idx)

    cited_idx = set()
    for m in INTEXT_RE.finditer(body):
        for part in m.group(1).split(","):
            part = part.strip()
            if part.isdigit():
                cited_idx.add(int(part))

    removed_intext = sorted(i for i in cited_idx if i not in valid_idx)
    uncited_bib = sorted(i for i in bib_entries if i not in cited_idx)
    kept_bib = sorted(i for i in bib_entries if i in valid_idx and i in cited_idx)

    def repl(m: re.Match) -> str:
        parts = [p.strip() for p in m.group(1).split(",")]
        kept = [p for p in parts if p.isdigit() and int(p) in valid_idx]
        if kept:
            return "[" + ",".join(kept) + "]"
        return "[unsupported-citation-removed]"

    new_body = INTEXT_RE.sub(repl, body)
    new_bib_lines = [f"[{i}] {bib_entries[i]}" for i in kept_bib]
    new_text = new_body.rstrip() + "\n\n" + marker + "\n" + "\n".join(new_bib_lines) + "\n"

    out_md = OUTPUT_DIR / f"{qid}_semantic_v23_b1.md"
    out_json = OUTPUT_DIR / f"{qid}_semantic_v23_b1.json"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_md.write_text(new_text, encoding="utf-8")
    meta = {
        "qid": qid,
        "protocol": "semantic_arl_v2_3",
        "source_v0": str(md_path.relative_to(PROJECT_ROOT)),
        "removed_in_text_refs": removed_intext,
        "removed_uncited_bib": uncited_bib,
        "kept_bib_indices": kept_bib,
        "top_papers": papers,
    }
    out_json.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "qid": qid,
        "removed_in_text_refs": len(removed_intext),
        "removed_uncited_bib": len(uncited_bib),
        "kept_bib": len(kept_bib),
    }


def main() -> None:
    summary = []
    for qid in PILOT_QIDS:
        path = latest_for_qid(qid)
        if not path:
            summary.append({"qid": qid, "status": "missing_v0"})
            continue
        summary.append(build_b1(qid, path))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
