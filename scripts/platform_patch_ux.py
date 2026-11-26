#!/usr/bin/env python3
"""FarsiJudge UX, routing, contest tags and page-resilience fixes."""
from pathlib import Path
import re

app_path = Path("src/App.tsx")
css_path = Path("src/style.css")
s = app_path.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8")

def once(old: str, new: str, label: str) -> None:
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    s = s.replace(old, new, 1)

# 1) Do not navigate away from an active screen on TOKEN_REFRESHED / focus.
once(
"""    const { data: authListener } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession)
      if (nextSession) setPage('dashboard')
      if (!nextSession) {
        setProfile(null)
        setExams([])
        setPage('welcome')
      }
    })""",
"""    const { data: authListener } = supabase.auth.onAuthStateChange((event, nextSession) => {
      setSession(nextSession)
      if (event === 'SIGNED_IN' && nextSession) setPage((current) => current === 'auth' ? 'dashboard' : current)
      if (event === 'SIGNED_OUT' || !nextSession) {
        setProfile(null)
        setExams([])
        setSelectedExam(null)
        setSelectedPublicExam(null)
        setPage('welcome')
      }
    })""",
"navigate after sign-in only from auth screen"
)

# Global public-review route state belongs to App, not to the Dashboard card component.
once(
"const [sidebarOpen, setSidebarOpen] = useState(false)",
"const [sidebarOpen, setSidebarOpen] = useState(false)\n  const [selectedPublicExam, setSelectedPublicExam] = useState<Exam | null>(null)",
"global public review state"
)

# Remove page-local review state and early returns from WelcomePage and Dashboard.
welcome_state = """  const [reviewExam, setReviewExam] = useState<Exam | null>(null)
  const [leaderboardExam, setLeaderboardExam] = useState<Exam | null>(null)
  if (leaderboardExam) return <PublicLeaderboardPage exam={leaderboardExam} onBack={() => setLeaderboardExam(null)} />
  if (reviewExam) return <PublicQuestionPage exam={reviewExam} onBack={() => setReviewExam(null)} onLeaderboard={() => setLeaderboardExam(reviewExam)} />
"""
if s.count(welcome_state) != 1:
    raise SystemExit("WelcomePage local review route block mismatch")
s = s.replace(welcome_state, "", 1)

dashboard_state = """  const [leaderboardExam, setLeaderboardExam] = useState<Exam | null>(null)
  const [reviewExam, setReviewExam] = useState<Exam | null>(null)
"""
if s.count(dashboard_state) != 1:
    raise SystemExit("Dashboard local review state block mismatch")
s = s.replace(dashboard_state, "", 1)

dashboard_routes = """  if (leaderboardExam) return <PublicLeaderboardPage exam={leaderboardExam} onBack={() => setLeaderboardExam(null)} />
  if (reviewExam) return <PublicQuestionPage exam={reviewExam} onBack={() => setReviewExam(null)} onLeaderboard={() => setLeaderboardExam(reviewExam)} />
"""
if s.count(dashboard_routes) != 1:
    raise SystemExit("Dashboard local review route block mismatch")
s = s.replace(dashboard_routes, "", 1)

# Welcome page and dashboard receive navigation callbacks from the App router.
once(
"function WelcomePage({ theme, onToggleTheme, onLogin, onRegister, onDemo, showDemo, exams, now }: {",
"function WelcomePage({ theme, onToggleTheme, onLogin, onRegister, onDemo, showDemo, exams, now, onReviewQuestions, onLeaderboard }: {",
"public page callbacks"
)
once(
"theme: 'light' | 'dark'; onToggleTheme: () => void; onLogin: () => void\n  onRegister: () => void; onDemo: () => void; showDemo: boolean; exams: Exam[]; now: number",
"theme: 'light' | 'dark'; onToggleTheme: () => void; onLogin: () => void\n  onRegister: () => void; onDemo: () => void; showDemo: boolean; exams: Exam[]; now: number\n  onReviewQuestions: (exam: Exam) => void; onLeaderboard: (exam: Exam) => void",
"public page callback types"
)
once(
"onClick={() => setReviewExam(exam)}",
"onClick={() => onReviewQuestions(exam)}",
"public question action callback"
)
once(
"onClick={() => setLeaderboardExam(exam)}",
"onClick={() => onLeaderboard(exam)}",
"public leaderboard action callback"
)

