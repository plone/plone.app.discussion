# Configuration file for the Sphinx documentation builder.
# plone.app.discussion documentation build configuration file

# -- Path setup --------------------------------------------------------------

from datetime import datetime

# -- Project information -----------------------------------------------------

project = "plone.app.discussion"
copyright = "Plone Foundation"
author = "Plone community"
trademark_name = "Plone"
now = datetime.now()
year = str(now.year)

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = "6"
# The full version, including alpha/beta/rc tags.
release = "6"

# -- General configuration ----------------------------------------------------

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# Add any Sphinx extension module names here, as strings.
# They can be extensions coming with Sphinx (named "sphinx.ext.*")
# or your custom ones.
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinxext.opengraph",
]

# If true, the Docutils Smart Quotes transform will be used to convert quotes
# and dashes to typographically correct entities.
smartquotes = False

# Options for the linkcheck builder
linkcheck_anchors = True
linkcheck_ignore = [
    # Ignore localhost
    r"http://127.0.0.1",
    r"http://localhost",
    # Ignore static file downloads
    r"^/_static/",
    r"^/_images/",
    # Ignore pages that require authentication
    r"https://github.com/orgs/plone/teams/",
]
linkcheck_retries = 1
linkcheck_report_timeouts_as_broken = True
linkcheck_timeout = 5

# The suffix of source filenames.
source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

# The master toctree document.
master_doc = "index"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = [
    "**.ipynb_checkpoints", 
    ".DS_Store", 
    "Thumbs.db", 
    "_build",
    "spelling_wordlist.txt",
    "**/CHANGES.md",
    "**/CHANGES.rst",
    "**/LICENSE.rst",
    "**/CONTRIBUTORS.md",
    "**/CONTRIBUTORS.rst",
    "**/README.md",
    "**/README.rst",
]

suppress_warnings = [
    "toc.not_readable",
    "myst.strikethrough",
]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.
html_theme = "plone_sphinx_theme"
html_logo = "_static/logo.svg" if "_static/logo.svg" else ""
html_favicon = "_static/favicon.ico" if "_static/favicon.ico" else ""

html_sidebars = {
    "**": [
        "navbar-logo",
        "search-button-field", 
        "sbt-sidebar-nav",
    ]
}

html_theme_options = {
    "article_header_start": ["toggle-primary-sidebar"],
    "extra_footer": """<p>The text and illustrations in this website are licensed by the Plone Foundation under a Creative Commons Attribution 4.0 International license. Plone and the Plone® logo are registered trademarks of the Plone Foundation, registered in the United States and other countries. For guidelines on the permitted uses of the Plone trademarks, see <a href="https://plone.org/foundation/logo">https://plone.org/foundation/logo</a>. All other trademarks are owned by their respective owners.</p>""",
    "footer_content_items": [
        "author",
        "copyright", 
        "last-updated",
        "extra-footer",
        "icon-links",
    ],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/plone/plone.app.discussion",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
            "attributes": {
                "target": "_blank",
                "rel": "noopener me",
            }
        },
    ],
    "logo": {
        "text": "plone.app.discussion v" + version,
    },
    "navigation_with_keys": True,
    "path_to_docs": "docs",
    "repository_branch": "master",
    "repository_url": "https://github.com/plone/plone.app.discussion",
    "search_bar_text": "Search",
    "show_toc_level": 2,
    "use_edit_page_button": False,
    "use_issues_button": True,
    "use_repository_button": True,
}

# The name for this set of Sphinx documents.
html_title = "%(project)s v%(release)s" % {"project": project, "release": release}

html_css_files = []
html_js_files = []
html_extra_path = []

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# -- Options for MyST markdown conversion to HTML -----------------------------

# For more information see:
# https://myst-parser.readthedocs.io/en/latest/syntax/optional.html
myst_enable_extensions = [
    "attrs_block",
    "attrs_inline", 
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_image",
    "linkify",
    "strikethrough",
    "substitution",
    "tasklist",
]

myst_substitutions = {}

# -- Intersphinx configuration ----------------------------------

# This extension can generate automatic links to the documentation of objects
# in other projects.
intersphinx_mapping = {
    "plone": ("https://6.docs.plone.org/", None),
    "python": ("https://docs.python.org/3/", None),
}

# -- OpenGraph configuration ----------------------------------

ogp_site_url = "https://6.docs.plone.org/"
ogp_description_length = 200
ogp_image = "https://6.docs.plone.org/_static/Plone_logo_square.png"
ogp_site_name = "Plone Documentation"
ogp_type = "website"

# -- Options for sphinx.ext.todo -----------------------

todo_include_todos = True

# -- Options for HTML help output -------------------------------------------------

htmlhelp_basename = "PloneAppDiscussionDocumentation"

# -- Options for LaTeX output -------------------------------------------------

latex_documents = [
    (
        "index",
        "PloneAppDiscussion.tex",
        "plone.app.discussion Documentation",
        "Plone community", 
        "manual",
    ),
]

latex_logo = "_static/logo_2x.png" if "_static/logo_2x.png" else ""

# -- Configuration for custom setup ----------------------------------

def setup(app):
    app.add_config_value("context", "documentation", "env")
