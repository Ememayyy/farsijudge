from pathlib import Path

css_path = Path("src/style.css")
css = css_path.read_text(encoding="utf-8")
css += """

/* Definitive mobile drawer layout: pin navigation to the drawer's top edge. */
@media (max-width: 900px) {
  .redesign-shell .sidebar {
    position: fixed !important;
    top: calc(58px + env(safe-area-inset-top, 0px)) !important;
    right: 0 !important;
    bottom: 0 !important;
    left: auto !important;
    width: min(300px, calc(100vw - 36px)) !important;
    min-width: 0 !important;
    height: auto !important;
    max-height: none !important;
    box-sizing: border-box !important;
    display: block !important;
    overflow: hidden !important;
    padding: 12px 14px calc(12px + env(safe-area-inset-bottom, 0px)) !important;
    z-index: 90 !important;
    background: var(--panel) !important;
    transform: translateX(105%);
    transition: transform .22s ease !important;
    box-shadow: -18px 0 45px rgba(0,0,0,.18);
  }

  .redesign-shell.sidebar-open .sidebar {
    transform: translateX(0) !important;
  }

  /* Keep the brand as a compact header; the links are independently docked. */
  .redesign-shell .sidebar > .brand {
    position: absolute !important;
    top: 12px !important;
    right: 14px !important;
    left: 14px !important;
    height: 44px !important;
    min-height: 44px !important;
    margin: 0 !important;
    padding: 2px 8px 10px !important;
    display: flex !important;
    align-items: center !important;
    z-index: 2;
  }

  .redesign-shell .sidebar .workspace-label,
  .redesign-shell .sidebar > .sidebar-bottom {
    display: none !important;
  }

  /* Absolute positioning removes the flex/grid flow that kept pushing links down. */
  .redesign-shell .sidebar .side-nav {
    position: absolute !important;
    top: 68px !important;
    right: 14px !important;
    bottom: calc(12px + env(safe-area-inset-bottom, 0px)) !important;
    left: 14px !important;
    inset-inline: 14px !important;
    width: auto !important;
    height: auto !important;
    min-height: 0 !important;
    max-height: none !important;
    margin: 0 !important;
    padding: 8px 2px 14px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: flex-start !important;
    align-items: stretch !important;
    gap: 7px !important;
    overflow-x: hidden !important;
    overflow-y: auto !important;
    overscroll-behavior: contain;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: thin;
    touch-action: pan-y;
  }

  .redesign-shell .sidebar .side-nav .nav-item {
    position: relative !important;
    inset: auto !important;
    flex: 0 0 auto !important;
    display: flex !important;
    width: 100% !important;
    min-width: 0 !important;
    min-height: 48px !important;
    height: 48px !important;
    margin: 0 !important;
    padding-inline: 13px !important;
    transform: none !important;
    border-radius: 12px !important;
  }

  .redesign-shell .mobile-appbar {
    position: fixed !important;
    z-index: 100 !important;
    top: 0 !important;
    right: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: calc(58px + env(safe-area-inset-top, 0px)) !important;
    padding-top: env(safe-area-inset-top, 0px) !important;
  }

  .redesign-shell .mobile-menu-toggle {
    position: relative;
    z-index: 101;
    width: 42px !important;
    height: 42px !important;
    min-width: 42px;
    display: grid !important;
    place-items: center;
    border-radius: 12px !important;
    touch-action: manipulation;
  }

  .redesign-shell .sidebar-scrim,
  .redesign-shell.sidebar-open .sidebar-scrim {
    position: fixed !important;
    top: calc(58px + env(safe-area-inset-top, 0px)) !important;
    right: 0 !important;
    bottom: 0 !important;
    left: 0 !important;
    z-index: 85 !important;
    display: block !important;
    border: 0 !important;
    background: rgba(8, 10, 18, .52) !important;
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
    transition: opacity .2s ease, visibility .2s ease;
  }

  .redesign-shell.sidebar-open .sidebar-scrim {
    opacity: 1;
    visibility: visible;
    pointer-events: auto;
  }
}

@media (max-width: 900px) and (max-height: 560px) {
  .redesign-shell .sidebar .side-nav { gap: 4px !important; padding-top: 3px !important; }
  .redesign-shell .sidebar .side-nav .nav-item { min-height: 42px !important; height: 42px !important; }
}

/* Small usability improvements across the platform. */
.redesign-shell button,
.public-site button,
.redesign-shell a,
.public-site a {
  -webkit-tap-highlight-color: transparent;
}

.redesign-shell button:focus-visible,
.public-site button:focus-visible,
.redesign-shell a:focus-visible,
.public-site a:focus-visible,
.redesign-shell input:focus-visible,
.public-site input:focus-visible,
.redesign-shell textarea:focus-visible,
.public-site textarea:focus-visible,
.redesign-shell select:focus-visible,
.public-site select:focus-visible {
  outline: 3px solid rgba(157, 125, 255, .7) !important;
  outline-offset: 3px !important;
}

.redesign-shell .button,
.public-site .button {
  min-height: 42px;
  border-radius: 11px;
  transition: transform .16s ease, box-shadow .16s ease, background .16s ease;
}

.redesign-shell .button:active,
.public-site .button:active {
  transform: scale(.98);
}

.redesign-shell input,
.redesign-shell textarea,
.redesign-shell select,
.public-site input,
.public-site textarea,
.public-site select {
  min-height: 42px;
  border-radius: 10px;
}

.redesign-shell .exam-card,
.public-site .public-panel,
.redesign-shell .dashboard-next-card {
  transition: border-color .18s ease, box-shadow .18s ease, transform .18s ease;
}

.redesign-shell .exam-card:hover,
.public-site .public-panel:hover {
  border-color: rgba(157, 125, 255, .32);
  box-shadow: 0 10px 28px rgba(0, 0, 0, .08);
}

@media (prefers-reduced-motion: reduce) {
  .redesign-shell *,
  .public-site * {
    scroll-behavior: auto !important;
    transition-duration: .01ms !important;
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
  }
}
"""
css_path.write_text(css, encoding="utf-8")
print("Applied absolutely top-docked mobile navigation and usability refinements.")


