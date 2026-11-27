#!/usr/bin/env python3
"""Refine desktop auth spacing without changing the working mobile layout."""
from pathlib import Path

app_path = Path("src/App.tsx")
css_path = Path("src/style.css")
app = app_path.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8")

if "FJ AUTH DESKTOP EXPERIENCE v2" in css:
    raise SystemExit("Desktop authentication refinement has already been applied.")

# Keep the original auth markup: no invented side panel or duplicate branding.
if 'className="auth-desktop-panel"' in app:
    raise SystemExit("Unexpected legacy desktop panel found in source markup.")

css += r"""

/* FJ AUTH DESKTOP EXPERIENCE v2 — calm, centered, proportionate desktop form */
@media (min-width:701px) {
  .auth-shell {
    width:100% !important;
    max-width:none !important;
    min-height:100svh !important;
    height:auto !important;
    margin:0 !important;
    padding:54px 32px !important;
    display:grid !important;
    grid-template-columns:minmax(0,1fr) !important;
    place-items:center !important;
    overflow-x:clip !important;
    overflow-y:auto !important;
    background:
      radial-gradient(ellipse at 50% 8%,rgba(137,111,235,.12),transparent 35rem),
      radial-gradient(ellipse at 12% 88%,rgba(91,178,211,.055),transparent 26rem),
      var(--bg) !important;
  }
  .auth-shell > .auth-form-wrap {
    width:min(100%,520px) !important;
    max-width:520px !important;
    min-height:0 !important;
    height:auto !important;
    margin:auto !important;
    padding:48px 50px 44px !important;
    border:1px solid var(--fj-border,var(--line)) !important;
    border-top:3px solid var(--fj-violet,var(--accent)) !important;
    border-radius:22px !important;
    background:var(--panel) !important;
    box-shadow:0 22px 70px rgba(0,0,0,.12),0 3px 14px rgba(100,75,180,.045) !important;
  }
  .auth-shell .mobile-brand {
    display:flex !important;
    margin-bottom:34px !important;
    padding-bottom:21px !important;
  }
  .auth-shell .auth-form-wrap > .eyebrow {
    margin-bottom:9px !important;
    font-size:11px !important;
  }
  .auth-shell .auth-form-wrap > h2 {
    margin-bottom:9px !important;
    font-size:30px !important;
    line-height:1.5 !important;
  }
  .auth-shell .auth-form-wrap .auth-subtitle {
    margin-bottom:28px !important;
    font-size:13px !important;
    line-height:2 !important;
  }
  .auth-shell .auth-form-wrap form { gap:17px !important; }
  .auth-shell .auth-form-wrap .field-label { gap:9px !important; font-size:12px !important; }
  .auth-shell .auth-form-wrap input { min-height:54px !important; padding-inline:15px !important; }
  .auth-shell .auth-form-wrap .button { min-height:54px !important; margin-top:3px; }
  .auth-shell .auth-form-wrap .welcome-back-link { margin-top:14px !important; }
}
@media (min-width:701px) and (max-width:1100px) {
  .auth-shell { padding-inline:24px !important; }
  .auth-shell > .auth-form-wrap { padding:40px 38px !important; }
}
@media (min-width:701px) and (max-height:720px) {
  .auth-shell { padding-block:24px !important; }
  .auth-shell > .auth-form-wrap { padding-block:30px !important; }
  .auth-shell .mobile-brand { margin-bottom:22px !important; }
  .auth-shell .auth-form-wrap .auth-subtitle { margin-bottom:18px !important; }
  .auth-shell .auth-form-wrap form { gap:12px !important; }
}
"""
css_path.write_text(css, encoding="utf-8")
print("Applied restrained desktop auth sizing; preserved the original mobile auth markup and layout.")
