from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
DATA_DIR = PROJECT_ROOT / "data" / "baselines"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    from modules.ai_provider import call_ai
    from modules.meta_opt import sync_baseline_result
    from modules.research_wiki import ingest_baseline_result
    from modules.searcher import _load_saved_search_config

    parser = argparse.ArgumentParser(description="Run Baseline A: single-agent direct report generation.")
    parser.add_argument("--query", required=True, help="Research topic or intelligence query.")
    parser.add_argument("--provider", default="deepseek", help="LLM provider, default deepseek.")
    parser.add_argument("--model", default="", help="Optional model override.")
    parser.add_argument("--out-prefix", default="single_agent", help="Output file prefix.")
    args = parser.parse_args()

    cfg = _load_saved_search_config()
    provider_key = cfg.get(f"{args.provider}_api_key", "") or ""

    system = (
        "You are an academic intelligence analyst. "
        "Answer in Chinese. Produce a concise but structured intelligence report. "
        "Do not invent references. If evidence is missing, explicitly state the uncertainty."
    )
    prompt = (
        f"Research topic: {args.query}\n\n"
        "Please write a structured intelligence-style report with the following sections:\n"
        "1. Problem framing\n"
        "2. Likely research directions\n"
        "3. Risks and unknowns\n"
        "4. A cautious conclusion\n\n"
        "This baseline has no external retrieval context. "
        "Make uncertainty explicit and avoid fabricated citations."
    )

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"{args.out_prefix}_{stamp}"
    md_path = DATA_DIR / f"{stem}.md"
    json_path = DATA_DIR / f"{stem}.json"
    err_path = DATA_DIR / "errors.jsonl"

    try:
        response = call_ai(
            prompt=prompt,
            system=system,
            provider=args.provider,
            api_key=provider_key,
            model=args.model or None,
            task_type="analysis",
            max_tokens=2200,
            temperature=0.3,
        )
    except Exception as exc:
        err_path.write_text(
            err_path.read_text(encoding="utf-8") + json.dumps(
                {
                    "baseline": "single_agent",
                    "query": args.query,
                    "provider": args.provider,
                    "error": str(exc),
                    "timestamp": stamp,
                },
                ensure_ascii=False,
            ) + "\n",
            encoding="utf-8",
        ) if err_path.exists() else err_path.write_text(
            json.dumps(
                {
                    "baseline": "single_agent",
                    "query": args.query,
                    "provider": args.provider,
                    "error": str(exc),
                    "timestamp": stamp,
                },
                ensure_ascii=False,
            ) + "\n",
            encoding="utf-8",
        )
        raise

    md_path.write_text(response, encoding="utf-8")
    json_path.write_text(
        json.dumps(
            {
                "baseline": "single_agent",
                "query": args.query,
                "provider": args.provider,
                "model": args.model or "",
                "output_markdown": str(md_path),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    try:
        ingest_baseline_result(json_path)
        sync_baseline_result(json_path)
    except Exception as exc:
        err_row = {
            "baseline": "single_agent",
            "query": args.query,
            "provider": args.provider,
            "error": f"sync_failed: {exc}",
            "timestamp": stamp,
        }
        with open(err_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(err_row, ensure_ascii=False) + "\n")

    print(f"[baseline] saved markdown: {md_path}")
    print(f"[baseline] saved metadata: {json_path}")


if __name__ == "__main__":
    main()
