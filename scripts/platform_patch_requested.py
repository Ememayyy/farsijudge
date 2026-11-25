from pathlib import Path

p = Path("src/App.tsx")
s = p.read_text(encoding="utf-8")

def once(a, b, label):
    global s
    n = s.count(a)
    if n != 1:
        raise SystemExit(label + ": expected one anchor, found " + str(n))
    s = s.replace(a, b, 1)

once(
"type TeamInvitation = { id: string; team_id: string; invited_by: string; created_at: string; teams?: { name: string } | null }",
"""type TeamInvitation = { id: string; team_id: string; invited_by: string; created_at: string; teams?: { name: string } | null }
type RegistrationMode = 'individual' | 'team'
type AdminControlValues = { examId: string; endAt: string; allowLate: boolean; registrationClosesAt: string; resultsReleaseAt: string; announcement: string; tags: string[] }
type ReviewRow = { question_number: number; points: number; submitted_answer: number | null; correct_answer: number | null; is_correct: boolean }""",
"new feature types"
)
once(
"  question_file_path?: string | null\n  created_at?: string",
"""  question_file_path?: string | null
  end_at_override?: string | null
  allow_late_registration?: boolean
  registration_closes_at?: string | null
  results_release_at?: string | null
  announcement?: string | null
  tags?: string[]
  created_at?: string""",
"exam control fields"
)
once("type Page = 'dashboard' | 'exam' | 'admin' | 'profile' | 'team'",
     "type Page = 'welcome' | 'auth' | 'dashboard' | 'registration' | 'exam' | 'admin' | 'profile' | 'team'",
     "page type")
once("const examEnd = (exam: Exam) => new Date(new Date(exam.starts_at).getTime() + exam.duration_minutes * 60_000)",
     "const examEnd = (exam: Exam) => new Date(exam.end_at_override || (new Date(exam.starts_at).getTime() + exam.duration_minutes * 60_000))",
     "effective contest end")
once("const [page, setPage] = useState<Page>('dashboard')",
     "const [page, setPage] = useState<Page>('welcome')",
     "initial welcome route")
once("  const [teamBusy, setTeamBusy] = useState(false)",
     "  const [teamBusy, setTeamBusy] = useState(false)\n  const [registerBusy, setRegisterBusy] = useState(false)",
     "registration busy state")
once(
"supabase.from('exams').select('id,title,description,starts_at,duration_minutes,is_published,created_at').order('starts_at', { ascending: false })",
"supabase.from('exams').select('id,title,description,starts_at,duration_minutes,is_published,question_pdf_url,question_file_path,end_at_override,allow_late_registration,registration_closes_at,results_release_at,announcement,tags,created_at').order('starts_at', { ascending: false })",
"load contest control fields"
)
once(
"""      if (alive) {
        setSession(data.session)
        setLoading(false)
      }""",
"""      if (alive) {
        setSession(data.session)
        if (data.session) setPage('dashboard')
        setLoading(false)
      }""",
"restore logged-in route"
)
once(
"""    const { data: authListener } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession)
      if (!nextSession) {
        setProfile(null)
        setExams([])
        setPage('dashboard')
      }
    })""",
"""    const { data: authListener } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession)
      if (nextSession) setPage('dashboard')
      if (!nextSession) {
        setProfile(null)
        setExams([])
        setPage('welcome')
      }
    })""",
"auth route listener"
)

const_old = """  const registerForExam = async (exam: Exam) => {
    if (!supabase) return
    if (team && team.role !== 'captain') return notify('برای ثبت‌نام تیمی، از کاپیتان تیم بخواهید اقدام کند.', 'info')
    const { error } = await supabase.rpc('register_for_exam', {
      p_exam_id: exam.id,
      p_team_id: team?.id ?? null,
    })
    if (error) notify('ثبت‌نام انجام نشد: ' + error.message, 'error')
    else {
      notify(team ? 'تیم با موفقیت در مسابقه ثبت‌نام شد.' : 'در مسابقه ثبت‌نام شدید.', 'success')
      await loadMainData()
    }
  }"""
