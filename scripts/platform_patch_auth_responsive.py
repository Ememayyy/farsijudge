#!/usr/bin/env python3
"""Cleanly rebuild the auth markup and replace every accumulated auth override."""
import re
from pathlib import Path

app_path = Path("src/App.tsx")
css_path = Path("src/style.css")
app = app_path.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8")

marker = "FJ AUTH RESPONSIVE REDESIGN v4"
if marker in css:
    raise SystemExit("The v4 authentication redesign is already present.")

def element_end(source: str, start: int, tag: str) -> int:
    tags = re.compile(rf"</?{tag}\b[^>]*>")
    depth = 0
    for match in tags.finditer(source, start):
        token = match.group(0)
        if token.startswith("</"):
            depth -= 1
            if depth == 0:
                return match.end()
        elif not token.rstrip().endswith("/>"):
            depth += 1
    raise SystemExit(f"Could not find closing tag for auth panel {tag}.")

# Remove any old generated desktop panel, then insert exactly one fresh panel.
panel_openings = list(re.finditer(r'<(div|aside)\b[^>]*className="auth-desktop-panel"[^>]*>', app))
if len(panel_openings) > 1:
    raise SystemExit("Multiple old desktop auth panels found; refusing ambiguous cleanup.")
if panel_openings:
    match = panel_openings[0]
    end = element_end(app, match.start(), match.group(1))
    app = app[:match.start()] + app[end:]

form_marker = '        <div className="auth-form-wrap">'
if app.count(form_marker) != 1:
    raise SystemExit("Expected exactly one auth form wrapper.")
if "mobile-brand" not in app or "setAuthMode(authMode === 'login' ? 'register' : 'login')" not in app:
    raise SystemExit("Existing auth branding or login/register switch is missing.")

panel = """      <aside className="auth-desktop-panel" aria-hidden="true">
        <div className="auth-panel-top">
          <div className="auth-panel-brand">
            <span className="auth-panel-brand-mark"><img src={brandLogo} alt="" /></span>
            <span className="auth-panel-brand-copy"><b>فارسی جاج</b><small>FARSI JUDGE</small></span>
          </div>
          <span className="auth-panel-label">ONLINE JUDGE</span>
        </div>
        <div className="auth-panel-center">
          <div className="auth-panel-kicker">THINK · SOLVE · COMPETE</div>
          <h1 className="auth-panel-title">حل کن.<br /><span>پیش برو.</span></h1>
          <div className="auth-panel-art">
            <span className="auth-art-orbit auth-art-orbit-a" />
            <span className="auth-art-orbit auth-art-orbit-b" />
            <span className="auth-art-line" />
            <div className="auth-art-core"><img src={brandLogo} alt="" /></div>
            <span className="auth-art-node auth-art-node-a">01</span>
            <span className="auth-art-node auth-art-node-b">Σ</span>
            <span className="auth-art-node auth-art-node-c">{'{ }'}</span>
          </div>
        </div>
        <div className="auth-panel-bottom"><span>FARSI JUDGE</span><span>BUILT FOR THINKERS</span></div>
      </aside>
"""
app = app.replace(form_marker, panel + form_marker, 1)

# Auth styles are appended last in the build pipeline. Replace that entire tail,
# rather than adding yet another override on top of previous versions.
old_auth = css.find("/* FJ AUTH EXPERIENCE v2")
if old_auth < 0:
    raise SystemExit("Could not locate the accumulated auth CSS tail.")
