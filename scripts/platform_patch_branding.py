from pathlib import Path
import re

app_path = Path("src/App.tsx")
source = app_path.read_text(encoding="utf-8")
logo_src = "{import.meta.env.BASE_URL + 'fj-logo.svg'}"

# Keep every place that displays the brand connected to the same vector asset.
source = source.replace("farsijudge-logo.webp", "fj-logo.svg")
source = source.replace("src={brandLogo}", "src=" + logo_src)

source, generic_marks = re.subn(
    r'(<span className="brand-mark">\s*)<(?:BookOpen|GraduationCap)\b[^>]*/>(\s*</span>)',
    lambda m: m.group(1) + '<img src=' + logo_src + ' alt="FJ" />' + m.group(2),
    source,
)
source, public_marks = re.subn(
    r'(<span className="public-brand-mark">\s*)<(?:BookOpen|GraduationCap)\b[^>]*/>(\s*</span>)',
    lambda m: m.group(1) + '<img src=' + logo_src + ' alt="فارسی جاج" />' + m.group(2),
    source,
)

# Preserve the legacy data-URL declaration without leaving an unused-local error.
if re.search(r"\bbrandLogo\b", source) and "src={brandLogo}" not in source:
    source += chr(10) + "void brandLogo;" + chr(10)

app_path.write_text(source, encoding="utf-8")

css_path = Path("src/style.css")
css = css_path.read_text(encoding="utf-8")
css += """
 
/* FarsiJudge unified algorithmic FJ identity. */
.redesign-shell .brand-mark,
.welcome-shell .brand-mark,
.public-brand-mark,
.mobile-appbar-brand .brand-mark {
  display: inline-grid;
  place-items: center;
  overflow: hidden;
  flex: 0 0 auto;
  background: linear-gradient(145deg, #9a75ff, #6443c8);
}
.redesign-shell .brand-mark img,
.welcome-shell .brand-mark img,
.public-brand-mark img,
.mobile-appbar-brand .brand-mark img {
  display: block;
  width: 100%;
  height: 100%;
  padding: 2px;
  box-sizing: border-box;
  object-fit: contain;
  border-radius: inherit;
}
.public-brand-mark {
  padding: 3px;
}
.topbar-brand .brand-mark {
  overflow: hidden;
}
.topbar-brand .brand-mark img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 1px;
  box-sizing: border-box;
}
"""
css_path.write_text(css, encoding="utf-8")

print(
    "Applied FJ logo replacements: "
    + str(generic_marks) + " app/welcome marks, "
    + str(public_marks) + " public marks."
)
