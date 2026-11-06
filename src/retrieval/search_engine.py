from src.retrieval.bm25_search import BM25Search, load_corpus
from src.retrieval.dense_search import DenseSearch
from src.retrieval.fusion import rrf_fuse
from src.retrieval.query_handler import build_vocab, contains_phrase, process_query


class SearchEngine:
    def __init__(self, corpus_path, cache_path=None):
        self.docs = load_corpus(corpus_path)
        self.bm25 = BM25Search(self.docs)
        self.dense = DenseSearch(self.docs, cache_path=cache_path)
        self.vocab = build_vocab(self.docs)

    def search(self, query, mode="fused", k=10):
        q = process_query(query, self.vocab)
        if not q["text"]:
            return q, []
        n = len(self.docs)  # rank every paper, cut to k at the end
        if mode == "bm25":
            results = self.bm25.search(q["text"], k=n)
        elif mode == "dense":
            results = self.dense.search(q["text"], k=n)
        else:
            results = rrf_fuse([self.bm25.search(q["text"], k=n), self.dense.search(q["text"], k=n)], top_n=n)
        for p in q["phrases"]:
            results = [r for r in results if contains_phrase(self.docs[r["doc_index"]], p)]
        return q, results[:k]


if __name__ == "__main__":
    engine = SearchEngine("tests/sample_corpus.jsonl", cache_path="tests/sample_embeddings.npy")
    for query in [
        "homomorphic encryption",
        "HOMOMORPHIC Encryption",
        "homomorphc encrypton",
        "PQC signatures",
        "key exchange",
        '"key exchange"',
    ]:
        q, results = engine.search(query, k=3)
        print(f"\nQuery: {query}  ->  {q}")
        for r in results:
            print(f"   {r['score']:.4f}  {engine.docs[r['doc_index']]['title']}")