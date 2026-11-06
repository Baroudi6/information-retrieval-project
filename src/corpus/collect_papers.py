import json
import time
from pathlib import Path

import arxiv
import certifi
import pandas as pd
import pymupdf
import requests

TARGET = 100

# Dataset folders
dataset = Path("dataset")
pdf_folder = dataset / "pdfs"
text_folder = dataset / "texts"

pdf_folder.mkdir(parents=True, exist_ok=True)
text_folder.mkdir(parents=True, exist_ok=True)

csv_path = dataset / "papers.csv"

# Fixed arXiv submission date range
DATE_START = "202001010000"
DATE_END = "202611032359"

# Four sub-topics
# Four sub-topics (ordered from most specific to most generic)
topics = {
    "Post-Quantum Cryptography": [
        "post-quantum cryptography",
        "lattice-based cryptography",
        "quantum resistant",
        "key encapsulation"
    ],

    "Privacy-Preserving Cryptography": [
        "homomorphic encryption",
        "zero knowledge proof",
        "secure multiparty computation",
        "private information retrieval"
    ],

    "Cryptographic Algorithms": [
        "encryption",
        "digital signature",
        "hash function",
        "cryptographic protocol"
    ],

    "Network and System Security": [
        "network security",
        "intrusion detection",
        "authentication",
        "access control"
    ]
}

# arXiv API client
client = arxiv.Client(
    page_size=50,
    delay_seconds=3,
    num_retries=3
)

# Save collection configuration
config = {
    "category": "cs.CR",
    "target_per_topic": TARGET,
    "date_start_utc": DATE_START,
    "date_end_utc": DATE_END,
    "topics": topics
}

(dataset / "collection_config.json").write_text(
    json.dumps(config, indent=2),
    encoding="utf-8"
)

print("Dataset configuration ready!")

# Load previous progress if it exists
if csv_path.exists():
    records = pd.read_csv(
        csv_path,
        keep_default_na=False
    ).to_dict("records")
else:
    records = []

seen_ids = {
    str(row["arxiv_id"]) for row in records
}

# HTTPS session
session = requests.Session()
session.verify = certifi.where()
session.headers.update({
    "User-Agent": "StudentResearchCorpus/1.0"
})


def download_pdf(url, path):
    """Download and validate a PDF safely."""

    for attempt in range(3):
        try:
            with session.get(
                url,
                stream=True,
                timeout=90
            ) as response:

                response.raise_for_status()

                with open(path, "wb") as f:
                    for chunk in response.iter_content(
                        chunk_size=65536
                    ):
                        if chunk:
                            f.write(chunk)

            # Check PDF signature
            with open(path, "rb") as f:
                if f.read(4) != b"%PDF":
                    raise ValueError("Invalid PDF")

            return True

        except Exception as e:
            path.unlink(missing_ok=True)
            print("Download error:", str(e)[:100])

            if attempt < 2:
                time.sleep(5 * (attempt + 1))

    return False


def get_length(pages):
    """Classify paper based on page count.

    Covers every page count (no gap at 6 pages):
      Short  : 6 pages or fewer
      Medium : 7-9 pages
      Long   : 10 pages or more
    Adjust the boundaries here if your assignment defines them differently.
    """

    if pages <= 6:
        return "Short"
    elif pages <= 9:
        return "Medium"
    else:
        return "Long"


def save_progress():
    """Save collected metadata to CSV."""

    pd.DataFrame(records).to_csv(
        csv_path,
        index=False
    )


# Collect papers for each topic
for topic, keywords in topics.items():

    count = sum(
        r["subtopic"] == topic for r in records
    )

    print("\n" + "=" * 55)
    print("TOPIC:", topic)
    print("Already collected:", count)
    print("=" * 55)

    if count >= TARGET:
        continue

    # Search each keyword separately
    for keyword in keywords:

        if count >= TARGET:
            break

        # Match title or abstract only (not authors/comments/journal refs)
        query = (
            f'cat:cs.CR AND (ti:"{keyword}" OR abs:"{keyword}") '
            f'AND submittedDate:[{DATE_START} TO {DATE_END}]'
        )

        print("\nSearching:", keyword)

        search = arxiv.Search(
            query=query,
            max_results=300,
            sort_by=arxiv.SortCriterion.Relevance
        )

        try:
            for paper in client.results(search):

                if count >= TARGET:
                    break

                paper_id = paper.get_short_id()

                # Prevent duplicates
                if paper_id in seen_ids:
                    continue

                # Require cs.CR category
                if "cs.CR" not in paper.categories:
                    continue

                # Enforce publication date range
                date_str = paper.published.date().isoformat()

                if not (
                    "2020-01-01" <= date_str <= "2026-11-03"
                ):
                    continue

                safe_id = paper_id.replace("/", "_")

                pdf_path = (
                    pdf_folder / f"{safe_id}.pdf"
                )

                text_path = (
                    text_folder / f"{safe_id}.txt"
                )

                # Respectful PDF request spacing
                time.sleep(3.2)

                success = download_pdf(
                    paper.pdf_url,
                    pdf_path
                )

                if not success:
                    continue

                try:
                    with pymupdf.open(pdf_path) as doc:
                        pages = len(doc)

                        content = "\n".join(
                            page.get_text()
                            for page in doc
                        )

                    # Skip documents with almost no text
                    if len(content.strip()) < 500:
                        pdf_path.unlink(missing_ok=True)
                        continue

                    length = get_length(pages)

                    # Save extracted full text
                    text_path.write_text(
                        content,
                        encoding="utf-8"
                    )

                    record = {
                        "arxiv_id": paper_id,
                        "title": paper.title,
                        "arxiv_link": paper.entry_id,
                        "pdf_url": paper.pdf_url,
                        "subtopic": topic,
                        "published": date_str,
                        "pages": pages,
                        "length": length,
                        "abstract": paper.summary,
                        "text_path": str(text_path),
                        "pdf_path": str(pdf_path),
                        "search_query": query
                    }

                    records.append(record)
                    seen_ids.add(paper_id)

                    count += 1

                    # Save progress after each paper
                    save_progress()

                    print(
                        f"[{count}/{TARGET}]",
                        paper.title[:55],
                        f"({pages} pages)"
                    )

                except Exception as e:
                    print("Processing error:", e)
                    pdf_path.unlink(missing_ok=True)
                    text_path.unlink(missing_ok=True)

        except Exception as e:
            print("Search error:", e)

    print(f"\nFinished {topic}: {count}/{TARGET}")

print("\nCOLLECTION FINISHED")
print("Total saved papers:", len(records))