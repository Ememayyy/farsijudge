from pathlib import Path

p = Path("src/App.tsx")
s = p.read_text(encoding="utf-8")

def once(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(label + ": expected exactly one anchor, found " + str(n))
    s = s.replace(old, new, 1)

once(
"""Sun, UserRound, Users, XCircle, UserPlus, Pencil, Trash2, FileUp, ExternalLink,""",
"""Sun, UserRound, Users, XCircle, UserPlus, Pencil, Trash2, FileUp, ExternalLink,
  CalendarDays, ChevronDown, Home, Menu, Search, Sparkles, Trophy,""",
"redesign icon imports"
)
once(
"""const [page, setPage] = useState<Page>('welcome')""",
"""const [page, setPage] = useState<Page>('welcome')
  const [sidebarOpen, setSidebarOpen] = useState(false)""",
"mobile sidebar state"
)
once(
"""  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('farsijudge-theme', theme)
  }, [theme])""",
"""  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('farsijudge-theme', theme)
  }, [theme])

  useEffect(() => {
    const client = supabase
    if (!client || isLoggedIn) return
    let alive = true
    const loadPublicContests = async () => {
      const { data } = await client.rpc('get_public_contests')
      if (alive && data) setExams(data as Exam[])
    }
    void loadPublicContests()
    return () => { alive = false }
  }, [isLoggedIn])""",
"public contest list loader"
)
once(
"""  return <div className="app-shell">
    <aside className="sidebar">""",
"""  return <div className={"app-shell redesign-shell " + (sidebarOpen ? "sidebar-open" : "")}>
    <div className="mobile-appbar">
      <button className="mobile-menu-toggle" onClick={() => setSidebarOpen(true)} aria-label="باز کردن منو"><Menu size={21} /></button>
      <div className="mobile-appbar-brand"><span className="brand-mark"><BookOpen size={20} /></span><b>فارسی جاج</b></div>
      <button className="icon-button" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} aria-label="تغییر پوسته">{theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}</button>
    </div>
    <aside className="sidebar">""",
"responsive app shell"
)
once(
"""      <nav className="side-nav">""",
"""      <nav className="side-nav" onClick={() => setSidebarOpen(false)}>""",
"close mobile sidebar after navigation"
)
once(
"""    </aside>

    <main className="main-area">""",
"""    </aside>
    <button className="sidebar-scrim" onClick={() => setSidebarOpen(false)} aria-label="بستن منو" />

    <main className="main-area">""",
"mobile sidebar backdrop"
)
once(
"""      showDemo={!isSupabaseConfigured}
    />""",
"""      showDemo={!isSupabaseConfigured}
      exams={exams}
      now={now}
    />""",
"public home data props"
)
once(
"""totalPoints={questionScore} questionResourceUrl={questionResourceUrl}""",
"""totalPoints={questionScore} now={now} questionResourceUrl={questionResourceUrl}""",
"exam clock prop"
)
once(
"""function ExamPage({ exam, questions, answers, remainingSeconds, status, result, saving, demo, onAnswer, onBack, totalPoints, questionResourceUrl, teamMode }: {""",
"""function ExamPage({ exam, questions, answers, remainingSeconds, status, result, saving, demo, onAnswer, onBack, totalPoints, questionResourceUrl, teamMode, now }: {""",
"ExamPage clock prop signature"
)
once(
"""questionResourceUrl: string; teamMode: boolean
}) {""",
"""questionResourceUrl: string; teamMode: boolean; now: number
}) {""",
"ExamPage clock prop type"
)

const_countdown = """function CountdownDisplay({ seconds, compact = false }: { seconds: number; compact?: boolean }) {
  const safe = Math.max(0, Math.floor(seconds))
  const parts = [
    { value: Math.floor(safe / 86400), label: 'روز' },
    { value: Math.floor((safe % 86400) / 3600), label: 'ساعت' },
    { value: Math.floor((safe % 3600) / 60), label: 'دقیقه' },
    { value: safe % 60, label: 'ثانیه' },
  ].filter((part) => part.value > 0)
  if (parts.length === 0) return <span className="countdown-started">لحظاتی تا آغاز</span>
  return <div className={'countdown-units ' + (compact ? 'compact' : '')}>
    {parts.map((part) => <div className="countdown-unit" key={part.label}>
      <strong>{fa(part.value)}</strong><span>{part.label}</span>
    </div>)}
  </div>
}

"""
once(
"""function Dashboard({""",
const_countdown + """function Dashboard({""",
"insert shared countdown component"
)

dash_start = s.index("function Dashboard(")
dash_end = s.index("\nfunction ClipboardIcon(", dash_start)
dashboard = """function Dashboard({ exams, profile, now, onOpen, onAdmin, isAdmin, isDemo, onRefresh, myRegistrations, myTeamRegistrations, team, onRegister }: {
  exams: Exam[]; profile: Profile | null; now: number; onOpen: (exam: Exam) => void; onAdmin: () => void
  isAdmin: boolean; isDemo: boolean; onRefresh: () => void
  myRegistrations: string[]; myTeamRegistrations: string[]; team: Team | null; onRegister: (exam: Exam) => void
}) {
  const active = exams.filter((exam) => getStatus(exam, now) === 'active')
  const upcoming = exams.filter((exam) => getStatus(exam, now) === 'upcoming').sort((a, b) => new Date(a.starts_at).getTime() - new Date(b.starts_at).getTime())
  const ended = exams.filter((exam) => getStatus(exam, now) === 'ended')
  const [filter, setFilter] = useState<'all' | 'active' | 'upcoming' | 'ended'>('all')
  const [search, setSearch] = useState('')
  const filtered = (filter === 'all' ? exams : filter === 'active' ? active : filter === 'upcoming' ? upcoming : ended)
    .filter((exam) => (exam.title + ' ' + (exam.description || '')).toLowerCase().includes(search.trim().toLowerCase()))
    .sort((a, b) => new Date(a.starts_at).getTime() - new Date(b.starts_at).getTime())
  const firstName = profile?.full_name?.trim().split(/\\s+/)[0] || 'خوش آمدید'

  return <>
    <section className="dashboard-hero">
      <div className="dashboard-hero-copy">
        <div className="dashboard-eyebrow"><Sparkles size={15} /> فضای مسابقهٔ شما</div>
        <h1>سلام، {firstName}</h1>
        <p>مسابقه‌های پیش‌رو را دنبال کن، برای رقابت آماده شو و عملکردت را در یک نگاه ببین.</p>
        <div className="dashboard-hero-actions">
          <button className="button primary" onClick={() => document.getElementById('dashboard-contests')?.scrollIntoView({ behavior: 'smooth' })}><Trophy size={17} />مشاهدهٔ مسابقه‌ها</button>
          {isAdmin && <button className="button soft" onClick={onAdmin}><Plus size={17} />ساخت مسابقه</button>}
          <button className="button ghost" onClick={onRefresh}><RefreshCw size={16} />به‌روزرسانی</button>
        </div>
        {isDemo && <div className="dashboard-demo-note"><span />حالت نمایشی؛ اطلاعات این بخش نمونه هستند.</div>}
      </div>
      <div className="dashboard-next-card">
        <div className="dashboard-next-top"><span className="live-indicator" />مسابقهٔ بعدی</div>
        {upcoming[0] ? <>
          <b className="dashboard-next-title">{upcoming[0].title}</b>
          <span className="dashboard-next-date"><CalendarDays size={15} />{dateText(upcoming[0].starts_at)}</span>
          <CountdownDisplay seconds={Math.max(0, Math.ceil((new Date(upcoming[0].starts_at).getTime() - now) / 1000))} />
          <button className="dashboard-next-link" onClick={() => onOpen(upcoming[0])}>مشاهدهٔ جزئیات <ArrowLeft size={15} /></button>
        </> : <div className="dashboard-no-next"><CalendarDays size={23} /><span>فعلاً مسابقهٔ پیش‌رویی نداریم.</span><small>به‌زودی دوباره این بخش را بررسی کن.</small></div>}
      </div>
      <div className="dashboard-hero-orb orb-a" /><div className="dashboard-hero-orb orb-b" />
    </section>

    <section className="dashboard-metrics">
      <button className={'dashboard-metric ' + (filter === 'all' ? 'is-active' : '')} onClick={() => setFilter('all')}>
        <span className="metric-icon violet"><BookOpen size={19} /></span><span className="metric-text"><small>کل مسابقه‌ها</small><strong>{fa(exams.length)}</strong><em>فهرست کامل</em></span><ChevronDown size={16} />
      </button>
      <button className={'dashboard-metric ' + (filter === 'active' ? 'is-active' : '')} onClick={() => setFilter('active')}>
        <span className="metric-icon green"><span className="metric-live-dot" /></span><span className="metric-text"><small>در حال برگزاری</small><strong>{fa(active.length)}</strong><em>هم‌اکنون فعال</em></span><ChevronDown size={16} />
      </button>
      <button className={'dashboard-metric ' + (filter === 'upcoming' ? 'is-active' : '')} onClick={() => setFilter('upcoming')}>
        <span className="metric-icon blue"><CalendarDays size={19} /></span><span className="metric-text"><small>مسابقه‌های پیش‌رو</small><strong>{fa(upcoming.length)}</strong><em>آمادهٔ رقابت</em></span><ChevronDown size={16} />
      </button>
      <button className={'dashboard-metric ' + (filter === 'ended' ? 'is-active' : '')} onClick={() => setFilter('ended')}>
        <span className="metric-icon orange"><Award size={19} /></span><span className="metric-text"><small>پایان‌یافته</small><strong>{fa(ended.length)}</strong><em>بررسی کارنامه</em></span><ChevronDown size={16} />
      </button>
    </section>

    <section className="dashboard-list-panel" id="dashboard-contests">
      <div className="dashboard-list-heading">
        <div><div className="eyebrow">CONTEST CENTER</div><h2>مسابقه‌های شما</h2><p>مسابقه‌ای را انتخاب کن و وضعیت آن را ببین.</p></div>
        <label className="dashboard-search"><Search size={17} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="جست‌وجوی مسابقه..." /></label>
      </div>
      <div className="dashboard-filter-row">
        {([['all', 'همه'], ['active', 'در حال برگزاری'], ['upcoming', 'پیش‌رو'], ['ended', 'پایان‌یافته']] as const).map(([value, label]) =>
          <button key={value} className={filter === value ? 'dashboard-filter active' : 'dashboard-filter'} onClick={() => setFilter(value)}>{label}<span>{value === 'all' ? exams.length : value === 'active' ? active.length : value === 'upcoming' ? upcoming.length : ended.length}</span></button>
        )}
        <span className="dashboard-total-label">{fa(filtered.length)} مسابقه</span>
      </div>
      {filtered.length === 0 ? <div className="dashboard-empty"><span className="empty-graphic"><Search size={25} /></span><b>چیزی برای نمایش پیدا نشد</b><p>عبارت جست‌وجو یا فیلتر را تغییر بده.</p></div>
        : <div className="exam-grid">{filtered.map((exam) => <ExamCard key={exam.id} exam={exam} now={now} onOpen={() => onOpen(exam)}
          registered={myRegistrations.includes(exam.id) || myTeamRegistrations.includes(exam.id)}
          teamMember={Boolean(team)} teamCaptain={team?.role === 'captain'} onRegister={() => onRegister(exam)} />)}</div>}
    </section>

    <section className="dashboard-bottom-grid">
      <article className="dashboard-tip-card"><span className="tip-symbol"><ShieldCheck size={20} /></span><div><b>پاسخ‌هایت محفوظ می‌مانند</b><p>پاسخ‌ها در زمان مسابقه به‌صورت خودکار ذخیره می‌شوند. تا پایان زمان می‌توانی آن‌ها را اصلاح کنی.</p></div></article>
      <article className="dashboard-tip-card"><span className="tip-symbol blue"><Users size={20} /></span><div><b>با تیمت رقابت کن</b><p>از بخش تیم و دعوت‌ها می‌توانی اعضای تیمت را مدیریت کنی و برای مسابقه ثبت‌نام شوید.</p></div></article>
    </section>
  </>
}
"""
s = s[:dash_start] + dashboard + s[dash_end:]

once(
"""    {status === 'upcoming' && <div className="start-countdown"><b>زمان باقی‌مانده تا شروع مسابقه</b><span>{fa(Math.max(0, Math.ceil((new Date(exam.starts_at).getTime() - Date.now()) / 1000)))} ثانیه</span></div>}""",
"""    {status === 'upcoming' && <div className="start-countdown">
      <div className="start-countdown-copy"><b>زمان باقی‌مانده تا شروع مسابقه</b><span>برای شروع آماده شو</span></div>
      <CountdownDisplay seconds={Math.max(0, Math.ceil((new Date(exam.starts_at).getTime() - now) / 1000))} />
    </div>}""",
"replace plain countdown"
)

const_welcome = """function WelcomePage({ theme, onToggleTheme, onLogin, onRegister, onDemo, showDemo, exams, now }: {
  theme: 'light' | 'dark'; onToggleTheme: () => void; onLogin: () => void
  onRegister: () => void; onDemo: () => void; showDemo: boolean; exams: Exam[]; now: number
}) {
  const publicExams = exams.filter((exam) => exam.is_published).sort((a, b) => new Date(a.starts_at).getTime() - new Date(b.starts_at).getTime())
  const nextContest = publicExams.find((exam) => getStatus(exam, now) === 'upcoming')
  const runningCount = publicExams.filter((exam) => getStatus(exam, now) === 'active').length
  return <div className="public-site">
    <header className="public-header">
      <a href="#public-top" className="public-brand"><span className="public-brand-mark"><BookOpen size={23} /></span><span>فارسی جاج</span><small>FARSI JUDGE</small></a>
      <nav className="public-nav">
        <a className="current" href="#public-top"><Home size={15} />خانه</a>
        <a href="#public-contests"><Trophy size={15} />مسابقه‌ها</a>
        <a href="#public-guide"><BookOpen size={15} />راهنما</a>
        <a href="#public-about"><Sparkles size={15} />دربارهٔ سامانه</a>
      </nav>
      <div className="public-actions">
        <button className="icon-button" onClick={onToggleTheme} aria-label="تغییر پوسته">{theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}</button>
        <button className="public-login-link" onClick={onLogin}>ورود</button>
        <button className="button primary small" onClick={onRegister}>ساخت حساب</button>
      </div>
    </header>

    <main className="public-main" id="public-top">
      <div className="public-announcement"><span className="announcement-dot" />سامانهٔ مسابقات برنامه‌نویسی، ریاضی و المپیاد <span className="announcement-side">محیط فارسی رقابت</span></div>
      <section className="public-hero">
        <div className="public-hero-copy">
          <div className="public-kicker"><span>ONLINE CONTEST PLATFORM</span><i />مسابقه، تمرین، پیشرفت</div>
          <h1>جای تو در <span>خط شروع</span> مسابقه است.</h1>
          <p>مسابقه‌های پیش‌رو را پیدا کن، انفرادی یا تیمی ثبت‌نام کن و نتیجهٔ تلاش خودت را با کارنامهٔ دقیق ببین.</p>
          <div className="public-hero-actions">
            <button className="button primary" onClick={onRegister}>شروع رقابت <ArrowLeft size={17} /></button>
            <button className="button soft" onClick={() => document.getElementById('public-contests')?.scrollIntoView({ behavior: 'smooth' })}>مرور مسابقه‌ها <ChevronDown size={16} /></button>
          </div>
          {showDemo && <button className="public-demo-link" onClick={onDemo}>ورود به پیش‌نمایش تعاملی</button>}
        </div>
        <div className="public-hero-side">
          <div className="public-hero-orbit public-orbit-one" /><div className="public-hero-orbit public-orbit-two" />
          <div className="public-hero-stat-card">
            <div className="public-hero-stat-head"><span className="live-indicator" />وضعیت سامانه</div>
            <div className="public-stat-number">{fa(runningCount)}</div>
            <b>مسابقهٔ در حال برگزاری</b>
            <div className="public-stat-divider" />
            <div className="public-stat-foot"><span>مسابقه‌های منتشرشده</span><strong>{fa(publicExams.length)}</strong></div>
            <div className="public-stat-foot"><span>مسابقهٔ پیش‌رو</span><strong>{nextContest ? dateText(nextContest.starts_at) : 'به‌زودی'}</strong></div>
          </div>
        </div>
      </section>

      <div className="public-content-grid">
        <section className="public-panel public-contests-panel" id="public-contests">
          <div className="public-panel-heading">
            <div><div className="public-panel-kicker">CONTESTS</div><h2>مسابقه‌های عمومی</h2><p>فهرست مسابقه‌های منتشرشده و زمان‌بندی آن‌ها</p></div>
            <span className="public-panel-count">{fa(publicExams.length)} مسابقه</span>
          </div>
          <div className="public-table-wrap">
            <table className="public-contest-table">
              <thead><tr><th>عنوان مسابقه</th><th>شروع</th><th>مدت</th><th>وضعیت</th><th></th></tr></thead>
              <tbody>
                {publicExams.map((exam) => <tr key={exam.id}>
                  <td><b>{exam.title}</b><small>{exam.description || 'مسابقهٔ آنلاین فارسی جاج'}</small></td>
                  <td>{dateText(exam.starts_at)}</td>
                  <td>{fa(exam.duration_minutes)} دقیقه</td>
                  <td><StatusBadge status={getStatus(exam, now)} /></td>
                  <td><button className="public-row-action" onClick={onLogin}>جزئیات <ChevronLeft size={14} /></button></td>
                </tr>)}
                {publicExams.length === 0 && <tr><td colSpan={5}><div className="public-empty"><CalendarDays size={24} /><b>هنوز مسابقه‌ای منتشر نشده است</b><span>به‌زودی فهرست مسابقه‌های جدید در این بخش قرار می‌گیرد.</span></div></td></tr>}
              </tbody>
            </table>
          </div>
          <div className="public-table-footer"><span>زمان‌ها بر اساس منطقهٔ زمانی دستگاه شما نمایش داده می‌شوند.</span><button onClick={onLogin}>ورود برای مشاهدهٔ جزئیات <ArrowLeft size={14} /></button></div>
        </section>

        <aside className="public-sidebar">
          <section className="public-panel public-auth-card">
            <div className="public-auth-icon"><UserRound size={20} /></div>
            <h2>آمادهٔ شرکت هستی؟</h2>
            <p>برای ثبت‌نام، ارسال پاسخ و مشاهدهٔ کارنامه وارد حساب خودت شو.</p>
            <button className="button primary full" onClick={onLogin}>ورود به حساب <ArrowLeft size={16} /></button>
            <button className="button soft full" onClick={onRegister}>ثبت‌نام کاربر جدید</button>
          </section>
          <section className="public-panel public-next-card" id="public-guide">
            <div className="public-side-heading"><CalendarDays size={17} /><b>مسابقهٔ بعدی</b></div>
            {nextContest ? <>
              <strong>{nextContest.title}</strong>
              <span className="public-next-date">{dateText(nextContest.starts_at)}</span>
              <CountdownDisplay seconds={Math.max(0, Math.ceil((new Date(nextContest.starts_at).getTime() - now) / 1000))} compact />
            </> : <p>به‌محض انتشار مسابقهٔ جدید، زمان شروع آن اینجا نمایش داده می‌شود.</p>}
          </section>
          <section className="public-panel public-guide-card">
            <div className="public-side-heading"><ShieldCheck size={17} /><b>شروع در سه قدم</b></div>
            <div className="public-guide-step"><span>۱</span><div><b>حساب بساز</b><small>با ایمیل خود ثبت‌نام کن.</small></div></div>
            <div className="public-guide-step"><span>۲</span><div><b>مسابقه را انتخاب کن</b><small>انفرادی یا با تیم خود شرکت کن.</small></div></div>
            <div className="public-guide-step"><span>۳</span><div><b>نتیجه را ببین</b><small>پس از انتشار، کارنامهٔ دقیق را بررسی کن.</small></div></div>
          </section>
        </aside>
      </div>

      <section className="public-bottom-info" id="public-about">
        <div><span className="public-info-icon"><Trophy size={18} /></span><b>رقابت شفاف</b><p>زمان‌بندی مشخص و وضعیت لحظه‌ای مسابقه‌ها</p></div>
        <div><span className="public-info-icon"><Users size={18} /></span><b>شرکت انفرادی و تیمی</b><p>انتخاب شیوهٔ حضور در هر مسابقه</p></div>
        <div><span className="public-info-icon"><Award size={18} /></span><b>کارنامهٔ دقیق</b><p>نمایش امتیاز و ریز پاسخ‌ها پس از انتشار</p></div>
      </section>
    </main>
    <footer className="public-footer"><span>فارسی جاج</span><span>مسابقهٔ خوب، شروع یک پیشرفت تازه است.</span><span>© Farsi Judge</span></footer>
  </div>
}

"""
welcome_start = s.index("function WelcomePage(")
welcome_end = s.index("\nfunction RegistrationPage(", welcome_start)
s = s[:welcome_start] + const_welcome + s[welcome_end:]

s = s.replace("function ClipboardIcon() { return <BookOpen size={20} /> }\n", "")

p.write_text(s, encoding="utf-8")

cssp = Path("src/style.css")
css = cssp.read_text(encoding="utf-8")
css += """

/* Farsi Judge 2026: public contest portal + responsive member workspace */
.mobile-appbar { display:none; }
.sidebar-scrim { display:none; }
.redesign-shell { display:block; min-height:100vh; width:100%; overflow-x:hidden; background:var(--bg); }
.redesign-shell .sidebar {
  position:fixed; z-index:60; top:0; right:0; bottom:0; width:276px; min-width:276px;
  display:flex; flex-direction:column; padding:25px 18px 17px; overflow-y:auto;
  background:linear-gradient(180deg,var(--panel),var(--bg)); border-left:1px solid var(--line);
  box-shadow:-12px 0 38px rgba(0,0,0,.08); transition:transform .24s ease;
}
.redesign-shell .brand { display:flex; align-items:center; gap:10px; padding:5px 9px 25px; font-size:18px; font-weight:850; }
.redesign-shell .workspace-label { margin:5px 10px 12px; color:var(--muted); font-size:10px; letter-spacing:.7px; }
.redesign-shell .side-nav { display:flex; flex-direction:column; gap:7px; }
.redesign-shell .nav-item { width:100%; min-height:46px; padding:0 13px; border-radius:12px; display:flex; align-items:center; gap:12px; text-align:right; background:transparent; color:var(--muted); border:1px solid transparent; transition:.18s ease; }
.redesign-shell .nav-item:hover { background:var(--panel-2); color:var(--text); }
.redesign-shell .nav-item.selected { color:var(--text); background:linear-gradient(100deg,rgba(143,105,255,.2),rgba(143,105,255,.06)); border-color:rgba(143,105,255,.2); box-shadow:inset -3px 0 #9874ff; }
.redesign-shell .sidebar-bottom { margin-top:auto; padding-top:20px; }
.redesign-shell .sidebar-help { padding:16px; border:1px solid var(--line); border-radius:15px; background:var(--panel-2); }
.redesign-shell .sidebar-help strong { display:block; margin-top:10px; font-size:12px; }
.redesign-shell .sidebar-help p { margin:6px 0 0; color:var(--muted); font-size:10px; line-height:1.9; }
.redesign-shell .user-mini { display:flex; align-items:center; gap:10px; margin-top:15px; padding:11px 9px 0; border-top:1px solid var(--line); }
.redesign-shell .user-mini-info { min-width:0; display:flex; flex:1; flex-direction:column; gap:4px; }
.redesign-shell .user-mini-info b { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-size:12px; }
.redesign-shell .user-mini-info span { color:var(--muted); font-size:10px; }
.redesign-shell .main-area { width:auto; min-width:0; min-height:100vh; margin:0 276px 0 0; display:flex; flex-direction:column; }
.redesign-shell .topbar { position:sticky; z-index:35; top:0; height:70px; min-height:70px; padding:0 clamp(20px,3vw,44px); border-bottom:1px solid var(--line); background:color-mix(in srgb,var(--bg) 88%,transparent); backdrop-filter:blur(16px); }
.redesign-shell .breadcrumb { font-size:12px; }
.redesign-shell .top-actions { gap:12px; }
.redesign-shell .page-content { flex:1; width:100%; max-width:1500px; margin:0 auto; padding:30px clamp(18px,3.2vw,48px) 38px; }
.redesign-shell .footer { width:100%; max-width:1500px; margin:0 auto; padding:17px clamp(18px,3.2vw,48px) 22px; border-top:1px solid var(--line); color:var(--muted); font-size:10px; }
.mobile-appbar-brand { display:flex; align-items:center; gap:8px; font-size:14px; }
.mobile-menu-toggle { width:40px; height:40px; display:grid; place-items:center; border:1px solid var(--line); border-radius:12px; background:var(--panel); color:var(--text); cursor:pointer; }

.dashboard-hero { isolation:isolate; position:relative; overflow:hidden; display:grid; grid-template-columns:minmax(0,1.35fr) minmax(270px,.75fr); gap:24px; align-items:center; padding:30px; border:1px solid rgba(153,119,255,.18); border-radius:23px; background:radial-gradient(ellipse at 5% 5%,rgba(135,94,255,.17),transparent 55%),linear-gradient(125deg,var(--panel),var(--panel-2)); box-shadow:0 18px 55px rgba(0,0,0,.08); }
.dashboard-hero-copy,.dashboard-next-card { position:relative; z-index:2; }
.dashboard-eyebrow { display:flex; align-items:center; gap:7px; color:#a98cff; font-size:11px; font-weight:750; }
.dashboard-hero h1 { margin:12px 0 7px; font-size:clamp(25px,3vw,38px); letter-spacing:-.7px; }
.dashboard-hero-copy>p { max-width:590px; margin:0; color:var(--muted); font-size:13px; line-height:2; }
.dashboard-hero-actions { display:flex; flex-wrap:wrap; align-items:center; gap:9px; margin-top:20px; }
.dashboard-demo-note { display:flex; align-items:center; gap:7px; margin-top:14px; color:var(--muted); font-size:10px; }
.dashboard-demo-note span { width:7px; height:7px; border-radius:50%; background:#efb85b; }
.dashboard-next-card { padding:20px; border:1px solid var(--line); border-radius:18px; background:color-mix(in srgb,var(--panel) 84%,transparent); box-shadow:0 12px 35px rgba(0,0,0,.08); }
.dashboard-next-top { display:flex; align-items:center; gap:8px; color:var(--muted); font-size:10px; }
.live-indicator { width:7px; height:7px; border-radius:50%; background:#2ac58d; box-shadow:0 0 0 4px rgba(42,197,141,.12); }
.dashboard-next-title { display:block; margin-top:15px; font-size:15px; }
.dashboard-next-date { display:flex; align-items:center; gap:7px; margin-top:8px; color:var(--muted); font-size:10px; }
.dashboard-next-link { display:flex; align-items:center; gap:7px; margin-top:15px; border:0; padding:0; background:transparent; color:#ad91ff; font:inherit; font-size:11px; cursor:pointer; }
.dashboard-no-next { display:flex; flex-direction:column; align-items:flex-start; gap:7px; margin-top:19px; color:var(--muted); font-size:11px; }
.dashboard-no-next svg { color:#a98cff; }
.dashboard-no-next small { font-size:10px; }
.dashboard-hero-orb { position:absolute; z-index:1; border:1px solid rgba(157,126,255,.14); border-radius:50%; pointer-events:none; }
.dashboard-hero-orb.orb-a { width:280px; height:280px; left:-130px; top:-160px; }
.dashboard-hero-orb.orb-b { width:190px; height:190px; left:-70px; top:-115px; }
.countdown-units { display:flex; align-items:stretch; flex-wrap:wrap; gap:7px; margin-top:15px; }
.countdown-unit { min-width:56px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:3px; padding:9px 10px; border:1px solid rgba(153,119,255,.19); border-radius:10px; background:rgba(143,105,255,.08); }
.countdown-unit strong { color:var(--text); font-size:20px; line-height:1.2; font-variant-numeric:tabular-nums; }
.countdown-unit span { color:var(--muted); font-size:9px; }
.countdown-units.compact { gap:5px; margin-top:12px; }
.countdown-units.compact .countdown-unit { min-width:43px; padding:7px 8px; }
.countdown-units.compact .countdown-unit strong { font-size:16px; }
.countdown-started { display:inline-flex; margin-top:13px; color:#23bd89; font-size:11px; }
.start-countdown { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; padding:18px 20px; border:1px solid rgba(153,119,255,.2); border-radius:15px; background:linear-gradient(110deg,rgba(145,105,255,.12),var(--panel)); }
.start-countdown-copy { display:flex; flex-direction:column; gap:5px; }
.start-countdown-copy b { font-size:13px; }
.start-countdown-copy span { color:var(--muted); font-size:10px; }
.start-countdown .countdown-units { margin:0; }
.dashboard-metrics { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:13px; margin:19px 0; }
.dashboard-metric { min-width:0; display:flex; align-items:center; gap:11px; padding:16px 14px; border:1px solid var(--line); border-radius:16px; background:var(--panel); color:var(--text); text-align:right; cursor:pointer; transition:.18s ease; }
.dashboard-metric:hover,.dashboard-metric.is-active { border-color:rgba(153,119,255,.42); background:linear-gradient(140deg,rgba(142,106,255,.09),var(--panel)); transform:translateY(-1px); }
.metric-icon { width:39px; height:39px; flex:0 0 39px; display:grid; place-items:center; border-radius:12px; }
.metric-icon.violet { color:#aa8dff; background:rgba(160,123,255,.13); }
.metric-icon.green { color:#26c28d; background:rgba(38,194,141,.12); }
.metric-icon.blue { color:#63a9f3; background:rgba(99,169,243,.12); }
.metric-icon.orange { color:#edae5f; background:rgba(237,174,95,.13); }
.metric-live-dot { width:9px; height:9px; border-radius:50%; background:#26c28d; box-shadow:0 0 0 5px rgba(38,194,141,.14); }
.metric-text { min-width:0; flex:1; display:flex; flex-direction:column; gap:3px; }
.metric-text small { overflow:hidden; color:var(--muted); font-size:10px; white-space:nowrap; text-overflow:ellipsis; }
.metric-text strong { font-size:22px; line-height:1.2; font-variant-numeric:tabular-nums; }
.metric-text em { color:var(--muted); font-size:9px; font-style:normal; }
.dashboard-metric>svg { color:var(--muted); transform:rotate(90deg); }
.dashboard-list-panel { padding:22px; border:1px solid var(--line); border-radius:20px; background:var(--panel); }
.dashboard-list-heading { display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:15px; }
.dashboard-list-heading h2 { margin:5px 0; font-size:20px; }
.dashboard-list-heading p { margin:0; color:var(--muted); font-size:11px; }
.dashboard-list-heading .eyebrow { color:#a98cff; font-size:9px; letter-spacing:1px; }
.dashboard-search { min-width:min(280px,100%); display:flex; align-items:center; gap:8px; padding:10px 12px; border:1px solid var(--line); border-radius:11px; background:var(--panel-2); color:var(--muted); }
.dashboard-search input { width:100%; min-width:0; border:0; outline:0; background:transparent; color:var(--text); font:inherit; font-size:11px; }
.dashboard-filter-row { display:flex; align-items:center; flex-wrap:wrap; gap:7px; margin:20px 0 16px; padding-bottom:14px; border-bottom:1px solid var(--line); }
.dashboard-filter { display:flex; align-items:center; gap:7px; padding:8px 11px; border:1px solid transparent; border-radius:9px; background:transparent; color:var(--muted); font:inherit; font-size:10px; cursor:pointer; }
.dashboard-filter.active { border-color:rgba(153,119,255,.24); background:rgba(153,119,255,.1); color:var(--text); }
.dashboard-filter span { color:inherit; opacity:.7; font-variant-numeric:tabular-nums; }
.dashboard-total-label { margin-inline-start:auto; color:var(--muted); font-size:10px; }
.dashboard-list-panel .exam-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:13px; }
.dashboard-list-panel .exam-card { height:100%; padding:17px; border:1px solid var(--line); border-radius:15px; background:var(--panel-2); box-shadow:none; transition:transform .18s,border-color .18s; }
.dashboard-list-panel .exam-card:hover { transform:translateY(-2px); border-color:rgba(153,119,255,.35); }
.dashboard-list-panel .exam-card h3 { font-size:14px; }
.dashboard-empty { min-height:210px; display:flex; flex-direction:column; justify-content:center; align-items:center; gap:8px; color:var(--muted); text-align:center; }
.dashboard-empty b { color:var(--text); font-size:13px; }
.dashboard-empty p { margin:0; font-size:10px; }
.empty-graphic { width:48px; height:48px; display:grid; place-items:center; margin-bottom:5px; border-radius:15px; background:var(--panel-2); color:#a98cff; }
.dashboard-bottom-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:13px; margin-top:16px; }
.dashboard-tip-card { display:flex; align-items:flex-start; gap:12px; padding:16px; border:1px solid var(--line); border-radius:15px; background:var(--panel); }
.tip-symbol { width:37px; height:37px; flex:0 0 37px; display:grid; place-items:center; border-radius:11px; color:#a98cff; background:rgba(169,140,255,.12); }
.tip-symbol.blue { color:#65aaf2; background:rgba(101,170,242,.12); }
.dashboard-tip-card b { font-size:11px; }
.dashboard-tip-card p { margin:5px 0 0; color:var(--muted); font-size:10px; line-height:1.9; }

.public-site { min-height:100vh; color:var(--text); background:var(--bg); }
.public-header { position:sticky; z-index:45; top:0; display:flex; align-items:center; justify-content:space-between; gap:22px; min-height:72px; padding:0 max(22px,calc((100vw - 1260px)/2)); border-bottom:1px solid var(--line); background:color-mix(in srgb,var(--panel) 92%,transparent); backdrop-filter:blur(16px); }
.public-brand { display:flex; align-items:center; gap:9px; color:var(--text); text-decoration:none; font-size:16px; font-weight:850; white-space:nowrap; }
.public-brand-mark { width:36px; height:36px; display:grid; place-items:center; border-radius:11px; color:#fff; background:linear-gradient(145deg,#9a75ff,#6443c8); }
.public-brand small { margin-inline-start:3px; color:var(--muted); font-size:8px; letter-spacing:1.1px; }
.public-nav { height:72px; display:flex; align-items:stretch; gap:4px; }
.public-nav a { display:flex; align-items:center; gap:7px; padding:0 13px; border-bottom:2px solid transparent; color:var(--muted); text-decoration:none; font-size:11px; transition:.18s ease; }
.public-nav a:hover,.public-nav a.current { color:var(--text); border-bottom-color:#9873ff; background:rgba(153,115,255,.06); }
.public-actions { display:flex; align-items:center; gap:10px; }
.public-login-link { border:0; background:transparent; color:var(--text); font:inherit; font-size:11px; cursor:pointer; }
.public-main { max-width:1260px; margin:auto; padding:18px 24px 34px; }
.public-announcement { display:flex; align-items:center; gap:9px; padding:10px 13px; border:1px solid var(--line); border-radius:10px; background:var(--panel); color:var(--muted); font-size:10px; }
.announcement-dot { width:7px; height:7px; border-radius:50%; background:#28c58f; box-shadow:0 0 0 4px rgba(40,197,143,.1); }
.announcement-side { margin-inline-start:auto; color:#ab91fb; }
.public-hero { position:relative; overflow:hidden; display:grid; grid-template-columns:minmax(0,1.2fr) minmax(260px,.8fr); gap:30px; align-items:center; min-height:300px; margin:15px 0 20px; padding:30px 34px; border:1px solid rgba(153,119,255,.18); border-radius:20px; background:radial-gradient(ellipse at 15% 0%,rgba(148,109,255,.18),transparent 55%),linear-gradient(120deg,var(--panel),var(--panel-2)); }
.public-hero-copy,.public-hero-side { position:relative; z-index:2; }
.public-kicker { display:flex; align-items:center; flex-wrap:wrap; gap:10px; color:#b39aff; font-size:10px; }
.public-kicker span { letter-spacing:1.2px; font-size:9px; font-weight:850; }
.public-kicker i { width:4px; height:4px; border-radius:50%; background:var(--muted); }
.public-hero h1 { margin:13px 0 9px; font-size:clamp(27px,4vw,43px); line-height:1.5; letter-spacing:-1px; }
.public-hero h1 span { color:#a98cff; }
.public-hero-copy>p { max-width:570px; margin:0; color:var(--muted); font-size:12px; line-height:2.2; }
.public-hero-actions { display:flex; flex-wrap:wrap; gap:9px; margin-top:19px; }
.public-demo-link { margin-top:12px; border:0; background:transparent; color:#b39aff; font:inherit; font-size:10px; cursor:pointer; }
.public-hero-side { display:grid; place-items:center; min-height:230px; }
.public-hero-orbit { position:absolute; border:1px solid rgba(153,119,255,.19); border-radius:50%; transform:rotate(-26deg); }
.public-orbit-one { width:320px; height:210px; }
.public-orbit-two { width:230px; height:300px; transform:rotate(37deg); }
.public-hero-stat-card { width:min(310px,90%); padding:21px; border:1px solid var(--line); border-radius:17px; background:var(--panel); box-shadow:0 18px 42px rgba(0,0,0,.14); }
.public-hero-stat-head { display:flex; align-items:center; gap:8px; color:var(--muted); font-size:10px; }
.public-stat-number { margin-top:14px; font-size:38px; font-weight:900; line-height:1; }
.public-hero-stat-card>b { display:block; margin-top:6px; font-size:12px; }
.public-stat-divider { height:1px; margin:15px 0 11px; background:var(--line); }
.public-stat-foot { display:flex; align-items:center; justify-content:space-between; gap:10px; margin-top:8px; color:var(--muted); font-size:9px; }
.public-stat-foot strong { max-width:65%; color:var(--text); font-size:9px; text-align:left; }
.public-content-grid { display:grid; grid-template-columns:minmax(0,1.8fr) minmax(260px,.78fr); gap:16px; align-items:start; }
.public-panel { min-width:0; padding:18px; border:1px solid var(--line); border-radius:16px; background:var(--panel); }
.public-panel-heading { display:flex; justify-content:space-between; align-items:center; gap:14px; margin-bottom:14px; }
.public-panel-kicker { color:#a98cff; font-size:8px; font-weight:850; letter-spacing:1.3px; }
.public-panel-heading h2 { margin:4px 0; font-size:16px; }
.public-panel-heading p { margin:0; color:var(--muted); font-size:10px; }
.public-panel-count { padding:6px 9px; border:1px solid var(--line); border-radius:8px; color:var(--muted); font-size:9px; white-space:nowrap; }
.public-table-wrap { overflow-x:auto; }
.public-contest-table { width:100%; border-collapse:collapse; min-width:660px; }
.public-contest-table th { padding:11px 10px; background:var(--panel-2); color:var(--muted); font-size:9px; font-weight:700; text-align:right; white-space:nowrap; }
.public-contest-table th:first-child { border-radius:0 8px 8px 0; }
.public-contest-table th:last-child { border-radius:8px 0 0 8px; }
.public-contest-table td { padding:12px 10px; border-bottom:1px solid var(--line); color:var(--muted); font-size:9px; vertical-align:middle; white-space:nowrap; }
.public-contest-table tr:last-child td { border-bottom:0; }
.public-contest-table td:first-child { min-width:180px; white-space:normal; }
.public-contest-table td:first-child b { display:block; color:var(--text); font-size:11px; }
.public-contest-table td:first-child small { display:block; margin-top:4px; color:var(--muted); font-size:9px; line-height:1.7; }
.public-contest-table .status-badge { font-size:9px; }
.public-row-action { display:inline-flex; align-items:center; gap:3px; border:0; background:transparent; color:#aa8cff; font:inherit; font-size:9px; cursor:pointer; }
.public-empty { min-height:170px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:8px; color:var(--muted); text-align:center; }
.public-empty svg { color:#a98cff; }
.public-empty b { color:var(--text); font-size:12px; }
.public-empty span { font-size:9px; }
.public-table-footer { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-top:12px; padding-top:11px; border-top:1px solid var(--line); color:var(--muted); font-size:9px; }
.public-table-footer button { display:flex; align-items:center; gap:6px; border:0; background:transparent; color:#aa8cff; font:inherit; cursor:pointer; }
.public-sidebar { display:flex; flex-direction:column; gap:13px; }
.public-auth-card { text-align:right; }
.public-auth-icon { width:39px; height:39px; display:grid; place-items:center; border-radius:12px; background:rgba(153,119,255,.13); color:#ae93ff; }
.public-auth-card h2 { margin:12px 0 6px; font-size:15px; }
.public-auth-card p,.public-next-card>p { margin:0 0 14px; color:var(--muted); font-size:10px; line-height:1.9; }
.public-auth-card .button { margin-top:8px; }
.public-auth-card .button.full { justify-content:center; }
.public-side-heading { display:flex; align-items:center; gap:8px; margin-bottom:12px; color:#aa8cff; }
.public-side-heading b { color:var(--text); font-size:11px; }
.public-next-card>strong { display:block; font-size:12px; }
.public-next-date { display:block; margin-top:6px; color:var(--muted); font-size:9px; }
.public-guide-card { padding-bottom:10px; }
.public-guide-step { display:flex; align-items:flex-start; gap:10px; padding:9px 0; border-bottom:1px solid var(--line); }
.public-guide-step:last-child { border-bottom:0; }
.public-guide-step>span { width:24px; height:24px; flex:0 0 24px; display:grid; place-items:center; border-radius:8px; background:rgba(153,119,255,.12); color:#ae93ff; font-size:10px; font-weight:800; }
.public-guide-step div { display:flex; flex-direction:column; gap:3px; }
.public-guide-step b { font-size:10px; }
.public-guide-step small { color:var(--muted); font-size:9px; }
.public-bottom-info { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:13px; margin-top:16px; }
.public-bottom-info>div { display:grid; grid-template-columns:40px 1fr; align-items:center; column-gap:10px; padding:14px; border:1px solid var(--line); border-radius:14px; background:var(--panel); }
.public-info-icon { grid-row:span 2; width:38px; height:38px; display:grid; place-items:center; border-radius:11px; background:rgba(153,119,255,.12); color:#ae93ff; }
.public-bottom-info b { font-size:10px; }
.public-bottom-info p { margin:4px 0 0; color:var(--muted); font-size:9px; }
.public-footer { max-width:1260px; display:flex; justify-content:space-between; flex-wrap:wrap; gap:12px; margin:auto; padding:18px 24px 24px; border-top:1px solid var(--line); color:var(--muted); font-size:9px; }

@media(max-width:1100px) {
  .dashboard-metrics { grid-template-columns:repeat(2,minmax(0,1fr)); }
  .public-content-grid { grid-template-columns:minmax(0,1.4fr) minmax(240px,.8fr); }
}
@media(max-width:900px) {
  .redesign-shell .sidebar { right:0; width:290px; min-width:290px; transform:translateX(105%); }
  .redesign-shell.sidebar-open .sidebar { transform:translateX(0); }
  .redesign-shell .main-area { width:100%; margin:0; }
  .redesign-shell .mobile-appbar { position:sticky; z-index:46; top:0; height:58px; display:flex; align-items:center; justify-content:space-between; gap:12px; padding:0 16px; border-bottom:1px solid var(--line); background:color-mix(in srgb,var(--panel) 93%,transparent); backdrop-filter:blur(16px); }
  .redesign-shell .mobile-appbar .icon-button { width:38px; height:38px; }
  .sidebar-scrim { display:none; }
  .redesign-shell.sidebar-open .sidebar-scrim { position:fixed; z-index:55; display:block; inset:0; border:0; background:rgba(0,0,0,.48); }
  .redesign-shell .topbar { top:58px; height:58px; min-height:58px; }
  .redesign-shell .page-content { padding:20px 16px 28px; }
  .dashboard-hero { grid-template-columns:1fr; }
  .dashboard-next-card { max-width:none; }
  .public-header { flex-wrap:wrap; min-height:unset; padding:10px 18px; }
  .public-nav { order:3; width:100%; height:42px; overflow-x:auto; }
  .public-nav a { padding:0 10px; white-space:nowrap; }
  .public-content-grid { grid-template-columns:1fr; }
  .public-sidebar { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); }
  .public-auth-card { grid-row:span 2; }
}
@media(max-width:640px) {
  .dashboard-hero { padding:20px; border-radius:17px; }
  .dashboard-hero h1 { font-size:26px; }
  .dashboard-hero-actions { gap:7px; }
  .dashboard-hero-actions .button { flex:1; justify-content:center; }
  .dashboard-metrics { gap:8px; }
  .dashboard-metric { gap:8px; padding:11px 9px; }
  .metric-icon { width:32px; height:32px; flex-basis:32px; }
  .metric-text strong { font-size:19px; }
  .dashboard-list-panel { padding:14px; }
  .dashboard-list-heading { align-items:stretch; }
  .dashboard-search { min-width:100%; }
  .dashboard-list-panel .exam-grid { grid-template-columns:1fr; }
  .dashboard-bottom-grid { grid-template-columns:1fr; }
  .countdown-unit { min-width:49px; padding:8px 8px; }
  .countdown-unit strong { font-size:17px; }
  .start-countdown { align-items:flex-start; flex-direction:column; }
  .public-main { padding:12px 12px 24px; }
  .public-announcement { flex-wrap:wrap; font-size:9px; }
  .announcement-side { display:none; }
  .public-hero { grid-template-columns:1fr; gap:8px; padding:22px 18px; }
  .public-hero h1 { font-size:29px; }
  .public-hero-side { min-height:205px; }
  .public-hero-stat-card { width:100%; }
  .public-header { gap:10px; padding:10px 12px; }
  .public-brand { font-size:14px; }
  .public-brand small { display:none; }
  .public-actions { gap:6px; }
  .public-actions .button { padding:8px 10px; }
  .public-sidebar { display:flex; }
  .public-bottom-info { grid-template-columns:1fr; }
  .public-footer { padding:16px 13px 22px; }
  .public-panel { padding:14px; }
  .public-panel-heading { align-items:flex-start; }
  .redesign-shell .topbar { padding:0 14px; }
  .redesign-shell .breadcrumb { font-size:10px; }
}
"""
cssp.write_text(css, encoding="utf-8")
print("Applied responsive dashboard, public contest homepage and non-zero countdown.")
