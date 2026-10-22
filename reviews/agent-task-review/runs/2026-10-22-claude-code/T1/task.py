import lancedb
import pandas as pd

# Connect to a local database folder (created if it doesn't exist).
db = lancedb.connect("ex_lancedb")

df = pd.DataFrame(
    [
        {"id": 1, "name": "Chef's knife", "category": "kitchen", "price": 45.0, "vector": [0.9, 0.1, 0.1, 0.0]},
        {"id": 2, "name": "Cutting board", "category": "kitchen", "price": 25.0, "vector": [0.8, 0.2, 0.0, 0.1]},
        {"id": 3, "name": "Cast-iron pan", "category": "kitchen", "price": 60.0, "vector": [0.7, 0.0, 0.3, 0.2]},
        {"id": 4, "name": "Desk lamp", "category": "office", "price": 35.0, "vector": [0.9, 0.1, 0.0, 0.0]},
        {"id": 5, "name": "Notebook", "category": "office", "price": 5.0, "vector": [0.1, 0.9, 0.1, 0.0]},
        {"id": 6, "name": "Garden hose", "category": "garden", "price": 30.0, "vector": [0.0, 0.1, 0.9, 0.4]},
    ]
)

# mode="overwrite" lets the script be re-run without a "table exists" error.
table = db.create_table("products", data=df, mode="overwrite")

# Pre-filtering is the default, so the where() condition is applied before
# the vector search and only matching rows are considered.
results = (
    table.search([1.0, 0.0, 0.0, 0.0])
    .where("category = 'kitchen' AND price < 50")
    .select(["id", "name", "_distance"])
    .limit(2)
    .to_pandas()
)

print(results[["id", "name", "_distance"]].to_string(index=False))
