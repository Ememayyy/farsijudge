from pathlib import Path

p = Path("src/App.tsx")
s = p.read_text(encoding="utf-8")

# Global interface terminology and brand.
s = s.replace("آزمون‌یار", "فارسی جاج").replace("آزمون", "مسابقه")
s = s.replace("members.length < 4", "members.length < 3")
s = s.replace("از ۴ عضو", "از ۳ عضو")
s = s.replace("یک تیم چهار نفره", "یک تیم سه‌نفره")
s = s.replace("سه عضو دیگر", "دو عضو دیگر")
s = s.replace("حداکثر ۴ عضو", "حداکثر ۳ عضو")

p.write_text(s, encoding="utf-8")
print("Applied Farsi-Judge naming and three-member team labels.")


p = Path("src/App.tsx")
s = p.read_text(encoding="utf-8")

def rep(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(label + ": expected one match, got " + str(n))
    s = s.replace(old, new, 1)

# A member may leave. The database transfers the captain role safely.
rep(
"  const createTeam = async (event: FormEvent) => {",
"""  const leaveTeam = async () => {
    if (!supabase || !window.confirm('از تیم خارج می‌شوید؟ در صورت کاپیتان بودن، مسئولیت به قدیمی‌ترین عضو منتقل می‌شود.')) return
    const { error } = await supabase.rpc('leave_team')
    if (error) notify(error.message, 'error')
    else { notify('از تیم خارج شدید.', 'success'); await loadMainData() }
  }

  const createTeam = async (event: FormEvent) => {""",
"leave-team handler")

rep(
"onCreate={createTeam} onInvite={inviteToTeam} onRespond={respondToInvitation} />}",
"onCreate={createTeam} onInvite={inviteToTeam} onRespond={respondToInvitation} onLeave={leaveTeam} />}",
"TeamPage leave callback")

rep(
"onInvite, onRespond }: {",
"onInvite, onRespond, onLeave }: {",
"TeamPage callback signature")
rep(
"  onRespond: (id: string, accept: boolean) => void\n}) {",
"  onRespond: (id: string, accept: boolean) => void; onLeave: () => void\n}) {",
"TeamPage leave type")

rep(
"      {team.role === 'captain' && <p className=\"muted small\">هر تیم حداکثر یک کاپیتان و دو عضو دیگر دارد.",
"      <button className=\"danger-link\" onClick={onLeave}>ترک تیم <LogOut size={15}/></button>\n      {team.role === 'captain' && <p className=\"muted small\">هر تیم حداکثر سه نفر با احتساب کاپیتان دارد.",
"leave button and capacity text")

# Incoming membership requests get a red notification badge.
rep(
"""<button className={page === 'team' ? 'nav-item selected' : 'nav-item'} onClick={() => setPage('team')}><Users size={19} />تیم و دعوت‌ها</button>""",
"""<button className={page === 'team' ? 'nav-item selected' : 'nav-item'} onClick={() => setPage('team')}><Users size={19} />تیم‌ها{teamInvitations.length > 0 && <b className="nav-badge">{fa(teamInvitations.length)}</b>}</button>""",
"team notification badge")

# The UI permits a member to choose an individual entry; only the captain can select team entry.
rep(
"""        : status === 'upcoming' ? (teamMember && !teamCaptain
          ? <span className="registration-hint">ثبت‌نام تیمی با کاپیتان</span>
          : <button className="button soft small" onClick={onRegister}><UserPlus size={15} />{teamMember ? 'ثبت‌نام تیمی' : 'ثبت‌نام در مسابقه'}</button>)""",
"""        : status === 'upcoming' ? <button className="button soft small" onClick={onRegister}><UserPlus size={15}/>{teamMember && !teamCaptain ? 'ثبت‌نام انفرادی' : 'انتخاب نوع ثبت‌نام'}</button>""",
"individual registration for team member")

# Replace immediate registration with a separate choice screen.
const oldReg = """  const registerForExam = async (exam: Exam) => {
    if (!supabase) return
    if (team && team.role !== 'captain') return notify('برای ثبت‌نام تیمی، از کاپیتان تیم بخواهید اقدام کند.', 'info')
    const { error } = await supabase.rpc('register_for_exam', {
      p_exam_id: exam.id,
      p_team_id: team?.id ?? null,
    })
    if (error) notify('ثبت‌نام انجام نشد: ' + error.message, 'error')
    else {
      notify('ثبت‌نام انجام شد.', 'success')
      await loadMainData()
    }
  }
"""
const newReg = """  const registerForExam = async (exam: Exam) => {
    setSelectedExam(exam)
    setRegistrationKind(team?.role === 'captain' ? 'team' : 'individual')
    setPage('registerExam')
  }

  const confirmRegistration = async () => {
    if (!supabase || !selectedExam) return
    if (registrationKind === 'team' && (!team || team.role !== 'captain')) return notify('ثبت‌نام تیمی فقط توسط کاپیتان امکان‌پذیر است.', 'error')
    setTeamBusy(true)
    const { error } = await supabase.rpc('register_for_exam', {
      p_exam_id: selectedExam.id,
      p_team_id: registrationKind === 'team' ? team!.id : null,
    })
    if (error) notify(error.message, 'error')
    else { notify('ثبت‌نام انجام شد.', 'success'); await loadMainData(); setPage('dashboard') }
    setTeamBusy(false)
  }
"""
rep(oldReg, newReg, "dedicated registration flow")

rep(
"  const [authUsername, setAuthUsername] = useState('')",
"""  const [authUsername, setAuthUsername] = useState('')
  const [registrationKind, setRegistrationKind] = useState<'individual' | 'team'>('individual')""",
"registration kind state")

rep(
"""        {page === 'team' && <TeamPage team={team} members={teamMembers} invitations={teamInvitations}""",
"""        {page === 'registerExam' && selectedExam && <section className="registration-screen">
          <div className="eyebrow">ثبت‌نام مسابقه</div><h1>{selectedExam.title}</h1>
          <p>نوع شرکت را انتخاب کنید. ثبت‌نام تیمی فقط توسط کاپیتان ممکن است.</p>
          <div className="registration-options">
            <button className={registrationKind === 'individual' ? 'chosen' : ''} onClick={() => setRegistrationKind('individual')}><UserRound/><b>شرکت انفرادی</b><small>ثبت‌نام با حساب شخصی شما</small></button>
            <button disabled={!team || team.role !== 'captain'} className={registrationKind === 'team' ? 'chosen' : ''} onClick={() => setRegistrationKind('team')}><Users/><b>شرکت تیمی</b><small>{team?.role === 'captain' ? 'ثبت‌نام تیم ' + team.name : 'فقط کاپیتان می‌تواند تیم را ثبت‌نام کند'}</small></button>
          </div>
          <div className="registration-summary"><span>زمان شروع</span><b>{dateText(selectedExam.starts_at)}</b><span>ظرفیت تیم</span><b>۳ نفر با احتساب کاپیتان</b></div>
          <button className="button primary full" disabled={teamBusy || (registrationKind === 'team' && team?.role !== 'captain')} onClick={confirmRegistration}>تأیید و ثبت‌نام <ChevronLeft/></button>
          <button className="text-link" onClick={() => setPage('dashboard')}>بازگشت</button>
        </section>}
        {page === 'team' && <TeamPage team={team} members={teamMembers} invitations={teamInvitations}""",
"registration page")

p.write_text(s, encoding="utf-8")
