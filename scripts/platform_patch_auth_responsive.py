#!/usr/bin/env python3
"""Replace the accumulated auth CSS with a coherent desktop/mobile experience."""
from pathlib import Path

app_path = Path("src/App.tsx")
css_path = Path("src/style.css")
app = app_path.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8")

if "FJ AUTH RESPONSIVE REDESIGN v3" in css:
    raise SystemExit("The responsive authentication redesign is already present.")
if 'className="auth-desktop-panel"' in app:
    raise SystemExit("A previous desktop auth panel exists; refusing to duplicate it.")

form_marker = '        <div className="auth-form-wrap">'
if app.count(form_marker) != 1:
    raise SystemExit("Expected exactly one authentication form wrapper.")
if "setAuthMode(authMode === 'login' ? 'register' : 'login')" not in app:
    raise SystemExit("Existing sign-in / sign-up switch was not found.")

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

css += r"""

/* FJ AUTH RESPONSIVE REDESIGN v3 — independent desktop and mobile compositions */
.auth-shell > .auth-desktop-panel { display:none !important; }
.auth-shell > .auth-form-wrap { box-sizing:border-box !important; }

@media (min-width:981px) {
  .auth-shell {
    position:relative !important;
    isolation:isolate;
    direction:ltr !important;
    display:grid !important;
    grid-template-columns:minmax(0,1.08fr) minmax(360px,.92fr) !important;
    align-items:stretch !important;
    gap:clamp(16px,2vw,28px) !important;
    width:min(1600px,100%) !important;
    max-width:1600px !important;
    min-height:100svh !important;
    height:auto !important;
    margin:0 auto !important;
    padding:clamp(18px,2.1vw,32px) !important;
    overflow-x:clip !important;
    overflow-y:auto !important;
    background:
      radial-gradient(ellipse at 12% 12%,rgba(140,112,240,.10),transparent 32rem),
      var(--bg) !important;
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
    min-width:0 !important;
    min-height:calc(100svh - clamp(36px,4.2vw,64px)) !important;
    height:auto !important;
    margin:0 !important;
    padding:clamp(30px,4.2vw,64px) !important;
    border:1px solid var(--line) !important;
    border-radius:28px !important;
    border-top:1px solid var(--line) !important;
    background:var(--panel) !important;
    box-shadow:0 24px 75px rgba(15,20,40,.09) !important;
  }
  .auth-shell .auth-form-wrap > *:not(.mobile-brand) {
    width:100%;
    max-width:510px;
    margin-left:auto;
    margin-right:auto;
  }
  .auth-shell .mobile-brand { display:none !important; }
  .auth-shell .auth-form-wrap > .eyebrow {
    margin-top:0 !important;
    margin-bottom:9px !important;
    color:var(--fj-violet,var(--accent));
    font-size:11px !important;
    font-weight:900;
  }
  .auth-shell .auth-form-wrap > h2 {
    margin:0 0 8px !important;
    color:var(--text);
    font-size:clamp(27px,2.3vw,34px) !important;
    line-height:1.5;
    font-weight:950;
  }
  .auth-shell .auth-form-wrap .auth-subtitle {
    margin:0 0 27px !important;
    color:var(--muted);
    font-size:13px !important;
    line-height:2;
  }
  .auth-shell .auth-form-wrap form {
    display:flex;
    flex-direction:column;
    gap:16px !important;
    width:100%;
    margin:0 auto;
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
    min-height:53px !important;
    padding-inline:15px !important;
    border:1px solid var(--line);
    border-radius:12px;
    background:var(--panel-2);
    color:var(--text);
    font-size:15px !important;
  }
  .auth-shell .auth-form-wrap input:focus {
    border-color:var(--fj-violet,var(--accent));
    outline:0;
    box-shadow:0 0 0 4px rgba(135,111,232,.12);
  }
  .auth-shell .auth-form-wrap .button {
    min-height:53px !important;
    margin-top:4px;
    border-radius:12px;
    font-size:13px;
    font-weight:900;
  }
  .auth-shell .auth-form-wrap .welcome-back-link { margin-top:13px !important; }
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
    min-height:calc(100svh - clamp(36px,4.2vw,64px));
    padding:clamp(30px,3.5vw,54px);
    overflow:hidden;
    border:1px solid rgba(255,255,255,.10);
    border-radius:28px;
    direction:rtl;
    color:#fff;
    background:
      radial-gradient(ellipse at 75% 23%,rgba(150,127,255,.26),transparent 23rem),
      radial-gradient(ellipse at 12% 83%,rgba(80,178,219,.17),transparent 24rem),
      linear-gradient(150deg,#17172b 0%,#20223c 54%,#252b49 100%);
  }
  .auth-shell > .auth-desktop-panel::before {
    position:absolute;
    z-index:-1;
    inset:0;
    content:"";
    opacity:.16;
    background-image:
      linear-gradient(rgba(255,255,255,.10) 1px,transparent 1px),
      linear-gradient(90deg,rgba(255,255,255,.10) 1px,transparent 1px);
    background-size:42px 42px;
    mask-image:linear-gradient(135deg,#000 0%,transparent 86%);
  }
  .auth-shell > .auth-desktop-panel::after {
    position:absolute;
    z-index:-1;
    width:430px;
    height:430px;
    left:-250px;
    bottom:-285px;
    content:"";
    border:1px solid rgba(186,174,255,.22);
    border-radius:50%;
    box-shadow:0 0 0 36px rgba(186,174,255,.035),0 0 0 82px rgba(186,174,255,.025);
  }
  .auth-panel-top,.auth-panel-brand,.auth-panel-brand-copy,.auth-panel-bottom {
    display:flex;
    align-items:center;
  }
  .auth-panel-top { justify-content:space-between; gap:15px; }
  .auth-panel-brand { gap:12px; }
  .auth-panel-brand-mark {
    display:grid;
    place-items:center;
    width:48px;
    height:48px;
    overflow:hidden;
    border:1px solid rgba(255,255,255,.28);
    border-radius:15px;
    background:#fff;
    box-shadow:0 9px 24px rgba(0,0,0,.20);
  }
  .auth-panel-brand-mark img { width:100%; height:100%; object-fit:contain; }
  .auth-panel-brand-copy { flex-direction:column; align-items:flex-start; gap:4px; }
  .auth-panel-brand-copy b { color:#fff; font-size:16px; font-weight:950; }
  .auth-panel-brand-copy small {
    color:rgba(236,232,255,.60);
    direction:ltr;
    font-size:8px;
    font-weight:850;
    letter-spacing:1.7px;
  }
  .auth-panel-label {
    padding:8px 11px;
    border:1px solid rgba(255,255,255,.14);
    border-radius:999px;
    color:rgba(241,239,255,.68);
    direction:ltr;
    font-size:8px;
    font-weight:850;
    letter-spacing:1.3px;
  }
  .auth-panel-center {
    position:relative;
    display:flex;
    flex:1;
    flex-direction:column;
    justify-content:center;
    min-height:0;
    padding:28px 0;
  }
  .auth-panel-kicker {
    margin-bottom:15px;
    color:#b9adff;
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
    font-size:clamp(38px,4.1vw,62px);
    font-weight:950;
    line-height:1.38;
    letter-spacing:-1.8px;
  }
  .auth-panel-title span {
    color:#b9adff;
    text-shadow:0 8px 35px rgba(144,121,255,.20);
  }
  .auth-panel-art {
    position:relative;
    width:min(100%,370px);
    aspect-ratio:1.42;
    margin:8px auto 0;
    display:grid;
    place-items:center;
  }
  .auth-art-orbit {
    position:absolute;
    width:68%;
    height:68%;
    border:1px solid rgba(184,171,255,.22);
    border-radius:50%;
    transform:rotate(-24deg) scaleX(.83);
  }
  .auth-art-orbit-a { transform:rotate(-24deg) scaleX(.83); }
  .auth-art-orbit-b {
    width:52%;
    height:92%;
    border-color:rgba(123,207,232,.22);
    transform:rotate(52deg) scaleX(.76);
  }
  .auth-art-line {
    position:absolute;
    width:88%;
    height:1px;
    background:linear-gradient(90deg,transparent,rgba(189,177,255,.55),transparent);
    transform:rotate(-17deg);
  }
  .auth-art-core {
    position:relative;
    z-index:2;
    display:grid;
    place-items:center;
    width:108px;
    height:108px;
    padding:14px;
    border:1px solid rgba(255,255,255,.33);
    border-radius:30px;
    background:linear-gradient(145deg,rgba(255,255,255,.20),rgba(133,111,229,.22));
    box-shadow:0 24px 70px rgba(0,0,0,.25),inset 0 1px rgba(255,255,255,.25);
    backdrop-filter:blur(12px);
  }
  .auth-art-core img { width:100%; height:100%; object-fit:contain; border-radius:17px; }
  .auth-art-node {
    position:absolute;
    z-index:3;
    display:grid;
    place-items:center;
    width:48px;
    height:48px;
    border:1px solid rgba(255,255,255,.17);
    border-radius:15px;
    color:#f0edff;
    background:rgba(255,255,255,.10);
    box-shadow:0 12px 35px rgba(0,0,0,.17);
    backdrop-filter:blur(10px);
    font-size:15px;
    font-weight:900;
  }
  .auth-art-node-a { top:9%; right:18%; }
  .auth-art-node-b { bottom:12%; right:13%; color:#a8ead8; font-size:22px; }
  .auth-art-node-c { top:20%; left:14%; font-size:14px; }
  .auth-panel-bottom {
    justify-content:space-between;
    gap:12px;
    padding-top:17px;
    border-top:1px solid rgba(255,255,255,.14);
    color:rgba(237,234,255,.55);
    direction:ltr;
    font-size:8px;
    font-weight:850;
    letter-spacing:1.6px;
  }
}

@media (min-width:701px) and (max-width:980px) {
  .auth-shell {
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
    min-height:100svh !important;
    padding:24px !important;
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
    border-top:1px solid var(--line) !important;
    background:var(--panel) !important;
    box-shadow:0 22px 68px rgba(15,20,40,.10) !important;
  }
  .auth-shell .mobile-brand { display:flex !important; }
}

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
    overflow-x:clip !important;
    overflow-y:auto !important;
    background:var(--bg) !important;
  }
  .auth-shell::before {
    position:absolute;
    z-index:-1;
    top:0;
    left:0;
    right:0;
    height:clamp(190px,30svh,245px);
    content:"";
    border-radius:0 0 30px 30px;
    background:
      radial-gradient(circle at 82% 12%,rgba(191,174,255,.28),transparent 12rem),
      linear-gradient(145deg,#242142 0%,#37305f 58%,#51478b 100%);
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
    margin:clamp(34px,7svh,58px) auto 0 !important;
    padding:25px clamp(18px,5vw,29px) 29px !important;
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
    margin:0 0 28px !important;
    padding:0 0 18px !important;
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
  .auth-shell .auth-form-wrap .welcome-back-link { margin-top:11px !important; }
  .auth-shell .auth-form-wrap button,
  .auth-shell .auth-form-wrap a { touch-action:manipulation; }
}

@media (max-width:380px) {
  .auth-shell { padding-inline:10px !important; }
  .auth-shell > .auth-form-wrap {
    margin-top:25px !important;
    padding:21px 16px 24px !important;
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
  .auth-shell > .auth-desktop-panel { padding-block:24px; }
  .auth-panel-center { padding-block:14px; }
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
print("Replaced the accumulated auth layout with separate desktop and mobile compositions.")