# Add sign-out action to the account/profile area.
app_path = Path("src/App.tsx")
app = app_path.read_text(encoding="utf-8")
profile_anchor = """{page === 'profile' && <ProfilePage profile={profile} email={session?.user.email || (isDemo ? demoUser.email : '')} exams={exams} />}"""
profile_replacement = """{page === 'profile' && <>
          <ProfilePage profile={profile} email={session?.user.email || (isDemo ? demoUser.email : '')} exams={exams} />
          <div className="profile-menu-actions">
            <div><b>حساب کاربری</b><span>مدیریت نشست و دسترسی حساب</span></div>
            <button className="button soft danger-text" onClick={async () => {
              if (supabase) await supabase.auth.signOut()
              setPage('welcome')
            }}>خروج از حساب کاربری</button>
          </div>
        </>}"""
if app.count(profile_anchor) != 1:
    raise SystemExit("Profile page insertion point mismatch: " + str(app.count(profile_anchor)))
app = app.replace(profile_anchor, profile_replacement, 1)
app_path.write_text(app, encoding="utf-8")

css_path = Path("src/style.css")
css = css_path.read_text(encoding="utf-8")
css += """
.profile-menu-actions {
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:16px;
  flex-wrap:wrap;
  margin-top:16px;
  padding:16px 18px;
  border:1px solid var(--line);
  border-radius:14px;
  background:var(--panel);
}
.profile-menu-actions > div { display:flex; flex-direction:column; gap:4px; }
.profile-menu-actions b { color:var(--text); font-size:13px; }
.profile-menu-actions span { color:var(--muted); font-size:11px; }
.profile-menu-actions .danger-text { color:#dc6262; border-color:rgba(220,98,98,.25); }
@media(max-width:640px) {
  .profile-menu-actions { align-items:stretch; flex-direction:column; }
  .profile-menu-actions .button { justify-content:center; }
}
"""
css_path.write_text(css, encoding="utf-8")
print("Added a responsive sign-out action to the profile area.")


# Add public contest participant counts and a dedicated participant directory page.
app_path = Path("src/App.tsx")
app = app_path.read_text(encoding="utf-8")

once_anchor = """  const runningCount = publicExams.filter((exam) => getStatus(exam, now) === 'active').length
  return <div className="public-site">"""
once_replacement = """  const runningCount = publicExams.filter((exam) => getStatus(exam, now) === 'active').length
  const [participantCounts, setParticipantCounts] = useState<Record<string, number>>({})
  const [selectedContest, setSelectedContest] = useState<Exam | null>(null)
  const [participants, setParticipants] = useState<{ display_name: string; username: string; team_name: string | null; registered_at: string }[]>([])
  const [participantsLoading, setParticipantsLoading] = useState(false)

  useEffect(() => {
    const client = supabase
    if (!client) return
    let alive = true
    const loadCounts = async () => {
      const { data } = await client.rpc('get_contest_participant_counts')
      if (!alive || !data) return
      const next: Record<string, number> = {}
      data.forEach((row: { exam_id: string; participant_count: number }) => {
        next[row.exam_id] = Number(row.participant_count) || 0
      })
      setParticipantCounts(next)
    }
    void loadCounts()
    return () => { alive = false }
  }, [exams.length])

  useEffect(() => {
    const client = supabase
    const contest = selectedContest
    if (!contest || !client) return
    let alive = true
    setParticipantsLoading(true)
    setParticipants([])
    const loadParticipants = async () => {
      const { data, error } = await client.rpc('get_contest_participants', { p_exam_id: contest.id })
      if (!alive) return
      if (!error && data) setParticipants(data as { display_name: string; username: string; team_name: string | null; registered_at: string }[])
      setParticipantsLoading(false)
    }
    void loadParticipants()
    return () => { alive = false }
  }, [selectedContest?.id])

  if (selectedContest) return <div className="public-site">
    <header className="public-header">
      <a href="#public-top" className="public-brand" onClick={(event) => { event.preventDefault(); setSelectedContest(null) }}><span className="public-brand-mark"><BookOpen size={23} /></span><span>فارسی جاج</span><small>FARSI JUDGE</small></a>
      <div className="public-actions">
        <button className="icon-button" onClick={onToggleTheme} aria-label="تغییر پوسته">{theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}</button>
        <button className="button soft small" onClick={() => setSelectedContest(null)}><ArrowLeft size={15} />بازگشت به مسابقه‌ها</button>
      </div>
    </header>
    <main className="public-main participants-page">
      <section className="participants-hero">
        <div className="participants-hero-copy">
          <div className="public-kicker"><span>CONTEST PARTICIPANTS</span><i />فهرست شرکت‌کنندگان</div>
          <h1>{selectedContest.title}</h1>
          <p>افرادی که برای این مسابقه ثبت‌نام کرده‌اند؛ شرکت‌کنندگان تیمی نیز به‌صورت جداگانه نمایش داده می‌شوند.</p>
          <div className="participants-hero-meta"><span><CalendarDays size={16} />{dateText(selectedContest.starts_at)}</span><span><Users size={16} />{fa(participantCounts[selectedContest.id] || 0)} شرکت‌کننده</span></div>
        </div>
        <div className="participants-hero-count"><Users size={25} /><strong>{fa(participantCounts[selectedContest.id] || 0)}</strong><span>REGISTERED</span></div>
      </section>
      <section className="public-panel participants-list-panel">
        <div className="participants-list-heading">
          <div><div className="public-panel-kicker">THE LINEUP</div><h2>شرکت‌کنندگان مسابقه</h2><p>فهرست بر اساس زمان ثبت‌نام مرتب شده است.</p></div>
          <span className="public-panel-count">{fa(participants.length)} نفر</span>
        </div>
        {participantsLoading ? <div className="participants-loading"><span className="participants-spinner" />در حال دریافت فهرست شرکت‌کنندگان...</div>
          : participants.length === 0 ? <div className="public-empty"><Users size={25} /><b>هنوز کسی ثبت‌نام نکرده است</b><span>به محض ثبت‌نام افراد، نام آن‌ها در این صفحه نمایش داده می‌شود.</span></div>
          : <div className="participants-grid">{participants.map((person, index) => <article className="participant-card" key={person.username + '-' + index}>
              <div className="participant-avatar">{(person.display_name || person.username || '?').trim().slice(0, 1)}</div>
              <div className="participant-info"><b>{person.display_name || person.username}</b><span>@{person.username}</span></div>
              <div className="participant-kind">{person.team_name ? <><Users size={14} />{person.team_name}</> : <><UserRound size={14} />انفرادی</>}</div>
              <div className="participant-rank">#{fa(index + 1)}</div>
            </article>)}</div>}
      </section>
      <div className="participants-footer"><ShieldCheck size={16} />اطلاعات نمایش‌داده‌شده فقط شامل نام نمایشی و نام کاربری است؛ ایمیل یا اطلاعات خصوصی منتشر نمی‌شود.</div>
    </main>
  </div>

  return <div className="public-site">"""