once(
"function Dashboard({ exams, profile, now, onOpen, onAdmin, isAdmin, isDemo, myRegistrations, myTeamRegistrations, team, onRegister }: {",
"function Dashboard({ exams, profile, now, onOpen, onAdmin, isAdmin, isDemo, myRegistrations, myTeamRegistrations, team, onRegister, onReviewQuestions, onLeaderboard }: {",
"dashboard review callbacks"
)
once(
"myRegistrations: string[]; myTeamRegistrations: string[]; team: Team | null; onRegister: (exam: Exam) => void",
"myRegistrations: string[]; myTeamRegistrations: string[]; team: Team | null; onRegister: (exam: Exam) => void\n  onReviewQuestions: (exam: Exam) => void; onLeaderboard: (exam: Exam) => void",
"dashboard callback types"
)
once(
'onReviewQuestions={() => setReviewExam(exam)} onLeaderboard={() => setLeaderboardExam(exam)}',
'onReviewQuestions={() => onReviewQuestions(exam)} onLeaderboard={() => onLeaderboard(exam)}',
"dashboard card callbacks"
)
once(
"""      showDemo={!isSupabaseConfigured}
      exams={exams}
      now={now}
    />""",
"""      showDemo={!isSupabaseConfigured}
      exams={exams}
      now={now}
      onReviewQuestions={(exam) => { setSelectedPublicExam(exam); setPage('public-questions') }}
      onLeaderboard={(exam) => { setSelectedPublicExam(exam); setPage('leaderboard') }}
    />""",
"welcome page navigation props"
)
once(
"team={team} onRegister={chooseRegistration}",
"team={team} onRegister={chooseRegistration}\n          onReviewQuestions={(exam) => { setSelectedPublicExam(exam); setPage('public-questions') }}\n          onLeaderboard={(exam) => { setSelectedPublicExam(exam); setPage('leaderboard') }}",
"dashboard navigation props"
)

# Render logged-out public review pages before the welcome/auth branches.
once(
"  if (!isLoggedIn && page === 'welcome') {",
"""  if (!isLoggedIn && selectedPublicExam && page === 'leaderboard') {
    return <PublicLeaderboardPage exam={selectedPublicExam} onBack={() => { setSelectedPublicExam(null); setPage('welcome') }} />
  }
  if (!isLoggedIn && selectedPublicExam && page === 'public-questions') {
    return <PublicQuestionPage exam={selectedPublicExam}
      onBack={() => { setSelectedPublicExam(null); setPage('welcome') }}
      onLeaderboard={() => setPage('leaderboard')} />
  }

  if (!isLoggedIn && page === 'welcome') {""",
"logged-out public review routes"
)

# Render authenticated public review pages in the main route outlet.
once(
"""        {page === 'exam' && selectedExam && <ExamPage""",
"""        {page === 'public-questions' && selectedPublicExam && <PublicQuestionPage
          exam={selectedPublicExam}
          onBack={() => { setSelectedPublicExam(null); setPage('dashboard') }}
          onLeaderboard={() => setPage('leaderboard')}
        />}
        {page === 'leaderboard' && selectedPublicExam && <PublicLeaderboardPage
          exam={selectedPublicExam}
          onBack={() => { setSelectedPublicExam(null); setPage('dashboard') }}
        />}
        {page === 'exam' && selectedExam && <ExamPage""",
"authenticated public review routes"
)

