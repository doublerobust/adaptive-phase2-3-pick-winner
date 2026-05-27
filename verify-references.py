#!/usr/bin/env python3
"""
verify-references.py - Systematic reference verification against Crossref API.

Usage:
    # Verify all references in a markdown doc
    python3 verify-references.py path/to/document.md

    # Verify a specific list of DOIs
    python3 verify-references.py --dois 10.1002/sim.1362 10.1093/biomet/ass002

What it does:
    1. Extracts numbered references with DOIs from the markdown file
    2. Queries Crossref API for each DOI
    3. Compares title, authors, journal, year, volume, pages
    4. Reports mismatches and non-existent DOIs
    5. For references without DOIs, notes them for manual review

Dependencies: curl (should be available on any Unix system)
"""

