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
  