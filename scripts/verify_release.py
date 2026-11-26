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
    check("exam-card--" in app, "Contest cards are not styled from their first topic tag.")
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
    for number in range(2, 11):
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
