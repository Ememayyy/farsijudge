-- FarsiJudge 010: public post-contest review, leaderboard, contest designers and profile access.
begin;

-- Keep the author of each contest so designers can only manage their own work.
alter table public.exams
  add column if not exists created_by uuid references auth.users(id) on delete set null;
create index if not exists exams_created_by_idx on public.exams(created_by);

create or replace function public.capture_exam_creator()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  if new.created_by is null then
    new.created_by := (select auth.uid());
  end if;
  return new;
end;
$$;

drop trigger if exists exams_capture_creator on public.exams;
create trigger exams_capture_creator
before insert on public.exams
for each row execute function public.capture_exam_creator();

-- Expand profile roles. Admin is still the only role that can grant roles or
-- administer every contest; designers can only create and manage their own.
do $$
declare c record;
begin
  for c in
    select conname
    from pg_catalog.pg_constraint
    where conrelid = 'public.profiles'::regclass
      and contype = 'c'
      and pg_catalog.pg_get_constraintdef(oid) ilike '%role%'
  loop
    execute pg_catalog.format('alter table public.profiles drop constraint %I', c.conname);
  end loop;
end;
$$;

alter table public.profiles
  add constraint profiles_role_allowed
  check (role in ('participant', 'designer', 'admin'));

create or replace function public.is_contest_designer()
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (
    select 1 from public.profiles p
    where p.id = (select auth.uid()) and p.role = 'designer'
  );
$$;

create or replace function public.can_manage_exam(p_exam_id uuid)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select (select public.is_admin())
    or (
      (select public.is_contest_designer())
      and exists (
        select 1 from public.exams e
        where e.id = p_exam_id and e.created_by = (select auth.uid())
      )
    );
$$;

revoke all on function public.is_contest_designer() from public, anon;
revoke all on function public.can_manage_exam(uuid) from public, anon;
grant execute on function public.is_contest_designer() to authenticated;
grant execute on function public.can_manage_exam(uuid) to authenticated;

-- Only admins may assign the designer role.
create or replace function public.admin_set_profile_role(p_user_id uuid, p_role text)
returns void
language plpgsql
security definer
set search_path = ''
as $$
begin
  if not (select public.is_admin()) then
    raise exception 'فقط مدیر سامانه اجازه تغییر نقش را دارد.';
  end if;
  if p_role not in ('participant', 'designer', 'admin') then
    raise exception 'نقش نامعتبر است.';
  end if;
  if p_user_id = (select auth.uid()) and p_role <> 'admin' then
    raise exception 'نمی‌توانید نقش مدیر خود را حذف کنید.';
  end if;
  update public.profiles set role = p_role where id = p_user_id;
  if not found then raise exception 'کاربر پیدا نشد.'; end if;
end;
$$;
revoke all on function public.admin_set_profile_role(uuid, text) from public, anon;
grant execute on function public.admin_set_profile_role(uuid, text) to authenticated;

-- Owner-scoped RLS for designer contest management. Existing admin/public
-- policies remain in place; policies are additive under PostgreSQL RLS.
drop policy if exists "designers_read_own_exams" on public.exams;
create policy "designers_read_own_exams"
on public.exams for select to authenticated
using (
  (select public.is_admin())
  or (
    (select public.is_contest_designer())
    and created_by = (select auth.uid())
  )
);

drop policy if exists "designers_insert_own_exams" on public.exams;
create policy "designers_insert_own_exams"
on public.exams for insert to authenticated
with check (
  (select public.is_admin())
  or (
    (select public.is_contest_designer())
    and created_by = (select auth.uid())
  )
);

drop policy if exists "designers_update_own_exams" on public.exams;
create policy "designers_update_own_exams"
on public.exams for update to authenticated
using ((select public.can_manage_exam(id)))
with check (
  (select public.is_admin())
  or (
    (select public.is_contest_designer())
    and created_by = (select auth.uid())
  )
);

drop policy if exists "designers_delete_own_exams" on public.exams;
create policy "designers_delete_own_exams"
on public.exams for delete to authenticated
using ((select public.can_manage_exam(id)));

