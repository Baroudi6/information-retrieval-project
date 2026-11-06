# arXiv Cybersecurity Literature Retrieval

A hybrid information retrieval system over arXiv papers in **cs.CR (Cryptography and Security)**. It combines lexical search (BM25) with dense semantic search, fuses the two rankings, and exposes the result through a simple GUI.

Built as a course project (Information Retrieval).

## Features

- **Corpus builder** that collects cs.CR papers from the arXiv API and records metadata for each one
- **BM25 retriever** for exact-term matching
- **Dense retriever** using sentence embeddings for semantic matching
- **Fusion** of both rankings into one hybrid result list
- **Query handling** to clean and prepare user queries
- **GUI** for entering queries and browsing results

## Corpus

| Property | Value |
|---|---|
| Source | arXiv API |
| Category | `cs.CR` |
| Submission dates | 2020-01-01 to 2026-11-03 |
| Size | 400 papers (100 per sub-topic) |
| Indexed fields | Title + abstract |

Papers are collected across four sub-topics:

1. Cryptographic Algorithms and Protocols
2. Network and System Security
3. Post-Quantum Cryptography
4. Privacy-Preserving Cryptography

Each paper is also labeled **Short / Medium / Long** based on its page count. PDFs are downloaded only to count pages and are not indexed.

### Collection details

Each topic has four search keywords. Queries match the title or abstract and are restricted to `cs.CR` and the date range. Topics are processed from most specific to most generic (post-quantum and privacy-preserving first), so broad keywords like "encryption" do not steal papers that belong to a more specific topic. Progress is saved after every paper, so collection can be stopped and resumed.

## Project structure

```
.
├── src/
│   ├── corpus/
│   │   └── collect_papers.py    # arXiv collection script
│   ├── retrieval/
│   │   ├── preprocess.py        # text cleaning
│   │   ├── bm25_search.py       # lexical retriever
│   │   ├── dense_search.py      # semantic retriever
│   │   ├── fusion.py            # hybrid ranking
│   │   ├── query_hndler.py      # query handling
│   │   └── search_engine.py     # ties retrievers together
│   └── gui/                     # user interface
├── data/                        # raw and processed data
├── reports/                     # project reports
├── tests/
├── ai-logs/                     # AI-assistance logs
└── requirements.txt
```

## Setup

```bash
conda create -n arxiv-ir python=3.11
conda activate arxiv-ir
pip install -r requirements.txt
```

## Usage

### 1. Build the corpus

Run from the repository root:

```bash
python src/corpus/collect_papers.py
```

This writes the PDFs, extracted text, and a `papers.csv` metadata file. Collection takes a while because requests to arXiv are rate-limited. Re-running resumes from `papers.csv`.

PDFs and extracted text are listed in `.gitignore` and are not committed.

### 2. Run the search system

Launch the GUI from the entry point in `src/gui/`, then enter a query to see hybrid BM25 + dense results.

## How retrieval works

1. The query is cleaned and normalized.
2. BM25 scores documents on term overlap.
3. The dense retriever scores documents by embedding similarity.
4. The two ranked lists are fused into a single ranking.
5. Results are shown with title, abstract, sub-topic, and length category.

## Data and licensing

Paper metadata and abstracts come from the [arXiv API](https://info.arxiv.org/help/api/index.html). Individual papers keep their own licenses; this repository does not redistribute PDFs.

## AI assistance

AI assistance used during development is documented in [`ai-logs/`](ai-logs/).

## Authors
- Omar Baroudi
- Abdulrahman Al-Qurneh
