from pathlib import Path

path = Path("src/App.tsx")
source = path.read_text(encoding="utf-8")

def replace_once(old: str, new: str, label: str) -> None:
    global source
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    source = source.replace(old, new, 1)

replace_once(
"""  LayoutDashboard, LogOut, Moon, Plus, RefreshCw, ShieldCheck,
  Sun, UserRound, Users, XCircle,
""",
"""  LayoutDashboard, LogOut, Moon, Plus, RefreshCw, ShieldCheck,
  Sun, UserRound, Users, XCircle, UserPlus, Pencil, Trash2, FileUp, ExternalLink,
""",
"icons"
)
replace_once(
"type Profile = { id: string; full_name: string; role: 'participant' | 'admin' }",
"""type Profile = { id: string; full_name: string; role: 'participant' | 'admin'; username?: string }
type Team = { id: string; name: string; captain_id: string; role: 'captain' | 'member' }
type TeamMember = { user_id: string; role: 'captain' | 'member'; full_name: string; username: string }
type TeamInvitation = { id: string; team_id: string; invited_by: string; created_at: string; teams?: { name: string } | null }""",
"profile types"
)

replace_once(
"type ExamResult = {\n  id: string",
"type ExamResult = {\n  team_id?: string | null\n  id: string",
"team result type"
)
replace_once(
"  is_published: boolean\n  created_at?: string\n",
"  is_published: boolean\n  question_pdf_url?: string | null\n  question_file_path?: string | null\n  created_at?: string\n",
"exam type"
)
replace_once("type Page = 'dashboard' | 'exam' | 'admin' | 'profile'", "type Page = 'dashboard' | 'exam' | 'admin' | 'profile' | 'team'", "page type")
replace_once(
"  const [profiles, setProfiles] = useState<Profile[]>([])\n",
"""  const [profiles, setProfiles] = useState<Profile[]>([])
  const [authUsername, setAuthUsername] = useState('')
  const [team, setTeam] = useState<Team | null>(null)
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([])
  const [teamInvitations, setTeamInvitations] = useState<TeamInvitation[]>([])
  const [myRegistrations, setMyRegistrations] = useState<string[]>([])
  const [myTeamRegistrations, setMyTeamRegistrations] = useState<string[]>([])
  const [teamName, setTeamName] = useState('')
  const [inviteIdentifier, setInviteIdentifier] = useState('')
  const [teamBusy, setTeamBusy] = useState(false)
  const [editingExamId, setEditingExamId] = useState<string | null>(null)
  const [questionPdfUrl, setQuestionPdfUrl] = useState('')
  const [questionFile, setQuestionFile] = useState<File | null>(null)
  const [questionFilePath, setQuestionFilePath] = useState<string | null>(null)
  const [questionResourceUrl, setQuestionResourceUrl] = useState('')
""",
"additional state"
)

replace_once(
"""    const [profileResponse, examResponse] = await Promise.all([
      supabase.from('profiles').select('id,full_name,role').eq('id', session.user.id).single(),
      supabase.from('exams').select('id,title,description,starts_at,duration_minutes,is_published,created_at').order('starts_at', { ascending: false }),
    ])
    if (profileResponse.data) setProfile(profileResponse.data as Profile)
""",
"""    const [profileResponse, examResponse, membershipResponse, invitationResponse, ownRegistrationResponse, teamRegistrationResponse] = await Promise.all([
      supabase.from('profiles').select('id,full_name,role,username').eq('id', session.user.id).single(),
      supabase.from('exams').select('id,title,description,starts_at,duration_minutes,is_published,created_at').order('starts_at', { ascending: false }),
      supabase.from('team_members').select('team_id,role').eq('user_id', session.user.id).maybeSingle(),
      supabase.from('team_invitations').select('id,team_id,invited_by,created_at,teams(name)').eq('invited_user_id', session.user.id).eq('status', 'pending').order('created_at', { ascending: false }),
      supabase.from('exam_registrations').select('exam_id').eq('user_id', session.user.id),
      supabase.from('exam_team_registrations').select('exam_id,team_id'),
    ])
    if (profileResponse.data) setProfile(profileResponse.data as Profile)
    if (invitationResponse.data) setTeamInvitations(invitationResponse.data as unknown as TeamInvitation[])
    if (ownRegistrationResponse.data) setMyRegistrations(ownRegistrationResponse.data.map((row) => row.exam_id))
    if (teamRegistrationResponse.data) setMyTeamRegistrations(teamRegistrationResponse.data.map((row) => row.exam_id))
    if (membershipResponse.data) {
      const [teamResponse, memberResponse] = await Promise.all([
        supabase.from('teams').select('id,name,captain_id').eq('id', membershipResponse.data.team_id).single(),
        supabase.from('team_members').select('team_id,user_id,role').eq('team_id', membershipResponse.data.team_id),
      ])
      if (teamResponse.data) setTeam({ ...teamResponse.data, role: membershipResponse.data.role } as Team)
      if (memberResponse.data) {
        const memberIds = memberResponse.data.map((row) => row.user_id)
        const memberProfilesResponse = await supabase.from('profiles').select('id,full_name,username').in('id', memberIds)
        const memberProfiles = new Map((memberProfilesResponse.data || []).map((row) => [row.id, row]))
        setTeamMembers(memberResponse.data.map((row) => {
          const p = memberProfiles.get(row.user_id)
          return { user_id: row.user_id, role: row.role, full_name: p?.full_name || 'کاربر', username: p?.username || '' }
        }) as TeamMember[])
      }
    } else {
      setTeam(null)
      setTeamMembers([])
    }
""",
"main data loading"
)

