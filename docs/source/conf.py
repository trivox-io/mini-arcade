# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

try:
    import tomllib  # py311+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

# -- Path setup --------------------------------------------------------------
# If you want autodoc to resolve imports, add package roots here.
# (Adjust if your docs folder lives somewhere else.)
ROOT = os.path.abspath(os.path.join(__file__, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "packages", "mini-arcade-core", "src"))
sys.path.insert(0, os.path.join(ROOT, "packages", "mini-arcade", "src"))
sys.path.insert(
    0, os.path.join(ROOT, "packages", "mini-arcade-pygame-backend", "src")
)
sys.path.insert(
    0, os.path.join(ROOT, "packages", "mini-arcade-native-backend", "src")
)


def _docs_version() -> str:
    """
    Resolve docs version without requiring editable installs.
    Priority:
      1) DOCS_VERSION env var
      2) packages/mini-arcade/pyproject.toml -> [project].version
      3) fallback 0.0.0
    """
    env_version = os.getenv("DOCS_VERSION")
    if env_version:
        return env_version

    pyproject_path = Path(ROOT) / "packages" / "mini-arcade" / "pyproject.toml"
    if pyproject_path.exists():
        try:
            data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
            version_value = data.get("project", {}).get("version")
            if isinstance(version_value, str) and version_value.strip():
                return version_value.strip()
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    return "0.0.0"

# -- Project information -----------------------------------------------------

project = "Mini Arcade"
copyright = f"{date.today().year}, Santiago Rincon"
author = "Santiago Rincon"

version = _docs_version()
release = version

# -- General configuration ---------------------------------------------------

extensions = [
    "autoapi.extension",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "myst_parser",
    "sphinxcontrib.mermaid",
    "sphinx_copybutton",
    "sphinx_inline_tabs",
    "sphinx_design",
]
mermaid_js = "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"
# Mermaid: make diagrams readable in Furo dark mode
mermaid_init_js = """
// Sphinx will inject this before mermaid renders
mermaid.initialize({
  startOnLoad: true,
  theme: "base",
  themeVariables: {
    // high contrast for dark backgrounds
    background: "#0B0F14",
    primaryColor: "#101826",
    secondaryColor: "#101826",
    tertiaryColor: "#101826",

    // text
    primaryTextColor: "#E6EDF3",
    secondaryTextColor: "#E6EDF3",
    tertiaryTextColor: "#E6EDF3",

    // lines/arrows
    lineColor: "#E6EDF3",
    arrowheadColor: "#E6EDF3",

    // node borders
    primaryBorderColor: "#00E5FF",
    secondaryBorderColor: "#00E5FF",
    tertiaryBorderColor: "#00E5FF",

    // labels / titles
    labelColor: "#E6EDF3",
    titleColor: "#E6EDF3",

    // sequence diagrams
    actorBorder: "#00E5FF",
    actorTextColor: "#E6EDF3",
    actorLineColor: "#E6EDF3",
    signalColor: "#E6EDF3",
    signalTextColor: "#E6EDF3",
    noteBkgColor: "#101826",
    noteTextColor: "#E6EDF3",

    // flowchart specifics
    nodeBorder: "#00E5FF",
    nodeTextColor: "#E6EDF3"
  }
});
"""


# If your docs live at repo_root/docs/source/conf.py, this is fine.
# If docs are inside packages, adjust the paths accordingly.
autoapi_dirs = [
    os.path.join(ROOT, "packages", "mini-arcade-core", "src"),
    os.path.join(ROOT, "packages", "mini-arcade", "src"),
    os.path.join(ROOT, "packages", "mini-arcade-pygame-backend", "src"),
    os.path.join(ROOT, "packages", "mini-arcade-native-backend", "src"),
]
autoapi_ignore = [
    "*scenes/systems/builtins/cull.py",
]

autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "special-members",
    "show-module-summary",
    "imported-members",
]

suppress_warnings = [
    "autoapi.python_import_resolution",
    "autoapi.not_readable",
]

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
]

# Markdown support (MyST)
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "tasklist",
]

todo_include_todos = True
autosummary_generate = True

# -- Options for HTML output -------------------------------------------------

html_theme = "furo"
html_static_path = ["_static"]
html_title = "Mini Arcade"

REPO_URL = "https://github.com/trivox-io/mini-arcade"
DOCS_URL = f"{REPO_URL}/tree/main/docs"

_logo_abs = os.path.join(os.path.dirname(__file__), "_static", "mini-arcade-logo.png")
_favicon_abs = os.path.join(os.path.dirname(__file__), "_static", "favicon-32x32.png")

html_logo = "_static/mini-arcade-logo.png" if os.path.exists(_logo_abs) else None
html_favicon = "_static/favicon-32x32.png" if os.path.exists(_favicon_abs) else None

html_css_files = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/fontawesome.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/solid.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/brands.min.css",
]

html_theme_options = {
    "dark_css_variables": {
        # Brand
        "color-brand-primary": "#00E5FF",  # electric cyan
        "color-brand-content": "#A6FF00",  # neon green (links/highlights)
        # UI
        "color-background-primary": "#0B0F14",
        "color-background-secondary": "#101826",
        # Hover + target highlight
        "color-background-hover": "#0F1B2A",
        "color-background-hover--transparent": "#0F1B2A",
        "color-highlight-on-target": "#00E5FF33",
        # Optional: code blocks feel more "terminal"
        "color-code-background": "#0A0D12",
    },
    "light_css_variables": {
        "color-brand-primary": "#006DFF",  # arcade blue
        "color-brand-content": "#00A86B",  # emerald accent
        "color-background-primary": "#FFFFFF",
        "color-background-secondary": "#F6F8FB",
        "color-background-hover": "#EEF4FF",
        "color-background-hover--transparent": "#EEF4FF",
        "color-highlight-on-target": "#006DFF22",
    },
    "footer_icons": [
        {
            "name": "GitHub",
            "url": REPO_URL,
            "html": "",
            "class": "fa-brands fa-github",
        },
        {
            "name": "Docs",
            "url": DOCS_URL,
            "html": "",
            "class": "fa-solid fa-book",
        },
    ],
}
