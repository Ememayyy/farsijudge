#!/usr/bin/env python3
"""Apply one consolidated responsive layout to the sign-in and sign-up screens."""
import re
from pathlib import Path

app_path = Path("src/App.tsx")
css_path = Path("src/style.css")
app = app_path.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8")

if "FJ AUTH RESPONSIVE SYSTEM v3" in css:
    raise SystemExit("The consolidated authentication layout has already been applied.")

# Remove only the old marketing panel. Keep the working form and auth-mode state.
visual_start_marker = '      <div className="auth-visual">'
form_start_marker = '        <div className="auth-form-wrap">'
if app.count(visual_start_marker) != 1 or app.count(form_start_marker) != 1:
    raise SystemExit("Expected exactly one auth marketing panel and one auth form.")
visual_start = app.index(visual_start_marker)
form_start = app.index(form_start_marker, visual_start)
if form_start <= visual_start:
    raise SystemExit("Authentication form appears before the visual panel.")

def find_div_end(source: str, start: int) -> int:
    tags = re.compile(r"</?div\b[^>]*>")
    depth = 0
    for match in tags.finditer(source, start):
        token = match.group(0)
        if token.startswith("</"):
            depth -= 1
            if depth == 0:
                return match.end()
        elif not token.rstrip().endswith("/>"):
            depth += 1
    raise SystemExit("Could not find the end of the authentication marketing panel.")

visual_end = find_div_end(app, visual_start)
if visual_end > form_start:
    raise SystemExit("Authentication marketing panel unexpectedly contains the form.")
app = app[:visual_start] + app[visual_end:]

brand_match = re.search(
    r'(<div className="mobile-brand">.*?</span>)<b>فارسی جاج</b></div>',
    app,
    re.S,
)
if brand_match:
    replacement = brand_match.group(1) + '<span><b>فارسی جاج</b><small>FARSI JUDGE</small></span></div>'
    app = app[:brand_match.start()] + replacement + app[brand_match.end():]

if "mobile-brand" not in app or "auth-form-wrap" not in app:
    raise SystemExit("Authentication brand or form disappeared during cleanup.")
if "setAuthMode(authMode === 'login' ? 'register' : 'login')" not in app:
    raise SystemExit("The existing sign-in / sign-up switch was not preserved.")

