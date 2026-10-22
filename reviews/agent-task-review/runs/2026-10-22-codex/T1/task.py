"""Create and search products using the official LanceDB documentation.

Sources (starting index: https://docs.lancedb.com/llms.txt):
https://docs.lancedb.com/quickstart.md
https://docs.lancedb.com/tables/create.md
https://docs.lancedb.com/search/filtering.md
https://docs.lancedb.com/search/vector-search.md
"""

from pathlib import Path

import lancedb
import pandas as pd


def main():
    products = pd.DataFrame(
        [
            (1, "Chef's knife", "kitchen", 45.0, [0.9, 0.1, 0.1, 0.0]),
            (2, "Cutting board", "kitchen", 25.0, [0.8, 0.2, 0.0, 0.1]),
            (3, "Cast-iron pan", "kitchen", 60.0, [0.7, 0.0, 0.3, 0.2]),
            (4, "Desk lamp", "office", 35.0, [0.9, 0.1, 0.0, 0.0]),
            (5, "Notebook", "office", 5.0, [0.1, 0.9, 0.1, 0.0]),
            (6, "Garden hose", "garden", 30.0, [0.0, 0.1, 0.9, 0.4]),
        ],
        columns=["id", "name", "category", "price", "vector"],
    )

    db = lancedb.connect(str(Path(__file__).resolve().parent / "lancedb_data"))
    # Overwrite makes this example repeatable with the same six input rows.
    table = db.create_table("products", data=products, mode="overwrite")
    results = (
        table.search([1.0, 0.0, 0.0, 0.0])
        .distance_type("l2")
        .where("category = 'kitchen' AND price < 50", prefilter=True)
        .limit(2)
        .to_pandas()
    )

    print("id  name           distance")
    for _, row in results.iterrows():
        print(f"{row['id']:2d}  {row['name']:<13}  {row['_distance']:.6f}")


if __name__ == "__main__":
    main()