const_new = """  const chooseRegistration = (exam: Exam) => {
    setSelectedExam(exam)
    setPage('registration')
  }

  const registerForExam = async (exam: Exam, mode: RegistrationMode) => {
    if (!supabase) return
    if (mode === 'team' && (!team || team.role !== 'captain')) return notify('ثبت‌نام تیمی فقط توسط کاپیتان تیم امکان‌پذیر است.', 'error')
    setRegisterBusy(true)
    const { error } = await supabase.rpc('register_for_exam', {
      p_exam_id: exam.id,
      p_team_id: mode === 'team' ? team!.id : null,
    })
    if (error) notify('ثبت‌نام انجام نشد: ' + error.message, 'error')
    else {
      notify(mode === 'team' ? 'تیم با موفقیت در مسابقه ثبت‌نام شد.' : 'ثبت‌نام انفرادی انجام شد.', 'success')
      await loadMainData()
      setPage('dashboard')
    }
    setRegisterBusy(false)
  }"""
once(const_old, const_new, "explicit registration mode handler")

once(
"  const createExam = async (event: FormEvent) => {",
"""  const saveContestControls = async (values: AdminControlValues) => {
    if (!supabase) return
    const { error } = await supabase.rpc('admin_update_contest_controls', {
      p_exam_id: values.examId,
      p_end_at_override: values.endAt ? new Date(values.endAt).toISOString() : null,
      p_allow_late_registration: values.allowLate,
      p_registration_closes_at: values.registrationClosesAt ? new Date(values.registrationClosesAt).toISOString() : null,
      p_results_release_at: values.resultsReleaseAt ? new Date(values.resultsReleaseAt).toISOString() : null,
      p_announcement: values.announcement.trim() || null,
      p_tags: values.tags,
    })
    if (error) {
      notify('ذخیره کنترل‌های مسابقه انجام نشد: ' + error.message, 'error')
      return
    }
    notify('کنترل‌های مسابقه و زمان انتشار کارنامه ذخیره شد.', 'success')
    await loadMainData()
  }

  const createExam = async (event: FormEvent) => {""",
"save live control handler"
)

once(
"  if (!isLoggedIn) {",
"""  if (!isLoggedIn && page === 'welcome') {
    return <WelcomePage
      theme={theme}
      onToggleTheme={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      onLogin={() => { setAuthMode('login'); setPage('auth') }}
      onRegister={() => { setAuthMode('register'); setPage('auth') }}
      onDemo={enterDemo}
      showDemo={!isSupabaseConfigured}
    />
  }

  if (!isLoggedIn) {""",
"welcome landing route"
)
once(
"""          </button>
          <span className="muted small">{authMode === 'login' ? 'حساب کاربری دارید؟' : 'قبلاً ثبت‌نام کرده‌اید؟'}</span>""",
"""          </button>
          <button className="welcome-back-link" onClick={() => setPage('welcome')}>صفحه اصلی</button>
          <span className="muted small">{authMode === 'login' ? 'حساب کاربری دارید؟' : 'قبلاً ثبت‌نام کرده‌اید؟'}</span>""",
"auth back to welcome"
)
once(
"""    setSelectedExam(null)
    setPage('dashboard')
  }

  const openExam""",
"""    setSelectedExam(null)
    setPage('welcome')
  }

  const openExam""",
"signout to welcome"
)

once("team={team} onRegister={registerForExam}",
     "team={team} onRegister={chooseRegistration}",
     "dashboard registration navigation")
