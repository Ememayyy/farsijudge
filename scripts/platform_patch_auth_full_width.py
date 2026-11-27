#!/usr/bin/env python3
"""Let the sign-in card span almost the full page width on every screen."""
from pathlib import Path

css_path = Path("src/style.css")
css = css_path.read_text(encoding="utf-8")

if "FJ AUTH FULL-WIDTH EXPERIENCE v1" in css:
    raise SystemExit("Full-width authentication layout has already been applied.")
if "FJ AUTH WIDTH EXPERIENCE v1" not in css:
    raise SystemExit("Expected the current authentication width refinement.")

css += r"""

/* FJ AUTH FULL-WIDTH EXPERIENCE v1 — card reaches close to both page edges */
.auth-shell > .auth-form-wrap {
  box-sizing:border-box !important;
}
@media (min-width:1101px) {
  .auth-shell {
    width:100% !important;
    max-width:none !important;
    padding-inline:clamp(22px,2.1vw,42px) !important;
  }
  .auth-shell > .auth-form-wrap {
    width:100% !important;
    max-width:none !important;
    margin-inline:0 !important;
  }
}
@media (min-width:701px) and (max-width:1100px) {
  .auth-shell {
    width:100% !important;
    max-width:none !important;
    padding-inline:14px !important;
  }
  .auth-shell > .auth-form-wrap {
    width:100% !important;
    max-width:none !important;
    margin-inline:0 !important;
  }
}
@media (max-width:700px) {
  .auth-shell {
    width:100% !important;
    padding-inline:6px !important;
  }
  .auth-shell > .auth-form-wrap {
    width:100% !important;
    max-width:none !important;
    margin-inline:0 !important;
    padding-inline:16px !important;
  }
}
@media (max-width:380px) {
  .auth-shell { padding-inline:4px !important; }
  .auth-shell > .auth-form-wrap { padding-inline:12px !important; }
}
"""
css_path.write_text(css, encoding="utf-8")
print("Expanded the sign-in card to nearly both edges of the viewport.")