replace_once(
"""      const [qRes, aRes] = await Promise.all([
        client.from('exam_questions').select('id,exam_id,question_number,points').eq('exam_id', selectedExam.id).order('question_number'),
        client.from('exam_answers').select('question_number,answer').eq('exam_id', selectedExam.id).eq('user_id', session.user.id),
      ])
""",
"""      const teamRegistrationResponse = team
        ? await client.from('exam_team_registrations').select('team_id').eq('exam_id', selectedExam.id).eq('team_id', team.id).maybeSingle()
        : { data: null }
      const isSharedTeamAttempt = Boolean(teamRegistrationResponse.data)
      const personalRegistrationResponse = !isSharedTeamAttempt
        ? await client.from('exam_registrations').select('exam_id').eq('exam_id', selectedExam.id).eq('user_id', session.user.id).maybeSingle()
        : { data: null }
      const answersQuery = isSharedTeamAttempt
        ? client.from('exam_answers').select('question_number,answer').eq('exam_id', selectedExam.id).eq('team_id', team!.id)
        : client.from('exam_answers').select('question_number,answer').eq('exam_id', selectedExam.id).eq('user_id', session.user.id).is('team_id', null)
      const [qRes, aRes] = await Promise.all([
        client.from('exam_questions').select('id,exam_id,question_number,points').eq('exam_id', selectedExam.id).order('question_number'),
        answersQuery,
      ])
      let resourceUrl = ''
      if ((isSharedTeamAttempt || personalRegistrationResponse.data) && selectedStatus === 'active') {
        const { data: resourceRows } = await client.rpc('get_exam_question_resource', { p_exam_id: selectedExam.id })
        const resource = Array.isArray(resourceRows) ? resourceRows[0] : resourceRows
        resourceUrl = resource?.question_pdf_url || ''
        if (resource?.question_file_path) {
          const fileTtl = Math.max(1, Math.ceil((examEnd(selectedExam).getTime() - Date.now()) / 1000))
          const { data: fileData } = await client.storage.from('exam-question-files').createSignedUrl(resource.question_file_path, fileTtl)
          if (fileData?.signedUrl) resourceUrl = fileData.signedUrl
        }
      }
      if (alive) setQuestionResourceUrl(resourceUrl)
""",
"load shared answers and resources"
)
replace_once(
"""        const resultRes = await client.from('exam_results').select('*').eq('exam_id', selectedExam.id).eq('user_id', session.user.id).maybeSingle()
        if (alive && resultRes.data) setExamResult(resultRes.data as ExamResult)
""",
"""        const resultRes = team
          ? await client.from('exam_results').select('*').eq('exam_id', selectedExam.id).eq('team_id', team.id).maybeSingle()
          : await client.from('exam_results').select('*').eq('exam_id', selectedExam.id).eq('user_id', session.user.id).is('team_id', null).maybeSingle()
        if (alive && resultRes.data) setExamResult(resultRes.data as ExamResult)
""",
"load team result"
)
replace_once("  }, [selectedExam?.id, selectedStatus, page, session?.user.id, isDemo])", "  }, [selectedExam?.id, selectedStatus, page, session?.user.id, isDemo, team?.id])", "exam load effect deps")
replace_once(
"""      const { data } = await client.from('exam_results').select('*').eq('exam_id', selectedExam.id).eq('user_id', session.user.id).maybeSingle()
      if (data) setExamResult(data as ExamResult)
""",
"""      const resultResponse = team
        ? await client.from('exam_results').select('*').eq('exam_id', selectedExam.id).eq('team_id', team.id).maybeSingle()
        : await client.from('exam_results').select('*').eq('exam_id', selectedExam.id).eq('user_id', session.user.id).is('team_id', null).maybeSingle()
      if (resultResponse.data) setExamResult(resultResponse.data as ExamResult)
""",
"finalize team result"
)
replace_once("  }, [selectedExam, page, now, isDemo, session?.user.id])", "  }, [selectedExam, page, now, isDemo, session?.user.id, team?.id])", "finalizer deps")
replace_once(
"""      const operations = (Object.entries(answerValues) as [string, string][]).map(async ([question, raw]) => {
        const questionNumber = Number(question)
        if (!raw.trim()) {
          return client.from('exam_answers').delete()
            .eq('exam_id', selectedExam.id).eq('user_id', session.user.id).eq('question_number', questionNumber)
        }
        if (!validNumber(raw)) return null
        return client.from('exam_answers').upsert({
          exam_id: selectedExam.id,
          user_id: session.user.id,
          question_number: questionNumber,
          answer: normalizeNumber(raw),
        }, { onConflict: 'exam_id,user_id,question_number' })
      })
""",
"""      const changedAnswers = { ...pendingAnswerChanges }
      const operations = (Object.entries(changedAnswers) as [string, string][]).map(async ([question, raw]) => {
        const questionNumber = Number(question)
        if (raw.trim() && !validNumber(raw)) return null
        return client.rpc('save_exam_answer', {
          p_exam_id: selectedExam.id,
          p_question_number: questionNumber,
          p_answer: raw.trim() ? normalizeNumber(raw) : null,
        })
      })
""",
"shared autosave"
)

replace_once(
"""  const [answerDirty, setAnswerDirty] = useState(false)""",
"""  const [answerDirty, setAnswerDirty] = useState(false)
  const [pendingAnswerChanges, setPendingAnswerChanges] = useState<Record<number, string>>({})""",
"pending team answer changes"
)
replace_once(
"""    setAnswerValues({})
    setExamResult(null)
    setAnswerDirty(false)
    setPage('exam')
""",
"""    setAnswerValues({})
    setExamResult(null)
    setAnswerDirty(false)
    setPendingAnswerChanges({})
    setPage('exam')
""",
"reset pending answers on exam open"
)
replace_once(
"""  const saveAnswer = (questionNumber: number, value: string) => {
    setAnswerValues((current) => ({ ...current, [questionNumber]: value }))
    setAnswerDirty(true)
  }
""",
"""  const saveAnswer = (questionNumber: number, value: string) => {
    setAnswerValues((current) => ({ ...current, [questionNumber]: value }))
    setPendingAnswerChanges((current) => ({ ...current, [questionNumber]: value }))
    setAnswerDirty(true)
  }
""",
"track only edited questions"
)
replace_once(
"    if (!answerDirty || !selectedExam || page !== 'exam' || selectedStatus !== 'active') return",
"    if (!answerDirty || !selectedExam || page !== 'exam' || selectedStatus !== 'active' || Object.keys(pendingAnswerChanges).length === 0) return",
"autosave only dirty questions"
)
replace_once(
"  }, [answerValues, answerDirty, selectedExam?.id, page, isDemo, session?.user.id])",
"  }, [pendingAnswerChanges, answerDirty, selectedExam?.id, page, selectedStatus, isDemo, session?.user.id])",
"autosave pending answer dependencies"
)
replace_once(
"""      if (isDemo) {
        setSaving(false)
        setAnswerDirty(false)
        return
      }
""",
"""      if (isDemo) {
        setSaving(false)
        setAnswerDirty(false)
        setPendingAnswerChanges({})
        return
      }
""",
"clear pending demo answers"
)
replace_once(
"""      const responses = await Promise.all(operations)
      const error = responses.find((item) => item && item.error)?.error
      if (error) setNotice({ type: 'error', text: `ذخیره پاسخ انجام نشد: ${error.message}` })
      else setNotice({ type: 'success', text: 'پاسخ‌ها ذخیره شدند.' })
      setSaving(false)
      setAnswerDirty(false)
""",
"""      const responses = await Promise.all(operations)
      const error = responses.find((item) => item && item.error)?.error
      if (error) setNotice({ type: 'error', text: `ذخیره پاسخ انجام نشد: ${error.message}` })
      else {
        setNotice({ type: 'success', text: 'پاسخ‌ها ذخیره شدند.' })
        setPendingAnswerChanges((current) => {
          const next = { ...current }
          for (const [question, raw] of Object.entries(changedAnswers)) {
            const key = Number(question)
            if (next[key] === raw) delete next[key]
          }
          return next
        })
      }
      setSaving(false)
""",
"clear only successfully saved team changes"
)

