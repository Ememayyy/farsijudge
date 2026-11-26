#!/usr/bin/env python3
"""Second-generation FarsiJudge layouts: contest hub, workspace, auth and contest room."""
from pathlib import Path
import re

app_path = Path("src/App.tsx")
css_path = Path("src/style.css")
app = app_path.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8")

def replace_region(source, start, end, replacement, label):
    a = source.find(start)
    b = source.find(end, a + len(start)) if a >= 0 else -1
    if a < 0 or b < 0:
        raise SystemExit(label + ": component boundary not found")
    return source[:a] + replacement.rstrip() + "\n\n" + source[b:]

dashboard = r'''
function Dashboard({ exams, profile, now, onOpen, onAdmin, isAdmin, isDemo, myRegistrations, myTeamRegistrations, team, onRegister, onReviewQuestions, onLeaderboard }: {
  exams: Exam[]; profile: Profile | null; now: number; onOpen: (exam: Exam) => void; onAdmin: () => void
  isAdmin: boolean; isDemo: boolean; myRegistrations: string[]; myTeamRegistrations: string[]
  team: Team | null; onRegister: (exam: Exam) => void
  onReviewQuestions: (exam: Exam) => void; onLeaderboard: (exam: Exam) => void
}) {
  const [filter, setFilter] = useState<'all' | 'active' | 'upcoming' | 'ended'>('all')
  const [search, setSearch] = useState('')
  const active = exams.filter((exam) => getStatus(exam, now) === 'active')
  const upcoming = exams.filter((exam) => getStatus(exam, now) === 'upcoming').sort((a, b) => new Date(a.starts_at).getTime() - new Date(b.starts_at).getTime())
  const ended = exams.filter((exam) => getStatus(exam, now) === 'ended')
  const firstName = profile?.full_name?.trim().split(/\s+/)[0] || 'خوش آمدید'
  const registered = new Set([...myRegistrations, ...myTeamRegistrations])
  const next = upcoming[0]
  const list = (filter === 'active' ? active : filter === 'upcoming' ? upcoming : filter === 'ended' ? ended : exams)
    .filter((exam) => (exam.title + ' ' + (exam.description || '') + ' ' + (exam.tags || []).join(' ')).toLocaleLowerCase().includes(search.trim().toLocaleLowerCase()))
    .sort((a, b) => {
      const rank = (x: Exam) => getStatus(x, now) === 'active' ? 0 : getStatus(x, now) === 'upcoming' ? 1 : 2
      return rank(a) - rank(b) || new Date(a.starts_at).getTime() - new Date(b.starts_at).getTime()
    })
  return <div className="oj-dashboard">
    <header className="oj-dashboard-heading">
      <div><div className="oj-overline">CONTEST WORKSPACE</div><h1>سلام، {firstName}</h1><p>مسابقه‌ها و فعالیت‌های رقابتی خودت را از یک‌جا مدیریت کن.</p></div>
      <div className="oj-dashboard-heading-actions">{isDemo && <span className="oj-demo-label">حالت نمایشی</span>}{isAdmin && <button className="button primary" onClick={onAdmin}><Plus size={16} /> ساخت مسابقه</button>}</div>
    </header>
    <section className="oj-dashboard-hero">
      <div className="oj-dashboard-hero-copy"><span className="oj-live-label"><i /> مرکز مسابقات</span><h2>{next ? 'مسابقهٔ بعدی نزدیک است.' : 'برای چالش بعدی آماده‌ای؟'}</h2>
        <p>{next ? 'برای مسابقهٔ «' + next.title + '» آماده شو و زمان شروع را از دست نده.' : 'مسابقه‌های منتشرشده را بررسی کن یا مسائل قبلی را برای تمرین دوباره مرور کن.'}</p>
        <div className="oj-hero-actions"><button className="button primary" onClick={() => document.getElementById('oj-contest-directory')?.scrollIntoView({behavior:'smooth'})}>مرور مسابقه‌ها <ArrowLeft size={16} /></button>{team && <span className="oj-team-chip"><Users size={14} />{team.name}</span>}</div>
      </div>
      <aside className="oj-next-contest"><div className="oj-next-contest-head"><CalendarDays size={16} /><span>مسابقهٔ پیش‌رو</span></div>
        {next ? <><b>{next.title}</b><span className="oj-next-date">{dateText(next.starts_at)} · {fa(next.duration_minutes)} دقیقه</span><CountdownDisplay seconds={Math.max(0, Math.ceil((new Date(next.starts_at).getTime() - now) / 1000))} compact /><button className="oj-text-action" onClick={() => onOpen(next)}>مشاهدهٔ جزئیات <ArrowLeft size={14} /></button></> : <div className="oj-next-empty">در حال حاضر مسابقهٔ آینده‌ای ثبت نشده است.</div>}
      </aside>
    </section>
    <section className="oj-stat-grid" aria-label="آمار حساب">
      <button className={filter === 'all' ? 'oj-stat-card is-selected' : 'oj-stat-card'} onClick={() => setFilter('all')}><span className="oj-stat-icon violet"><Trophy size={18} /></span><span><small>همهٔ مسابقه‌ها</small><strong>{fa(exams.length)}</strong></span></button>
      <button className={filter === 'active' ? 'oj-stat-card is-selected' : 'oj-stat-card'} onClick={() => setFilter('active')}><span className="oj-stat-icon green"><i /></span><span><small>در حال برگزاری</small><strong>{fa(active.length)}</strong></span></button>
      <button className={filter === 'upcoming' ? 'oj-stat-card is-selected' : 'oj-stat-card'} onClick={() => setFilter('upcoming')}><span className="oj-stat-icon blue"><CalendarDays size={18} /></span><span><small>مسابقه‌های آینده</small><strong>{fa(upcoming.length)}</strong></span></button>
      <div className="oj-stat-card oj-stat-card-static"><span className="oj-stat-icon amber"><CheckCircle2 size={18} /></span><span><small>ثبت‌نام‌های من</small><strong>{fa(registered.size)}</strong></span></div>
    </section>
    <section className="oj-directory" id="oj-contest-directory">
      <div className="oj-directory-head"><div><div className="oj-overline">CONTESTS</div><h2>فهرست مسابقه‌ها</h2><p>مسابقهٔ موردنظرت را پیدا کن و وارد صفحهٔ آن شو.</p></div><label className="oj-search"><Search size={17} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="جست‌وجوی عنوان یا موضوع..." /></label></div>
      <div className="oj-directory-toolbar"><div className="oj-filter-tabs">{([['all','همه'],['active','فعال'],['upcoming','آینده'],['ended','پایان‌یافته']] as const).map(([value,label]) => <button key={value} className={filter === value ? 'active' : ''} onClick={() => setFilter(value)}>{label}<span>{value === 'all' ? exams.length : value === 'active' ? active.length : value === 'upcoming' ? upcoming.length : ended.length}</span></button>)}</div><span className="oj-results-count">{fa(list.length)} مسابقه</span></div>
      <div className="oj-contest-list">
        {list.map((exam) => {
          const status = getStatus(exam, now)
          const isRegistered = registered.has(exam.id)
          return <article className="oj-contest-row" key={exam.id}>
            <div className="oj-contest-row-status"><StatusBadge status={status} /><span>{fa(exam.duration_minutes)} دقیقه</span></div>
            <div className="oj-contest-row-main"><button className="oj-contest-title" onClick={() => onOpen(exam)}>{exam.title}</button><p>{exam.description || 'مسابقهٔ آنلاین فارسی جاج'}</p><ContestTagList tags={exam.tags} compact /><div className="oj-contest-row-meta"><span><CalendarDays size={13} />{dateText(exam.starts_at)}</span>{isRegistered && <span className="oj-registered"><CheckCircle2 size={13} />ثبت‌نام‌شده</span>}</div></div>
            <div className="oj-contest-row-actions">
              {status === 'upcoming' && !isRegistered && <button className="button soft small" onClick={() => onRegister(exam)}><UserPlus size={14} /> ثبت‌نام</button>}
              {status === 'active' && <button className="button primary small" disabled={!isRegistered} onClick={() => onOpen(exam)}>{isRegistered ? 'ورود به مسابقه' : 'ثبت‌نام لازم است'}</button>}
              {status === 'ended' && <><button className="button soft small" onClick={() => onReviewQuestions(exam)}>صورت سؤال</button><button className="button soft small" onClick={() => onLeaderboard(exam)}>رتبه‌بندی</button></>}
              {status === 'upcoming' && <button className="oj-icon-action" aria-label="جزئیات مسابقه" onClick={() => onOpen(exam)}><ArrowLeft size={17} /></button>}
            </div>
          </article>
        })}
        {list.length === 0 && <div className="oj-empty-state"><Search size={25} /><b>{exams.length === 0 ? 'هنوز مسابقه‌ای منتشر نشده است' : 'مسابقه‌ای با این مشخصات پیدا نشد'}</b><p>{exams.length === 0 ? 'مسابقه‌های جدید پس از انتشار در این فهرست قرار می‌گیرند.' : 'فیلتر یا عبارت جست‌وجو را تغییر بده.'}</p></div>}
      </div>
    </section>
    <div className="oj-dashboard-footnote"><ShieldCheck size={15} />پاسخ‌های مسابقه‌های فعال به‌صورت خودکار ذخیره می‌شوند.</div>
  </div>
}
'''
app = replace_region(app, "function Dashboard(", "\nfunction StatusBadge(", dashboard, "Dashboard component")

