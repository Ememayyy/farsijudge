#!/usr/bin/env python3
"""Final mobile-first navigation and layout pass; runs after every visual patch."""
from pathlib import Path

app_path = Path("src/App.tsx")
css_path = Path("src/style.css")
app = app_path.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8")

def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return source.replace(old, new, 1)

if "FJ MOBILE-FIRST NAVIGATION v3" in css:
    raise SystemExit("Mobile-first patch has already been applied.")

app = replace_once(
    app,
    '<button className="mobile-menu-toggle" onClick={() => setSidebarOpen(true)} aria-label="باز کردن منو"><Menu size={21} /></button>',
    '<button className="mobile-menu-toggle" onClick={() => setSidebarOpen((open) => !open)} aria-label={sidebarOpen ? "بستن منو" : "باز کردن منو"} aria-expanded={sidebarOpen}><Menu size={21} /></button>',
    "mobile menu toggle",
)

theme_button = '<button className="icon-button" onClick={() => setTheme(theme === \'dark\' ? \'light\' : \'dark\')} aria-label="تغییر پوسته">{theme === \'dark\' ? <Sun size={18} /> : <Moon size={18} />}</button>'
signout_button = '''<button className="mobile-signout-button" type="button" onClick={async () => {
        if (supabase) await supabase.auth.signOut()
        setSidebarOpen(false)
        setPage('welcome')
      }}>خروج</button>'''
app = replace_once(app, theme_button, theme_button + "\n      " + signout_button, "mobile appbar actions")

state_line = "  const [sidebarOpen, setSidebarOpen] = useState(false)"
effect = """
  
  useEffect(() => {
    const previousOverflow = document.body.style.overflow
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setSidebarOpen(false)
    }
    if (sidebarOpen) {
      document.body.style.overflow = 'hidden'
      window.addEventListener('keydown', closeOnEscape)
    }
    return () => {
      document.body.style.overflow = previousOverflow
      window.removeEventListener('keydown', closeOnEscape)
    }
  }, [sidebarOpen])
"""
app = replace_once(app, state_line, state_line + effect, "mobile drawer state effect")

# The public contest hero shows completed contests, not only contests active right now.
app = replace_once(
    app,
    '<div className="oj-hero-live-count">{fa(active.length)}<span>مسابقهٔ فعال</span></div>',
    '<div className="oj-hero-live-count">{fa(ended.length)}<span>مسابقهٔ برگزارشده</span></div>',
    "completed contest total in public hero",
)

