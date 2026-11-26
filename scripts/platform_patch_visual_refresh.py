#!/usr/bin/env python3
"""Premium visual refresh for FarsiJudge public, auth, workspace and contest screens."""
from pathlib import Path

app_path = Path("src/App.tsx")
app = app_path.read_text(encoding="utf-8")

def replace_once(old: str, new: str, label: str) -> None:
    global app
    count = app.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    app = app.replace(old, new, 1)

# Sharpen the product message without advertising unfinished judge capabilities.
replace_once(
    '<div className="public-announcement"><span className="announcement-dot" />سامانهٔ مسابقات برنامه‌نویسی، ریاضی و المپیاد <span className="announcement-side">محیط فارسی رقابت</span></div>',
    '<div className="public-announcement"><span className="announcement-dot" />FARSIJUDGE · فضای یکپارچهٔ رقابت علمی <span className="announcement-side">تمرین، رقابت، پیشرفت</span></div>',
    "public announcement"
)
replace_once(
    '<div className="public-kicker"><span>ONLINE CONTEST PLATFORM</span><i />مسابقه، تمرین، پیشرفت</div>',
    '<div className="public-kicker"><span>THINK · SOLVE · COMPETE</span><i />برای قدم بعدی آماده شو</div>',
    "public hero kicker"
)
replace_once(
    '<h1>جای تو در <span>خط شروع</span> مسابقه است.</h1>',
    '<h1>ایده‌هایت را به <span>نتیجه</span> تبدیل کن.</h1>',
    "public hero headline"
)
replace_once(
    '<p>مسابقه‌های پیش‌رو را پیدا کن، انفرادی یا تیمی ثبت‌نام کن و نتیجهٔ تلاش خودت را با کارنامهٔ دقیق ببین.</p>',
    '<p>مسابقه‌های علمی را کشف کن، با دوستانت رقابت کن و مسیر پیشرفتت را با نتایج و تجربهٔ هر مسابقه بساز.</p>',
    "public hero description"
)
replace_once(
    '<h1>تمرکز روی حل مسئله،<br /><span>نه حاشیه‌ها.</span></h1>',
    '<h1>هر مسئله،<br /><span>یک فرصت تازه.</span></h1>',
    "auth visual headline"
)
replace_once(
    '<p>محیطی ساده و امن برای آزمون‌های عددی، با ثبت خودکار پاسخ‌ها و تصحیح دقیق.</p>',
    '<p>وارد فضای رقابت شو؛ مسابقه‌ها را دنبال کن، با دقت حل کن و نتیجهٔ تلاش‌هایت را ثبت کن.</p>',
    "auth visual description"
)
replace_once(
    '<div className="auth-kicker">سامانه برگزاری آزمون آنلاین</div>',
    '<div className="auth-kicker">THINK CLEAR · COMPETE FAIR</div>',
    "auth visual kicker"
)

app_path.write_text(app, encoding="utf-8")