# Keep the shared statistic tile used by ProfilePage, independently of the new dashboard.
stat_component = """
function StatCard(props: any) {
  const label = props.label || props.title || props.name || ''
  const value = props.value ?? props.count ?? props.total ?? '—'
  const detail = props.description || props.subtitle || props.detail || props.caption || ''
  return <div className={'stat-card oj-shared-stat ' + (props.className || '')}>
    {props.icon && <span className="oj-shared-stat-icon">{props.icon}</span>}
    <span className="oj-shared-stat-copy">
      {label && <small>{label}</small>}
      <strong>{value}</strong>
      {detail && <em>{detail}</em>}
    </span>
  </div>
}
"""
if "function StatCard(" not in app:
    app = app.replace("\\nfunction StatusBadge(", "\\n" + stat_component + "\\nfunction StatusBadge(", 1)

# Remove imports that belonged only to the old dashboard markup.
app = app.replace("CalendarDays, ChevronDown, Home, Menu, Search, Sparkles, Trophy,", "CalendarDays, Menu, Search, Trophy,")
lines = app.splitlines()
for index, line in enumerate(lines):
    if "from 'react'" in line or 'from "react"' in line:
        line = re.sub(r'\\b(?:type\\s+)?ReactNode\\s*,\\s*', '', line)
        line = re.sub(r',\\s*(?:type\\s+)?ReactNode\\b', '', line)
        lines[index] = line
app = "\\n".join(lines) + "\\n"


