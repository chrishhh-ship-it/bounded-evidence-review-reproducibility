import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_QUERIES_PATH = PROJECT_ROOT / "data" / "benchmarks" / "multi_agent_intel_service_queries.json"
RESULTS_DIR = PROJECT_ROOT / "data" / "baselines"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def run_baseline_a(query: str, qid: str):
    cmd = [
        "python", str(PROJECT_ROOT / "scripts" / "run_baseline_single_agent.py"),
        "--query", query,
        "--provider", "deepseek",
        "--out-prefix", f"{qid}_baseline_a"
    ]
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Running Baseline A for {qid}...")
    subprocess.run(cmd, check=True)

def run_baseline_b(query: str, qid: str):
    cmd = [
        "python", str(PROJECT_ROOT / "scripts" / "run_baseline_retrieval_single_agent.py"),
        "--query", query,
        "--provider", "deepseek",
        "--out-prefix", f"{qid}_baseline_b"
    ]
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Running Baseline B for {qid}...")
    subprocess.run(cmd, check=True)

def main():
    if not BENCHMARK_QUERIES_PATH.exists():
        print(f"Error: Benchmark queries not found at {BENCHMARK_QUERIES_PATH}")
        return

    with open(BENCHMARK_QUERIES_PATH, "r", encoding="utf-8") as f:
        queries = json.load(f)

    print(f"Loaded {len(queries)} benchmark queries. Starting batch execution...")
    print(f"Results will be saved to {RESULTS_DIR}")
    print("-" * 50)
    
    success_count = 0
    
    for i, q in enumerate(queries):
        qid = q["id"]
        query_text = q["query"]
        print(f"\nProcessing ({i+1}/{len(queries)}): {qid} - {query_text[:30]}...")
        
        # Check if already run (look for files starting with qid_baseline_a)
        a_files = list(RESULTS_DIR.glob(f"{qid}_baseline_a*.md"))
        b_files = list(RESULTS_DIR.glob(f"{qid}_baseline_b*.md"))
        
        if not a_files:
            try:
                run_baseline_a(query_text, qid)
                success_count += 1
            except Exception as e:
                print(f"Error running Baseline A for {qid}: {e}")
        else:
            print(f"  -> Baseline A for {qid} already exists. Skipping.")
            
        time.sleep(2) # Small pause between calls
            
        if not b_files:
            try:
                run_baseline_b(query_text, qid)
                success_count += 1
            except Exception as e:
                print(f"Error running Baseline B for {qid}: {e}")
        else:
            print(f"  -> Baseline B for {qid} already exists. Skipping.")
            
        # Sleep to avoid API rate limits (DeepSeek/Kimi usually have strict limits)
        print("Waiting 10 seconds to respect API rate limits...")
        time.sleep(10)
        
    print("\n" + "=" * 50)
    print(f"Batch run completed! Executed {success_count} new tasks.")
    print("You can now proceed to evaluate the metrics (Citation Precision, Orphan Rate, etc.)")

if __name__ == "__main__":
    main()