-- Designer-specific RPCs keep the existing admin-only RPC contracts unchanged.
create or replace function public.designer_create_exam_with_answer_key(
  p_title text,
  p_description text,
  p_starts_at timestamptz,
  p_duration_minutes integer,
  p_questions jsonb
)
returns uuid
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_uid uuid := (select auth.uid());
  v_exam_id uuid;
  v_item jsonb;
  v_q integer;
  v_points numeric;
  v_answer numeric;
begin
  if v_uid is null or not (select public.is_contest_designer()) then
    raise exception 'فقط طراح مسابقه می‌تواند مسابقه بسازد.';
  end if;
  if nullif(btrim(p_title), '') is null then raise exception 'عنوان مسابقه الزامی است.'; end if;
  if p_starts_at is null then raise exception 'زمان شروع نامعتبر است.'; end if;
  if p_duration_minutes is null or p_duration_minutes < 1 or p_duration_minutes > 600 then
    raise exception 'مدت مسابقه باید بین ۱ تا ۶۰۰ دقیقه باشد.';
  end if;
  if pg_catalog.jsonb_typeof(p_questions) <> 'array'
     or pg_catalog.jsonb_array_length(p_questions) < 1
     or pg_catalog.jsonb_array_length(p_questions) > 300 then
    raise exception 'مسابقه باید بین ۱ تا ۳۰۰ سؤال داشته باشد.';
  end if;

  insert into public.exams(title, description, starts_at, duration_minutes, is_published, created_by)
  values (btrim(p_title), coalesce(p_description, ''), p_starts_at, p_duration_minutes, true, v_uid)
  returning id into v_exam_id;

  for v_item in select value from pg_catalog.jsonb_array_elements(p_questions)
  loop
    v_q := (v_item ->> 'question_number')::integer;
    v_points := (v_item ->> 'points')::numeric;
    v_answer := (v_item ->> 'correct_answer')::numeric;
    if v_q < 1 or v_q > 300 or v_points <= 0 then raise exception 'اطلاعات سؤال نامعتبر است.'; end if;
    insert into public.exam_questions(exam_id, question_number, points)
    values (v_exam_id, v_q, v_points);
    insert into public.exam_answer_keys(exam_id, question_number, correct_answer)
    values (v_exam_id, v_q, v_answer);
  end loop;
  return v_exam_id;
end;
$$;
revoke all on function public.designer_create_exam_with_answer_key(text, text, timestamptz, integer, jsonb) from public, anon;
grant execute on function public.designer_create_exam_with_answer_key(text, text, timestamptz, integer, jsonb) to authenticated;

create or replace function public.designer_edit_exam_with_answer_key(
  p_exam_id uuid,
  p_title text,
  p_description text,
  p_starts_at timestamptz,
  p_duration_minutes integer,
  p_questions jsonb,
  p_question_pdf_url text,
  p_question_file_path text
)
returns void
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_item jsonb;
  v_q integer;
  v_points numeric;
  v_answer numeric;
