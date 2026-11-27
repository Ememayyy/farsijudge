#!/usr/bin/env python3
"""Replace the split authentication marketing panel with a focused, responsive auth card."""
from pathlib import Path

app_path = Path("src/App.tsx")
css_path = Path("src/style.css")
app = app_path.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8")

if "FJ AUTH EXPERIENCE v2" in css:
    raise SystemExit("Authentication refresh has already been applied.")

visual_start_marker = '      <div className="auth-visual">'
form_start_marker = '        <div className="auth-form-wrap">'
if app.count(visual_start_marker) != 1:
    raise SystemExit("Expected exactly one authentication marketing panel.")
if app.count(form_start_marker) != 1:
    raise SystemExit("Expected exactly one authentication form panel.")

visual_start = app.index(visual_start_marker)
form_start = app.index(form_start_marker, visual_start)
if form_start <= visual_start:
    raise SystemExit("Authentication form appears before the visual panel.")
# The auth visual is a complete first child of auth-shell. Keep the actual form,
# its mode toggle, validation notices, and all Supabase event handlers unchanged.
app = app[:visual_start] + app[form_start:]

# The formerly mobile-only identity row becomes the single brand header on all screens.
app = app.replace(
    '<div className="mobile-brand"><span className="brand-mark"><img src={brandLogo} alt="" /></span><b>فارسی جاج</b></div>',
    '<div className="mobile-brand"><span className="brand-mark"><img src={brandLogo} alt="" /></span><span><b>فارسی جاج</b><small>FARSI JUDGE</small></span></div>',
    1,
)
if "mobile-brand" not in app or "auth-form-wrap" not in app:
    raise SystemExit("Authentication brand or form disappeared during cleanup.")

