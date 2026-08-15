import re
from typing import Dict

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
EN_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*")

# Roughly maps Chinese characters to English-word-equivalent length so mixed
# Chinese/English drafts are measured consistently across generation and review.
CJK_TO_WORD_EQ = 0.8


def analyze_text_length(text: str) -> Dict[str, int]:
    chinese_chars = len(CJK_RE.findall(text or ""))
    english_words = len(EN_WORD_RE.findall(text or ""))
    word_equivalent = english_words + int(round(chinese_chars * CJK_TO_WORD_EQ))
    return {
        "chinese_chars": chinese_chars,
        "english_words": english_words,
        "word_equivalent": word_equivalent,
    }


def count_word_equivalent(text: str) -> int:
    return analyze_text_length(text)["word_equivalent"]


def describe_text_length(text: str) -> str:
    metrics = analyze_text_length(text)
    return (
        f"{metrics['word_equivalent']} word-equivalent "
        f"({metrics['english_words']} English words, "
        f"{metrics['chinese_chars']} Chinese chars)"
    )


def estimate_pages(text: str) -> float:
    metrics = analyze_text_length(text)
    return max(metrics["english_words"] / 300.0, metrics["chinese_chars"] / 800.0, 0.0)