if app.count(once_anchor) != 1:
    raise SystemExit("WelcomePage participant state anchor mismatch: " + str(app.count(once_anchor)))
app = app.replace(once_anchor, once_replacement, 1)

table_anchor = """<thead><tr><th>عنوان مسابقه</th><th>شروع</th><th>مدت</th><th>وضعیت</th><th></th></tr></thead>"""
table_replacement = """<thead><tr><th>عنوان مسابقه</th><th>شروع</th><th>مدت</th><th>وضعیت</th><th>شرکت‌کنندگان</th><th></th></tr></thead>"""
if app.count(table_anchor) != 1:
    raise SystemExit("Public contest table header anchor mismatch: " + str(app.count(table_anchor)))
app = app.replace(table_anchor, table_replacement, 1)

row_anchor = """                  <td><StatusBadge status={getStatus(exam, now)} /></td>
                  <td><button className="public-row-action" onClick={onLogin}>جزئیات <ChevronLeft size={14} /></button></td>"""
row_replacement = """                  <td><StatusBadge status={getStatus(exam, now)} /></td>
                  <td><button className="participant-count-link" onClick={() => setSelectedContest(exam)} aria-label={"نمایش شرکت‌کنندگان " + exam.title}><span>#</span>{fa(participantCounts[exam.id] || 0)}</button></td>
                  <td><button className="public-row-action" onClick={onLogin}>جزئیات <ChevronLeft size={14} /></button></td>"""
if app.count(row_anchor) != 1:
    raise SystemExit("Public contest row anchor mismatch: " + str(app.count(row_anchor)))
app = app.replace(row_anchor, row_replacement, 1)
app = app.replace('<td colSpan={5}><div className="public-empty">', '<td colSpan={6}><div className="public-empty">', 1)

app_path.write_text(app, encoding="utf-8")

