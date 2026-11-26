from pathlib import Path
import io
import json
import cairosvg
from PIL import Image

app_path = Path("src/App.tsx")
source = app_path.read_text(encoding="utf-8")

def once(old: str, new: str, label: str) -> None:
    global source
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    source = source.replace(old, new, 1)

# If the extended contest columns are not installed yet, still load the core
# contest fields instead of leaving the dashboard empty.
once(
    "supabase.from('exams').select('id,title,description,starts_at,duration_minutes,is_published,end_at_override,allow_late_registration,registration_closes_at,results_release_at,announcement,tags,created_at').order('starts_at', { ascending: false }),",
    """(async () => {
        const extended = await supabase.from('exams')
          .select('id,title,description,starts_at,duration_minutes,is_published,end_at_override,allow_late_registration,registration_closes_at,results_release_at,announcement,tags,created_at')
          .order('starts_at', { ascending: false })
        if (!extended.error) return extended
        return await supabase.from('exams')
          .select('id,title,description,starts_at,duration_minutes,is_published,created_at')
          .order('starts_at', { ascending: false })
      })(),""",
    "contest query fallback"
)

once(
    """      const { data } = await client.rpc('get_public_contests')
      if (alive && data) setExams(data as Exam[])""",
    """      const { data, error } = await client.rpc('get_public_contests')
      if (!error && Array.isArray(data) && data.length > 0) {
        if (alive) setExams(data as Exam[])
        return
      }
      const fallback = await client.from('exams')
        .select('id,title,description,starts_at,duration_minutes,is_published,created_at')
        .eq('is_published', true)
        .order('starts_at', { ascending: true })
      if (alive && fallback.data) setExams(fallback.data as Exam[])""",
    "public contest feed fallback"
)

# Use the same site logo in the public header and mobile app bar.
once(
    '<span className="public-brand-mark"><BookOpen size={23} /></span>',
    '<span className="public-brand-mark"><img src={import.meta.env.BASE_URL + \'fj-logo.svg\'} alt="فارسی جاج" /></span>',
    "public site logo"
)
once(
    '<div className="mobile-appbar-brand"><span className="brand-mark"><BookOpen size={20} /></span><b>فارسی جاج</b></div>',
    '<div className="mobile-appbar-brand"><span className="brand-mark mobile-brand-mark"><img src={import.meta.env.BASE_URL + \'fj-logo.svg\'} alt="" /></span><b>فارسی جاج</b></div>',
    "mobile app bar logo"
)

# Remove the dashboard refresh action and its now-unused prop.
once(
    '          <button className="button ghost" onClick={onRefresh}><RefreshCw size={16} />به‌روزرسانی</button>\n',
    '',
    "dashboard refresh button"
)
once(
    'isDemo={isDemo} onRefresh={loadMainData}',
    'isDemo={isDemo}',
    "dashboard refresh prop"
)
once(
    'isDemo, onRefresh, myRegistrations',
    'isDemo, myRegistrations',
    "dashboard refresh parameter"
)
once(
    'isDemo: boolean; onRefresh: () => void',
    'isDemo: boolean;',
    "dashboard refresh prop type"
)
once(
    'LayoutDashboard, LogOut, Moon, Plus, RefreshCw, ShieldCheck,',
    'LayoutDashboard, LogOut, Moon, Plus, ShieldCheck,',
    "unused refresh icon import"
)

# Make the empty state explain whether there are no contests or the filter
# simply has no matches.
once(
    """{filtered.length === 0 ? <div className="dashboard-empty"><span className="empty-graphic"><Search size={25} /></span><b>چیزی برای نمایش پیدا نشد</b><p>عبارت جست‌وجو یا فیلتر را تغییر بده.</p></div>""",
    """{filtered.length === 0 ? <div className="dashboard-empty"><span className="empty-graphic"><Search size={25} /></span><b>{exams.length === 0 ? 'هنوز مسابقه‌ای برای نمایش وجود ندارد' : 'چیزی برای نمایش پیدا نشد'}</b><p>{exams.length === 0 ? 'مسابقه‌های منتشرشده پس از بارگذاری در این بخش قرار می‌گیرند.' : 'عبارت جست‌وجو یا فیلتر را تغییر بده.'}</p></div>""",
    "contest empty state"
)