welcome = r'''
function WelcomePage({ theme, onToggleTheme, onLogin, onRegister, onDemo, showDemo, exams, now, onReviewQuestions, onLeaderboard }: {
  theme: 'light' | 'dark'; onToggleTheme: () => void; onLogin: () => void
  onRegister: () => void; onDemo: () => void; showDemo: boolean; exams: Exam[]; now: number
  onReviewQuestions: (exam: Exam) => void; onLeaderboard: (exam: Exam) => void
}) {
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState<'all' | 'upcoming' | 'active' | 'ended'>('all')
  const publicExams = exams.filter((exam) => exam.is_published).sort((a, b) => new Date(a.starts_at).getTime() - new Date(b.starts_at).getTime())
  const upcoming = publicExams.filter((exam) => getStatus(exam, now) === 'upcoming')
  const active = publicExams.filter((exam) => getStatus(exam, now) === 'active')
  const ended = publicExams.filter((exam) => getStatus(exam, now) === 'ended')
  const next = upcoming[0]
  const visible = (filter === 'upcoming' ? upcoming : filter === 'active' ? active : filter === 'ended' ? ended : publicExams)
    .filter((exam) => (exam.title + ' ' + (exam.description || '') + ' ' + (exam.tags || []).join(' ')).toLocaleLowerCase().includes(query.trim().toLocaleLowerCase()))
  return <div className="oj-public-home">
    <header className="oj-public-header">
      <a className="oj-brand" href="#oj-home"><span className="oj-brand-mark"><img src={import.meta.env.BASE_URL + 'fj-logo.svg'} alt="FJ" /></span><span><b>فارسی جاج</b><small>ONLINE JUDGE & CONTESTS</small></span></a>
      <nav className="oj-public-nav"><a className="active" href="#oj-home">خانه</a><a href="#oj-public-contests">مسابقه‌ها</a><a href="#oj-about">درباره</a></nav>
      <div className="oj-public-actions"><button className="oj-theme-toggle" onClick={onToggleTheme} aria-label="تغییر پوسته">{theme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}</button><button className="oj-login-button" onClick={onLogin}>ورود</button><button className="oj-signup-button" onClick={onRegister}>ساخت حساب <ArrowLeft size={15} /></button></div>
    </header>
    <main id="oj-home" className="oj-public-main">
      <section className="oj-public-hero">
        <div className="oj-public-hero-copy"><div className="oj-public-kicker"><span />پلتفرم رقابت و حل مسئله</div><h1>فکر کن. حل کن.<br /><em>رتبه‌ات را بساز.</em></h1><p>مسابقه‌های برنامه‌نویسی و المپیادی را پیدا کن، در رقابت شرکت کن و مسیر پیشرفتت را با نتیجه‌های واقعی دنبال کن.</p><div className="oj-public-hero-actions"><button className="oj-cta-primary" onClick={onRegister}>شروع رقابت <ArrowLeft size={17} /></button><button className="oj-cta-secondary" onClick={() => document.getElementById('oj-public-contests')?.scrollIntoView({behavior:'smooth'})}>دیدن مسابقه‌ها</button></div>{showDemo && <button className="oj-demo-link" onClick={onDemo}>مشاهدهٔ نسخهٔ نمایشی</button>}</div>
        <aside className="oj-public-hero-aside"><div className="oj-hero-card-top"><span className="oj-live-pulse" /> وضعیت رقابت‌ها <small>LIVE</small></div><div className="oj-hero-live-count">{fa(active.length)}<span>مسابقهٔ فعال</span></div><div className="oj-hero-divider" /><div className="oj-hero-stat-line"><span>مسابقهٔ آینده</span><b>{next ? dateText(next.starts_at) : 'اعلام نشده'}</b></div><div className="oj-hero-stat-line"><span>مسابقه‌های آرشیوشده</span><b>{fa(ended.length)}</b></div>{next && <div className="oj-hero-next"><b>{next.title}</b><CountdownDisplay seconds={Math.max(0, Math.ceil((new Date(next.starts_at).getTime() - now) / 1000))} compact /></div>}</aside>
        <div className="oj-hero-decoration oj-hero-decoration-one" /><div className="oj-hero-decoration oj-hero-decoration-two" />
      </section>
      <section className="oj-public-stats"><div><b>{fa(publicExams.length)}</b><span>مسابقهٔ منتشرشده</span></div><div><b>{fa(upcoming.length)}</b><span>مسابقهٔ پیش‌رو</span></div><div><b>{fa(active.length)}</b><span>در حال برگزاری</span></div><div><b>{fa(ended.length)}</b><span>در آرشیو</span></div></section>
      <section id="oj-public-contests" className="oj-public-directory">
        <div className="oj-public-directory-heading"><div><div className="oj-overline">CONTEST CALENDAR</div><h2>مسابقه‌های عمومی</h2><p>برنامهٔ رقابت‌های آینده و نتایج مسابقه‌های گذشته</p></div><label className="oj-search"><Search size={16} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="جست‌وجوی مسابقه..." /></label></div>
        <div className="oj-directory-toolbar"><div className="oj-filter-tabs">{([['all','همه'],['upcoming','پیش‌رو'],['active','فعال'],['ended','پایان‌یافته']] as const).map(([value,label]) => <button key={value} className={filter === value ? 'active' : ''} onClick={() => setFilter(value)}>{label}</button>)}</div><span className="oj-results-count">{fa(visible.length)} نتیجه</span></div>
        <div className="oj-public-contest-list">
          {visible.map((exam) => {
            const status = getStatus(exam, now)
            return <article className="oj-public-contest-row" key={exam.id}>
              <div className="oj-public-contest-indicator"><StatusBadge status={status} /></div>
              <div className="oj-public-contest-copy"><b>{exam.title}</b><p>{exam.description || 'مسابقهٔ علمی فارسی جاج'}</p><ContestTagList tags={exam.tags} compact /><small><CalendarDays size={12} />{dateText(exam.starts_at)} · {fa(exam.duration_minutes)} دقیقه</small></div>
              <div className="oj-public-contest-actions">{status === 'ended' ? <><button onClick={() => onReviewQuestions(exam)}>صورت سؤال</button><button onClick={() => onLeaderboard(exam)}>رتبه‌بندی</button></> : <button className="primary" onClick={status === 'upcoming' ? onRegister : onLogin}>{status === 'upcoming' ? 'ثبت‌نام' : 'ورود به مسابقه'} <ArrowLeft size={14} /></button>}</div>
            </article>
          })}
          {visible.length === 0 && <div className="oj-empty-state"><CalendarDays size={25} /><b>مسابقه‌ای برای این فیلتر پیدا نشد</b><p>فیلتر دیگری انتخاب کن یا بعداً دوباره سر بزن.</p></div>}
        </div>
      </section>
      <section className="oj-public-bottom" id="oj-about"><div><span>01</span><b>یک حساب بساز</b><p>پروفایل خودت را داشته باش و در مسابقه‌ها ثبت‌نام کن.</p></div><div><span>02</span><b>حل مسئله را شروع کن</b><p>در مسابقه‌های انفرادی یا تیمی شرکت کن.</p></div><div><span>03</span><b>نتیجه‌ات را دنبال کن</b><p>پس از انتشار نتایج، صورت سؤال و رتبه‌بندی را ببین.</p></div></section>
    </main>
    <footer className="oj-public-footer"><b>FARSI JUDGE</b><span>پلتفرمی برای فکر کردن، رقابت کردن و پیشرفت.</span><span>© {new Date().getFullYear()} FarsiJudge</span></footer>
  </div>
}
'''
app = replace_region(app, "function WelcomePage(", "\nfunction RegistrationPage(", welcome, "WelcomePage component")
app = app.replace("آزمون‌یار", "فارسی جاج")
app = app.replace('className={"app-shell redesign-shell " + (sidebarOpen ? "sidebar-open" : "")}', 'className={"app-shell redesign-shell oj-app-shell " + (sidebarOpen ? "sidebar-open" : "")}', 1)
app_path.write_text(app, encoding="utf-8")

