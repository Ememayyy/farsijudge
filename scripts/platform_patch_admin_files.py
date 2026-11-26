from pathlib import Path

app_path = Path("src/App.tsx")
app = app_path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global app
    count = app.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    app = app.replace(old, new, 1)


# Load each exam's private resource metadata for the administrator's exam list.
# Storage files stay private; only short-lived signed URLs are exposed to admins.
admin_resource_hooks = """  const [examResources, setExamResources] = useState<Record<string, {
    questionPdfUrl: string; filePath: string; fileName: string; signedUrl: string; error: string
  }>>({})
  const [examResourcesLoading, setExamResourcesLoading] = useState(false)
  const [editingFilePreviewUrl, setEditingFilePreviewUrl] = useState('')

  useEffect(() => {
    const client = supabase
    if (!client) return
    let alive = true

    if (exams.length === 0) {
      setExamResources({})
      setExamResourcesLoading(false)
      return
    }

    setExamResourcesLoading(true)
    const loadResources = async () => {
      const entries = await Promise.all(exams.map(async (exam) => {
        try {
          const { data, error } = await client.rpc('get_exam_question_resource', { p_exam_id: exam.id })
          if (error) {
            return [exam.id, {
              questionPdfUrl: '', filePath: '', fileName: '', signedUrl: '', error: error.message
            }] as const
          }

          const resource = (Array.isArray(data) ? data[0] : data) as {
            question_pdf_url?: string | null; question_file_path?: string | null
          } | null
          const filePath = resource?.question_file_path || ''
          const fileName = filePath ? filePath.split('/').pop() || 'question.pdf' : ''
          let signedUrl = ''
          let fileError = ''

          if (filePath) {
            const { data: fileData, error: signedError } = await client.storage
              .from('exam-question-files')
              .createSignedUrl(filePath, 3600)
            if (signedError) fileError = signedError.message
            else signedUrl = fileData?.signedUrl || ''
          }

          return [exam.id, {
            questionPdfUrl: resource?.question_pdf_url || '',
            filePath,
            fileName,
            signedUrl,
            error: fileError,
          }] as const
        } catch (cause) {
          return [exam.id, {
            questionPdfUrl: '', filePath: '', fileName: '', signedUrl: '',
            error: cause instanceof Error ? cause.message : String(cause),
          }] as const
        }
      }))

      if (!alive) return
      setExamResources(Object.fromEntries(entries))
      setExamResourcesLoading(false)
    }

    void loadResources()
    return () => { alive = false }
  }, [exams])

  // Refresh the private file URL when an administrator opens an exam for editing.
  // This avoids relying on an older signed URL that may have expired in the list.
  useEffect(() => {
    const client = supabase
    const filePath = editingExamId ? examResources[editingExamId]?.filePath : ''
    if (!client || !filePath) {
      setEditingFilePreviewUrl('')
      return
    }

    let alive = true
    setEditingFilePreviewUrl('')
    const refreshPreview = async () => {
      const { data, error } = await client.storage
        .from('exam-question-files')
        .createSignedUrl(filePath, 3600)
      if (alive) setEditingFilePreviewUrl(error ? '' : data?.signedUrl || '')
    }
    void refreshPreview()
    return () => { alive = false }
  }, [editingExamId, examResources])

  const editingResource = editingExamId ? examResources[editingExamId] : undefined
  const hasEditingResource = Boolean(editingResource?.filePath || editingResource?.questionPdfUrl || questionPdfUrl)
"""
replace_once(
    """  const names = new Map(profiles.map((p) => [p.id, p.full_name] as const))
  return <>""",
    admin_resource_hooks + """
  const names = new Map(profiles.map((p) => [p.id, p.full_name] as const))
  return <>""",
    "admin file resource loading hooks"
)

# Show both uploaded private PDFs and externally linked PDFs beside each exam.
exam_row_old = """            <div className="admin-exam-copy"><b>{exam.title}</b><small>{dateText(exam.starts_at)} · {exam.is_published ? 'منتشرشده' : 'پیش‌نویس'}</small></div>"""
exam_row_new = """            <div className="admin-exam-copy">
              <b>{exam.title}</b>
              <small>{dateText(exam.starts_at)} · {exam.is_published ? 'منتشرشده' : 'پیش‌نویس'}</small>
              <div className="admin-exam-files">
                {examResourcesLoading && !examResources[exam.id] && <span className="admin-file-muted">در حال بررسی فایل‌ها...</span>}
                {examResources[exam.id]?.filePath && examResources[exam.id]?.signedUrl && <a href={examResources[exam.id].signedUrl} target="_blank" rel="noreferrer"><FileUp size={13} />{examResources[exam.id].fileName || 'مشاهده فایل PDF'}</a>}
                {examResources[exam.id]?.filePath && !examResources[exam.id]?.signedUrl && <span className="admin-file-muted">{examResources[exam.id].fileName || 'فایل PDF'} · لینک موقت در دسترس نیست</span>}
                {examResources[exam.id]?.questionPdfUrl && <a href={examResources[exam.id].questionPdfUrl} target="_blank" rel="noreferrer"><ExternalLink size={13} />لینک PDF</a>}
                {examResources[exam.id]?.error && <span className="admin-file-error">خطای دریافت فایل: {examResources[exam.id].error}</span>}
                {!examResourcesLoading && examResources[exam.id] && !examResources[exam.id].filePath && !examResources[exam.id].questionPdfUrl && !examResources[exam.id].error && <span className="admin-file-muted">فایلی برای این آزمون ثبت نشده است.</span>}
              </div>
            </div>"""