css = css[:old_auth] + r"""

/* FJ AUTH RESPONSIVE REDESIGN v4 — two deliberately different layouts */
.auth-shell {
  box-sizing:border-box !important;
  width:100% !important;
  max-width:none !important;
  min-width:0 !important;
  min-height:100svh !important;
  margin:0 !important;
  overflow-x:hidden !important;
  background:var(--bg) !important;
}
.auth-shell > .auth-desktop-panel { display:none !important; }
.auth-shell > .auth-form-wrap { box-sizing:border-box !important; min-width:0 !important; }

/* Desktop: a real two-panel composition, with the form and brand occupying
   separate halves of a centered canvas. */
@media (min-width:980px) {
  .auth-shell {
    direction:ltr !important;
    display:grid !important;
    grid-template-columns:minmax(0,.96fr) minmax(0,1.04fr) !important;
    align-items:stretch !important;
    gap:22px !important;
    width:min(1480px,calc(100% - 64px)) !important;
    max-width:1480px !important;
    min-height:calc(100svh - 64px) !important;
    margin:32px auto !important;
    padding:0 !important;
    background:transparent !important;
  }
  .auth-shell > .auth-form-wrap {
    grid-column:1 !important;
    grid-row:1 !important;
    direction:rtl !important;
    display:flex !important;
    flex-direction:column !important;
    align-items:stretch !important;
    justify-content:center !important;
    width:100% !important;
    max-width:none !important;
    min-height:calc(100svh - 64px) !important;
    height:auto !important;
    margin:0 !important;
    padding:clamp(34px,4vw,62px) !important;
    border:1px solid var(--line) !important;
    border-radius:26px !important;
    border-top:1px solid var(--line) !important;
    background:var(--panel) !important;
    box-shadow:0 18px 58px rgba(12,18,38,.10) !important;
  }
  .auth-shell .mobile-brand { display:none !important; }
  .auth-shell .auth-form-wrap > .eyebrow,
  .auth-shell .auth-form-wrap > h2,
  .auth-shell .auth-form-wrap > .auth-subtitle,
  .auth-shell .auth-form-wrap > form,
  .auth-shell .auth-form-wrap > .welcome-back-link {
    width:100%;
    max-width:500px;
    margin-left:auto !important;
    margin-right:auto !important;
  }
  .auth-shell .auth-form-wrap > .eyebrow {
    margin-top:0 !important;
    margin-bottom:9px !important;
    color:var(--fj-violet,var(--accent));
    font-size:11px !important;
    font-weight:900;
  }
  .auth-shell .auth-form-wrap > h2 {
    margin-top:0 !important;
    margin-bottom:8px !important;
    color:var(--text);
    font-size:clamp(28px,2.4vw,35px) !important;
    font-weight:950;
    line-height:1.5;
  }
  .auth-shell .auth-form-wrap .auth-subtitle {
    margin-top:0 !important;
    margin-bottom:27px !important;
    color:var(--muted);
    font-size:13px !important;
    line-height:1.95;
  }
  .auth-shell .auth-form-wrap form {
    display:flex;
    flex-direction:column;
    gap:16px !important;
    width:100%;
  }
  .auth-shell .auth-form-wrap .field-label {
    display:flex;
    flex-direction:column;
    gap:8px;
    color:var(--text);
    font-size:12px !important;
    font-weight:800;
  }
  .auth-shell .auth-form-wrap input {
    box-sizing:border-box;
    width:100%;
    min-width:0;
    min-height:54px !important;
    padding:0 15px !important;
    border:1px solid var(--line);
    border-radius:12px;
    background:var(--panel-2);
    color:var(--text);
    font-size:15px !important;
  }
  .auth-shell .auth-form-wrap input:focus {
    border-color:var(--fj-violet,var(--accent));
    outline:0;
    box-shadow:0 0 0 4px rgba(137,112,232,.12);
  }
  .auth-shell .auth-form-wrap .button {
    min-height:54px !important;
    margin-top:4px;
    border-radius:12px;
    font-size:13px;
    font-weight:900;
  }
  .auth-shell .auth-form-wrap button,
  .auth-shell .auth-form-wrap a { touch-action:manipulation; }

  .auth-shell > .auth-desktop-panel {
    position:relative;
    grid-column:2 !important;
    grid-row:1 !important;
    isolation:isolate;
    display:flex !important;
    flex-direction:column;
    justify-content:space-between;
    min-width:0;
    min-height:calc(100svh - 64px);
    padding:clamp(30px,3.5vw,54px);
    overflow:hidden;
    border:1px solid rgba(255,255,255,.11);
    border-radius:26px;
    direction:rtl;
    color:#fff;
    background:
      radial-gradient(ellipse at 76% 20%,rgba(160,139,255,.29),transparent 24rem),
      radial-gradient(ellipse at 14% 84%,rgba(78,185,219,.18),transparent 25rem),
      linear-gradient(145deg,#18182d 0%,#22243f 58%,#292d4a 100%);
  }
  .auth-shell > .auth-desktop-panel::before {
    position:absolute;
    z-index:-1;
    inset:0;
    content:"";
    opacity:.18;
    background-image:
      linear-gradient(rgba(255,255,255,.09) 1px,transparent 1px),
      linear-gradient(90deg,rgba(255,255,255,.09) 1px,transparent 1px);
    background-size:40px 40px;
    mask-image:linear-gradient(145deg,#000,transparent 85%);
  }
  .auth-shell > .auth-desktop-panel::after {
    position:absolute;
    z-index:-1;
    width:430px;
    height:430px;
    left:-245px;
    bottom:-285px;
    content:"";
    border:1px solid rgba(188,177,255,.2);
    border-radius:50%;
    box-shadow:0 0 0 38px rgba(188,177,255,.035),0 0 0 82px rgba(188,177,255,.025);
  }
  .auth-panel-top,.auth-panel-brand,.auth-panel-brand-copy,.auth-panel-bottom {
    display:flex;
    align-items:center;
  }
  .auth-panel-top { justify-content:space-between; gap:14px; }
  .auth-panel-brand { gap:12px; }
  .auth-panel-brand-mark {
    display:block;
    width:48px;
    height:48px;
    overflow:hidden;
    border:1px solid rgba(255,255,255,.22);
    border-radius:15px;
    background:#fff;
    box-shadow:0 9px 24px rgba(0,0,0,.18);
  }
  .auth-panel-brand-mark img { width:100%; height:100%; object-fit:contain; }
  .auth-panel-brand-copy { flex-direction:column; align-items:flex-start; gap:4px; }
  .auth-panel-brand-copy b { color:#fff; font-size:16px; font-weight:950; }
  .auth-panel-brand-copy small {
    color:rgba(238,235,255,.62);
    direction:ltr;
    font-size:8px;
    font-weight:850;
    letter-spacing:1.7px;
  }
  .auth-panel-label {
    padding:8px 11px;
    border:1px solid rgba(255,255,255,.14);
    border-radius:999px;
    color:rgba(241,239,255,.7);
    direction:ltr;
    font-size:8px;
    font-weight:850;
    letter-spacing:1.3px;
  }
  .auth-panel-center {
    display:flex;
    flex:1;
    flex-direction:column;
    justify-content:center;
    min-height:0;
    padding:24px 0;
  }
  .auth-panel-kicker {
    margin-bottom:14px;
    color:#bcb0ff;
    direction:ltr;
    text-align:right;
    font-size:9px;
    font-weight:900;
    letter-spacing:2px;
  }
  .auth-panel-title {
    position:relative;
    z-index:2;
    margin:0;
    color:#fff;
    font-size:clamp(40px,4.4vw,66px);
    font-weight:950;
    line-height:1.4;
    letter-spacing:-1.5px;
  }
  .auth-panel-title span { color:#bcb0ff; }
  .auth-panel-art {
    position:relative;
    display:grid;
    place-items:center;
    width:min(100%,390px);
    aspect-ratio:1.55;
    margin:8px auto 0;
  }
  .auth-art-orbit {
    position:absolute;
    width:66%;
    height:66%;
    border:1px solid rgba(188,177,255,.25);
    border-radius:50%;
  }
  .auth-art-orbit-a { transform:rotate(-25deg) scaleX(.82); }
  .auth-art-orbit-b {
    width:50%;
    height:92%;
    border-color:rgba(126,210,233,.23);
    transform:rotate(49deg) scaleX(.76);
  }
  .auth-art-line {
    position:absolute;
    width:88%;
    height:1px;
    background:linear-gradient(90deg,transparent,rgba(188,177,255,.55),transparent);
    transform:rotate(-16deg);
  }
  .auth-art-core {
    position:relative;
    z-index:2;
    display:grid;
    place-items:center;
    width:104px;
    height:104px;
    padding:13px;
    border:1px solid rgba(255,255,255,.3);
    border-radius:29px;
    background:rgba(255,255,255,.13);
    box-shadow:0 22px 65px rgba(0,0,0,.25),inset 0 1px rgba(255,255,255,.22);
    backdrop-filter:blur(10px);
  }
  .auth-art-core img { width:100%; height:100%; object-fit:contain; border-radius:15px; }
  .auth-art-node {
    position:absolute;
    z-index:3;
    display:grid;
    place-items:center;
    width:47px;
    height:47px;
    border:1px solid rgba(255,255,255,.17);
    border-radius:15px;
    color:#f2efff;
    background:rgba(255,255,255,.10);
    box-shadow:0 12px 30px rgba(0,0,0,.18);
    font-size:15px;
    font-weight:900;
  }
  .auth-art-node-a { top:10%; right:18%; }
  .auth-art-node-b { bottom:12%; right:13%; color:#a9ead8; font-size:22px; }
  .auth-art-node-c { top:20%; left:14%; font-size:13px; }
  .auth-panel-bottom {
    justify-content:space-between;
    gap:12px;
    padding-top:17px;
    border-top:1px solid rgba(255,255,255,.14);
    color:rgba(237,234,255,.56);
    direction:ltr;
    font-size:8px;
    font-weight:850;
    letter-spacing:1.6px;
  }
}

/* Tablet: keep one comfortable form card; do not squeeze the desktop split. */
@media (min-width:701px) and (max-width:979px) {
  .auth-shell {
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
    min-height:100svh !important;
    padding:28px 24px !important;
    background:
      radial-gradient(ellipse at 50% 0%,rgba(140,112,240,.12),transparent 30rem),
      var(--bg) !important;
  }
  .auth-shell > .auth-desktop-panel { display:none !important; }
  .auth-shell > .auth-form-wrap {
    width:min(100%,620px) !important;
    max-width:620px !important;
    min-height:0 !important;
    height:auto !important;
    margin:auto !important;
    padding:42px 48px !important;
    border:1px solid var(--line) !important;
    border-radius:25px !important;
    background:var(--panel) !important;
    box-shadow:0 22px 68px rgba(15,20,40,.10) !important;
  }
  .auth-shell .mobile-brand { display:flex !important; }
}

/* Mobile: a colored brand header with a wide, floating form card below it. */
@media (max-width:700px) {
  .auth-shell {
    position:relative !important;
    isolation:isolate;
    display:flex !important;
    flex-direction:column !important;
    align-items:center !important;
    justify-content:flex-start !important;
    width:100% !important;
    max-width:none !important;
    min-height:100svh !important;
    height:auto !important;
    margin:0 !important;
    padding:0 14px calc(22px + env(safe-area-inset-bottom,0px)) !important;
    overflow-x:hidden !important;
    overflow-y:auto !important;
    background:var(--bg) !important;
  }
  .auth-shell::before {
    position:absolute;
    z-index:-1;
    top:0;
    left:0;
    right:0;
    height:clamp(185px,29svh,235px);
    content:"";
    border-radius:0 0 28px 28px;
    background:
      radial-gradient(circle at 82% 12%,rgba(191,174,255,.3),transparent 12rem),
      linear-gradient(145deg,#242142 0%,#39315f 58%,#51478b 100%);
  }
  .auth-shell > .auth-desktop-panel { display:none !important; }
  .auth-shell > .auth-form-wrap {
    position:relative;
    z-index:1;
    display:flex !important;
    flex-direction:column !important;
    align-items:stretch !important;
    justify-content:flex-start !important;
    width:100% !important;
    max-width:570px !important;
    min-width:0 !important;
    min-height:0 !important;
    height:auto !important;
    margin:clamp(34px,6svh,52px) auto 0 !important;
    padding:26px clamp(18px,5vw,28px) 29px !important;
    border:1px solid var(--line) !important;
    border-radius:23px !important;
    border-top:1px solid var(--line) !important;
    background:var(--panel) !important;
    box-shadow:0 22px 58px rgba(18,19,44,.17) !important;
  }
  .auth-shell .mobile-brand {
    display:flex !important;
    align-items:center !important;
    gap:11px !important;
    margin:0 0 27px !important;
    padding:0 0 17px !important;
    border-bottom:1px solid var(--line) !important;
    color:var(--text);
  }
  .auth-shell .mobile-brand .brand-mark {
    flex:0 0 42px;
    width:42px;
    height:42px;
    border-radius:13px;
  }
  .auth-shell .mobile-brand b { font-size:15px; font-weight:950; }
  .auth-shell .auth-form-wrap > .eyebrow {
    margin:0 0 7px !important;
    color:var(--fj-violet,var(--accent));
    font-size:10px !important;
    font-weight:900;
  }
  .auth-shell .auth-form-wrap > h2 {
    margin:0 0 7px !important;
    color:var(--text);
    font-size:25px !important;
    line-height:1.5;
    font-weight:950;
  }
  .auth-shell .auth-form-wrap .auth-subtitle {
    margin:0 0 22px !important;
    color:var(--muted);
    font-size:12px !important;
    line-height:1.9;
  }
  .auth-shell .auth-form-wrap form {
    display:flex;
    flex-direction:column;
    gap:13px !important;
    width:100%;
  }
  .auth-shell .auth-form-wrap .field-label {
    display:flex;
    flex-direction:column;
    gap:7px;
    color:var(--text);
    font-size:12px !important;
    font-weight:800;
  }
  .auth-shell .auth-form-wrap input {
    box-sizing:border-box;
    width:100%;
    min-width:0;
    min-height:51px !important;
    padding-inline:13px !important;
    border:1px solid var(--line);
    border-radius:12px;
    background:var(--panel-2);
    color:var(--text);
    font-size:16px !important;
  }
  .auth-shell .auth-form-wrap input:focus {
    border-color:var(--fj-violet,var(--accent));
    outline:0;
    box-shadow:0 0 0 4px rgba(135,111,232,.12);
  }
  .auth-shell .auth-form-wrap .button {
    min-height:51px !important;
    margin-top:3px;
    border-radius:12px;
    font-size:13px;
    font-weight:900;
  }
  .auth-shell .auth-form-wrap button,
  .auth-shell .auth-form-wrap a { touch-action:manipulation; }
  .auth-shell .auth-form-wrap .welcome-back-link { margin-top:11px !important; }
}

@media (max-width:380px) {
  .auth-shell { padding-inline:10px !important; }
  .auth-shell > .auth-form-wrap {
    margin-top:25px !important;
    padding:22px 16px 24px !important;
    border-radius:20px !important;
  }
  .auth-shell .mobile-brand { margin-bottom:22px !important; }
  .auth-shell .auth-form-wrap > h2 { font-size:23px !important; }
  .auth-shell .auth-form-wrap form { gap:11px !important; }
}

@media (max-height:620px) and (min-width:701px) {
  .auth-shell { align-items:start !important; }
  .auth-shell > .auth-form-wrap,
  .auth-shell > .auth-desktop-panel { min-height:0 !important; }
  .auth-shell > .auth-form-wrap { padding-block:28px !important; }
  .auth-shell .auth-form-wrap .auth-subtitle { margin-bottom:16px !important; }
  .auth-shell .auth-form-wrap form { gap:11px !important; }
  .auth-panel-center { padding-block:13px; }
  .auth-panel-art { max-width:280px; }
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
print("Replaced all previous auth CSS layers and normalized the desktop/mobile auth markup.")
