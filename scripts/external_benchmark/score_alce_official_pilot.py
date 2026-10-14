"""Score the ALCE official-data pilot with the repository's published rules.

The answer metrics below mirror the formulas in ALCE/eval.py. AutoAIS is not
silently replaced: it needs the very large official NLI checkpoint, so this
script reports marker/index diagnostics separately as an adapter metric.
"""

from __future__ import annotations

import json
import re
import argparse
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ALCE_EVAL = PROJECT_ROOT / "external" / "github_learned_projects" / "ALCE" / "eval.py"
DEFAULT_DIR = PROJECT_ROOT / "data" / "external_benchmarks" / "alce_official_pilot_n1"


def normalize_answer(text: str) -> str:
    text = re.sub(r"\b(a|an|the)\b", " ", text.lower())
    text = "".join(ch for ch in text if ch not in set("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"))
    return " ".join(text.split())


def exact_presence(short_answers, context: str) -> bool:
    normalized = normalize_answer(context)
    return any(normalize_answer(ans) in normalized for ans in short_answers)


def remove_citations(text: str) -> str:
    return re.sub(r"\[\d+", "", re.sub(r" \[\d+", "", text)).replace(" |", "").replace("]", "")


def official_normalized_output(text: str) -> str:
    # Mirrors ALCE/eval.py main: trim, keep first line, then remove citations
    # for non-AutoAIS answer metrics.
    return remove_citations(text.strip().split("\n")[0].replace("<|im_end|>", ""))


def qampari_metrics(item):
    preds = [normalize_answer(x.strip()) for x in official_normalized_output(item["output"]).rstrip(".").rstrip(",").split(",")]
    preds = [p for p in preds if p]
    answers = [[normalize_answer(x) for x in ans] for ans in item["answers"]]
    flat = [x for group in answers for x in group]
    precision = sum(p in flat for p in preds) / len(preds) if preds else 0.0
    recall = sum(any(x in preds for x in group) for group in answers) / len(answers)
    recall_top5 = min(5, sum(any(x in preds for x in group) for group in answers)) / min(5, len(answers))
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    f1_top5 = 2 * precision * recall_top5 / (precision + recall_top5) if precision + recall_top5 else 0.0
    return {"num_preds": len(preds), "qampari_prec": precision, "qampari_rec": recall,
            "qampari_rec_top5": recall_top5, "qampari_f1": f1, "qampari_f1_top5": f1_top5}


def citation_diagnostics(item, top_k: int = 5):
    markers = [int(x) for x in re.findall(r"\[(\d+)\]", item["output"])]
    valid = [x for x in markers if 1 <= x <= top_k]
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", item["output"]) if s.strip()]
    cited_sentences = sum(bool(re.search(r"\[\d+\]", s)) for s in sentences)
    return {
        "citation_markers": len(markers),
        "valid_top5_markers": len(valid),
        "citation_index_validity": len(valid) / len(markers) if markers else 0.0,
        "sentence_citation_coverage": cited_sentences / len(sentences) if sentences else 0.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_DIR)
    args = parser.parse_args()
    input_path = args.run_dir / "alce_official_pilot_outputs.json"
    output_path = args.run_dir / "metrics.json"
    records = json.loads(input_path.read_text(encoding="utf-8"))
    grouped = defaultdict(list)
    for item in records:
        grouped[(item["dataset"], item["condition"])].append(item)

    report = {
        "official_source": str(ALCE_EVAL),
        "metric_note": "Answer metrics mirror ALCE eval.py; citation diagnostics are adapter metrics. AutoAIS was not run because its official checkpoint was not downloaded.",
        "groups": {},
    }
    for (dataset, condition), items in sorted(grouped.items()):
        diag = [citation_diagnostics(x) for x in items]
        row = {
            "n": len(items),
            "avg_words": sum(len(official_normalized_output(x["output"]).split()) for x in items) / len(items),
            "citation_index_validity": sum(x["citation_index_validity"] for x in diag) / len(diag),
            "sentence_citation_coverage": sum(x["sentence_citation_coverage"] for x in diag) / len(diag),
        }
        if dataset == "asqa":
            per_item = [sum(exact_presence(q["short_answers"], official_normalized_output(x["output"])) for q in x["qa_pairs"]) / len(x["qa_pairs"]) for x in items]
            row["str_em"] = 100 * sum(per_item) / len(per_item)
            row["str_hit"] = 100 * sum(v == 1 for v in per_item) / len(per_item)
        else:
            qm = [qampari_metrics(x) for x in items]
            for key in ("num_preds", "qampari_prec", "qampari_rec", "qampari_rec_top5", "qampari_f1", "qampari_f1_top5"):
                row[key] = sum(x[key] for x in qm) / len(qm)
                if key != "num_preds":
                    row[key] *= 100
        report["groups"][f"{dataset}/{condition}"] = row

    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"WROTE {output_path}")


if __name__ == "__main__":
    main()
