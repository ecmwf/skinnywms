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
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

import datetime
import os
import sys

top = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, top)


source_suffix = ".rst"
master_doc = "index"
pygments_style = "sphinx"
html_theme_options = {"logo_only": True}
html_logo = "_static/logo.png"


# -- Project information -----------------------------------------------------

project = "skinnyWMS"

author = "ECMWF"

year = datetime.datetime.now().year
if year == 2020:
    years = "2020"
else:
    years = "2020-%s" % (year,)

copyright = "%s, ECMWF" % (years,)


# The full version, including alpha/beta/rc tags
# release = climetlab.__version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_panels",
    # "sphinx.ext.intersphinx",
    # "sphinx.ext.extlinks",
    # "sphinx.ext.mathjax",
    "sphinx.ext.doctest",
    "sphinx.ext.napoleon",
    # "sphinx.ext.viewcode", # Uncomment to add links to source code
    "sphinx.ext.todo",
    "nbsphinx",
    "IPython.sphinxext.ipython_directive",
    "IPython.sphinxext.ipython_console_highlighting",
    "sphinx.ext.graphviz",
    "sphinx_gallery.gen_gallery",
    # "sphinx-prompt",
    # "climetlab.sphinxext.sources",
    # "climetlab.sphinxext.command_output",
    # "climetlab.sphinxext.module_output",
]

# Add any paths that contain templates here, relative to this directory.
# templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "'**.ipynb_checkpoints'"]


# https://www.notion.so/Deepnote-Launch-Buttons-63c642a5e875463495ed2341e83a4b2a

nbsphinx_prolog = """
{% set docname = env.doc2path(env.docname, base=None) %}

You can run this notebook in |Binder|, in |Colab|.

.. |Binder| image:: https://mybinder.org/badge.svg
   :target: https://mybinder.org/v2/gh/ecmwf/ecmwf-geomaps/main?urlpath=lab/tree/docs/{{ docname }}
   :alt: Binder
   :class: cmlbadge


.. |Colab| image:: https://colab.research.google.com/assets/colab-badge.svg
   :target: https://colab.research.google.com/github/ecmwf/ecmwf-geomaps/blob/main/docs/{{ docname }}
   :alt: Colab
   :class: cmlbadge


"""  # noqa

todo_include_todos = True

# ipython_warning_is_error = False

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = ["style.css"]

# See https://www.sphinx-doc.org/en/master/usage/extensions/graphviz.html
graphviz_output_format = "svg"

sphinx_gallery_conf = {
    "examples_dirs": ["gallery/styles"],  # path to your example scripts
    "gallery_dirs": [
        "auto_gallery/styles"
    ],  # path to where to save gallery generated output
}
