"""v2.3 V1: single-agent self-critique starting from the SAME B1 draft that V2
(ARL) starts from -- this is the fairness fix the v2.2 pilot already
established and v2.3 must not regress on. Frozen per
semantic_arl_v2_3_protocol_freeze_20260725.md.

Evidence-availability check happens INSIDE the prompt (the model is told to
output EVIDENCE_UNAVAILABLE directly when the supplied abstract is empty),
not reconstructed afterwards from abstract length -- this was the
methodological weakness the HEDGE v2.3 simulation audit flagged.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

B1_DIR = PROJECT_ROOT / "data" / "expanded_outputs" / "semantic_v23_b1"
OUTPUT_DIR = PROJECT_ROOT / "data" / "expanded_outputs" / "semantic_v23_v1_self_critique"
PRINT_LOCK = threading.Lock()

TEMPERATURE = 0.0
MAX_TOKENS = 24000


def _prompt_for(draft: str, papers: list[dict[str, Any]]) -> str:
    evidence_blocks = []
    for i, p in enumerate(papers, start=1):
        abstract = (p.get("abstract") or "").strip()
        if abstract:
            ev_text = f"Abstract: {abstract}"
        else:
            ev_text = "Abstract: [NO ABSTRACT AVAILABLE -- do not guess or infer support from title alone]"
        evidence_blocks.append(f"[{i}] {p.get('title','')} ({p.get('year','')})\n{ev_text}")
    return (
        "You wrote the draft below using only the numbered evidence records that "
        "follow it. Re-read every sentence that carries a [N] citation and "
        "classify it using exactly one of these five labels:\n\n"
        "EVIDENCE_UNAVAILABLE -- the evidence record for this citation has no "
        "abstract text (marked '[NO ABSTRACT AVAILABLE]'). Use this label "
        "whenever the cited record's abstract is missing, regardless of how "
        "plausible the claim sounds. Do not guess.\n"
        "SUPPORTED -- an abstract IS available and it directly backs the "
        "specific claim.\n"
        "PARTIAL -- an abstract is available, is topically related, but does "
        "not fully back the specific wording (the claim is broader or more "
        "definite than the abstract supports).\n"
        "INSUFFICIENT -- an abstract is available but does not contain enough "
        "information to judge the claim either way.\n"
        "CONTRADICTED -- an abstract is available and states something "
        "inconsistent with the claim.\n\n"
        "Then rewrite the report applying these rules:\n"
        "- EVIDENCE_UNAVAILABLE: keep the sentence, but append this exact "
        "parenthetical immediately after it: "
        "（注：本主张所引证据在"
        "当前语料中缺失可用的摘要"
        "文本，无法核实该主张，"
        "需在后续补齐证据后复核。）\n"
        "- SUPPORTED: keep the sentence unchanged.\n"
        "- PARTIAL: narrow or hedge the sentence so its wording matches only "
        "what the abstract actually supports.\n"
        "- INSUFFICIENT or CONTRADICTED: delete the sentence entirely.\n"
        "- Do not introduce any new citation identifier or new claim not in "
        "the original draft.\n"
        "- Preserve section structure and the bibliography (remove a "
        "bibliography entry only if every sentence citing it was deleted).\n\n"
        "Original draft:\n" + draft + "\n\n"
        "Evidence records:\n" + "\n\n".join(evidence_blocks) + "\n\n"
        "Output only the revised report, in the same format as the original "
        "draft. Do not include your per-sentence classifications in the output."
    )


def _run_one(qid: str, provider: str, model: str, provider_key: str,
             overwrite: bool) -> dict[str, Any]:
    from modules.ai_provider import call_ai

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    existing = sorted(OUTPUT_DIR.glob(f"{qid}_v23v1_*.md"))
    if existing and not overwrite:
        return {"qid": qid, "status": "skipped", "file": str(existing[-1])}

    b1_md = B1_DIR / f"{qid}_semantic_v23_b1.md"
    b1_json = B1_DIR / f"{qid}_semantic_v23_b1.json"
    if not b1_md.exists():
        return {"qid": qid, "status": "failed", "error": "no B1 source"}
    draft = b1_md.read_text(encoding="utf-8")
    meta_b1 = json.loads(b1_json.read_text(encoding="utf-8"))
    papers = meta_b1.get("top_papers") or []

    prompt = _prompt_for(draft, papers)
    system = (
        "You are a careful academic self-reviewer. Classify strictly by "
        "whether abstract text is present before judging support; never treat "
        "a missing abstract as grounds to guess support or non-support."
    )
    started = time.time()
    response = call_ai(
        prompt=prompt, system=system, provider=provider, api_key=provider_key,
        model=model or None, task_type="analysis", max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE, timeout=180,
    )
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"{qid}_v23v1_{stamp}"
    md_path = OUTPUT_DIR / f"{stem}.md"
    json_path = OUTPUT_DIR / f"{stem}.json"
    md_path.write_text(response, encoding="utf-8")
    meta = {
        "condition": "V1_self_critique",
        "protocol": "semantic_arl_v2_3",
        "qid": qid,
        "source_b1": str(b1_md.relative_to(PROJECT_ROOT)),
        "provider": provider,
        "model": model,
        "top_papers": papers,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "elapsed_seconds": round(time.time() - started, 3),
        "output_markdown": str(md_path.relative_to(PROJECT_ROOT)),
    }
    json_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"qid": qid, "status": "completed", "file": str(md_path),
            "elapsed_seconds": meta["elapsed_seconds"]}


def main() -> None:
    from modules.searcher import _load_saved_search_config

    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="deepseek")
    ap.add_argument("--model", default="deepseek-v4-pro")
    ap.add_argument("--start", type=int, default=31)
    ap.add_argument("--end", type=int, default=60)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    config = _load_saved_search_config()
    provider_key = config.get(f"{args.provider}_api_key", "") or ""
    if not provider_key:
        raise SystemExit(f"Missing API key for provider={args.provider}")

    qids = [f"Q{n:02d}" for n in range(args.start, args.end + 1)]
    results = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
        futs = {ex.submit(_run_one, qid, args.provider, args.model, provider_key,
                           args.overwrite): qid for qid in qids}
        for fut in as_completed(futs):
            qid = futs[fut]
            try:
                r = fut.result()
            except Exception as exc:
                r = {"qid": qid, "status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            results.append(r)
            with PRINT_LOCK:
                print(json.dumps(r, ensure_ascii=False))

    print(json.dumps({"summary": results}, ensure_ascii=False))


if __name__ == "__main__":
    main()
