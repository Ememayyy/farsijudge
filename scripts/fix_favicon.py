#!/usr/bin/env python3
"""Normalize the favicon after Vite's HTML transforms and verify the built asset."""
from __future__ import annotations

import re
import sys
from pathlib import Path

root = Path("farsijudge")
asset = root / "dist" / "fj-logo.svg"
if not asset.is_file():
    raise SystemExit(f"Required favicon asset is missing: {asset}")

targets = [root / "index.html", root / "dist" / "index.html"]
for path in targets:
    if not path.is_file():
        continue
    html = path.read_text(encoding="utf-8")
    # Replace any stale favicon reference regardless of URL prefix or attributes.
    html = re.sub(
        r"<link\b(?=[^>]*farsijudge-logo\.webp)[^>]*>",
        '<link rel="icon" type="image/svg+xml" href="./fj-logo.svg" />',
        html,
        flags=re.IGNORECASE,
    )
    html = html.replace("/farsijudge/farsijudge-logo.webp", "./fj-logo.svg")
    html = html.replace("farsijudge-logo.webp", "fj-logo.svg")
    if not re.search(r'<link\b[^>]*rel=["\']icon["\'][^>]*fj-logo\.svg', html, flags=re.IGNORECASE):
        html = html.replace(
            "</head>",
            '  <link rel="icon" type="image/svg+xml" href="./fj-logo.svg" />\n</head>',
            1,
        )
    if "farsijudge-logo.webp" in html or "fj-logo.svg" not in html:
        raise SystemExit(f"Failed to normalize favicon in {path}")
    path.write_text(html, encoding="utf-8")
    print(f"Favicon OK: {path}")

if not (root / "dist" / "index.html").is_file():
    raise SystemExit("Built index.html is missing.")
