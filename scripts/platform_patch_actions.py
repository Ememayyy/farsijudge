from pathlib import Path
p=Path("src/App.tsx")
s=p.read_text(encoding="utf-8")
def once(a,b):
 global s
 if s.count(a)!=1: raise SystemExit("Patch anchor mismatch: "+a[:70])
 s=s.replace(a,b,1)
once("  const changeUserRole = async (userId: string, role: 'participant' | 'admin') => {","""  const deleteUser = async (userId: string) => {
    if (!supabase || !window.confirm('حساب این کاربر و داده‌های وابسته حذف شود؟ این کار برگشت‌پذیر نیست.')) return
    const { error } = await supabase.rpc('admin_delete_user', { p_user_id: userId })
    if (error) notify('حذف کاربر ناموفق بود: '+error.message,'error')
    else { notify('کاربر حذف شد.','success'); await loadMainData(); const {data}=await supabase.from('profiles').select('id,full_name,role,username'); if(data)setProfiles(data as Profile[]) }
  }
  const changeUserRole = async (userId: string, role: 'participant' | 'admin') => {""")
once("onSetRole={changeUserRole} editingExamId={editingExamId}","onSetRole={changeUserRole} onDeleteUser={deleteUser} editingExamId={editingExamId}")
once("onSetRole, editingExamId, questionPdfUrl","onSetRole, onDeleteUser, editingExamId, questionPdfUrl")
once("onSetRole: (userId: string, role: 'participant' | 'admin') => void; editingExamId","onSetRole: (userId: string, role: 'participant' | 'admin') => void; onDeleteUser: (userId: string) => void; editingExamId")
once("<button className=\"button soft small\" onClick={() => onSetRole(p.id, 'admin')}>ارتقای مدیر</button>","<button className=\"button soft small\" onClick={() => onSetRole(p.id, 'admin')}>ارتقای مدیر</button><button className='button soft small danger-text' onClick={() => onDeleteUser(p.id)}>حذف کاربر</button>")
once("  const createTeam = async (event: FormEvent) => {","""  const leaveTeam = async () => {
    if (!supabase || !window.confirm('از تیم فعلی خارج می‌شوید؟')) return
    const { error } = await supabase.rpc('leave_team')
    if (error) notify('خروج از تیم ناموفق بود: '+error.message,'error')
    else { notify('از تیم خارج شدید.','success'); await loadMainData() }
  }

  const createTeam = async (event: FormEvent) => {""")
once("onRespond={respondToInvitation} />","onRespond={respondToInvitation} onLeave={leaveTeam} />")
once("onCreate, onInvite, onRespond }: {","onCreate, onInvite, onRespond, onLeave }: {")
once("onRespond: (id: string, accept: boolean) => void\n}) {","onRespond: (id: string, accept: boolean) => void; onLeave: () => void\n}) {")
once("      {team.role === 'captain' && members.length < 4","      <div className='team-leave-row'><span className='muted small'>با خروج کاپیتان، مسئولیت کاپیتانی طبق ترتیب اعضا منتقل می‌شود.</span><button className='button soft small danger-text' onClick={onLeave}>ترک تیم</button></div>\n      {team.role === 'captain' && members.length < 4")
once("<Users size={19} />تیم و دعوت‌ها</button>","<Users size={19} />تیم و دعوت‌ها{teamInvitations.length>0 && <span className='team-notification-badge'>{fa(teamInvitations.length)}</span>}</button>")
once("""    {questionResourceUrl && <a className="question-paper-link" href={questionResourceUrl} target="_blank" rel="noreferrer"><ExternalLink size={17} />دانلود / مشاهده فایل صورت سؤال</a>}""","""    {questionResourceUrl && <a className="question-paper-link" href={questionResourceUrl} target="_blank" rel="noreferrer"><ExternalLink size={17} />دانلود / مشاهده فایل صورت سؤال</a>}
    {questionResourceUrl && <div className="paper-preview"><div>پیش‌نمایش صورت مسابقه <a href={questionResourceUrl} target="_blank" rel="noreferrer">باز کردن در صفحه جدید</a></div><iframe src={questionResourceUrl} title="صورت مسابقه" loading="lazy" /></div>}""")
once("""    <div className="exam-info-grid">""","""    {status === 'upcoming' && <div className="start-countdown"><b>زمان باقی‌مانده تا شروع مسابقه</b><span>{fa(Math.max(0, Math.ceil((new Date(exam.starts_at).getTime() - Date.now()) / 1000)))} ثانیه</span></div>}
    <div className="exam-info-grid">""")
p.write_text(s,encoding="utf-8")
c=Path("src/style.css")
c.write_text(c.read_text(encoding="utf-8")+"\n.team-leave-row{display:flex;justify-content:space-between;align-items:center;gap:12px;padding-top:14px;margin-top:12px;border-top:1px solid var(--line)}.danger-text{color:#e45e70!important}.team-notification-badge{display:inline-flex;min-width:19px;height:19px;align-items:center;justify-content:center;margin-inline-start:auto;padding:0 6px;border-radius:20px;background:#e94f68;color:white;font-size:10px;font-weight:800}@media(max-width:640px){.team-leave-row{flex-direction:column;align-items:stretch}}",encoding="utf-8")
print("Team leave and invite badge integrated.")