replace_once(
"""  useEffect(() => {
    const client = supabase
    if (!isAdmin || !client || !session?.user.id || page !== 'admin') return
""",
"""  useEffect(() => {
    const client = supabase
    if (!client || !team?.id || !selectedExam || page !== 'exam' || selectedStatus !== 'active' || !myTeamRegistrations.includes(selectedExam.id)) return
    let alive = true
    const refreshSharedAnswers = async () => {
      const { data } = await client.from('exam_answers').select('question_number,answer')
        .eq('exam_id', selectedExam.id).eq('team_id', team.id)
      if (!alive || !data) return
      setAnswerValues(() => {
        const next: Record<number, string> = {}
        for (const row of data) next[row.question_number] = String(row.answer)
        for (const [question, raw] of Object.entries(pendingAnswerChanges)) next[Number(question)] = raw
        return next
      })
    }
    void refreshSharedAnswers()
    const timer = window.setInterval(() => { void refreshSharedAnswers() }, 2500)
    return () => { alive = false; window.clearInterval(timer) }
  }, [selectedExam?.id, team?.id, page, selectedStatus, myTeamRegistrations, pendingAnswerChanges])

  useEffect(() => {
    const client = supabase
    if (!isAdmin || !client || !session?.user.id || page !== 'admin') return
""",
"live shared team answer refresh"
)
replace_once(
"""      const [r, p] = await Promise.all([
        client.from('exam_results').select('*').order('graded_at', { ascending: false }).limit(100),
        client.from('profiles').select('id,full_name,role'),
      ])
""",
"""      const [r, p] = await Promise.all([
        client.from('exam_results').select('*').order('graded_at', { ascending: false }).limit(100),
        client.from('profiles').select('id,full_name,role,username').order('created_at', { ascending: false }),
      ])
""",
"admin lists"
)

replace_once(
"""      if (!authName.trim()) {
        setAuthBusy(false)
        return notify('نام و نام خانوادگی را وارد کنید.', 'error')
      }
""",
"""      if (!authName.trim()) {
        setAuthBusy(false)
        return notify('نام و نام خانوادگی را وارد کنید.', 'error')
      }
      if (!/^[a-zA-Z0-9_]{3,24}$/.test(authUsername)) {
        setAuthBusy(false)
        return notify('نام کاربری باید ۳ تا ۲۴ حرف انگلیسی، عدد یا زیرخط باشد.', 'error')
      }
""",
"signup validation"
)
replace_once(
"options: { data: { full_name: authName.trim() }, emailRedirectTo: new URL(import.meta.env.BASE_URL, window.location.origin).toString() },",
"options: { data: { full_name: authName.trim(), username: authUsername.trim() }, emailRedirectTo: window.location.origin + window.location.pathname },",
"signup username metadata"
)
replace_once(
"""            {authMode === 'register' && <label className="field-label">نام و نام خانوادگی<input value={authName} onChange={(e) => setAuthName(e.target.value)} placeholder="مثلاً محمدمهدی افشار" autoComplete="name" /></label>}
            <label className="field-label">ایمیل (نام کاربری)<input type="email" value={authEmail} onChange={(e) => setAuthEmail(e.target.value)} placeholder="name@example.com" autoComplete="email" dir="ltr" /></label>
""",
"""            {authMode === 'register' && <>
              <label className="field-label">نام و نام خانوادگی<input value={authName} onChange={(e) => setAuthName(e.target.value)} placeholder="مثلاً محمدمهدی افشار" autoComplete="name" /></label>
              <label className="field-label">نام کاربری <small>(برای دعوت به تیم)</small><input value={authUsername} onChange={(e) => setAuthUsername(e.target.value)} placeholder="مثلاً EMEMAY" autoComplete="username" dir="ltr" /></label>
            </>}
            <label className="field-label">ایمیل<input type="email" value={authEmail} onChange={(e) => setAuthEmail(e.target.value)} placeholder="name@example.com" autoComplete="email" dir="ltr" /></label>
""",
"signup username field"
)

