from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
df = pd.read_csv(ROOT / "dataset" / "papers.csv", keep_default_na=False)

print("Total papers:", len(df))

print("\n=== Papers per sub-topic ===")
print(df["subtopic"].value_counts())

print("\n=== Papers per length tier ===")
print(df["length"].value_counts())

print("\n=== Sub-topic x length tier ===")
print(pd.crosstab(df["subtopic"], df["length"], margins=True))

print("\n=== Papers per year ===")
print(df["published"].str[:4].value_counts().sort_index())

print("\n=== Pages ===")
print(df["pages"].describe()[["min", "max", "mean", "50%"]].round(1))

print("\n=== Average abstract length (words) ===")
print(round(df["abstract"].str.split().str.len().mean(), 1))

print("\n=== Example arXiv query ===")
print(df["search_query"].iloc[0])