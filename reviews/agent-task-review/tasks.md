# LanceDB: agent task review tasks

- **Method:** [agent task review](../../../../methods/agent-task-review/method.md), version 0.1
- **Docs entry point given to the agent:** `https://docs.lancedb.com/llms.txt`
- **Environment for every run:** Ubuntu 24.04 under WSL 2, Python 3.12, a new empty folder outside this repository, and a fresh agent session with no project instructions or memory

## Standard instructions

Give the agent these instructions first in every session, then the task prompt. Use the same wording every time, so runs can be compared.

> I'm learning LanceDB, an open-source vector database. Use only the official LanceDB documentation at https://docs.lancedb.com to do this task. Start from https://docs.lancedb.com/llms.txt. Don't rely on what you remember about LanceDB, and don't use other websites. Each time you rely on a docs page, tell me its URL.
>
> Work only in the current folder. Create a Python virtual environment here and install what you need. When you're done, give me the final code as a single Python file named `task.py`, run it, and show me the output.

## Before the first run: confirm the expected answers

Tasks T2, T3, and T4 depend on embedding models, so check their expected answers on your machine first. The [`reference/`](reference/) folder has a working solution for each task. Run them in their own virtual environment, outside any agent's folder:

```bash
mkdir -p ~/agent-runs/reference && cd ~/agent-runs/reference
python3 -m venv .venv && source .venv/bin/activate
pip install lancedb pandas sentence-transformers open-clip-torch pillow
R=~/projects/agent-ready-docs/case-studies/lancedb/reviews/agent-task-review
python $R/make_sample_images.py .
for t in 1 2 3 4 5; do echo "== T$t"; python $R/reference/t${t}_reference.py; done
```

If a reference result differs from the success criteria below, update the criteria before running any agent. Never show the agent these files.

## Scoring

- **Outcome** and **root cause** use the categories in the [rubric](../../../../methods/agent-task-review/rubric.md).
- A task passes only if you run `task.py` yourself in the agent's folder and every success criterion is met.
- Deprecation warnings don't fail a task, but log each one with root cause `outdated-content` if the docs page the agent cited showed the deprecated form.
- When the agent stalls, give the smallest hint that lets it continue, and log the hint word for word.

---

## Task T1: Create a table and run a filtered vector search

**Prompt given to the agent:**
> Create a LanceDB table called `products` from a pandas DataFrame with these rows:
>
> | id | name | category | price | vector |
> | --- | --- | --- | --- | --- |
> | 1 | Chef's knife | kitchen | 45.0 | [0.9, 0.1, 0.1, 0.0] |
> | 2 | Cutting board | kitchen | 25.0 | [0.8, 0.2, 0.0, 0.1] |
> | 3 | Cast-iron pan | kitchen | 60.0 | [0.7, 0.0, 0.3, 0.2] |
> | 4 | Desk lamp | office | 35.0 | [0.9, 0.1, 0.0, 0.0] |
> | 5 | Notebook | office | 5.0 | [0.1, 0.9, 0.1, 0.0] |
> | 6 | Garden hose | garden | 30.0 | [0.0, 0.1, 0.9, 0.4] |
>
> Then find the 2 products nearest to the vector [1.0, 0.0, 0.0, 0.0] that are in the `kitchen` category and cost less than 50. Print their ids, names, and distances.

**Docs area exercised:** quickstart, tables, vector search, filtering