app_path.write_text(source, encoding="utf-8")

# Visual refinements and mobile layout corrections.
css_path = Path("src/style.css")
css = css_path.read_text(encoding="utf-8")
css += """

/* Farsi Judge polish: fixed mobile controls, logo-forward identity and calmer dashboard */
.public-brand-mark { overflow:hidden; padding:3px; }
.public-brand-mark img { display:block; width:100%; height:100%; object-fit:contain; border-radius:inherit; }
.mobile-appbar-brand .mobile-brand-mark { overflow:hidden; padding:3px; background:linear-gradient(145deg,#9a75ff,#6443c8); }
.mobile-appbar-brand .mobile-brand-mark img { display:block; width:100%; height:100%; object-fit:contain; border-radius:inherit; }

@media(max-width:900px) {
  .redesign-shell .mobile-appbar {
    position:fixed;
    z-index:80;
    top:0;
    right:0;
    left:0;
    width:100%;
    height:calc(58px + env(safe-area-inset-top, 0px));
    padding-top:env(safe-area-inset-top, 0px);
  }
  .redesign-shell .main-area {
    padding-top:calc(58px + env(safe-area-inset-top, 0px));
  }
  .redesign-shell .topbar {
    top:calc(58px + env(safe-area-inset-top, 0px));
  }
  .redesign-shell .sidebar {
    top:calc(58px + env(safe-area-inset-top, 0px));
    z-index:70;
  }
  .redesign-shell.sidebar-open .sidebar-scrim {
    inset:calc(58px + env(safe-area-inset-top, 0px)) 0 0;
    z-index:65;
  }
}

.dashboard-metrics,
.dashboard-bottom-grid { display:none !important; }
.dashboard-hero { margin-bottom:17px; }
.dashboard-list-panel { margin-top:0; }
.dashboard-list-heading h2 { display:flex; align-items:center; gap:9px; }
.dashboard-list-heading h2::before {
  content:"";
  display:inline-block;
  width:5px;
  height:21px;
  border-radius:5px;
  background:linear-gradient(180deg,#b69bff,#7040d5);
}
.dashboard-list-panel .exam-card { border-radius:16px; }
.dashboard-filter { min-height:36px; }
.dashboard-search { min-height:40px; }
.dashboard-next-card { min-width:0; }
.public-contest-table td:first-child b { display:block; }
.public-contest-table td:first-child small {
  display:block;
  max-width:420px;
  margin-top:4px;
  overflow:hidden;
  color:var(--muted);
  font-size:10px;
  text-overflow:ellipsis;
  white-space:nowrap;
}

@media(max-width:640px) {
  .public-table-wrap { overflow-x:visible; }
  .public-contest-table { width:100%; min-width:0; }
  .public-contest-table thead { display:none; }
  .public-contest-table tbody tr {
    display:grid;
    grid-template-columns:minmax(0,1fr) minmax(0,1fr);
    gap:9px 12px;
    padding:13px 0;
    border-bottom:1px solid var(--line);
  }
  .public-contest-table tbody td { display:block; min-width:0; padding:0; border:0; font-size:10px; }
  .public-contest-table tbody td:first-child { grid-column:1/-1; }
  .public-contest-table tbody td:last-child { justify-self:end; align-self:end; }
  .public-contest-table tbody td:first-child small { white-space:normal; line-height:1.7; }
  .public-contest-table tbody td[colspan] { grid-column:1/-1; }
  .public-contest-table tbody td[colspan] .public-empty { padding:22px 8px; }
  .public-table-footer { align-items:flex-start; flex-direction:column; gap:9px; }
  .dashboard-hero { gap:15px; }
  .dashboard-next-card { padding:15px; }
  .dashboard-list-panel .dashboard-filter-row { gap:5px; }
  .dashboard-filter { padding:7px 9px; font-size:9px; }
  .dashboard-total-label { width:100%; margin:3px 0 0; }
  .redesign-shell .page-content { padding-top:16px; }
}
"""

