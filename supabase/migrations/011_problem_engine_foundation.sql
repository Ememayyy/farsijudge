-- FarsiJudge 011: extensible problem bank, typed submissions and public profile metadata.
-- Run once AFTER migration 010. This migration is additive and preserves the legacy exam tables.
begin;

-- Contest-level options. Existing contests keep the legacy behavior and remain unrated.
alter table public.exams
  add column if not exists contest_type text not null default 'legacy'
    check (contest_type in ('legacy', 'programming', 'olympiad', 'theoretical', 'mixed')),
  add column if not exists scoring_mode text not null default 'points'
    check (scoring_mode in ('points', 'icpc', 'partial')),
  add column if not exists rating_mode text not null default 'unrated'
    check (rating_mode in ('unrated', 'rated')),
  add column if not exists allow_virtual boolean not null default true;
create index if not exists exams_contest_type_idx on public.exams(contest_type, starts_at desc);

-- Public profile metadata. Avatar files remain in private Storage; only the owner path is stored here.
alter table public.profiles
  add column if not exists country_code text,
  add column if not exists city text,
  add column if not exists organization text,
  add column if not exists bio text,
  add column if not exists avatar_path text,
  add column if not exists website_url text,
  add column if not exists github_handle text,
  add column if not exists codeforces_handle text,
  add column if not exists updated_at timestamptz not null default pg_catalog.now();

do $$
begin
  if not exists (select 1 from pg_catalog.pg_constraint where conrelid = 'public.profiles'::regclass and conname = 'profiles_country_code_format') then
    alter table public.profiles add constraint profiles_country_code_format
      check (country_code is null or country_code ~ '^[A-Z]{2}$');
  end if;
  if not exists (select 1 from pg_catalog.pg_constraint where conrelid = 'public.profiles'::regclass and conname = 'profiles_bio_length') then
    alter table public.profiles add constraint profiles_bio_length
      check (bio is null or char_length(bio) <= 280);
  end if;
  if not exists (select 1 from pg_catalog.pg_constraint where conrelid = 'public.profiles'::regclass and conname = 'profiles_avatar_path_owner_scope') then
    alter table public.profiles add constraint profiles_avatar_path_owner_scope
      check (avatar_path is null or (id is not null and avatar_path like (id::text || '/%')));
  end if;
end;
$$;

create or replace function public.update_my_profile_details(
  p_country_code text,
  p_city text,
  p_organization text,
  p_bio text,
  p_avatar_path text,
  p_website_url text,
  p_github_handle text,
  p_codeforces_handle text
)
returns void
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_uid uuid := (select auth.uid());
  v_country text := nullif(upper(btrim(p_country_code)), '');
  v_avatar text := nullif(btrim(p_avatar_path), '');
  v_website text := nullif(btrim(p_website_url), '');
begin
  if v_uid is null then
    raise exception 'ابتدا وارد حساب کاربری شوید.';
  end if;
  if v_country is not null and v_country !~ '^[A-Z]{2}$' then
    raise exception 'کد کشور باید از قالب دوحرفی ISO استفاده کند.';
  end if;
  if char_length(coalesce(btrim(p_city), '')) > 80
     or char_length(coalesce(btrim(p_organization), '')) > 120
     or char_length(coalesce(btrim(p_bio), '')) > 280
     or char_length(coalesce(v_website, '')) > 300
     or char_length(coalesce(btrim(p_github_handle), '')) > 60
     or char_length(coalesce(btrim(p_codeforces_handle), '')) > 60 then
    raise exception 'یکی از فیلدهای پروفایل بیش از حد مجاز طول دارد.';
  end if;
  if v_website is not null and v_website !~* '^https?://' then
    raise exception 'آدرس وب‌سایت باید با http:// یا https:// شروع شود.';
  end if;
  if v_avatar is not null and left(v_avatar, char_length(v_uid::text) + 1) <> (v_uid::text || '/') then
    raise exception 'مسیر تصویر پروفایل باید متعلق به حساب خودتان باشد.';
  end if;

  update public.profiles
  set country_code = v_country,
      city = nullif(btrim(p_city), ''),
      organization = nullif(btrim(p_organization), ''),
      bio = nullif(btrim(p_bio), ''),
      avatar_path = v_avatar,
      website_url = v_website,
      github_handle = nullif(btrim(p_github_handle), ''),
      codeforces_handle = nullif(btrim(p_codeforces_handle), ''),
      updated_at = pg_catalog.now()
  where id = v_uid;
  if not found then
    raise exception 'پروفایل کاربر پیدا نشد.';
  end if;
