from pathlib import Path

p = Path("src/App.tsx")
s = p.read_text(encoding="utf-8")

# Global interface terminology and brand.
s = s.replace("آزمون‌یار", "فارسی جاج").replace("آزمون", "مسابقه")
s = s.replace("members.length < 3", "members.length < 4")
s = s.replace("از ۳ عضو", "از ۴ عضو")
s = s.replace("یک تیم سه‌نفره", "یک تیم چهار نفره")
s = s.replace("دو عضو دیگر", "سه عضو دیگر")
s = s.replace("حداکثر ۳ عضو", "حداکثر ۴ عضو")

p.write_text(s, encoding="utf-8")
print("Applied Farsi-Judge naming and four-member team labels.")


p = Path("src/App.tsx")
s = p.read_text(encoding="utf-8")

def rep(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(label + ": expected one match, got " + str(n))
    s = s.replace(old, new, 1)

# A member may leave. The database transfers the captain role safely.
rep(
"  const createTeam = async (event: FormEvent) => {",
"""  const leaveTeam = async () => {
    if (!supabase || !window.confirm('از تیم خارج می‌شوید؟ در صورت کاپیتان بودن، مسئولیت به قدیمی‌ترین عضو منتقل می‌شود.')) return
    const { error } = await supabase.rpc('leave_team')
    if (error) notify(error.message, 'error')
    else { notify('از تیم خارج شدید.', 'success'); await loadMainData() }
  }

  const createTeam = async (event: FormEvent) => {""",
"leave-team handler")

rep(
"onCreate={createTeam} onInvite={inviteToTeam} onRespond={respondToInvitation} />}",
"onCreate={createTeam} onInvite={inviteToTeam} onRespond={respondToInvitation} onLeave={leaveTeam} />}",
"TeamPage leave callback")

rep(
"onInvite, onRespond }: {",
"onInvite, onRespond, onLeave }: {",
"TeamPage callback signature")
rep(
"  onRespond: (id: string, accept: boolean) => void\n}) {",
"  onRespond: (id: string, accept: boolean) => void; onLeave: () => void\n}) {",
"TeamPage leave type")

rep(
"      {team.role === 'captain' && <p className=\"muted small\">هر تیم حداکثر یک کاپیتان و دو عضو دیگر دارد.",
"      <button className=\"danger-link\" onClick={onLeave}>ترک تیم <LogOut size={15}/></button>\n      {team.role === 'captain' && <p className=\"muted small\">هر تیم حداکثر سه نفر با احتساب کاپیتان دارد.",
"leave button and capacity text")

# Incoming membership requests get a red notification badge.
rep(
"""<button className={page === 'team' ? 'nav-item selected' : 'nav-item'} onClick={() => setPage('team')}><Users size={19} />تیم و دعوت‌ها</button>""",
"""<button className={page === 'team' ? 'nav-item selected' : 'nav-item'} onClick={() => setPage('team')}><Users size={19} />تیم‌ها{teamInvitations.length > 0 && <b className="nav-badge">{fa(teamInvitations.length)}</b>}</button>""",
"team notification badge")

# The UI permits a member to choose an individual entry; only the captain can select team entry.
rep(
"""        : status === 'upcoming' ? (teamMember && !teamCaptain
          ? <span className="registration-hint">ثبت‌نام تیمی با کاپیتان</span>
          : <button className="button soft small" onClick={onRegister}><UserPlus size={15} />{teamMember ? 'ثبت‌نام تیمی' : 'ثبت‌نام در مسابقه'}</button>)""",
"""        : status === 'upcoming' ? <button className="button soft small" onClick={onRegister}><UserPlus size={15}/>{teamMember && !teamCaptain ? 'ثبت‌نام انفرادی' : 'انتخاب نوع ثبت‌نام'}</button>""",
"individual registration for team member")

# Replace immediate registration with a separate choice screen.
const oldReg = """  const registerForExam = async (exam: Exam) => {
    if (!supabase) return
    if (team && team.role !== 'captain') return notify('برای ثبت‌نام تیمی، از کاپیتان تیم بخواهید اقدام کند.', 'info')
    const { error } = await supabase.rpc('register_for_exam', {
      p_exam_id: exam.id,
      p_team_id: team?.id ?? null,
    })
    if (error) notify('ثبت‌نام انجام نشد: ' + error.message, 'error')
    else {
      notify('ثبت‌نام انجام شد.', 'success')
      await loadMainData()
    }
  }
"""
const newReg = """  const registerForExam = async (exam: Exam) => {
    setSelectedExam(exam)
    setRegistrationKind(team?.role === 'captain' ? 'team' : 'individual')
    setPage('registerExam')
  }

  const confirmRegistration = async () => {
    if (!supabase || !selectedExam) return
    if (registrationKind === 'team' && (!team || team.role !== 'captain')) return notify('ثبت‌نام تیمی فقط توسط کاپیتان امکان‌پذیر است.', 'error')
    setTeamBusy(true)
    const { error } = await supabase.rpc('register_for_exam', {
      p_exam_id: selectedExam.id,
      p_team_id: registrationKind === 'team' ? team!.id : null,
    })
    if (error) notify(error.message, 'error')
    else { notify('ثبت‌نام انجام شد.', 'success'); await loadMainData(); setPage('dashboard') }
    setTeamBusy(false)
  }
"""
rep(oldReg, newReg, "dedicated registration flow")

rep(
"  const [authUsername, setAuthUsername] = useState('')",
"""  const [authUsername, setAuthUsername] = useState('')
  const [registrationKind, setRegistrationKind] = useState<'individual' | 'team'>('individual')""",
"registration kind state")

rep(
"""        {page === 'team' && <TeamPage team={team} members={teamMembers} invitations={teamInvitations}""",
"""        {page === 'registerExam' && selectedExam && <section className="registration-screen">
          <div className="eyebrow">ثبت‌نام مسابقه</div><h1>{selectedExam.title}</h1>
          <p>نوع شرکت را انتخاب کنید. ثبت‌نام تیمی فقط توسط کاپیتان ممکن است.</p>
          <div className="registration-options">
            <button className={registrationKind === 'individual' ? 'chosen' : ''} onClick={() => setRegistrationKind('individual')}><UserRound/><b>شرکت انفرادی</b><small>ثبت‌نام با حساب شخصی شما</small></button>
            <button disabled={!team || team.role !== 'captain'} className={registrationKind === 'team' ? 'chosen' : ''} onClick={() => setRegistrationKind('team')}><Users/><b>شرکت تیمی</b><small>{team?.role === 'captain' ? 'ثبت‌نام تیم ' + team.name : 'فقط کاپیتان می‌تواند تیم را ثبت‌نام کند'}</small></button>
          </div>
          <div className="registration-summary"><span>زمان شروع</span><b>{dateText(selectedExam.starts_at)}</b><span>ظرفیت تیم</span><b>۴ نفر با احتساب کاپیتان</b></div>
          <button className="button primary full" disabled={teamBusy || (registrationKind === 'team' && team?.role !== 'captain')} onClick={confirmRegistration}>تأیید و ثبت‌نام <ChevronLeft/></button>
          <button className="text-link" onClick={() => setPage('dashboard')}>بازگشت</button>
        </section>}
        {page === 'team' && <TeamPage team={team} members={teamMembers} invitations={teamInvitations}""",
"registration page")

p.write_text(s, encoding="utf-8")


# Independent browser-history screens. Hash routes work on GitHub Pages without server rewrites.
p = Path("src/App.tsx")
s = p.read_text(encoding="utf-8")
def rep2(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(label + ": expected one match, got " + str(n))
    s = s.replace(old, new, 1)

rep2(
"type Page = 'dashboard' | 'exam' | 'admin' | 'profile' | 'team'",
"type Page = 'landing' | 'login' | 'register' | 'dashboard' | 'exam' | 'admin' | 'profile' | 'team' | 'registerExam'",
"page route type")
rep2(
"  const [page, setPage] = useState<Page>('dashboard')",
"""  const [page, setPageState] = useState<Page>(() => (window.location.hash.slice(2) as Page) || 'landing')
  const setPage = (next: Page) => {
    window.history.pushState({ page: next }, '', window.location.pathname + '#/' + next)
    setPageState(next)
  }
  useEffect(() => {
    const onPop = () => setPageState((window.location.hash.slice(2) as Page) || 'landing')
    window.addEventListener('popstate', onPop)
    return () => window.removeEventListener('popstate', onPop)
  }, [])
""",
"history routing state")

rep2(
"  const [profiles, setProfiles] = useState<Profile[]>([])",
"""  const [profiles, setProfiles] = useState<Profile[]>([])
  const [mobileMenu, setMobileMenu] = useState(false)
  const [cookieAccepted, setCookieAccepted] = useState(localStorage.getItem('fj-cookie-consent') === 'yes')""",
"mobile and cookie state")

rep2(
"  const isLoggedIn = Boolean(userId)",
"""  const isLoggedIn = Boolean(userId)
  useEffect(() => {
    if (isLoggedIn && page === 'landing') setPage('dashboard')
    if (page === 'register') setAuthMode('register')
    if (page === 'login') setAuthMode('login')
  }, [isLoggedIn, page])""",
"route state synchronization")

rep2(
"  if (!isLoggedIn) {",
"""  if (!isLoggedIn && page === 'landing') return <LandingPage
    onLogin={() => { setAuthMode('login'); setPage('login') }}
    onRegister={() => { setAuthMode('register'); setPage('register') }}
    cookieAccepted={cookieAccepted}
    onCookie={() => { localStorage.setItem('fj-cookie-consent', 'yes'); setCookieAccepted(true) }}
  />

  if (!isLoggedIn) {""",
"public landing branch")

# Keep successful authentication on its own route and preserve the browser back stack.
s = s.replace(
"else if (data.session) notify('حساب شما ساخته شد. خوش آمدید!', 'success')",
"else if (data.session) { notify('حساب فارسی جاج ساخته شد.', 'success'); setPage('dashboard') }"
)
s = s.replace(
"if (error) notify('ورود انجام نشد؛ ایمیل و رمز عبور را بررسی کنید.', 'error')\n      else notify('با موفقیت وارد شدید.', 'success')",
"if (error) notify('ورود انجام نشد؛ ایمیل و رمز عبور را بررسی کنید.', 'error')\n      else { notify('با موفقیت وارد شدید.', 'success'); setPage('dashboard') }"
)
s = s.replace(
"setAuthMode(authMode === 'login' ? 'register' : 'login')",
"setAuthMode(authMode === 'login' ? 'register' : 'login'); setPage(authMode === 'login' ? 'register' : 'login')"
)

# Desktop sidebar on mobile becomes a hamburger drawer with a backdrop.
rep2(
'    <aside className="sidebar">',
'    <aside className={mobileMenu ? "sidebar mobile-open" : "sidebar"}>',
"sidebar drawer")
rep2(
'      <div className="brand"><span className="brand-mark"><GraduationCap size={25} /></span><span>فارسی جاج</span></div>',
'      <div className="brand"><span className="brand-mark"><GraduationCap size={25} /></span><span>فارسی جاج</span><button className="mobile-close" onClick={() => setMobileMenu(false)}><XCircle size={18}/></button></div>',
"sidebar brand mobile close")
rep2(
'        <div className="breadcrumb"><span>فارسی جاج</span>',
'        <div className="breadcrumb"><button className="mobile-menu-toggle" onClick={() => setMobileMenu(true)} aria-label="بازکردن منو"><Menu size={19}/></button><span>فارسی جاج</span>',
"mobile hamburger header")

# Overlay and cookie consent.
rep2(
'    {notice && <div className="toast-wrap"><Notice notice={notice} onClose={() => setNotice(null)} /></div>}',
"""    {mobileMenu && <button className="sidebar-backdrop" onClick={() => setMobileMenu(false)} aria-label="بستن منو"/>}
    {!cookieAccepted && <div className="fj-cookie"><ShieldCheck/><span>برای نگه‌داشتن ورود و ترجیحات از ذخیره‌سازی مرورگر استفاده می‌شود؛ رمز عبور در فارسی جاج ذخیره نمی‌شود.</span><button onClick={() => { localStorage.setItem('fj-cookie-consent','yes'); setCookieAccepted(true) }}>می‌پذیرم</button></div>}
    {notice && <div className="toast-wrap"><Notice notice={notice} onClose={() => setNotice(null)} /></div>}""",
"cookie and drawer overlay")

# Public landing page with concise product positioning.
insert_at = s.index("function Dashboard(")
landing = """function LandingPage({onLogin,onRegister,cookieAccepted,onCookie}:{onLogin:()=>void;onRegister:()=>void;cookieAccepted:boolean;onCookie:()=>void}) {
  return <div className="fj-public-home">
    <header className="fj-public-nav"><div className="fj-brand"><span className="brand-mark"><GraduationCap/></span><b>فارسی جاج</b></div>
      <nav><a href="#fj-features">امکانات</a><a href="#fj-about">درباره فارسی جاج</a></nav>
      <div><button className="button soft" onClick={onLogin}>ورود</button><button className="button primary" onClick={onRegister}>ساخت حساب <ChevronLeft/></button></div>
    </header>
    <section className="fj-public-hero"><div><small className="eyebrow">FARSI-JUDGE / COMPETITIVE PLATFORM</small>
      <h1>رقابت جدی‌تر؛<br/><em>پیشرفت واقعی‌تر.</em></h1>
      <p>فارسی جاج محیطی یکپارچه برای برگزاری مسابقه‌های علمی و برنامه‌نویسی است؛ از ثبت‌نام و رقابت تیمی تا ذخیره پاسخ‌ها، رتبه‌بندی و کارنامه دقیق.</p>
      <div><button className="button primary large" onClick={onRegister}>شروع رقابت <ArrowLeft/></button><button className="button soft large" onClick={onLogin}>ورود به حساب</button></div>
    </div><div className="fj-public-art"><div className="fj-public-orbit"/><div className="fj-public-emblem"><Trophy/><b>FJ</b></div><span>01 · GRAPH THEORY</span></div></section>
    <section className="fj-public-features" id="fj-features"><h2>همه‌چیز برای یک مسابقه حرفه‌ای</h2><div>
      <article><Clock3/><b>زمان‌بندی دقیق</b><p>شروع و پایان کنترل‌شده، شمارش معکوس و تمدید زمان.</p></article>
      <article><Users/><b>رقابت تیمی</b><p>تیم سه‌نفره، دعوت اعضا و پاسخ‌های مشترک.</p></article>
      <article><FileText/><b>صورت مسابقه یکپارچه</b><p>نمایش PDF در سایت یا بازکردن آن در صفحه جدید.</p></article>
      <article><BarChart3/><b>کارنامه تحلیلی</b><p>امتیاز، درصد و بررسی سؤال‌به‌سؤال.</p></article>
      <article><ShieldCheck/><b>امنیت حساب</b><p>نشست تک‌دستگاهی و بررسی ضدربات.</p></article>
      <article><Flag/><b>دسته‌بندی علمی</b><p>تگ‌های رنگی برای گراف، ترکیبیات، الگوریتم و جبر.</p></article>
    </div></section>
    <section className="fj-public-cta" id="fj-about"><small>FARSI-JUDGE</small><h2>برای حل مسئله ساخته شده.</h2><p>بستری حرفه‌ای برای رقابت منصفانه و پیشرفت پیوسته.</p><button className="button primary large" onClick={onRegister}>به فارسی جاج بپیوندید <ArrowLeft/></button></section>
    <footer className="fj-public-footer"><b>فارسی جاج</b><span>رقابت منصفانه، پیشرفت واقعی</span></footer>
    {!cookieAccepted && <div className="fj-cookie"><ShieldCheck/><span>برای نگه‌داشتن ورود و ترجیحات از ذخیره‌سازی مرورگر استفاده می‌شود؛ رمز عبور را ذخیره نمی‌کنیم.</span><button onClick={onCookie}>می‌پذیرم</button></div>}
  </div>
}

"""
s = s[:insert_at] + landing + s[insert_at:]
p.write_text(s, encoding="utf-8")


p = Path("src/App.tsx")
s = p.read_text(encoding="utf-8")

# Icons used by the public landing page and mobile navigation.
s = s.replace(
"ExternalLink,\n",
"ExternalLink, ArrowRight, ArrowUpRight, BarChart3, Bell, CalendarClock, FileText, Flag, Menu, Search, Settings, Sparkles, Trophy, Activity,\n", 1
)
# Cloudflare Turnstile is verified by Supabase Auth; it is not a decorative checkbox.
s = s.replace("import type { FormEvent } from 'react'\n", "import type { FormEvent } from 'react'\nimport { Turnstile } from '@marsidev/react-turnstile'\n", 1)
s = s.replace(
"  const [authUsername, setAuthUsername] = useState('')",
"""  const [authUsername, setAuthUsername] = useState('')
  const [captchaToken, setCaptchaToken] = useState('')
  const [captchaKey, setCaptchaKey] = useState(0)""", 1
)
s = s.replace(
"  const [authMode, setAuthMode] = useState<'login' | 'register'>('login')",
"  const [authMode, setAuthMode] = useState<'login' | 'register'>('login')\n  const turnstileSiteKey = (import.meta.env as ImportMetaEnv & { VITE_TURNSTILE_SITE_KEY?: string }).VITE_TURNSTILE_SITE_KEY || ''",
1
)
# Reject form submissions without a completed challenge whenever Turnstile is configured.
s = s.replace(
"    setAuthBusy(true)\n    if (authMode === 'register') {",
"    if (turnstileSiteKey && !captchaToken) return notify('لطفاً بررسی امنیتی را تکمیل کنید.', 'error')\n    setAuthBusy(true)\n    if (authMode === 'register') {",
1
)
s = s.replace(
"emailRedirectTo: new URL(import.meta.env.BASE_URL, window.location.origin).toString() },",
"emailRedirectTo: new URL(import.meta.env.BASE_URL, window.location.origin).toString(), captchaToken: captchaToken || undefined },",
1
)
s = s.replace(
"supabase.auth.signInWithPassword({ email: authEmail.trim(), password: authPassword })",
"supabase.auth.signInWithPassword({ email: authEmail.trim(), password: authPassword, options: { captchaToken: captchaToken || undefined } })",
1
)
# Activate the single-device session on successful login / immediate signup.
s = s.replace(
"      else notify('با موفقیت وارد شدید.', 'success')",
"      else { const active = await supabase.rpc('activate_my_single_session'); if (active.error) notify(active.error.message, 'error'); else { notify('با موفقیت وارد شدید.', 'success'); setPage('dashboard') } }",
1
)
s = s.replace(
"      else if (data.session) notify('حساب شما ساخته شد. خوش آمدید!', 'success')",
"      else if (data.session) { const active = await supabase.rpc('activate_my_single_session'); if (active.error) notify(active.error.message, 'error'); else { notify('حساب فارسی جاج ساخته شد.', 'success'); setPage('dashboard') } }",
1
)
# Put the real widget inside the authentication form.
constCaptcha = """            {turnstileSiteKey ? <Turnstile key={captchaKey} siteKey={turnstileSiteKey} onSuccess={setCaptchaToken} onExpire={() => setCaptchaToken('')} /> : <small className="captcha-setup-note">برای فعال‌سازی ضدربات، کلید Cloudflare Turnstile را در تنظیمات انتشار قرار دهید.</small>}
"""
s = s.replace('            <button className="button primary full" type="submit" disabled={authBusy}>', constCaptcha + '            <button className="button primary full" type="submit" disabled={authBusy || (Boolean(turnstileSiteKey) && !captchaToken)}>', 1)
# Reset challenge after one authentication attempt.
s = s.replace("    setAuthBusy(false)\n  }\n\n  const enterDemo", "    setAuthBusy(false)\n    setCaptchaToken('')\n    setCaptchaKey((x) => x + 1)\n  }\n\n  const enterDemo", 1)

p.write_text(s, encoding="utf-8")

# Add the widget as an ordinary frontend dependency.
pkg_path = Path("package.json")
pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
pkg.setdefault("dependencies", {})["@marsidev/react-turnstile"] = "^1.3.1"
pkg_path.write_text(json.dumps(pkg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

env_path = Path("src/vite-env.d.ts")
env = env_path.read_text(encoding="utf-8") if env_path.exists() else "/// <reference types=\"vite/client\" />\n"
if "VITE_TURNSTILE_SITE_KEY" not in env:
    env += "\ninterface ImportMetaEnv { readonly VITE_TURNSTILE_SITE_KEY?: string }\n"
env_path.write_text(env, encoding="utf-8")


css_path = Path("src/style.css")
css = css_path.read_text(encoding="utf-8")
css += r"""
:root { --fj-purple:#9668f2; --fj-ink:#08080b; }
[data-theme="dark"] { --bg:#08080b !important; --panel:#111116 !important; --panel2:#191920 !important; }
.nav-badge { margin-right:auto; border-radius:18px; padding:3px 7px; background:#e94f68; color:#fff; font-size:9px; }
.mobile-menu-toggle { display:none; border:1px solid var(--line); border-radius:9px; background:var(--panel); color:var(--text); width:36px; height:36px; place-items:center; margin-left:9px; }
.mobile-close { display:none; margin-right:auto; border:0; background:none; color:var(--muted); }
.sidebar.mobile-open { transform:translateX(0); }
.sidebar-backdrop { display:none; position:fixed; z-index:50; inset:0; background:#0009; border:0; }
.registration-screen { max-width:700px; margin:18px auto; padding:24px; background:var(--panel); border:1px solid var(--line); border-radius:16px; }
.registration-screen h1 { font-size:23px; }
.registration-screen p { color:var(--muted); font-size:10px; line-height:1.9; }
.registration-options { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin:22px 0; }
.registration-options button { display:grid; gap:9px; text-align:right; padding:18px; border:1px solid var(--line); background:var(--panel2); color:var(--text); border-radius:12px; }
.registration-options button.chosen { border-color:var(--fj-purple); background:#9668f21a; }
.registration-options button:disabled { opacity:.45; cursor:not-allowed; }
.registration-options svg { color:var(--fj-purple); }
.registration-options b { font-size:12px; }
.registration-options small { color:var(--muted); font-size:9px; }
.registration-summary { display:grid; grid-template-columns:1fr 1.5fr; gap:11px; padding:15px; background:var(--panel2); border-radius:10px; margin:12px 0; }
.registration-summary span { color:var(--muted); font-size:9px; }
.registration-summary b { font-size:10px; }
.danger-link { color:#ef637a; background:none; border:0; display:inline-flex; align-items:center; gap:6px; padding:9px 0; font-size:10px; }
.fj-public-home { min-height:100vh; background:var(--bg); color:var(--text); }
.fj-public-nav { max-width:1280px; height:72px; margin:auto; padding:0 22px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--line); }
.fj-public-nav nav { display:flex; gap:24px; color:var(--muted); font-size:11px; }
.fj-public-nav>div { display:flex; gap:8px; align-items:center; }
.fj-public-hero { max-width:1280px; margin:auto; min-height:510px; padding:70px 35px; display:grid; grid-template-columns:1fr .85fr; align-items:center; gap:30px; }
.fj-public-hero h1 { font-size:clamp(38px,5vw,65px); line-height:1.5; margin:18px 0; letter-spacing:-1.5px; }
.fj-public-hero h1 em { color:#b18fff; font-style:normal; }
.fj-public-hero p { max-width:630px; font-size:13px; line-height:2.25; color:var(--muted); }
.fj-public-hero>div:first-child>div { display:flex; gap:10px; flex-wrap:wrap; margin-top:26px; }
.fj-public-art { height:350px; display:grid; place-items:center; position:relative; background:radial-gradient(circle,#8957e52b,transparent 62%); }
.fj-public-orbit { position:absolute; width:310px; height:190px; border:1px solid #a47aff62; border-radius:50%; transform:rotate(-23deg); box-shadow:0 0 0 32px #986cff09,0 0 0 64px #986cff06; }
.fj-public-emblem { position:relative; width:160px; height:160px; border-radius:50%; display:grid; place-items:center; color:#c1a4ff; background:#986cff15; animation:fjFloat 5s ease-in-out infinite; }
.fj-public-emblem svg { width:92px; height:92px; stroke-width:1.1; }
.fj-public-emblem b { position:absolute; font-size:22px; }
.fj-public-art>span { position:absolute; top:35px; right:5%; padding:10px 13px; background:#17131f; border:1px solid #986cff65; border-radius:9px; color:#c6b4eb; font-size:9px; direction:ltr; }
.fj-public-features,.fj-public-cta { max-width:1180px; margin:0 auto 70px; padding:0 18px; }
.fj-public-features h2,.fj-public-cta h2 { font-size:25px; margin:12px 0 24px; }
.fj-public-features>div { display:grid; grid-template-columns:repeat(3,1fr); gap:13px; }
.fj-public-features article { display:grid; gap:10px; padding:21px; border:1px solid var(--line); border-radius:14px; background:var(--panel); }
.fj-public-features article svg { color:var(--fj-purple); }
.fj-public-features article b { font-size:12px; }
.fj-public-features article p,.fj-public-cta p { margin:0; color:var(--muted); font-size:10px; line-height:2; }
.fj-public-cta { padding:34px; border:1px solid #986cff44; border-radius:17px; background:radial-gradient(ellipse at 85% 40%,#986cff22,transparent 52%),var(--panel); }
.fj-public-cta small { color:var(--fj-purple); letter-spacing:2px; }
.fj-public-cta p { margin:12px 0 20px; }
.fj-public-footer { max-width:1180px; margin:auto; padding:20px 18px; border-top:1px solid var(--line); display:flex; align-items:center; justify-content:space-between; color:var(--muted); font-size:9px; }
.fj-cookie { position:fixed; z-index:90; bottom:14px; left:14px; right:14px; max-width:750px; margin:auto; padding:14px; border:1px solid var(--line); border-radius:13px; background:var(--panel); display:flex; align-items:center; gap:12px; box-shadow:0 15px 40px #0003; font-size:10px; }
.fj-cookie span { flex:1; color:var(--muted); line-height:1.8; }
.fj-cookie button { border:0; border-radius:8px; background:var(--fj-purple); color:white; padding:9px 13px; font-size:9px; }
.captcha-setup-note { display:block; color:var(--muted); font-size:9px; }
.paper-preview { padding:12px; border:1px solid var(--line); border-radius:12px; background:var(--panel2); margin:12px 0; }
.paper-preview>div { display:flex; align-items:center; gap:8px; margin-bottom:10px; }
.paper-preview>div b { flex:1; font-size:11px; }
.paper-preview a { color:var(--fj-purple); display:flex; align-items:center; gap:5px; font-size:9px; }
.paper-preview iframe { width:100%; height:440px; border:0; border-radius:9px; background:white; }
.paper-download { display:inline-flex; margin-top:10px; color:var(--fj-purple); font-size:9px; }
.contest-controls-editor { display:grid; gap:11px; padding:14px; background:var(--panel2); border:1px solid var(--line); border-radius:12px; }
.contest-controls-editor h3 { margin:0; }
.contest-controls-editor label { display:grid; gap:7px; font-size:10px; }
.contest-controls-editor input,.contest-controls-editor textarea { border:1px solid var(--line); border-radius:8px; padding:10px; background:var(--panel); color:var(--text); }
.admin-tag-picker { display:flex; flex-wrap:wrap; gap:6px; }
.admin-tag-picker button { border:1px solid var(--line); background:var(--panel); border-radius:18px; padding:6px 9px; color:var(--muted); font-size:9px; }
.admin-tag-picker button.picked { color:var(--fj-purple); border-color:var(--fj-purple); background:#986cff16; }
.danger-user-button { display:flex; align-items:center; gap:5px; border:1px solid #ef637a44; background:#ef637a11; color:#ef637a; border-radius:8px; padding:7px 9px; font-size:9px; }
.review-panel { display:grid; gap:8px; margin-top:18px; }
.review-panel h2 { font-size:15px; }
.review-row { display:flex; align-items:center; gap:11px; padding:11px; border:1px solid var(--line); border-radius:10px; background:var(--panel); }
.review-row>span { color:var(--green); }
.review-row.wrong>span,.review-row.wrong em { color:#ef637a; }
.review-row b { flex:1; font-size:10px; }
.review-row small { color:var(--muted); font-size:9px; }
.review-row em { color:var(--green); font-size:9px; font-style:normal; }
@keyframes fjFloat { 50% { transform:translateY(-10px); } }
@media(max-width:760px) {
 .fj-public-nav { height:64px; padding:0 13px; }
 .fj-public-nav nav { display:none; }
 .fj-public-nav>div>.button { display:none; }
 .fj-public-hero { grid-template-columns:1fr; gap:0; padding:25px 16px; }
 .fj-public-art { height:205px; order:-1; }
 .fj-public-emblem { width:115px; height:115px; }
 .fj-public-emblem svg { width:67px; }
 .fj-public-orbit { width:220px; height:138px; }
 .fj-public-hero h1 { font-size:35px; }
 .fj-public-hero p { font-size:11px; }
 .fj-public-features,.fj-public-cta { padding:0 13px; margin-bottom:42px; }
 .fj-public-features h2,.fj-public-cta h2 { font-size:20px; }
 .fj-public-features>div { grid-template-columns:1fr 1fr; gap:8px; }
 .fj-public-features article { padding:14px; }
 .fj-public-features article p { font-size:8px; }
 .fj-public-footer { padding:15px; gap:10px; flex-wrap:wrap; }
 .mobile-menu-toggle { display:grid; width:35px; height:35px; }
 .sidebar { transform:translateX(105%); transition:transform .24s ease; z-index:60; }
 .sidebar.mobile-open { transform:translateX(0); }
 .mobile-close { display:block; }
 .sidebar-backdrop { display:block; }
 .registration-options { grid-template-columns:1fr; }
 .paper-preview iframe { height:380px; }
 .registration-screen { margin:10px; padding:18px; }
 .fj-cookie { left:8px; right:8px; flex-wrap:wrap; }
 .fj-cookie button { width:100%; }
 .contest-detail-grid { grid-template-columns:1fr; }
}
"""
css_path.write_text(css, encoding="utf-8")