once(
"""        {page === 'exam' && selectedExam && <ExamPage""",
"""        {page === 'registration' && selectedExam && <RegistrationPage
          exam={selectedExam} team={team} busy={registerBusy}
          onBack={() => setPage('dashboard')}
          onConfirm={(mode) => registerForExam(selectedExam, mode)}
        />}
        {page === 'exam' && selectedExam && <ExamPage""",
"registration page render"
)
once(
"onQuestionPdfUrl={setQuestionPdfUrl} onQuestionFile={setQuestionFile}",
"onQuestionPdfUrl={setQuestionPdfUrl} onQuestionFile={setQuestionFile} onSaveControls={saveContestControls}",
"admin controls callback prop"
)
once(
"""<b>{page === 'dashboard' ? 'داشبورد' : page === 'exam' ? 'صفحه مسابقه' : page === 'admin' ? 'مدیریت مسابقه‌ها' : page === 'team' ? 'تیم و دعوت‌ها' : 'پروفایل من'}</b>""",
"""<b>{page === 'dashboard' ? 'داشبورد' : page === 'registration' ? 'انتخاب نوع ثبت‌نام' : page === 'exam' ? 'صفحه مسابقه' : page === 'admin' ? 'مدیریت مسابقه‌ها' : page === 'team' ? 'تیم و دعوت‌ها' : 'پروفایل من'}</b>""",
"route breadcrumb"
)

once(
"function AdminPage({ title, description, start, duration, questions, busy, exams, results, profiles, onTitle, onDescription, onStart, onDuration, onQuestionChange, onCount, onSubmit, onBack, onEditExam, onDeleteExam, onTogglePublish, onSetRole, editingExamId, questionPdfUrl, questionFile, onQuestionPdfUrl, onQuestionFile }: {",
"function AdminPage({ title, description, start, duration, questions, busy, exams, results, profiles, onTitle, onDescription, onStart, onDuration, onQuestionChange, onCount, onSubmit, onBack, onEditExam, onDeleteExam, onTogglePublish, onSetRole, editingExamId, questionPdfUrl, questionFile, onQuestionPdfUrl, onQuestionFile, onSaveControls }: {",
"AdminPage live panel signature"
)
once(
"questionPdfUrl: string; questionFile: File | null; onQuestionPdfUrl: (v: string) => void; onQuestionFile: (v: File | null) => void",
"questionPdfUrl: string; questionFile: File | null; onQuestionPdfUrl: (v: string) => void; onQuestionFile: (v: File | null) => void\n  onSaveControls: (values: AdminControlValues) => Promise<void>",
"AdminPage live control callback type"
)
once(
"""    <div className="admin-layout">
      <section className="panel-card create-panel">""",
"""    <LiveControlPanel exams={exams} onSave={onSaveControls} />
    <div className="admin-layout">
      <section className="panel-card create-panel">""",
"add live controls panel"
)
once(
"""<div className="exam-heading-panel"><div><div className="eyebrow">مسابقه آنلاین</div><h1>{exam.title}</h1><p>{exam.description || 'پاسخ هر سؤال را به‌صورت عددی وارد کنید.'}</p></div><StatusBadge status={status} /></div>
    <div className="exam-info-grid">""",
"""<div className="exam-heading-panel"><div><div className="eyebrow">مسابقه آنلاین</div><h1>{exam.title}</h1><p>{exam.description || 'پاسخ هر سؤال را به‌صورت عددی وارد کنید.'}</p></div><StatusBadge status={status} /></div>
    {(exam.tags?.length || exam.announcement) && <div className="contest-meta-panel">
      {exam.tags && exam.tags.length > 0 && <div className="contest-topic-tags">{exam.tags.map((tag) => <span key={tag}>{tag}</span>)}</div>}
      {exam.announcement && <p>{exam.announcement}</p>}
    </div>}
    <div className="exam-info-grid">""",
"show live contest announcement and tags"
)
once(
"""    {demo && <div className="demo-note">این اطلاعات نمونه‌اند و در حالت نمایشی به دیتابیس ارسال نمی‌شوند.</div>}""",
"""    {ended && result && <ReviewPanel examId={exam.id} />}
    {demo && <div className="demo-note">این اطلاعات نمونه‌اند و در حالت نمایشی به دیتابیس ارسال نمی‌شوند.</div>}""",
"detail report on results"
)