replace_once(exam_row_old, exam_row_new, "admin exam list file links")

# In edit mode, show the currently saved upload and embed a PDF preview.
file_picker_anchor = """          <label className="field-label file-picker"><span><FileUp size={17} />آپلود فایل PDF صورت سؤال</span><input type="file" accept="application/pdf,.pdf" onChange={(e) => onQuestionFile(e.target.files?.[0] || null)} />{questionFile && <small>{questionFile.name}</small>}</label>
          <div className="admin-warning">"""
file_picker_replacement = """          <label className="field-label file-picker"><span><FileUp size={17} />آپلود فایل PDF صورت سؤال</span><input type="file" accept="application/pdf,.pdf" onChange={(e) => onQuestionFile(e.target.files?.[0] || null)} />{questionFile && <small>{questionFile.name}</small>}</label>
          {editingExamId && <section className="admin-current-files">
            <div className="admin-current-files-heading"><b>فایل‌های فعلی این آزمون</b><span>فایل ذخیره‌شده تا زمان جایگزینی حفظ می‌شود.</span></div>
            {!hasEditingResource && <div className="admin-file-muted">هنوز فایلی برای این آزمون ثبت نشده است.</div>}
            {editingResource?.filePath && <div className="admin-current-file">
              <div className="admin-current-file-meta"><FileUp size={17} /><span>{editingResource.fileName || 'فایل PDF بارگذاری‌شده'}</span>
                {editingFilePreviewUrl && <a href={editingFilePreviewUrl} target="_blank" rel="noreferrer">باز کردن فایل</a>}
              </div>
              {editingFilePreviewUrl ? <iframe src={editingFilePreviewUrl} title="پیش‌نمایش فایل ذخیره‌شدهٔ آزمون" loading="lazy" /> : <small className="admin-file-muted">در حال آماده‌سازی پیش‌نمایش فایل...</small>}
            </div>}
            {(questionPdfUrl || editingResource?.questionPdfUrl) && <a className="admin-current-external-link" href={questionPdfUrl || editingResource?.questionPdfUrl || ''} target="_blank" rel="noreferrer"><ExternalLink size={15} />باز کردن PDF از لینک ثبت‌شده</a>}
            {editingResource?.error && <div className="admin-file-error">ساخت لینک امن فایل ممکن نشد: {editingResource.error}</div>}
          </section>}
          <div className="admin-warning">"""
replace_once(file_picker_anchor, file_picker_replacement, "existing uploaded file preview in edit form")

app_path.write_text(app, encoding="utf-8")

css_path = Path("src/style.css")
css = css_path.read_text(encoding="utf-8")
css += """

/* Admin exam resource visibility: private PDFs are opened through short-lived signed URLs. */
.admin-exam-files {
  display:flex;
  flex-wrap:wrap;
  align-items:center;
  gap:6px 12px;
  margin-top:7px;
  min-width:0;
}
.admin-exam-files a,
.admin-current-external-link {
  display:inline-flex;
  align-items:center;
  gap:5px;
  width:fit-content;
  color:var(--accent);
  font-size:10px;
  font-weight:800;
  text-decoration:none;
}
.admin-exam-files a:hover,
.admin-current-external-link:hover { text-decoration:underline; }
.admin-file-muted { color:var(--muted); font-size:10px; line-height:1.8; }
.admin-file-error { color:#c85b65; font-size:10px; line-height:1.8; overflow-wrap:anywhere; }
.admin-current-files {
  display:flex;
  flex-direction:column;
  gap:12px;
  padding:15px;
  border:1px solid var(--line);
  border-radius:14px;
  background:var(--panel);
}
.admin-current-files-heading { display:flex; flex-direction:column; gap:4px; }
.admin-current-files-heading b { color:var(--text); font-size:12px; }
.admin-current-files-heading span { color:var(--muted); font-size:10px; }
.admin-current-file { display:flex; flex-direction:column; gap:10px; min-width:0; }
.admin-current-file-meta {
  display:flex;
  align-items:center;
  flex-wrap:wrap;
  gap:8px;
  color:var(--text);
  font-size:11px;
}
.admin-current-file-meta > span { min-width:0; flex:1; overflow-wrap:anywhere; }
.admin-current-file-meta a {
  color:var(--accent);
  font-size:10px;
  font-weight:800;
  text-decoration:none;
}
.admin-current-file iframe {
  width:100%;
  height:440px;
  border:1px solid var(--line);
  border-radius:10px;
  background:#fff;
}
@media(max-width:640px) {
  .admin-current-files { padding:11px; }
  .admin-current-file iframe { height:320px; }
  .admin-exam-files { gap:5px 9px; }
}
"""
css_path.write_text(css, encoding="utf-8")
print("Added private uploaded-file links in admin exam list and a saved-file PDF preview in edit mode.")
