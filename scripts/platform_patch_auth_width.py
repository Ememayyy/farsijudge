#!/usr/bin/env python3
"""Widen the authentication card on desktop and mobile without changing its design."""
from pathlib import Path

css_path = Path("src/style.css")
css = css_path.read_text(encoding="utf-8")

if "FJ AUTH WIDTH EXPERIENCE v1" in css:
    raise SystemExit("Authentication width refinement has already been applied.")
if "FJ AUTH DESKTOP EXPERIENCE v2" not in css:
    raise SystemExit("Expected the current authentication layout before widening it.")

css += r"""

/* FJ AUTH WIDTH EXPERIENCE v1 — more room on wide and small screens */
@media (min-width:701px) {
  .auth-shell > .auth-form-wrap {
    width:min(100%,600px) !important;
    max-width:600px !important;
    padding-inline:56px !important;
  }
}
@media (min-width:701px) and (max-width:1100px) {
  .auth-shell > .auth-form-wrap { padding:40px 50px !important; }
}
@media (max-width:700px) {
  .auth-shell { padding-inline:8px !important; }
  .auth-shell > .auth-form-wrap {
    width:100% !important;
    max-width:620px !important;
    padding:22px 16px 25px !important;
  }
}
@media (max-width:380px) {
  .auth-shell { padding-inline:7px !important; }
  .auth-shell > .auth-form-wrap { padding:19px 13px 22px !important; }
}
"""
css_path.write_text(css, encoding="utf-8")
print("Widened the authentication form for desktop, tablets, and phones.")