css_path = Path("src/style.css")
css = css_path.read_text(encoding="utf-8")
css += """
.participant-count-link {
  display:inline-flex; align-items:center; gap:6px; border:1px solid rgba(139,112,245,.28);
  border-radius:999px; padding:7px 12px; background:rgba(139,112,245,.09); color:var(--accent);
  font:inherit; font-size:12px; font-weight:800; cursor:pointer; transition:all .18s ease;
}
.participant-count-link span { font-size:15px; opacity:.8; }
.participant-count-link:hover { transform:translateY(-2px); background:rgba(139,112,245,.16); box-shadow:0 7px 20px rgba(111,82,210,.14); }
.participants-page { max-width:1120px; }
.participants-hero {
  position:relative; display:flex; align-items:center; justify-content:space-between; gap:28px;
  overflow:hidden; margin:24px 0; padding:clamp(24px,5vw,48px); border:1px solid rgba(143,119,242,.2);
  border-radius:26px; background:radial-gradient(circle at 85% 15%,rgba(147,115,255,.2),transparent 34%),linear-gradient(125deg,var(--panel),var(--panel-soft));
}
.participants-hero-copy { position:relative; z-index:1; }
.participants-hero h1 { margin:12px 0 8px; font-size:clamp(25px,4vw,38px); letter-spacing:-.8px; }
.participants-hero p { max-width:650px; color:var(--muted); line-height:1.9; font-size:13px; }
.participants-hero-meta { display:flex; flex-wrap:wrap; gap:18px; margin-top:20px; color:var(--muted); font-size:12px; }
.participants-hero-meta span { display:flex; align-items:center; gap:7px; }
.participants-hero-count {
  flex:0 0 150px; width:150px; height:150px; display:flex; flex-direction:column; align-items:center; justify-content:center;
  gap:4px; border:1px solid rgba(150,124,255,.28); border-radius:36px;
  background:linear-gradient(145deg,rgba(150,124,255,.2),rgba(150,124,255,.04)); color:var(--accent);
  box-shadow:0 18px 45px rgba(90,65,180,.12);
}
.participants-hero-count strong { font-size:40px; line-height:1.15; }
.participants-hero-count span { font-size:9px; font-weight:900; letter-spacing:2px; opacity:.7; }
.participants-list-panel { padding:clamp(18px,3vw,30px); }
.participants-list-heading { display:flex; align-items:center; justify-content:space-between; gap:16px; margin-bottom:22px; }
.participants-list-heading h2 { margin:6px 0; font-size:20px; }
.participants-list-heading p { color:var(--muted); font-size:12px; }
.participants-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }
.participant-card {
  display:flex; align-items:center; gap:12px; min-width:0; padding:13px; border:1px solid var(--line);
  border-radius:15px; background:var(--panel); transition:transform .16s ease,border-color .16s ease,box-shadow .16s ease;
}
.participant-card:hover { transform:translateY(-2px); border-color:rgba(143,119,242,.4); box-shadow:0 9px 24px rgba(20,15,50,.07); }
.participant-avatar { flex:0 0 42px; width:42px; height:42px; display:grid; place-items:center; border-radius:13px; color:white; font-size:17px; font-weight:900; background:linear-gradient(145deg,#9275f5,#5b4ab2); }
.participant-info { display:flex; flex-direction:column; gap:4px; min-width:0; flex:1; }
.participant-info b { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-size:13px; }
.participant-info span { color:var(--muted); font-size:11px; direction:ltr; text-align:right; }
.participant-kind { display:flex; align-items:center; gap:5px; color:var(--muted); font-size:10px; white-space:nowrap; }
.participant-rank { color:var(--muted); font-size:11px; font-weight:800; direction:ltr; }
.participants-loading { display:flex; align-items:center; justify-content:center; gap:12px; padding:50px 10px; color:var(--muted); font-size:13px; }
.participants-spinner { width:18px; height:18px; border:2px solid var(--line); border-top-color:var(--accent); border-radius:50%; animation:participant-spin .8s linear infinite; }
@keyframes participant-spin { to { transform:rotate(360deg); } }
.participants-footer { display:flex; align-items:center; gap:8px; margin:14px 4px; color:var(--muted); font-size:11px; }
@media(max-width:700px) {
  .participants-hero { align-items:flex-start; padding:22px; }
  .participants-hero-count { flex-basis:92px; width:92px; height:92px; border-radius:24px; }
  .participants-hero-count strong { font-size:27px; }
  .participants-hero-count span { font-size:7px; letter-spacing:1px; }
  .participants-grid { grid-template-columns:1fr; }
  .participant-card { gap:9px; padding:10px; }
  .participant-kind { max-width:90px; overflow:hidden; text-overflow:ellipsis; }
}
@media(max-width:430px) {
  .participants-hero { flex-direction:column-reverse; }
  .participants-hero-count { flex-direction:row; width:auto; height:auto; padding:8px 13px; gap:7px; }
  .participants-hero-count strong { font-size:21px; }
  .participants-hero-count span { display:none; }
  .participants-footer { align-items:flex-start; line-height:1.8; }
}
"""
css_path.write_text(css, encoding="utf-8")
print("Added participant counts and participant directory UI.")


# Show participant counts beside each contest in the signed-in user's dashboard.
app_path = Path("src/App.tsx")
app = app_path.read_text(encoding="utf-8")

dashboard_state_anchor = """  const [search, setSearch] = useState('')
  const filtered = (filter === 'all' ? exams : filter === 'active' ? active : filter === 'upcoming' ? upcoming : ended)"""
dashboard_state_replacement = """  const [search, setSearch] = useState('')
  const [dashboardParticipantCounts, setDashboardParticipantCounts] = useState<Record<string, number>>({})
  const [selectedParticipantContest, setSelectedParticipantContest] = useState<Exam | null>(null)
  const [dashboardParticipants, setDashboardParticipants] = useState<{ display_name: string; username: string; team_name: string | null; registered_at: string }[]>([])
  const [dashboardParticipantsLoading, setDashboardParticipantsLoading] = useState(false)
  const filtered = (filter === 'all' ? exams : filter === 'active' ? active : filter === 'upcoming' ? upcoming : ended)"""
if app.count(dashboard_state_anchor) != 1:
    raise SystemExit("Dashboard state insertion anchor mismatch: " + str(app.count(dashboard_state_anchor)))
app = app.replace(dashboard_state_anchor, dashboard_state_replacement, 1)

dashboard_effect_anchor = """  const firstName = profile?.full_name?.trim().split(/\\s+/)[0] || 'خوش آمدید'

  return <>"""