needle = """  const enterDemo = () => {
"""
insert = """  const createTeam = async (event: FormEvent) => {
    event.preventDefault()
    if (!supabase || !teamName.trim()) return
    setTeamBusy(true)
    const { error } = await supabase.rpc('create_team', { p_name: teamName.trim() })
    if (error) notify('ساخت تیم انجام نشد: ' + error.message, 'error')
    else {
      notify('تیم ساخته شد؛ شما کاپیتان آن هستید.', 'success')
      setTeamName('')
      await loadMainData()
    }
    setTeamBusy(false)
  }

  const inviteToTeam = async (event: FormEvent) => {
    event.preventDefault()
    if (!supabase || !inviteIdentifier.trim()) return
    setTeamBusy(true)
    const { error } = await supabase.rpc('invite_team_member', { p_identifier: inviteIdentifier.trim() })
    if (error) notify('ارسال دعوت‌نامه ناموفق بود: ' + error.message, 'error')
    else {
      notify('دعوت‌نامه ارسال شد.', 'success')
      setInviteIdentifier('')
      await loadMainData()
    }
    setTeamBusy(false)
  }

  const respondToInvitation = async (id: string, accept: boolean) => {
    if (!supabase) return
    const { error } = await supabase.rpc('respond_team_invitation', { p_invitation_id: id, p_accept: accept })
    if (error) notify('ثبت پاسخ دعوت‌نامه ناموفق بود: ' + error.message, 'error')
    else {
      notify(accept ? 'به تیم اضافه شدید.' : 'دعوت‌نامه رد شد.', 'success')
      await loadMainData()
    }
  }

  const registerForExam = async (exam: Exam) => {
    if (!supabase) return
    if (team && team.role !== 'captain') return notify('برای ثبت‌نام تیمی، از کاپیتان تیم بخواهید اقدام کند.', 'info')
    const { error } = await supabase.rpc('register_for_exam', {
      p_exam_id: exam.id,
      p_team_id: team?.id ?? null,
    })
    if (error) notify('ثبت‌نام انجام نشد: ' + error.message, 'error')
    else {
      notify(team ? 'تیم با موفقیت در آزمون ثبت‌نام شد.' : 'در آزمون ثبت‌نام شدید.', 'success')
      await loadMainData()
    }
  }

  const loadExamForEdit = async (exam: Exam) => {
    if (!supabase) return
    const [questionResponse, keyResponse, resourceResponse] = await Promise.all([
      supabase.from('exam_questions').select('question_number,points').eq('exam_id', exam.id).order('question_number'),
      supabase.from('exam_answer_keys').select('question_number,correct_answer').eq('exam_id', exam.id).order('question_number'),
      supabase.rpc('get_exam_question_resource', { p_exam_id: exam.id }),
    ])
    if (questionResponse.error || keyResponse.error || resourceResponse.error) return notify('دریافت اطلاعات آزمون برای ویرایش ناموفق بود.', 'error')
    const resource = Array.isArray(resourceResponse.data) ? resourceResponse.data[0] : resourceResponse.data
    const answerMap = new Map((keyResponse.data || []).map((row) => [row.question_number, String(row.correct_answer)]))
    setAdminTitle(exam.title)
    setAdminDescription(exam.description || '')
    const localStart = new Date(new Date(exam.starts_at).getTime() - new Date().getTimezoneOffset() * 60000)
    setAdminStart(localStart.toISOString().slice(0, 16))
    setAdminDuration(String(exam.duration_minutes))
    setAdminQuestions((questionResponse.data || []).map((row) => ({
      answer: answerMap.get(row.question_number) || '',
      points: String(row.points),
    })))
    setQuestionPdfUrl(resource?.question_pdf_url || '')
    setQuestionFilePath(resource?.question_file_path || null)
    setQuestionFile(null)
    setEditingExamId(exam.id)
    setPage('admin')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const deleteExam = async (exam: Exam) => {
    if (!supabase || !window.confirm('آزمون «' + exam.title + '» و تمام پاسخ‌ها و نتایج آن حذف شود؟')) return
    const { error } = await supabase.from('exams').delete().eq('id', exam.id)
    if (error) notify('حذف آزمون ناموفق بود: ' + error.message, 'error')
    else {
      notify('آزمون حذف شد.', 'success')
      await loadMainData()
    }
  }

  const toggleExamPublish = async (exam: Exam) => {
    if (!supabase) return
    const { error } = await supabase.from('exams').update({ is_published: !exam.is_published }).eq('id', exam.id)
    if (error) notify('تغییر وضعیت انتشار ناموفق بود: ' + error.message, 'error')
    else {
      notify(exam.is_published ? 'آزمون از دسترس خارج شد.' : 'آزمون منتشر شد.', 'success')
      await loadMainData()
    }
  }

  const changeUserRole = async (userId: string, role: 'participant' | 'admin') => {
    if (!supabase) return
    const { error } = await supabase.rpc('admin_set_profile_role', { p_user_id: userId, p_role: role })
    if (error) notify('تغییر نقش انجام نشد: ' + error.message, 'error')
    else {
      notify('نقش کاربر تغییر کرد.', 'success')
      await loadMainData()
      if (page === 'admin') {
        const { data } = await supabase.from('profiles').select('id,full_name,role,username')
        if (data) setProfiles(data as Profile[])
      }
    }
  }

"""
replace_once(needle, insert + needle, "team/admin handlers")

start = source.index("  const createExam = async (event: FormEvent) => {")
end = source.index("\n  const changeQuestionCount", start)
source = source[:start] + """  const createExam = async (event: FormEvent) => {
    event.preventDefault()
    if (!supabase || !session?.user.id) return
    if (!adminTitle.trim()) return notify('عنوان آزمون را وارد کنید.', 'error')
    if (!adminStart || !Number.isFinite(new Date(adminStart).getTime()) || (!editingExamId && new Date(adminStart).getTime() <= Date.now())) {
      return notify('زمان شروع آزمون جدید باید در آینده باشد.', 'error')
    }
    if (!Number.isInteger(Number(adminDuration)) || Number(adminDuration) < 1 || Number(adminDuration) > 600) {
      return notify('مدت آزمون باید بین ۱ تا ۶۰۰ دقیقه باشد.', 'error')
    }
    if (adminQuestions.length < 1 || adminQuestions.some((q) => !q.answer.trim() || !validNumber(q.answer) || !q.points.trim() || Number(q.points) <= 0)) {
      return notify('برای همه سؤال‌ها پاسخ عددی معتبر و نمره مثبت تعیین کنید.', 'error')
    }

    setAdminBusy(true)
    let examId = editingExamId
    let filePath = questionFilePath
    let failed = false

    if (editingExamId) {
      if (questionFile) {
        const safeName = questionFile.name.replace(/[^a-zA-Z0-9._-]/g, '_')
        filePath = editingExamId + '/' + Date.now() + '-' + safeName
        const { error: uploadError } = await supabase.storage.from('exam-question-files').upload(filePath, questionFile, { upsert: true, contentType: 'application/pdf' })
        if (uploadError) {
          notify('آپلود فایل سؤال ناموفق بود: ' + uploadError.message, 'error')
          failed = true
        }
      }
      if (!failed) {
        const { error } = await supabase.rpc('edit_exam_with_answer_key', {
          p_exam_id: editingExamId,
          p_title: adminTitle.trim(),
          p_description: adminDescription.trim(),
          p_starts_at: new Date(adminStart).toISOString(),
          p_duration_minutes: Number(adminDuration),
          p_questions: adminQuestions.map((q, i) => ({ question_number: i + 1, points: q.points, correct_answer: normalizeNumber(q.answer) })),
          p_question_pdf_url: questionPdfUrl.trim() || null,
          p_question_file_path: filePath,
        })
        if (error) {
          notify('ویرایش آزمون ناموفق بود: ' + error.message, 'error')
          failed = true
        } else notify('آزمون و پاسخ‌نامه با موفقیت ویرایش شدند.', 'success')
      }
    } else {
      const { data, error } = await supabase.rpc('create_exam_with_answer_key', {
        p_title: adminTitle.trim(),
        p_description: adminDescription.trim(),
        p_starts_at: new Date(adminStart).toISOString(),
        p_duration_minutes: Number(adminDuration),
        p_questions: adminQuestions.map((q, i) => ({ question_number: i + 1, points: q.points, correct_answer: normalizeNumber(q.answer) })),
      })
      if (error) {
        notify('ساخت آزمون ناموفق بود: ' + error.message, 'error')
        failed = true
      } else {
        examId = data as string
        if (questionFile && examId) {
          const safeName = questionFile.name.replace(/[^a-zA-Z0-9._-]/g, '_')
          filePath = examId + '/' + Date.now() + '-' + safeName
          const { error: uploadError } = await supabase.storage.from('exam-question-files').upload(filePath, questionFile, { upsert: true, contentType: 'application/pdf' })
          if (uploadError) {
            notify('آزمون ساخته شد اما آپلود فایل سؤال ناموفق بود: ' + uploadError.message, 'error')
            failed = true
          }
        }
        if (!failed && examId && (questionPdfUrl.trim() || filePath)) {
          const { error: resourceError } = await supabase.rpc('set_exam_question_resource', {
            p_exam_id: examId,
            p_question_pdf_url: questionPdfUrl.trim() || null,
            p_question_file_path: filePath,
          })
          if (resourceError) {
            notify('آزمون ساخته شد اما ثبت لینک سؤال ناموفق بود: ' + resourceError.message, 'error')
            failed = true
          }
        }
        if (!failed) notify('آزمون با موفقیت ساخته و منتشر شد.', 'success')
      }
    }

    if (!failed) {
      setAdminTitle('')
      setAdminDescription('')
      setAdminQuestions([{ answer: '', points: '1' }, { answer: '', points: '1' }, { answer: '', points: '1' }])
      setQuestionPdfUrl('')
      setQuestionFile(null)
      setQuestionFilePath(null)
      setEditingExamId(null)
      await loadMainData()
    }
    setAdminBusy(false)
  }
""" + source[end:]