welcome_and_registration = """function WelcomePage({ theme, onToggleTheme, onLogin, onRegister, onDemo, showDemo }: {
  theme: 'light' | 'dark'; onToggleTheme: () => void; onLogin: () => void
  onRegister: () => void; onDemo: () => void; showDemo: boolean
}) {
  return <div className="welcome-shell">
    <header className="welcome-header">
      <div className="welcome-brand"><span className="brand-mark"><GraduationCap size={25} /></span><b>فارسی جاج</b></div>
      <div className="welcome-header-actions">
        <button className="icon-button" onClick={onToggleTheme} aria-label="تغییر تم">{theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}</button>
        <button className="button soft small" onClick={onLogin}>ورود</button>
        <button className="button primary small" onClick={onRegister}>ثبت‌نام</button>
      </div>
    </header>
    <main className="welcome-main">
      <section className="welcome-hero">
        <div className="welcome-copy">
          <div className="eyebrow">سامانهٔ برگزاری مسابقه‌های آنلاین</div>
          <h1>برای رقابت آماده‌ای؟<span> جای حل مسئله همین‌جاست.</span></h1>
          <p>فارسی جاج محیطی متمرکز برای شرکت در مسابقه‌های علمی و برنامه‌نویسی است؛ با زمان‌بندی روشن، پاسخ‌گویی ساده و کارنامهٔ دقیق.</p>
          <div className="welcome-cta">
            <button className="button primary" onClick={onRegister}>ساخت حساب و شروع <ArrowLeft size={17} /></button>
            <button className="button soft" onClick={onLogin}>قبلاً حساب ساخته‌ام</button>
          </div>
          {showDemo && <button className="welcome-demo-link" onClick={onDemo}>مشاهدهٔ پیش‌نمایش سامانه</button>}
        </div>
        <div className="welcome-visual">
          <div className="welcome-orbit orbit-one" /><div className="welcome-orbit orbit-two" />
          <div className="welcome-score-card">
            <div className="welcome-score-top"><span className="welcome-live-dot" />محیط مسابقه</div>
            <div className="welcome-score-icon"><GraduationCap size={34} /></div>
            <b>تمرکز روی حل مسئله</b>
            <span>از ثبت‌نام تا مشاهدهٔ کارنامه</span>
            <div className="welcome-mini-stats"><div><Clock3 size={16} /><b>زمان‌بندی‌شده</b></div><div><ShieldCheck size={16} /><b>نتیجهٔ دقیق</b></div></div>
          </div>
        </div>
      </section>
      <section className="welcome-features">
        <article><span><Clock3 size={19} /></span><b>زمان‌بندی شفاف</b><p>زمان شروع و پایان هر مسابقه مشخص است.</p></article>
        <article><span><Users size={19} /></span><b>ثبت‌نام منعطف</b><p>امکان شرکت انفرادی یا در قالب تیم.</p></article>
        <article><span><Award size={19} /></span><b>کارنامهٔ دقیق</b><p>امتیاز و جزئیات پاسخ‌ها پس از انتشار.</p></article>
      </section>
    </main>
    <footer className="welcome-footer"><span>فارسی جاج</span><span>محیطی برای رقابت و یادگیری</span></footer>
  </div>
}

function RegistrationPage({ exam, team, busy, onBack, onConfirm }: {
  exam: Exam; team: Team | null; busy: boolean; onBack: () => void; onConfirm: (mode: RegistrationMode) => void
}) {
  const [mode, setMode] = useState<RegistrationMode>(team?.role === 'captain' ? 'team' : 'individual')
  const canRegisterTeam = team?.role === 'captain'
  return <>
    <div className="backline"><button className="back-button" onClick={onBack}><ArrowLeft size={17} />بازگشت به مسابقه‌ها</button></div>
    <div className="registration-page-head"><div className="eyebrow">مرحلهٔ ثبت‌نام</div><h1>چطور می‌خواهید شرکت کنید؟</h1><p>برای مسابقهٔ «{exam.title}» نوع ثبت‌نام را انتخاب کنید. این انتخاب فقط برای همین مسابقه است.</p></div>
    <div className="registration-options">
      <button type="button" className={mode === 'individual' ? 'selected' : ''} onClick={() => setMode('individual')}>
        <span className="registration-option-icon"><UserRound size={22} /></span><b>ثبت‌نام انفرادی</b><small>با حساب شخصی خودتان در مسابقه شرکت می‌کنید.</small>
        <span className="registration-radio">{mode === 'individual' ? 'انتخاب شده' : 'انتخاب'}</span>
      </button>
      <button type="button" className={mode === 'team' ? 'selected' : ''} disabled={!canRegisterTeam} onClick={() => setMode('team')}>
        <span className="registration-option-icon"><Users size={22} /></span><b>ثبت‌نام تیمی</b>
        <small>{!team ? 'برای این گزینه ابتدا باید عضو یک تیم شوید.' : team.role !== 'captain' ? 'ثبت‌نام تیمی را فقط کاپیتان تیم می‌تواند انجام دهد.' : 'همهٔ اعضای تیم با یک ثبت‌نام مشترک شرکت می‌کنند.'}</small>
        <span className="registration-radio">{mode === 'team' ? 'انتخاب شده' : canRegisterTeam ? 'انتخاب' : 'غیرفعال'}</span>
      </button>
    </div>
    <div className="registration-confirm-row">
      <span>{mode === 'team' ? 'ثبت‌نام برای تیم «' + (team?.name || '') + '» انجام می‌شود.' : 'ثبت‌نام فقط برای حساب خودتان انجام می‌شود.'}</span>
      <button className="button primary" disabled={busy || (mode === 'team' && !canRegisterTeam)} onClick={() => onConfirm(mode)}>{busy ? 'در حال ثبت‌نام...' : 'تأیید و ثبت‌نام'}<ArrowLeft size={17} /></button>
    </div>
  </>
}

"""
anchor = "function Dashboard({"
if s.count(anchor) != 1:
    raise SystemExit("Welcome and registration insertion point mismatch")
