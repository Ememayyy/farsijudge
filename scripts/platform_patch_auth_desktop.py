#!/usr/bin/env python3
"""Give the desktop sign-in and sign-up screens a balanced two-column layout."""
from pathlib import Path

app_path = Path("src/App.tsx")
css_path = Path("src/style.css")
app = app_path.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8")

if "FJ AUTH DESKTOP EXPERIENCE v1" in css or "auth-desktop-panel" in app:
    raise SystemExit("Desktop authentication layout has already been applied.")

form_marker = '        <div className="auth-form-wrap">'
if app.count(form_marker) != 1:
    raise SystemExit("Expected exactly one authentication form wrapper.")
panel = """      <div className="auth-desktop-panel" aria-hidden="true">
        <div className="auth-desktop-brand">
          <span className="auth-desktop-brand-mark">ف</span>
          <span className="auth-desktop-brand-text"><b>فارسی جاج</b><small>FARSI JUDGE</small></span>
        </div>
        <div className="auth-desktop-art">
          <span className="auth-desktop-orbit auth-desktop-orbit-one" />
          <span className="auth-desktop-orbit auth-desktop-orbit-two" />
          <span className="auth-desktop-art-core">FJ</span>
          <span className="auth-desktop-art-chip auth-desktop-chip-one">01</span>
          <span className="auth-desktop-art-chip auth-desktop-chip-two">{ }</span>
          <span className="auth-desktop-art-chip auth-desktop-chip-three">∑</span>
          <span className="auth-desktop-art-chip auth-desktop-chip-four">✓</span>
        </div>
        <div className="auth-desktop-footer"><span>FARSI JUDGE</span><span>ONLINE JUDGE</span></div>
      </div>
"""
app = app.replace(form_marker, panel + form_marker, 1)

