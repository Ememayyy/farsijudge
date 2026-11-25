from pathlib import Path
p=Path("src/App.tsx")
s=p.read_text(encoding="utf-8")
def rep(a,b,label):
 global s
 n=s.count(a)
 if n!=1: raise SystemExit(f"{label}: expected 1 match, got {n}")
 s=s.replace(a,b,1)

rep("""  const changeUserRole = async (userId: string, role: 'participant' | 'admin') => {""","""  const leaveTeam = async () => {
    if (!supabase || !window.confirm('از تیم فعلی خارج می‌شوید. ادامه می‌دهید؟')) return
    const { error } = await supabase.rpc('leave_team')
    if (error) notify('خروج از تیم ناموفق بود: ' + error.message, 'error')
    else { notify('از تیم خارج شدید.', 'success'); await loadMainData() }
  }
  const deleteUser = async (userId: string) => {
    if (!supabase || !window.confirm('حساب این کاربر و داده‌های وابسته حذف شود؟ این کار برگشت‌پذیر نیست.')) return
    const { error } = await supabase.rpc('admin_delete_user', { p_user_id: userId })
    if (error) notify('حذف کاربر ناموفق بود: ' + error.message, 'error')
    else { notify('کاربر حذف شد.', 'success'); await loadMainData(); const {data}=await supabase.from('profiles').select('id,full_name,role,username'); if(data)setProfiles(data as Profile[]) }
  }
  const changeUserRole = async (userId: string, role: 'participant' | 'admin') => {""","handlers")
rep("""onSetRole={changeUserRole} editingExamId={editingExamId}""","""onSetRole={changeUserRole} onDeleteUser={deleteUser} editingExamId={editingExamId}""","admin prop")
rep("""onCreate={createTeam} onInvite={inviteToTeam} onRespond={respondToInvitation} />""","""onCreate={createTeam} onInvite={inviteToTeam} onRespond={respondToInvitation} onLeave={leaveTeam} />""","team prop")
rep("""<Users size={19} />تیم و دعوت‌ها</button>""","""<Users size={19} />تیم و دعوت‌ها{teamInvitations.length>0 && <span className="team-notification-badge">{fa(teamInvitations.length)}</span>}</button>""","invite badge")
rep("""onSetRole, editingExamId, questionPdfUrl""","""onSetRole, onDeleteUser, editingExamId, questionPdfUrl""","admin destructure")
rep("""onSetRole: (userId: string, role: 'participant' | 'admin') => void; editingExamId""","""onSetRole: (userId: string, role: 'participant' | 'admin') => void; onDeleteUser: (userId: string) => void; editingExamId""","admin prop type")
rep("""onSetRole(p.id, 'admin')}>ارتقای مدیر</button>}</div>)}</div>""","""onSetRole(p.id, 'admin')}>ارتقای مدیر</button>}<button className="button soft small danger-text" onClick={() => onDeleteUser(p.id)}>حذف کاربر</button></div>)}</div>""","delete user button")
rep("""onCreate, onInvite, onRespond }: {""","""onCreate, onInvite, onRespond, onLeave }: {""","team destructure")
rep("""onRespond: (id: string, accept: boolean) => void
}) {""","""onRespond: (id: string, accept: boolean) => void; onLeave: () => void
}) {""","team prop type")
rep("""</div>
      {team.role === 'captain' && members.length < 4""","""</div>
      <div className="team-leave-row"><span className="muted small">با خروج کاپیتان، دیتابیس مسئولیت کاپیتانی را به عضو بعدی منتقل می‌کند.</span><button className="button soft small danger-text" onClick={onLeave}>ترک تیم</button></div>
      {team.role === 'captain' && members.length < 4""","leave team UI")
s=s.replace("یک تیم چهار نفره بسازید","یک تیم سه‌نفره بسازید").replace("از ۴ عضو","از ۳ عضو").replace("سه عضو دیگر","دو عضو دیگر")
p.write_text(s,encoding="utf-8")
css=Path("src/style.css")
css.write_text(css.read_text(encoding="utf-8")+"""
.team-leave-row{display:flex;align-items:center;justify-content:space-between;gap:12px;padding-top:14px;margin-top:12px;border-top:1px solid var(--line)}
.danger-text{color:#e45e70!important}
.team-notification-badge{display:inline-flex;min-width:19px;height:19px;align-items:center;justify-content:center;margin-inline-start:auto;padding:0 6px;border-radius:20px;background:#e94f68;color:white;font-size:10px;font-weight:800}
@media(max-width:640px){.team-leave-row{align-items:stretch;flex-direction:column}}
""",encoding="utf-8")
print("Extra team and admin actions patched.")