css_path = Path("src/style.css")
css = css_path.read_text(encoding="utf-8")
css += r"""

/* ==========================================================
   FARSIJUDGE VISUAL SYSTEM — premium competitive workspace
   Appended after legacy styles intentionally: this is the
   single visual override layer for the redesigned product.
   ========================================================== */
:root {
  --fj-violet: #9270ff;
  --fj-violet-strong: #7854e9;
  --fj-cyan: #69c8f4;
  --fj-mint: #48d5ad;
  --fj-amber: #f3bc68;
  --fj-border: color-mix(in srgb, var(--line) 82%, var(--fj-violet) 18%);
  --fj-glow: 0 22px 70px rgba(65, 39, 130, .16);
}

html { scroll-behavior: smooth; }
body { text-rendering: optimizeLegibility; -webkit-font-smoothing: antialiased; }
button, input, textarea, select { font: inherit; }
::selection { color: #fff; background: rgba(128, 91, 236, .72); }

/* Public landing page */
.public-site {
  position: relative;
  isolation: isolate;
  min-height: 100vh;
  overflow: clip;
  background:
    radial-gradient(ellipse at 88% 6%, rgba(124, 85, 235, .13), transparent 34rem),
    radial-gradient(ellipse at 8% 48%, rgba(60, 172, 213, .07), transparent 32rem),
    var(--bg);
}
.public-header {
  min-height: 78px;
  padding-inline: max(24px, calc((100vw - 1360px) / 2));
  border-bottom-color: var(--fj-border);
  background: color-mix(in srgb, var(--bg) 78%, transparent);
  box-shadow: 0 8px 36px rgba(0,0,0,.035);
}
.public-brand { gap: 11px; font-size: 16px; letter-spacing: -.25px; }
.public-brand-mark {
  width: 40px; height: 40px; border-radius: 13px;
  background: linear-gradient(145deg, #9b7aff, #6041c8);
  box-shadow: 0 8px 24px rgba(123, 87, 229, .28);
}
.public-brand small { font-size: 8px; letter-spacing: 1.35px; }
.public-nav { height: 78px; gap: 8px; }
.public-nav a {
  position: relative; padding-inline: 14px; border-bottom-width: 2px;
  color: var(--muted); font-size: 11px; transition: color .18s ease, background .18s ease;
}
.public-nav a:hover { color: var(--text); background: color-mix(in srgb, var(--panel) 55%, transparent); }
.public-nav a.current { color: var(--text); font-weight: 800; }
.public-nav a.current::after {
  content: ""; position: absolute; inset-inline: 14px; bottom: -1px; height: 2px;
  border-radius: 4px; background: linear-gradient(90deg, var(--fj-violet), var(--fj-cyan));
}
.public-actions { gap: 9px; }
.public-actions .icon-button { border-radius: 12px; }
.public-login-link { color: var(--text); font-size: 11px; font-weight: 750; }
.public-main { width: min(1360px, 100%); padding: 27px clamp(16px, 3vw, 42px) 44px; }
.public-announcement {
  min-height: 35px; width: fit-content; max-width: 100%;
  display: flex; align-items: center; gap: 9px;
  padding: 7px 12px; border: 1px solid var(--fj-border); border-radius: 999px;
  background: color-mix(in srgb, var(--panel) 78%, transparent);
  color: var(--muted); font-size: 9px; font-weight: 800; letter-spacing: .15px;
}
.announcement-dot { box-shadow: 0 0 0 5px rgba(72,213,173,.1), 0 0 14px rgba(72,213,173,.48); }
.announcement-side { margin-inline-start: 3px; padding-inline-start: 10px; border-inline-start: 1px solid var(--line); color: var(--fj-violet); }
.public-hero {
  position: relative; isolation: isolate; overflow: hidden;
  min-height: 390px; grid-template-columns: minmax(0, 1.15fr) minmax(340px, .85fr);
  gap: clamp(30px, 5vw, 76px); align-items: center;
  margin: 17px 0 22px; padding: clamp(30px, 5vw, 64px);
  border: 1px solid var(--fj-border); border-radius: 30px;
  background:
    radial-gradient(ellipse at 78% 32%, rgba(137, 100, 255, .19), transparent 25rem),
    linear-gradient(120deg, color-mix(in srgb, var(--panel) 92%, #17122c), color-mix(in srgb, var(--panel-2) 94%, #18142b));
  box-shadow: var(--fj-glow);
}
.public-hero::before {
  content: ""; position: absolute; z-index: -1; inset: 0; opacity: .28; pointer-events: none;
  background-image: linear-gradient(rgba(160,140,230,.11) 1px, transparent 1px), linear-gradient(90deg, rgba(160,140,230,.11) 1px, transparent 1px);
  background-size: 42px 42px;
  mask-image: linear-gradient(110deg, transparent 15%, #000 100%);
}
.public-hero::after {
  content: ""; position: absolute; z-index: -1; width: 480px; height: 480px;
  inset-inline-end: -190px; top: -280px; border: 1px solid rgba(170,145,255,.18);
  border-radius: 50%; box-shadow: 0 0 0 35px rgba(170,145,255,.025), 0 0 0 72px rgba(170,145,255,.02);
}
.public-hero-copy { max-width: 670px; }
.public-kicker { gap: 11px; color: var(--muted); font-size: 10px; font-weight: 750; letter-spacing: .2px; }
.public-kicker span { color: #b49aff; font-size: 9px; letter-spacing: 1.7px; }
.public-kicker i { width: 23px; height: 1px; background: linear-gradient(90deg, var(--fj-violet), transparent); }
.public-hero h1 {
  max-width: 640px; margin: 23px 0 12px;
  font-size: clamp(37px, 5vw, 66px); font-weight: 950; line-height: 1.28;
  letter-spacing: -1.5px;
}
.public-hero h1 span {
  color: transparent; background: linear-gradient(100deg, #c0aaff 0%, #8e70ff 47%, #64c9ee 100%);
  -webkit-background-clip: text; background-clip: text;
}
.public-hero-copy > p { max-width: 560px; font-size: 13px; line-height: 2.2; }
.public-hero-actions { gap: 11px; margin-top: 24px; }
.public-hero-actions .button { min-height: 47px; padding-inline: 19px; border-radius: 13px; }
.public-hero-actions .button.primary,
.redesign-shell .button.primary,
.auth-form-wrap .button.primary {
  border: 1px solid rgba(183,160,255,.26);
  background: linear-gradient(110deg, #8c68f2, #6945d3);
  box-shadow: 0 9px 24px rgba(116,79,219,.25), inset 0 1px rgba(255,255,255,.19);
}
.public-hero-actions .button.primary:hover,
.redesign-shell .button.primary:hover,
.auth-form-wrap .button.primary:hover { filter: brightness(1.08); box-shadow: 0 12px 30px rgba(116,79,219,.34); }
.public-hero-actions .button.soft { border: 1px solid var(--fj-border); background: rgba(255,255,255,.035); }
.public-hero-side { min-height: 285px; }
.public-hero-orbit { border-color: rgba(164,139,255,.22); }
.public-orbit-one { width: 345px; height: 345px; }
.public-orbit-two { width: 270px; height: 270px; }
.public-hero-stat-card {
  position: relative; width: min(320px, 90%); padding: 23px;
  border: 1px solid rgba(173,151,255,.24); border-radius: 21px;
  background: color-mix(in srgb, var(--panel) 82%, transparent);
  box-shadow: 0 25px 70px rgba(0,0,0,.2), inset 0 1px rgba(255,255,255,.08);
  backdrop-filter: blur(18px);
}
.public-stat-number { font-size: 48px; font-weight: 950; letter-spacing: -1px; }
.public-stat-foot strong { color: var(--fj-cyan); }
.public-content-grid { gap: 18px; grid-template-columns: minmax(0, 1.9fr) minmax(260px, .78fr); }
.public-panel {
  border-color: var(--fj-border); border-radius: 19px; padding: 21px;
  box-shadow: 0 10px 32px rgba(0,0,0,.04);
  transition: border-color .2s ease, transform .2s ease, box-shadow .2s ease;
}
.public-panel:hover { transform: translateY(-2px); box-shadow: 0 17px 42px rgba(0,0,0,.08); }
.public-panel-heading h2 { font-size: 18px; letter-spacing: -.3px; }
.public-panel-heading p { font-size: 10px; line-height: 1.8; }
.public-panel-kicker { letter-spacing: 1.6px; }
.public-table-wrap { border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }
.public-contest-table th { padding: 13px 12px; font-size: 9px; }
.public-contest-table td { padding: 14px 12px; }
.public-contest-table tbody tr { transition: background .15s ease; }
.public-contest-table tbody tr:hover { background: color-mix(in srgb, var(--panel-2) 72%, transparent); }
.public-contest-table td:first-child b { font-size: 12px; }
.public-row-action { padding: 7px 9px; border: 1px solid var(--fj-border); border-radius: 8px; background: color-mix(in srgb, var(--panel-2) 75%, transparent); font-weight: 750; }
.public-sidebar { gap: 15px; }
.public-auth-card { padding: 23px; }
.public-auth-icon { width: 43px; height: 43px; border-radius: 14px; color: #b8a4ff; }
.public-auth-card h2 { font-size: 17px; }
.public-auth-card p { font-size: 11px; line-height: 2; }
.public-guide-step { padding-block: 11px; }
.public-guide-step > span { border-radius: 9px; }
.public-bottom-info { gap: 15px; margin-top: 19px; }
.public-bottom-info > div { padding: 17px; border-color: var(--fj-border); border-radius: 16px; }
.public-bottom-info b { font-size: 11px; }
.public-bottom-info p { font-size: 10px; }
.public-footer { max-width: 1360px; padding: 20px clamp(16px, 3vw, 42px) 28px; }

/* Authentication: brand stage + focused form panel */
.auth-shell {
  position: relative; isolation: isolate; min-height: 100svh; overflow: hidden;
  grid-template-columns: minmax(0, 1.08fr) minmax(430px, .92fr);
  background:
    radial-gradient(ellipse at 95% 12%, rgba(119,83,223,.13), transparent 33rem),
    radial-gradient(ellipse at 12% 90%, rgba(69,174,215,.07), transparent 30rem),
    var(--bg);
}
.auth-visual {
  position: relative; isolation: isolate; overflow: hidden;
  display: flex; align-items: center; padding: clamp(38px, 7vw, 100px);
  background:
    radial-gradient(ellipse at 18% 18%, rgba(153,119,255,.28), transparent 28rem),
    radial-gradient(ellipse at 88% 80%, rgba(63,176,221,.13), transparent 30rem),
    linear-gradient(145deg, #15112a 0%, #100f1d 58%, #101a27 100%);
  border-inline-end: 1px solid rgba(182,160,255,.15);
}
.auth-visual::before {
  content: ""; position: absolute; z-index: -1; inset: 0; opacity: .42; pointer-events: none;
  background-image: linear-gradient(rgba(176,157,244,.09) 1px, transparent 1px), linear-gradient(90deg, rgba(176,157,244,.09) 1px, transparent 1px);
  background-size: 42px 42px;
  mask-image: linear-gradient(135deg, #000 0%, transparent 88%);
}
.auth-visual::after {
  content: ""; position: absolute; z-index: -1; width: 600px; height: 600px;
  inset-inline-start: -310px; bottom: -380px; border: 1px solid rgba(158,130,255,.24);
  border-radius: 50%; box-shadow: 0 0 0 38px rgba(158,130,255,.035), 0 0 0 82px rgba(158,130,255,.025), 0 0 0 130px rgba(158,130,255,.018);
}
.auth-visual .auth-glow { filter: blur(4px); opacity: .55; }
.auth-visual-content { position: relative; z-index: 2; width: min(650px, 100%); margin-inline: auto; }
.auth-visual-content .brand { margin-bottom: clamp(55px, 9vh, 110px); color: #fff; font-size: 20px; }
.auth-visual-content .brand-mark { width: 48px; height: 48px; border-radius: 15px; box-shadow: 0 10px 27px rgba(111,77,217,.35); }
.auth-kicker { display: inline-flex; align-items: center; gap: 9px; color: #b5a2f4; font-size: 9px; font-weight: 850; letter-spacing: 2px; }
.auth-visual-content h1 { margin: 21px 0 14px; color: #fff; font-size: clamp(38px, 4.4vw, 62px); font-weight: 950; line-height: 1.35; letter-spacing: -1.4px; }
.auth-visual-content h1 span { color: transparent; background: linear-gradient(100deg,#c2adff,#8a70f4 50%,#73c9ec); -webkit-background-clip:text; background-clip:text; }
.auth-visual-content > p { max-width: 510px; color: rgba(235,231,255,.72); font-size: 13px; line-height: 2.25; }
.auth-form-wrap {
  position: relative; display: flex; flex-direction: column; align-items: stretch; justify-content: center;
  width: 100%; max-width: 620px; min-width: 0; margin-inline: auto;
  padding: clamp(30px, 5vw, 74px);
}
.auth-form-wrap > .eyebrow { color: var(--fj-violet); font-size: 10px; font-weight: 850; letter-spacing: 1px; }
.auth-form-wrap > h2 { margin: 10px 0 6px; font-size: clamp(26px, 2.6vw, 34px); font-weight: 900; letter-spacing: -.8px; }
.auth-form-wrap .auth-subtitle { margin: 0 0 24px; font-size: 11px; line-height: 1.9; }
.auth-form-wrap form { display: flex; flex-direction: column; gap: 13px; }
.auth-form-wrap .field-label { gap: 7px; font-size: 10px; font-weight: 800; }
.auth-form-wrap input {
  min-height: 48px; padding: 0 14px; border: 1px solid var(--fj-border); border-radius: 12px;
  background: color-mix(in srgb, var(--panel) 78%, transparent); transition: border-color .18s, box-shadow .18s;
}
.auth-form-wrap input:focus { border-color: var(--fj-violet); box-shadow: 0 0 0 4px rgba(146,112,255,.12); outline: none; }
.auth-form-wrap .button { min-height: 48px; border-radius: 12px; font-weight: 850; }
.auth-form-wrap .muted.small { font-size: 10px; }
.auth-form-wrap .welcome-back-link { color: var(--fj-violet); font-weight: 800; }
.mobile-brand { margin-bottom: 26px; }
.mobile-brand .brand-mark { width: 42px; height: 42px; border-radius: 13px; }

/* Signed-in workspace */
.redesign-shell { background: radial-gradient(ellipse at 80% 0%, rgba(135,103,245,.075), transparent 34rem), var(--bg); }
.redesign-shell .sidebar {
  border-left-color: var(--fj-border);
  background: linear-gradient(180deg, color-mix(in srgb, var(--panel) 96%, #2a1a4b), var(--bg));
  box-shadow: -15px 0 55px rgba(0,0,0,.075);
}
.redesign-shell .brand { padding-bottom: 29px; font-size: 19px; letter-spacing: -.3px; }
.redesign-shell .brand-mark { border-radius: 14px; }
.redesign-shell .workspace-label { letter-spacing: 1.4px; font-size: 9px; }
.redesign-shell .nav-item {
  min-height: 48px; border-radius: 13px; font-size: 11px; font-weight: 720;
}
.redesign-shell .nav-item.selected {
  border-color: rgba(146,112,255,.23);
  background: linear-gradient(100deg, rgba(146,112,255,.18), rgba(146,112,255,.045));
  box-shadow: inset -3px 0 var(--fj-violet), 0 8px 20px rgba(85,58,161,.07);
}
.redesign-shell .main-area { background: transparent; }
.redesign-shell .topbar {
  border-bottom-color: var(--fj-border);
  background: color-mix(in srgb, var(--bg) 83%, transparent);
  backdrop-filter: blur(18px);
}
.redesign-shell .topbar .icon-button { width: 40px; height: 40px; border-radius: 12px; }
.redesign-shell .page-content { padding-top: clamp(20px, 3vw, 38px); }
.redesign-shell .page-title-row { margin-bottom: 21px; }
.redesign-shell .page-title-row h1 { font-size: clamp(23px, 2.7vw, 32px); font-weight: 930; letter-spacing: -.7px; }
.redesign-shell .page-title-row p { max-width: 720px; line-height: 2; }
.redesign-shell .panel-card {
  border-color: var(--fj-border); border-radius: 18px;
  background: color-mix(in srgb, var(--panel) 94%, transparent);
  box-shadow: 0 13px 38px rgba(0,0,0,.045);
}
.redesign-shell .panel-title h2 { font-size: 15px; font-weight: 850; }
.redesign-shell .panel-title p { line-height: 1.9; }
.redesign-shell .button { min-height: 42px; border-radius: 11px; font-weight: 780; }
.redesign-shell .button.soft { border-color: var(--fj-border); background: color-mix(in srgb, var(--panel-2) 80%, transparent); }
.redesign-shell input, .redesign-shell textarea, .redesign-shell select {
  border-color: var(--fj-border); border-radius: 11px; background: color-mix(in srgb, var(--panel-2) 80%, transparent);
}
.redesign-shell input:focus, .redesign-shell textarea:focus, .redesign-shell select:focus {
  border-color: var(--fj-violet); box-shadow: 0 0 0 3px rgba(146,112,255,.12); outline: none;
}
.dashboard-hero {
  min-height: 300px; grid-template-columns: minmax(0,1.25fr) minmax(290px,.75fr);
  gap: 32px; padding: clamp(24px, 3.5vw, 46px);
  border-color: var(--fj-border); border-radius: 25px;
  background:
    radial-gradient(ellipse at 12% 10%, rgba(147,112,255,.18), transparent 27rem),
    radial-gradient(ellipse at 90% 100%, rgba(74,190,224,.08), transparent 28rem),
    linear-gradient(125deg, var(--panel), var(--panel-2));
  box-shadow: var(--fj-glow);
}
.dashboard-hero h1 { font-size: clamp(30px, 3.3vw, 43px); }
.dashboard-hero-copy > p { font-size: 12px; line-height: 2.15; }
.dashboard-next-card { border-color: rgba(165,139,255,.24); border-radius: 17px; }
.dashboard-metrics { margin-block: 19px; gap: 12px; }
.dashboard-metric {
  min-height: 106px; border-color: var(--fj-border); border-radius: 16px;
  background: color-mix(in srgb, var(--panel) 94%, transparent);
}
.dashboard-metric:hover, .dashboard-metric.is-active { border-color: rgba(146,112,255,.48); box-shadow: 0 10px 28px rgba(92,65,167,.09); }
.dashboard-list-panel {
  padding: clamp(16px, 2.4vw, 27px); border: 1px solid var(--fj-border);
  border-radius: 21px; background: color-mix(in srgb, var(--panel) 88%, transparent);
  box-shadow: 0 14px 38px rgba(0,0,0,.04);
}
.dashboard-list-heading h2 { font-size: 20px; font-weight: 900; }
.dashboard-list-heading p { font-size: 10px; }
.dashboard-search { border: 1px solid var(--fj-border); border-radius: 12px; background: var(--panel-2); }
.dashboard-filter { border-radius: 9px; font-size: 10px; }
.dashboard-filter.active { border-color: rgba(146,112,255,.3); background: rgba(146,112,255,.12); color: var(--text); }
.dashboard-list-panel .exam-grid { gap: 14px; }
.dashboard-list-panel .exam-card {
  position: relative; overflow: hidden; padding: 19px; border-color: var(--fj-border);
  border-radius: 17px; background: linear-gradient(145deg, var(--panel-2), color-mix(in srgb, var(--panel) 90%, transparent));
}
.dashboard-list-panel .exam-card::before {
  content: ""; position: absolute; top: 0; inset-inline: 0; height: 2px;
  opacity: .85; background: linear-gradient(90deg, transparent, var(--fj-violet), var(--fj-cyan), transparent);
}
.dashboard-list-panel .exam-card h3 { font-size: 14px; font-weight: 850; }
.dashboard-list-panel .exam-card .exam-description { line-height: 1.9; }
.dashboard-list-panel .exam-card:hover { transform: translateY(-3px); border-color: rgba(146,112,255,.43); box-shadow: 0 14px 35px rgba(80,57,147,.12); }
.exam-card .exam-symbol { border-radius: 12px; }
.exam-card .exam-meta { gap: 8px 14px; flex-wrap: wrap; }
.exam-card .exam-registration { gap: 8px; }

/* Contest room and scoring workspace */
.redesign-shell .exam-info-grid {
  display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 12px; margin-block: 17px;
}
.redesign-shell .exam-info-grid > * {
  min-width: 0; border: 1px solid var(--fj-border); border-radius: 14px;
  background: var(--panel); padding: 14px;
}
.redesign-shell .question-paper-link, .redesign-shell .team-shared-note {
  border: 1px solid var(--fj-border); border-radius: 13px; background: var(--panel);
}
.redesign-shell .question-paper-link { padding: 12px 15px; color: var(--fj-violet); font-weight: 850; }
.redesign-shell .team-shared-note { padding: 12px 15px; }
.redesign-shell .question-card, .redesign-shell .question-panel {
  border: 1px solid var(--fj-border); border-radius: 17px; background: var(--panel);
  box-shadow: 0 10px 28px rgba(0,0,0,.04);
}
.redesign-shell .question-card { padding: 19px; }
.redesign-shell .question-card:focus-within { border-color: rgba(146,112,255,.48); }
.redesign-shell .question-card input { min-height: 48px; font-size: 14px; }
.redesign-shell .exam-timer, .redesign-shell .timer-card {
  border: 1px solid rgba(146,112,255,.26); border-radius: 15px;
  background: linear-gradient(135deg, rgba(146,112,255,.13), rgba(105,200,244,.07));
  font-variant-numeric: tabular-nums;
}
.redesign-shell .exam-status, .redesign-shell .status-badge { border-radius: 999px; }

/* Designer/admin and profile surfaces */
.redesign-shell .admin-layout { gap: 17px; align-items: start; }
.redesign-shell .admin-layout .create-panel { padding: clamp(17px, 2.2vw, 25px); }
.redesign-shell .admin-form { gap: 15px; }
.redesign-shell .question-admin-heading { padding: 13px; border: 1px solid var(--line); border-radius: 12px; background: var(--panel-2); }
.redesign-shell .key-table { overflow: hidden; border: 1px solid var(--line); border-radius: 12px; }
.redesign-shell .admin-exam-row, .redesign-shell .admin-user-row {
  border-color: var(--line); border-radius: 12px; background: color-mix(in srgb, var(--panel-2) 62%, transparent);
}
.redesign-shell .admin-exam-row:hover, .redesign-shell .admin-user-row:hover { border-color: rgba(146,112,255,.38); }
.redesign-shell .profile-settings, .redesign-shell .team-panel { border-radius: 18px; }
.redesign-shell .profile-menu-actions { border-color: var(--fj-border); border-radius: 15px; }
.redesign-shell .avatar { box-shadow: 0 0 0 3px rgba(146,112,255,.1); }

/* Tablet and mobile: use a true single-column reading and contest layout. */
@media (max-width: 1100px) {
  .public-hero { grid-template-columns: minmax(0,1fr) minmax(280px,.8fr); padding: 34px; }
  .public-hero h1 { font-size: clamp(34px, 4.4vw, 52px); }
  .dashboard-hero { grid-template-columns: minmax(0,1fr) minmax(250px,.78fr); }
}
@media (max-width: 900px) {
  .public-header { padding-inline: 18px; }
  .public-main { padding-top: 17px; }
  .public-hero { min-height: unset; }
  .auth-shell { grid-template-columns: minmax(0,1fr) minmax(360px,.95fr); }
  .auth-visual { padding: 34px; }
  .auth-visual-content .brand { margin-bottom: 48px; }
  .auth-visual-content h1 { font-size: clamp(32px, 4vw, 45px); }
  .redesign-shell .page-content { padding-inline: 18px; }
  .dashboard-hero { grid-template-columns: 1fr; }
  .dashboard-next-card { max-width: 520px; }
}
@media (max-width: 700px) {
  .public-header { min-height: 64px; gap: 8px; padding: 8px 13px; }
  .public-brand { font-size: 13px; gap: 8px; }
  .public-brand-mark { width: 34px; height: 34px; border-radius: 11px; }
  .public-nav { height: 40px; gap: 2px; }
  .public-nav a { padding-inline: 10px; font-size: 10px; }
  .public-nav a.current::after { inset-inline: 10px; }
  .public-main { padding: 12px 12px 28px; }
  .public-announcement { width: 100%; justify-content: center; border-radius: 11px; font-size: 8px; }
  .public-announcement .announcement-side { display: none; }
  .public-hero { gap: 10px; margin-block: 12px 15px; padding: 23px 19px; border-radius: 20px; }
  .public-hero h1 { margin-top: 18px; font-size: clamp(31px, 8vw, 42px); line-height: 1.4; letter-spacing: -.8px; }
  .public-hero-copy > p { font-size: 11px; line-height: 2.1; }
  .public-hero-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
  .public-hero-actions .button { justify-content: center; min-width: 0; padding-inline: 8px; font-size: 10px; }
  .public-hero-side { min-height: 210px; }
  .public-hero-stat-card { max-width: 330px; }
  .public-content-grid { grid-template-columns: minmax(0,1fr); gap: 12px; }
  .public-panel { padding: 14px; border-radius: 15px; }
  .public-sidebar { display: flex; }
  .public-bottom-info { grid-template-columns: 1fr; gap: 9px; }
  .public-bottom-info > div { padding: 13px; }
  .public-footer { justify-content: center; text-align: center; }
  .auth-shell { display: flex; flex-direction: column; min-height: 100svh; }
  .auth-visual { min-height: 0; padding: 25px 21px 23px; border-inline-end: 0; border-bottom: 1px solid rgba(182,160,255,.15); }
  .auth-visual-content .brand { margin-bottom: 24px; font-size: 16px; }
  .auth-visual-content .brand-mark { width: 38px; height: 38px; }
  .auth-kicker { font-size: 8px; }
  .auth-visual-content h1 { margin: 13px 0 7px; font-size: clamp(27px, 7vw, 36px); line-height: 1.3; }
  .auth-visual-content > p { margin: 0; font-size: 10px; line-height: 1.85; }
  .auth-form-wrap { max-width: 560px; padding: 26px 21px 36px; }
  .auth-form-wrap > h2 { font-size: 25px; }
  .auth-form-wrap .auth-subtitle { margin-bottom: 17px; }
  .redesign-shell .page-content { padding: 16px 13px 26px; }
  .redesign-shell .topbar { padding-inline: 13px; }
  .dashboard-hero { padding: 20px; border-radius: 19px; }
  .dashboard-hero h1 { font-size: 27px; }
  .dashboard-hero-copy > p { font-size: 10px; }
  .dashboard-hero-actions { display: grid; grid-template-columns: 1fr 1fr; }
  .dashboard-hero-actions .button { min-width: 0; justify-content: center; font-size: 10px; }
  .dashboard-next-card { padding: 14px; }
  .dashboard-list-panel { padding: 14px; border-radius: 16px; }
  .dashboard-list-heading { gap: 10px; }
  .dashboard-list-heading h2 { font-size: 17px; }
  .dashboard-list-panel .exam-grid { grid-template-columns: minmax(0,1fr); }
  .redesign-shell .exam-info-grid { grid-template-columns: repeat(2,minmax(0,1fr)); gap: 8px; }
  .redesign-shell .admin-layout { grid-template-columns: minmax(0,1fr); }
  .redesign-shell .admin-side { grid-row: 1; }
  .redesign-shell .key-table { overflow-x: auto; }
  .redesign-shell .admin-user-row { align-items: flex-start; flex-wrap: wrap; }
  .redesign-shell .profile-settings-form,
  .redesign-shell .profile-settings-form.password-form { grid-template-columns: minmax(0,1fr); }
  .redesign-shell .profile-menu-actions { align-items: stretch; flex-direction: column; }
}
@media (max-width: 390px) {
  .public-actions .public-login-link { display: none; }
  .public-actions .button { min-height: 36px; padding: 7px 9px; font-size: 9px; }
  .public-hero-actions { grid-template-columns: 1fr; }
  .redesign-shell .exam-info-grid { grid-template-columns: minmax(0,1fr); }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  .public-site *, .auth-shell *, .redesign-shell * {
    scroll-behavior: auto !important; animation-duration: .01ms !important;
    animation-iteration-count: 1 !important; transition-duration: .01ms !important;
  }
}
"""
css_path.write_text(css, encoding="utf-8")

# Keep browser and PWA metadata aligned with the new positioning.
index_path = Path("index.html")
if index_path.exists():
    html = index_path.read_text(encoding="utf-8")
    html = html.replace("<title>فارسی جاج | سامانه برگزاری مسابقه آنلاین</title>", "<title>FarsiJudge | رقابت، تمرین، پیشرفت</title>")
    html = html.replace('content="سامانه برگزاری مسابقه آنلاین با پاسخ عددی و تصحیح خودکار"', 'content="FarsiJudge؛ فضای یکپارچه برای مسابقات علمی، تمرین و پیشرفت."')
    index_path.write_text(html, encoding="utf-8")

print("Applied FarsiJudge premium visual system.")
