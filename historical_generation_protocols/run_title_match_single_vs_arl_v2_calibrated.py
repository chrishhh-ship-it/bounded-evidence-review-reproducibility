from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import subprocess
import sys
import tempfile
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

VERIFIED_PATH = Path(r"<USER_ROOT>\Downloads\title_match_verified_key_20260730.csv")
OUTPUT_ROOT = (
    PROJECT_ROOT
    / "data"
    / "reports"
    / "ipm_major_revision_20260721"
    / "repro"
    / "v3"
    / "title_match_single_vs_arl_20260730_calibrated"
)

SINGLE_MODEL = "deepseek-v4-pro"
ARL_ANALYST_MODEL = "deepseek-v4-pro"
ARL_CRITIC_MODEL = "moonshot-v1-32k"
ARL_ADJUDICATOR_MODEL = "deepseek-v4-pro"
TEMPERATURE = 0.0
MAX_TOKENS = 12000
TIMEOUT = 240

# The user's adjudication of the two remaining human disagreements.
ADJUDICATION_OVERRIDES = {"TM077": "match", "TM189": "nonmatch"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_gold() -> list[dict[str, Any]]:
    rows = read_csv(VERIFIED_PATH)
    result = []
    for row in rows:
        label = ADJUDICATION_OVERRIDES.get(row["pair_id"], row["coder_label"].strip().lower())
        if label not in {"match", "nonmatch"}:
            raise ValueError(f"Unexpected gold label: {row['pair_id']}={label}")
        result.append(
            {
                "pair_id": row["pair_id"],
                "query_id": row["query_id"],
                "domain": row["domain"],
                "reference_string": row["reference_string"],
                "candidate_evidence_title": row["candidate_evidence_title"],
                "gold_label": label,
                "gold_source": "verified_human_key_with_TM077_TM189_adjudication",
            }
        )
    if len(result) != 320:
        raise ValueError(f"Expected 320 gold rows, got {len(result)}")
    return result


def prompt_single(item: dict[str, Any]) -> str:
    return f"""You are the single-agent baseline for a controlled citation-title matching task.

Decide whether the candidate title identifies the same publication as the reference record.
Use semantic identity, not loose topical overlap. Shared words such as multi-agent,
artificial intelligence, climate, or systematic review are not enough. A match requires
the candidate to be the same work, including an exact, distinctive title or an unambiguous
translation/variant. Missing author, venue, or year in the candidate is not sufficient for
nonmatch when the title is exact and distinctive; use those fields to disambiguate generic
titles. If the topic, study, or work is different, label nonmatch.

Return JSON only, with exactly these fields:
{{"label":"match" or "nonmatch", "reason":"one concise sentence"}}

Reference record:
{item['reference_string']}

Candidate title:
{item['candidate_evidence_title']}
"""


def prompt_analyst(item: dict[str, Any]) -> str:
    return f"""You are Analyst 1 in a multi-agent citation-title audit.

Assess whether the candidate title refers to the same publication as the reference record.
Do semantic identity checking, not token-overlap matching. Distinguish exact/equivalent
titles from merely related topics, shared methods, or shared words. Missing bibliographic
fields do not override an exact distinctive title; use them to resolve generic ambiguity.
Be conservative about topical overlap, but do not confuse missing metadata with a different work.

Return JSON only:
{{"label":"match" or "nonmatch", "evidence":"brief comparison", "risk":"brief ambiguity note"}}

Reference record:
{item['reference_string']}

Candidate title:
{item['candidate_evidence_title']}
"""


def prompt_critic(item: dict[str, Any], analyst: str) -> str:
    return f"""You are Analyst 2, an adversarial critic in a multi-agent citation audit.

    Independently inspect the reference and candidate, then challenge Analyst 1. Apply a two-layer
    identity rule: first determine whether the candidate title is the same title, an unambiguous
    translation, or an unambiguous variant of the reference work; then use author, venue, and year
    as corroborating metadata. Missing venue, year, or authors in the candidate is not sufficient
    evidence of a nonmatch when the title is exact and distinctive. Require corroborating metadata
    for generic or genuinely ambiguous titles. Reject matches based only on shared words or a broad
    subject relationship. Do not confuse metadata completeness with publication identity.

Return JSON only:
{{"label":"match" or "nonmatch", "challenge":"brief reason", "confidence":"high, medium, or low"}}

Reference record:
{item['reference_string']}

Candidate title:
{item['candidate_evidence_title']}

Analyst 1 output to audit:
{analyst}
"""


def prompt_adjudicator(item: dict[str, Any], analyst: str, critic: str) -> str:
    return f"""You are the final adjudicator in a role-separated citation-title audit.

    Determine whether the candidate is the same publication as the reference. Resolve the two
    analyses using the actual title and bibliographic identity. A match means an exact, distinctive
    title, an unambiguous translation, or an unambiguous title variant of the same work. The
    reference string may contain author, journal, and year fields absent from the candidate; this
    is a metadata-completeness issue and must not override an exact title identity. Use metadata to
    disambiguate generic titles. A nonmatch requires a substantive title/work difference or
    unresolved identity ambiguity, not merely missing metadata. Do not reward token overlap or
    general topical relatedness.

Return JSON only:
{{"label":"match" or "nonmatch", "reason":"one concise sentence"}}

Reference record:
{item['reference_string']}

Candidate title:
{item['candidate_evidence_title']}

Analyst 1:
{analyst}

Analyst 2:
{critic}
"""


def parse_label(text: str) -> str:
    clean = text.strip().lower()
    # Prefer a JSON label if the provider wrapped it in a code fence.
    match = re.search(r'"label"\s*:\s*"(match|nonmatch)"', clean)
    if match:
        return match.group(1)
    if re.search(r"\bnonmatch\b", clean):
        return "nonmatch"
    if re.search(r"\bmatch\b", clean):
        return "match"
    raise ValueError(f"Could not parse match/nonmatch label from: {text[:500]!r}")


def call_json(prompt: str, provider: str, api_key: str, model: str) -> tuple[str, str, float]:
    from modules.ai_provider import PROVIDERS

    started = time.time()
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Return only the requested JSON. Do not add markdown or commentary.",
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
    }
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            with tempfile.TemporaryDirectory(prefix="title_match_api_") as temp_dir:
                temp_path = Path(temp_dir)
                payload_path = temp_path / "payload.json"
                config_path = temp_path / "curl.cfg"
                payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
                config_path.write_text(
                    "\n".join(
                        [
                            f'url = "{PROVIDERS[provider]["base_url"]}"',
                            'request = "POST"',
                            'header = "Content-Type: application/json"',
                            f'header = "Authorization: Bearer {api_key}"',
                        ]
                    ),
                    encoding="utf-8",
                )
                completed = subprocess.run(
                    [
                        "curl.exe",
                        "--silent",
                        "--show-error",
                        "--fail-with-body",
                        "--retry",
                        "2",
                        "--retry-delay",
                        "2",
                        "--retry-all-errors",
                        "--max-time",
                        str(TIMEOUT),
                        "--config",
                        str(config_path),
                        "--data-binary",
                        f"@{payload_path}",
                    ],
                    capture_output=True,
                    check=False,
                )
                stdout = completed.stdout.decode("utf-8", errors="replace")
                stderr = completed.stderr.decode("utf-8", errors="replace")
                if completed.returncode != 0:
                    raise RuntimeError(
                        f"{provider} curl transport failed ({completed.returncode}): "
                        f"{(stdout or stderr)[:800]}"
                    )
                # A provider may occasionally append a second JSON envelope to the
                # response. Decode the first complete envelope instead of losing the
                # whole item to JSONDecodeError: Extra data.
                try:
                    data = json.loads(stdout)
                except json.JSONDecodeError:
                    decoder = json.JSONDecoder()
                    data, _ = decoder.raw_decode(stdout.lstrip())
                if "error" in data:
                    raise RuntimeError(f"{provider} API error: {json.dumps(data['error'])[:800]}")
                raw = data["choices"][0]["message"]["content"]
                return parse_label(raw), raw, round(time.time() - started, 3)
        except Exception as exc:
            last_error = exc
            if attempt < 3:
                time.sleep(2 * attempt)
            else:
                raise RuntimeError(f"{provider} request failed after 3 attempts: {exc}") from exc
    raise RuntimeError(f"{provider} request failed: {last_error}")