end;
$$;
revoke all on function public.update_my_profile_details(text, text, text, text, text, text, text, text) from public, anon;
grant execute on function public.update_my_profile_details(text, text, text, text, text, text, text, text) to authenticated;

-- Problems are independent objects. A problem can be reused in multiple contests or practice sets.
create table if not exists public.problems (
  id uuid primary key default gen_random_uuid(),
  slug text,
  title text not null check (char_length(btrim(title)) between 1 and 160),
  statement_md text not null default '',
  input_format_md text not null default '',
  output_format_md text not null default '',
  constraints_md text not null default '',
  answer_type text not null default 'short_answer'
    check (answer_type in ('code', 'output_only', 'answer_only', 'single_choice', 'multiple_choice', 'short_answer', 'essay', 'file_upload')),
  grading_mode text not null default 'automatic'
    check (grading_mode in ('automatic', 'manual', 'hybrid')),
  difficulty smallint check (difficulty between 1 and 5),
  default_points numeric(10,2) not null default 100 check (default_points >= 0),
  time_limit_ms integer check (time_limit_ms is null or time_limit_ms between 1 and 600000),
  memory_limit_mb integer check (memory_limit_mb is null or memory_limit_mb between 1 and 1048576),
  visibility text not null default 'private' check (visibility in ('private', 'public', 'contest')),
  status text not null default 'draft' check (status in ('draft', 'published', 'archived')),
  author_name text,
  created_by uuid not null references auth.users(id) on delete restrict,
  legacy_exam_id uuid references public.exams(id) on delete set null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default pg_catalog.now(),
  updated_at timestamptz not null default pg_catalog.now()
);
create unique index if not exists problems_slug_lower_uidx
  on public.problems (lower(slug)) where slug is not null and btrim(slug) <> '';
create index if not exists problems_public_catalog_idx
  on public.problems (status, visibility, created_at desc);
create index if not exists problems_created_by_idx on public.problems(created_by, updated_at desc);
create index if not exists problems_legacy_exam_idx on public.problems(legacy_exam_id) where legacy_exam_id is not null;

create table if not exists public.problem_tags (
  id uuid primary key default gen_random_uuid(),
  name text not null check (char_length(btrim(name)) between 1 and 50),
  slug text not null unique,
  tone text not null default 'violet'
    check (tone in ('violet', 'blue', 'green', 'orange', 'yellow', 'red', 'cyan', 'gray')),
  created_at timestamptz not null default pg_catalog.now()
);
create unique index if not exists problem_tags_name_lower_uidx on public.problem_tags(lower(name));

create table if not exists public.problem_tag_links (
  problem_id uuid not null references public.problems(id) on delete cascade,
  tag_id uuid not null references public.problem_tags(id) on delete cascade,
  created_at timestamptz not null default pg_catalog.now(),
  primary key (problem_id, tag_id)
);
create index if not exists problem_tag_links_tag_idx on public.problem_tag_links(tag_id, problem_id);

-- Contest association is separate from the problem itself; scores/order can differ by contest.
create table if not exists public.exam_problems (
  id uuid primary key default gen_random_uuid(),
  exam_id uuid not null references public.exams(id) on delete cascade,
  problem_id uuid not null references public.problems(id) on delete restrict,
  problem_order integer not null check (problem_order > 0),
  points numeric(10,2) not null default 100 check (points >= 0),
  is_required boolean not null default true,
  scoring_config jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default pg_catalog.now(),
  unique (exam_id, problem_id),
  unique (exam_id, problem_order)
);
create index if not exists exam_problems_problem_idx on public.exam_problems(problem_id, exam_id);