# 2) Add topic-tag normalization and readable colored chips.
tag_helpers = r'''
function getContestTagTone(tag: string): string {
  const value = tag.trim().toLocaleLowerCase().replace(/[\s‌ـ_-]+/g, '')
  if (value.includes('ترکیبیات') || value.includes('combinatorics')) return 'combinatorics'
  if (value.includes('الگوریتم') || value.includes('algorithm')) return 'algorithm'
  if (value.includes('برنامهنویسی') || value.includes('programming') || value.includes('coding')) return 'programming'
  if (value.includes('گراف') || value.includes('graph')) return 'graph'
  if (value.includes('جبر') || value.includes('algebra')) return 'algebra'
  if (value.includes('هندسه') || value.includes('geometry')) return 'geometry'
  if (value.includes('نظریهاعداد') || value.includes('numbertheory')) return 'number-theory'
  if (value.includes('احتمال') || value.includes('probability')) return 'probability'
  if (value.includes('ریاضی') || value.includes('math')) return 'mathematics'
  if (value.includes('فیزیک') || value.includes('physics')) return 'physics'
  return 'default'
}

function ContestTagList({ tags, compact = false }: { tags?: string[] | null; compact?: boolean }) {
  const visible = (tags || []).map((tag) => tag.trim()).filter(Boolean).slice(0, 6)
  if (visible.length === 0) return null
  return <div className={'contest-tag-list' + (compact ? ' compact' : '')}>
    {visible.map((tag) => <span className={'contest-tag contest-tag--' + getContestTagTone(tag)} key={tag}>{tag}</span>)}
  </div>
}

'''
if s.count("function getContestTagTone(") != 0:
    raise SystemExit("Tag helper already exists")
tag_anchor = "function WelcomePage("
if s.count(tag_anchor) != 1:
    raise SystemExit("WelcomePage tag helper insertion point mismatch")
s = s.replace(tag_anchor, tag_helpers + tag_anchor, 1)

# Dashboard card gets tags within its own component, independent of markup around it.
card_start = s.index("function ExamCard(")
card_end = s.index("\nfunction StatusBadge(", card_start)
card = s[card_start:card_end]
if "ContestTagList tags={exam.tags}" not in card:
    title_anchor = "<h3>{exam.title}</h3>"
    if card.count(title_anchor) != 1:
        raise SystemExit("ExamCard title tag insertion point mismatch")
    card = card.replace(title_anchor, title_anchor + "<ContestTagList tags={exam.tags} />", 1)
s = s[:card_start] + card + s[card_end:]

once(
"""<td><b>{exam.title}</b><small>{exam.description || 'مسابقهٔ آنلاین فارسی جاج'}</small></td>""",
"""<td><b>{exam.title}</b><small>{exam.description || 'مسابقهٔ آنلاین فارسی جاج'}</small><ContestTagList tags={exam.tags} compact /></td>""",
"public contest table tags"
)
once(
"""<small>{dateText(exam.starts_at)} · {exam.is_published ? 'منتشرشده' : 'پیش‌نویس'}</small>
              <div className="admin-exam-files">""",
"""<small>{dateText(exam.starts_at)} · {exam.is_published ? 'منتشرشده' : 'پیش‌نویس'}</small>
              <ContestTagList tags={exam.tags} compact />
              <div className="admin-exam-files">""",
"admin contest list tags"
)
search_anchor = "(exam.title + ' ' + (exam.description || '')).toLowerCase()"
if search_anchor not in s:
    raise SystemExit("Contest search expression was not found.")
s = s.replace(
    search_anchor,
    "(exam.title + ' ' + (exam.description || '') + ' ' + (exam.tags || []).join(' ')).toLowerCase()"
)

# 3) Topic tags in create/edit form and persist them on the contest row.
once(
"const [editingExamId, setEditingExamId] = useState<string | null>(null)",
"const [editingExamId, setEditingExamId] = useState<string | null>(null)\n  const [adminTags, setAdminTags] = useState('')",
"admin contest tag state"
)
once(
"setAdminDescription(exam.description || '')",
"setAdminDescription(exam.description || '')\n    setAdminTags((exam.tags || []).join(', '))",
"load contest tags into edit form"
)
once(
"""function AdminPage({ title, description, start, duration,""",
"""function AdminPage({ title, description, tagsText, onTagsText, start, duration,""",
"admin tag props"
)
once(
"""title: string; description: string; start: string; duration: string; questions: AdminQuestion[]; busy: boolean;""",
"""title: string; description: string; tagsText: string; onTagsText: (value: string) => void; start: string; duration: string; questions: AdminQuestion[]; busy: boolean;""",
"admin tag prop types"
)
admin_start = s.index("function AdminPage(")
admin_end = s.index("\nfunction ProfilePage(", admin_start)
admin = s[admin_start:admin_end]
description_index = admin.find("توضیحات کوتاه")
if description_index < 0:
    raise SystemExit("Admin form description field was not found.")
