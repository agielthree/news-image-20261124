#!/usr/bin/env python3
"""Entrypoint: draw the 24 November 2026 news poster to /output/entry.png."""

import os
import sys

# Grader runs with `python3 -P -s`, so the script's directory is NOT on
# sys.path; add it explicitly so the sibling module is importable.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import draw_poster

if __name__ == "__main__":
    draw_poster.main()