begin
  if not (select public.can_manage_exam(p_exam_id))
     or not (select public.is_contest_designer()) then
    raise exception 'فقط طراح همان مسابقه می‌تواند آن را ویرایش کند.';
  end if;
  if nullif(btrim(p_title), '') is null then raise exception 'عنوان مسابقه الزامی است.'; end if;
  if p_starts_at is null then raise exception 'زمان شروع نامعتبر است.'; end if;
  if p_duration_minutes is null or p_duration_minutes < 1 or p_duration_minutes > 600 then
    raise exception 'مدت مسابقه باید بین ۱ تا ۶۰۰ دقیقه باشد.';
  end if;
  if pg_catalog.jsonb_typeof(p_questions) <> 'array'
     or pg_catalog.jsonb_array_length(p_questions) < 1
     or pg_catalog.jsonb_array_length(p_questions) > 300 then
    raise exception 'مسابقه باید بین ۱ تا ۳۰۰ سؤال داشته باشد.';
  end if;

  update public.exams set
    title = btrim(p_title),
    description = coalesce(p_description, ''),
    starts_at = p_starts_at,
    duration_minutes = p_duration_minutes
  where id = p_exam_id and created_by = (select auth.uid());
  if not found then raise exception 'مسابقه پیدا نشد یا متعلق به شما نیست.'; end if;

  insert into public.exam_question_resources(exam_id, question_pdf_url, question_file_path, updated_at)
  values (p_exam_id, nullif(btrim(p_question_pdf_url), ''), nullif(btrim(p_question_file_path), ''), pg_catalog.now())
  on conflict (exam_id) do update set
    question_pdf_url = excluded.question_pdf_url,
    question_file_path = excluded.question_file_path,
    updated_at = excluded.updated_at;

  for v_item in select value from pg_catalog.jsonb_array_elements(p_questions)
  loop
    v_q := (v_item ->> 'question_number')::integer;
    v_points := (v_item ->> 'points')::numeric;
    v_answer := (v_item ->> 'correct_answer')::numeric;
    if v_q < 1 or v_q > 300 or v_points <= 0 then raise exception 'اطلاعات سؤال نامعتبر است.'; end if;
    insert into public.exam_questions(exam_id, question_number, points)
    values (p_exam_id, v_q, v_points)
    on conflict (exam_id, question_number) do update set points = excluded.points;
    insert into public.exam_answer_keys(exam_id, question_number, correct_answer)
    values (p_exam_id, v_q, v_answer)
    on conflict (exam_id, question_number) do update set correct_answer = excluded.correct_answer;
  end loop;

  delete from public.exam_questions q
  where q.exam_id = p_exam_id
    and not exists (
      select 1 from pg_catalog.jsonb_array_elements(p_questions) x
      where (x.value ->> 'question_number')::integer = q.question_number
    );
  delete from public.exam_results where exam_id = p_exam_id;
  perform public.finalize_exam_internal(p_exam_id);
end;
$$;
revoke all on function public.designer_edit_exam_with_answer_key(uuid, text, text, timestamptz, integer, jsonb, text, text) from public, anon;
grant execute on function public.designer_edit_exam_with_answer_key(uuid, text, text, timestamptz, integer, jsonb, text, text) to authenticated;

create or replace function public.designer_set_exam_question_resource(
  p_exam_id uuid,
  p_question_pdf_url text,
  p_question_file_path text
)
returns void
language plpgsql
security definer
set search_path = ''
as $$
begin
  if not (select public.can_manage_exam(p_exam_id))
     or not (select public.is_contest_designer()) then
    raise exception 'فقط طراح همان مسابقه می‌تواند فایل سؤال را تغییر دهد.';
  end if;
  insert into public.exam_question_resources(exam_id, question_pdf_url, question_file_path, updated_at)
  values (p_exam_id, nullif(btrim(p_question_pdf_url), ''), nullif(btrim(p_question_file_path), ''), pg_catalog.now())
  on conflict (exam_id) do update set
    question_pdf_url = excluded.question_pdf_url,
    question_file_path = excluded.question_file_path,
    updated_at = excluded.updated_at;
end;
$$;
revoke all on function public.designer_set_exam_question_resource(uuid, text, text) from public, anon;
grant execute on function public.designer_set_exam_question_resource(uuid, text, text) to authenticated;

create or replace function public.get_designer_exam_question_resource(p_exam_id uuid)
returns table(question_pdf_url text, question_file_path text)
language plpgsql
stable
security definer
set search_path = ''
as $$
begin
  if not (select public.can_manage_exam(p_exam_id))
     or not (select public.is_contest_designer()) then
    raise exception 'فقط طراح همان مسابقه می‌تواند فایل سؤال را مشاهده کند.';
  end if;
  return query
  select r.question_pdf_url, r.question_file_path
  from public.exam_question_resources r
  where r.exam_id = p_exam_id;
end;
$$;
revoke all on function public.get_designer_exam_question_resource(uuid) from public, anon;
grant execute on function public.get_designer_exam_question_resource(uuid) to authenticated;

-- Designers may upload only into the folder belonging to their own contest.
drop policy if exists "designers_upload_own_question_files" on storage.objects;
create policy "designers_upload_own_question_files"
on storage.objects for insert to authenticated
with check (
  bucket_id = 'exam-question-files'
  and (select public.is_contest_designer())
  and exists (
    select 1 from public.exams e
    where e.id::text = split_part(storage.objects.name, '/', 1)
      and e.created_by = (select auth.uid())
  )
);

