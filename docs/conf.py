"""Sphinx configuration for the O-RAN rApp/xApp template.

Builds the API reference from the Sphinx/RST docstrings required by BMW Lab
SOP source-code-guide Section 4.  Build locally with::

    pip install -e ".[docs]"
    sphinx-build -b html docs docs/_build/html
"""

from __future__ import annotations

import os
import sys

# The template uses a src/ layout with three importable top-level packages.
sys.path.insert(0, os.path.abspath("../src"))

project = "O-RAN rApp/xApp Template"
author = "BMW Lab, NTUST ECE"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

autosummary_generate = True
autodoc_typehints = "description"
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

# Napoleon is enabled for mixed docstring styles; the codebase uses RST field
# lists (:param:/:return:) which autodoc parses natively.
napoleon_google_docstring = False
napoleon_numpy_docstring = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "requests": ("https://requests.readthedocs.io/en/stable/", None),
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = []

# requests is the only third-party runtime import; mock nothing — it installs
# cleanly in CI. Keep autodoc_mock_imports ready for heavier optional deps.
autodoc_mock_imports: list[str] = []