replace_once(
"""        {isAdmin && <button className={page === 'admin' ? 'nav-item selected' : 'nav-item'} onClick={() => setPage('admin')}><ShieldCheck size={19} />مدیریت آزمون‌ها</button>}
        <button className={page === 'profile' ? 'nav-item selected' : 'nav-item'} onClick={() => setPage('profile')}><UserRound size={19} />پروفایل من</button>
""",
"""        {isAdmin && <button className={page === 'admin' ? 'nav-item selected' : 'nav-item'} onClick={() => setPage('admin')}><ShieldCheck size={19} />مدیریت آزمون‌ها</button>}
        <button className={page === 'team' ? 'nav-item selected' : 'nav-item'} onClick={() => setPage('team')}><Users size={19} />تیم و دعوت‌ها</button>
        <button className={page === 'profile' ? 'nav-item selected' : 'nav-item'} onClick={() => setPage('profile')}><UserRound size={19} />پروفایل من</button>
""",
"team nav"
)
replace_once(
"""        <div className="breadcrumb"><span className="topbar-brand"><span className="brand-mark"><img src={brandLogo} alt="" /></span><span>آزمون‌یار</span></span><ChevronLeft size={15} /><b>{page === 'dashboard' ? 'داشبورد' : page === 'exam' ? 'صفحه آزمون' : page === 'admin' ? 'مدیریت آزمون‌ها' : 'پروفایل من'}</b></div>
""",
"""        <div className="breadcrumb"><span className="topbar-brand"><span className="brand-mark"><img src={brandLogo} alt="" /></span><span>آزمون‌یار</span></span><ChevronLeft size={15} /><b>{page === 'dashboard' ? 'داشبورد' : page === 'exam' ? 'صفحه آزمون' : page === 'admin' ? 'مدیریت آزمون‌ها' : page === 'team' ? 'تیم و دعوت‌ها' : 'پروفایل من'}</b></div>
""",
"team breadcrumb"
)
replace_once(
"""          exams={exams} profile={profile} now={now} onOpen={openExam} onAdmin={() => setPage('admin')}
          isAdmin={isAdmin} isDemo={isDemo} onRefresh={loadMainData}
""",
"""          exams={exams} profile={profile} now={now} onOpen={openExam} onAdmin={() => setPage('admin')}
          isAdmin={isAdmin} isDemo={isDemo} onRefresh={loadMainData}
          myRegistrations={myRegistrations} myTeamRegistrations={myTeamRegistrations}
          team={team} onRegister={registerForExam}
""",
"dashboard props"
)
replace_once(
"""          saving={saving} demo={isDemo} onAnswer={saveAnswer} onBack={() => setPage('dashboard')}
          totalPoints={questionScore}
""",
"""          saving={saving} demo={isDemo} onAnswer={saveAnswer} onBack={() => setPage('dashboard')}
          totalPoints={questionScore} questionResourceUrl={questionResourceUrl} teamMode={Boolean(team && myTeamRegistrations.includes(selectedExam.id))}
""",
"exam props"
)
replace_once(
"""          onCount={changeQuestionCount} onSubmit={createExam} onBack={() => setPage('dashboard')}
        />}
        {page === 'profile' && <ProfilePage profile={profile} email={session?.user.email || (isDemo ? demoUser.email : '')} exams={exams} />}
""",
"""          onCount={changeQuestionCount} onSubmit={createExam} onBack={() => setPage('dashboard')}
          onEditExam={loadExamForEdit} onDeleteExam={deleteExam} onTogglePublish={toggleExamPublish}
          onSetRole={changeUserRole} editingExamId={editingExamId}
          questionPdfUrl={questionPdfUrl} questionFile={questionFile}
          onQuestionPdfUrl={setQuestionPdfUrl} onQuestionFile={setQuestionFile}
        />}
        {page === 'team' && <TeamPage team={team} members={teamMembers} invitations={teamInvitations}
          teamName={teamName} inviteIdentifier={inviteIdentifier} busy={teamBusy}
          onTeamName={setTeamName} onInviteIdentifier={setInviteIdentifier}
          onCreate={createTeam} onInvite={inviteToTeam} onRespond={respondToInvitation} />}
        {page === 'profile' && <ProfilePage profile={profile} email={session?.user.email || (isDemo ? demoUser.email : '')} exams={exams} />}
""",
"admin and team page props"
)

