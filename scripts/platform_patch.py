from pathlib import Path

p = Path("src/App.tsx")
s = p.read_text(encoding="utf-8")

# Global interface terminology and brand.
s = s.replace("آزمون‌یار", "فارسی جاج").replace("آزمون", "مسابقه")
s = s.replace("members.length < 4", "members.length < 3")
s = s.replace("از ۴ عضو", "از ۳ عضو")
s = s.replace("یک تیم چهار نفره", "یک تیم سه‌نفره")
s = s.replace("سه عضو دیگر", "دو عضو دیگر")
s = s.replace("حداکثر ۴ عضو", "حداکثر ۳ عضو")

p.write_text(s, encoding="utf-8")
print("Applied Farsi-Judge naming and three-member team labels.")


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
          <div className="registration-summary"><span>زمان شروع</span><b>{dateText(selectedExam.starts_at)}</b><span>ظرفیت تیم</span><b>۳ نفر با احتساب کاپیتان</b></div>
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
