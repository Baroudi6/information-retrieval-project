import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
df = pd.read_csv(ROOT / "dataset" / "papers.csv", keep_default_na=False)

out = ROOT / "data" / "processed" / "corpus.jsonl"
out.parent.mkdir(parents=True, exist_ok=True)

with open(out, "w", encoding="utf-8") as f:
    for r in df.to_dict("records"):
        abstract = " ".join(r["abstract"].split())
        f.write(json.dumps({
            "id": r["arxiv_id"],
            "arxiv_id": r["arxiv_id"],
            "title": r["title"],
            "text": abstract,
            "abstract": abstract,
            "arxiv_link": r["arxiv_link"],
            "subtopic": r["subtopic"],
            "length": r["length"],
            "published": r["published"],
        }, ensure_ascii=False) + "\n")

print("Wrote", len(df), "papers to", out)