s = s.replace(anchor, welcome_and_registration + anchor, 1)

controls_and_review = """function LiveControlPanel({ exams, onSave }: { exams: Exam[]; onSave: (values: AdminControlValues) => Promise<void> }) {
  const [examId, setExamId] = useState(exams[0]?.id || '')
  const selected = exams.find((exam) => exam.id === examId) || exams[0]
  const toLocal = (value: string | Date) => {
    const date = value instanceof Date ? value : new Date(value)
    if (!Number.isFinite(date.getTime())) return ''
    return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16)
  }
  const [endAt, setEndAt] = useState('')
  const [allowLate, setAllowLate] = useState(false)
  const [registrationClosesAt, setRegistrationClosesAt] = useState('')
  const [resultsReleaseAt, setResultsReleaseAt] = useState('')
  const [announcement, setAnnouncement] = useState('')
  const [tagsText, setTagsText] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (!selected) return
    setExamId(selected.id)
    setEndAt(toLocal(examEnd(selected)))
    setAllowLate(Boolean(selected.allow_late_registration))
    setRegistrationClosesAt(selected.registration_closes_at ? toLocal(selected.registration_closes_at) : '')
    setResultsReleaseAt(selected.results_release_at ? toLocal(selected.results_release_at) : '')
    setAnnouncement(selected.announcement || '')
    setTagsText((selected.tags || []).join(', '))
  }, [selected?.id, selected?.end_at_override, selected?.allow_late_registration, selected?.registration_closes_at, selected?.results_release_at, selected?.announcement, selected?.tags])

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (!selected) return
    setBusy(true)
    await onSave({
      examId: selected.id,
      endAt,
      allowLate,
      registrationClosesAt,
      resultsReleaseAt,
      announcement,
      tags: tagsText.split(',').map((tag) => tag.trim()).filter(Boolean),
    })
    setBusy(false)
  }

  return <section className="panel-card live-controls-panel">
    <div className="panel-title"><div><div className="eyebrow">کنترل عملیاتی</div><h2>کنترل زندهٔ مسابقه و انتشار کارنامه</h2><p>زمان پایان، ثبت‌نام دیرهنگام و زمان نمایش نتایج را مدیریت کنید.</p></div><span className="private-chip"><ShieldCheck size={14} />ویژهٔ مدیر</span></div>
    {exams.length === 0 ? <div className="mini-empty">برای تنظیم کنترل‌ها ابتدا یک مسابقه بسازید.</div> : <form className="live-controls-form" onSubmit={submit}>
      <label className="field-label">مسابقهٔ موردنظر<select value={selected?.id || ''} onChange={(event) => setExamId(event.target.value)}>{exams.map((exam) => <option key={exam.id} value={exam.id}>{exam.title}</option>)}</select></label>
      <div className="live-controls-grid">
        <label className="field-label">زمان پایان جدید<input type="datetime-local" value={endAt} onChange={(event) => setEndAt(event.target.value)} required /><small>مبنای وضعیت فعال یا پایان‌یافتهٔ مسابقه است.</small></label>
        <label className="field-label">آخرین مهلت ثبت‌نام<input type="datetime-local" value={registrationClosesAt} onChange={(event) => setRegistrationClosesAt(event.target.value)} /><small>خالی باشد، محدودیت جداگانه‌ای تعیین نمی‌شود.</small></label>
        <label className="field-label">زمان انتشار کارنامه<input type="datetime-local" value={resultsReleaseAt} onChange={(event) => setResultsReleaseAt(event.target.value)} /><small>خالی باشد، کارنامه پس از پایان مسابقه قابل مشاهده می‌شود.</small></label>
        <label className="field-label">اعلان برای شرکت‌کنندگان<textarea value={announcement} onChange={(event) => setAnnouncement(event.target.value)} rows={2} maxLength={500} placeholder="اطلاعیه یا توضیح مهم مسابقه" /></label>
      </div>
      <label className="live-toggle"><input type="checkbox" checked={allowLate} onChange={(event) => setAllowLate(event.target.checked)} /><span><b>فعال‌کردن ثبت‌نام دیرهنگام</b><small>در صورت فعال بودن، ثبت‌نام تا مهلت بالا امکان‌پذیر می‌شود.</small></span></label>
      <label className="field-label">برچسب‌های موضوعی <input value={tagsText} onChange={(event) => setTagsText(event.target.value)} placeholder="مثلاً الگوریتم، ترکیبیات، ریاضی" /><small>برچسب‌ها را با ویرگول جدا کنید.</small></label>
      <div className="live-controls-actions"><span>تغییرات برای همهٔ شرکت‌کنندگان اعمال می‌شود.</span><button className="button primary" type="submit" disabled={busy}>{busy ? 'در حال ذخیره...' : 'ذخیرهٔ کنترل‌ها'}<CheckCircle2 size={16} /></button></div>
    </form>}
  </section>
}

function ReviewPanel({ examId }: { examId: string }) {
  const [open, setOpen] = useState(false)
  const [busy, setBusy] = useState(false)
  const [loaded, setLoaded] = useState(false)
  const [rows, setRows] = useState<ReviewRow[]>([])
  const [error, setError] = useState('')
  const load = async () => {
    if (!supabase) { setError('گزارش جزئی در حالت پیش‌نمایش در دسترس نیست.'); setLoaded(true); return }
    setBusy(true)
    setError('')
    const { data, error: reviewError } = await supabase.rpc('get_exam_review', { p_exam_id: examId })
    if (reviewError) setError(reviewError.message)
    else setRows((data || []) as ReviewRow[])
    setLoaded(true)
    setBusy(false)
  }
  const toggle = () => {
    if (open) { setOpen(false); return }
    setOpen(true)
    if (!loaded) void load()
  }
  return <section className="panel-card review-panel">
    <div className="review-panel-heading"><div><b>گزارش جزئی پاسخ‌ها</b><p>پاسخ ثبت‌شده، پاسخ صحیح و نمرهٔ هر سؤال</p></div><button className="button soft small" onClick={toggle}>{open ? 'بستن گزارش' : 'مشاهدهٔ ریز پاسخ‌ها'}<ChevronLeft size={15} /></button></div>
    {open && <>
      {busy && <div className="mini-empty">در حال دریافت گزارش...</div>}
      {error && <div className="notice error">{error}</div>}
      {!busy && !error && rows.length > 0 && <div className="review-list">{rows.map((row) => <div className={'review-row ' + (row.is_correct ? 'correct' : 'wrong')} key={row.question_number}>
        <b>سؤال {fa(row.question_number)}</b>
        <span>پاسخ شما: <strong>{row.submitted_answer === null ? 'ثبت نشده' : fa(row.submitted_answer)}</strong></span>
        <span>پاسخ صحیح: <strong>{row.correct_answer === null ? '—' : fa(row.correct_answer)}</strong></span>
        <strong>{row.is_correct ? 'درست' : 'نادرست'} · {fa(row.points)} نمره</strong>
      </div>)}</div>}
      {!busy && !error && rows.length === 0 && loaded && <div className="mini-empty">برای این مسابقه گزارشی ثبت نشده است.</div>}
    </>}
  </section>
}

"""
anchor = "function ProfilePage("
if s.count(anchor) != 1:
    raise SystemExit("Live control/report insertion point mismatch")