dashboard_effect_replacement = """  const firstName = profile?.full_name?.trim().split(/\\s+/)[0] || 'خوش آمدید'

  useEffect(() => {
    const client = supabase
    if (!client) return
    let alive = true
    const loadCounts = async () => {
      const { data } = await client.rpc('get_contest_participant_counts')
      if (!alive || !data) return
      const next: Record<string, number> = {}
      data.forEach((row: { exam_id: string; participant_count: number }) => {
        next[row.exam_id] = Number(row.participant_count) || 0
      })
      setDashboardParticipantCounts(next)
    }
    void loadCounts()
    return () => { alive = false }
  }, [exams.length])

  useEffect(() => {
    const client = supabase
    const contest = selectedParticipantContest
    if (!client || !contest) return
    let alive = true
    setDashboardParticipantsLoading(true)
    setDashboardParticipants([])
    const loadParticipants = async () => {
      const { data, error } = await client.rpc('get_contest_participants', { p_exam_id: contest.id })
      if (!alive) return
      if (!error && data) setDashboardParticipants(data as { display_name: string; username: string; team_name: string | null; registered_at: string }[])
      setDashboardParticipantsLoading(false)
    }
    void loadParticipants()
    return () => { alive = false }
  }, [selectedParticipantContest?.id])

  if (selectedParticipantContest) return <section className="dashboard-participants-page">
    <div className="dashboard-participants-nav">
      <button className="back-button" onClick={() => setSelectedParticipantContest(null)}><ArrowLeft size={16} />بازگشت به مسابقه‌ها</button>
    </div>
    <section className="participants-hero">
      <div className="participants-hero-copy">
        <div className="public-kicker"><span>CONTEST PARTICIPANTS</span><i />فهرست شرکت‌کنندگان</div>
        <h1>{selectedParticipantContest.title}</h1>
        <p>افرادی که برای این مسابقه ثبت‌نام کرده‌اند؛ اعضای تیم‌ها نیز به‌صورت جداگانه نمایش داده می‌شوند.</p>
        <div className="participants-hero-meta"><span><CalendarDays size={16} />{dateText(selectedParticipantContest.starts_at)}</span><span><Users size={16} />{fa(dashboardParticipantCounts[selectedParticipantContest.id] || 0)} شرکت‌کننده</span></div>
      </div>
      <div className="participants-hero-count"><Users size={25} /><strong>{fa(dashboardParticipantCounts[selectedParticipantContest.id] || 0)}</strong><span>REGISTERED</span></div>
    </section>
    <section className="public-panel participants-list-panel">
      <div className="participants-list-heading">
        <div><div className="public-panel-kicker">THE LINEUP</div><h2>شرکت‌کنندگان مسابقه</h2><p>فهرست بر اساس زمان ثبت‌نام مرتب شده است.</p></div>
        <span className="public-panel-count">{fa(dashboardParticipants.length)} نفر</span>
      </div>
      {dashboardParticipantsLoading ? <div className="participants-loading"><span className="participants-spinner" />در حال دریافت فهرست شرکت‌کنندگان...</div>
        : dashboardParticipants.length === 0 ? <div className="public-empty"><Users size={25} /><b>هنوز کسی ثبت‌نام نکرده است</b><span>به محض ثبت‌نام افراد، نام آن‌ها در این صفحه نمایش داده می‌شود.</span></div>
        : <div className="participants-grid">{dashboardParticipants.map((person, index) => <article className="participant-card" key={person.username + '-' + index}>
            <div className="participant-avatar">{(person.display_name || person.username || '?').trim().slice(0, 1)}</div>
            <div className="participant-info"><b>{person.display_name || person.username}</b><span>@{person.username}</span></div>
            <div className="participant-kind">{person.team_name ? <><Users size={14} />{person.team_name}</> : <><UserRound size={14} />انفرادی</>}</div>
            <div className="participant-rank">#{fa(index + 1)}</div>
          </article>)}</div>}
    </section>
    <div className="participants-footer"><ShieldCheck size={16} />فقط نام نمایشی و نام کاربری افراد نمایش داده می‌شود؛ ایمیل و اطلاعات خصوصی مخفی می‌ماند.</div>
  </section>

  return <>"""
if app.count(dashboard_effect_anchor) != 1:
    raise SystemExit("Dashboard effects insertion anchor mismatch: " + str(app.count(dashboard_effect_anchor)))
app = app.replace(dashboard_effect_anchor, dashboard_effect_replacement, 1)

dashboard_cards_anchor = """        : <div className="exam-grid">{filtered.map((exam) => <ExamCard key={exam.id} exam={exam} now={now} onOpen={() => onOpen(exam)}
          registered={myRegistrations.includes(exam.id) || myTeamRegistrations.includes(exam.id)}
          teamMember={Boolean(team)} teamCaptain={team?.role === 'captain'} onRegister={() => onRegister(exam)} />)}</div>}"""
dashboard_cards_replacement = """        : <div className="exam-grid">{filtered.map((exam) => <div className="dashboard-exam-card-wrap" key={exam.id}>
          <button type="button" className="dashboard-participant-count" onClick={() => setSelectedParticipantContest(exam)} aria-label={"نمایش شرکت‌کنندگان " + exam.title}>
            <span>#</span>{fa(dashboardParticipantCounts[exam.id] || 0)}
          </button>
          <ExamCard exam={exam} now={now} onOpen={() => onOpen(exam)}
            registered={myRegistrations.includes(exam.id) || myTeamRegistrations.includes(exam.id)}
            teamMember={Boolean(team)} teamCaptain={team?.role === 'captain'} onRegister={() => onRegister(exam)} />
        </div>)}</div>}"""
if app.count(dashboard_cards_anchor) != 1:
    raise SystemExit("Dashboard exam-card insertion anchor mismatch: " + str(app.count(dashboard_cards_anchor)))
