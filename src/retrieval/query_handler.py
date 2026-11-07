import re
from difflib import get_close_matches


KNOWN_TYPOS = {}

ABBREVIATIONS = {
    # post-quantum & public-key crypto
    "pqc": "post-quantum cryptography",
    "kem": "key encapsulation mechanism",
    "lwe": "learning with errors",
    "ecc": "elliptic curve cryptography",
    "ecdsa": "elliptic curve digital signature algorithm",
    "rsa": "rivest shamir adleman",
    "pki": "public key infrastructure",
    "nist": "national institute of standards and technology",
    # privacy-preserving crypto
    "fhe": "fully homomorphic encryption",
    "mpc": "secure multi-party computation",
    "smpc": "secure multi-party computation",
    "zkp": "zero-knowledge proof",
    "pir": "private information retrieval",
    "psi": "private set intersection",
    "ot": "oblivious transfer",
    "dp": "differential privacy",
    "abe": "attribute-based encryption",
    "ibe": "identity-based encryption",
    # algorithms & protocols
    "aes": "advanced encryption standard",
    "mac": ["message authentication code", "media access control"],
    "hmac": "hash-based message authentication code",
    "prf": "pseudorandom function",
    "tls": "transport layer security",
    "ssl": "secure sockets layer",
    "vpn": "virtual private network",
    # network & system security
    "ids": "intrusion detection system",
    "ips": "intrusion prevention system",
    "dos": "denial of service",
    "ddos": "distributed denial of service",
    "mitm": "man-in-the-middle",
    "apt": "advanced persistent threat",
    "xss": "cross-site scripting",
    "sqli": "sql injection",
    "cve": "common vulnerabilities and exposures",
    "tee": "trusted execution environment",
    "sgx": "software guard extensions",
    "iot": "internet of things",
    # general
    "ml": "machine learning",
    "dl": "deep learning",
    "llm": "large language model",
    "nlp": "natural language processing",
    "ai": "artificial intelligence",
}

def words(text):
    """Lowercase and split into words (no stemming, no stopword removal)."""
    return re.findall(r"[a-z0-9]+", text.lower())


def build_vocab(docs):
    """Every word that appears in the corpus = the spell checker's dictionary."""
    vocab = set()
    for d in docs:
        vocab.update(words(d["title"] + " " + d["text"]))
    return vocab


def correct(word, vocab):

    if word in KNOWN_TYPOS:
        return KNOWN_TYPOS[word]

    if word in ABBREVIATIONS or len(word) <= 3:
        return word

    if word in vocab:
        return word

    match = get_close_matches(word, vocab, n=1, cutoff=0.8)

    return match[0] if match else word

def process_query(query, vocab):
    phrases = [p for p in query.split('"')[1::2] if p.strip()]
    tokens = [correct(w, vocab) for w in words(query)]
    
    expansions = []
    for w in tokens:
        if w in ABBREVIATIONS:
            full = ABBREVIATIONS[w]
            expansions += full if isinstance(full, list) else [full]
            
    return {
        "text": " ".join(tokens + expansions),
        "phrases": [" ".join(correct(w, vocab) for w in words(p)) for p in phrases],
    }


def contains_phrase(doc, phrase):
    """True if the phrase appears in the paper as whole words, in this order."""
    doc_text = " " + " ".join(words(doc["title"] + " " + doc["text"])) + " "
    return " " + phrase + " " in doc_text