-- File metadata only. Actual uploads and private test data live in private Storage/CMS, not public rows.
create table if not exists public.problem_assets (
  id uuid primary key default gen_random_uuid(),
  problem_id uuid not null references public.problems(id) on delete cascade,
  storage_path text not null,
  file_name text not null check (char_length(btrim(file_name)) between 1 and 255),
  mime_type text,
  byte_size bigint check (byte_size is null or byte_size between 0 and 52428800),
  purpose text not null default 'statement'
    check (purpose in ('statement', 'example', 'editorial', 'answer', 'attachment', 'checker', 'test_data')),
  uploaded_by uuid not null references auth.users(id) on delete restrict,
  created_at timestamptz not null default pg_catalog.now(),
  unique (storage_path)
);
create index if not exists problem_assets_problem_idx on public.problem_assets(problem_id, purpose);

-- Answer keys, rubrics and CMS task configuration are intentionally inaccessible to browser roles.
create table if not exists public.problem_private_data (
  problem_id uuid primary key references public.problems(id) on delete cascade,
  expected_answer jsonb,
  answer_tolerance numeric,
  answer_options jsonb,
  rubric jsonb not null default '[]'::jsonb,
  judge_provider text not null default 'builtin' check (judge_provider in ('builtin', 'cms')),
  cms_task_id text,
  judge_config jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default pg_catalog.now(),
  check (answer_tolerance is null or answer_tolerance >= 0)
);

-- One submission model supports code, output files, final answers, quizzes and written responses.
create table if not exists public.problem_submissions (
  id uuid primary key default gen_random_uuid(),
  problem_id uuid not null references public.problems(id) on delete restrict,
  exam_id uuid references public.exams(id) on delete set null,
  user_id uuid not null references auth.users(id) on delete cascade,
  team_id uuid references public.teams(id) on delete set null,
  attempt_mode text not null default 'practice' check (attempt_mode in ('practice', 'contest', 'virtual')),
  answer_type text not null
    check (answer_type in ('code', 'output_only', 'answer_only', 'single_choice', 'multiple_choice', 'short_answer', 'essay', 'file_upload')),
  language text,
  answer_text text,
  answer_data jsonb,
  storage_path text,
  judge_provider text not null default 'builtin' check (judge_provider in ('builtin', 'cms')),
  judge_submission_id text,
  status text not null default 'queued'
    check (status in ('queued', 'judging', 'finished', 'needs_review', 'error')),
  verdict text
    check (verdict is null or verdict in ('accepted', 'wrong_answer', 'time_limit', 'memory_limit', 'runtime_error', 'compilation_error', 'partial', 'pending', 'not_applicable')),
  score numeric(10,2) not null default 0 check (score >= 0),
  max_score numeric(10,2) not null default 0 check (max_score >= 0),
  result_data jsonb not null default '{}'::jsonb,
  feedback text,
  submitted_at timestamptz not null default pg_catalog.now(),
  judged_at timestamptz,
  check (exam_id is not null or attempt_mode <> 'contest'),
  check (score <= max_score or max_score = 0)
);
create index if not exists problem_submissions_user_history_idx
  on public.problem_submissions(user_id, submitted_at desc);
create index if not exists problem_submissions_problem_history_idx
  on public.problem_submissions(problem_id, submitted_at desc);
create index if not exists problem_submissions_exam_score_idx
  on public.problem_submissions(exam_id, score desc, submitted_at asc) where exam_id is not null;
create unique index if not exists problem_submissions_cms_ref_uidx
  on public.problem_submissions(judge_provider, judge_submission_id)
  where judge_submission_id is not null;

create table if not exists public.problem_manual_grades (
  id uuid primary key default gen_random_uuid(),
  submission_id uuid not null unique references public.problem_submissions(id) on delete cascade,
  grader_id uuid not null references auth.users(id) on delete restrict,
  score numeric(10,2) not null check (score >= 0),
  feedback text,
  is_final boolean not null default false,
  graded_at timestamptz not null default pg_catalog.now()
);

create or replace function public.touch_problem_updated_at()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at := pg_catalog.now();
  return new;
end;
$$;
revoke all on function public.touch_problem_updated_at() from public, anon, authenticated;
drop trigger if exists problems_touch_updated_at on public.problems;
create trigger problems_touch_updated_at
before update on public.problems
for each row execute function public.touch_problem_updated_at();

