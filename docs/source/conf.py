# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("./../../src/"))
# sys.path.insert(0, os.path.join("..", "..", "src"))

from pandas_visual_analysis.version import __version__

# -- Project information -----------------------------------------------------

project = "pandas-visual-analysis"
copyright = "2020, Matthias Matt"
author = "Matthias Matt"

# The full version, including alpha/beta/rc tags
release = __version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx_autodoc_typehints",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.viewcode",
]

autoclass_content = "both"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"

main_color = "#323EEC"
dark_gray = "#0f111f"
medium_gray = "#3b3c45"
light_gray = "#878892"

html_theme_options = {
    "logo": "assets/logo_tall.jpeg",
    "logo_name": None,
    "github_user": "meffmadd",
    "github_repo": "pandas-visual-analysis",
    "anchor": main_color,
    "link_hover": main_color,
    "link": dark_gray,
    "note_border": main_color,
    "sidebar_search_button": main_color,
    "gray_1": dark_gray,
    "gray_2": light_gray,
    "gray_3": medium_gray,
    "pre_bg": "#ffffff",  # background color of code blocks and other preformatted text
}