app = app.replace(dashboard_cards_anchor, dashboard_cards_replacement, 1)

app_path.write_text(app, encoding="utf-8")

css_path = Path("src/style.css")
css = css_path.read_text(encoding="utf-8")
css += """
.dashboard-exam-card-wrap { position:relative; min-width:0; height:100%; }
.dashboard-exam-card-wrap > .exam-card { height:100%; }
.dashboard-participant-count {
  position:absolute; z-index:5; top:12px; left:12px; display:inline-flex; align-items:center; gap:5px;
  min-height:29px; padding:5px 10px; border:1px solid rgba(139,112,245,.3); border-radius:999px;
  background:var(--panel); color:var(--accent); box-shadow:0 3px 12px rgba(35,25,75,.1);
  font:inherit; font-size:11px; font-weight:850; cursor:pointer; direction:ltr;
  transition:transform .16s ease,background .16s ease,box-shadow .16s ease;
}
.dashboard-participant-count span { font-size:14px; line-height:1; opacity:.8; }
.dashboard-participant-count:hover { transform:translateY(-2px); background:rgba(139,112,245,.12); box-shadow:0 6px 18px rgba(90,65,180,.16); }
.dashboard-participant-count:focus-visible { outline:3px solid rgba(157,125,255,.65); outline-offset:3px; }
.dashboard-participants-page { width:100%; min-width:0; }
.dashboard-participants-nav { display:flex; justify-content:flex-start; margin:0 0 12px; }
.dashboard-participants-page .participants-hero { margin-top:8px; }
@media(max-width:640px) {
  .dashboard-participant-count { top:9px; left:9px; min-height:27px; padding:4px 8px; }
}
"""
css_path.write_text(css, encoding="utf-8")
print("Added participant counts and directory navigation inside each user's dashboard.");


# Manage a user's existing registration and reposition the participant count.
app_path = Path("src/App.tsx")
app = app_path.read_text(encoding="utf-8")

exam_card_signature = """function ExamCard({ exam, now, onOpen, registered, teamMember, teamCaptain, onRegister }: {
  exam: Exam; now: number; onOpen: () => void; registered: boolean
  teamMember: boolean; teamCaptain: boolean; onRegister: () => void
}) {"""
exam_card_signature_new = """function ExamCard({ exam, now, onOpen, registered, teamMember, teamCaptain, onRegister, participantCount, onShowParticipants, onManageRegistration }: {
  exam: Exam; now: number; onOpen: () => void; registered: boolean
  teamMember: boolean; teamCaptain: boolean; onRegister: () => void
  participantCount: number; onShowParticipants: () => void; onManageRegistration: () => void
}) {"""
if app.count(exam_card_signature) != 1:
    raise SystemExit("ExamCard signature insertion mismatch: " + str(app.count(exam_card_signature)))
app = app.replace(exam_card_signature, exam_card_signature_new, 1)

exam_card_title = """    <h3>{exam.title}</h3><p className="exam-description">"""
exam_card_title_new = """    <div className="exam-card-heading">
      <h3>{exam.title}</h3>
      <button type="button" className="exam-participant-count" onClick={onShowParticipants} aria-label={"نمایش شرکت‌کنندگان " + exam.title}>
        <Users size={13} /><span>#</span>{fa(participantCount)}
      </button>
    </div><p className="exam-description">"""
if app.count(exam_card_title) != 1:
    raise SystemExit("ExamCard title insertion mismatch: " + str(app.count(exam_card_title)))
app = app.replace(exam_card_title, exam_card_title_new, 1)

registered_label = """{registered ? <span className="registration-done"><CheckCircle2 size={15} />ثبت‌نام انجام شده</span>"""
registered_label_new = """{registered ? <button type="button" className="registration-done registration-manage-link" onClick={onManageRegistration} title="مدیریت یا لغو ثبت‌نام"><CheckCircle2 size={15} />ثبت‌نام انجام شده<ChevronLeft size={13} /></button>"""
if app.count(registered_label) != 1:
    raise SystemExit("ExamCard registered label insertion mismatch: " + str(app.count(registered_label)))
app = app.replace(registered_label, registered_label_new, 1)

participant_state_anchor = """  const [selectedParticipantContest, setSelectedParticipantContest] = useState<Exam | null>(null)"""
if app.count(participant_state_anchor) != 1:
    raise SystemExit("Dashboard participant state anchor mismatch: " + str(app.count(participant_state_anchor)))
app = app.replace(participant_state_anchor, participant_state_anchor + """
  const [selectedRegistrationContest, setSelectedRegistrationContest] = useState<Exam | null>(null)
  const [unregisterBusy, setUnregisterBusy] = useState(false)
  const [unregisterError, setUnregisterError] = useState('')""", 1)

dashboard_cards_old = """        : <div className="exam-grid">{filtered.map((exam) => <div className="dashboard-exam-card-wrap" key={exam.id}>
          <button type="button" className="dashboard-participant-count" onClick={() => setSelectedParticipantContest(exam)} aria-label={"نمایش شرکت‌کنندگان " + exam.title}>
            <span>#</span>{fa(dashboardParticipantCounts[exam.id] || 0)}
          </button>
          <ExamCard exam={exam} now={now} onOpen={() => onOpen(exam)}
            registered={myRegistrations.includes(exam.id) || myTeamRegistrations.includes(exam.id)}
            teamMember={Boolean(team)} teamCaptain={team?.role === 'captain'} onRegister={() => onRegister(exam)} />
        </div>)}</div>}"""