def run_item(
    item: dict[str, Any],
    single_provider: str,
    single_key: str,
    analyst_provider: str,
    analyst_key: str,
    critic_provider: str,
    critic_key: str,
    adjudicator_provider: str,
    adjudicator_key: str,
) -> dict[str, Any]:
    single_prompt = prompt_single(item)
    analyst_prompt = prompt_analyst(item)
    single_label, single_raw, single_elapsed = call_json(
        single_prompt, single_provider, single_key, SINGLE_MODEL
    )
    analyst_label, analyst_raw, analyst_elapsed = call_json(
        analyst_prompt, analyst_provider, analyst_key, ARL_ANALYST_MODEL
    )
    critic_prompt = prompt_critic(item, analyst_raw)
    critic_label, critic_raw, critic_elapsed = call_json(
        critic_prompt, critic_provider, critic_key, ARL_CRITIC_MODEL
    )
    adjudicator_prompt = prompt_adjudicator(item, analyst_raw, critic_raw)
    arl_label, adjudicator_raw, adjudicator_elapsed = call_json(
        adjudicator_prompt, adjudicator_provider, adjudicator_key, ARL_ADJUDICATOR_MODEL
    )
    return {
        **item,
        "single_provider": single_provider,
        "single_model": SINGLE_MODEL,
        "arl_analyst_provider": analyst_provider,
        "arl_analyst_model": ARL_ANALYST_MODEL,
        "arl_critic_provider": critic_provider,
        "arl_critic_model": ARL_CRITIC_MODEL,
        "arl_adjudicator_provider": adjudicator_provider,
        "arl_adjudicator_model": ARL_ADJUDICATOR_MODEL,
        "temperature": TEMPERATURE,
        "single_label": single_label,
        "arl_analyst_label": analyst_label,
        "arl_critic_label": critic_label,
        "arl_final_label": arl_label,
        "single_correct": single_label == item["gold_label"],
        "arl_correct": arl_label == item["gold_label"],
        "single_prompt_sha256": hashlib.sha256(single_prompt.encode("utf-8")).hexdigest(),
        "arl_analyst_prompt_sha256": hashlib.sha256(analyst_prompt.encode("utf-8")).hexdigest(),
        "arl_critic_prompt_sha256": hashlib.sha256(critic_prompt.encode("utf-8")).hexdigest(),
        "arl_adjudicator_prompt_sha256": hashlib.sha256(adjudicator_prompt.encode("utf-8")).hexdigest(),
        "single_raw": single_raw,
        "arl_analyst_raw": analyst_raw,
        "arl_critic_raw": critic_raw,
        "arl_adjudicator_raw": adjudicator_raw,
        "elapsed_seconds": single_elapsed + analyst_elapsed + critic_elapsed + adjudicator_elapsed,
    }


