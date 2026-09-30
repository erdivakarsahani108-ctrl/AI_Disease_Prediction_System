"""Language detection & normalization for EN / Hindi / Hinglish / Bhojpuri."""
from __future__ import annotations

import re
from typing import Tuple

try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0
    HAS_LANGDETECT = True
except ImportError:
    HAS_LANGDETECT = False


# Simple Devanagari detector
DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")

# Common Hinglish / Roman Hindi markers
HINGLISH_MARKERS = {
    "hai", "hain", "kya", "nahi", "nahin", "bahut", "thoda", "zyada", "kam",
    "dard", "bukhar", "khansi", "thakaan", "pet", "sir", "gale", "saans",
    "dawai", "doctor", "ilaaj", "bimari", "tabiyat", "theek", "kharab",
    "mujhe", "mere", "meri", "aapka", "karke", "batao", "samjhao",
}

BHOJPURI_MARKERS = {
    "ba", "baate", "hamar", "tohara", "ka", "ke", "na", "ho", "raha",
    "jila", "bujha", "suni", "bata", "kaise", "kahan",
}


def detect_language(text: str) -> str:
    """
    Returns one of: en, hi, hinglish, bhojpuri
    """
    text = text.strip()
    if not text:
        return "en"

    # Devanagari → Hindi
    if DEVANAGARI_RE.search(text):
        return "hi"

    tokens = set(re.findall(r"[a-zA-Z]+", text.lower()))
    hinglish_hits = len(tokens & HINGLISH_MARKERS)
    bhojpuri_hits = len(tokens & BHOJPURI_MARKERS)

    if bhojpuri_hits >= 2:
        return "bhojpuri"
    if hinglish_hits >= 2:
        return "hinglish"

    if HAS_LANGDETECT:
        try:
            lang = detect(text)
            if lang == "hi":
                return "hi"
            if lang in ("en", "id", "tl"):  # sometimes misdetects
                return "en"
        except Exception:
            pass

    return "en"


def normalize_query(text: str, lang: str) -> str:
    """Light normalization for better retrieval."""
    text = text.strip()
    # collapse multiple spaces
    text = re.sub(r"\s+", " ", text)
    return text


def get_language_name(code: str) -> str:
    return {
        "en": "English",
        "hi": "Hindi",
        "hinglish": "Hinglish / Roman Hindi",
        "bhojpuri": "Bhojpuri",
    }.get(code, code)
