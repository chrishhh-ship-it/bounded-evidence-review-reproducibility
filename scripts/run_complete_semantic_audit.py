"""Run reproducible external semantic checks for the IPM revision.

This script deliberately separates:
1) SciFact labels against the dataset's public gold labels; and
2) ALCE citation entailment, scored by a locally cached NLI classifier.

The NLI result is not called official AutoAIS because the official T5
checkpoint is not used here. It is reported as a local NLI claim-entailment
check with model name, cache path, and threshold recorded in the output.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "reports" / "ipm_major_revision_20260721" / "completion_5678_20260726"
OUT.mkdir(parents=True, exist_ok=True)


def find_snapshot(model_glob: str) -> Path:
    candidates = sorted(Path.home().glob(model_glob))
    snapshots = [p for p in candidates if p.is_dir() and (p / "config.json").exists()]
    if not snapshots:
        raise FileNotFoundError(model_glob)
    return snapshots[-1]


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def normalize_label(x: str) -> str:
    x = str(x).strip().upper()
    aliases = {"ENTAILMENT": "SUPPORT", "SUPPORTS": "SUPPORT", "SUPPORT": "SUPPORT",
               "CONTRADICTION": "CONTRADICT", "CONTRADICTED": "CONTRADICT",
               "CONTRADICT": "CONTRADICT", "NEUTRAL": "NEI", "NOT ENOUGH INFO": "NEI",
               "NEI": "NEI"}
    return aliases.get(x, x)


def scifact_metrics(path: Path) -> dict:
    rows = load_json(path)
    gold = [normalize_label(r["gold"]) for r in rows]
    result = {"n": len(rows), "labels": sorted(set(gold)), "conditions": {}}
    for key in ("v0_label", "v2_reviewer_label", "v2_final_label"):
        pred = [normalize_label(r[key]) for r in rows]
        labels = sorted(set(gold) | set(pred))
        result["conditions"][key] = {
            "accuracy": float(accuracy_score(gold, pred)),
            "macro_f1": float(f1_score(gold, pred, labels=labels, average="macro", zero_division=0)),
            "confusion_matrix_labels": labels,
            "confusion_matrix": confusion_matrix(gold, pred, labels=labels).tolist(),
            "prediction_counts": dict(Counter(pred)),
        }
    return result


def split_claims(item: dict) -> list[str]:
    text = str(item.get("output", "")).strip()
    if item.get("dataset", "").lower() == "qampari":
        parts = [p.strip() for p in text.rstrip("., ").split(",") if p.strip()]
        question = str(item.get("question", "")).strip()
        return [f"{question} {p}" for p in parts]
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if p.strip()]


def cited_pairs(item: dict) -> tuple[list[dict], int, int]:
    pairs = []
    invalid = 0
    uncited = 0
    for sentence in split_claims(item):
        ids = [int(x) - 1 for x in re.findall(r"\[(\d+)\]", sentence)]
        if not ids:
            uncited += 1
            continue
        if any(i < 0 or i >= len(item.get("docs", [])) for i in ids):
            invalid += 1
            continue
        premise = "\n".join(
            f"Title: {item['docs'][i].get('title', '')}\n{item['docs'][i].get('text', item['docs'][i].get('sent', ''))}"
            for i in ids
        )
        claim = re.sub(r"\s*\[\d+\]", "", sentence).strip()
        pairs.append({"claim": claim, "premise": premise, "n_refs": len(ids)})
    return pairs, invalid, uncited


def run_nli(rows: list[dict], model_path: Path, threshold: float = 0.5) -> dict:
    tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(str(model_path), local_files_only=True)
    model.eval()
    labels = {int(k): str(v).upper() for k, v in model.config.id2label.items()}
    entail_ids = [i for i, v in labels.items() if "ENTAIL" in v or "SUPPORT" in v]
    if not entail_ids:
        raise RuntimeError(f"No entailment label in {labels}")
    all_scores = []
    batch_size = 8
    for start in range(0, len(rows), batch_size):
        batch = rows[start:start + batch_size]
        inputs = tokenizer([r["premise"] for r in batch], [r["claim"] for r in batch],
                           padding=True, truncation=True, max_length=512, return_tensors="pt")
        with torch.inference_mode():
            logits = model(**inputs).logits
            probs = torch.softmax(logits, dim=-1).cpu().numpy()
        for r, p in zip(batch, probs):
            score = float(sum(p[i] for i in entail_ids))
            r["entailment_probability"] = score
            r["supported_at_threshold"] = bool(score >= threshold)
            all_scores.append(score)
    return {
        "model": str(model_path),
        "model_labels": labels,
        "threshold": threshold,
        "pairs": rows,
        "mean_entailment_probability": float(np.mean(all_scores)) if all_scores else None,
        "supported_pairs": int(sum(r["supported_at_threshold"] for r in rows)),
        "total_pairs": len(rows),
    }


def alce_entailment(path: Path, model_path: Path) -> dict:
    data = load_json(path)
    by_condition = defaultdict(list)
    flat = []
    structure = {}
    for item in data:
        pairs, invalid, uncited = cited_pairs(item)
        key = f"{item.get('dataset','unknown').lower()}::{item.get('condition','unknown')}"
        by_condition[key].extend(pairs)
        structure.setdefault(key, {"items": 0, "sentences": 0, "uncited": 0, "invalid": 0})
        structure[key]["items"] += 1
        structure[key]["sentences"] += len(split_claims(item))
        structure[key]["uncited"] += uncited
        structure[key]["invalid"] += invalid
        flat.extend({"dataset": item.get("dataset"), "condition": item.get("condition"), **p} for p in pairs)

    scored = run_nli(flat, model_path)
    scored_by_condition = {}
    cursor = 0
    for key, pairs in by_condition.items():
        n = len(pairs)
        subset = scored["pairs"][cursor:cursor+n]
        cursor += n
        s = structure[key]
        denom = s["sentences"]
        scored_by_condition[key] = {
            **{k: s[k] for k in ("items", "sentences", "uncited", "invalid")},
            "cited_sentence_rate": float((denom - s["uncited"] - s["invalid"]) / denom) if denom else None,
            "claim_entailment_rate": float(np.mean([x["supported_at_threshold"] for x in subset])) if subset else None,
            "mean_entailment_probability": float(np.mean([x["entailment_probability"] for x in subset])) if subset else None,
            "pairs": len(subset),
        }
    return {
        "source": str(path),
        "scoring_type": "local_nli_claim_entailment_not_official_autoais",
        "model": str(model_path),
        "total_items": len(data),
        "total_claim_evidence_pairs": len(flat),
        "conditions": scored_by_condition,
        "pair_scores": scored["pairs"],
    }


def main() -> None:
    scifact = ROOT / "data" / "external_benchmarks" / "scifact_semantic_pilot_n40" / "scifact_semantic_pilot_outputs.json"
    alce = ROOT / "data" / "external_benchmarks" / "alce_official_pilot_n40_structural" / "alce_official_pilot_outputs.json"
    model = find_snapshot(r".cache\huggingface\hub\models--cross-encoder--nli-MiniLM2-L6-H768\snapshots\*")
    result = {
        "created_utc": "2026-07-26",
        "scifact_external_gold": scifact_metrics(scifact),
        "alce_full_local_nli": alce_entailment(alce, model),
        "scope_note": "SciFact uses the public dataset gold labels. ALCE uses a local cached NLI classifier as a complete claim-entailment audit; it is not labeled official AutoAIS because the official T5 AutoAIS checkpoint was not used.",
    }
    path = OUT / "external_semantic_completion.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(path)
    print(json.dumps({"scifact": result["scifact_external_gold"], "alce": {"conditions": result["alce_full_local_nli"]["conditions"], "pairs": result["alce_full_local_nli"]["total_claim_evidence_pairs"]}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
