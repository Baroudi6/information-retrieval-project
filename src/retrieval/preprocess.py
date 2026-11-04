import re
from functools import lru_cache

import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

# Download NLTK's stopword list the first time only (needs internet)
try:
    stopwords.words("english")
except LookupError:
    nltk.download("stopwords", quiet=True)

# NLTK's English stopwords + a few filler words common in paper abstracts
STOPWORDS = set(stopwords.words("english")) | {"using", "use", "used", "via", "also", "paper"}

_stemmer = SnowballStemmer("english")


@lru_cache(maxsize=None)
def stem(word: str) -> str:
    """Reduce a word to its stem: encryption / encrypted / encrypts -> encrypt."""
    return _stemmer.stem(word)


def tokenize(text: str) -> list[str]:
    """Lowercase -> split into words -> remove stopwords -> stem."""
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [stem(t) for t in tokens if t not in STOPWORDS]


if __name__ == "__main__":
    print(tokenize("Post-Quantum Key Exchange for the IoT"))
    print(tokenize("Homomorphic encryption"))
    print(tokenize("files are encrypted"))