css += r"""

/* FJ MOBILE-FIRST NAVIGATION v3 — deliberately last to override desktop nav styles */
:root { -webkit-text-size-adjust: 100%; }
html, body, #root { width:100%; min-height:100%; }
html, body { max-width:100%; overflow-x:clip; }
body { margin:0; }
*, *::before, *::after { box-sizing:border-box; }
img, svg, video, canvas, iframe { max-width:100%; }
button, a, input, textarea, select { -webkit-tap-highlight-color:transparent; }
button, a { touch-action:manipulation; }
.oj-public-home, .public-site, .auth-page, .auth-shell, .oj-app-shell { width:100%; max-width:100%; min-width:0; }
.oj-public-home, .public-site, .oj-app-shell { overflow-x:clip !important; }
.oj-public-home *, .public-site *, .auth-shell *, .oj-app-shell * { min-width:0; }
.oj-public-home input, .public-site input, .auth-shell input, .oj-app-shell input,
.oj-public-home textarea, .public-site textarea, .auth-shell textarea, .oj-app-shell textarea,
.oj-public-home select, .public-site select, .auth-shell select, .oj-app-shell select { max-width:100%; }

@media (max-width:950px) {
  /* The appbar is always visible; all app destinations live in one vertical drawer. */
  .oj-app-shell { display:block !important; min-height:100svh !important; }
  .oj-app-shell .mobile-appbar {
    position:sticky !important;
    z-index:130 !important;
    top:0 !important;
    right:0 !important;
    left:0 !important;
    width:100% !important;
    height:58px !important;
    min-height:58px !important;
    display:flex !important;
    align-items:center !important;
    justify-content:space-between !important;
    gap:9px !important;
    padding:0 12px !important;
    border-bottom:1px solid var(--line) !important;
    background:color-mix(in srgb,var(--panel) 96%,transparent) !important;
    backdrop-filter:blur(18px);
  }
  .oj-app-shell .mobile-appbar-brand { flex:1 1 auto !important; justify-content:center; font-size:13px !important; }
  .oj-app-shell .mobile-menu-toggle,
  .oj-app-shell .mobile-appbar .icon-button,
  .oj-app-shell .mobile-signout-button {
    flex:0 0 40px !important;
    width:40px !important;
    min-width:40px !important;
    height:40px !important;
    min-height:40px !important;
    display:grid !important;
    place-items:center !important;
    padding:0 !important;
    border:1px solid var(--line) !important;
    border-radius:11px !important;
    background:var(--panel-2) !important;
    color:var(--text) !important;
    font:inherit !important;
    font-size:11px !important;
    font-weight:850 !important;
    cursor:pointer;
  }
  .oj-app-shell .mobile-signout-button { color:#e06b76 !important; border-color:rgba(224,107,118,.28) !important; }
  .oj-app-shell .sidebar {
    position:fixed !important;
    z-index:121 !important;
    top:58px !important;
    right:0 !important;
    bottom:0 !important;
    left:auto !important;
    inset-inline-start:auto !important;
    width:min(340px,calc(100vw - 38px)) !important;
    min-width:0 !important;
    max-width:calc(100vw - 24px) !important;
    height:auto !important;
    min-height:0 !important;
    max-height:none !important;
    margin:0 !important;
    padding:14px 14px calc(14px + env(safe-area-inset-bottom, 0px)) !important;
    display:flex !important;
    flex-direction:column !important;
    align-items:stretch !important;
    justify-content:flex-start !important;
    gap:10px !important;
    overflow:hidden !important;
    border:1px solid var(--line) !important;
    border-top:0 !important;
    border-radius:0 0 0 18px !important;
    background:var(--panel) !important;
    box-shadow:-18px 22px 50px rgba(0,0,0,.2) !important;
    transform:translate3d(110%,0,0) !important;
    visibility:hidden !important;
    pointer-events:none !important;
    transition:transform .22s ease,visibility .22s ease !important;
  }
  .oj-app-shell.sidebar-open .sidebar {
    transform:translate3d(0,0,0) !important;
    visibility:visible !important;
    pointer-events:auto !important;
  }
  .oj-app-shell .sidebar > .brand {
    position:relative !important;
    inset:auto !important;
    width:100% !important;
    min-width:0 !important;
    min-height:45px !important;
    height:45px !important;
    flex:0 0 45px !important;
    margin:0 !important;
    padding:0 7px 9px !important;
    display:flex !important;
    align-items:center !important;
    justify-content:flex-start !important;
    border-bottom:1px solid var(--line);
    font-size:14px !important;
  }
  .oj-app-shell .sidebar .workspace-label {
    display:block !important;
    flex:0 0 auto !important;
    margin:0 5px !important;
    font-size:9px !important;
  }
  .oj-app-shell .sidebar .side-nav {
    position:relative !important;
    inset:auto !important;
    order:0 !important;
    flex:1 1 auto !important;
    width:100% !important;
    min-width:0 !important;
    min-height:0 !important;
    height:auto !important;
    max-height:none !important;
    margin:0 !important;
    padding:4px 1px 12px !important;
    display:flex !important;
    flex-direction:column !important;
    align-items:stretch !important;
    justify-content:flex-start !important;
    gap:6px !important;
    overflow-x:hidden !important;
    overflow-y:auto !important;
    overscroll-behavior:contain;
    -webkit-overflow-scrolling:touch;
    scrollbar-width:thin;
    touch-action:pan-y;
  }
  .oj-app-shell .sidebar .side-nav .nav-item {
    position:relative !important;
    inset:auto !important;
    flex:0 0 auto !important;
    width:100% !important;
    min-width:0 !important;
    min-height:48px !important;
    height:48px !important;
    margin:0 !important;
    padding:0 13px !important;
    display:flex !important;
    align-items:center !important;
    justify-content:flex-start !important;
    gap:10px !important;
    transform:none !important;
    border-radius:11px !important;
    text-align:right !important;
    font-size:12px !important;
  }
  .oj-app-shell .sidebar-bottom {
    position:relative !important;
    inset:auto !important;
    flex:0 0 auto !important;
    width:100% !important;
    min-width:0 !important;
    height:auto !important;
    margin:0 !important;
    padding:11px 0 0 !important;
    display:flex !important;
    flex-direction:column !important;
    align-items:stretch !important;
    gap:8px !important;
    border:0 !important;
    border-top:1px solid var(--line) !important;
    background:transparent !important;
  }
  .oj-app-shell .sidebar-bottom .sidebar-help { display:none !important; }
  .oj-app-shell .sidebar-bottom .user-mini {
    width:100% !important;
    min-height:44px !important;
    margin:0 !important;
    padding:5px 7px !important;
    display:flex !important;
    align-items:center !important;
    gap:9px !important;
    border:0 !important;
  }
  .oj-app-shell .sidebar-bottom .user-mini-info { max-width:none !important; }
  .oj-app-shell .sidebar-scrim {
    position:fixed !important;
    z-index:120 !important;
    inset:58px 0 0 !important;
    width:100% !important;
    height:auto !important;
    margin:0 !important;
    padding:0 !important;
    display:block !important;
    border:0 !important;
    border-radius:0 !important;
    background:rgba(8,12,22,.52) !important;
    opacity:0 !important;
    visibility:hidden !important;
    pointer-events:none !important;
    transition:opacity .2s ease,visibility .2s ease !important;
  }
  .oj-app-shell.sidebar-open .sidebar-scrim {
    opacity:1 !important;
    visibility:visible !important;
    pointer-events:auto !important;
  }
  .oj-app-shell .main-area {
    width:100% !important;
    min-width:0 !important;
    min-height:calc(100svh - 58px) !important;
    margin:0 !important;
  }
  .oj-app-shell .topbar {
    position:sticky !important;
    z-index:60 !important;
    top:58px !important;
    width:100% !important;
    min-width:0 !important;
    min-height:48px !important;
    height:auto !important;
    padding:7px 12px !important;
    gap:8px !important;
  }
  .oj-app-shell .topbar .breadcrumb { min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .oj-app-shell .topbar .top-actions { flex:0 0 auto; gap:5px !important; }
  .oj-app-shell .page-content {
    width:100% !important;
    max-width:100% !important;
    min-width:0 !important;
    margin:0 !important;
    padding:17px 13px 28px !important;
    overflow-x:clip !important;
  }
  .oj-app-shell .footer { width:100% !important; max-width:100% !important; padding:13px !important; }
  .oj-app-shell .admin-layout,
  .oj-app-shell .admin-content-grid,
  .oj-app-shell .profile-layout,
  .oj-app-shell .team-layout,
  .oj-app-shell .dashboard-bottom-grid { grid-template-columns:minmax(0,1fr) !important; }
}

@media (max-width:700px) {
  /* Public landing page: compact two-row header, single-column content. */
  .oj-public-header {
    position:sticky !important;
    top:0 !important;
    z-index:100 !important;
    width:100% !important;
    min-height:0 !important;
    padding:9px 11px 7px !important;
    display:flex !important;
    flex-wrap:wrap !important;
    align-items:center !important;
    gap:7px 9px !important;
  }
  .oj-public-header .oj-brand { flex:1 1 auto; min-width:95px; gap:7px; }
  .oj-public-header .oj-brand-mark { width:32px; height:32px; }
  .oj-public-header .oj-brand b { font-size:12px; }
  .oj-public-header .oj-brand small { font-size:6px; }
  .oj-public-header .oj-public-actions { flex:0 0 auto; margin:0; gap:5px !important; }
  .oj-public-header .oj-theme-toggle,
  .oj-public-header .oj-login-button,
  .oj-public-header .oj-signup-button { min-height:36px !important; height:36px !important; }
  .oj-public-header .oj-theme-toggle { width:36px !important; }
  .oj-public-header .oj-login-button { display:inline-flex !important; align-items:center; justify-content:center; padding:0 9px !important; font-size:10px; }
  .oj-public-header .oj-signup-button { padding:0 9px !important; font-size:9px !important; }
  .oj-public-nav {
    order:3 !important;
    flex:0 0 100% !important;
    width:100% !important;
    height:36px !important;
    min-height:36px !important;
    display:flex !important;
    align-items:center !important;
    gap:5px !important;
    overflow-x:auto !important;
    overflow-y:hidden !important;
    scrollbar-width:none;
    -webkit-overflow-scrolling:touch;
  }
  .oj-public-nav::-webkit-scrollbar { display:none; }
  .oj-public-nav a { flex:0 0 auto; min-height:32px; padding:0 11px !important; white-space:nowrap; }
  .oj-public-main { width:100% !important; max-width:100% !important; padding:13px 11px 25px !important; }
  .oj-public-hero { width:100%; grid-template-columns:minmax(0,1fr) !important; gap:15px !important; padding:19px 15px !important; }
  .oj-public-hero-copy, .oj-public-hero-aside { min-width:0; width:100%; }
  .oj-public-hero h1 { font-size:clamp(31px,9vw,42px) !important; line-height:1.45 !important; overflow-wrap:anywhere; }
  .oj-public-hero-copy>p { font-size:12px !important; line-height:1.95 !important; }
  .oj-public-hero-actions { display:grid !important; grid-template-columns:1fr !important; gap:8px !important; }
  .oj-public-hero-actions button { width:100% !important; min-height:44px !important; justify-content:center; }
  .oj-public-stats { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
  .oj-public-directory, .oj-directory { width:100%; max-width:100%; }
  .oj-public-directory-heading, .oj-directory-head { width:100%; padding:14px !important; display:flex !important; flex-direction:column !important; align-items:stretch !important; }
  .oj-public-directory-heading .oj-search, .oj-directory-head .oj-search { width:100% !important; max-width:none !important; min-width:0 !important; }
  .oj-public-contest-row, .oj-contest-row { width:100%; grid-template-columns:minmax(0,1fr) !important; gap:9px !important; }
  .oj-public-contest-copy, .oj-contest-row-main { overflow-wrap:anywhere; }
  .oj-public-contest-actions, .oj-contest-row-actions { width:100%; display:flex; flex-wrap:wrap; justify-content:flex-start !important; gap:7px; }
  .oj-public-contest-actions button, .oj-contest-row-actions button { min-height:42px !important; }
  .oj-public-bottom { grid-template-columns:minmax(0,1fr) !important; }
  .oj-public-footer { width:100%; flex-wrap:wrap; gap:7px 13px; padding:15px 12px; }
  /* Auth screen */
  .auth-shell { width:calc(100% - 20px) !important; max-width:560px !important; height:auto !important; min-height:0 !important; margin:10px auto 18px !important; display:flex !important; flex-direction:column !important; }
  .auth-visual { min-height:0 !important; padding:17px 16px !important; }
  .auth-visual-content .brand { margin-bottom:12px !important; }
  .auth-visual-content h1 { margin:9px 0 6px !important; font-size:27px !important; }
  .auth-visual-content>p { font-size:11px !important; }
  .auth-form-wrap { min-height:0 !important; padding:19px 16px 22px !important; }
  .auth-form-wrap form { width:100%; gap:12px !important; }
  .auth-form-wrap input, .auth-form-wrap button { min-height:46px !important; }
  /* Dashboard and every internal section */
  .oj-app-shell .page-content { padding:14px 11px 25px !important; }
  .oj-dashboard-heading { align-items:stretch !important; flex-direction:column !important; }
  .oj-dashboard-heading h1 { font-size:22px !important; }
  .oj-dashboard-heading-actions { width:100%; flex-wrap:wrap; }
  .oj-dashboard-heading-actions button { min-height:44px; }
  .oj-dashboard-hero { grid-template-columns:minmax(0,1fr) !important; gap:12px !important; padding:14px !important; }
  .oj-dashboard-hero h2 { font-size:21px !important; overflow-wrap:anywhere; }
  .oj-stat-grid { grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:7px !important; }
  .oj-stat-card { min-width:0; padding:9px !important; gap:7px !important; }
  .oj-stat-card small { white-space:normal !important; line-height:1.5; }
  .oj-directory-toolbar { min-height:0 !important; flex-wrap:wrap !important; padding:9px 10px !important; gap:8px !important; }
  .oj-filter-tabs { max-width:100%; overflow-x:auto; scrollbar-width:none; }
  .oj-filter-tabs button { flex:0 0 auto; min-height:38px; white-space:nowrap; }
  .oj-contest-list { padding:0 11px !important; }
  .oj-app-shell .exam-heading-panel { align-items:stretch !important; flex-direction:column !important; padding:14px !important; }
  .oj-app-shell .exam-heading-panel h1 { font-size:21px !important; overflow-wrap:anywhere; }
  .oj-app-shell .exam-info-grid { grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:7px !important; }
  .oj-app-shell .question-card, .oj-app-shell .question-panel, .oj-app-shell .answer-panel, .oj-app-shell .exam-question { padding:12px !important; }
  .oj-app-shell .admin-layout { grid-template-columns:minmax(0,1fr) !important; }
  .oj-app-shell .admin-side { grid-row:auto !important; }
  .oj-app-shell .team-panel, .oj-app-shell .profile-settings { padding:13px !important; }
  .oj-app-shell .page-title-row { align-items:stretch !important; flex-direction:column !important; }
  .oj-app-shell .page-title-row h1 { font-size:22px !important; }
  .oj-app-shell .registration-options { grid-template-columns:minmax(0,1fr) !important; }
  .oj-app-shell .admin-form, .oj-app-shell .profile-settings-form { grid-template-columns:minmax(0,1fr) !important; }
  .oj-app-shell .admin-form>*,
  .oj-app-shell .profile-settings-form>* { width:100%; max-width:100%; }
  .oj-app-shell .page-content button,
  .oj-app-shell .page-content .button { max-width:100%; }
  .oj-app-shell input, .oj-app-shell textarea, .oj-app-shell select,
  .auth-shell input, .auth-shell textarea, .auth-shell select,
  .oj-public-home input, .oj-public-home textarea, .oj-public-home select {
    min-height:44px !important;
    font-size:16px !important;
  }
  /* Wide tables scroll inside their own panel, never across the whole viewport. */
  .oj-app-shell .table-wrap, .oj-app-shell .table-responsive,
  .oj-app-shell .public-table-wrap, .oj-app-shell .leaderboard-table-wrap,
  .oj-app-shell .admin-table-wrap, .oj-app-shell .data-table-wrap,
  .oj-app-shell .key-table {
    display:block;
    width:100% !important;
    max-width:100% !important;
    overflow-x:auto !important;
    overflow-y:hidden;
    -webkit-overflow-scrolling:touch;
    overscroll-behavior-inline:contain;
  }
  .oj-app-shell table { max-width:100%; }
  .oj-app-shell th, .oj-app-shell td { padding:8px 9px !important; white-space:normal; }
  .public-site .public-main { width:100%; max-width:100%; padding:12px; }
  .public-site .public-header { position:sticky; top:0; z-index:100; flex-wrap:wrap; gap:8px; }
  .public-site .public-nav { max-width:100%; overflow-x:auto; scrollbar-width:none; }
  .public-site .public-nav a { flex:0 0 auto; white-space:nowrap; }
  .public-site .public-table-wrap { width:100%; max-width:100%; overflow-x:auto; -webkit-overflow-scrolling:touch; }
  .public-site .public-contest-table { min-width:620px; }
  .participants-grid { grid-template-columns:minmax(0,1fr) !important; }
}
@media (max-width:390px) {
  .oj-public-header { padding-inline:8px !important; gap:6px !important; }
  .oj-public-header .oj-brand { min-width:90px; }
  .oj-public-header .oj-public-actions { gap:3px !important; }
  .oj-public-header .oj-login-button { padding-inline:6px !important; }
  .oj-public-header .oj-signup-button { padding-inline:7px !important; }
  .oj-public-nav a { padding-inline:9px !important; }
  .oj-public-main { padding-inline:8px !important; }
  .oj-app-shell .exam-info-grid { grid-template-columns:minmax(0,1fr) !important; }
  .oj-app-shell .oj-stat-grid, .oj-app-shell .oj-stat-grid>* { min-width:0; }
}
@media (prefers-reduced-motion:reduce) {
  .oj-app-shell *, .oj-public-home *, .public-site *, .auth-shell * {
    scroll-behavior:auto !important;
    transition-duration:.01ms !important;
    animation-duration:.01ms !important;
    animation-iteration-count:1 !important;
  }
}
@media (max-width:950px) {
  /* Keep the appbar theme switch as the sole mobile theme control. */
  .oj-app-shell .topbar button[aria-label*="پوسته"],
  .oj-app-shell .topbar button[title*="پوسته"],
  .oj-app-shell .topbar button[aria-label*="تم"],
  .oj-app-shell .topbar button[title*="تم"],
  .oj-app-shell .topbar button:has(svg.lucide-sun),
  .oj-app-shell .topbar button:has(svg.lucide-moon) {
    display:none !important;
  }
}
"""
app_path.write_text(app, encoding="utf-8")
css_path.write_text(css, encoding="utf-8")
print("Applied final mobile-first drawer, visible logout action, touch layouts and overflow containment.")
