from pathlib import Path

app_path = Path("src/App.tsx")
app = app_path.read_text(encoding="utf-8")

# The product name and competition terminology.
app = app.replace("آزمون‌یار", "فارسی جاج")
app = app.replace("آزمون ها", "مسابقه‌ها")
app = app.replace("آزمون‌ها", "مسابقه‌ها")
app = app.replace("آزمون", "مسابقه")

# Team capacity is four people total, including the captain. Keep the
# interface aligned with the database migration 009.
app = app.replace("members.length < 3", "members.length < 4")
app = app.replace("از ۳ عضو", "از ۴ عضو")
app = app.replace("از 3 عضو", "از 4 عضو")
app = app.replace("یک تیم سه‌نفره", "یک تیم چهار نفره")
app = app.replace("یک تیم سه نفره", "یک تیم چهار نفره")
app = app.replace("یک تیم ۳ نفره", "یک تیم ۴ نفره")
app = app.replace("دو عضو دیگر", "سه عضو دیگر")
app = app.replace("دو عضو به‌علاوه کاپیتان", "سه عضو به‌جز کاپیتان")
app = app.replace("هر تیم حداکثر سه نفر با احتساب کاپیتان دارد", "هر تیم حداکثر چهار نفر با احتساب کاپیتان دارد")

app_path.write_text(app, encoding="utf-8")

css_path = Path("src/style.css")
css = css_path.read_text(encoding="utf-8")
css += r"""

/* Farsi-Judge visual foundation */
:root {
  --bg: #08080b;
  --panel: #111116;
  --panel-2: #191920;
  --panel-3: #24232c;
  --text: #f5f2f8;
  --muted: #a29dab;
  --line: rgba(255,255,255,.09);
}
:root[data-theme="light"] {
  --bg: #f3f4f7;
  --panel: #ffffff;
  --panel-2: #f8f9fc;
  --panel-3: #eceef4;
  --text: #252b38;
  --muted: #687386;
  --line: rgba(40,52,80,.12);
}
.exam-card, .panel-card, .team-panel, .admin-panel {
  border-radius: 14px;
}
.nav-badge, .team-notification-badge {
  display: inline-flex;
  min-width: 19px;
  height: 19px;
  align-items: center;
  justify-content: center;
  margin-inline-start: auto;
  padding: 0 6px;
  border-radius: 20px;
  background: #e94f68;
  color: white;
  font-size: 10px;
  font-weight: 800;
}
.registration-options {
  display: grid;
  grid-template-columns: repeat(2,minmax(0,1fr));
  gap: 12px;
}
.registration-options button {
  min-height: 100px;
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--panel);
  color: var(--text);
  text-align: right;
}
.registration-options button.selected {
  border-color: #986cff;
  background: rgba(152,108,255,.10);
}
.registration-options button:disabled { opacity: .45; cursor: not-allowed; }
.contest-topic-tags, .admin-tag-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.contest-topic-tags span, .admin-tag-picker button {
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 5px 9px;
  background: var(--panel-2);
  color: var(--muted);
  font-size: 10px;
}
.start-countdown, .team-live-banner, .paper-preview {
  margin: 12px 0;
  padding: 14px;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--panel);
}
.paper-preview iframe {
  display: block;
  width: 100%;
  height: min(70vh, 680px);
  margin-top: 12px;
  border: 0;
  border-radius: 10px;
  background: white;
}
.paper-preview a { color: #9a70ff; font-size: 12px; }
.review-row {
  display: grid;
  grid-template-columns: auto 1fr 1fr auto;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--panel);
}
.review-row.correct { border-inline-start: 3px solid #24b88a; }
.review-row.wrong { border-inline-start: 3px solid #ee5a73; }
.fj-cookie-banner {
  position: fixed;
  z-index: 1000;
  inset-inline: 12px;
  bottom: 12px;
  max-width: 720px;
  margin-inline: auto;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--panel);
  box-shadow: 0 16px 50px rgba(0,0,0,.22);
}
@media(max-width:760px) {
  .registration-options { grid-template-columns: 1fr; }
  .review-row { grid-template-columns: auto 1fr; }
  .paper-preview iframe { height: 58vh; }
  .fj-cookie-banner { flex-wrap: wrap; }
}
"""
css_path.write_text(css, encoding="utf-8")
print("Applied Farsi-Judge language, team-size and responsive style patch.")