dashboard_cards_new = """        : <div className="exam-grid">{filtered.map((exam) => <ExamCard key={exam.id} exam={exam} now={now} onOpen={() => onOpen(exam)}
          registered={myRegistrations.includes(exam.id) || myTeamRegistrations.includes(exam.id)}
          teamMember={Boolean(team)} teamCaptain={team?.role === 'captain'} onRegister={() => onRegister(exam)}
          participantCount={dashboardParticipantCounts[exam.id] || 0}
          onShowParticipants={() => setSelectedParticipantContest(exam)}
          onManageRegistration={() => { setUnregisterError(''); setSelectedRegistrationContest(exam) }} />)}</div>}"""
if app.count(dashboard_cards_old) != 1:
    raise SystemExit("Dashboard card wrapper replacement mismatch: " + str(app.count(dashboard_cards_old)))
app = app.replace(dashboard_cards_old, dashboard_cards_new, 1)

management_branch = """  if (selectedRegistrationContest) {
    const teamRegistered = myTeamRegistrations.includes(selectedRegistrationContest.id)
    const canCancel = getStatus(selectedRegistrationContest, now) === 'upcoming' && (!teamRegistered || team?.role === 'captain') && !isDemo
    const cancelRegistration = async () => {
      const client = supabase
      const contest = selectedRegistrationContest
      if (!client || !contest || unregisterBusy) return
      setUnregisterBusy(true)
      setUnregisterError('')
      const { error } = await client.rpc('unregister_from_exam', { p_exam_id: contest.id })
      if (error) {
        setUnregisterError(error.message || 'لغو ثبت‌نام انجام نشد.')
        setUnregisterBusy(false)
        return
      }
      await onRefresh()
      setUnregisterBusy(false)
      setSelectedRegistrationContest(null)
    }
    return <section className="dashboard-registration-page">
      <div className="dashboard-registration-nav">
        <button className="back-button" onClick={() => setSelectedRegistrationContest(null)}><ArrowLeft size={16} />بازگشت به مسابقه‌ها</button>
      </div>
      <section className="dashboard-registration-hero">
        <div className="dashboard-registration-copy">
          <div className="eyebrow">REGISTRATION MANAGEMENT</div>
          <h1>مدیریت ثبت‌نام مسابقه</h1>
          <p>از این بخش می‌توانی وضعیت ثبت‌نام خودت را مدیریت کنی.</p>
        </div>
        <span className="dashboard-registration-status"><CheckCircle2 size={17} />ثبت‌نام فعال</span>
      </section>
      <section className="public-panel dashboard-registration-panel">
        <div className="dashboard-registration-contest">
          <div className="dashboard-registration-icon"><Trophy size={22} /></div>
          <div><span>مسابقهٔ انتخاب‌شده</span><h2>{selectedRegistrationContest.title}</h2><small><CalendarDays size={14} />{dateText(selectedRegistrationContest.starts_at)}</small></div>
        </div>
        <div className="dashboard-registration-detail">
          <div><span>وضعیت</span><b className="registration-state-active">ثبت‌نام انجام شده</b></div>
          <div><span>نوع ثبت‌نام</span><b>{teamRegistered ? 'تیمی' : 'انفرادی'}</b></div>
          {teamRegistered && <div><span>تیم</span><b>{team?.name || 'تیم شما'}</b></div>}
        </div>
        <div className="dashboard-registration-note">
          <ShieldCheck size={18} />
          <p>با لغو ثبت‌نام، نامت (و در صورت ثبت‌نام تیمی، کل تیمت) از فهرست شرکت‌کنندگان حذف می‌شود. تا قبل از شروع مسابقه می‌توانی دوباره ثبت‌نام کنی.</p>
        </div>
        {teamRegistered && team?.role !== 'captain' && <div className="dashboard-registration-warning">ثبت‌نام تیمی را فقط کاپیتان تیم می‌تواند لغو کند. برای لغو، از کاپیتان بخواه اقدام کند.</div>}
        {getStatus(selectedRegistrationContest, now) !== 'upcoming' && <div className="dashboard-registration-warning">مهلت لغو ثبت‌نام به پایان رسیده است؛ پس از شروع مسابقه امکان لغو وجود ندارد.</div>}
        {isDemo && <div className="dashboard-registration-warning">در حالت نمایشی امکان تغییر ثبت‌نام وجود ندارد.</div>}
        {unregisterError && <div className="dashboard-registration-error">{unregisterError}</div>}
        <div className="dashboard-registration-actions">
          <button className="button soft" onClick={() => setSelectedRegistrationContest(null)}>بازگشت</button>
          <button className="button danger dashboard-unregister-button" disabled={!canCancel || unregisterBusy} onClick={() => void cancelRegistration()}>
            {unregisterBusy ? 'در حال لغو ثبت‌نام...' : teamRegistered ? 'لغو ثبت‌نام تیم' : 'لغو ثبت‌نام من'}
            <XCircle size={16} />
          </button>
        </div>
      </section>
    </section>
  }

"""
const registrationBranchAnchor = """  if (selectedParticipantContest) return <section className="dashboard-participants-page">"""
if (app.count(registrationBranchAnchor) != 1) {
    raise SystemExit("Dashboard registration page branch anchor mismatch: " + str(app.count(registrationBranchAnchor)))
}
app = app.replace(registrationBranchAnchor, management_branch + registrationBranchAnchor, 1)

