import re

STOPWORDS = {
    "a", "an", "the", "of", "for", "and", "or", "in", "on", "to", "from", "with",
    "by", "at", "as", "is", "are", "was", "were", "be", "been", "this", "that",
    "these", "those", "it", "its", "we", "our", "us", "can", "which", "using",
    "use", "used", "via", "into", "than", "such", "also", "not", "has", "have",
}


def tokenize(text: str) -> list[str]:
    """Lowercase, split into word tokens, and remove stopwords.

    Hyphenated terms are split (post-quantum -> post, quantum), so a query
    for just "quantum" still matches papers about post-quantum cryptography.
    """
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [t for t in tokens if t not in STOPWORDS]


if __name__ == "__main__":
    print(tokenize("Post-Quantum Key Exchange for the IoT"))