s = s.replace(anchor, controls_and_review + anchor, 1)

p.write_text(s, encoding="utf-8")

cssp = Path("src/style.css")
css = cssp.read_text(encoding="utf-8")
css += """

/* Requested Welcome, registration, live controls and detailed review */
.welcome-shell { min-height:100vh; background:var(--bg); color:var(--text); }
.welcome-header { max-width:1180px; margin:auto; padding:22px 28px; display:flex; align-items:center; justify-content:space-between; gap:16px; }
.welcome-brand { display:flex; align-items:center; gap:10px; font-size:17px; }
.welcome-header-actions { display:flex; align-items:center; gap:9px; }
.welcome-main { max-width:1180px; margin:auto; padding:52px 28px 30px; }
.welcome-hero { display:grid; grid-template-columns:1.1fr .9fr; align-items:center; gap:44px; min-height:420px; }
.welcome-copy h1 { margin:15px 0; font-size:clamp(34px,5vw,58px); line-height:1.45; letter-spacing:-1.4px; }
.welcome-copy h1 span { display:block; color:#9a75ff; }
.welcome-copy>p { max-width:620px; color:var(--muted); font-size:15px; line-height:2.1; }
.welcome-cta { display:flex; flex-wrap:wrap; gap:10px; margin-top:26px; }
.welcome-demo-link { margin-top:15px; border:0; background:transparent; color:#a98cff; cursor:pointer; font:inherit; }
.welcome-visual { min-height:350px; display:grid; place-items:center; position:relative; overflow:hidden; }
.welcome-orbit { position:absolute; border:1px solid rgba(150,112,255,.24); border-radius:50%; transform:rotate(-24deg); }
.orbit-one { width:390px; height:270px; }
.orbit-two { width:310px; height:390px; transform:rotate(34deg); }
.welcome-score-card { z-index:1; width:min(340px,90%); padding:27px; border:1px solid var(--line); border-radius:22px; background:var(--panel); box-shadow:0 24px 80px rgba(0,0,0,.22); display:flex; flex-direction:column; gap:12px; }
.welcome-score-top { display:flex; align-items:center; gap:8px; color:var(--muted); font-size:11px; }
.welcome-live-dot { width:8px; height:8px; border-radius:50%; background:#22b88a; box-shadow:0 0 14px #22b88a; }
.welcome-score-icon { width:65px; height:65px; display:grid; place-items:center; border-radius:18px; background:rgba(145,105,255,.14); color:#a987ff; margin:12px 0; }
.welcome-score-card>b { font-size:19px; }
.welcome-score-card>span { color:var(--muted); font-size:12px; }
.welcome-mini-stats { display:flex; gap:10px; margin-top:14px; }
.welcome-mini-stats div { flex:1; padding:12px 9px; border-radius:11px; background:var(--panel-2); display:flex; align-items:center; gap:7px; color:#a987ff; }
.welcome-mini-stats b { color:var(--text); font-size:10px; }
.welcome-features { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; margin-top:38px; }
.welcome-features article { padding:20px; border:1px solid var(--line); background:var(--panel); border-radius:15px; }
.welcome-features article>span { width:38px; height:38px; border-radius:11px; display:grid; place-items:center; color:#a987ff; background:rgba(145,105,255,.12); }
.welcome-features b { display:block; margin-top:13px; }
.welcome-features p { color:var(--muted); font-size:12px; line-height:1.9; margin:7px 0 0; }
.welcome-footer { max-width:1180px; margin:auto; padding:20px 28px 28px; border-top:1px solid var(--line); color:var(--muted); display:flex; justify-content:space-between; font-size:11px; }
.welcome-back-link { border:0; background:transparent; color:var(--accent); cursor:pointer; font:inherit; font-size:12px; }
.registration-page-head { margin:25px 0 20px; }
.registration-page-head h1 { margin:8px 0; font-size:28px; }
.registration-page-head p { color:var(--muted); font-size:13px; line-height:1.9; }
.registration-options { margin:25px 0; }
.registration-options button { position:relative; display:flex; flex-direction:column; align-items:flex-start; gap:9px; cursor:pointer; }
.registration-options button b { font-size:16px; }
.registration-options button small { color:var(--muted); font-size:12px; line-height:1.8; }
.registration-option-icon { width:42px; height:42px; border-radius:12px; display:grid; place-items:center; background:rgba(145,105,255,.12); color:#a987ff; }
.registration-radio { margin-top:5px; color:#a987ff; font-size:11px; }
.registration-confirm-row { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:14px; margin:18px 0; padding:16px; border:1px solid var(--line); border-radius:12px; background:var(--panel); }
.registration-confirm-row>span { color:var(--muted); font-size:12px; }
.live-controls-panel { margin:18px 0 22px; padding:22px; }
.live-controls-form { display:flex; flex-direction:column; gap:16px; margin-top:18px; }
.live-controls-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; }
.live-controls-grid .field-label small,.live-controls-form .field-label small { display:block; color:var(--muted); font-size:10px; margin-top:5px; }
.live-toggle { display:flex; align-items:flex-start; gap:11px; padding:14px; border:1px solid var(--line); border-radius:11px; background:var(--panel-2); cursor:pointer; }
.live-toggle input { margin-top:4px; accent-color:#956eff; }
.live-toggle span { display:flex; flex-direction:column; gap:5px; }
.live-toggle b { font-size:12px; }
.live-toggle small { color:var(--muted); font-size:10px; }
.live-controls-actions { display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; }
.live-controls-actions>span { color:var(--muted); font-size:11px; }
.review-panel { margin-top:18px; padding:20px; }
.review-panel-heading { display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; }
.review-panel-heading p { margin:5px 0 0; color:var(--muted); font-size:11px; }
.review-list { display:flex; flex-direction:column; gap:9px; margin-top:16px; }
.review-row { grid-template-columns:.7fr 1fr 1fr auto; font-size:12px; }
.review-row span { color:var(--muted); }
.review-row strong { color:var(--text); }
.contest-meta-panel { display:flex; flex-direction:column; gap:8px; margin:12px 0; }
.contest-meta-panel>p { padding:12px 14px; border-radius:10px; border:1px solid var(--line); background:var(--panel); color:var(--text); font-size:12px; line-height:1.9; margin:0; }
@media(max-width:760px) {
 .welcome-main { padding:28px 18px 22px; }
 .welcome-header { padding:16px 18px; }
 .welcome-hero { grid-template-columns:1fr; gap:5px; }
 .welcome-visual { min-height:280px; }
 .welcome-features { grid-template-columns:1fr; }
 .welcome-footer { padding:18px; }
 .live-controls-grid { grid-template-columns:1fr; }
 .registration-confirm-row { align-items:stretch; }
 .registration-confirm-row .button { width:100%; }
 .review-row { grid-template-columns:1fr 1fr; }
}
"""
cssp.write_text(css, encoding="utf-8")
print("Requested UI features applied.")