label_start = admin.rfind("<label", 0, description_index)
label_end = admin.find("</label>", description_index)
if label_start < 0 or label_end < 0:
    raise SystemExit("Could not isolate the admin description field.")
label_end += len("</label>")
tag_field = """
          <label className="field-label">تگ‌های موضوعی مسابقه
            <input value={tagsText} onChange={(e) => onTagsText(e.target.value)} placeholder="مثلاً ترکیبیات، گراف، الگوریتم" />
            <small>تگ‌ها را با ویرگول جدا کن؛ رنگ هر تگ به‌صورت خودکار انتخاب می‌شود.</small>
          </label>"""
if "تگ‌های موضوعی مسابقه" not in admin:
    admin = admin[:label_end] + tag_field + admin[label_end:]
    s = s[:admin_start] + admin + s[admin_end:]
once(
"questionFile={questionFile}",
"questionFile={questionFile} tagsText={adminTags} onTagsText={setAdminTags}",
"admin tag props at route"
)

once(
"""    let examId = editingExamId
    let filePath = questionFilePath""",
"""    let examId = editingExamId
    const normalizedExamTags = Array.from(new Set(adminTags.split(',').map((tag) => tag.trim().slice(0, 32)).filter(Boolean))).slice(0, 6)
    let filePath = questionFilePath""",
"normalize contest tags"
)
once(
"else notify('آزمون و پاسخ‌نامه با موفقیت ویرایش شدند.', 'success')",
"""else {
          const { error: tagError } = await supabase.from('exams').update({ tags: normalizedExamTags }).eq('id', editingExamId)
          if (tagError) {
            notify('آزمون ویرایش شد اما ذخیره تگ‌ها ناموفق بود: ' + tagError.message, 'error')
            failed = true
          } else notify('آزمون، پاسخ‌نامه و تگ‌ها با موفقیت ویرایش شدند.', 'success')
        }""",
"persist edited contest tags"
)
once(
"""        examId = data as string
        if (questionFile && examId) {""",
"""        examId = data as string
        if (examId) {
          const { error: tagError } = await supabase.from('exams').update({ tags: normalizedExamTags }).eq('id', examId)
          if (tagError) {
            notify('آزمون ساخته شد اما ذخیره تگ‌ها ناموفق بود: ' + tagError.message, 'error')
            failed = true
          }
        }
        if (!failed && questionFile && examId) {""",
"persist new contest tags"
)
once(
"setAdminDescription('')",
"setAdminDescription('')\n      setAdminTags('')",
"reset contest tag form"
)

# Give public review pages their own visible canvas and prevent uncaught async failures.
once(
"""  return <section className="leaderboard-page">""",
"""  return <section className="leaderboard-page public-review-screen" role="main">""",
"leaderboard screen container"
)
question_page_start = s.index("function PublicQuestionPage(")
question_page_end = s.index("\nfunction ProfilePage(", question_page_start)
question_page = s[question_page_start:question_page_end]
question_shell = '  return <div className="public-site">'
if question_page.count(question_shell) != 1:
    raise SystemExit("PublicQuestionPage shell insertion point mismatch")
