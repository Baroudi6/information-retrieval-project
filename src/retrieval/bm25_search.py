import json

from rank_bm25 import BM25Okapi

from src.retrieval.preprocess import tokenize


def load_corpus(path: str):
    """Read a JSONL corpus: one paper (a dict) per line."""
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


class BM25Search:
    def __init__(self, docs: list[dict]):
        self.docs = docs
        # Index title + abstract together
        corpus_tokens = [tokenize(d["title"] + " " + d["text"]) for d in docs]
        self.index = BM25Okapi(corpus_tokens)

    def search(self, query: str, k: int = 10) -> list[dict]:
        """Return the top-k papers as {"doc_index": position in corpus, "score": BM25 score}."""
        scores = self.index.get_scores(tokenize(query))
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        results = []                          
        for i in ranked[:k]:                  
            if scores[i] > 0:                
                results.append(               
                    {"doc_index": i, "score": float(scores[i])}
        )
        return results                        


if __name__ == "__main__":
    docs = load_corpus("data/processed/corpus.jsonl")
    engine = BM25Search(docs)
    for q in ["post-quantum signatures", "homomorphic encryption", "intrusion detection"]:
        print(f"\nQuery: {q}")
        for r in engine.search(q, k=3):
            print(f"  {r['score']:.3f}  {docs[r['doc_index']]['title']}")