drop policy if exists "designers_update_own_question_files" on storage.objects;
create policy "designers_update_own_question_files"
on storage.objects for update to authenticated
using (
  bucket_id = 'exam-question-files'
  and (select public.is_contest_designer())
  and exists (
    select 1 from public.exams e
    where e.id::text = split_part(storage.objects.name, '/', 1)
      and e.created_by = (select auth.uid())
  )
)
with check (
  bucket_id = 'exam-question-files'
  and (select public.is_contest_designer())
  and exists (
    select 1 from public.exams e
    where e.id::text = split_part(storage.objects.name, '/', 1)
      and e.created_by = (select auth.uid())
  )
);

drop policy if exists "designers_delete_own_question_files" on storage.objects;
create policy "designers_delete_own_question_files"
on storage.objects for delete to authenticated
using (
  bucket_id = 'exam-question-files'
  and (select public.is_contest_designer())
  and exists (
    select 1 from public.exams e
    where e.id::text = split_part(storage.objects.name, '/', 1)
      and e.created_by = (select auth.uid())
  )
);

-- Designers must be able to reopen and edit the questions, answer keys and
-- uploaded resource belonging to their own contests.
drop policy if exists "designers_read_own_exam_questions" on public.exam_questions;
create policy "designers_read_own_exam_questions"
on public.exam_questions for select to authenticated
using ((select public.can_manage_exam(exam_id)));

drop policy if exists "designers_read_own_answer_keys" on public.exam_answer_keys;
create policy "designers_read_own_answer_keys"
on public.exam_answer_keys for select to authenticated
using ((select public.can_manage_exam(exam_id)));

drop policy if exists "designers_read_own_question_resources" on public.exam_question_resources;
create policy "designers_read_own_question_resources"
on public.exam_question_resources for select to authenticated
using ((select public.can_manage_exam(exam_id)));

drop policy if exists "designers_read_own_question_files" on storage.objects;
create policy "designers_read_own_question_files"
on storage.objects for select to authenticated
using (
  bucket_id = 'exam-question-files'
  and (select public.is_contest_designer())
  and exists (
    select 1 from public.exams e
    where e.id::text = split_part(storage.objects.name, '/', 1)
      and e.created_by = (select auth.uid())
  )
);

-- Public question access is deliberately read-only and begins only after
-- the contest end time. The private bucket stays private.
create or replace function public.get_public_exam_question_resource(p_exam_id uuid)
returns table(question_pdf_url text, question_file_path text)
language plpgsql
stable
security definer
set search_path = ''
as $$
begin
  if not exists (
    select 1 from public.exams e
    where e.id = p_exam_id
      and e.is_published is true
      and pg_catalog.now() >= coalesce(
        e.end_at_override,
        e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes)
      )
  ) then
    raise exception 'صورت سؤال پس از پایان مسابقه در دسترس قرار می‌گیرد.';
  end if;
  return query
  select r.question_pdf_url, r.question_file_path
  from public.exam_question_resources r
  where r.exam_id = p_exam_id;
end;
$$;
revoke all on function public.get_public_exam_question_resource(uuid) from public;
grant execute on function public.get_public_exam_question_resource(uuid) to anon, authenticated;

create or replace function public.get_public_exam_questions(p_exam_id uuid)
returns table(question_number integer, points numeric)
language plpgsql
stable
security definer
set search_path = ''
as $$
begin
  if not exists (
    select 1 from public.exams e
    where e.id = p_exam_id
      and e.is_published is true
      and pg_catalog.now() >= coalesce(
        e.end_at_override,
        e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes)
      )
  ) then
    raise exception 'سؤال‌های مسابقه پس از پایان آن در دسترس قرار می‌گیرند.';
  end if;
  return query
  select q.question_number, q.points
  from public.exam_questions q
  where q.exam_id = p_exam_id
  order by q.question_number;
end;
$$;
revoke all on function public.get_public_exam_questions(uuid) from public;
grant execute on function public.get_public_exam_questions(uuid) to anon, authenticated;

