# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'WTRobot'
copyright = '2022, Vishal Vijayraghavan'
author = 'Vishal Vijayraghavan'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.autosectionlabel",
    "sphinx_design",
    "sphinx_copybutton"
    ]

source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "restructuredtext",
    ".md": "markdown",
}

myst_enable_extensions = ["colon_fence"]

master_doc = "index"

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

#html_theme = 'alabaster'
html_theme = "sphinx_rtd_theme"

html_static_path = ['_static']

html_logo='_static/wtlogo.png'

html_theme_options = {
    'logo_only': False,
    'show_related': True,
    'collapse_navigation': True,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'sticky_navigation': True,
    'includehidden': True,
    'navigation_depth': 4,

}