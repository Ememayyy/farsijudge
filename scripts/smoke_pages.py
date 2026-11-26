#!/usr/bin/env python3
"""HTTP smoke test the published GitHub Pages shell and its primary assets."""
from __future__ import annotations

import os
import re
import sys
import time
from urllib.error import URLError, HTTPError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

base_url = os.environ.get("PAGES_URL", "").strip()
if not base_url:
    raise SystemExit("PAGES_URL is not configured.")
if not base_url.endswith("/"):
    base_url += "/"

def get(url: str) -> tuple[int, bytes]:
    request = Request(url, headers={"User-Agent": "FarsiJudge-Pages-Smoke/1.0"})
    with urlopen(request, timeout=25) as response:
        return response.status, response.read()

last_error: Exception | None = None
html = b""
for attempt in range(1, 13):
    try:
        status, html = get(base_url)
        if status == 200 and html:
            break
        last_error = RuntimeError(f"unexpected HTTP status {status}")
    except (URLError, HTTPError, TimeoutError) as exc:
        last_error = exc
    if attempt < 12:
        time.sleep(5)
else:
    raise SystemExit(f"GitHub Pages did not return HTTP 200: {last_error}")

source = html.decode("utf-8", errors="replace")
if "fj-logo.svg" not in source:
    raise SystemExit("Published homepage does not reference fj-logo.svg.")
if "farsijudge-logo.webp" in source:
    raise SystemExit("Published homepage still references the removed WebP favicon.")

refs = re.findall(r"""(?:src|href)=["']([^"']+)["']""", source, flags=re.IGNORECASE)
assets = []
for ref in refs:
    if ref.startswith(("http://", "https://", "data:", "#")):
        continue
    absolute = urljoin(base_url, ref)
    if re.search(r"\.(?:js|css|svg)(?:\?|$)", absolute, flags=re.IGNORECASE):
        assets.append(absolute)

required_extensions = {".js", ".css", ".svg"}
found_extensions = {os.path.splitext(url.split("?", 1)[0])[1].lower() for url in assets}
if not required_extensions.issubset(found_extensions):
    raise SystemExit(f"Homepage is missing required JS/CSS/SVG asset references: {found_extensions}")

for asset_url in dict.fromkeys(assets):
    status, data = get(asset_url)
    if status != 200 or not data:
        raise SystemExit(f"Published asset failed: HTTP {status} {asset_url}")

print(f"PASS: live GitHub Pages homepage and {len(set(assets))} JS/CSS/SVG assets returned HTTP 200.")
