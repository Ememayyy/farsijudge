from pathlib import Path

app_path = Path('src/App.tsx')
source = app_path.read_text(encoding='utf-8')
css_path = Path('src/style.css')
css = css_path.read_text(encoding='utf-8')

def replace_once(old: str, new: str, label: str) -> None:
    global source
    count = source.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    source = source.replace(old, new, 1)

def replace_css_once(old: str, new: str, label: str) -> None:
    global css
    count = css.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one CSS match, found {count}')
    css = css.replace(old, new, 1)

# Shared contest metadata and review rows.
replace_once(
"""  Sun, UserRound, Users, XCircle, UserPlus, Pencil, Trash2, FileUp, ExternalLink,
""",
"""  Sun, UserRound, Users, XCircle, UserPlus, Pencil, Trash2, FileUp, ExternalLink,
  Menu, X, Zap, Trophy, CalendarDays, ArrowRight, Tag, BarChart3,
""",
'icons'
)
replace_once(
"""  created_at?: string
}
type Question = { id: string; exam_id: string; question_number: number; points: number }
""",
"""  created_at?: string
  tags?: string[]
  results_release_at?: string | null
  allow_late_registration?: boolean
  registration_closes_at?: string | null
  end_at_override?: string | null
  announcement?: string | null
}
type Question = { id: string; exam_id: string; question_number: number; points: number }
type ExamReviewRow = { question_number: number; points: number; submitted_answer: number | null; correct_answer: number; is_correct: boolean }
""",
'exam metadata and review types'
)
replace_once(
"""type Page = 'dashboard' | 'exam' | 'admin' | 'profile' | 'team'

 type AdminQuestion""".replace("\n\n type", "\n\ntype"),
"""type Page = 'dashboard' | 'exam' | 'admin' | 'profile' | 'team' | 'registration'

 type AdminQuestion""".replace("\n\n type", "\n\ntype"),
'page type'
)
# route state + welcome-first auth
replace_once(
"""  const [page, setPage] = useState<Page>('dashboard')
""",
"""  const [page, setPage] = useState<Page>(() => {
    const requested = new URLSearchParams(window.location.search).get('page')
    return requested === 'admin' || requested === 'team' || requested === 'profile' ? requested : 'dashboard'
  })
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [registrationMode, setRegistrationMode] = useState<'individual' | 'team'>('individual')
  const [examReview, setExamReview] = useState<ExamReviewRow[]>([])
""",
'page routing state'
)
replace_once(
"""  const [authMode, setAuthMode] = useState<'login' | 'register'>('login')
""",
"""  const [authMode, setAuthMode] = useState<'welcome' | 'login' | 'register'>('welcome')
""",
'welcome first auth state'
)
replace_once(
"""  const [adminBusy, setAdminBusy] = useState(false)
""",
"""  const [adminBusy, setAdminBusy] = useState(false)
  const [adminTags, setAdminTags] = useState<string[]>([])
  const [adminResultsReleaseAt, setAdminResultsReleaseAt] = useState('')
  const [adminAllowLateRegistration, setAdminAllowLateRegistration] = useState(false)
  const [adminRegistrationClosesAt, setAdminRegistrationClosesAt] = useState('')
  const [adminEndAtOverride, setAdminEndAtOverride] = useState('')
  const [adminAnnouncement, setAdminAnnouncement] = useState('')
""",
'admin contest control state'
)
replace_once(
"""  const selectedStatus = selectedExam ? getStatus(selectedExam, now) : null

  useEffect(() => {
""",
"""  const selectedStatus = selectedExam ? getStatus(selectedExam, now) : null
  const startCountdownSeconds = selectedExam && selectedStatus === 'upcoming'
    ? Math.max(0, Math.ceil((new Date(selectedExam.starts_at).getTime() - now) / 1000)) : 0
  const navigate = useCallback((next: Page) => {
    const url = new URL(window.location.href)
    if (next === 'dashboard') url.searchParams.delete('page')
    else url.searchParams.set('page', next)
    window.history.pushState({ page: next }, '', url)
    setPage(next)
    setMobileMenuOpen(false)
  }, [])

  useEffect(() => {
    const syncRoute = () => {
      const requested = new URLSearchParams(window.location.search).get('page')
      if (requested === 'admin' || requested === 'team' || requested === 'profile') setPage(requested)
      else if ((requested === 'exam' || requested === 'registration') && selectedExam) setPage(requested)
      else setPage('dashboard')
      setMobileMenuOpen(false)
    }
    window.addEventListener('popstate', syncRoute)
    return () => window.removeEventListener('popstate', syncRoute)
  }, [selectedExam?.id])

  useEffect(() => {
    if (!session?.user.id || !supabase) return
    let alive = true
    void supabase.rpc('activate_my_single_session').then(({ error }) => {
      if (!alive || !error) return
      setNotice({ type: 'error', text: 'این نشست نتوانست به‌عنوان دستگاه فعال ثبت شود. دوباره وارد شوید: ' + error.message })
      void supabase.auth.signOut()
    })
    return () => { alive = false }
  }, [session?.user.id])

  useEffect(() => {
""",
'navigation and single-session activation'
)
# Make end time respect live override and load all contest metadata.
replace_once(
"""const examEnd = (exam: Exam) => new Date(new Date(exam.starts_at).getTime() + exam.duration_minutes * 60_000)
""",
"""const examEnd = (exam: Exam) => new Date(exam.end_at_override || (new Date(new Date(exam.starts_at).getTime() + exam.duration_minutes * 60_000)).toISOString())
""",
'live end time helper'
)
replace_once(
"""supabase.from('exams').select('id,title,description,starts_at,duration_minutes,is_published,created_at').order('starts_at', { ascending: false }),""",
"""supabase.from('exams').select('id,title,description,starts_at,duration_minutes,is_published,created_at,tags,results_release_at,allow_late_registration,registration_closes_at,end_at_override,announcement').order('starts_at', { ascending: false }),""",
'load contest controls'
)
# Review retrieval after finalization and after contest closes.
replace_once(
"""        if (alive && resultRes.data) setExamResult(resultRes.data as ExamResult)
""",
"""        if (alive && resultRes.data) {
          setExamResult(resultRes.data as ExamResult)
          const { data: reviewRows } = await client.rpc('get_exam_review', { p_exam_id: selectedExam.id })
          if (alive && reviewRows) setExamReview(reviewRows as ExamReviewRow[])
        }
""",
'load question review after result'
)
replace_once(
"""      if (resultResponse.data) setExamResult(resultResponse.data as ExamResult)
""",
"""      if (resultResponse.data) {
        setExamResult(resultResponse.data as ExamResult)
        const { data: reviewRows } = await client.rpc('get_exam_review', { p_exam_id: selectedExam.id })
        if (reviewRows) setExamReview(reviewRows as ExamReviewRow[])
      }
""",
'load review from expiry finalizer'
)
# Subscribe to live database events and keep polling as fallback.
replace_once(
"""    void refreshSharedAnswers()
    const timer = window.setInterval(() => { void refreshSharedAnswers() }, 2500)
    return () => { alive = false; window.clearInterval(timer) }
""",
"""    void refreshSharedAnswers()
    const channel = client.channel('team-answers-' + selectedExam.id + '-' + team.id)
      .on('postgres_changes', { event: '*', schema: 'public', table: 'exam_answers', filter: 'exam_id=eq.' + selectedExam.id }, () => {
        void refreshSharedAnswers()
      }).subscribe()
    const timer = window.setInterval(() => { void refreshSharedAnswers() }, 2500)
    return () => { alive = false; window.clearInterval(timer); void client.removeChannel(channel) }
""",
'realtime team answer subscription'
)
# Registration is a page; preserve the chosen mode and enforce captain role in the UI.
replace_once(
"""  const registerForExam = async (exam: Exam) => {
    if (!supabase) return
    if (team && team.role !== 'captain') return notify('برای ثبت‌نام تیمی، از کاپیتان تیم بخواهید اقدام کند.', 'info')
    const { error } = await supabase.rpc('register_for_exam', {
      p_exam_id: exam.id,
      p_team_id: team?.id ?? null,
    })
""",
"""  const openRegistration = (exam: Exam) => {
    setSelectedExam(exam)
    setRegistrationMode(team && team.role === 'captain' ? 'team' : 'individual')
    navigate('registration')
  }

  const registerForExam = async (exam: Exam, mode: 'individual' | 'team') => {
    if (!supabase) return
    if (mode === 'team' && (!team || team.role !== 'captain')) return notify('ثبت‌نام تیمی فقط توسط کاپیتان امکان‌پذیر است.', 'error')
    const { error } = await supabase.rpc('register_for_exam', {
      p_exam_id: exam.id,
      p_team_id: mode === 'team' ? team!.id : null,
    })
""",
'registration handler'
)
replace_once(
"""      notify(team ? 'تیم با موفقیت در مسابقه ثبت‌نام شد.' : 'در مسابقه ثبت‌نام شدید.', 'success')
      await loadMainData()
""",
"""      notify(mode === 'team' ? 'تیم با موفقیت در مسابقه ثبت‌نام شد.' : 'در مسابقه ثبت‌نام شدید.', 'success')
      navigate('dashboard')
      await loadMainData()
""",
'registration confirmation'
)
# Team leave and admin user deletion.
needle = """  const respondToInvitation = async (id: string, accept: boolean) => {
"""
insert = """  const leaveTeam = async () => {
    if (!supabase || !window.confirm('از تیم خارج شوید؟ اگر کاپیتان باشید، مسئولیت به قدیمی‌ترین عضو منتقل می‌شود.')) return
    const { error } = await supabase.rpc('leave_team')
    if (error) notify('خروج از تیم انجام نشد: ' + error.message, 'error')
    else { notify('از تیم خارج شدید.', 'success'); await loadMainData() }
  }

  const deleteUser = async (userId: string, fullName: string) => {
    if (!supabase || !window.confirm('حساب «' + fullName + '» و اطلاعات وابسته حذف شود؟ این کار قابل بازگشت نیست.')) return
    const { error } = await supabase.rpc('admin_delete_user', { p_user_id: userId })
    if (error) notify('حذف کاربر انجام نشد: ' + error.message, 'error')
    else {
      notify('حساب کاربر حذف شد.', 'success')
      setProfiles((current) => current.filter((p) => p.id !== userId))
      await loadMainData()
    }
  }

"""
replace_once(needle, insert + needle, 'team leave and user deletion handlers')
# Edit-load contest metadata.
replace_once(
"""    setQuestionPdfUrl(resource?.question_pdf_url || '')
    setQuestionFilePath(resource?.question_file_path || null)
""",
"""    setQuestionPdfUrl(resource?.question_pdf_url || '')
    setAdminTags(exam.tags || [])
    setAdminResultsReleaseAt(exam.results_release_at ? new Date(new Date(exam.results_release_at).getTime() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16) : '')
    setAdminAllowLateRegistration(Boolean(exam.allow_late_registration))
    setAdminRegistrationClosesAt(exam.registration_closes_at ? new Date(new Date(exam.registration_closes_at).getTime() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16) : '')
    setAdminEndAtOverride(exam.end_at_override ? new Date(new Date(exam.end_at_override).getTime() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16) : '')
    setAdminAnnouncement(exam.announcement || '')
    setQuestionFilePath(resource?.question_file_path || null)
""",
'load contest metadata for editing'
)
# create/edit transaction: update live controls through the security-definer RPC.
replace_once(
"""    if (!failed) {
      setAdminTitle('')
""",
"""    if (!failed && examId) {
      const controlsResponse = await supabase.rpc('admin_update_contest_controls', {
        p_exam_id: examId,
        p_end_at_override: adminEndAtOverride ? new Date(adminEndAtOverride).toISOString() : null,
        p_allow_late_registration: adminAllowLateRegistration,
        p_registration_closes_at: adminRegistrationClosesAt ? new Date(adminRegistrationClosesAt).toISOString() : null,
        p_results_release_at: adminResultsReleaseAt ? new Date(adminResultsReleaseAt).toISOString() : null,
        p_announcement: adminAnnouncement.trim() || null,
        p_tags: adminTags,
      })
      if (controlsResponse.error) {
        notify('مسابقه ذخیره شد اما تنظیمات تکمیلی اعمال نشد: ' + controlsResponse.error.message, 'error')
        failed = true
      }
    }

    if (!failed) {
      setAdminTitle('')
""",
'apply contest controls'
)
replace_once(
"""      setQuestionPdfUrl('')
      setQuestionFile(null)
""",
"""      setQuestionPdfUrl('')
      setAdminTags([])
      setAdminResultsReleaseAt('')
      setAdminAllowLateRegistration(false)
      setAdminRegistrationClosesAt('')
      setAdminEndAtOverride('')
      setAdminAnnouncement('')
      setQuestionFile(null)
""",
'clear contest controls'
)
# Team leave page and badges, mobile nav, route links.
replace_once(
"""        <button className={page === 'team' ? 'nav-item selected' : 'nav-item'} onClick={() => setPage('team')}><Users size={19} />تیم و دعوت‌ها</button>
""",
"""        <button className={page === 'team' ? 'nav-item selected' : 'nav-item'} onClick={() => navigate('team')}><Users size={19} />تیم و دعوت‌ها{teamInvitations.length > 0 && <span className="nav-badge">{fa(teamInvitations.length)}</span>}</button>
""",
'invitation badge'
)
# Convert remaining page changes to history-aware navigation.
for page_name in ['dashboard', 'exam', 'admin', 'profile', 'team']:
    source = source.replace(f"setPage('{page_name}')", f"navigate('{page_name}')")