-- RLS: public catalog rows are readable, drafts stay with their author and platform admins.
alter table public.problems enable row level security;
alter table public.problem_tags enable row level security;
alter table public.problem_tag_links enable row level security;
alter table public.exam_problems enable row level security;
alter table public.problem_assets enable row level security;
alter table public.problem_private_data enable row level security;
alter table public.problem_submissions enable row level security;
alter table public.problem_manual_grades enable row level security;

revoke all on public.problems, public.problem_tags, public.problem_tag_links, public.exam_problems,
  public.problem_assets, public.problem_private_data, public.problem_submissions, public.problem_manual_grades
  from public, anon, authenticated;

grant select on public.problems, public.problem_tags, public.problem_tag_links, public.exam_problems to anon, authenticated;
grant insert, update, delete on public.problems, public.problem_tags, public.problem_tag_links, public.exam_problems to authenticated;
grant select on public.problem_assets, public.problem_submissions to authenticated;

create policy problems_public_read on public.problems
for select to anon, authenticated
using (status = 'published' and visibility = 'public');
create policy problems_owner_read on public.problems
for select to authenticated
using (created_by = (select auth.uid()) or (select public.is_admin()));
create policy problems_author_insert on public.problems
for insert to authenticated
with check (
  created_by = (select auth.uid())
  and ((select public.is_admin()) or (select public.is_contest_designer()))
);
create policy problems_author_update on public.problems
for update to authenticated
using (created_by = (select auth.uid()) or (select public.is_admin()))
with check (created_by = (select auth.uid()) or (select public.is_admin()));
create policy problems_author_delete on public.problems
for delete to authenticated
using (created_by = (select auth.uid()) or (select public.is_admin()));

create policy problem_tags_public_read on public.problem_tags
for select to anon, authenticated using (true);
create policy problem_tags_staff_write on public.problem_tags
for all to authenticated
using ((select public.is_admin()) or (select public.is_contest_designer()))
with check ((select public.is_admin()) or (select public.is_contest_designer()));

create policy problem_tag_links_public_read on public.problem_tag_links
for select to anon, authenticated
using (exists (
  select 1 from public.problems p
  where p.id = problem_id and p.status = 'published' and p.visibility = 'public'
));
create policy problem_tag_links_owner_read on public.problem_tag_links
for select to authenticated
using (exists (
  select 1 from public.problems p
  where p.id = problem_id and (p.created_by = (select auth.uid()) or (select public.is_admin()))
));
create policy problem_tag_links_owner_write on public.problem_tag_links
for all to authenticated
using (exists (
  select 1 from public.problems p
  where p.id = problem_id and (p.created_by = (select auth.uid()) or (select public.is_admin()))
))
with check (exists (
  select 1 from public.problems p
  where p.id = problem_id and (p.created_by = (select auth.uid()) or (select public.is_admin()))
));

create policy exam_problems_public_read on public.exam_problems
for select to anon, authenticated
using (exists (
  select 1 from public.exams e
  join public.problems p on p.id = problem_id
  where e.id = exam_id and e.is_published is true
    and p.status = 'published' and p.visibility = 'public'
));
create policy exam_problems_manager_read on public.exam_problems
for select to authenticated
using ((select public.can_manage_exam(exam_id)) or (select public.is_admin()));
create policy exam_problems_manager_write on public.exam_problems
for all to authenticated
using ((select public.can_manage_exam(exam_id)) or (select public.is_admin()))
with check ((select public.can_manage_exam(exam_id)) or (select public.is_admin()));

create policy problem_assets_owner_read on public.problem_assets
for select to authenticated
using (exists (
  select 1 from public.problems p
  where p.id = problem_id and (p.created_by = (select auth.uid()) or (select public.is_admin()))
));

create policy problem_submissions_owner_read on public.problem_submissions
for select to authenticated
using (
  user_id = (select auth.uid())
  or (select public.is_admin())
  or exists (select 1 from public.problems p where p.id = problem_id and p.created_by = (select auth.uid()))
  or (exam_id is not null and (select public.can_manage_exam(exam_id)))
);

-- No browser role can read answer keys, rubrics, judge configuration or write authoritative verdicts.
-- Future submission and grading RPCs will validate authorization before mutating these tables.

commit;