replace_once(
"""function Dashboard({ exams, profile, now, onOpen, onAdmin, isAdmin, isDemo, onRefresh }: {
  exams: Exam[]; profile: Profile | null; now: number; onOpen: (exam: Exam) => void; onAdmin: () => void
  isAdmin: boolean; isDemo: boolean; onRefresh: () => void
}) {""",
"""function Dashboard({ exams, profile, now, onOpen, onAdmin, isAdmin, isDemo, onRefresh, myRegistrations, myTeamRegistrations, team, onRegister }: {
  exams: Exam[]; profile: Profile | null; now: number; onOpen: (exam: Exam) => void; onAdmin: () => void
  isAdmin: boolean; isDemo: boolean; onRefresh: () => void
  myRegistrations: string[]; myTeamRegistrations: string[]; team: Team | null; onRegister: (exam: Exam) => void
}) {""",
"dashboard signature"
)
replace_once(
"""<div className="exam-grid">{visible.map((exam) => <ExamCard key={exam.id} exam={exam} now={now} onOpen={() => onOpen(exam)} />)}</div>""",
"""<div className="exam-grid">{visible.map((exam) => <ExamCard key={exam.id} exam={exam} now={now} onOpen={() => onOpen(exam)}
        registered={myRegistrations.includes(exam.id) || myTeamRegistrations.includes(exam.id)}
        teamMember={Boolean(team)} teamCaptain={team?.role === 'captain'} onRegister={() => onRegister(exam)} />)}</div>""",
"exam cards registration"
)
card_start = source.index("function ExamCard(")
card_end = source.index("\nfunction StatusBadge(", card_start)
source = source[:card_start] + """function ExamCard({ exam, now, onOpen, registered, teamMember, teamCaptain, onRegister }: {
  exam: Exam; now: number; onOpen: () => void; registered: boolean
  teamMember: boolean; teamCaptain: boolean; onRegister: () => void
}) {
  const status = getStatus(exam, now)
  const ended = status === 'ended'
  const active = status === 'active'
  return <article className="exam-card">
    <div className="exam-card-top"><div className={'exam-symbol ' + (active ? 'active' : ended ? 'ended' : '')}><BookOpen size={20} /></div><StatusBadge status={status} /></div>
    <h3>{exam.title}</h3><p className="exam-description">{exam.description || 'برای مشاهده جزئیات این آزمون وارد صفحه آن شوید.'}</p>
    <div className="exam-meta"><div><Clock3 size={15} /><span>{dateText(exam.starts_at)}</span></div><div><Users size={15} /><span>مدت آزمون: {fa(exam.duration_minutes)} دقیقه</span></div></div>
    <div className="exam-registration">
      {registered ? <span className="registration-done"><CheckCircle2 size={15} />ثبت‌نام انجام شده</span>
        : status === 'upcoming' ? (teamMember && !teamCaptain
          ? <span className="registration-hint">ثبت‌نام تیمی با کاپیتان</span>
          : <button className="button soft small" onClick={onRegister}><UserPlus size={15} />{teamMember ? 'ثبت‌نام تیمی' : 'ثبت‌نام در آزمون'}</button>)
        : <span className="registration-hint">برای شرکت باید پیش از شروع ثبت‌نام کنید</span>}
      <button className={'button ' + (active && registered ? 'primary' : 'soft')} disabled={active && !registered} onClick={onOpen}>
        {active ? registered ? 'ورود به آزمون' : 'ثبت‌نام لازم است' : ended ? 'مشاهده نتیجه' : 'جزئیات آزمون'}<ChevronLeft size={16} />
      </button>
    </div>
    <div className="exam-card-bottom"><span>{active ? 'پایان: ' + dateText(examEnd(exam).toISOString()) : ended ? 'زمان آزمون به پایان رسیده' : 'شروع زمان‌بندی‌شده'}</span></div>
  </article>
}
""" + source[card_end:]

replace_once(
"""function ExamPage({ exam, questions, answers, remainingSeconds, status, result, saving, demo, onAnswer, onBack, totalPoints }: {
  exam: Exam; questions: Question[]; answers: Record<number, string>; remainingSeconds: number
  status: 'upcoming' | 'active' | 'ended'; result: ExamResult | null; saving: boolean; demo: boolean
  onAnswer: (n: number, value: string) => void; onBack: () => void; totalPoints: number
}) {""",
"""function ExamPage({ exam, questions, answers, remainingSeconds, status, result, saving, demo, onAnswer, onBack, totalPoints, questionResourceUrl, teamMode }: {
  exam: Exam; questions: Question[]; answers: Record<number, string>; remainingSeconds: number
  status: 'upcoming' | 'active' | 'ended'; result: ExamResult | null; saving: boolean; demo: boolean
  onAnswer: (n: number, value: string) => void; onBack: () => void; totalPoints: number
  questionResourceUrl: string; teamMode: boolean
}) {""",
"exam page signature"
)
replace_once(
"""    <div className="exam-info-grid">
""",
"""    {questionResourceUrl && <a className="question-paper-link" href={questionResourceUrl} target="_blank" rel="noreferrer"><ExternalLink size={17} />دانلود / مشاهده فایل صورت سؤال</a>}
    {teamMode && <div className="team-shared-note"><Users size={16} />این آزمون به‌صورت تیمی است؛ پاسخ‌های ثبت‌شده برای همه اعضای تیم مشترک هستند.</div>}
    <div className="exam-info-grid">
""",
"exam paper resource"
)