css_path.write_text(css, encoding="utf-8")

# Make the site installable and use the same Farsi Judge artwork for the
# browser tab and the home-screen icon on iOS/Android.
public = Path("public")
public.mkdir(exist_ok=True)
logo_path = public / "fj-logo.svg"
if not logo_path.exists():
    raise SystemExit("PWA logo source public/fj-logo.svg is missing")

logo_png = cairosvg.svg2png(url=str(logo_path), output_width=768, output_height=768)
logo = Image.open(io.BytesIO(logo_png)).convert("RGBA")
for size in (180, 192, 512):
    canvas = Image.new("RGBA", (size, size), (11, 11, 16, 255))
    mark = logo.copy()
    mark.thumbnail((int(size * 0.84), int(size * 0.84)), Image.Resampling.LANCZOS)
    canvas.alpha_composite(mark, ((size - mark.width) // 2, (size - mark.height) // 2))
    canvas.save(public / f"farsijudge-logo-{size}.png", format="PNG", optimize=True)

manifest = {
    "id": "./",
    "name": "فارسی جاج",
    "short_name": "فارسی‌جاج",
    "description": "سامانهٔ برگزاری مسابقه‌های آنلاین فارسی جاج",
    "lang": "fa",
    "dir": "rtl",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "background_color": "#0b0b10",
    "theme_color": "#7040d5",
    "icons": [
        {"src": "./farsijudge-logo-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "./farsijudge-logo-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}
    ]
}
(public / "manifest.webmanifest").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8"
)

(public / "sw.js").write_text("""const CACHE_NAME = 'farsi-judge-shell-v1';
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.add('./'))
      .then(() => self.skipWaiting())
  );
});
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET' || event.request.mode !== 'navigate') return;
  event.respondWith(
    fetch(event.request).then((response) => {
      const copy = response.clone();
      caches.open(CACHE_NAME).then((cache) => cache.put('./', copy));
      return response;
    }).catch(() => caches.match('./'))
  );
});
""", encoding="utf-8")

index_path = Path("index.html")
html = index_path.read_text(encoding="utf-8")
head_assets = """  <meta name="application-name" content="فارسی جاج">
  <meta name="apple-mobile-web-app-title" content="فارسی جاج">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">
  <meta name="theme-color" content="#7040d5">
  <link rel="icon" type="image/png" sizes="192x192" href="./farsijudge-logo-192.png">
  <link rel="apple-touch-icon" sizes="180x180" href="./farsijudge-logo-180.png">
  <link rel="manifest" href="./manifest.webmanifest">
"""
if 'rel="manifest"' not in html:
    if "</head>" not in html:
        raise SystemExit("Could not find </head> in index.html")
    html = html.replace("</head>", head_assets + "</head>", 1)
if "navigator.serviceWorker.register('./sw.js')" not in html:
    worker_registration = """  <script>
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('./sw.js', { scope: './' }).catch(() => {});
      });
    }
  </script>
"""
    if "</body>" not in html:
        raise SystemExit("Could not find </body> in index.html")
    html = html.replace("</body>", worker_registration + "</body>", 1)
# Replace the obsolete root-scoped WebP favicon after all source index edits.
# The vector logo is shipped by the build and works under the GitHub Pages base path.
html = html.replace(
    '<link rel="icon" type="image/webp" href="/farsijudge/farsijudge-logo.webp" />',
    '<link rel="icon" type="image/svg+xml" href="./fj-logo.svg" />',
)
html = html.replace("/farsijudge/farsijudge-logo.webp", "./fj-logo.svg")
index_path.write_text(html, encoding="utf-8")

print("Applied mobile/dashboard/contest and PWA polish.")