**Success criteria:**
- The table is created from a pandas DataFrame, not from a list of dictionaries.
- The output lists exactly two products: id 1 (Chef's knife) first and id 2 (Cutting board) second.
- Distances are about 0.03 and 0.09 (squared L2, LanceDB's default).

**What this tests:** The nearest product overall is the Desk lamp (id 4), which the filter must exclude. A filter applied after the search (a postfilter) with a limit of 2 returns only the Chef's knife, so an agent that misunderstands prefiltering fails this task.

**Starting state:** empty folder; fresh virtual environment

**Out of scope:** LanceDB Cloud or Enterprise; API keys

---

## Task T2: Embed text automatically

**Prompt given to the agent:**
> Create a LanceDB table of these five sentences, set up so that LanceDB generates the embeddings automatically, both when I add rows and when I search with a text query. Use a local sentence-transformers model, not a paid API.
>
> 1. Cats often purr when they are content.
> 2. Dogs need regular walks to stay healthy.
> 3. Goldfish can live for more than ten years.
> 4. Parrots can learn to imitate human speech.
> 5. Rabbits are most active at dawn and dusk.
>
> Then search the table with the text "Which animal makes a soft rumbling sound when happy?" and print the top 3 sentences with their distances.

**Docs area exercised:** embeddings, embedding function registry, schemas

**Success criteria:**
- `task.py` never calls the embedding model directly, for example with `model.encode(...)`. Embeddings come from an embedding function attached to the table's schema.
- The search is called with the text string, not with a vector the code computed itself.
- The top result is sentence 1, about cats.

**What this tests:** whether the docs explain the registry and schema approach clearly enough that the agent doesn't fall back on computing embeddings by hand. The question shares no key words with the answer, so only meaning matches it.

**Starting state:** empty folder; fresh virtual environment

**Out of scope:** paid embedding APIs; API keys

---

## Task T3: Full-text and hybrid search with a reranker

**Prompt given to the agent:**
> Create a LanceDB table of these help-center passages, with automatic embeddings from a local sentence-transformers model:
>
> 1. Press Ctrl+Z to undo the last change you made. Press Ctrl+Y to redo it.
> 2. To change the color theme, open Settings and choose Appearance.
> 3. Track changes records every edit so reviewers can accept or reject them.
> 4. Your work is saved automatically every two minutes.
> 5. To restore an earlier copy of a file, open File, then Version History.
> 6. Use Ctrl+F to find text and Ctrl+H to replace it.
> 7. You can change the default font size in Settings under Editor.
> 8. Comments let you discuss a passage without changing the text.
>
> Build a full-text search index on the passage text. Then answer the question "How do I reverse my most recent edit?" three ways and print the top 3 passages for each: vector search, full-text search, and hybrid search that combines the two with an explicitly chosen reranker.

**Docs area exercised:** full-text indexing, hybrid search, rerankers

**Success criteria:**
- A full-text index is created on the passage text column.
- Three result lists are printed, labeled vector, full-text, and hybrid.
- The hybrid search sets a reranker explicitly, for example `RRFReranker()`.
- The results match a correct implementation: compare them with the [reference solution](reference/t3_reference.py)'s output, using the same reranker.

**What this tests:** whether the agent can find the current way to create a full-text index, and whether the docs explain how hybrid search and rerankers fit together.

**Expected behavior to understand before scoring:** The question uses "reverse" and "edit" rather than "undo" and "change". Full-text search should return only passage 3, the only passage containing "edit". Vector search should rank passage 1 highest. With `RRFReranker`, passage 3 will probably rank first in hybrid search because it appears in both lists, even though passage 1 is the better answer. That's how rank fusion works, not an agent failure. If the agent notices and explains it, record that in `notes`.

**Starting state:** empty folder; fresh virtual environment

**Out of scope:** paid rerankers and embedding APIs; API keys

---

## Task T4: Store images and find similar images

**Prompt given to the agent:**
> The `images` folder here has 12 PNG images of simple shapes, and `query.png` is one more image. Store the 12 images in a LanceDB table, including the image data itself, not just the file paths, with embeddings from a local multimodal model that works with both images and text. Then find the 3 images most similar to `query.png`, and separately the 3 images that best match the text "a red circle". Print the file names and distances for both searches.

**Docs area exercised:** multimodal tables, image embeddings

**Success criteria:**
- The table stores each image's bytes in a column, as well as its file name.
- Embeddings come from a local multimodal model, such as an OpenCLIP model from the embedding registry.
- `red_circle.png` is first for the image search.
- `red_circle.png` is in the top 3 for the text search.

**What this tests:** whether the docs explain how to store binary image data and attach an embedding function that handles both images and text.

**Starting state:** empty folder plus the sample images. Before the session, run [`make_sample_images.py`](make_sample_images.py) in the folder:

```bash
python /path/to/agent-ready-docs/case-studies/lancedb/reviews/agent-task-review/make_sample_images.py .
```

That creates `images/` (12 shapes: circle, square, and triangle in red, green, blue, and yellow) and `query.png` (a slightly smaller red circle in a different position). Then start the agent session. Don't show the agent the script.

**Out of scope:** paid APIs; GPU acceleration

---

## Task T5: Add a vector index to a large table

**Prompt given to the agent:**
> Create a LanceDB table of 100,000 random 128-dimensional vectors, generated with NumPy using the seed 42, with an integer `id` column from 0 to 99,999. Add a vector index suited to a table this size. Then search for the 10 nearest neighbors of the vector in row 123, and print the time the search took both with and without the index. Finally, explain in a few sentences when a LanceDB table needs a vector index, and what you give up by using one.

**Docs area exercised:** vector indexes, search tuning

**Success criteria:**
- A vector index is created with the current index API, and listing the table's indexes shows it.
- The search with the index returns row 123 first.
- Both search times are printed.
- The explanation says that without an index LanceDB compares the query with every row, that an index makes search faster but approximate, and that settings such as `nprobes` or `refine_factor` trade speed for accuracy.

**What this tests:** whether the agent finds current index guidance, including the current way to create an index, and whether the docs explain when an index is worth building.

**Expected behavior to understand before scoring:** Random vectors are a hard case for an approximate index, because they're nearly equidistant from each other. In the reference run, the indexed search found row 123 first, but only 2 of its top 10 matched the exact top 10. Record the overlap if the agent measures it. An agent that reports low recall and explains why has done well.

**Starting state:** empty folder; fresh virtual environment

**Out of scope:** GPU index building; LanceDB Cloud