def metric_block(rows: list[dict[str, Any]], label_key: str, gold_key: str = "gold_label") -> dict[str, float]:
    n = len(rows)
    counts = Counter((row[gold_key], row[label_key]) for row in rows)
    accuracy = sum(counts[(label, label)] for label in ("match", "nonmatch")) / n
    values: dict[str, float] = {"accuracy": accuracy}
    f1s = []
    for label in ("match", "nonmatch"):
        tp = counts[(label, label)]
        fp = counts[("nonmatch" if label == "match" else "match", label)]
        fn = counts[(label, "nonmatch" if label == "match" else "match")]
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        score = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        values[f"{label}_precision"] = precision
        values[f"{label}_recall"] = recall
        values[f"{label}_f1"] = score
        f1s.append(score)
    values["macro_f1"] = sum(f1s) / 2
    values["errors"] = n - sum(counts[(label, label)] for label in ("match", "nonmatch"))
    return values


def exact_mcnemar_p(rows: list[dict[str, Any]]) -> tuple[int, int, float]:
    arl_wins = sum(row["arl_correct"] and not row["single_correct"] for row in rows)
    single_wins = sum(row["single_correct"] and not row["arl_correct"] for row in rows)
    total = arl_wins + single_wins
    if total == 0:
        return arl_wins, single_wins, 1.0
    tail = sum(math.comb(total, k) for k in range(arl_wins, total + 1)) / (2 ** total)
    p = min(1.0, 2 * min(tail, 1 - tail + math.comb(total, arl_wins) / (2 ** total)))
    return arl_wins, single_wins, p