admin_start = source.index("function AdminPage(")
admin_end = source.index("\nfunction ProfilePage(", admin_start)
source = source[:admin_start] + """function AdminPage({ title, description, start, duration, questions, busy, exams, results, profiles, onTitle, onDescription, onStart, onDuration, onQuestionChange, onCount, onSubmit, onBack, onEditExam, onDeleteExam, onTogglePublish, onSetRole, editingExamId, questionPdfUrl, questionFile, onQuestionPdfUrl, onQuestionFile }: {
  title: string; description: string; start: string; duration: string; questions: AdminQuestion[]; busy: boolean; exams: Exam[]; results: ExamResult[]; profiles: Profile[]
  onTitle: (v: string) => void; onDescription: (v: string) => void; onStart: (v: string) => void; onDuration: (v: string) => void
  onQuestionChange: (i: number, key: keyof AdminQuestion, value: string) => void; onCount: (v: number) => void
  onSubmit: (e: FormEvent) => void; onBack: () => void
  onEditExam: (exam: Exam) => void; onDeleteExam: (exam: Exam) => void; onTogglePublish: (exam: Exam) => void
  onSetRole: (userId: string, role: 'participant' | 'admin') => void; editingExamId: string | null
  questionPdfUrl: string; questionFile: File | null; onQuestionPdfUrl: (v: string) => void; onQuestionFile: (v: File | null) => void
}) {
  const names = new Map(profiles.map((p) => [p.id, p.full_name] as const))
  return <>
    <div className="backline"><button className="back-button" onClick={onBack}><ArrowLeft size={17} />بازگشت به داشبورد</button><span className="muted small">فقط مدیر سامانه</span></div>
    <div className="page-title-row"><div><div className="eyebrow">پنل مدیریت پیشرفته</div><h1>مدیریت سامانه</h1><p>آزمون‌ها، پاسخ‌نامه‌ها، انتشار، فایل سؤال و سطح دسترسی کاربران را مدیریت کنید.</p></div><div className="admin-mark"><ShieldCheck size={24} /></div></div>
    <div className="admin-layout">
      <section className="panel-card create-panel">
        <div className="panel-title"><div><h2>{editingExamId ? 'ویرایش آزمون' : 'ساخت آزمون جدید'}</h2><p>متن سؤال در صفحه پاسخ‌گویی نمایش داده نمی‌شود.</p></div><span className="private-chip"><ShieldCheck size={14} />پاسخ‌نامه محرمانه</span></div>
        <form onSubmit={onSubmit} className="admin-form">
          <label className="field-label">عنوان آزمون<input value={title} onChange={(e) => onTitle(e.target.value)} placeholder="مثلاً آزمون مرحله اول" required /></label>
          <label className="field-label">توضیحات کوتاه <small>(اختیاری)</small><textarea value={description} onChange={(e) => onDescription(e.target.value)} placeholder="توضیحات یا دستورالعمل آزمون" rows={2} /></label>
          <div className="form-row"><label className="field-label">زمان شروع<input type="datetime-local" value={start} onChange={(e) => onStart(e.target.value)} required /></label><label className="field-label">مدت (دقیقه)<input type="number" min="1" max="600" value={duration} onChange={(e) => onDuration(e.target.value)} /></label></div>
          <div className="question-admin-heading"><div><b>پاسخ‌نامه</b><span>پاسخ صحیح هر سؤال و نمره آن را وارد کنید.</span></div><label className="count-picker">تعداد سؤال <input type="number" min="1" max="100" value={questions.length} onChange={(e) => onCount(Number(e.target.value))} /></label></div>
          <div className="key-table"><div className="key-table-head"><span>شماره</span><span>پاسخ صحیح</span><span>نمره</span></div>{questions.map((q, i) => <div className="key-table-row" key={i}><b>{fa(i + 1)}</b><input aria-label={'پاسخ سؤال ' + (i + 1)} inputMode="decimal" value={q.answer} onChange={(e) => onQuestionChange(i, 'answer', e.target.value)} placeholder="عدد" dir="ltr" /><input aria-label={'نمره سؤال ' + (i + 1)} type="number" min="0.001" step="0.001" value={q.points} onChange={(e) => onQuestionChange(i, 'points', e.target.value)} dir="ltr" /></div>)}</div>
          <label className="field-label">لینک مستقیم PDF صورت سؤال <input type="url" value={questionPdfUrl} onChange={(e) => onQuestionPdfUrl(e.target.value)} placeholder="https://example.com/questions.pdf" dir="ltr" /></label>
          <label className="field-label file-picker"><span><FileUp size={17} />آپلود فایل PDF صورت سؤال</span><input type="file" accept="application/pdf,.pdf" onChange={(e) => onQuestionFile(e.target.files?.[0] || null)} />{questionFile && <small>{questionFile.name}</small>}</label>
          <div className="admin-warning"><ShieldCheck size={17} /><span>فایل آپلودشده در فضای خصوصی ذخیره می‌شود و فقط شرکت‌کنندگان ثبت‌نام‌شده و مدیر به آن دسترسی دارند.</span></div>
          <button className="button primary full" type="submit" disabled={busy}>{busy ? 'در حال ذخیره...' : editingExamId ? 'ذخیره ویرایش آزمون' : 'ساخت و انتشار آزمون'}<Plus size={17} /></button>
        </form>
      </section>
      <aside className="admin-side">
        <div className="panel-card admin-summary"><div className="summary-icon"><BookOpen size={20} /></div><b>{fa(exams.length)} آزمون ثبت‌شده</b><span>مدیریت آزمون‌های منتشرشده و پیش‌رو</span></div>
        <div className="panel-card"><div className="panel-title compact"><div><h2>مدیریت آزمون‌های قبلی</h2><p>ویرایش پاسخ‌نامه، فایل سؤال و وضعیت انتشار</p></div></div>
          <div className="admin-exam-list">{exams.map((exam) => <div className="admin-exam-row" key={exam.id}>
            <div className="admin-exam-copy"><b>{exam.title}</b><small>{dateText(exam.starts_at)} · {exam.is_published ? 'منتشرشده' : 'پیش‌نویس'}</small></div>
            <div className="admin-exam-actions"><button className="icon-button" title="ویرایش آزمون و پاسخ‌ها" onClick={() => onEditExam(exam)}><Pencil size={16} /></button><button className="icon-button" title={exam.is_published ? 'عدم انتشار' : 'انتشار'} onClick={() => onTogglePublish(exam)}><ShieldCheck size={16} /></button><button className="icon-button danger" title="حذف آزمون" onClick={() => onDeleteExam(exam)}><Trash2 size={16} /></button></div>
          </div>)}</div>
        </div>
        <div className="panel-card"><div className="panel-title compact"><div><h2>آخرین نتایج</h2><p>نتایج آزمون‌های تصحیح‌شده</p></div></div>{results.length === 0 ? <div className="mini-empty">هنوز نتیجه‌ای ثبت نشده است.</div> : <div className="result-list">{results.slice(0, 8).map((r) => <div className="result-row" key={r.id}><div className="avatar tiny">{(names.get(r.user_id) || 'ک').slice(0, 1)}</div><div className="result-user"><b>{names.get(r.user_id) || r.user_id.slice(0, 8)}</b><span>{r.team_id ? 'نتیجه تیمی' : 'نتیجه انفرادی'} · {fa(r.correct_count)} پاسخ صحیح</span></div><strong>{fa(r.score)}<small> / {fa(r.max_score)}</small></strong></div>)}</div>}</div>
      </aside>
    </div>
    <section className="panel-card admin-users"><div className="panel-title"><div><h2>مدیریت کاربران</h2><p>تغییر نقش کاربران بین شرکت‌کننده و مدیر</p></div><span className="private-chip"><Users size={14} />{fa(profiles.length)} کاربر</span></div>
      <div className="admin-user-list">{profiles.map((p) => <div className="admin-user-row" key={p.id}><div className="avatar tiny">{(p.full_name || 'ک').slice(0, 1)}</div><div className="admin-exam-copy"><b>{p.full_name}</b><small dir="ltr">@{p.username || '—'}</small></div><span className={p.role === 'admin' ? 'role-pill admin-role' : 'role-pill'}>{p.role === 'admin' ? 'مدیر' : 'شرکت‌کننده'}</span>{p.role === 'admin' ? <button className="button soft small" onClick={() => onSetRole(p.id, 'participant')}>حذف مدیریت</button> : <button className="button soft small" onClick={() => onSetRole(p.id, 'admin')}>ارتقای مدیر</button>}</div>)}</div>
    </section>
  </>
}
""" + source[admin_end:]

replace_once(
"""<div className="profile-data"><h2>{profile?.full_name || 'کاربر'}</h2><p>{email}</p><span className="role-pill">{profile?.role === 'admin' ? 'مدیر سامانه' : 'شرکت‌کننده'}</span></div>""",
"""<div className="profile-data"><h2>{profile?.full_name || 'کاربر'}</h2><p>{email}</p><p dir="ltr">@{profile?.username || '—'}</p><span className="role-pill">{profile?.role === 'admin' ? 'مدیر سامانه' : 'شرکت‌کننده'}</span></div>""",
"profile username"
)

