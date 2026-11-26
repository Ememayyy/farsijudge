# FarsiJudge implementation roadmap

The project is delivered in six release gates. Each gate must build and pass its regression checks before work moves to the next one.

## Gate 1 — Foundation and product shell
- Preserve the current contest/auth flows.
- Add the extensible domain model for problems, typed submissions, contest formats and public profile metadata.
- Define reusable visual tokens and page-layout rules before the global redesign.
- Verify desktop/mobile navigation, auth restoration and old contest compatibility.

## Gate 2 — Problem Engine and problem bank
- Build create/edit/preview for all answer types.
- Add problem search, filters, tags, difficulty, author attribution and reuse across contests.
- Add private assets, answer keys, rubrics and manual grading workflow.
- Backfill legacy questions only after mapping their statements, scoring and answer semantics.

## Gate 3 — Judge Engine
- Provision a separate Linux host and install CMS with its required isolation dependencies.
- Implement a private adapter service; do not expose CMS to the browser.
- Prove code and Output-Only submissions end-to-end before opening the feature to users.
- Add quotas, file validation, rate limits, audit logs and operational monitoring.

## Gate 4 — Contest Engine
- Add the Contest Builder and programming/olympiad/theory/mixed formats.
- Implement live contest UX, autosave, clarifications, submission history and score aggregation.
- Add Virtual attempts with independent timers, submissions and results.
- Preserve existing team registration and legacy results.

## Gate 5 — Profiles and competition
- Add editable avatar, country, city, organization and public biography.
- Add friend requests and friends lists.
- Add separate rating tracks where competition formats are not directly comparable.
- Add rating history, ranks, organization/country leaderboards and achievements.

## Gate 6 — Product polish and learning tools
- Finish responsive redesign of landing, auth, dashboard, contest, problemset and profile pages.
- Add upsolving, editorial/discussions, problem recommendations, contest replay and daily challenge.
- Perform accessibility, mobile, security, performance and regression testing.
