from pathlib import Path

p = Path("src/App.tsx")
s = p.read_text(encoding="utf-8")

def once(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(label + ": expected one anchor, got " + str(n))
    s = s.replace(old, new, 1)

# Designer is a distinct profile role and can manage only contests it owns.
s = s.replace("role: 'participant' | 'admin'; username?: string", "role: 'participant' | 'designer' | 'admin'; username?: string")
s = s.replace("type Page = 'dashboard' | 'exam' | 'admin' | 'profile' | 'team'", "type Page = 'dashboard' | 'exam' | 'admin' | 'profile' | 'team' | 'leaderboard' | 'public-questions'")
s = s.replace("  is_published: boolean\n  question_pdf_url?: string | null", "  is_published: boolean\n  created_by?: string | null\n  end_at_override?: string | null\n  question_pdf_url?: string | null")
s = s.replace("select('id,title,description,starts_at,duration_minutes,is_published,created_at')", "select('id,title,description,starts_at,duration_minutes,is_published,created_at,created_by,end_at_override')")

m = __import__("re").search(r"^(\s*)const isAdmin\s*=.*$", s, __import__("re").M)
if not m:
    raise SystemExit("Could not locate isAdmin")
indent = m.group(1)
s = s[:m.end()] + "\n" + indent + "const isDesigner = profile?.role === 'designer'\n" + indent + "const canManageContests = isAdmin || isDesigner" + s[m.end():]

s = s.replace("const changeUserRole = async (userId: string, role: 'participant' | 'admin') => {", "const changeUserRole = async (userId: string, role: 'participant' | 'designer' | 'admin') => {")
s = s.replace("onSetRole: (userId: string, role: 'participant' | 'admin') => void", "onSetRole: (userId: string, role: 'participant' | 'designer' | 'admin') => void")
s = s.replace("supabase.rpc('edit_exam_with_answer_key', {", "supabase.rpc(isDesigner && !isAdmin ? 'designer_edit_exam_with_answer_key' : 'edit_exam_with_answer_key', {")
s = s.replace("supabase.rpc('create_exam_with_answer_key', {", "supabase.rpc(isDesigner && !isAdmin ? 'designer_create_exam_with_answer_key' : 'create_exam_with_answer_key', {")
s = s.replace("supabase.rpc('set_exam_question_resource', {", "supabase.rpc(isDesigner && !isAdmin ? 'designer_set_exam_question_resource' : 'set_exam_question_resource', {")
s = s.replace("supabase.rpc('get_exam_question_resource', { p_exam_id: exam.id })", "supabase.rpc(isDesigner && !isAdmin ? 'get_designer_exam_question_resource' : 'get_exam_question_resource', { p_exam_id: exam.id })")

once(
    "{isAdmin && <button className={page === 'admin' ? 'nav-item selected' : 'nav-item'} onClick={() => setPage('admin')}><ShieldCheck size={19} />مدیریت مسابقه‌ها</button>}",
    "{canManageContests && <button className={page === 'admin' ? 'nav-item selected' : 'nav-item'} onClick={() => setPage('admin')}><ShieldCheck size={19} />{isAdmin ? 'مدیریت مسابقه‌ها' : 'طراحی مسابقه'}</button>}",
    "designer navigation"
)

# Admin page receives a mode so designers never see global user controls.
s = s.replace(
    "onQuestionPdfUrl, onQuestionFile }: {",
    "onQuestionPdfUrl, onQuestionFile, designerMode }: {"
)
s = s.replace(
    "onQuestionFile: (v: File | null) => void\n}) {",
    "onQuestionFile: (v: File | null) => void; designerMode: boolean\n}) {"
)
s = s.replace(
    "<section className=\"panel-card admin-users\"><div className=\"panel-title\"><div><h2>مدیریت کاربران</h2><p>تغییر نقش کاربران بین شرکت‌کننده و مدیر</p></div>",
    "{!designerMode && <section className=\"panel-card admin-users\"><div className=\"panel-title\"><div><h2>مدیریت کاربران</h2><p>تغییر نقش کاربران بین شرکت‌کننده، طراح و مدیر</p></div>"
)
s = s.replace(
    """<span className={p.role === 'admin' ? 'role-pill admin-role' : 'role-pill'}>{p.role === 'admin' ? 'مدیر' : 'شرکت‌کننده'}</span>{p.role === 'admin' ? <button className="button soft small" onClick={() => onSetRole(p.id, 'participant')}>حذف مدیریت</button> : <button className="button soft small" onClick={() => onSetRole(p.id, 'admin')}>ارتقای مدیر</button>}""",
    """<span className={p.role === 'admin' ? 'role-pill admin-role' : p.role === 'designer' ? 'role-pill designer-role' : 'role-pill'}>{p.role === 'admin' ? 'مدیر' : p.role === 'designer' ? 'طراح مسابقه' : 'شرکت‌کننده'}</span>
          {p.role !== 'participant' && <button className="button soft small" onClick={() => onSetRole(p.id, 'participant')}>بازگرداندن به شرکت‌کننده</button>}
          {p.role === 'participant' && <button className="button soft small" onClick={() => onSetRole(p.id, 'designer')}>تبدیل به طراح</button>}
          {p.role !== 'admin' && <button className="button soft small" onClick={() => onSetRole(p.id, 'admin')}>ارتقای مدیر</button>}"""
)
# Close the designer-only conditional.
s = s.replace(
    "</div></div>\n    </section>\n  </>\n}\n\nfunction TeamPage",
    "</div></div>\n    </section>}\n  </>\n}\n\nfunction TeamPage",
    1
)

# Designers edit only their own contests, and do not receive the global user/results lists.
s = s.replace(
    "exams={exams} results={results} profiles={profiles}",
    "exams={isDesigner && !isAdmin ? exams.filter((exam) => exam.created_by === session?.user.id) : exams} results={isDesigner && !isAdmin ? [] : results} profiles={isDesigner && !isAdmin ? [] : profiles}",
    1
)
s = s.replace(
    "onQuestionPdfUrl={setQuestionPdfUrl} onQuestionFile={setQuestionFile}",
    "onQuestionPdfUrl={setQuestionPdfUrl} onQuestionFile={setQuestionFile} designerMode={isDesigner && !isAdmin}",
    1
)
s = s.replace("page === 'admin' && isAdmin", "page === 'admin' && canManageContests")

# The main dashboard create button is shared by admins and designers.
s = s.replace("isAdmin={isAdmin} isDemo={isDemo} onRefresh={loadMainData}", "isAdmin={canManageContests} isDemo={isDemo} onRefresh={loadMainData}", 1)

s = s.replace("profile?.role === 'admin' ? 'مدیر سامانه' : 'شرکت‌کننده'", "profile?.role === 'admin' ? 'مدیر سامانه' : profile?.role === 'designer' ? 'طراح مسابقه' : 'شرکت‌کننده'")
p.write_text(s, encoding="utf-8")

# The existing admin-file loader also supports a designer's own contest resources.
f = Path("src/App.tsx")
s = f.read_text(encoding="utf-8")
s = s.replace("client.rpc('get_exam_question_resource', { p_exam_id: exam.id })", "client.rpc(isDesigner && !isAdmin ? 'get_designer_exam_question_resource' : 'get_exam_question_resource', { p_exam_id: exam.id })")
f.write_text(s, encoding="utf-8")

cssp = Path("src/style.css")
css = cssp.read_text(encoding="utf-8")
css += """
.designer-role { color:#8d68e8; background:rgba(141,104,232,.12); }
"""
cssp.write_text(css, encoding="utf-8")
print("Applied designer role and owner-scoped contest management UI.")