question_page = question_page.replace(
    question_shell,
    '  return <div className="public-site public-review-screen">',
    1
)
s = s[:question_page_start] + question_page + s[question_page_end:]
once(
"""      const { data, error: queryError } = await client.rpc('get_public_exam_leaderboard', { p_exam_id: exam.id })
      if (!alive) return
      if (queryError) setError(queryError.message)
      else setRows((data || []) as LeaderboardRow[])
      setLoading(false)""",
"""      try {
        const { data, error: queryError } = await client.rpc('get_public_exam_leaderboard', { p_exam_id: exam.id })
        if (!alive) return
        if (queryError) setError(queryError.message)
        else setRows(Array.isArray(data) ? data as LeaderboardRow[] : [])
      } catch (cause) {
        if (alive) setError(cause instanceof Error ? cause.message : 'دریافت جدول امتیازات ناموفق بود.')
      } finally {
        if (alive) setLoading(false)
      }""",
"leaderboard async error handling"
)
once(
"""      const [questions, resource] = await Promise.all([
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
      setLoading(false)""",
"""      try {
        const [questions, resource] = await Promise.all([
          client.rpc('get_public_exam_questions', { p_exam_id: exam.id }),
          client.rpc('get_public_exam_question_resource', { p_exam_id: exam.id }),
        ])
        if (!alive) return
        if (questions.error) setError(questions.error.message)
        else setQuestionRows(Array.isArray(questions.data) ? questions.data : [])
        if (resource.error) setError((current) => current || resource.error.message)
        const item = Array.isArray(resource.data) ? resource.data[0] : resource.data
        let url = item?.question_pdf_url || ''
        if (item?.question_file_path) {
          const { data, error: signedError } = await client.storage
            .from('exam-question-files').createSignedUrl(item.question_file_path, 3600)
          if (!signedError && data?.signedUrl) url = data.signedUrl
          else if (!url && signedError) setError((current) => current || signedError.message)
        }
        if (alive) setPaperUrl(url)
      } catch (cause) {
        if (alive) setError(cause instanceof Error ? cause.message : 'دریافت صورت سؤال ناموفق بود.')
      } finally {
        if (alive) setLoading(false)
      }""",
"question resource async error handling"
)

# Prefer a visible download/open action; make the embedded PDF preview optional.
once(
"""          {paperUrl
            ? <><div className="public-question-actions"><a href={paperUrl} target="_blank" rel="noreferrer">باز کردن یا دانلود فایل PDF <ExternalLink size={14} /></a></div><iframe src={paperUrl} title={'صورت سؤال ' + exam.title} loading="lazy" /></>
            : <div className="public-empty"><FileUp size={25} /><b>فایل صورت سؤال برای این مسابقه ثبت نشده است.</b><span>{error || 'از برگزارکننده بخواهید فایل PDF را اضافه کند.'}</span></div>}""",
"""          {paperUrl
            ? <div className="public-question-file">
                <div className="public-question-file-copy"><FileUp size={23} /><div><b>فایل صورت سؤال آماده است</b><span>می‌توانی PDF را در صفحه‌ای جدا باز کنی یا پیش‌نمایش آن را همین‌جا ببینی.</span></div></div>
                <div className="public-question-actions"><a className="button primary small" href={paperUrl} target="_blank" rel="noreferrer">باز کردن PDF <ExternalLink size={14} /></a></div>
                <details className="public-pdf-preview"><summary>نمایش پیش‌نمایش PDF</summary><iframe src={paperUrl} title={'صورت سؤال ' + exam.title} loading="lazy" /></details>
              </div>
            : <div className="public-empty"><FileUp size={25} /><b>فایل صورت سؤال برای این مسابقه ثبت نشده است.</b><span>{error || 'از برگزارکننده بخواهید فایل PDF را اضافه کند.'}</span></div>}""",
"make pdf preview optional and visible"
)

# Add tags to the public review headers and show errors as readable content.
once(
"""<div className="leaderboard-hero"><div className="eyebrow">CONTEST LEADERBOARD</div><h1>جدول امتیازات</h1><p>{exam.title}</p></div>""",
"""<div className="leaderboard-hero"><div className="eyebrow">CONTEST LEADERBOARD</div><h1>جدول امتیازات</h1><p>{exam.title}</p><ContestTagList tags={exam.tags} /></div>""",
"leaderboard tags"
)
once(
"""<div className="eyebrow">CONTEST REVIEW</div><h1>{exam.title}</h1><p>صورت سؤال مسابقه پس از پایان برای همه قابل مشاهده است.</p>""",
"""<div className="eyebrow">CONTEST REVIEW</div><h1>{exam.title}</h1><p>صورت سؤال مسابقه پس از پایان برای همه قابل مشاهده است.</p><ContestTagList tags={exam.tags} />""",
"question page tags"
)

