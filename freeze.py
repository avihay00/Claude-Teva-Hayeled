# =============================================================================
# freeze.py  —  Export Flask app to static HTML for GitHub Pages
# =============================================================================
# Usage:
#   pip install frozen-flask
#   python freeze.py
#
# Output: ./dist/  (ready to deploy as a static site)
# GitHub Pages URL: https://avihay00.github.io/Claude-Teva-Hayeled/
# =============================================================================

import os
import shutil

# Set static-build flag BEFORE importing app so templates can read it
os.environ["STATIC_BUILD"] = "true"

from flask_frozen import Freezer
from app import app

# ── Frozen-Flask configuration ─────────────────────────────────────────────
app.config["FREEZER_DESTINATION"]             = "dist"
app.config["FREEZER_RELATIVE_URLS"]           = True   # use ../static/... paths
app.config["FREEZER_IGNORE_MIMETYPE_WARNINGS"] = True
app.config["FREEZER_REMOVE_EXTRA_FILES"]      = True   # clean old files

freezer = Freezer(app)

if __name__ == "__main__":
    # Clean previous build
    if os.path.exists("dist"):
        shutil.rmtree("dist")

    freezer.freeze()
    print("\nStatic site built -> dist/")
    print("  Preview: open dist/index.html")
    print("  Live URL (after GH Pages enabled): "
          "https://avihay00.github.io/Claude-Teva-Hayeled/\n")
