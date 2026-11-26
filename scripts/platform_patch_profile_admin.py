from pathlib import Path

p = Path("src/App.tsx")
s = p.read_text(encoding="utf-8")

def once(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(label + ": expected one anchor, got " + str(n))
    s = s.replace(old, new, 1)

# Add display-name and password forms to the existing profile page.
if "ProfileSettings profile={profile}" not in s:
    import re
    profile_render = re.search(r"<ProfilePage\\b[^>]*/>", s)
    if not profile_render:
        raise SystemExit("ProfilePage JSX element not found")
    tag = profile_render.group(0)
    s = s[:profile_render.end()] + "<ProfileSettings profile={profile} />" + s[profile_render.end():]

profile_component = """
function ProfileSettings({ profile }: { profile: Profile | null }) {
  const [displayName, setDisplayName] = useState(profile?.full_name || '')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [nameBusy, setNameBusy] = useState(false)
  const [passwordBusy, setPasswordBusy] = useState(false)

  useEffect(() => { setDisplayName(profile?.full_name || '') }, [profile?.full_name])

  const saveDisplayName = async (event: FormEvent) => {
    event.preventDefault()
    if (!supabase || nameBusy) return
    if (displayName.trim().length < 2 || displayName.trim().length > 60) {
      window.alert('نام نمایشی باید بین ۲ تا ۶۰ نویسه باشد.')
      return
    }
    setNameBusy(true)
    const { error } = await supabase.rpc('update_my_display_name', { p_full_name: displayName.trim() })
    setNameBusy(false)
    if (error) window.alert('ذخیره نام نمایشی ناموفق بود: ' + error.message)
    else window.location.reload()
  }

  const savePassword = async (event: FormEvent) => {
    event.preventDefault()
    if (!supabase || passwordBusy) return
    if (newPassword.length < 8) {
      window.alert('رمز عبور باید حداقل ۸ نویسه داشته باشد.')
      return
    }
    if (newPassword !== confirmPassword) {
      window.alert('تکرار رمز عبور با رمز جدید یکسان نیست.')
      return
    }
    setPasswordBusy(true)
    const { error } = await supabase.auth.updateUser({ password: newPassword })
    setPasswordBusy(false)
    if (error) window.alert('تغییر رمز عبور ناموفق بود: ' + error.message)
    else {
      setNewPassword('')
      setConfirmPassword('')
      window.alert('رمز عبور با موفقیت تغییر کرد.')
    }
  }

  return <section className="panel-card profile-settings">
    <div className="panel-title"><div><h2>تنظیمات حساب</h2><p>نام نمایشی و رمز عبور خود را به‌روزرسانی کن.</p></div></div>
    <form className="profile-settings-form" onSubmit={saveDisplayName}>
      <label className="field-label">نام نمایشی<input value={displayName} onChange={(event) => setDisplayName(event.target.value)} minLength={2} maxLength={60} /></label>
      <button className="button primary" type="submit" disabled={nameBusy || displayName.trim() === (profile?.full_name || '')}>{nameBusy ? 'در حال ذخیره...' : 'ذخیره نام نمایشی'}</button>
    </form>
    <form className="profile-settings-form password-form" onSubmit={savePassword}>
      <label className="field-label">رمز عبور جدید<input type="password" autoComplete="new-password" value={newPassword} onChange={(event) => setNewPassword(event.target.value)} minLength={8} placeholder="حداقل ۸ نویسه" /></label>
      <label className="field-label">تکرار رمز عبور<input type="password" autoComplete="new-password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} minLength={8} placeholder="تکرار رمز جدید" /></label>
      <button className="button soft" type="submit" disabled={passwordBusy || !newPassword || !confirmPassword}>{passwordBusy ? 'در حال تغییر...' : 'تغییر رمز عبور'}</button>
    </form>
  </section>
}

"""
if s.count("function ProfilePage(") != 1:
    raise SystemExit("ProfilePage insertion point mismatch")
s = s.replace("function ProfilePage(", profile_component + "function ProfilePage(", 1)

# Make contest management searchable and filterable by schedule status.
once(
    "  const names = new Map(profiles.map((p) => [p.id, p.full_name] as const))\n  return <>",
    """  const names = new Map(profiles.map((p) => [p.id, p.full_name] as const))
  const [adminExamSearch, setAdminExamSearch] = useState('')
  const [adminExamFilter, setAdminExamFilter] = useState<'all' | 'upcoming' | 'active' | 'ended'>('all')
  const visibleAdminExams = exams.filter((exam) => {
    const status = getStatus(exam, Date.now())
    return (adminExamFilter === 'all' || status === adminExamFilter)
      && (exam.title + ' ' + (exam.description || '')).toLowerCase().includes(adminExamSearch.trim().toLowerCase())
  }).sort((a, b) => new Date(b.starts_at).getTime() - new Date(a.starts_at).getTime())
  return <>""",
    "admin exam search state"
)
once(
    "          <div className=\"admin-exam-list\">{exams.map((exam) => <div className=\"admin-exam-row\"",
    """          <div className="admin-exam-tools">
            <input aria-label="جست‌وجوی مسابقه" value={adminExamSearch} onChange={(event) => setAdminExamSearch(event.target.value)} placeholder="جست‌وجوی عنوان مسابقه..." />
            <select aria-label="فیلتر وضعیت مسابقه" value={adminExamFilter} onChange={(event) => setAdminExamFilter(event.target.value as 'all' | 'upcoming' | 'active' | 'ended')}>
              <option value="all">همهٔ وضعیت‌ها</option><option value="upcoming">پیش‌رو</option><option value="active">در حال برگزاری</option><option value="ended">پایان‌یافته</option>
            </select>
            <span>{fa(visibleAdminExams.length)} مسابقه</span>
          </div>
          <div className="admin-exam-list">{visibleAdminExams.map((exam) => <div className="admin-exam-row" """.replace('className="admin-exam-row" "', 'className="admin-exam-row" '),
    "admin exam search controls"
)

p.write_text(s, encoding="utf-8")

cssp = Path("src/style.css")
css = cssp.read_text(encoding="utf-8")
css += """
.profile-settings { margin-top:16px; padding:20px; }
.profile-settings-form { display:grid; grid-template-columns:minmax(0,1fr) auto; align-items:end; gap:12px; margin-top:14px; }
.profile-settings-form.password-form { grid-template-columns:repeat(2,minmax(0,1fr)) auto; padding-top:15px; border-top:1px solid var(--line); }
.profile-settings-form .field-label { min-width:0; }
.admin-exam-tools { display:flex; align-items:center; gap:9px; flex-wrap:wrap; margin:12px 0; }
.admin-exam-tools input,.admin-exam-tools select {
  min-width:0; flex:1; min-height:40px; padding:8px 11px; border:1px solid var(--line);
  border-radius:10px; background:var(--panel-2); color:var(--text); font:inherit; font-size:11px;
}
.admin-exam-tools span { color:var(--muted); font-size:10px; white-space:nowrap; }
@media(max-width:700px) {
  .profile-settings-form,.profile-settings-form.password-form { grid-template-columns:1fr; }
  .profile-settings-form .button { width:100%; justify-content:center; }
  .admin-exam-tools { flex-direction:column; align-items:stretch; }
}
"""
cssp.write_text(css, encoding="utf-8")
print("Added profile editing and admin contest search/filter controls.")