def main() -> None:
    from modules.searcher import _load_saved_search_config

    parser = argparse.ArgumentParser()
    parser.add_argument("--single-provider", default="deepseek")
    parser.add_argument("--arl-analyst-provider", default="deepseek")
    parser.add_argument("--arl-critic-provider", default="kimi")
    parser.add_argument("--arl-adjudicator-provider", default="deepseek")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=320)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    gold = load_gold()
    if args.smoke:
        gold = gold[:2]
    else:
        gold = [row for row in gold if args.start <= int(row["pair_id"][2:]) <= args.end]

    config = _load_saved_search_config()
    providers = {
        "single": args.single_provider,
        "arl_analyst": args.arl_analyst_provider,
        "arl_critic": args.arl_critic_provider,
        "arl_adjudicator": args.arl_adjudicator_provider,
    }
    keys = {
        role: config.get(f"{provider}_api_key", "") or ""
        for role, provider in providers.items()
    }
    missing = [role for role, key in keys.items() if not key]
    if missing:
        raise SystemExit(f"Missing API keys for roles={missing}; providers={providers}")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_ROOT / (f"smoke_{stamp}" if args.smoke else f"full_{stamp}")
    run_dir.mkdir(parents=True, exist_ok=True)
    items_dir = run_dir / "items"
    items_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "started_at": datetime.now().isoformat(),
        "providers": providers,
        "models": {
            "single": SINGLE_MODEL,
            "arl_analyst": ARL_ANALYST_MODEL,
            "arl_critic": ARL_CRITIC_MODEL,
            "arl_adjudicator": ARL_ADJUDICATOR_MODEL,
        },
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "gold_source": str(VERIFIED_PATH),
        "adjudication_overrides": ADJUDICATION_OVERRIDES,
        "n": len(gold),
        "results": [],
    }
    manifest_path = run_dir / "run_manifest.json"
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {
            pool.submit(
                run_item,
                item,
                providers["single"],
                keys["single"],
                providers["arl_analyst"],
                keys["arl_analyst"],
                providers["arl_critic"],
                keys["arl_critic"],
                providers["arl_adjudicator"],
                keys["arl_adjudicator"],
            ): item["pair_id"]
            for item in gold
        }
        for future in as_completed(futures):
            pair_id = futures[future]
            try:
                result = future.result()
                results.append(result)
                (items_dir / f"{pair_id}.json").write_text(
                    json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                status = {"pair_id": pair_id, "status": "completed"}
            except Exception as exc:
                status = {"pair_id": pair_id, "status": "failed", "error": f"{type(exc).__name__}: {exc}"}
                results.append({"pair_id": pair_id, "status": "failed", "error": status["error"]})
            manifest["results"].append(status)
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps(status, ensure_ascii=False))

    successful = [row for row in results if row.get("status") != "failed"]
    if len(successful) != len(gold):
        raise SystemExit(f"Failed items: {len(gold) - len(successful)}; no metrics written as complete")
    successful.sort(key=lambda row: int(row["pair_id"][2:]))
    result_csv = run_dir / "title_match_single_vs_arl_results.csv"
    fields = [
        "pair_id", "query_id", "domain", "gold_label", "single_label",
        "arl_analyst_label", "arl_critic_label", "arl_final_label",
        "single_correct", "arl_correct", "reference_string", "candidate_evidence_title",
        "elapsed_seconds",
    ]
    with result_csv.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in successful)
    raw_jsonl = run_dir / "title_match_single_vs_arl_raw.jsonl"
    with raw_jsonl.open("w", encoding="utf-8") as handle:
        for row in successful:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    single_metrics = metric_block(successful, "single_label")
    arl_metrics = metric_block(successful, "arl_final_label")
    arl_wins, single_wins, mcnemar_p = exact_mcnemar_p(successful)
    report = {
        "n": len(successful),
        "gold_counts": dict(Counter(row["gold_label"] for row in successful)),
        "single_agent": single_metrics,
        "arl": arl_metrics,
        "delta_arl_minus_single": {
            key: arl_metrics[key] - single_metrics[key]
            for key in ("accuracy", "macro_f1", "errors")
        },
        "paired_comparison": {
            "arl_correct_single_wrong": arl_wins,
            "single_correct_arl_wrong": single_wins,
            "exact_mcnemar_p": mcnemar_p,
        },
        "interpretation": (
            "ARL is supported as an incremental structural-title-audit method only if its "
            "gold-referenced performance exceeds the single-agent baseline under the same "
            "inputs and the paired comparison is substantively and statistically persuasive."
        ),
    }
    metrics_path = run_dir / "TITLE_MATCH_SINGLE_VS_ARL_METRICS.json"
    metrics_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest["finished_at"] = datetime.now().isoformat()
    manifest["status"] = "complete"
    manifest["result_csv"] = str(result_csv)
    manifest["raw_jsonl"] = str(raw_jsonl)
    manifest["metrics_json"] = str(metrics_path)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": "complete", "run_dir": str(run_dir), "metrics": report}, ensure_ascii=False))


if __name__ == "__main__":
    main()