insert_at = source.index("function ProfilePage(")
team_component = """function TeamPage({ team, members, invitations, teamName, inviteIdentifier, busy, onTeamName, onInviteIdentifier, onCreate, onInvite, onRespond }: {
  team: Team | null; members: TeamMember[]; invitations: TeamInvitation[]
  teamName: string; inviteIdentifier: string; busy: boolean
  onTeamName: (v: string) => void; onInviteIdentifier: (v: string) => void
  onCreate: (e: FormEvent) => void; onInvite: (e: FormEvent) => void
  onRespond: (id: string, accept: boolean) => void
}) {
  return <>
    <div className="page-title-row"><div><div className="eyebrow">همکاری گروهی</div><h1>تیم و دعوت‌ها</h1><p>یک تیم چهار نفره بسازید یا دعوت‌نامه عضویت را بپذیرید.</p></div><div className="admin-mark"><Users size={24} /></div></div>
    {team ? <section className="panel-card team-panel">
      <div className="panel-title"><div><h2>{team.name}</h2><p>{team.role === 'captain' ? 'شما کاپیتان تیم هستید.' : 'عضو تیم هستید؛ ثبت‌نام آزمون تیمی با کاپیتان است.'}</p></div><span className="private-chip">{fa(members.length)} از ۴ عضو</span></div>
      <div className="team-member-list">{members.map((member) => <div className="team-member-row" key={member.user_id}><div className="avatar tiny">{member.full_name.slice(0, 1)}</div><div className="admin-exam-copy"><b>{member.full_name}</b><small dir="ltr">@{member.username || '—'}</small></div><span className="role-pill">{member.role === 'captain' ? 'کاپیتان' : 'عضو'}</span></div>)}</div>
      {team.role === 'captain' && members.length < 4 && <form className="team-invite-form" onSubmit={onInvite}><label className="field-label">دعوت با نام کاربری یا ایمیل<input value={inviteIdentifier} onChange={(e) => onInviteIdentifier(e.target.value)} placeholder="username یا email@example.com" dir="ltr" /></label><button className="button primary" disabled={busy || !inviteIdentifier.trim()} type="submit"><UserPlus size={16} />ارسال دعوت</button></form>}
      {team.role === 'captain' && <p className="muted small">هر تیم حداکثر یک کاپیتان و سه عضو دیگر دارد. پس از ثبت‌نام تیم در آزمون پیش‌رو، ترکیب اعضا تا پایان آزمون ثابت می‌ماند.</p>}
    </section> : <section className="panel-card team-panel">
      <div className="panel-title"><div><h2>هنوز عضو تیمی نیستید</h2><p>می‌توانید یک تیم بسازید یا یکی از دعوت‌نامه‌ها را بپذیرید.</p></div></div>
      <form className="team-create-form" onSubmit={onCreate}><label className="field-label">نام تیم<input value={teamName} onChange={(e) => onTeamName(e.target.value)} placeholder="مثلاً تیم ترکیبیات" maxLength={40} /></label><button className="button primary" disabled={busy || teamName.trim().length < 2} type="submit"><Users size={16} />ساخت تیم و کاپیتان شدن</button></form>
    </section>}
    <section className="panel-card team-panel"><div className="panel-title"><div><h2>دعوت‌نامه‌های دریافتی</h2><p>برای عضویت در تیم، دعوت‌نامه باید پذیرفته شود.</p></div></div>
      {invitations.length === 0 ? <div className="mini-empty">دعوت‌نامه فعالی ندارید.</div> : <div className="team-member-list">{invitations.map((inv) => <div className="team-member-row" key={inv.id}><div className="admin-exam-copy"><b>{inv.teams?.name || 'تیم جدید'}</b><small>{dateText(inv.created_at)}</small></div><div className="team-invitation-actions"><button className="button primary small" onClick={() => onRespond(inv.id, true)}>پذیرفتن</button><button className="button soft small" onClick={() => onRespond(inv.id, false)}>رد کردن</button></div></div>)}</div>}
    </section>
  </>
}

"""
source = source[:insert_at] + team_component + source[insert_at:]

css_path = Path("src/style.css")
css = css_path.read_text(encoding="utf-8")
css += """

/* Team registration and expanded administration */
.exam-registration { display:flex; align-items:center; justify-content:space-between; gap:10px; flex-wrap:wrap; margin-top:14px; }
.exam-card-bottom { margin-top:10px; }
.registration-done,.registration-hint { display:inline-flex; align-items:center; gap:6px; color:var(--muted); font-size:11px; }
.registration-done { color:#20a477; }
.exam-registration .button.small { padding:8px 11px; font-size:11px; }
.question-paper-link,.team-shared-note { display:flex; align-items:center; gap:9px; border:1px solid var(--line); background:var(--panel); border-radius:12px; padding:13px 15px; margin:14px 0; color:var(--text); text-decoration:none; font-size:13px; }
.question-paper-link { color:var(--accent); }
.team-shared-note { color:var(--muted); }
.team-panel,.admin-users { margin:18px 0; padding:22px; }
.team-member-list,.admin-exam-list,.admin-user-list { display:flex; flex-direction:column; gap:0; }
.team-member-row,.admin-exam-row,.admin-user-row { display:flex; align-items:center; gap:12px; padding:12px 0; border-bottom:1px solid var(--line); }
.team-member-row:last-child,.admin-exam-row:last-child,.admin-user-row:last-child { border-bottom:0; }
.admin-exam-copy { display:flex; flex:1; min-width:0; flex-direction:column; gap:4px; }
.admin-exam-copy b { font-size:13px; }
.admin-exam-copy small { color:var(--muted); font-size:11px; }
.admin-exam-actions,.team-invitation-actions { display:flex; align-items:center; gap:6px; }
.admin-exam-actions .icon-button { width:32px; height:32px; }
.admin-exam-actions .danger { color:#dc6262; }
.team-create-form,.team-invite-form { display:flex; align-items:flex-end; gap:12px; margin-top:18px; }
.team-create-form .field-label,.team-invite-form .field-label { flex:1; }
.file-picker { display:flex; flex-direction:column; gap:9px; border:1px dashed var(--line); padding:13px; border-radius:12px; }
.file-picker span { display:flex; align-items:center; gap:8px; }
.file-picker input { max-width:100%; }
.file-picker small { color:var(--muted); }
.admin-role { background:rgba(126,103,245,.14); }
.admin-user-row .role-pill { margin-inline-start:auto; }
@media (max-width:640px) {
 .team-create-form,.team-invite-form { flex-direction:column; align-items:stretch; }
 .admin-user-row { flex-wrap:wrap; }
 .admin-user-row .role-pill { margin-inline-start:0; }
 .exam-registration { align-items:stretch; }
}
"""
css_path.write_text(css, encoding="utf-8")
path.write_text(source, encoding="utf-8")
print("Applied FarsiJudge teams, registration, admin editing and question-resource UI.")
