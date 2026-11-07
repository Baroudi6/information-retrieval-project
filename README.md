# arXiv Cryptography & Security Search Engine

A hybrid information retrieval system over **400 arXiv papers** from **cs.CR (Cryptography and Security)**. It combines lexical search (BM25) with dense semantic search, fuses the two rankings with Reciprocal Rank Fusion, and serves the results through a Gradio web interface.

Built as an Information Retrieval course project.

## Features

- **Three search modes:** `bm25` (exact terms), `dense` (meaning), and `fused` (both, combined with RRF)
- **Typo correction:** query words are auto-corrected to the closest vocabulary word when the similarity is above 80%
- **Phrase search:** wrap words in quotes (`"key exchange"`) to keep only papers that contain that exact phrase
- **Case-insensitive queries:** `HOMOMORPHIC Encryption` and `homomorphic encryption` return the same results
- **Embedding cache:** document embeddings are computed once and reused on later runs
- **Web GUI:** search box, model selector, ranked results with snippet, score, and arXiv link

## Corpus

| Property | Value |
|---|---|
| Source | arXiv API |
| Category | `cs.CR` |
| Submission dates | 2020-01-01 to 2026-11-03 |
| Size | 400 papers (100 per sub-topic) |
| Indexed fields | Title + abstract |

The corpus covers four sub-topics:

| Sub-topic | Search keywords |
|---|---|
| Post-Quantum Cryptography | post-quantum cryptography, lattice-based cryptography, quantum resistant, key encapsulation |
| Privacy-Preserving Cryptography | homomorphic encryption, zero knowledge proof, secure multiparty computation, private information retrieval |
| Cryptographic Algorithms | encryption, digital signature, hash function, cryptographic protocol |
| Network and System Security | network security, intrusion detection, authentication, access control |

Each paper is also labeled **Short** (6 pages or fewer), **Medium** (7–9), or **Long** (10 or more) by page count.

### How the corpus was collected

- Queries match the **title or abstract** only and are restricted to `cs.CR` and the date range.
- Topics are collected from **most specific to most generic**, so broad keywords like "encryption" don't take papers that belong to a more specific topic such as homomorphic encryption.
- Duplicate papers are skipped, PDFs are validated, and papers with almost no extractable text are dropped.
- Progress is saved after every paper, so collection can be stopped and resumed.

## Project structure

```
.
├── src/
│   ├── corpus/
│   │   ├── collect_papers.py    # downloads papers + metadata from arXiv
│   │   └── make_corpus.py       # converts papers.csv into corpus.jsonl
│   ├── retrieval/
│   │   ├── preprocess.py        # text cleaning
│   │   ├── bm25_search.py       # BM25 retriever + corpus loader
│   │   ├── dense_search.py      # embedding-based retriever
│   │   ├── fusion.py            # Reciprocal Rank Fusion
│   │   ├── query_handler.py     # query processing, typo correction, phrases
│   │   └── search_engine.py     # combines everything behind one search()
│   └── gui/
│       └── gui_ir.py            # Gradio web interface
├── dataset/                     # papers.csv + collection_config.json
├── data/processed/              # corpus.jsonl + embeddings cache
├── tests/                       # small sample corpus for quick tests
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

Run every command from the repository root.

### 1. Collect papers (optional, slow)

```bash
python src/corpus/collect_papers.py
```

Writes `dataset/papers.csv` plus PDFs and extracted text. arXiv requests are rate-limited, so this takes a few hours. Re-running resumes where it stopped. PDFs and text files are git-ignored.

### 2. Build the search corpus

```bash
python src/corpus/make_corpus.py
```

Converts `dataset/papers.csv` into `data/processed/corpus.jsonl` (one paper per line: title, abstract, link, sub-topic, length).

### 3. Launch the search engine

```bash
python src/gui/gui_ir.py
```

Open **http://127.0.0.1:7860** in your browser. The first launch downloads the embedding model and builds the embeddings cache, which takes a few minutes. Later launches are fast. Press `Ctrl+C` in the terminal to stop.

## How retrieval works

1. **Query processing:** the query is lowercased and tokenized, misspelled words are corrected against the corpus vocabulary, and quoted phrases are extracted.
2. **BM25:** scores papers by term overlap with the query.
3. **Dense retrieval:** scores papers by cosine similarity between query and document embeddings.
4. **Fusion:** in `fused` mode, the BM25 and dense rankings are combined with **Reciprocal Rank Fusion (RRF)**, which rewards papers ranked highly by either model.
5. **Phrase filter:** if the query has quoted phrases, only papers containing them are kept.
6. **Results:** the top 10 papers are shown with title, snippet, score, and arXiv link.

## Example queries

| Query | What it shows |
|---|---|
| `lattice-based key encapsulation` | keyword match, BM25 is strong |
| `computing on data without decrypting it` | paraphrase, dense finds homomorphic encryption |
| `homomorphc encrypton` | typo correction |
| `"key exchange"` | exact phrase filter |
| `post-quantum homomorphic encryption` | query across two sub-topics |

## Data and licensing

Paper metadata and abstracts come from the [arXiv API](https://info.arxiv.org/help/api/index.html). Each paper keeps its own license. This repository does not redistribute PDFs.

## AI assistance

AI assistance used during development is documented in [`ai-logs/`](ai-logs/).

## Authors
- Omar Baroudi
- Abdelrahman Alqurneh
