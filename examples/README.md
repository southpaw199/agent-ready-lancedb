# LanceDB examples

[`docs-search.ipynb`](docs-search.ipynb) builds semantic search over the [FastAPI documentation](https://fastapi.tiangolo.com) with [LanceDB](https://docs.lancedb.com). It covers:

1. Downloading and cleaning a real documentation set
2. Splitting pages into sections and storing them with automatic embeddings
3. Vector search, with prefilters and postfilters
4. Full-text and hybrid search, compared side by side with two rerankers
5. Vector and scalar indexes
6. Adding columns and moving between table versions

The notebook also shows a search that fails, explains why, and fixes it.

## Prerequisites

- **Python 3.12.** Tested with 3.12.3 on Ubuntu 24.04 under WSL 2 on Windows 11.
- **Git.** The notebook uses it to download the docs.
- **An internet connection for the first run.** It downloads the FastAPI docs from GitHub and two models from Hugging Face. Later runs reuse them.
- **No API keys or accounts.** Both models run locally on the CPU.

On Windows, run everything inside WSL, and keep the repository in your Linux home folder (for example `~/projects`), not under `/mnt/c` or in a OneDrive folder. Access across the Windows/Linux boundary is much slower, and sync tools interfere with the virtual environment and LanceDB's data files.

## Set up

From the repository root:

```bash
cd case-studies/lancedb/examples
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

`requirements.txt` pins every version that was tested, and it points pip at PyTorch's CPU-only package index, which is a much smaller download than the default build with GPU support.

Check the install:

```bash
python -c "import lancedb, sentence_transformers; print(lancedb.__version__)"
```

This should print `0.40.0`.

## Run the notebook

1. Open `docs-search.ipynb` in VS Code (with the Python and Jupyter extensions) or in Jupyter (`jupyter lab`).
2. Select the `.venv` environment as the kernel. See [Troubleshooting](#troubleshooting) if VS Code doesn't list it.
3. Run all cells.

The first run takes a few minutes, mostly to download the models and embed about 800 sections. Everything the notebook creates goes in a `data/` folder next to it, which Git ignores. Delete `data/` to start over.

## Troubleshooting

| What you see | What it means and what to do |
| --- | --- |
| `error: externally-managed-environment` when running `pip install` | Ubuntu 24.04 blocks installing packages into the system Python. Create and activate the virtual environment first, as in [Set up](#set-up). |
| `pip freeze` or `import lancedb` finds nothing, or `ModuleNotFoundError: No module named 'lancedb'` | The virtual environment isn't active in this terminal. Run `source .venv/bin/activate` from this folder. Each new terminal needs it; the prompt starts with `(.venv)` when it's active. |
| VS Code's kernel picker doesn't list `.venv` | VS Code doesn't find environments deep inside a repository. Choose **Select Another Kernel** > **Python Environments** > **Enter interpreter path**, and enter the full path to `.venv/bin/python` in this folder. Don't choose `/usr/bin/python3`, which doesn't have the packages. |
| VS Code asks whether to create a virtual environment because packages may be installed globally | Choose **No** if `.venv` is already active (check with `which python`). The prompt appears because VS Code hasn't been told which interpreter you're using; selecting the kernel as above stops it. |
| VS Code asks to download files for `@jupyter-widgets/base` | This only affects how progress bars display. **Enable Downloads** shows them; **Cancel** shows plain text instead. Either way, the notebook runs. |
| `Warning: You are sending unauthenticated requests to the HF Hub` | Harmless. Both models are public and need no Hugging Face token. The models are cached in `~/.cache/huggingface` after the first download. |
| `WARN lance::dataset::write::insert ... No existing dataset ... it will be created` | Normal on the first run: LanceDB logs this whenever it creates a new table. |
| `WARN ... KMeans: more than 10% of clusters are empty` during Step 7 | LanceDB noting that the table is small for a vector index. Harmless here; the notebook explains why the index is included anyway. |

## Data source and license

The FastAPI documentation is © Sebastián Ramírez and contributors, used under the [MIT License](https://github.com/fastapi/fastapi/blob/master/LICENSE). The notebook downloads it from GitHub at release 0.159.0 when it runs; this repository doesn't include a copy.
