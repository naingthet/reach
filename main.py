from google.cloud import bigquery
from pathlib import Path
import os

papers_dir = Path("./papers")
client = bigquery.Client()

table_id = "prod_indra.reach_abstracts_to_read"
LIMIT = os.environ.get("LIMIT", 1000)


def load_abstracts_to_files(limit):
    print(f"Loading {limit:,} abstracts to files...")
    rows = (
        client.query(f"SELECT * FROM {table_id} limit {limit}")
        .result()
        .to_dataframe()
        .to_dict(orient="records")
    )
    for row in rows:
        filepath = papers_dir / f"{row['pubmed_id']}.txt"
        with open(filepath, "w") as f:
            f.write(row["abstract"])

if __name__ == "__main__":
    load_abstracts_to_files(limit=LIMIT)
    print("Done.")
