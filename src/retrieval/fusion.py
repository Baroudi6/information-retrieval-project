from src.retrieval.bm25_search import BM25Search, load_corpus
from src.retrieval.dense_search import DenseSearch

RRF_K = 60  # standard RRF constant
DEPTH = 50  # how many results to take from each retriever before fusing


def rrf_fuse(rankings: list[list[dict]], k: int = RRF_K, top_n: int = 10) -> list[dict]:
    """Reciprocal Rank Fusion.

    rankings: one list per retriever, each ordered best-first, with items like
              {"doc_index": ..., "score": ...}. Only the order (rank) is used.
    Returns the top_n papers as {"doc_index": ..., "score": RRF score}.
    """
    fused: dict[int, float] = {}
    for ranking in rankings:
        for position, item in enumerate(ranking, start=1):  # position 1 = best
            idx = item["doc_index"]
            fused[idx] = fused.get(idx, 0.0) + 1.0 / (k + position)
    ordered = sorted(fused.items(), key=lambda pair: pair[1], reverse=True)
    return [{"doc_index": idx, "score": score} for idx, score in ordered[:top_n]]


def show(label: str, results: list[dict], docs: list[dict], n: int = 3) -> None:
    print(f"  {label}")
    if not results:
        print("    (no results)")
    for r in results[:n]:
        print(f"    {r['score']:.4f}  {docs[r['doc_index']]['title']}")


if __name__ == "__main__":
    docs = load_corpus("tests/sample_corpus.jsonl")
    bm25 = BM25Search(docs)
    dense = DenseSearch(docs, cache_path="tests/sample_embeddings.npy")

    queries = [
        "post-quantum signatures",
        "computing on encrypted data without decrypting it",
        "detecting attacks on a network",
        "intrusion detection",
    ]
    for q in queries:
        bm25_results = bm25.search(q, k=DEPTH)
        dense_results = dense.search(q, k=DEPTH)
        fused_results = rrf_fuse([bm25_results, dense_results], top_n=10)

        print(f"\nQuery: {q}")
        show("BM25 ", bm25_results, docs)
        show("Dense", dense_results, docs)
        show("FUSED", fused_results, docs)