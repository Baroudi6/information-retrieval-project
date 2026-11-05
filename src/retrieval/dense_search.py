import os

import numpy as np
from sentence_transformers import SentenceTransformer

from src.retrieval.bm25_search import load_corpus

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class DenseSearch:
    def __init__(self, docs: list[dict], model_name: str = MODEL_NAME, cache_path: str | None = None):
        self.docs = docs
        self.model = SentenceTransformer(model_name)

        embeddings = None
        if cache_path and os.path.exists(cache_path):
            embeddings = np.load(cache_path)
            if embeddings.shape[0] != len(docs):  # corpus size changed -> cache is stale
                embeddings = None

        if embeddings is None:
            texts = [d["title"] + ". " + d["text"] for d in docs]
            embeddings = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
            if cache_path:
                np.save(cache_path, embeddings)

        self.embeddings = embeddings  # shape: (num_docs, 384), unit-length vectors

    def search(self, query: str, k: int = 10) -> list[dict]:
        """Return the top-k papers as {"doc_index": position in corpus, "score": cosine similarity}."""
        q = self.model.encode([query], normalize_embeddings=True)[0]
        scores = self.embeddings @ q  # unit vectors -> dot product = cosine similarity
        ranked = np.argsort(-scores)[:k]
        return [{"doc_index": int(i), "score": float(scores[i])} for i in ranked]


if __name__ == "__main__":
    docs = load_corpus("tests/sample_corpus.jsonl")
    engine = DenseSearch(docs, cache_path="tests/sample_embeddings.npy")
    for q in [
        "post-quantum signatures",
        "computing on encrypted data without decrypting it",
        "detecting attacks on a network",
    ]:
        print(f"\nQuery: {q}")
        for r in engine.search(q, k=3):
            print(f"  {r['score']:.3f}  {docs[r['doc_index']]['title']}")