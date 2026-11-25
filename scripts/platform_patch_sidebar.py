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