app_path.write_text(app, encoding="utf-8")

css_path = Path("src/style.css")
css = css_path.read_text(encoding="utf-8")
css += """
/* Dashboard contest card: participant count sits inline with the title. */
.dashboard-list-panel .exam-card-heading {
  display:flex; align-items:center; justify-content:space-between; gap:10px; min-width:0; margin:13px 0 6px;
}
.dashboard-list-panel .exam-card-heading h3 { min-width:0; margin:0; flex:1; line-height:1.65; }
.exam-participant-count {
  flex:0 0 auto; display:inline-flex; align-items:center; gap:5px; min-height:29px; padding:5px 9px;
  border:1px solid rgba(139,112,245,.25); border-radius:999px; background:rgba(139,112,245,.08);
  color:var(--accent); font:inherit; font-size:10px; font-weight:850; cursor:pointer; direction:ltr;
  transition:transform .16s ease,background .16s ease,border-color .16s ease;
}
.exam-participant-count:hover { transform:translateY(-1px); background:rgba(139,112,245,.15); border-color:rgba(139,112,245,.45); }
.exam-participant-count span { opacity:.7; font-size:13px; }
.exam-participant-count:focus-visible,.registration-manage-link:focus-visible { outline:3px solid rgba(157,125,255,.65); outline-offset:3px; }
.registration-manage-link {
  display:inline-flex; align-items:center; gap:5px; padding:4px 0; border:0; background:transparent;
  color:#2eaa72; font:inherit; font-size:11px; font-weight:800; cursor:pointer;
}
.registration-manage-link:hover { color:#21865a; text-decoration:underline; }
.dashboard-registration-page { width:100%; max-width:860px; margin:0 auto; }
.dashboard-registration-nav { display:flex; justify-content:flex-start; margin-bottom:12px; }
.dashboard-registration-hero {
  display:flex; align-items:center; justify-content:space-between; gap:18px; padding:25px;
  border:1px solid rgba(143,119,242,.2); border-radius:22px;
  background:radial-gradient(circle at 85% 10%,rgba(147,115,255,.18),transparent 34%),var(--panel);
}
.dashboard-registration-copy h1 { margin:7px 0; font-size:clamp(23px,4vw,31px); }
.dashboard-registration-copy p { color:var(--muted); font-size:12px; line-height:1.8; }
.dashboard-registration-status {
  flex:0 0 auto; display:inline-flex; align-items:center; gap:7px; padding:9px 13px;
  border:1px solid rgba(46,170,114,.22); border-radius:999px; color:#259a66; background:rgba(46,170,114,.09);
  font-size:11px; font-weight:850;
}
.dashboard-registration-panel { margin-top:14px; padding:clamp(18px,3vw,28px); }
.dashboard-registration-contest { display:flex; align-items:center; gap:13px; padding-bottom:19px; border-bottom:1px solid var(--line); }
.dashboard-registration-icon { width:48px; height:48px; display:grid; place-items:center; border-radius:15px; background:rgba(139,112,245,.11); color:var(--accent); }
.dashboard-registration-contest > div:last-child { min-width:0; }
.dashboard-registration-contest span { color:var(--muted); font-size:10px; }
.dashboard-registration-contest h2 { margin:4px 0; font-size:17px; }
.dashboard-registration-contest small { display:flex; align-items:center; gap:5px; color:var(--muted); font-size:10px; }
.dashboard-registration-detail { display:flex; flex-wrap:wrap; gap:24px; padding:18px 0; }
.dashboard-registration-detail > div { display:flex; flex-direction:column; gap:6px; min-width:95px; }
.dashboard-registration-detail span { color:var(--muted); font-size:10px; }
.dashboard-registration-detail b { color:var(--text); font-size:12px; }
.dashboard-registration-detail .registration-state-active { color:#259a66; }
.dashboard-registration-note { display:flex; align-items:flex-start; gap:10px; padding:13px; border-radius:13px; background:rgba(139,112,245,.07); color:var(--accent); }
.dashboard-registration-note svg { flex:0 0 auto; margin-top:2px; }
.dashboard-registration-note p { color:var(--muted); font-size:11px; line-height:1.9; }
.dashboard-registration-warning,.dashboard-registration-error { margin-top:11px; padding:11px 13px; border-radius:11px; font-size:11px; line-height:1.8; }
.dashboard-registration-warning { border:1px solid rgba(222,164,63,.2); background:rgba(222,164,63,.08); color:#c38b30; }
.dashboard-registration-error { border:1px solid rgba(220,90,90,.22); background:rgba(220,90,90,.08); color:#cc5252; }
.dashboard-registration-actions { display:flex; align-items:center; justify-content:flex-end; gap:9px; margin-top:20px; }
.dashboard-unregister-button { border:1px solid rgba(220,90,90,.25)!important; color:#cf5555!important; }
.dashboard-unregister-button:disabled { opacity:.45; cursor:not-allowed; }
@media(max-width:600px) {
  .dashboard-registration-hero { align-items:flex-start; flex-direction:column; padding:19px; }
  .dashboard-registration-detail { gap:14px; }
  .dashboard-registration-actions { align-items:stretch; flex-direction:column-reverse; }
  .dashboard-registration-actions .button { width:100%; justify-content:center; }
  .dashboard-list-panel .exam-card-heading { gap:7px; }
  .exam-participant-count { padding:4px 7px; min-height:26px; }
}
"""
css_path.write_text(css, encoding="utf-8")
print("Added self-service unregistration management and inline participant counters.");