-- Public results are aggregated at the actual competitor level: one row per
-- team registration or individual registration, never one row per teammate.
create or replace function public.get_public_exam_leaderboard(p_exam_id uuid)
returns table(
  position bigint,
  display_name text,
  team_name text,
  score numeric,
  max_score numeric,
  correct_count integer,
  wrong_count integer,
  question_count integer,
  is_team boolean
)
language plpgsql
stable
security definer
set search_path = ''
as $$
declare v_release_at timestamptz;
begin
  select greatest(
    coalesce(e.results_release_at, coalesce(e.end_at_override, e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes))),
    coalesce(e.end_at_override, e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes))
  )
  into v_release_at
  from public.exams e
  where e.id = p_exam_id and e.is_published is true;

  if v_release_at is null then raise exception 'مسابقه پیدا نشد یا منتشر نشده است.'; end if;
  if pg_catalog.now() < v_release_at then
    raise exception 'جدول امتیازات پس از انتشار نتایج در دسترس قرار می‌گیرد.';
  end if;

  -- Ensure final score rows exist even when the scheduled finalizer has not run.
  perform public.finalize_exam_internal(p_exam_id);

  return query
  with scored as (
    select
      case when r.team_id is not null then t.name
           else coalesce(nullif(btrim(p.full_name), ''), nullif(p.username, ''), 'شرکت‌کننده')
      end as display_name,
      case when r.team_id is not null then t.name else null end as team_name,
      r.score,
      r.max_score,
      r.correct_count,
      coalesce((
        select count(*)::integer
        from public.exam_answers a
        join public.exam_answer_keys k
          on k.exam_id = a.exam_id
         and k.question_number = a.question_number
        where a.exam_id = r.exam_id
          and a.answer is not null
          and a.answer <> k.correct_answer
          and (
            (r.team_id is not null and a.team_id = r.team_id)
            or (r.team_id is null and a.team_id is null and a.user_id = r.user_id)
          )
      ), 0) as wrong_count,
      r.question_count,
      (r.team_id is not null) as is_team
    from public.exam_results r
    left join public.profiles p on p.id = r.user_id
    left join public.teams t on t.id = r.team_id
    where r.exam_id = p_exam_id
  )
  select
    row_number() over (
      order by s.score desc, s.wrong_count asc, s.display_name collate "C" asc
    ) as position,
    s.display_name,
    s.team_name,
    s.score,
    s.max_score,
    s.correct_count,
    s.wrong_count,
    s.question_count,
    s.is_team
  from scored s
  order by s.score desc, s.wrong_count asc, s.display_name collate "C" asc;
end;
$$;
revoke all on function public.get_public_exam_leaderboard(uuid) from public;
grant execute on function public.get_public_exam_leaderboard(uuid) to anon, authenticated;

-- Do not truncate the public feed to the first 50 contests. Preserve metadata
-- used by the frontend to distinguish upcoming, active and ended contests.
drop function if exists public.get_public_contests();
create function public.get_public_contests()
returns table (
  id uuid,
  title text,
  description text,
  starts_at timestamptz,
  duration_minutes integer,
  is_published boolean,
  end_at_override timestamptz,
  tags text[]
)
language sql
stable
security definer
set search_path = ''
as $$
  select e.id, e.title, e.description, e.starts_at, e.duration_minutes,
         e.is_published, e.end_at_override, coalesce(e.tags, '{}'::text[])
  from public.exams e
  where e.is_published is true
  order by e.starts_at desc;
$$;
revoke all on function public.get_public_contests() from public;
grant execute on function public.get_public_contests() to anon, authenticated;

-- A visitor may mint a short-lived signed URL to a finished contest PDF.
drop policy if exists "question_files_public_after_end" on storage.objects;
create policy "question_files_public_after_end"
on storage.objects for select to anon, authenticated
using (
  bucket_id = 'exam-question-files'
  and exists (
    select 1 from public.exams e
    where e.id::text = split_part(storage.objects.name, '/', 1)
      and e.is_published is true
      and pg_catalog.now() >= coalesce(
        e.end_at_override,
        e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes)
      )
  )
);

commit;