# restore state setter occurrences accidentally changed in route sync and navigate internals
source = source.replace("window.history.pushState({ page: next }, '', url)\n    navigate(next)", "window.history.pushState({ page: next }, '', url)\n    setPage(next)")
source = source.replace("if (requested === 'admin' || requested === 'team' || requested === 'profile') navigate(requested)", "if (requested === 'admin' || requested === 'team' || requested === 'profile') setPage(requested)")
source = source.replace("else if ((requested === 'exam' || requested === 'registration') && selectedExam) navigate(requested)", "else if ((requested === 'exam' || requested === 'registration') && selectedExam) setPage(requested)")
source = source.replace("else navigate('dashboard')", "else setPage('dashboard')")
# openExam should reset detailed result state.
replace_once(
"""    setExamResult(null)
    setAnswerDirty(false)
""",
"""    setExamResult(null)
    setExamReview([])
    setAnswerDirty(false)
""",
'clear question review on opening exam'
)
# After sign out return to the public landing page.
replace_once(
"""    setSelectedExam(null)
    navigate('dashboard')
  }
""",
"""    setSelectedExam(null)
    setAuthMode('welcome')
    navigate('dashboard')
  }
""",
'return to welcome on logout'
)
# Public welcome screen before auth form rendering.
replace_once(
"""  if (!isLoggedIn) {
    return <div className="auth-shell">
""",
"""  if (!isLoggedIn && authMode === 'welcome') return <WelcomePage
    theme={theme} onToggleTheme={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
    onLogin={() => setAuthMode('login')} onRegister={() => setAuthMode('register')}
  />

  if (!isLoggedIn) {
    return <div className="auth-shell">
""",
'welcome landing page branch'
)
replace_once(
"""        <div className="auth-panel-top">
          <button className="icon-button" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} aria-label="تغییر تم">
""",
"""        <div className="auth-panel-top">
          <button className="button soft small" type="button" onClick={() => setAuthMode('welcome')}><ArrowRight size={15} /> صفحه اصلی</button>
          <button className="icon-button" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} aria-label="تغییر تم">
""",
'auth back to welcome'
)
# Mobile menu button and sidebar overlay.
replace_once(
"""  return <div className="app-shell">
    <aside className="sidebar">
""",
"""  return <div className="app-shell">
    {mobileMenuOpen && <button className="mobile-nav-backdrop" aria-label="بستن منو" onClick={() => setMobileMenuOpen(false)} />}
    <aside className={mobileMenuOpen ? 'sidebar mobile-open' : 'sidebar'}>
""",
'mobile sidebar state'
)
replace_once(
"""      <header className=\"topbar\">
        <div className=\"breadcrumb\"><span className=\"topbar-brand\">""",
"""      <header className=\"topbar\">
        <button className=\"mobile-menu-toggle\" aria-label=\"باز کردن منو\" onClick={() => setMobileMenuOpen(true)}><Menu size={20} /></button>
        <div className=\"breadcrumb\"><span className=\"topbar-brand\">""",
'mobile menu button'
)
# registration route, more detailed exam results, and pass new props.
replace_once(
"""        {page === 'exam' && selectedExam && <ExamPage
""",
"""        {page === 'registration' && selectedExam && <RegistrationPage
          exam={selectedExam} team={team} selected={registrationMode}
          onSelect={setRegistrationMode} onBack={() => navigate('dashboard')}
          onConfirm={() => void registerForExam(selectedExam, registrationMode)}
          alreadyRegistered={myRegistrations.includes(selectedExam.id) || myTeamRegistrations.includes(selectedExam.id)}
        />}
        {page === 'exam' && selectedExam && <ExamPage
""",
'registration route component'
)
replace_once(
"""          totalPoints={questionScore} questionResourceUrl={questionResourceUrl} teamMode={Boolean(team && myTeamRegistrations.includes(selectedExam.id))}
""",
"""          totalPoints={questionScore} questionResourceUrl={questionResourceUrl} teamMode={Boolean(team && myTeamRegistrations.includes(selectedExam.id))}
          startCountdownSeconds={startCountdownSeconds} reviewRows={examReview}
""",
'exam countdown and review props'
)
replace_once(
"""          onSetRole={changeUserRole} editingExamId={editingExamId}
          questionPdfUrl={questionPdfUrl} questionFile={questionFile}
          onQuestionPdfUrl={setQuestionPdfUrl} onQuestionFile={setQuestionFile}
""",
"""          onSetRole={changeUserRole} onDeleteUser={deleteUser} editingExamId={editingExamId}
          questionPdfUrl={questionPdfUrl} questionFile={questionFile}
          onQuestionPdfUrl={setQuestionPdfUrl} onQuestionFile={setQuestionFile}
          tags={adminTags} onTags={setAdminTags} resultsReleaseAt={adminResultsReleaseAt} onResultsReleaseAt={setAdminResultsReleaseAt}
          allowLateRegistration={adminAllowLateRegistration} onAllowLateRegistration={setAdminAllowLateRegistration}
          registrationClosesAt={adminRegistrationClosesAt} onRegistrationClosesAt={setAdminRegistrationClosesAt}
          endAtOverride={adminEndAtOverride} onEndAtOverride={setAdminEndAtOverride}
          announcement={adminAnnouncement} onAnnouncement={setAdminAnnouncement}
""",
'admin controls props'
)
replace_once(
"""          onCreate={createTeam} onInvite={inviteToTeam} onRespond={respondToInvitation} />}
""",
"""          onCreate={createTeam} onInvite={inviteToTeam} onRespond={respondToInvitation} onLeave={leaveTeam} />}
""",
'leave team prop'
)
# Dashboard routes to registration instead of direct database mutation; nearest contest priority.
replace_once(
"""          team={team} onRegister={registerForExam}
""",
"""          team={team} onRegister={openRegistration}
""",
'dashboard registration route callback'
)
# Extend child component props and implementations.
replace_once(
"""function ExamPage({ exam, questions, answers, remainingSeconds, status, result, saving, demo, onAnswer, onBack, totalPoints, questionResourceUrl, teamMode }: {
""",
"""function ExamPage({ exam, questions, answers, remainingSeconds, status, result, saving, demo, onAnswer, onBack, totalPoints, questionResourceUrl, teamMode, startCountdownSeconds, reviewRows }: {
""",
'exam page props signature'
)
replace_once(
"""  questionResourceUrl: string; teamMode: boolean
}) {
  const progress = questions.length ? Object.values(answers).filter((v) => v.trim() && validNumber(v)).length : 0
""",
"""  questionResourceUrl: string; teamMode: boolean; startCountdownSeconds: number; reviewRows: ExamReviewRow[]
}) {
  const progress = questions.length ? Object.values(answers).filter((v) => v.trim() && validNumber(v)).length : 0
  const [paperExpanded, setPaperExpanded] = useState(false)
""",
'exam page countdown and preview state'
)
replace_once(
"""    {questionResourceUrl && <a className=\"question-paper-link\" href={questionResourceUrl} target=\"_blank\" rel=\"noreferrer\"><ExternalLink size={17} />دانلود / مشاهده فایل صورت سؤال</a>}
""",
"""    {questionResourceUrl && <section className=\"paper-preview\">
      <div className=\"paper-preview-head\"><div><b>صورت سؤال مسابقه</b><small>نمایش مستقیم در همین صفحه</small></div><div className=\"paper-preview-actions\"><button className=\"button soft small\" onClick={() => setPaperExpanded((v) => !v)}>{paperExpanded ? 'بستن پیش‌نمایش' : 'نمایش PDF'}</button><a className=\"button secondary small\" href={questionResourceUrl} target=\"_blank\" rel=\"noreferrer\"><ExternalLink size={15} />بازکردن در صفحه جدید</a></div></div>
      {paperExpanded && <iframe src={questionResourceUrl + '#view=FitH'} title=\"صورت سؤال مسابقه\" loading=\"lazy\" />}
    </section>}
""",
'embedded question pdf preview'
)
replace_once(
"""    {status === 'upcoming' && <div className=\"waiting-panel\"><div className=\"waiting-icon\"><Clock3 size={24} /></div><h2>مسابقه هنوز شروع نشده است</h2><p>شروع مسابقه برای زمان زیر برنامه‌ریزی شده است:</p><strong>{dateText(exam.starts_at)}</strong><span>صفحه را باز نگه دارید یا بعداً دوباره مراجعه کنید.</span></div>}
""",
"""    {status === 'upcoming' && <div className=\"waiting-panel\"><div className=\"waiting-icon\"><Clock3 size={24} /></div><div className=\"eyebrow\">شمارش معکوس شروع</div><h2>مسابقه هنوز شروع نشده است</h2><strong className=\"start-countdown\" dir=\"ltr\">{durationText(startCountdownSeconds)}</strong><p>شروع مسابقه: {dateText(exam.starts_at)}</p><span>صفحه به‌صورت خودکار با رسیدن زمان شروع به‌روزرسانی می‌شود.</span></div>}
""",
'prestart countdown'
)
replace_once(
"""    {ended && <div className=\"result-panel\"><div className=\"result-icon\"><Award size={29} /></div><div className=\"eyebrow\">مسابقه به پایان رسید</div><h2>{result ? 'نتیجه شما آماده است' : 'در حال تصحیح پاسخ‌ها'}</h2>{result ? <><div className=\"score-big\"><strong>{fa(result.score)}</strong><span>از {fa(result.max_score)} نمره</span></div><div className=\"result-stats\"><div><b>{fa(result.correct_count)}</b><span>پاسخ صحیح</span></div><div><b>{fa(Math.max(0, result.question_count - result.correct_count))}</b><span>پاسخ نادرست یا خالی</span></div><div><b>{fa(result.question_count)}</b><span>تعداد سؤال</span></div></div><p className=\"result-note\">تصحیح بر اساس برابری دقیق عددی انجام شده است.</p></> : <p>برای این مسابقه تلاشی ثبت نشده یا نتیجه هنوز آماده نیست. صفحه را کمی بعد به‌روزرسانی کنید.</p>}</div>}
""",
"""    {ended && <div className=\"result-panel\"><div className=\"result-icon\"><Award size={29} /></div><div className=\"eyebrow\">مسابقه به پایان رسید</div><h2>{result ? 'کارنامه شما آماده است' : 'در انتظار انتشار کارنامه'}</h2>{result ? <><div className=\"score-big\"><strong>{fa(result.score)}</strong><span>از {fa(result.max_score)} نمره</span></div><div className=\"result-percentage\">{fa(result.max_score ? Math.round(result.score / result.max_score * 1000) / 10 : 0)}٪ امتیاز کسب‌شده</div><div className=\"result-stats\"><div><b>{fa(result.correct_count)}</b><span>پاسخ صحیح</span></div><div><b>{fa(Math.max(0, result.question_count - result.correct_count))}</b><span>غلط یا بدون پاسخ</span></div><div><b>{fa(result.question_count)}</b><span>تعداد سؤال</span></div></div><p className=\"result-note\">تصحیح بر اساس برابری دقیق عددی انجام شده است.</p>
      {reviewRows.length > 0 && <section className=\"review-section\"><div className=\"section-heading\"><div><h2>بررسی سؤال‌به‌سؤال</h2><p>پاسخ ثبت‌شده، پاسخ صحیح و نمرهٔ هر سؤال</p></div></div><div className=\"review-list\">{reviewRows.map((row) => <article className={row.is_correct ? 'review-row correct' : 'review-row wrong'} key={row.question_number}><b>سؤال {fa(row.question_number)}</b><div><small>پاسخ شما</small><strong>{row.submitted_answer === null ? 'بدون پاسخ' : fa(row.submitted_answer)}</strong></div><div><small>پاسخ صحیح</small><strong>{fa(row.correct_answer)}</strong></div><span className=\"review-status\">{row.is_correct ? 'درست' : 'نادرست'} · {fa(row.points)} نمره</span></article>)}</div></section>}
      </> : <p>کارنامه هنوز منتشر نشده است. زمان انتشار را در جزئیات مسابقه بررسی کنید.</p>}</div>}
""",
'detailed score report'
)
# Admin component props: edit controls and user removal.
replace_once(
"""function AdminPage({ title, description, start, duration, questions, busy, exams, results, profiles, onTitle, onDescription, onStart, onDuration, onQuestionChange, onCount, onSubmit, onBack, onEditExam, onDeleteExam, onTogglePublish, onSetRole, editingExamId, questionPdfUrl, questionFile, onQuestionPdfUrl, onQuestionFile }: {
""",
"""function AdminPage({ title, description, start, duration, questions, busy, exams, results, profiles, onTitle, onDescription, onStart, onDuration, onQuestionChange, onCount, onSubmit, onBack, onEditExam, onDeleteExam, onTogglePublish, onSetRole, onDeleteUser, editingExamId, questionPdfUrl, questionFile, onQuestionPdfUrl, onQuestionFile, tags, onTags, resultsReleaseAt, onResultsReleaseAt, allowLateRegistration, onAllowLateRegistration, registrationClosesAt, onRegistrationClosesAt, endAtOverride, onEndAtOverride, announcement, onAnnouncement }: {
""",
'AdminPage signature'
)
replace_once(
"""  onSetRole: (userId: string, role: 'participant' | 'admin') => void
  editingExamId: string | null
""",
"""  onSetRole: (userId: string, role: 'participant' | 'admin') => void
  onDeleteUser: (userId: string, fullName: string) => void
  editingExamId: string | null
""",
'admin delete type'
)
replace_once(
"""  onQuestionPdfUrl: (value: string) => void; onQuestionFile: (file: File | null) => void; onCancelEdit: () => void
}) {
""",
"""  onQuestionPdfUrl: (value: string) => void; onQuestionFile: (file: File | null) => void; onCancelEdit: () => void
  tags: string[]; onTags: (value: string[]) => void; resultsReleaseAt: string; onResultsReleaseAt: (value: string) => void
  allowLateRegistration: boolean; onAllowLateRegistration: (value: boolean) => void; registrationClosesAt: string; onRegistrationClosesAt: (value: string) => void
  endAtOverride: string; onEndAtOverride: (value: string) => void; announcement: string; onAnnouncement: (value: string) => void
}) {
""",
'admin controls type'
)
# user list includes deletion button.
replace_once(
"""<button className=\"button soft small\" onClick={() => onSetRole(profile.id, profile.role === 'admin' ? 'participant' : 'admin')}>{profile.role === 'admin' ? 'حذف مدیریت' : 'ارتقای نقش'}</button>""",
"""<div className=\"admin-user-actions\"><button className=\"button soft small\" onClick={() => onSetRole(profile.id, profile.role === 'admin' ? 'participant' : 'admin')}>{profile.role === 'admin' ? 'حذف مدیریت' : 'ارتقای نقش'}</button><button className=\"button danger small\" onClick={() => onDeleteUser(profile.id, profile.full_name)}><Trash2 size={14} />حذف کاربر</button></div>""",
'user delete button'
)
# Advanced controls in admin form.
replace_once(
"""          <label className=\"field-label\">لینک مستقیم PDF صورت سؤال <input type=\"url\" value={questionPdfUrl} onChange={(e) => onQuestionPdfUrl(e.target.value)} placeholder=\"https://example.com/questions.pdf\" dir=\"ltr\" /></label>
""",
"""          <label className=\"field-label\">لینک مستقیم PDF صورت سؤال <input type=\"url\" value={questionPdfUrl} onChange={(e) => onQuestionPdfUrl(e.target.value)} placeholder=\"https://example.com/questions.pdf\" dir=\"ltr\" /></label>
          <section className=\"admin-extra-settings\"><h3>تنظیمات پیشرفته مسابقه</h3>
            <label className=\"field-label\">انتشار کارنامه <input type=\"datetime-local\" value={resultsReleaseAt} onChange={(e) => onResultsReleaseAt(e.target.value)} /></label>
            <label className=\"toggle-row\"><input type=\"checkbox\" checked={allowLateRegistration} onChange={(e) => onAllowLateRegistration(e.target.checked)} /> اجازه ثبت‌نام پس از شروع مسابقه</label>
            <label className=\"field-label\">بستن ثبت‌نام دیرهنگام در <input type=\"datetime-local\" value={registrationClosesAt} onChange={(e) => onRegistrationClosesAt(e.target.value)} /></label>
            <label className=\"field-label\">زمان پایان جدید (اختیاری) <input type=\"datetime-local\" value={endAtOverride} onChange={(e) => onEndAtOverride(e.target.value)} /></label>
            <label className=\"field-label\">اطلاعیه زنده <textarea rows={2} value={announcement} onChange={(e) => onAnnouncement(e.target.value)} /></label>
            <div><b>تگ‌های موضوعی</b><div className=\"admin-tag-picker\">{['ترکیبیات','گراف','الگوریتم','هندسه','جبر','نظریه اعداد','احتمالات','ساختمان داده'].map((tag) => <button type=\"button\" key={tag} data-tag={tag} className={tags.includes(tag) ? 'selected' : ''} onClick={() => onTags(tags.includes(tag) ? tags.filter((x) => x !== tag) : [...tags, tag])}>{tag}</button>)}</div></div>
          </section>
""",
'admin advanced controls'
)
# Team page leave action.
replace_once(
"""function TeamPage({ team, members, invitations, busy, onCreate, onInvite, onRespond }: {
""",
"""function TeamPage({ team, members, invitations, busy, onCreate, onInvite, onRespond, onLeave }: {
""",
'team leave props signature'
)
replace_once(
"""  onCreate: (event: FormEvent) => void; onInvite: (event: FormEvent) => void; onRespond: (id: string, accept: boolean) => void
}) {
""",
"""  onCreate: (event: FormEvent) => void; onInvite: (event: FormEvent) => void; onRespond: (id: string, accept: boolean) => void; onLeave: () => void
}) {
""",
'team leave props type'
)
replace_once(
"""      {team.role === 'captain' && <form className=\"team-invite-form\"""",
"""      <div className=\"team-actions\"><span>{team.role === 'captain' ? 'کاپیتان تیم' : 'عضو تیم'}</span><button className=\"button danger small\" type=\"button\" onClick={onLeave}>ترک تیم</button></div>
      {team.role === 'captain' && <form className=\"team-invite-form\"""",
'team leave button'
)