css += r"""

/* FJ AUTH RESPONSIVE SYSTEM v3 — one source of truth for phone, tablet and desktop */
.auth-shell,
.auth-shell * {
  box-sizing:border-box;
}
.auth-shell {
  position:relative;
  isolation:isolate;
  display:grid;
  grid-template-columns:minmax(0,1fr);
  place-items:center;
  width:100%;
  min-width:0;
  min-height:100vh;
  min-height:100svh;
  height:auto;
  margin:0;
  padding:clamp(22px,5vh,54px) 16px;
  overflow-x:clip;
  overflow-y:auto;
  background:
    radial-gradient(ellipse at 50% 0%,rgba(146,112,255,.14),transparent 34rem),
    radial-gradient(ellipse at 8% 90%,rgba(89,190,225,.07),transparent 27rem),
    var(--bg);
}
.auth-shell > .auth-visual {
  display:none;
}
.auth-shell > .auth-form-wrap {
  position:relative;
  z-index:1;
  display:flex;
  flex-direction:column;
  align-items:stretch;
  justify-content:center;
  width:min(100%,620px);
  max-width:620px;
  min-width:0;
  min-height:0;
  height:auto;
  margin:0 auto;
  padding:clamp(22px,4.5vw,40px);
  border:1px solid var(--fj-border,var(--line));
  border-radius:21px;
  background:var(--panel);
  box-shadow:0 24px 68px rgba(0,0,0,.14),0 4px 16px rgba(100,75,180,.06);
}
.auth-shell .mobile-brand {
  display:flex;
  align-items:center;
  justify-content:flex-start;
  gap:11px;
  width:100%;
  margin:0 0 25px;
  padding:0 0 17px;
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
.auth-shell .mobile-brand b {
  font-size:15px;
  font-weight:950;
}
.auth-shell .mobile-brand small {
  color:var(--muted);
  direction:ltr;
  text-align:right;
  font-size:8px;
  font-weight:850;
  letter-spacing:1.4px;
}
.auth-shell .auth-form-wrap > .eyebrow {
  margin:0 0 7px;
  color:var(--fj-violet,var(--accent));
  font-size:10px;
  font-weight:900;
  letter-spacing:.35px;
}
.auth-shell .auth-form-wrap > h2 {
  margin:0 0 7px;
  color:var(--text);
  font-size:clamp(25px,3vw,31px);
  font-weight:950;
  line-height:1.45;
  letter-spacing:-.6px;
}
.auth-shell .auth-form-wrap .auth-subtitle {
  margin:0 0 22px;
  color:var(--muted);
  font-size:12px;
  line-height:1.9;
}
.auth-shell .auth-form-wrap form {
  display:flex;
  flex-direction:column;
  gap:13px;
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
  min-height:49px;
  padding:0 13px;
  border:1px solid var(--line);
  border-radius:11px;
  background:var(--panel-2);
  color:var(--text);
  font-size:16px;
  outline:none;
  transition:border-color .16s ease,box-shadow .16s ease,background .16s ease;
}
.auth-shell .auth-form-wrap input:focus {
  border-color:var(--fj-violet,var(--accent));
  background:var(--panel);
  box-shadow:0 0 0 4px rgba(146,112,255,.12);
}
.auth-shell .auth-form-wrap .button {
  min-height:49px;
  justify-content:center;
  border-radius:11px;
  font-size:12px;
  font-weight:900;
}
.auth-shell .auth-form-wrap .welcome-back-link {
  margin-top:9px;
}
.auth-shell .auth-form-wrap .muted.small {
  font-size:11px;
  line-height:1.8;
}
.auth-shell .auth-form-wrap button,
.auth-shell .auth-form-wrap a {
  touch-action:manipulation;
}

/* Phone: keep a single column, narrow outer gutters and comfortable touch targets. */
@media (max-width:760px) {
  .auth-shell {
    min-height:100svh;
    padding:16px 8px calc(20px + env(safe-area-inset-bottom,0px));
    place-items:center;
  }
  .auth-shell > .auth-form-wrap {
    width:100%;
    max-width:620px;
    padding:22px 17px 25px;
    border-radius:18px;
  }
  .auth-shell .mobile-brand {
    margin-bottom:21px;
    padding-bottom:15px;
  }
  .auth-shell .auth-form-wrap > h2 {
    font-size:24px;
  }
  .auth-shell .auth-form-wrap .auth-subtitle {
    margin-bottom:18px;
    font-size:11px;
  }
  .auth-shell .auth-form-wrap form {
    gap:12px;
  }
  .auth-shell .auth-form-wrap input,
  .auth-shell .auth-form-wrap .button {
    min-height:48px;
  }
  .auth-shell .auth-form-wrap .field-label {
    font-size:11px;
  }
}

/* Desktop: a wider centered card, with the form itself kept at a readable line length. */
@media (min-width:761px) {
  .auth-shell {
    padding:clamp(34px,5vh,64px) clamp(28px,5vw,88px);
  }
  .auth-shell > .auth-form-wrap {
    width:min(100%,880px);
    max-width:880px;
    padding:52px clamp(48px,6vw,76px) 48px;
    border-radius:24px;
  }
  .auth-shell .mobile-brand {
    margin-bottom:32px;
    padding-bottom:20px;
  }
  .auth-shell .auth-form-wrap > .eyebrow {
    font-size:11px;
  }
  .auth-shell .auth-form-wrap > h2 {
    font-size:32px;
  }
  .auth-shell .auth-form-wrap .auth-subtitle {
    margin-bottom:28px;
    font-size:13px;
  }
  .auth-shell .auth-form-wrap form {
    max-width:660px;
    margin-inline:auto;
    gap:17px;
  }
  .auth-shell .auth-form-wrap .field-label {
    gap:9px;
    font-size:12px;
  }
  .auth-shell .auth-form-wrap input,
  .auth-shell .auth-form-wrap .button {
    min-height:54px;
  }
  .auth-shell .auth-form-wrap .welcome-back-link {
    margin-top:13px;
  }
}

/* Tablet / compact desktop: reduce the card width and horizontal padding gradually. */
@media (min-width:761px) and (max-width:1100px) {
  .auth-shell {
    padding-inline:24px;
  }
  .auth-shell > .auth-form-wrap {
    width:min(100%,720px);
    max-width:720px;
    padding:40px 46px;
  }
}

/* Short viewports scroll naturally instead of clipping the register form. */
@media (max-height:660px) {
  .auth-shell {
    place-items:start center;
    padding-block:14px;
  }
}
@media (prefers-reduced-motion:reduce) {
  .auth-shell *,
  .auth-shell *::before,
  .auth-shell *::after {
    transition-duration:.01ms;
    animation-duration:.01ms;
  }
}
"""
app_path.write_text(app, encoding="utf-8")
css_path.write_text(css, encoding="utf-8")
print("Applied the consolidated responsive authentication layout.")
