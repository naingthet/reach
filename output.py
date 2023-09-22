from google.cloud import bigquery
from pathlib import Path
import os
from pprint import pprint
import json

UPLOAD_BATCH_SIZE = int(os.environ.get("UPLOAD_BATCH_SIZE", 100))
output_dir = Path("./output")
client = bigquery.Client()

table_id = "prod_indra.reach_results"

def _join_json_files(prefix, clear=False):
    """Join different REACH output JSON files into a single JSON object.

    The output of REACH is broken into three files that need to be joined
    before processing. Specifically, there will be three files of the form:
    `<prefix>.uaz.<subcategory>.json`.

    Parameters
    ----------
    prefix : str
        The absolute path up to the extensions that reach will add.
    clear : bool
        Default False - if True, delete the files as soon as they are
        loaded.

    Returns
    -------
    json_obj : dict
        The result of joining the files, keyed by the three subcategories.
    """
    filetype_list = ['entities', 'events', 'sentences']
    json_dict = {}
    try:
        for filetype in filetype_list:
            fname = "output/" + prefix + '.uaz.' + filetype + '.json'
            with open(fname, 'rt') as f:
                json_dict[filetype] = json.load(f)
            if clear:
                os.remove(fname)
    except FileNotFoundError as e:
        pass
    return {
        "pubmed_id": prefix,
        "reach_results": json.dumps(json_dict)
    }

def get_output_files(limit):
    output_filenames = os.listdir("./output")
    output_filenames = [filename for filename in output_filenames if filename.endswith(".json")]
    print(f"{len(output_filenames):,} files found.")
    if len(output_filenames) == 0:
        return

    output_filenames = output_filenames[:limit]
    output_prefixes = list(set([filename.split(".")[0] for filename in output_filenames]))
    joined_jsons = []
    for prefix in output_prefixes:
        joined_jsons.append(_join_json_files(prefix, clear=True))
    errors = client.insert_rows_json(table_id, joined_jsons)
    if not errors:
        print(f"{len(joined_jsons):,} new rows have been added.")
        papers_dir = Path("./papers")
        for filename in output_filenames:
            pmid = filename.split(".")[0]
            try:
                os.remove(papers_dir /  f"{pmid}.txt")
            except FileNotFoundError as e:
                pass

if __name__ == "__main__":
    while True:
        get_output_files(limit=UPLOAD_BATCH_SIZE)
