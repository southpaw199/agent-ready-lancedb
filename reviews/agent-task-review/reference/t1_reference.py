"""Reference solution for T1: table from a DataFrame, filtered vector search."""
import lancedb
import pandas as pd

df = pd.DataFrame({
    "id": [1, 2, 3, 4, 5, 6],
    "name": ["Chef's knife", "Cutting board", "Cast-iron pan", "Desk lamp", "Notebook", "Garden hose"],
    "category": ["kitchen", "kitchen", "kitchen", "office", "office", "garden"],
    "price": [45.0, 25.0, 60.0, 35.0, 5.0, 30.0],
    "vector": [[0.9, 0.1, 0.1, 0.0], [0.8, 0.2, 0.0, 0.1], [0.7, 0.0, 0.3, 0.2],
               [0.9, 0.1, 0.0, 0.0], [0.1, 0.9, 0.1, 0.0], [0.0, 0.1, 0.9, 0.4]],
})

db = lancedb.connect("data/t1")
table = db.create_table("products", data=df, mode="overwrite")
result = (
    table.search([1.0, 0.0, 0.0, 0.0])
    .where("category = 'kitchen' AND price < 50")
    .limit(2)
    .select(["id", "name", "_distance"])
    .to_pandas()
)
print(result)
