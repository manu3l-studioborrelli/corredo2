#!/usr/bin/env python3
"""Rebuild every generated page: index.html, categoria-*.html, prodotto.html (+ data/catalog.json)."""
import sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_home, build_pages  # noqa: E402

build_home.build()
build_pages.build()