css += r"""

/* Readable topic badges */
.contest-tag-list { display:flex; flex-wrap:wrap; align-items:center; gap:6px; margin:9px 0 3px; }
.contest-tag-list.compact { gap:5px; margin-top:7px; }
.contest-tag { display:inline-flex; align-items:center; min-height:24px; padding:4px 9px; border:1px solid transparent; border-radius:999px; font-size:10px; font-weight:750; line-height:1.35; white-space:nowrap; }
.contest-tag-list.compact .contest-tag { min-height:20px; padding:3px 7px; font-size:9px; }
.contest-tag--combinatorics { color:#168553; background:rgba(34,184,111,.12); border-color:rgba(34,184,111,.26); }
.contest-tag--algorithm { color:#d64b55; background:rgba(226,75,87,.11); border-color:rgba(226,75,87,.25); }
.contest-tag--programming { color:#347ed7; background:rgba(59,130,246,.12); border-color:rgba(59,130,246,.25); }
.contest-tag--graph { color:#aa8500; background:rgba(240,190,40,.16); border-color:rgba(220,175,25,.3); }
.contest-tag--algebra { color:#cb741c; background:rgba(237,145,52,.14); border-color:rgba(237,145,52,.27); }
.contest-tag--geometry { color:#8756d8; background:rgba(146,102,230,.14); border-color:rgba(146,102,230,.27); }
.contest-tag--number-theory { color:#168b9b; background:rgba(34,184,197,.12); border-color:rgba(34,184,197,.25); }
.contest-tag--probability { color:#bc4f91; background:rgba(210,89,158,.12); border-color:rgba(210,89,158,.25); }
.contest-tag--mathematics { color:#6b65d8; background:rgba(115,108,224,.13); border-color:rgba(115,108,224,.26); }
.contest-tag--physics { color:#278b80; background:rgba(43,170,152,.12); border-color:rgba(43,170,152,.25); }
.contest-tag--default { color:var(--muted); background:var(--panel-2); border-color:var(--line); }

/* Self-contained review screens never inherit a blank/transparent canvas. */
.public-review-screen { position:relative; isolation:isolate; display:block; width:100%; min-height:calc(100vh - 60px); color:var(--text); background:var(--bg); }
.redesign-shell .public-review-screen { padding:8px 0 28px; }
.leaderboard-page.public-review-screen { padding:8px 0 30px; }
.public-review-screen .leaderboard-panel,
.public-review-screen .public-question-panel { color:var(--text); background:var(--panel); }
.leaderboard-hero .contest-tag-list { margin-top:12px; }
.public-question-file { display:flex; flex-direction:column; gap:14px; }
.public-question-file-copy { display:flex; align-items:center; gap:12px; padding:15px; border:1px solid var(--line); border-radius:13px; background:var(--panel-2); }
.public-question-file-copy>svg { flex:0 0 auto; color:var(--accent); }
.public-question-file-copy>div { display:flex; flex-direction:column; gap:5px; }
.public-question-file-copy b { font-size:13px; color:var(--text); }
.public-question-file-copy span { font-size:11px; color:var(--muted); line-height:1.8; }
.public-question-actions { display:flex; justify-content:flex-start; margin:0; }
.public-pdf-preview { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
.public-pdf-preview summary { padding:13px 15px; background:var(--panel-2); color:var(--text); font-size:12px; cursor:pointer; }
.public-pdf-preview iframe { display:block; width:100%; min-height:70vh; border:0; background:#fff; }
@media(max-width:640px) {
  .contest-tag { font-size:9px; }
  .public-review-screen { min-height:calc(100dvh - 58px); }
  .public-question-file-copy { align-items:flex-start; }
  .public-pdf-preview iframe { min-height:60vh; }
}
"""
app_path.write_text(s, encoding="utf-8")
css_path.write_text(css, encoding="utf-8")
print("Applied stable review routing, auth refresh preservation, colored contest tags and resilient PDF viewing.")
