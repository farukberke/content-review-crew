import re

from crewai.tools import tool

LONG_SENTENCE_WORDS = 20
ABSOLUTE_PHRASES = [
    "bütün", "tüm", "her", "herkes", "hiç", "hiçbir", "her zaman", "asla",
    "kesinlikle", "mutlaka", "artık", "tamamen", "hepsi",
    "all", "every", "everyone", "always", "never", "definitely", "nobody",
]


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]


@tool("count_words")
def count_words(text: str) -> str:
    """Counts words and sentences in the text and returns the average sentence length."""
    words = len(text.split())
    sentences = len(_sentences(text))
    average = words / sentences if sentences else 0
    return f"words={words}, sentences={sentences}, average_words_per_sentence={average:.1f}"


@tool("count_long_sentences")
def count_long_sentences(text: str) -> str:
    """Finds sentences longer than 20 words in the text."""
    long = [s for s in _sentences(text) if len(s.split()) > LONG_SENTENCE_WORDS]
    if not long:
        return f"No sentences longer than {LONG_SENTENCE_WORDS} words."
    return f"{len(long)} long sentence(s):\n" + "\n".join(f"- {s}" for s in long)


@tool("find_absolute_phrases")
def find_absolute_phrases(text: str) -> str:
    """Finds absolute words such as 'bütün', 'asla', 'artık', 'always' that make claims sound certain."""
    lowered = text.lower()
    found = [
        p for p in ABSOLUTE_PHRASES
        if re.search(rf"\b{re.escape(p)}\b", lowered)
    ]
    return "Absolute phrases: " + ", ".join(found) if found else "No absolute phrases found."
