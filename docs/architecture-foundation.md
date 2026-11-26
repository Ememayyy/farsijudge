# FarsiJudge — Architecture Foundation

## Product boundary

FarsiJudge owns the user experience and the platform domain: accounts, profiles, problem catalog, contest configuration, registration, submissions, score aggregation, rating history, friends and public pages.

Supabase remains the initial control plane for authentication, relational data and private file metadata. GitHub Pages hosts only the static web client. It is not a trusted execution environment.

A separate Linux judging host will run CMS workers and a small private integration service. The browser must never call CMS directly and must never receive CMS credentials, answer keys, checker configuration or private test data.

## Core domain model

- `problems`: canonical reusable problem statement, answer type, difficulty, limits, visibility and author.
- `problem_tags` / `problem_tag_links`: many-to-many topic taxonomy.
- `exam_problems`: attach a reusable problem to a contest with its own order, points and scoring configuration.
- `problem_private_data`: private answer keys, tolerances, rubrics and judge-provider configuration.
- `problem_assets`: metadata for private files; bytes live in private Storage or the CMS task package.
- `problem_submissions`: one history model for code, output-only, answer-only, quiz, short-answer, essay and file submissions.
- `problem_manual_grades`: audit-friendly manual grading records.
- `exams`: keeps the legacy contest model while gaining contest type, scoring mode, rating mode and Virtual eligibility.

The old `exam_questions`, `exam_answers` and `exam_results` tables remain authoritative for existing contests until an explicit backfill and compatibility release is prepared. No destructive migration is part of this foundation.

## Supported answer types

`code`, `output_only`, `answer_only`, `single_choice`, `multiple_choice`, `short_answer`, `essay`, `file_upload`.

Automatic, manual and hybrid grading are modeled independently from the answer type. This allows a mixed contest to combine computer-judged programming problems with teacher-reviewed proofs.

## Judge isolation

1. A signed-in user submits through FarsiJudge.
2. A trusted server validates the user, contest window, attempt mode, language and file limits.
3. The server stores an immutable submission record and enqueues the job.
4. For code or output-only tasks, the private integration service submits the task to CMS.
5. CMS compiles/runs/checks inside its isolated workers.
6. The integration service maps the CMS result into FarsiJudge verdicts and score fields.
7. FarsiJudge updates the leaderboard from authoritative database records.

CMS is a private execution dependency, not the source of truth for users or contests. An adapter boundary keeps the option open to replace CMS later.

## Security invariants

- Never expose service-role keys, CMS API credentials, answer keys, test data or checker settings to the browser.
- Do not grant direct browser writes to authoritative verdict, score, private grading or judge-configuration tables.
- Keep uploaded answers and judge assets in private buckets; mint short-lived signed URLs only after authorization.
- Contestant access to contest-only statements must be checked server-side against registration and contest timing.
- A Virtual attempt is a separate attempt mode and must not alter official contest results or rating.
- Rating changes must be idempotent and auditable; only finalized rated contests affect rating history.

## Current deployment topology

- Frontend: Vite/React static build, deployed by GitHub Actions to GitHub Pages.
- Auth/database: Supabase.
- Judge: not deployed yet; CMS integration is a later stage and requires a separate Linux host.

## Migration 011

Migration 011 adds the reusable problem model and profile metadata without deleting or rewriting legacy contest data. It must be run manually in Supabase SQL Editor after migrations 002–010 have been applied successfully.
