import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import gradio as gr
import html
from src.retrieval.search_engine import SearchEngine

search_engine = SearchEngine(
    ROOT / "data" / "processed" / "corpus.jsonl",        # <- path to your real corpus file
    cache_path=ROOT / "data" / "processed" / "embeddings.npy",  # <- path to your embeddings file, if you have one
)
docs = search_engine.docs
def search_gui(query, mode):
    if not query.strip():
        return "Please enter a query."

    processed, results = search_engine.search(
        query, mode=mode, k=10
    )

    output = (
        "<h3>Processed Query: "
        + html.escape(processed["text"])
        + "</h3>"
    )

    if not results:
        return output + "<p>No papers found.</p>"

    for rank, result in enumerate(results, 1):
        paper = docs[result["doc_index"]]

        title = html.escape(paper["title"])
        text = " ".join(paper["text"].split())
        snippet = html.escape(text[:200])
        link = html.escape(
            paper["arxiv_link"], quote=True
        )

        output += f"""
        <div style="padding:15px; border-bottom:1px solid #ccc">
            <h3>{rank}. {title}</h3>
            <p>{snippet}...</p>
            <p><b>Ranking Score:</b> {result['score']:.5f}</p>
            <a href="{link}" target="_blank">View Paper on arXiv</a>
        </div>
        """

    return output


demo = gr.Interface(
    fn=search_gui,
    inputs=[
        gr.Textbox(
            label="Search Query",
            placeholder="Enter your search..."
        ),
        gr.Dropdown(
            choices=["fused", "bm25", "dense"],
            value="fused",
            label="Search Model"
        )
    ],
    outputs=gr.HTML(label="Search Results"),
    title="Cryptography & Security Search Engine",
    description="Search 400 arXiv research papers",
    flagging_mode="never"
)

demo.launch(
    inline=False,
    inbrowser=False,
    share=False
)