css += r"""

/* FJ AUTH EXPERIENCE v2 — one focused sign-in / sign-up surface */
.auth-shell {
  position:relative !important;
  isolation:isolate;
  width:100% !important;
  max-width:100% !important;
  min-width:0 !important;
  min-height:100svh !important;
  height:auto !important;
  margin:0 !important;
  padding:clamp(22px,5vh,54px) 18px !important;
  display:grid !important;
  grid-template-columns:minmax(0,1fr) !important;
  place-items:center !important;
  overflow-x:clip !important;
  overflow-y:auto !important;
  background:
    radial-gradient(ellipse at 50% 0%,rgba(146,112,255,.14),transparent 34rem),
    radial-gradient(ellipse at 8% 90%,rgba(89,190,225,.07),transparent 27rem),
    var(--bg) !important;
}
.auth-shell > .auth-visual { display:none !important; }
.auth-shell > .auth-form-wrap {
  position:relative;
  z-index:1;
  display:flex !important;
  flex-direction:column !important;
  align-items:stretch !important;
  justify-content:center !important;
  width:min(100%,470px) !important;
  max-width:470px !important;
  min-width:0 !important;
  min-height:0 !important;
  height:auto !important;
  margin:0 auto !important;
  padding:clamp(23px,4.5vw,43px) !important;
  border:1px solid var(--fj-border,var(--line)) !important;
  border-radius:23px !important;
  background:var(--panel) !important;
  box-shadow:0 26px 78px rgba(0,0,0,.16),0 4px 18px rgba(100,75,180,.07) !important;
}
.auth-shell .mobile-brand {
  display:flex !important;
  align-items:center !important;
  justify-content:flex-start !important;
  gap:11px !important;
  width:100%;
  margin:0 0 29px !important;
  padding:0 0 19px;
  border-bottom:1px solid var(--line);
  color:var(--text);
}
.auth-shell .mobile-brand .brand-mark {
  flex:0 0 43px;
  width:43px;
  height:43px;
  border-radius:13px;
}
.auth-shell .mobile-brand > span:last-child {
  display:flex;
  flex-direction:column;
  gap:3px;
}
.auth-shell .mobile-brand b { font-size:15px; font-weight:950; }
.auth-shell .mobile-brand small {
  color:var(--muted);
  direction:ltr;
  text-align:right;
  font-size:8px;
  font-weight:850;
  letter-spacing:1.4px;
}
.auth-shell .auth-form-wrap > .eyebrow {
  margin:0 0 7px !important;
  color:var(--fj-violet,var(--accent));
  font-size:10px;
  font-weight:900;
  letter-spacing:.35px;
}
.auth-shell .auth-form-wrap > h2 {
  margin:0 0 7px !important;
  color:var(--text);
  font-size:clamp(25px,3vw,31px) !important;
  font-weight:950;
  line-height:1.45;
  letter-spacing:-.6px;
}
.auth-shell .auth-form-wrap .auth-subtitle {
  margin:0 0 24px !important;
  color:var(--muted);
  font-size:12px;
  line-height:1.9;
}
.auth-shell .auth-form-wrap form {
  display:flex;
  flex-direction:column;
  gap:14px !important;
  width:100%;
}
.auth-shell .auth-form-wrap .field-label {
  display:flex;
  flex-direction:column;
  gap:7px;
  color:var(--text);
  font-size:11px;
  font-weight:800;
}
.auth-shell .auth-form-wrap input {
  width:100%;
  min-width:0;
  min-height:49px !important;
  padding:0 13px;
  border:1px solid var(--line);
  border-radius:11px;
  background:var(--panel-2);
  color:var(--text);
  font-size:15px;
  outline:none;
  transition:border-color .16s ease,box-shadow .16s ease,background .16s ease;
}
.auth-shell .auth-form-wrap input:focus {
  border-color:var(--fj-violet,var(--accent));
  background:var(--panel);
  box-shadow:0 0 0 4px rgba(146,112,255,.12);
}
.auth-shell .auth-form-wrap .button {
  min-height:49px !important;
  justify-content:center;
  border-radius:11px;
  font-size:12px;
  font-weight:900;
}
.auth-shell .auth-form-wrap .welcome-back-link { margin-top:9px; }
.auth-shell .auth-form-wrap .muted.small { font-size:11px; line-height:1.8; }
.auth-shell .auth-form-wrap button,
.auth-shell .auth-form-wrap a { touch-action:manipulation; }

@media (max-width:700px) {
  .auth-shell {
    min-height:100svh !important;
    padding:16px 12px calc(20px + env(safe-area-inset-bottom,0px)) !important;
    place-items:center !important;
  }
  .auth-shell > .auth-form-wrap {
    width:100% !important;
    max-width:480px !important;
    padding:22px 17px 25px !important;
    border-radius:18px !important;
  }
  .auth-shell .mobile-brand {
    margin-bottom:22px !important;
    padding-bottom:15px;
  }
  .auth-shell .auth-form-wrap > h2 { font-size:24px !important; }
  .auth-shell .auth-form-wrap .auth-subtitle {
    margin-bottom:19px !important;
    font-size:11px;
  }
  .auth-shell .auth-form-wrap form { gap:12px !important; }
  .auth-shell .auth-form-wrap input {
    min-height:48px !important;
    padding-inline:12px;
    font-size:16px !important;
  }
  .auth-shell .auth-form-wrap .button { min-height:48px !important; }
  .auth-shell .auth-form-wrap .field-label { font-size:11px; }
}
@media (max-width:380px) {
  .auth-shell { padding-inline:9px !important; }
  .auth-shell > .auth-form-wrap { padding:19px 14px 21px !important; }
  .auth-shell .mobile-brand { margin-bottom:18px !important; }
}
@media (max-height:650px) {
  .auth-shell { place-items:start center !important; padding-block:14px !important; }
  .auth-shell > .auth-form-wrap { margin-block:auto !important; }
}
@media (prefers-reduced-motion:reduce) {
  .auth-shell *, .auth-shell *::before, .auth-shell *::after {
    transition-duration:.01ms !important;
    animation-duration:.01ms !important;
  }
}
"""
app_path.write_text(app, encoding="utf-8")
css_path.write_text(css, encoding="utf-8")
print("Rebuilt sign-in and sign-up as a single responsive form card.")
