# Documentation Folder (`docs/`)

This folder is reserved for **project documentation** and **research notes**.

## What belongs here

### 1) Generated documentation (Sphinx / Doxygen)

Use this repo’s `docs/` folder to store:

- **Sphinx (Python) documentation sources** (recommended structure example):
  - `docs/sphinx/` (sources: `conf.py`, `index.rst` or `index.md`, etc.)
  - `docs/sphinx/_build/` (generated output; typically ignored by git)

- **Doxygen (C/C++) documentation configuration and output** (recommended structure example):
  - `docs/doxygen/` (e.g., `Doxyfile`)
  - `docs/doxygen/html/` (generated output; typically ignored by git)

If you publish generated docs (e.g., GitHub Pages), prefer output in a dedicated folder (e.g., `docs/site/`) and keep sources under `docs/sphinx/` and/or `docs/doxygen/`.

### 2) Related-study / reading notes

Keep research materials required for this project here, for example:

- `docs/related-study/`:
  - paper summaries
  - interface notes (O1/A1/E2/F1)
  - experiment logs and design decisions
  - dataset descriptions and preprocessing notes
  - “what we tried / what failed” notes for reproducibility

### 3) How-to guides

This repo already includes a containerization/deployment guide:

- `docs/continerized.md` (Docker + Helm tutorial)

Add additional practical guides as needed (installation, integration, debugging).

---

> [!WARNING]
> **Documentation is required for every function in `src/`.**
>
> - Any new function/class/method added under `src/` MUST have documentation comments (docstrings for Python, Doxygen-style comments for C/C++).
> - Any public entrypoint (CLI/API/HTTP handler) MUST have usage documented in Markdown under `docs/`.
> - Every major module should have a short “purpose + inputs/outputs + examples” note.
>
> This repo is designed for research reproducibility: undocumented code is treated as incomplete.
