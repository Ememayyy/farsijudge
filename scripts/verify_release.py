#!/usr/bin/env python3
"""Static release checks for FarsiJudge's built frontend and SQL contracts."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path("farsijudge")
DIST = ROOT / "dist"
APP = ROOT / "src" / "App.tsx"
MIGRATIONS = ROOT / "supabase" / "migrations"
BASE_PATH = os.environ.get("VITE_BASE_PATH", "./")
if not BASE_PATH.endswith("/"):
    BASE_PATH += "/"

errors: list[str] = []
checks = 0


def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        errors.append(message)


class AssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        for key in ("src", "href"):
            value = values.get(key)
            if value:
                self.refs.append(value)


def is_external(value: str) -> bool:
    parsed = urlsplit(value)
    return bool(parsed.scheme or parsed.netloc) or value.startswith(("#", "data:", "blob:"))


def check_asset(ref: str, origin: str, base_dir: Path = DIST) -> None:
    value = unquote(urlsplit(ref).path)
    if not value or is_external(ref):
        return
    if value.startswith("/"):
        if not value.startswith(BASE_PATH):
            errors.append(f"{origin}: absolute asset is outside the configured base path: {ref}")
            return
        candidate = DIST / value[len(BASE_PATH):]
    else:
        candidate = base_dir / value
    candidate = candidate.resolve()
    try:
        candidate.relative_to(DIST.resolve())
    except ValueError:
        errors.append(f"{origin}: asset escapes the deployment directory: {ref}")
        return
    check(candidate.is_file(), f"{origin}: referenced file does not exist: {ref} -> {candidate}")


check(DIST.is_dir(), "Build output directory farsijudge/dist is missing.")
index_path = DIST / "index.html"
manifest_path = DIST / "manifest.webmanifest"
check(index_path.is_file(), "Built index.html is missing.")
check(manifest_path.is_file(), "Built manifest.webmanifest is missing.")
check((DIST / "sw.js").is_file(), "Service worker sw.js is missing.")

if index_path.is_file():
    html = index_path.read_text(encoding="utf-8")
    parser = AssetParser()
    parser.feed(html)
    for ref in parser.refs:
        check_asset(ref, "index.html")
    check("farsijudge-logo.webp" not in html, "index.html still refers to the missing farsijudge-logo.webp.")
    check("fj-logo.svg" in html, "index.html does not use the available FJ SVG favicon.")

if manifest_path.is_file():
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for item in manifest.get("icons", []):
            if item.get("src"):
                check_asset(item["src"], "manifest.webmanifest")
        check(manifest.get("start_url") in ("./", BASE_PATH, BASE_PATH.rstrip("/")), "PWA start_url is not scoped to the deployed app.")
        check(manifest.get("scope") in ("./", BASE_PATH, BASE_PATH.rstrip("/")), "PWA scope is not scoped to the deployed app.")
    except (json.JSONDecodeError, OSError) as exc:
        errors.append(f"manifest.webmanifest could not be parsed: {exc}")

for css_path in (DIST / "assets").glob("*.css"):
    css = css_path.read_text(encoding="utf-8")
    for match in re.finditer(r"url\(\s*['\"]?([^'\"\)]+)", css):
        check_asset(match.group(1).strip(), css_path.name, css_path.parent)

js_files = sorted((DIST / "assets").glob("*.js"))
check(bool(js_files), "No built JavaScript bundle was found.")
bundle = "\n".join(path.read_text(encoding="utf-8") for path in js_files)
for required in (
    "get_public_exam_leaderboard",
    "get_public_exam_questions",
    "get_public_exam_question_resource",
    "designer_create_exam_with_answer_key",
    "designer_edit_exam_with_answer_key",
    "designer_update_contest_controls",
    "get_my_team_pending_invitation_count",
    "update_my_display_name",
):
    check(required in bundle, f"Built frontend is missing expected RPC contract: {required}")

for js_path in js_files:
    result = subprocess.run(
        ["node", "--check", str(js_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    check(result.returncode == 0, f"JavaScript syntax check failed for {js_path.name}: {result.stderr.strip()}")

if APP.is_file():
    app = APP.read_text(encoding="utf-8")
    check("team.role === 'captain' && members.length + pendingInvitationCount < 4" in app,
          "Team invitation UI must count pending invitations toward its four-person capacity.")
    check("از ۴ عضو" in app or "از 4 عضو" in app, "Team capacity label does not advertise four people.")
    check(not re.search(r"team\.role\s*===\s*['\"]captain['\"]\s*&&\s*members\.length\s*<\s*3", app),
          "A stale three-person team limit remains in the UI.")
    check("team.role === 'captain' && members.length < 4" not in app,
          "Team invitation UI still ignores pending invitations.")
    check("onSetRole(p.id, 'designer')" in app, "Administrator UI is missing the control to assign designer role.")
    check("طراح مسابقه" in app, "Designer role label is missing from the administrator UI.")
    check("setPage((current) => current === 'auth' ? 'dashboard' : current)" in app,
          "Auth listener must not reset the current route when a session is refreshed.")
    check("setSelectedPublicExam" in app and "page === 'public-questions'" in app and "page === 'leaderboard'" in app,
          "Public review pages must use the top-level route state.")
    check("farsijudge-route" in app and "routeSnapshotReady" in app,
          "Active route and selected contest must survive tab suspension or reload.")
    check("current === 'welcome' || current === 'auth' ? 'dashboard' : current" in app,
          "Session hydration must not overwrite a restored in-app route.")
    check("onReviewQuestions(exam)" in app and "onLeaderboard(exam)" in app,
          "Public review buttons must navigate through the root route callbacks.")
    check("function ContestTagList(" in app and "function getContestTagTone(" in app,
          "Colored contest tag rendering is missing.")
    check("oj-contest-row" in app and ".oj-contest-row" in (ROOT / "src" / "style.css").read_text(encoding="utf-8"), "Contest directory rows are missing their new layout styling.")
    full_redesign_css = (ROOT / "src" / "style.css").read_text(encoding="utf-8")
    for layout_contract in (".oj-public-home", ".oj-public-header", ".oj-dashboard", ".oj-contest-row", ".oj-app-shell .sidebar", ".auth-shell", ".oj-app-shell .exam-heading-panel", "@media(max-width:700px)"):
        check(layout_contract in full_redesign_css, f"Full redesign responsive layout is missing: {layout_contract}.")
    for content_contract in ("CONTEST WORKSPACE", "فهرست مسابقه‌ها", "مسابقه‌های عمومی", "مسابقهٔ پیش‌رو"):
        check(content_contract in app, f"Full redesign content contract is missing: {content_contract}.")
    mobile_css = full_redesign_css[full_redesign_css.find("FJ MOBILE-FIRST NAVIGATION v3"):]
    check(bool(mobile_css), "Final mobile-first overrides are missing.")
    for mobile_contract in (
        ".oj-app-shell.sidebar-open .sidebar",
        ".oj-app-shell .mobile-signout-button",
        ".oj-app-shell .sidebar-scrim",
        "overflow-y:auto !important",
        "grid-template-columns:minmax(0,1fr) !important",
        "font-size:16px !important",
    ):
        check(mobile_contract in mobile_css, f"Mobile usability contract is missing: {mobile_contract}.")
    check('.oj-app-shell .topbar button:has(svg.lucide-sun)' in mobile_css,
          "The extra theme control in the mobile topbar must be hidden.")
    check('.oj-app-shell .topbar button:has(svg.lucide-moon)' in mobile_css,
          "The extra theme control in the mobile topbar must be hidden for both themes.")
    check('<div className="oj-hero-live-count">{fa(ended.length)}<span>مسابقهٔ برگزارشده</span></div>' in app,
          "The public homepage hero must show the completed contest count.")
    check('<div className="oj-hero-live-count">{fa(active.length)}<span>مسابقهٔ فعال</span></div>' not in app,
          "The public homepage hero still shows the active contest count.")
    check("mobile-signout-button" in app and "await supabase.auth.signOut()" in app,
          "The mobile app bar must provide a direct sign-out action.")
    check("aria-expanded={sidebarOpen}" in app and "setSidebarOpen((open) => !open)" in app,
          "The mobile drawer toggle must expose and toggle its open state.")
    check("window.addEventListener('keydown', closeOnEscape)" in app,
          "The mobile drawer must be dismissible with Escape.")
    check(full_redesign_css.rfind("FJ MOBILE-FIRST NAVIGATION v3") > full_redesign_css.find("FJ SECOND GENERATION"),
          "Mobile-first overrides must be appended after the desktop layout rules.")
    for visual_contract in (
        "FARSIJUDGE VISUAL SYSTEM",
        ".public-hero h1",
        ".auth-visual-content h1",
        ".dashboard-hero",
        ".redesign-shell .exam-info-grid",
        "@media (prefers-reduced-motion: reduce)",
    ):
        check(visual_contract in (ROOT / "src" / "style.css").read_text(encoding="utf-8"),
              f"Visual refresh contract is missing: {visual_contract}.")
    check("فکر کن. حل کن." in app and "رتبه‌ات را بساز." in app, "The new contest hub headline is missing.")
    check('className="auth-visual"' not in app and 'className="auth-visual-content"' not in app,
          "The repeated authentication marketing panel must be removed from the JSX.")
    check('className="auth-desktop-panel"' not in app,
          "Authentication markup must not contain the rejected decorative desktop panel.")
    check("setAuthMode(authMode === 'login' ? 'register' : 'login')" in app,
          "The redesigned auth form must retain its existing sign-in / sign-up switch.")
    auth_refresh_css = full_redesign_css[full_redesign_css.find("FJ AUTH EXPERIENCE v2"):]
    check(bool(auth_refresh_css), "The final authentication redesign CSS is missing.")
    for auth_contract in (
        ".auth-shell > .auth-form-wrap",
        ".auth-shell .mobile-brand",
        "@media (max-width:700px)",
        "font-size:16px !important",
    ):
        check(auth_contract in auth_refresh_css, f"Authentication mobile layout contract is missing: {auth_contract}.")
    auth_desktop_css = full_redesign_css[full_redesign_css.find("FJ AUTH DESKTOP EXPERIENCE v2"): ]
    check(bool(auth_desktop_css), "The desktop authentication layout CSS is missing.")
    for desktop_auth_contract in (
        ".auth-shell > .auth-form-wrap",
        "width:min(100%,520px) !important",
        "border-top:3px solid var(--fj-violet,var(--accent))",
        "@media (min-width:701px)",
    ):
        check(desktop_auth_contract in auth_desktop_css,
              f"Desktop authentication layout contract is missing: {desktop_auth_contract}.")

    auth_width_css = full_redesign_css[full_redesign_css.find("FJ AUTH WIDTH EXPERIENCE v1"):]
    check(bool(auth_width_css), "The wider authentication layout overrides are missing.")
    for auth_width_contract in (
        "width:min(100%,600px) !important",
        "max-width:620px !important",
        "@media (max-width:700px)",
        "@media (max-width:380px)",
    ):
        check(auth_width_contract in auth_width_css,
              f"Authentication width contract is missing: {auth_width_contract}.")

    auth_full_width_css = full_redesign_css[full_redesign_css.find("FJ AUTH FULL-WIDTH EXPERIENCE v1"):]
    check(bool(auth_full_width_css), "The edge-to-edge authentication layout is missing.")
    for full_width_contract in (
        "padding-inline:clamp(22px,2.1vw,42px) !important",
        "width:100% !important",
        "max-width:none !important",
        "@media (min-width:1101px)",
        "@media (min-width:701px) and (max-width:1100px)",
        "@media (max-width:700px)",
    ):
        check(full_width_contract in auth_full_width_css,
              f"Full-width authentication contract is missing: {full_width_contract}.")

    check("contest-tag-preset-list" in app and "انتخاب سریع موضوع" in app,
          "Contest designer is missing quick topic presets.")
    for tag in ("combinatorics", "algorithm", "programming", "graph", "algebra", "geometry"):
        check(f"return '{tag}'" in app, f"Contest tag color mapping is missing: {tag}.")
    check("tagsText={adminTags}" in app and "onTagsText={setAdminTags}" in app,
          "Contest designer form is missing topic tag input.")
    check("tags: normalizedExamTags" in app,
          "Contest topic tags are not persisted on create/edit.")

team_migration_path = MIGRATIONS / "009_restore_four_person_teams.sql"
check(team_migration_path.is_file(), "Migration 009 is missing.")
if team_migration_path.is_file():
    team_sql = team_migration_path.read_text(encoding="utf-8")
    check("v_member_count + v_pending_count >= 4" in team_sql,
          "Database invite RPC does not count existing pending invitations.")
    check("v_members + v_pending >= 4" in team_sql,
          "Database invitation trigger does not enforce the four-person capacity.")

migration_path = MIGRATIONS / "010_public_review_leaderboard_designers.sql"
check(migration_path.is_file(), "Migration 010 is missing from the built source tree.")
problem_engine_path = MIGRATIONS / "011_problem_engine_foundation.sql"
check(problem_engine_path.is_file(), "Migration 011 problem engine foundation is missing.")
if problem_engine_path.is_file():
    sql = problem_engine_path.read_text(encoding="utf-8")
    for required in (
        "create table if not exists public.problems",
        "create table if not exists public.problem_tags",
        "create table if not exists public.problem_tag_links",
        "create table if not exists public.exam_problems",
        "create table if not exists public.problem_submissions",
        "create table if not exists public.problem_private_data",
        "create table if not exists public.problem_manual_grades",
        "public.update_my_profile_details",
        "contest_type text",
        "rating_mode text",
        "allow_virtual boolean",
    ):
        check(required in sql, f"Migration 011 is missing required problem/profile schema contract: {required}.")
    check("revoke all on public.problems" in sql and "public.problem_private_data" in sql,
          "Migration 011 must keep answer keys and judge configuration inaccessible to browser roles.")
    check("grant select on public.problem_assets, public.problem_submissions to authenticated" in sql,
          "Migration 011 is missing owner-scoped submission and asset read grants.")

if migration_path.is_file():
    sql = migration_path.read_text(encoding="utf-8")
    start = sql.lower().find("create or replace function public.get_public_exam_leaderboard(")
    end = sql.find("$$;", start)
    check(start >= 0 and end > start, "Could not locate the public leaderboard SQL function.")
    if start >= 0 and end > start:
        declaration = sql[start:end]
        header = declaration[:declaration.lower().find("as $$")]
        check(bool(re.search(r"\bvolatile\b", header, re.I)),
              "get_public_exam_leaderboard must be VOLATILE because it finalizes scores.")
        check(not bool(re.search(r"\bstable\b", header, re.I)),
              "get_public_exam_leaderboard is incorrectly marked STABLE.")
        check("rank bigint" in header and "position bigint" not in header,
              "Leaderboard output column must be rank, not reserved word position.")
        check("perform public.finalize_exam_internal(p_exam_id)" in declaration,
              "Leaderboard no longer finalizes scores on access.")
    check("function public.designer_update_contest_controls" in sql,
          "Migration 010 is missing owner-scoped designer contest controls.")
    check("function public.get_my_team_pending_invitation_count" in sql,
          "Migration 010 is missing the secure team pending-invitation count RPC.")

# Parse every SQL migration with PostgreSQL's grammar parser in CI.
try:
    from pglast import parse_sql
except ImportError:
    if os.environ.get("REQUIRE_PGLAST") == "1":
        errors.append("pglast is required for SQL syntax checks but is not installed.")
else:
    for number in range(2, 12):
        matches = sorted(MIGRATIONS.glob(f"{number:03d}_*.sql"))
        check(len(matches) == 1, f"Expected exactly one migration numbered {number:03d}.")
        if matches:
            try:
                parse_sql(matches[0].read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append(f"PostgreSQL syntax parse failed for {matches[0].name}: {exc}")

if errors:
    print(f"FAILED: {len(errors)} issue(s) across {checks} checks")
    for item in errors:
        print(f" - {item}")
    sys.exit(1)

print(f"PASS: {checks} release checks completed.")
