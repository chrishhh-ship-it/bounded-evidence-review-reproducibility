from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
METHOD2_SCRIPT = PROJECT_ROOT / "scripts" / "batch_run_method2.py"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convenience wrapper for running Method 2b (same-model ARL control)."
    )
    parser.add_argument("--writer-provider", default="deepseek")
    parser.add_argument("--writer-model", default="deepseek-chat")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=30)
    parser.add_argument("--query-id", default=None)
    parser.add_argument("--benchmark-path", default="")
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--review-rounds", type=int, default=1)
    parser.add_argument("--no-stop-on-accept", action="store_true")
    parser.add_argument("--sleep", type=float, default=12.0)
    args = parser.parse_args()

    cmd = [
        sys.executable,
        str(METHOD2_SCRIPT),
        "--mode",
        "same_model",
        "--writer-provider",
        args.writer_provider,
        "--writer-model",
        args.writer_model,
        "--start",
        str(args.start),
        "--end",
        str(args.end),
        "--review-rounds",
        str(args.review_rounds),
        "--sleep",
        str(args.sleep),
    ]
    if args.query_id:
        cmd.extend(["--query-id", args.query_id])
    if args.benchmark_path:
        cmd.extend(["--benchmark-path", args.benchmark_path])
    if args.output_dir:
        cmd.extend(["--output-dir", args.output_dir])
    if args.no_stop_on_accept:
        cmd.append("--no-stop-on-accept")

    raise SystemExit(subprocess.call(cmd, cwd=str(PROJECT_ROOT)))


if __name__ == "__main__":
    main()