css += r"""

/* FJ AUTH DESKTOP EXPERIENCE v1 — brand-led split layout, no repeated feature copy */
@media (min-width:961px) {
  .auth-shell {
    direction:ltr !important;
    display:grid !important;
    grid-template-columns:minmax(0,1.08fr) minmax(440px,.92fr) !important;
    align-items:stretch !important;
    width:min(1220px,calc(100% - 88px)) !important;
    max-width:1220px !important;
    min-height:640px !important;
    height:auto !important;
    margin:40px auto !important;
    padding:0 !important;
    overflow:hidden !important;
    border:1px solid var(--line) !important;
    border-radius:29px !important;
    background:var(--panel) !important;
    box-shadow:0 32px 100px rgba(0,0,0,.17),0 5px 24px rgba(100,75,180,.08) !important;
  }
  .auth-shell > .auth-desktop-panel {
    position:relative;
    isolation:isolate;
    grid-column:1;
    grid-row:1;
    min-width:0;
    min-height:640px;
    padding:clamp(34px,4.6vw,58px);
    display:flex !important;
    flex-direction:column;
    align-items:stretch;
    justify-content:space-between;
    overflow:hidden;
    direction:rtl;
    color:#fff;
    background:
      radial-gradient(ellipse at 23% 17%,rgba(159,130,255,.30),transparent 22rem),
      radial-gradient(ellipse at 83% 84%,rgba(77,189,222,.17),transparent 21rem),
      linear-gradient(145deg,#17172b 0%,#1c1e37 52%,#202744 100%);
  }
  .auth-shell > .auth-desktop-panel::before {
    position:absolute;
    z-index:-1;
    inset:0;
    content:"";
    opacity:.20;
    background-image:linear-gradient(rgba(255,255,255,.075) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.075) 1px,transparent 1px);
    background-size:38px 38px;
    mask-image:linear-gradient(135deg,#000,transparent 78%);
  }
  .auth-shell > .auth-desktop-panel::after {
    position:absolute;
    z-index:-1;
    width:380px;
    height:380px;
    left:-190px;
    bottom:-220px;
    content:"";
    border:1px solid rgba(183,166,255,.18);
    border-radius:50%;
    box-shadow:0 0 0 32px rgba(183,166,255,.035),0 0 0 70px rgba(183,166,255,.025);
  }
  .auth-desktop-brand {
    display:flex;
    align-items:center;
    gap:13px;
    width:max-content;
    max-width:100%;
  }
  .auth-desktop-brand-mark {
    display:grid;
    place-items:center;
    flex:0 0 48px;
    width:48px;
    height:48px;
    border:1px solid rgba(255,255,255,.24);
    border-radius:15px;
    color:#fff;
    background:linear-gradient(145deg,rgba(167,147,255,.38),rgba(103,85,205,.22));
    box-shadow:0 12px 32px rgba(0,0,0,.18),inset 0 1px rgba(255,255,255,.18);
    font-size:25px;
    font-weight:950;
  }
  .auth-desktop-brand-text {
    display:flex;
    flex-direction:column;
    gap:4px;
  }
  .auth-desktop-brand-text b { color:#fff; font-size:17px; font-weight:950; }
  .auth-desktop-brand-text small {
    color:rgba(232,228,255,.65);
    direction:ltr;
    text-align:right;
    font-size:8px;
    font-weight:850;
    letter-spacing:1.8px;
  }
  .auth-desktop-art {
    position:relative;
    width:min(100%,430px);
    aspect-ratio:1;
    margin:18px auto;
    display:grid;
    place-items:center;
    flex:0 1 auto;
  }
  .auth-desktop-orbit {
    position:absolute;
    inset:10%;
    border:1px solid rgba(185,170,255,.23);
    border-radius:50%;
    transform:rotate(-28deg) scaleX(.82);
  }
  .auth-desktop-orbit-one { inset:7%; }
  .auth-desktop-orbit-two {
    inset:20%;
    border-color:rgba(139,205,235,.25);
    transform:rotate(38deg) scaleX(.78);
  }
  .auth-desktop-art-core {
    position:relative;
    z-index:2;
    width:39%;
    aspect-ratio:1;
    display:grid;
    place-items:center;
    border:1px solid rgba(255,255,255,.28);
    border-radius:31%;
    color:#fff;
    background:linear-gradient(145deg,#9180ef,#6255bd 68%,#4b76a7);
    box-shadow:0 24px 75px rgba(5,7,22,.35),inset 0 1px rgba(255,255,255,.35);
    font-size:clamp(38px,5vw,66px);
    font-weight:950;
    letter-spacing:-5px;
  }
  .auth-desktop-art-chip {
    position:absolute;
    z-index:3;
    display:grid;
    place-items:center;
    width:56px;
    height:56px;
    border:1px solid rgba(255,255,255,.17);
    border-radius:17px;
    color:#f4f1ff;
    background:rgba(255,255,255,.10);
    box-shadow:0 15px 40px rgba(0,0,0,.18);
    backdrop-filter:blur(12px);
    font-size:16px;
    font-weight:900;
  }
  .auth-desktop-chip-one { top:14%; right:17%; }
  .auth-desktop-chip-two { right:5%; bottom:22%; font-size:20px; }
  .auth-desktop-chip-three { bottom:10%; left:23%; font-size:22px; }
  .auth-desktop-chip-four { top:22%; left:10%; color:#a9f0dc; font-size:23px; }
  .auth-desktop-footer {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    padding-top:17px;
    border-top:1px solid rgba(255,255,255,.14);
    color:rgba(235,232,255,.58);
    direction:ltr;
    font-size:8px;
    font-weight:850;
    letter-spacing:1.8px;
  }
  .auth-shell > .auth-form-wrap {
    grid-column:2;
    grid-row:1;
    width:100% !important;
    max-width:none !important;
    min-height:640px !important;
    height:100% !important;
    margin:0 !important;
    padding:clamp(38px,4.6vw,62px) !important;
    display:flex !important;
    flex-direction:column !important;
    justify-content:center !important;
    direction:rtl;
    border:0 !important;
    border-radius:0 !important;
    box-shadow:none !important;
    background:var(--panel) !important;
  }
  .auth-shell .mobile-brand { display:none !important; }
  .auth-shell .auth-form-wrap > .eyebrow { margin-top:0 !important; }
  .auth-shell .auth-form-wrap > h2 { font-size:clamp(28px,2.5vw,34px) !important; }
  .auth-shell .auth-form-wrap .auth-subtitle { margin-bottom:29px !important; font-size:13px; }
  .auth-shell .auth-form-wrap form { gap:17px !important; }
  .auth-shell .auth-form-wrap .field-label { font-size:12px; }
  .auth-shell .auth-form-wrap input { min-height:53px !important; font-size:15px; }
  .auth-shell .auth-form-wrap .button { min-height:53px !important; font-size:13px; }
}
@media (min-width:701px) and (max-width:960px) {
  .auth-shell {
    width:min(560px,calc(100% - 48px)) !important;
    max-width:560px !important;
    min-height:600px !important;
    height:auto !important;
    margin:32px auto !important;
    grid-template-columns:minmax(0,1fr) !important;
    place-items:center !important;
  }
  .auth-shell > .auth-desktop-panel { display:none !important; }
  .auth-shell > .auth-form-wrap {
    grid-column:1;
    grid-row:1;
    width:100% !important;
    max-width:none !important;
    min-height:600px !important;
    height:auto !important;
    margin:0 !important;
  }
  .auth-shell .mobile-brand { display:flex !important; }
}
@media (max-width:700px) {
  .auth-shell {
    grid-template-columns:minmax(0,1fr) !important;
    direction:rtl !important;
  }
  .auth-shell > .auth-desktop-panel { display:none !important; }
  .auth-shell > .auth-form-wrap {
    grid-column:1;
    grid-row:1;
    height:auto !important;
  }
  .auth-shell .mobile-brand { display:flex !important; }
}
@media (min-width:961px) and (max-height:720px) {
  .auth-shell { min-height:0 !important; margin-block:24px !important; }
  .auth-shell > .auth-desktop-panel,
  .auth-shell > .auth-form-wrap { min-height:0 !important; }
  .auth-shell > .auth-form-wrap { padding-block:30px !important; }
  .auth-shell .auth-form-wrap .auth-subtitle { margin-bottom:18px !important; }
  .auth-shell .auth-form-wrap form { gap:12px !important; }
}
"""
app_path.write_text(app, encoding="utf-8")
css_path.write_text(css, encoding="utf-8")
print("Applied a brand-led split desktop auth layout; mobile auth remains single-column.")