css += r"""
/* FJ SECOND GENERATION — independent layouts for public, auth, workspace and contests */
:root { --oj-accent:#8b73f6; }
html[data-theme="dark"] { --bg:#0d111b; --panel:#141b29; --panel-2:#192335; --line:rgba(151,169,199,.16); --text:#edf2fb; --muted:#8d9bb1; --accent:#8b73f6; color-scheme:dark; }
html[data-theme="light"] { --bg:#f3f5fa; --panel:#fff; --panel-2:#f7f8fc; --line:#e2e7f0; --text:#20283a; --muted:#758096; --accent:#7357dc; color-scheme:light; }
body { background:var(--bg); color:var(--text); }
button { -webkit-tap-highlight-color:transparent; }
button:focus-visible,a:focus-visible,input:focus-visible,textarea:focus-visible,select:focus-visible { outline:2px solid color-mix(in srgb,var(--accent) 78%,white); outline-offset:3px; }

/* Public contest hub */
.oj-public-home { min-height:100vh; color:var(--text); background:radial-gradient(ellipse at 75% -10%,rgba(109,86,220,.17),transparent 36rem),var(--bg); }
.oj-public-header { position:sticky; z-index:80; top:0; min-height:76px; padding:0 max(22px,calc((100vw - 1320px)/2)); display:flex; align-items:center; justify-content:space-between; gap:24px; border-bottom:1px solid var(--line); background:color-mix(in srgb,var(--bg) 92%,transparent); backdrop-filter:blur(18px); }
.oj-brand { display:flex; align-items:center; gap:11px; color:var(--text); text-decoration:none; white-space:nowrap; }
.oj-brand-mark { width:40px; height:40px; padding:4px; border-radius:12px; display:grid; place-items:center; background:linear-gradient(145deg,#9177ff,#5a46ba); box-shadow:0 8px 22px rgba(100,77,204,.25); }
.oj-brand-mark img { width:100%; height:100%; object-fit:contain; }
.oj-brand>span:last-child { display:flex; flex-direction:column; gap:3px; }
.oj-brand b { font-size:15px; font-weight:900; }
.oj-brand small { color:var(--muted); font:700 8px/1.2 ui-sans-serif,system-ui,sans-serif; letter-spacing:1.15px; }
.oj-public-nav { height:76px; display:flex; align-items:stretch; gap:5px; }
.oj-public-nav a { display:grid; place-items:center; padding:0 17px; color:var(--muted); border-bottom:2px solid transparent; text-decoration:none; font-size:11px; font-weight:700; }
.oj-public-nav a:hover,.oj-public-nav a.active { color:var(--text); border-bottom-color:var(--oj-accent); }
.oj-public-actions { display:flex; align-items:center; gap:9px; }
.oj-theme-toggle,.oj-login-button { min-height:39px; border:1px solid var(--line); border-radius:10px; padding:0 12px; color:var(--text); background:var(--panel); cursor:pointer; font:inherit; font-size:11px; font-weight:800; }
.oj-theme-toggle { width:39px; display:grid; place-items:center; padding:0; }
.oj-signup-button { min-height:40px; padding:0 14px; display:flex; align-items:center; gap:8px; border:1px solid rgba(161,141,255,.34); border-radius:10px; color:#fff; background:linear-gradient(120deg,#8d70ee,#654fc1); cursor:pointer; font:inherit; font-size:11px; font-weight:850; }
.oj-public-main { width:min(1320px,100%); margin:0 auto; padding:34px clamp(16px,3.2vw,42px) 38px; }
.oj-public-hero { position:relative; isolation:isolate; overflow:hidden; min-height:340px; padding:clamp(25px,4vw,50px); display:grid; grid-template-columns:minmax(0,1.3fr) minmax(270px,.7fr); align-items:center; gap:35px; border:1px solid var(--line); border-radius:22px; background:linear-gradient(115deg,rgba(117,91,216,.13),transparent 54%),var(--panel); }
.oj-public-hero::before { content:""; position:absolute; z-index:-1; inset:0; opacity:.24; pointer-events:none; background-image:linear-gradient(rgba(159,146,211,.12) 1px,transparent 1px),linear-gradient(90deg,rgba(159,146,211,.12) 1px,transparent 1px); background-size:34px 34px; mask-image:linear-gradient(110deg,#000,transparent 88%); }
.oj-public-hero-copy { position:relative; z-index:2; max-width:650px; }
.oj-public-kicker { display:flex; align-items:center; gap:9px; color:var(--muted); font-size:11px; font-weight:750; }
.oj-public-kicker>span { width:8px; height:8px; border-radius:50%; background:#43c99c; box-shadow:0 0 0 5px rgba(67,201,156,.1); }
.oj-public-hero h1 { margin:20px 0 13px; font-size:clamp(36px,5.2vw,64px); line-height:1.27; letter-spacing:-1.4px; font-weight:950; }
.oj-public-hero h1 em { color:transparent; background:linear-gradient(100deg,#b9aaff,#8975f2 55%,#5fc9d9); -webkit-background-clip:text; background-clip:text; font-style:normal; }
.oj-public-hero-copy>p { max-width:570px; color:var(--muted); font-size:13px; line-height:2.15; }
.oj-public-hero-actions { display:flex; flex-wrap:wrap; gap:10px; margin-top:23px; }
.oj-cta-primary,.oj-cta-secondary { min-height:45px; padding:0 17px; border-radius:11px; display:flex; align-items:center; justify-content:center; gap:9px; cursor:pointer; font:inherit; font-size:11px; font-weight:850; }
.oj-cta-primary { border:1px solid rgba(179,160,255,.24); color:#fff; background:linear-gradient(115deg,#9073f1,#6651c9); box-shadow:0 9px 22px rgba(99,76,202,.22); }
.oj-cta-secondary { border:1px solid var(--line); color:var(--text); background:var(--panel-2); }
.oj-demo-link { margin-top:13px; padding:0; border:0; background:transparent; color:#a995ff; font:inherit; font-size:10px; cursor:pointer; }
.oj-public-hero-aside { position:relative; z-index:2; padding:21px; border:1px solid rgba(155,139,233,.2); border-radius:17px; background:color-mix(in srgb,var(--panel-2) 80%,transparent); box-shadow:0 20px 50px rgba(0,0,0,.14); }
.oj-hero-card-top { display:flex; align-items:center; gap:8px; color:var(--muted); font-size:10px; font-weight:800; }
.oj-hero-card-top small { margin-inline-start:auto; color:#43c99c; letter-spacing:1px; font-size:8px; }
.oj-live-pulse { width:7px; height:7px; border-radius:50%; background:#43c99c; box-shadow:0 0 0 4px rgba(67,201,156,.12); }
.oj-hero-live-count { display:flex; align-items:baseline; gap:10px; margin:18px 0; font-size:42px; line-height:1; font-weight:950; font-variant-numeric:tabular-nums; }
.oj-hero-live-count span { color:var(--muted); font-size:12px; font-weight:650; }
.oj-hero-divider { height:1px; background:var(--line); margin:16px 0; }
.oj-hero-stat-line { display:flex; align-items:center; justify-content:space-between; gap:12px; margin-top:10px; font-size:10px; }
.oj-hero-stat-line span { color:var(--muted); }
.oj-hero-stat-line b { color:var(--text); font-size:10px; }
.oj-hero-next { margin-top:16px; padding:13px; border-radius:11px; background:rgba(139,115,246,.1); border:1px solid rgba(139,115,246,.17); }
.oj-hero-next>b { display:block; font-size:11px; }
.oj-hero-decoration { position:absolute; z-index:0; border:1px solid rgba(149,129,234,.16); border-radius:50%; pointer-events:none; }
.oj-hero-decoration-one { width:360px; height:360px; left:-220px; top:-230px; }
.oj-hero-decoration-two { width:220px; height:220px; left:-150px; top:-160px; }
.oj-public-stats { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); margin:16px 0 27px; border:1px solid var(--line); border-radius:14px; background:var(--panel); overflow:hidden; }
.oj-public-stats>div { min-width:0; display:flex; align-items:center; gap:12px; padding:15px 19px; border-inline-start:1px solid var(--line); }
.oj-public-stats>div:last-child { border-inline-start:0; }
.oj-public-stats b { font-size:22px; font-weight:900; font-variant-numeric:tabular-nums; }
.oj-public-stats span { color:var(--muted); font-size:10px; }
.oj-public-directory { border:1px solid var(--line); border-radius:17px; background:var(--panel); overflow:hidden; }
.oj-public-directory-heading { display:flex; align-items:flex-end; justify-content:space-between; gap:15px; padding:22px 23px 17px; }
.oj-public-directory-heading h2,.oj-directory-head h2 { margin:6px 0 4px; font-size:20px; font-weight:900; }
.oj-public-directory-heading p,.oj-directory-head p { margin:0; color:var(--muted); font-size:11px; line-height:1.8; }
.oj-search { min-width:min(260px,100%); min-height:40px; padding:0 11px; display:flex; align-items:center; gap:8px; border:1px solid var(--line); border-radius:10px; background:var(--panel-2); color:var(--muted); }
.oj-search input { width:100%; min-width:0; border:0; outline:0; background:transparent; color:var(--text); font:inherit; font-size:11px; }
.oj-directory-toolbar { min-height:48px; padding:0 22px; display:flex; align-items:center; justify-content:space-between; gap:12px; border-top:1px solid var(--line); border-bottom:1px solid var(--line); background:var(--panel-2); }
.oj-filter-tabs { display:flex; align-items:stretch; gap:5px; height:48px; overflow-x:auto; }
.oj-filter-tabs button { min-width:max-content; padding:0 12px; border:0; border-bottom:2px solid transparent; background:transparent; color:var(--muted); font:inherit; font-size:10px; cursor:pointer; }
.oj-filter-tabs button.active { border-bottom-color:var(--oj-accent); color:var(--text); font-weight:850; }
.oj-results-count { color:var(--muted); font-size:10px; white-space:nowrap; }
.oj-public-contest-list { padding:0 22px; }
.oj-public-contest-row { display:grid; grid-template-columns:112px minmax(0,1fr) auto; align-items:center; gap:16px; padding:17px 0; border-bottom:1px solid var(--line); }
.oj-public-contest-row:last-child { border-bottom:0; }
.oj-public-contest-copy { min-width:0; }
.oj-public-contest-copy>b { font-size:13px; font-weight:850; }
.oj-public-contest-copy>p { margin:5px 0 0; color:var(--muted); font-size:10px; line-height:1.7; }
.oj-public-contest-copy>small { display:flex; align-items:center; gap:6px; margin-top:9px; color:var(--muted); font-size:9px; }
.oj-public-contest-copy .contest-tag-list { margin-top:7px; }
.oj-public-contest-actions { display:flex; justify-content:flex-end; gap:6px; }
.oj-public-contest-actions button { min-height:33px; padding:0 10px; display:flex; align-items:center; justify-content:center; gap:5px; border:1px solid var(--line); border-radius:8px; background:var(--panel-2); color:var(--text); cursor:pointer; font:inherit; font-size:9px; font-weight:800; white-space:nowrap; }
.oj-public-contest-actions button.primary { border-color:rgba(139,115,246,.24); background:rgba(139,115,246,.13); color:#a996ff; }
.oj-public-contest-indicator .status-badge { white-space:nowrap; }
.oj-public-bottom { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin-top:15px; }
.oj-public-bottom>div { padding:17px 19px; border:1px solid var(--line); border-radius:13px; background:var(--panel); }
.oj-public-bottom>div>span { color:var(--oj-accent); font:850 10px/1 ui-sans-serif,system-ui,sans-serif; letter-spacing:1px; }
.oj-public-bottom b { display:block; margin-top:12px; font-size:12px; }
.oj-public-bottom p { margin:6px 0 0; color:var(--muted); font-size:10px; line-height:1.8; }
.oj-public-footer { max-width:1320px; margin:auto; padding:20px clamp(16px,3.2vw,42px) 26px; display:flex; justify-content:space-between; flex-wrap:wrap; gap:10px; border-top:1px solid var(--line); color:var(--muted); font-size:9px; }
.oj-public-footer>b { color:var(--text); letter-spacing:1.3px; }
.oj-empty-state { min-height:180px; padding:25px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:8px; color:var(--muted); text-align:center; }
.oj-empty-state svg { color:var(--oj-accent); }
.oj-empty-state b { color:var(--text); font-size:13px; }
.oj-empty-state p { margin:0; font-size:10px; }

/* Auth */
.auth-shell { width:min(1120px,calc(100% - 48px)); min-height:680px; height:min(760px,calc(100svh - 64px)); margin:32px auto; padding:0; display:grid; align-content:stretch; grid-template-columns:minmax(0,1.08fr) minmax(390px,.92fr); gap:0; border:1px solid var(--line); border-radius:25px; overflow:hidden; background:var(--panel); box-shadow:0 28px 90px rgba(0,0,0,.22); }
.auth-visual { min-height:0; display:flex; align-items:center; padding:clamp(28px,4.8vw,58px); border:0; border-radius:0; background:radial-gradient(ellipse at 18% 20%,rgba(144,112,244,.25),transparent 25rem),linear-gradient(145deg,#17172a,#111a29); }
.auth-visual-content { width:100%; max-width:520px; margin:auto; }
.auth-visual-content .brand { margin-bottom:clamp(35px,7vh,78px); }
.auth-visual-content h1 { font-size:clamp(34px,4.1vw,52px); }
.auth-visual-content>p { max-width:430px; }
.auth-form-wrap { min-height:0; max-width:none; width:100%; padding:clamp(28px,4.5vw,58px); background:var(--panel); border:0; display:flex; justify-content:center; }
.auth-form-wrap>.eyebrow { margin-top:auto; }
.auth-form-wrap form { gap:14px; }
.auth-form-wrap input { min-height:49px; }
.auth-form-wrap .button.primary { min-height:48px; }
.auth-form-wrap .welcome-back-link { margin-top:10px; }
.mobile-brand { display:none; }

/* Main workspace header navigation */
.oj-app-shell { display:flex !important; flex-direction:column !important; min-height:100svh; width:100%; overflow:visible !important; background:radial-gradient(ellipse at 82% -18%,rgba(121,94,219,.085),transparent 34rem),var(--bg); }
.oj-app-shell .mobile-appbar,.oj-app-shell .sidebar-scrim { display:none !important; }
.oj-app-shell .sidebar { position:sticky !important; z-index:70; top:0 !important; right:auto !important; bottom:auto !important; left:auto !important; width:100% !important; min-width:0 !important; height:auto !important; min-height:68px !important; max-height:none !important; padding:0 clamp(15px,3vw,42px) !important; display:flex !important; flex-direction:row !important; align-items:center !important; gap:22px; overflow:visible !important; transform:none !important; border:0; border-bottom:1px solid var(--line); border-radius:0; box-shadow:0 8px 30px rgba(0,0,0,.045); background:color-mix(in srgb,var(--panel) 94%,transparent) !important; backdrop-filter:blur(18px); }
.oj-app-shell .sidebar>.brand { flex:0 0 auto; min-width:max-content; margin:0 !important; padding:0 !important; font-size:16px; }
.oj-app-shell .sidebar>.brand .brand-mark { width:36px; height:36px; border-radius:10px; }
.oj-app-shell .sidebar .workspace-label { display:none !important; }
.oj-app-shell .sidebar .side-nav { flex:1 1 auto; min-width:0; width:auto; height:auto; max-height:none; margin:0; padding:0; display:flex !important; flex-direction:row !important; align-items:center; justify-content:flex-start; gap:4px; overflow:visible; background:transparent; }
.oj-app-shell .sidebar .nav-item { flex:0 0 auto; width:auto; min-width:max-content; min-height:40px; height:40px; padding:0 12px; display:flex; align-items:center; justify-content:center; gap:8px; border:1px solid transparent; border-radius:9px; background:transparent; color:var(--muted); font-size:10px; font-weight:780; }
.oj-app-shell .sidebar .nav-item:hover { background:var(--panel-2); color:var(--text); }
.oj-app-shell .sidebar .nav-item.selected { border-color:rgba(139,115,246,.18); color:var(--text); background:rgba(139,115,246,.12); box-shadow:inset 0 -2px var(--oj-accent); }
.oj-app-shell .sidebar-bottom { flex:0 0 auto; width:auto; min-width:0; height:auto; margin:0; padding:0; display:flex; flex-direction:row; align-items:center; gap:8px; border:0; background:transparent; }
.oj-app-shell .sidebar-bottom .sidebar-help { display:none !important; }
.oj-app-shell .sidebar-bottom .user-mini { margin:0; padding:0; border:0; gap:8px; }
.oj-app-shell .sidebar-bottom .user-mini-info { max-width:125px; }
.oj-app-shell .main-area { width:100%; min-width:0; min-height:calc(100svh - 68px); margin:0 !important; display:flex; flex-direction:column; }
.oj-app-shell .topbar { position:sticky; z-index:45; top:68px; min-height:55px; height:55px; padding:0 clamp(15px,3vw,42px); border:0; border-bottom:1px solid var(--line); background:color-mix(in srgb,var(--bg) 94%,transparent); backdrop-filter:blur(16px); }
.oj-app-shell .breadcrumb { font-size:10px; }
.oj-app-shell .topbar-brand { display:none; }
.oj-app-shell .top-actions { gap:8px; }
.oj-app-shell .page-content { width:min(1320px,100%); max-width:1320px; margin:0 auto; padding:27px clamp(15px,3vw,42px) 38px; }
.oj-app-shell .footer { width:min(1320px,100%); max-width:1320px; margin:0 auto; padding:14px clamp(15px,3vw,42px) 20px; }
.oj-app-shell .page-title-row { display:flex; align-items:flex-end; justify-content:space-between; gap:16px; }
.oj-app-shell .page-title-row h1 { font-size:26px; font-weight:950; letter-spacing:-.55px; }
.oj-app-shell .page-title-row p { max-width:700px; font-size:11px; line-height:1.9; }

/* Dashboard */
.oj-dashboard { width:100%; }
.oj-dashboard-heading { display:flex; align-items:flex-end; justify-content:space-between; gap:15px; margin-bottom:19px; }
.oj-dashboard-heading h1 { margin:5px 0 4px; font-size:26px; font-weight:950; letter-spacing:-.65px; }
.oj-dashboard-heading p { margin:0; color:var(--muted); font-size:11px; line-height:1.8; }
.oj-dashboard-heading-actions { display:flex; align-items:center; gap:9px; }
.oj-demo-label { padding:6px 9px; border:1px solid rgba(230,174,83,.24); border-radius:8px; background:rgba(230,174,83,.1); color:#d5a04e; font-size:9px; font-weight:800; }
.oj-dashboard-hero { display:grid; grid-template-columns:minmax(0,1.25fr) minmax(280px,.75fr); gap:18px; padding:22px; border:1px solid var(--line); border-radius:17px; background:linear-gradient(110deg,rgba(123,99,222,.09),transparent 55%),var(--panel); }
.oj-dashboard-hero-copy { padding:9px 5px; }
.oj-live-label { display:flex; align-items:center; gap:8px; color:var(--muted); font-size:10px; font-weight:800; }
.oj-live-label i { width:7px; height:7px; border-radius:50%; background:#40c595; box-shadow:0 0 0 4px rgba(64,197,149,.1); }
.oj-dashboard-hero h2 { max-width:570px; margin:13px 0 8px; font-size:clamp(22px,3vw,31px); font-weight:930; line-height:1.45; }
.oj-dashboard-hero-copy>p { max-width:590px; color:var(--muted); font-size:11px; line-height:2; }
.oj-hero-actions { display:flex; flex-wrap:wrap; align-items:center; gap:10px; margin-top:16px; }
.oj-team-chip { display:flex; align-items:center; gap:6px; color:var(--muted); font-size:10px; }
.oj-next-contest { min-width:0; padding:16px; border:1px solid var(--line); border-radius:12px; background:var(--panel-2); }
.oj-next-contest-head { display:flex; align-items:center; gap:8px; color:var(--muted); font-size:10px; }
.oj-next-contest-head svg { color:var(--oj-accent); }
.oj-next-contest>b { display:block; margin-top:13px; font-size:13px; line-height:1.7; }
.oj-next-date { display:block; margin-top:5px; color:var(--muted); font-size:9px; }
.oj-text-action { display:flex; align-items:center; gap:6px; margin-top:12px; padding:0; border:0; background:transparent; color:#a995ff; font:inherit; font-size:10px; cursor:pointer; }
.oj-next-empty { padding:16px 0 5px; color:var(--muted); font-size:10px; line-height:1.9; }
.oj-stat-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin:13px 0 20px; }
.oj-stat-card { min-width:0; min-height:72px; padding:12px 14px; display:flex; align-items:center; gap:11px; border:1px solid var(--line); border-radius:12px; background:var(--panel); color:var(--text); text-align:right; cursor:pointer; transition:border-color .15s,background .15s; }
.oj-stat-card:hover,.oj-stat-card.is-selected { border-color:rgba(139,115,246,.44); background:color-mix(in srgb,var(--panel) 78%,rgba(139,115,246,.12)); }
.oj-stat-card>span:last-child { min-width:0; display:flex; flex-direction:column; gap:5px; }
.oj-stat-card small { color:var(--muted); font-size:9px; white-space:nowrap; }
.oj-stat-card strong { font-size:19px; font-weight:950; font-variant-numeric:tabular-nums; }
.oj-stat-icon { width:36px; height:36px; flex:0 0 36px; display:grid; place-items:center; border-radius:10px; }
.oj-stat-icon.violet { background:rgba(139,115,246,.13); color:#a995ff; }
.oj-stat-icon.green { background:rgba(61,190,143,.12); }
.oj-stat-icon.green i { width:8px; height:8px; border-radius:50%; background:#40c595; }
.oj-stat-icon.blue { background:rgba(79,157,224,.12); color:#65a9e5; }
.oj-stat-icon.amber { background:rgba(226,174,82,.12); color:#dfb15e; }
.oj-stat-card-static { cursor:default; }
.oj-directory { border:1px solid var(--line); border-radius:16px; background:var(--panel); overflow:hidden; }
.oj-directory-head { padding:20px 21px 16px; display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:14px; }
.oj-directory-head h2 { margin:5px 0; font-size:18px; }
.oj-directory-head p { font-size:10px; }
.oj-directory-toolbar { padding:0 20px; min-height:46px; display:flex; align-items:center; justify-content:space-between; gap:12px; border-top:1px solid var(--line); border-bottom:1px solid var(--line); background:var(--panel-2); }
.oj-contest-list { padding:0 20px; }
.oj-contest-row { display:grid; grid-template-columns:105px minmax(0,1fr) auto; align-items:center; gap:14px; padding:15px 0; border-bottom:1px solid var(--line); }
.oj-contest-row:last-child { border-bottom:0; }
.oj-contest-row-status { display:flex; flex-direction:column; gap:8px; align-items:flex-start; }
.oj-contest-row-status>span:last-child { color:var(--muted); font-size:9px; }
.oj-contest-row-main { min-width:0; }
.oj-contest-title { max-width:100%; padding:0; border:0; background:transparent; color:var(--text); text-align:right; font:inherit; font-size:12px; font-weight:900; cursor:pointer; }
.oj-contest-title:hover { color:#a995ff; }
.oj-contest-row-main>p { margin:5px 0 0; color:var(--muted); font-size:10px; line-height:1.8; }
.oj-contest-row-meta { display:flex; align-items:center; flex-wrap:wrap; gap:10px; margin-top:9px; color:var(--muted); font-size:9px; }
.oj-contest-row-meta span { display:flex; align-items:center; gap:5px; }
.oj-contest-row-meta .oj-registered { color:#36ba8c; }
.oj-contest-row-actions { display:flex; align-items:center; justify-content:flex-end; flex-wrap:wrap; gap:5px; }
.oj-icon-action { width:34px; height:34px; display:grid; place-items:center; border:1px solid var(--line); border-radius:8px; background:var(--panel-2); color:var(--muted); cursor:pointer; }
.oj-directory-head .oj-search { max-width:290px; }
.oj-dashboard-footnote { display:flex; align-items:center; gap:8px; margin-top:14px; color:var(--muted); font-size:9px; }
.oj-dashboard-footnote svg { color:#51bd97; }

/* Contest room, admin, profile and team */
.oj-app-shell .exam-heading-panel { padding:20px 22px; border:1px solid var(--line); border-radius:15px; background:linear-gradient(110deg,rgba(126,102,224,.1),transparent 65%),var(--panel); display:flex; align-items:center; justify-content:space-between; gap:16px; }
.oj-app-shell .exam-heading-panel h1 { margin:6px 0; font-size:25px; font-weight:950; }
.oj-app-shell .exam-heading-panel p { margin:0; color:var(--muted); font-size:11px; line-height:1.8; }
.oj-app-shell .exam-info-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:9px; margin:12px 0; }
.oj-app-shell .exam-info-grid>* { min-width:0; padding:13px; border:1px solid var(--line); border-radius:11px; background:var(--panel); }
.oj-app-shell .question-paper-link,.oj-app-shell .team-shared-note { padding:11px 13px; border-radius:10px; border:1px solid var(--line); background:var(--panel); }
.oj-app-shell .question-paper-link { color:#aa98ff; font-size:10px; font-weight:850; }
.oj-app-shell .contest-meta-panel { display:flex; flex-direction:column; gap:8px; margin:12px 0; }
.oj-app-shell .contest-meta-panel>p { padding:12px 14px; border:1px solid var(--line); border-radius:10px; background:var(--panel-2); color:var(--text); font-size:11px; line-height:1.8; }
.oj-app-shell .exam-page,.oj-app-shell .exam-workspace { width:100%; max-width:100%; }
.oj-app-shell .question-card,.oj-app-shell .question-panel,.oj-app-shell .answer-panel,.oj-app-shell .exam-question { border:1px solid var(--line); border-radius:13px; background:var(--panel); box-shadow:none; }
.oj-app-shell .question-card { padding:17px; }
.oj-app-shell .question-card input,.oj-app-shell .question-card textarea { min-height:45px; border-radius:9px; }
.oj-app-shell .exam-timer,.oj-app-shell .timer-card { border-radius:11px; font-variant-numeric:tabular-nums; }
.oj-app-shell .exam-submit,.oj-app-shell .submit-exam-button { border-radius:10px; }
.oj-app-shell .admin-layout { display:grid; grid-template-columns:minmax(0,1fr) minmax(270px,.55fr); gap:14px; align-items:start; }
.oj-app-shell .create-panel,.oj-app-shell .admin-side>.panel-card,.oj-app-shell .admin-users { border:1px solid var(--line); border-radius:14px; background:var(--panel); box-shadow:none; }
.oj-app-shell .admin-form { gap:14px; }
.oj-app-shell .question-admin-heading { border:1px solid var(--line); border-radius:10px; background:var(--panel-2); padding:12px; }
.oj-app-shell .key-table { border:1px solid var(--line); border-radius:10px; overflow:hidden; }
.oj-app-shell .admin-exam-row,.oj-app-shell .admin-user-row { border-bottom:1px solid var(--line); padding:12px; }
.oj-app-shell .team-panel,.oj-app-shell .profile-settings,.oj-app-shell .profile-menu-actions { border:1px solid var(--line); border-radius:14px; background:var(--panel); }
.oj-app-shell .team-panel { padding:19px; margin-bottom:13px; }
.oj-app-shell .profile-settings { padding:19px; }
.oj-app-shell .profile-menu-actions { padding:16px; }
.oj-app-shell .profile-data h2 { font-size:22px; font-weight:950; }
.oj-app-shell .profile-settings-form { gap:11px; }
.oj-app-shell .leaderboard-page { width:100%; max-width:100%; }
.oj-app-shell .leaderboard-hero,.oj-app-shell .leaderboard-panel { border:1px solid var(--line); border-radius:14px; background:var(--panel); }
.oj-app-shell .leaderboard-table th { background:var(--panel-2); }
.oj-app-shell .registration-options button { border-radius:13px; background:var(--panel); }
.oj-app-shell .registration-options button.selected { border-color:var(--oj-accent); }

/* Responsive */
@media(max-width:950px) {
  .oj-app-shell .sidebar { min-height:62px !important; gap:12px; padding-inline:14px !important; }
  .oj-app-shell .sidebar>.brand { font-size:13px; }
  .oj-app-shell .sidebar .side-nav { overflow-x:auto; scrollbar-width:none; }
  .oj-app-shell .sidebar .side-nav::-webkit-scrollbar { display:none; }
  .oj-app-shell .sidebar .nav-item { min-height:37px; height:37px; padding-inline:9px; font-size:9px; }
  .oj-app-shell .sidebar-bottom { display:none !important; }
  .oj-app-shell .main-area { min-height:calc(100svh - 62px); }
  .oj-app-shell .topbar { top:62px; }
  .oj-app-shell .admin-layout { grid-template-columns:minmax(0,1fr); }
}
@media(max-width:700px) {
  .oj-public-header { min-height:62px; padding:8px 12px; gap:8px; flex-wrap:wrap; }
  .oj-brand-mark { width:34px; height:34px; }
  .oj-brand b { font-size:13px; }
  .oj-brand small { font-size:7px; }
  .oj-public-nav { order:3; width:100%; height:38px; overflow-x:auto; }
  .oj-public-nav a { min-width:max-content; padding:0 11px; font-size:10px; }
  .oj-public-actions { margin-inline-start:auto; gap:5px; }
  .oj-theme-toggle,.oj-login-button { min-height:34px; }
  .oj-theme-toggle { width:34px; }
  .oj-signup-button { min-height:34px; padding-inline:9px; font-size:9px; }
  .oj-public-main { padding:14px 12px 25px; }
  .oj-public-hero { grid-template-columns:minmax(0,1fr); gap:19px; padding:22px 18px; border-radius:15px; }
  .oj-public-hero h1 { margin:15px 0 9px; font-size:clamp(33px,9vw,43px); }
  .oj-public-hero-copy>p { font-size:11px; }
  .oj-public-hero-aside { padding:16px; }
  .oj-public-stats { grid-template-columns:repeat(2,minmax(0,1fr)); margin:10px 0 16px; }
  .oj-public-stats>div { padding:11px 12px; gap:8px; border-bottom:1px solid var(--line); }
  .oj-public-stats>div:nth-child(2n) { border-inline-start:0; }
  .oj-public-stats>div:nth-last-child(-n+2) { border-bottom:0; }
  .oj-public-stats b { font-size:18px; }
  .oj-public-stats span { font-size:9px; }
  .oj-public-directory-heading { padding:15px; align-items:stretch; flex-direction:column; }
  .oj-public-directory-heading h2 { font-size:17px; }
  .oj-public-directory-heading .oj-search { min-width:0; max-width:none; width:100%; }
  .oj-directory-toolbar { padding-inline:13px; }
  .oj-public-contest-list { padding-inline:13px; }
  .oj-public-contest-row { grid-template-columns:minmax(0,1fr); gap:8px; padding:14px 0; }
  .oj-public-contest-indicator { display:flex; justify-content:flex-start; }
  .oj-public-contest-actions { justify-content:flex-start; }
  .oj-public-contest-actions button { min-height:36px; }
  .oj-public-bottom { grid-template-columns:minmax(0,1fr); gap:8px; }
  .oj-public-footer { justify-content:center; text-align:center; padding-inline:14px; }
  .auth-shell { width:calc(100% - 24px); height:auto; min-height:0; margin:12px auto; display:flex; flex-direction:column; border-radius:17px; }
  .auth-visual { min-height:0; padding:20px 18px; }
  .auth-visual-content .brand { margin-bottom:18px; font-size:15px; }
  .auth-visual-content .brand-mark { width:35px; height:35px; }
  .auth-kicker { font-size:8px; }
  .auth-visual-content h1 { margin:12px 0 6px; font-size:29px; line-height:1.3; }
  .auth-visual-content>p { margin:0; font-size:10px; line-height:1.85; }
  .auth-form-wrap { min-height:0; padding:22px 18px 25px; }
  .auth-form-wrap>.eyebrow { margin-top:0; }
  .auth-form-wrap>h2 { font-size:23px; }
  .auth-form-wrap form { gap:11px; }
  .auth-form-wrap input { min-height:46px; }
  .oj-app-shell .sidebar { min-height:0 !important; padding:9px 12px 0 !important; display:flex !important; flex-wrap:wrap; gap:5px 12px; }
  .oj-app-shell .sidebar>.brand { min-height:32px; }
  .oj-app-shell .sidebar .side-nav { order:2; flex:0 0 100%; width:100%; padding:2px 0 7px; }
  .oj-app-shell .sidebar .nav-item { min-height:34px; height:34px; padding-inline:9px; font-size:9px; }
  .oj-app-shell .topbar { top:91px; min-height:43px; height:43px; padding-inline:12px; }
  .oj-app-shell .topbar .breadcrumb { font-size:9px; }
  .oj-app-shell .topbar .top-actions { gap:5px; }
  .oj-app-shell .topbar .icon-button { width:32px; height:32px; }
  .oj-app-shell .page-content { padding:15px 12px 25px; }
  .oj-dashboard-heading { align-items:flex-start; flex-direction:column; gap:10px; }
  .oj-dashboard-heading h1 { font-size:22px; }
  .oj-dashboard-hero { grid-template-columns:minmax(0,1fr); padding:15px; gap:12px; }
  .oj-dashboard-hero h2 { font-size:22px; }
  .oj-stat-grid { grid-template-columns:repeat(2,minmax(0,1fr)); gap:7px; margin:9px 0 13px; }
  .oj-stat-card { min-height:65px; padding:9px; gap:8px; }
  .oj-stat-icon { width:31px; height:31px; flex-basis:31px; }
  .oj-stat-card small { font-size:8px; }
  .oj-stat-card strong { font-size:17px; }
  .oj-directory-head { padding:14px; flex-direction:column; align-items:stretch; }
  .oj-directory-head .oj-search { min-width:0; max-width:none; width:100%; }
  .oj-directory-toolbar { padding-inline:10px; }
  .oj-contest-list { padding-inline:13px; }
  .oj-contest-row { grid-template-columns:minmax(0,1fr); gap:8px; padding:13px 0; }
  .oj-contest-row-status { flex-direction:row; align-items:center; gap:9px; }
  .oj-contest-row-actions { justify-content:flex-start; }
  .oj-contest-row-actions .button { min-height:34px; }
  .oj-app-shell .exam-heading-panel { align-items:flex-start; flex-direction:column; padding:15px; }
  .oj-app-shell .exam-heading-panel h1 { font-size:21px; }
  .oj-app-shell .exam-info-grid { grid-template-columns:repeat(2,minmax(0,1fr)); gap:7px; }
  .oj-app-shell .admin-layout { grid-template-columns:minmax(0,1fr); }
  .oj-app-shell .admin-side { grid-row:1; }
  .oj-app-shell .page-title-row { align-items:flex-start; flex-direction:column; }
}
@media(max-width:390px) {
  .oj-public-actions .oj-login-button { display:none; }
  .oj-public-hero-actions { display:grid; grid-template-columns:1fr; }
  .oj-dashboard-heading-actions { width:100%; }
  .oj-dashboard-heading-actions .button { width:100%; justify-content:center; }
  .oj-app-shell .exam-info-grid { grid-template-columns:minmax(0,1fr); }
}
@media(prefers-reduced-motion:reduce) { *,*::before,*::after { scroll-behavior:auto !important; animation-duration:.01ms !important; transition-duration:.01ms !important; animation-iteration-count:1 !important; } }
"""
css_path.write_text(css, encoding="utf-8")
print("Applied full second-generation page layouts.")
