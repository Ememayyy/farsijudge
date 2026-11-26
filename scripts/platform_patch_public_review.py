from pathlib import Path

p = Path("src/App.tsx")
s = p.read_text(encoding="utf-8")

def once(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(label + ": expected one anchor, got " + str(n))
    s = s.replace(old, new, 1)

# Shared row type for the public leaderboard.
page_line = "type Page = 'dashboard' | 'exam' | 'admin' | 'profile' | 'team' | 'leaderboard' | 'public-questions'"
if "type LeaderboardRow =" not in s:
    if page_line not in s:
        raise SystemExit("Page type anchor missing")
    s = s.replace(
        page_line,
        "type LeaderboardRow = { position: number; display_name: string; team_name: string | null; score: number; max_score: number; correct_count: number; wrong_count: number; question_count: number; is_team: boolean }\n" + page_line,
        1
    )

# --- Public landing page ---
# WelcomePage is rendered inside the root shell. Keep review state local so it
# works without an account and does not depend on authenticated page routing.
welcome_anchor = """  const publicExams = exams.filter((exam) => exam.is_published).sort((a, b) => new Date(a.starts_at).getTime() - new Date(b.starts_at).getTime())
  const nextContest = publicExams.find((exam) => getStatus(exam, now) === 'upcoming')
  const runningCount = publicExams.filter((exam) => getStatus(exam, now) === 'active').length
  return <div className="public-site">"""
welcome_new = """  const publicExams = exams.filter((exam) => exam.is_published).sort((a, b) => new Date(a.starts_at).getTime() - new Date(b.starts_at).getTime())
  const runningCount = publicExams.filter((exam) => getStatus(exam, now) === 'active').length
  const upcomingCount = publicExams.filter((exam) => getStatus(exam, now) === 'upcoming').length
  const endedCount = publicExams.filter((exam) => getStatus(exam, now) === 'ended').length
  const [reviewExam, setReviewExam] = useState<Exam | null>(null)
  const [leaderboardExam, setLeaderboardExam] = useState<Exam | null>(null)
  if (leaderboardExam) return <PublicLeaderboardPage exam={leaderboardExam} onBack={() => setLeaderboardExam(null)} />
  if (reviewExam) return <PublicQuestionPage exam={reviewExam} onBack={() => setReviewExam(null)} onLeaderboard={() => setLeaderboardExam(reviewExam)} />
  return <div className="public-site">"""
once(welcome_anchor, welcome_new, "public landing review state")

# Ended contests offer public question review and public leaderboard links.
once(
    """<td><button className="public-row-action" onClick={onLogin}>جزئیات <ChevronLeft size={14} /></button></td>""",
    """<td className="public-row-actions">
                    {getStatus(exam, now) === 'ended'
                      ? <><button className="public-row-action" onClick={() => setReviewExam(exam)}>صورت سؤال <FileUp size={14} /></button><button className="public-row-action" onClick={() => setLeaderboardExam(exam)}>امتیازات <Trophy size={14} /></button></>
                      : <button className="public-row-action" onClick={onLogin}>جزئیات <ChevronLeft size={14} /></button>}
                  </td>""",
    "public contest ended actions"
)

# Use reliable state counts rather than the old next-contest date summary.
once(
    """            <div className="public-stat-foot"><span>مسابقه‌های منتشرشده</span><strong>{fa(publicExams.length)}</strong></div>
            <div className="public-stat-foot"><span>مسابقهٔ پیش‌رو</span><strong>{nextContest ? dateText(nextContest.starts_at) : 'به‌زودی'}</strong></div>""",
    """            <div className="public-stat-foot"><span>کل مسابقه‌ها</span><strong>{fa(publicExams.length)}</strong></div>
            <div className="public-stat-foot"><span>پیش‌رو</span><strong>{fa(upcomingCount)}</strong></div>
            <div className="public-stat-foot"><span>در حال برگزاری</span><strong>{fa(runningCount)}</strong></div>
            <div className="public-stat-foot"><span>پایان‌یافته</span><strong>{fa(endedCount)}</strong></div>""",
    "public landing status summary"
)

# --- Per-user dashboard leaderboard ---
# The redesigned Dashboard already owns filter/search state. Add the
# leaderboard selector after those hooks and show the table in-place.
dashboard_search = "  const [search, setSearch] = useState('')"
once(
    dashboard_search,
    dashboard_search + "\n  const [leaderboardExam, setLeaderboardExam] = useState<Exam | null>(null)",
    "dashboard leaderboard state"
)
dashboard_first_name = "  const firstName = profile?.full_name?.trim().split(/\\s+/)[0] || 'خوش آمدید'"
once(
    dashboard_first_name,
    dashboard_first_name + "\n  if (leaderboardExam) return <PublicLeaderboardPage exam={leaderboardExam} onBack={() => setLeaderboardExam(null)} />",
    "dashboard leaderboard view"
)

# Add a public leaderboard control to ended cards, keeping active/upcoming
# interactions unchanged.
exam_card_signature = "function ExamCard({ exam, now, onOpen, registered, teamMember, teamCaptain, onRegister }: {"
once(
    exam_card_signature,
    "function ExamCard({ exam, now, onOpen, registered, teamMember, teamCaptain, onRegister, onLeaderboard }: {",
    "exam card leaderboard callback"
)
once(
    "  teamMember: boolean; teamCaptain: boolean; onRegister: () => void\n}) {",
    "  teamMember: boolean; teamCaptain: boolean; onRegister: () => void; onLeaderboard: () => void\n}) {",
    "exam card leaderboard callback type"
)
once(
    """      <button className={'button ' + (active && registered ? 'primary' : 'soft')} disabled={active && !registered} onClick={onOpen}>
        {active ? registered ? 'ورود به آزمون' : 'ثبت‌نام لازم است' : ended ? 'مشاهده نتیجه' : 'جزئیات آزمون'}<ChevronLeft size={16} />
      </button>""",
    """      <button className={'button ' + (active && registered ? 'primary' : 'soft')} disabled={active && !registered} onClick={onOpen}>
        {active ? registered ? 'ورود به آزمون' : 'ثبت‌نام لازم است' : ended ? 'مشاهده سؤال‌ها و نتیجه' : 'جزئیات مسابقه'}<ChevronLeft size={16} />
      </button>
      {ended && <button className="button soft small leaderboard-card-link" onClick={onLeaderboard}><Trophy size={14} />جدول امتیازات</button>}""",
    "ended contest card leaderboard button"
)
once(
    "teamCaptain={team?.role === 'captain'} onRegister={() => onRegister(exam)} />",
    "teamCaptain={team?.role === 'captain'} onRegister={() => onRegister(exam)} onLeaderboard={() => setLeaderboardExam(exam)} />",
    "dashboard card leaderboard callback"
)

# --- Public review components ---
components = r'''
function PublicLeaderboardPage({ exam, onBack }: { exam: Exam; onBack: () => void }) {
  const [rows, setRows] = useState<LeaderboardRow[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  useEffect(() => {
    const client = supabase
    let alive = true
    const load = async () => {
      if (!client) {
        setError('اتصال به سامانه در دسترس نیست.')
        setLoading(false)
        return
      }
      const { data, error: queryError } = await client.rpc('get_public_exam_leaderboard', { p_exam_id: exam.id })
      if (!alive) return
      if (queryError) setError(queryError.message)
      else setRows((data || []) as LeaderboardRow[])
      setLoading(false)
    }
    void load()
    return () => { alive = false }
  }, [exam.id])
  return <section className="leaderboard-page">
    <div className="backline"><button className="back-button" onClick={onBack}><ArrowLeft size={16} />بازگشت</button></div>
    <div className="leaderboard-hero"><div className="eyebrow">CONTEST LEADERBOARD</div><h1>جدول امتیازات</h1><p>{exam.title}</p></div>
    <div className="panel-card leaderboard-panel">
      {loading ? <div className="mini-empty">در حال دریافت جدول امتیازات...</div>
        : error ? <div className="mini-empty">{error}</div>
        : rows.length === 0 ? <div className="mini-empty">هنوز نتیجه‌ای برای این مسابقه ثبت نشده است.</div>
        : <div className="leaderboard-table-wrap"><table className="leaderboard-table">
          <thead><tr><th>رتبه</th><th>شرکت‌کننده</th><th>نوع</th><th>نمره</th><th>درست</th><th>غلط</th></tr></thead>
          <tbody>{rows.map((row) => <tr key={(row.team_name || row.display_name) + '-' + row.position}>
            <td><b className="leaderboard-rank">{fa(row.position)}</b></td>
            <td><b>{row.display_name}</b></td>
            <td>{row.is_team ? 'تیمی' : 'انفرادی'}</td>
            <td><strong>{fa(row.score)}</strong><small> / {fa(row.max_score)}</small></td>
            <td className="leaderboard-correct">{fa(row.correct_count)}</td>
            <td className="leaderboard-wrong">{fa(row.wrong_count)}</td>
          </tr>)}</tbody>
        </table></div>}
    </div>
  </section>
}

function PublicQuestionPage({ exam, onBack, onLeaderboard }: {
  exam: Exam; onBack: () => void; onLeaderboard: () => void
}) {
  const [paperUrl, setPaperUrl] = useState('')
  const [questionRows, setQuestionRows] = useState<{ question_number: number; points: number }[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  useEffect(() => {
    const client = supabase
    let alive = true
    const load = async () => {
      if (!client) {
        setLoading(false)
        setError('اتصال به سامانه در دسترس نیست.')
        return
      }
      const [questions, resource] = await Promise.all([
        client.rpc('get_public_exam_questions', { p_exam_id: exam.id }),
        client.rpc('get_public_exam_question_resource', { p_exam_id: exam.id }),
      ])
      if (!alive) return
      if (questions.error) setError(questions.error.message)
      else setQuestionRows(questions.data || [])
      if (resource.error) setError((current) => current || resource.error.message)
      const item = Array.isArray(resource.data) ? resource.data[0] : resource.data
      let url = item?.question_pdf_url || ''
      if (item?.question_file_path) {
        const { data, error: signedError } = await client.storage
          .from('exam-question-files').createSignedUrl(item.question_file_path, 3600)
        if (!signedError && data?.signedUrl) url = data.signedUrl
        else if (!url && signedError) setError((current) => current || signedError.message)
      }
      if (!alive) return
      setPaperUrl(url)
      setLoading(false)
    }
    void load()
    return () => { alive = false }
  }, [exam.id])
  return <div className="public-site">
    <header className="public-header">
      <a href="#public-top" className="public-brand"><span className="public-brand-mark"><img src={import.meta.env.BASE_URL + 'fj-logo.svg'} alt="FJ" /></span><span>فارسی جاج</span></a>
      <div className="public-actions">
        <button className="button soft small" onClick={onBack}><ArrowLeft size={15} />بازگشت</button>
        <button className="button primary small" onClick={onLeaderboard}><Trophy size={15} />جدول امتیازات</button>
      </div>
    </header>
    <main className="public-main public-question-page">
      <div className="eyebrow">CONTEST REVIEW</div><h1>{exam.title}</h1><p>صورت سؤال مسابقه پس از پایان برای همه قابل مشاهده است.</p>
      {loading ? <div className="panel-card mini-empty">در حال بارگذاری صورت سؤال...</div> :
        <section className="panel-card public-question-panel">
          {paperUrl
            ? <><div className="public-question-actions"><a href={paperUrl} target="_blank" rel="noreferrer">باز کردن یا دانلود فایل PDF <ExternalLink size={14} /></a></div><iframe src={paperUrl} title={'صورت سؤال ' + exam.title} loading="lazy" /></>
            : <div className="public-empty"><FileUp size={25} /><b>فایل صورت سؤال برای این مسابقه ثبت نشده است.</b><span>{error || 'از برگزارکننده بخواهید فایل PDF را اضافه کند.'}</span></div>}
          {questionRows.length > 0 && <div className="public-question-counts">
            <b>{fa(questionRows.length)} سؤال</b>
            <span>مجموع نمره: {fa(questionRows.reduce((sum, row) => sum + Number(row.points || 0), 0))}</span>
            {questionRows.map((row) => <span key={row.question_number}>سؤال {fa(row.question_number)} · {fa(row.points)} نمره</span>)}
          </div>}
        </section>}
      {error && <p className="public-resource-error">{error}</p>}
    </main>
  </div>
}
'''
if s.count("function ProfilePage(") != 1:
    raise SystemExit("ProfilePage insertion point mismatch")
s = s.replace("function ProfilePage(", components + "\nfunction ProfilePage(", 1)

p.write_text(s, encoding="utf-8")

cssp = Path("src/style.css")
css = cssp.read_text(encoding="utf-8")
css += """
@media (max-width: 900px) { .redesign-shell .mobile-appbar > .icon-button { display:none !important; } }
.leaderboard-page { width:100%; max-width:1100px; margin:0 auto; }
.leaderboard-hero { padding:22px; border:1px solid var(--line); border-radius:18px; background:linear-gradient(110deg,rgba(143,105,255,.12),var(--panel)); }
.leaderboard-hero h1 { margin:6px 0; font-size:26px; }
.leaderboard-hero p { margin:0; color:var(--muted); font-size:12px; }
.leaderboard-panel { margin-top:14px; overflow:hidden; }
.leaderboard-table-wrap { width:100%; overflow-x:auto; }
.leaderboard-table { width:100%; border-collapse:collapse; min-width:600px; }
.leaderboard-table th,.leaderboard-table td { padding:13px 12px; border-bottom:1px solid var(--line); text-align:right; font-size:12px; }
.leaderboard-table th { color:var(--muted); background:var(--panel-2); font-size:10px; }
.leaderboard-table tr:last-child td { border-bottom:0; }
.leaderboard-rank { color:var(--accent); }
.leaderboard-correct { color:#1ca878; font-weight:800; }
.leaderboard-wrong { color:#d36a73; font-weight:800; }
.leaderboard-table td small { color:var(--muted); font-size:10px; }
.leaderboard-card-link { margin-inline-start:auto; }
.public-question-page > h1 { margin:7px 0; }
.public-question-page > p { color:var(--muted); font-size:12px; }
.public-question-panel { margin-top:16px; padding:15px; }
.public-question-panel iframe { width:100%; min-height:75vh; border:1px solid var(--line); border-radius:10px; background:#fff; }
.public-question-actions { display:flex; justify-content:flex-end; margin-bottom:10px; }
.public-question-actions a { color:var(--accent); display:inline-flex; gap:7px; align-items:center; font-size:11px; text-decoration:none; }
.public-question-counts { display:flex; flex-wrap:wrap; gap:8px 14px; margin-top:13px; color:var(--muted); font-size:10px; }
.public-question-counts b { color:var(--text); }
.public-resource-error { color:#d36a73; font-size:11px; }
.public-row-actions { display:flex; align-items:center; gap:10px; }
.public-row-actions .public-row-action { white-space:nowrap; }
@media(max-width:640px) {
  .public-question-panel iframe { min-height:60vh; }
  .public-row-actions { flex-wrap:wrap; gap:5px; }
}
"""
cssp.write_text(css, encoding="utf-8")
print("Added public post-contest questions, public leaderboards and mobile theme cleanup.")
