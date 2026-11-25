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
