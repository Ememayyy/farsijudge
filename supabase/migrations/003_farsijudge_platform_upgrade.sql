-- Farsi-Judge platform upgrade 003
-- Run once AFTER 002_teams_registration_admin_features.sql in Supabase SQL Editor.
begin;

-- Contest metadata and live controls.
alter table public.exams
  add column if not exists tags text[] not null default '{}',
  add column if not exists results_release_at timestamptz,
  add column if not exists allow_late_registration boolean not null default false,
  add column if not exists registration_closes_at timestamptz,
  add column if not exists end_at_override timestamptz,
  add column if not exists announcement text;

create index if not exists exams_tags_gin_idx on public.exams using gin(tags);
create index if not exists exams_release_at_idx on public.exams(results_release_at);

-- User-facing session registry: the newest authenticated device becomes the only active one.
create table if not exists public.user_active_sessions (
  user_id uuid primary key references auth.users(id) on delete cascade,
  session_id uuid not null,
  activated_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.user_active_sessions enable row level security;
revoke all on public.user_active_sessions from public, anon, authenticated;

create or replace function public.activate_my_single_session()
returns void
language plpgsql security definer set search_path = ''
as $$
declare
  v_uid uuid := (select auth.uid());
  v_session_id uuid := nullif((select auth.jwt() ->> 'session_id'), '')::uuid;
begin
  if v_uid is null or v_session_id is null then
    raise exception 'شناسه نشست معتبر نیست؛ دوباره وارد حساب شوید.';
  end if;
  insert into public.user_active_sessions(user_id, session_id, activated_at, updated_at)
  values (v_uid, v_session_id, pg_catalog.now(), pg_catalog.now())
  on conflict (user_id) do update set
    session_id = excluded.session_id,
    activated_at = excluded.activated_at,
    updated_at = excluded.updated_at;
end;
$$;
revoke all on function public.activate_my_single_session() from public, anon;
grant execute on function public.activate_my_single_session() to authenticated;

create or replace function public.is_my_single_session_active()
returns boolean
language sql stable security definer set search_path = ''
as $$
  select exists (
    select 1
    from public.user_active_sessions s
    where s.user_id = (select auth.uid())
      and s.session_id = nullif((select auth.jwt() ->> 'session_id'), '')::uuid
  );
$$;
revoke all on function public.is_my_single_session_active() from public, anon;
grant execute on function public.is_my_single_session_active() to authenticated;

create or replace function public.require_my_single_session()
returns void
language plpgsql stable security definer set search_path = ''
as $$
begin
  if not (select public.is_my_single_session_active()) then
    raise exception 'این حساب در دستگاه دیگری وارد شده است. برای ادامه دوباره وارد شوید.';
  end if;
end;
$$;
revoke all on function public.require_my_single_session() from public, anon;
grant execute on function public.require_my_single_session() to authenticated;

-- Database-level cap: exactly three people total, captain included.
create or replace function public.enforce_team_member_limit()
returns trigger
language plpgsql security definer set search_path = ''
as $$
declare v_count integer;
begin
  perform 1 from public.teams where id = new.team_id for update;
  select count(*) into v_count
  from public.team_members
  where team_id = new.team_id
    and (tg_op <> 'UPDATE' or user_id <> old.user_id);
  if v_count >= 3 then
    raise exception 'هر تیم حداکثر سه عضو دارد؛ کاپیتان هم جزو همین سه نفر است.';
  end if;
  return new;
end;
$$;

drop trigger if exists team_member_limit_before_write on public.team_members;
create trigger team_member_limit_before_write
before insert or update of team_id on public.team_members
for each row execute function public.enforce_team_member_limit();

-- Replace team creation so it uses the active single-device session.
create or replace function public.create_team(p_name text)
returns uuid
language plpgsql security definer set search_path = ''
as $$
declare v_team_id uuid; v_uid uuid := (select auth.uid());
begin
  if v_uid is null then raise exception 'ابتدا وارد حساب کاربری شوید.'; end if;
  perform public.require_my_single_session();
  if nullif(btrim(p_name), '') is null or char_length(btrim(p_name)) > 40 then
    raise exception 'نام تیم باید بین ۲ تا ۴۰ کاراکتر باشد.';
  end if;
  if exists (select 1 from public.team_members where user_id = v_uid) then
    raise exception 'شما هم‌اکنون عضو یک تیم هستید.';
  end if;
  insert into public.teams(name, captain_id) values (btrim(p_name), v_uid)
  returning id into v_team_id;
  insert into public.team_members(team_id, user_id, role)
  values (v_team_id, v_uid, 'captain');
  return v_team_id;
end;
$$;
revoke all on function public.create_team(text) from public, anon;
grant execute on function public.create_team(text) to authenticated;

create or replace function public.invite_team_member(p_identifier text)
returns uuid
language plpgsql security definer set search_path = ''
as $$
declare
  v_uid uuid := (select auth.uid());
  v_team_id uuid;
  v_target uuid;
  v_invitation_id uuid;
  v_member_count integer;
  v_pending_count integer;
begin
  if v_uid is null then raise exception 'ابتدا وارد حساب کاربری شوید.'; end if;
  perform public.require_my_single_session();
  select tm.team_id into v_team_id
  from public.team_members tm
  where tm.user_id = v_uid and tm.role = 'captain';
  if v_team_id is null then raise exception 'فقط کاپیتان تیم می‌تواند دعوت‌نامه بفرستد.'; end if;

  perform 1 from public.teams where id = v_team_id for update;
  select p.id into v_target
  from public.profiles p
  join auth.users u on u.id = p.id
  where lower(p.username) = lower(btrim(p_identifier))
     or lower(u.email) = lower(btrim(p_identifier))
  limit 1;
  if v_target is null then raise exception 'کاربری با این نام کاربری یا ایمیل پیدا نشد.'; end if;
  if v_target = v_uid then raise exception 'نمی‌توانید خودتان را دعوت کنید.'; end if;
  if exists (select 1 from public.team_members where user_id = v_target) then
    raise exception 'این کاربر هم‌اکنون عضو یک تیم است.';
  end if;

  select count(*) into v_member_count from public.team_members where team_id = v_team_id;
  select count(*) into v_pending_count from public.team_invitations
    where team_id = v_team_id and status = 'pending';
  if v_member_count + v_pending_count >= 3 then
    raise exception 'ظرفیت تیم تکمیل است؛ هر تیم حداکثر سه عضو با احتساب کاپیتان دارد.';
  end if;

  insert into public.team_invitations(team_id, invited_user_id, invited_by)
  values (v_team_id, v_target, v_uid)
  on conflict (team_id, invited_user_id) do update
    set status = 'pending', invited_by = excluded.invited_by,
        created_at = pg_catalog.now(), responded_at = null
  returning id into v_invitation_id;
  return v_invitation_id;
end;
$$;
revoke all on function public.invite_team_member(text) from public, anon;
grant execute on function public.invite_team_member(text) to authenticated;

create or replace function public.respond_team_invitation(p_invitation_id uuid, p_accept boolean)
returns void
language plpgsql security definer set search_path = ''
as $$
declare
  v_uid uuid := (select auth.uid());
  v_team_id uuid;
  v_member_count integer;
begin
  if v_uid is null then raise exception 'ابتدا وارد حساب کاربری شوید.'; end if;
  perform public.require_my_single_session();
  perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(v_uid::text, 0));
  select i.team_id into v_team_id
  from public.team_invitations i
  where i.id = p_invitation_id and i.invited_user_id = v_uid and i.status = 'pending'
  for update;
  if v_team_id is null then raise exception 'این دعوت‌نامه معتبر یا فعال نیست.'; end if;

  perform 1 from public.teams where id = v_team_id for update;
  if p_accept then
    if exists (
      select 1 from public.exam_team_registrations etr
      join public.exams e on e.id = etr.exam_id
      where etr.team_id = v_team_id
        and pg_catalog.now() < coalesce(e.end_at_override, e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes))
    ) then
      raise exception 'تا پایان مسابقه فعال، ترکیب اعضای تیم قابل تغییر نیست.';
    end if;
    if exists (select 1 from public.team_members where user_id = v_uid) then
      raise exception 'ابتدا باید از تیم فعلی خارج شوید.';
    end if;
    if exists (
      select 1 from public.exam_registrations er
      join public.exams e on e.id = er.exam_id
      where er.user_id = v_uid
        and pg_catalog.now() < coalesce(e.end_at_override, e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes))
    ) then
      raise exception 'تا پایان مسابقه‌ای که در آن ثبت‌نام کرده‌اید نمی‌توانید عضو تیم دیگری شوید.';
    end if;
    select count(*) into v_member_count from public.team_members where team_id = v_team_id;
    if v_member_count >= 3 then raise exception 'ظرفیت تیم تکمیل شده است؛ حداکثر سه نفر.'; end if;
    insert into public.team_members(team_id, user_id, role) values (v_team_id, v_uid, 'member');
    update public.team_invitations set status = 'accepted', responded_at = pg_catalog.now()
    where id = p_invitation_id;
  else
    update public.team_invitations set status = 'declined', responded_at = pg_catalog.now()
    where id = p_invitation_id;
  end if;
end;
$$;
revoke all on function public.respond_team_invitation(uuid, boolean) from public, anon;
grant execute on function public.respond_team_invitation(uuid, boolean) to authenticated;

create or replace function public.leave_team()
returns void
language plpgsql security definer set search_path = ''
as $$
declare
  v_uid uuid := (select auth.uid());
  v_team_id uuid;
  v_role text;
  v_next_captain uuid;
begin
  if v_uid is null then raise exception 'ابتدا وارد حساب کاربری شوید.'; end if;
  perform public.require_my_single_session();
  select team_id, role into v_team_id, v_role
  from public.team_members where user_id = v_uid;
  if v_team_id is null then raise exception 'شما عضو هیچ تیمی نیستید.'; end if;

  perform 1 from public.teams where id = v_team_id for update;
  if exists (
    select 1
    from public.exam_team_registrations etr
    join public.exams e on e.id = etr.exam_id
    where etr.team_id = v_team_id
      and pg_catalog.now() < coalesce(e.end_at_override, e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes))
  ) then
    raise exception 'تا پایان مسابقه فعال، خروج از تیم مجاز نیست.';
  end if;

  if v_role = 'captain' then
    select user_id into v_next_captain
    from public.team_members
    where team_id = v_team_id and user_id <> v_uid
    order by joined_at asc, user_id asc
    limit 1;

    if v_next_captain is null then
      delete from public.teams where id = v_team_id;
      return;
    end if;

    update public.team_members set role = 'captain'
    where team_id = v_team_id and user_id = v_next_captain;
    update public.teams set captain_id = v_next_captain where id = v_team_id;
  end if;

  delete from public.team_members where team_id = v_team_id and user_id = v_uid;
  update public.team_invitations
  set status = 'cancelled', responded_at = pg_catalog.now()
  where team_id = v_team_id and invited_by = v_uid and status = 'pending';
end;
$$;
revoke all on function public.leave_team() from public, anon;
grant execute on function public.leave_team() to authenticated;

-- A participant can choose individual registration even while they belong to a team.
-- Only the captain can register the team, and a participant/team cannot be registered twice.
create or replace function public.register_for_exam(p_exam_id uuid, p_team_id uuid default null)
returns void
language plpgsql security definer set search_path = ''
as $$
declare
  v_uid uuid := (select auth.uid());
  v_starts_at timestamptz;
  v_end_at timestamptz;
  v_allow_late boolean;
  v_registration_closes_at timestamptz;
begin
  if v_uid is null then raise exception 'ابتدا وارد حساب کاربری شوید.'; end if;
  perform public.require_my_single_session();
  perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(v_uid::text, 0));

  select e.starts_at,
         coalesce(e.end_at_override, e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes)),
         e.allow_late_registration,
         e.registration_closes_at
    into v_starts_at, v_end_at, v_allow_late, v_registration_closes_at
  from public.exams e where e.id = p_exam_id and e.is_published;
  if v_starts_at is null then raise exception 'مسابقه پیدا نشد یا منتشر نشده است.'; end if;

  if pg_catalog.now() >= v_starts_at then
    if not v_allow_late or (v_registration_closes_at is not null and pg_catalog.now() >= v_registration_closes_at) then
      raise exception 'مهلت ثبت‌نام به پایان رسیده است.';
    end if;
  end if;
  if pg_catalog.now() >= v_end_at then raise exception 'مسابقه به پایان رسیده است.'; end if;

  if p_team_id is null then
    if exists (
      select 1 from public.exam_team_registrations etr
      join public.team_members tm on tm.team_id = etr.team_id
      where etr.exam_id = p_exam_id and tm.user_id = v_uid
    ) then raise exception 'تیم شما قبلاً در این مسابقه ثبت‌نام کرده است.'; end if;
    insert into public.exam_registrations(exam_id, user_id)
    values (p_exam_id, v_uid) on conflict do nothing;
  else
    if not exists (
      select 1 from public.team_members tm
      where tm.team_id = p_team_id and tm.user_id = v_uid and tm.role = 'captain'
    ) then raise exception 'ثبت‌نام تیمی فقط توسط کاپیتان امکان‌پذیر است.'; end if;
    perform 1 from public.teams where id = p_team_id for update;
    if (select count(*) from public.team_members where team_id = p_team_id) > 3 then
      raise exception 'تعداد اعضای تیم از حد مجاز بیشتر است.';
    end if;
    if exists (
      select 1 from public.exam_registrations er
      join public.team_members tm on tm.user_id = er.user_id
      where er.exam_id = p_exam_id and tm.team_id = p_team_id
    ) then raise exception 'یکی از اعضای تیم قبلاً به‌صورت انفرادی ثبت‌نام کرده است.'; end if;
    insert into public.exam_team_registrations(exam_id, team_id, registered_by)
    values (p_exam_id, p_team_id, v_uid) on conflict do nothing;
  end if;
end;
$$;
revoke all on function public.register_for_exam(uuid, uuid) from public, anon;
grant execute on function public.register_for_exam(uuid, uuid) to authenticated;

-- Open/close late registration, adjust the finish time, publish results later, and edit the announcement/tags.
create or replace function public.admin_update_contest_controls(
  p_exam_id uuid,
  p_end_at_override timestamptz,
  p_allow_late_registration boolean,
  p_registration_closes_at timestamptz,
  p_results_release_at timestamptz,
  p_announcement text,
  p_tags text[]
)
returns void
language plpgsql security definer set search_path = ''
as $$
declare v_start timestamptz;
begin
  if not (select public.is_admin()) then raise exception 'فقط مدیر می‌تواند تنظیمات مسابقه را تغییر دهد.'; end if;
  select starts_at into v_start from public.exams where id = p_exam_id for update;
  if v_start is null then raise exception 'مسابقه پیدا نشد.'; end if;
  if p_end_at_override is not null and p_end_at_override <= greatest(v_start, pg_catalog.now() - interval '1 minute') then
    raise exception 'زمان پایان جدید باید بعد از زمان شروع و زمان فعلی باشد.';
  end if;
  if p_registration_closes_at is not null and p_registration_closes_at <= v_start then
    raise exception 'زمان بسته‌شدن ثبت‌نام باید بعد از شروع مسابقه باشد.';
  end if;
  if p_results_release_at is not null and p_results_release_at < v_start then
    raise exception 'زمان انتشار کارنامه معتبر نیست.';
  end if;
  update public.exams set
    end_at_override = p_end_at_override,
    allow_late_registration = coalesce(p_allow_late_registration, false),
    registration_closes_at = p_registration_closes_at,
    results_release_at = p_results_release_at,
    announcement = nullif(btrim(p_announcement), ''),
    tags = coalesce(p_tags, '{}')
  where id = p_exam_id;
end;
$$;
revoke all on function public.admin_update_contest_controls(uuid, timestamptz, boolean, timestamptz, timestamptz, text, text[]) from public, anon;
grant execute on function public.admin_update_contest_controls(uuid, timestamptz, boolean, timestamptz, timestamptz, text, text[]) to authenticated;

-- Use the active end time for the live exam gate.
create or replace function public.start_exam(p_exam_id uuid)
returns void
language plpgsql security definer set search_path = ''
as $$
declare v_uid uuid := (select auth.uid()); v_team_id uuid; v_captain_id uuid;
begin
  if v_uid is null then raise exception 'ورود به حساب کاربری الزامی است.'; end if;
  perform public.require_my_single_session();
  if not exists (
    select 1 from public.exams e
    where e.id = p_exam_id and e.is_published
      and pg_catalog.now() >= e.starts_at
      and pg_catalog.now() < coalesce(e.end_at_override, e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes))
  ) then raise exception 'این مسابقه در حال حاضر فعال نیست.'; end if;

  select etr.team_id, t.captain_id into v_team_id, v_captain_id
  from public.exam_team_registrations etr
  join public.teams t on t.id = etr.team_id
  join public.team_members tm on tm.team_id = etr.team_id
  where etr.exam_id = p_exam_id and tm.user_id = v_uid
  limit 1;

  if v_team_id is not null then
    insert into public.exam_attempts(exam_id, user_id, team_id)
    values (p_exam_id, v_captain_id, v_team_id)
    on conflict (exam_id, user_id) do nothing;
  else
    if not exists (
      select 1 from public.exam_registrations
      where exam_id = p_exam_id and user_id = v_uid
    ) then raise exception 'برای شرکت در مسابقه باید ثبت‌نام کرده باشید.'; end if;
    insert into public.exam_attempts(exam_id, user_id)
    values (p_exam_id, v_uid) on conflict (exam_id, user_id) do nothing;
  end if;
end;
$$;
revoke all on function public.start_exam(uuid) from public, anon;
grant execute on function public.start_exam(uuid) to authenticated;

create or replace function public.save_exam_answer(
  p_exam_id uuid,
  p_question_number integer,
  p_answer numeric
)
returns void
language plpgsql security definer set search_path = ''
as $$
declare
  v_uid uuid := (select auth.uid());
  v_team_id uuid;
  v_captain_id uuid;
begin
  if v_uid is null then raise exception 'ابتدا وارد حساب کاربری شوید.'; end if;
  perform public.require_my_single_session();
  if not exists (
    select 1 from public.exams e
    where e.id = p_exam_id and e.is_published
      and pg_catalog.now() >= e.starts_at
      and pg_catalog.now() < coalesce(e.end_at_override, e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes))
  ) then raise exception 'زمان پاسخ‌دهی این مسابقه به پایان رسیده یا هنوز شروع نشده است.'; end if;
  if not exists (select 1 from public.exam_questions q where q.exam_id = p_exam_id and q.question_number = p_question_number) then
    raise exception 'شماره سؤال نامعتبر است.';
  end if;

  select etr.team_id, t.captain_id into v_team_id, v_captain_id
  from public.exam_team_registrations etr
  join public.teams t on t.id = etr.team_id
  join public.team_members tm on tm.team_id = etr.team_id
  where etr.exam_id = p_exam_id and tm.user_id = v_uid
  limit 1;

  if v_team_id is not null then
    if not exists (select 1 from public.exam_attempts a where a.exam_id = p_exam_id and a.team_id = v_team_id) then
      raise exception 'ابتدا مسابقه را باز کنید.';
    end if;
    if p_answer is null then
      delete from public.exam_answers where exam_id = p_exam_id and team_id = v_team_id and question_number = p_question_number;
    else
      insert into public.exam_answers(exam_id, user_id, team_id, question_number, answer)
      values (p_exam_id, v_captain_id, v_team_id, p_question_number, p_answer)
      on conflict (exam_id, team_id, question_number) where team_id is not null
      do update set answer = excluded.answer, updated_at = pg_catalog.now();
    end if;
  else
    if not exists (select 1 from public.exam_attempts a where a.exam_id = p_exam_id and a.user_id = v_uid and a.team_id is null) then
      raise exception 'ابتدا مسابقه را باز کنید.';
    end if;
    if p_answer is null then
      delete from public.exam_answers where exam_id = p_exam_id and team_id is null and user_id = v_uid and question_number = p_question_number;
    else
      insert into public.exam_answers(exam_id, user_id, question_number, answer)
      values (p_exam_id, v_uid, p_question_number, p_answer)
      on conflict (exam_id, user_id, question_number)
      do update set answer = excluded.answer, updated_at = pg_catalog.now();
    end if;
  end if;
end;
$$;
revoke all on function public.save_exam_answer(uuid, integer, numeric) from public, anon;
grant execute on function public.save_exam_answer(uuid, integer, numeric) to authenticated;

-- Keep grading and automated cron aligned with the live, overridable end time.
create or replace function public.finalize_exam_internal(p_exam_id uuid)
returns void
language plpgsql security definer set search_path = ''
as $$
begin
  if not exists (
    select 1 from public.exams e
    where e.id = p_exam_id and e.is_published
      and pg_catalog.now() >= coalesce(e.end_at_override, e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes))
  ) then return; end if;

  with participants as (
    select er.user_id, null::uuid as team_id
    from public.exam_registrations er where er.exam_id = p_exam_id
    union
    select a.user_id, null::uuid as team_id
    from public.exam_attempts a
    where a.exam_id = p_exam_id and a.team_id is null
    union all
    select t.captain_id as user_id, etr.team_id
    from public.exam_team_registrations etr
    join public.teams t on t.id = etr.team_id
    where etr.exam_id = p_exam_id
  )
  insert into public.exam_results (
    exam_id, user_id, team_id, score, max_score, correct_count, question_count, graded_at
  )
  select
    p_exam_id, p.user_id, p.team_id,
    coalesce(sum(case when a.answer = k.correct_answer then q.points else 0 end), 0),
    coalesce(sum(q.points), 0),
    count(*) filter (where a.answer = k.correct_answer)::integer,
    count(*)::integer,
    pg_catalog.now()
  from participants p
  cross join public.exam_questions q
  left join public.exam_answers a
    on a.exam_id = p_exam_id and a.question_number = q.question_number
   and ((p.team_id is null and a.team_id is null and a.user_id = p.user_id)
     or (p.team_id is not null and a.team_id = p.team_id))
  left join public.exam_answer_keys k
    on k.exam_id = p_exam_id and k.question_number = q.question_number
  where q.exam_id = p_exam_id
  group by p.user_id, p.team_id
  on conflict (exam_id, user_id) do update set
    team_id = excluded.team_id,
    score = excluded.score,
    max_score = excluded.max_score,
    correct_count = excluded.correct_count,
    question_count = excluded.question_count,
    graded_at = excluded.graded_at;
end;
$$;
revoke all on function public.finalize_exam_internal(uuid) from public, anon, authenticated;

create or replace function public.finalize_all_expired_exams()
returns void
language plpgsql security definer set search_path = ''
as $$
declare v_exam_id uuid;
begin
  for v_exam_id in
    select e.id from public.exams e
    where e.is_published
      and pg_catalog.now() >= coalesce(e.end_at_override, e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes))
      and (
        exists (
          select 1 from public.exam_registrations er
          left join public.exam_results r on r.exam_id = er.exam_id and r.user_id = er.user_id
          where er.exam_id = e.id and r.id is null
        )
        or exists (
          select 1 from public.exam_team_registrations etr
          left join public.exam_results r on r.exam_id = etr.exam_id and r.team_id = etr.team_id
          where etr.exam_id = e.id and r.id is null
        )
        or exists (
          select 1 from public.exam_attempts a
          left join public.exam_results r on r.exam_id = a.exam_id and r.user_id = a.user_id
          where a.exam_id = e.id and a.team_id is null and r.id is null
        )
      )
  loop
    perform public.finalize_exam_internal(v_exam_id);
  end loop;
end;
$$;
revoke all on function public.finalize_all_expired_exams() from public, anon, authenticated;

create or replace function public.get_exam_question_resource(p_exam_id uuid)
returns table(question_pdf_url text, question_file_path text)
language plpgsql stable security definer set search_path = ''
as $$
declare v_uid uuid := (select auth.uid());
begin
  if v_uid is null then raise exception 'ابتدا وارد حساب کاربری شوید.'; end if;
  if not (select public.is_admin()) then
    if not exists (
      select 1 from public.exams e
      where e.id = p_exam_id
        and pg_catalog.now() >= e.starts_at
        and pg_catalog.now() < coalesce(e.end_at_override, e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes))
    ) then
      raise exception 'فایل صورت مسابقه فقط در زمان برگزاری قابل مشاهده است.';
    end if;
    if not exists (select 1 from public.exam_registrations er where er.exam_id = p_exam_id and er.user_id = v_uid)
       and not exists (
         select 1 from public.exam_team_registrations etr
         join public.team_members tm on tm.team_id = etr.team_id
         where etr.exam_id = p_exam_id and tm.user_id = v_uid
       ) then
      raise exception 'برای مشاهده صورت مسابقه باید ثبت‌نام کرده باشید.';
    end if;
  end if;
  return query select r.question_pdf_url, r.question_file_path
  from public.exam_question_resources r where r.exam_id = p_exam_id;
end;
$$;
revoke all on function public.get_exam_question_resource(uuid) from public, anon;
grant execute on function public.get_exam_question_resource(uuid) to authenticated;

-- Result visibility is controlled by the administrator's release timestamp.
drop policy if exists "results_read_after_end" on public.exam_results;
create policy "results_read_after_release" on public.exam_results for select to authenticated
using (
  (select public.is_admin())
  or (
    pg_catalog.now() >= coalesce(
      (select e.results_release_at from public.exams e where e.id = exam_results.exam_id),
      (select coalesce(e.end_at_override, e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes))
       from public.exams e where e.id = exam_results.exam_id)
    )
    and (
      user_id = (select auth.uid())
      or (team_id is not null and (select public.is_team_member(team_id)))
    )
  )
);

-- Detailed review is available only after result publication.
create or replace function public.get_exam_review(p_exam_id uuid)
returns table (
  question_number integer,
  points numeric,
  submitted_answer numeric,
  correct_answer numeric,
  is_correct boolean
)
language plpgsql stable security definer set search_path = ''
as $$
declare
  v_uid uuid := (select auth.uid());
  v_team_id uuid;
  v_release_at timestamptz;
begin
  if v_uid is null then raise exception 'ابتدا وارد حساب کاربری شوید.'; end if;
  perform public.require_my_single_session();

  select coalesce(
    e.results_release_at,
    coalesce(e.end_at_override, e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes))
  ) into v_release_at
  from public.exams e where e.id = p_exam_id and e.is_published;
  if v_release_at is null then raise exception 'مسابقه پیدا نشد.'; end if;
  if pg_catalog.now() < v_release_at and not (select public.is_admin()) then
    raise exception 'کارنامه این مسابقه هنوز منتشر نشده است.';
  end if;

  select etr.team_id into v_team_id
  from public.exam_team_registrations etr
  join public.team_members tm on tm.team_id = etr.team_id
  where etr.exam_id = p_exam_id and tm.user_id = v_uid
  limit 1;

  if not (select public.is_admin()) and not exists (
    select 1 from public.exam_results r
    where r.exam_id = p_exam_id
      and ((v_team_id is not null and r.team_id = v_team_id)
        or (v_team_id is null and r.user_id = v_uid and r.team_id is null))
  ) then
    raise exception 'برای مشاهده کارنامه این مسابقه مجاز نیستید.';
  end if;

  return query
  select q.question_number, q.points, a.answer, k.correct_answer,
         (a.answer is not null and a.answer = k.correct_answer) as is_correct
  from public.exam_questions q
  left join public.exam_answer_keys k
    on k.exam_id = q.exam_id and k.question_number = q.question_number
  left join public.exam_answers a
    on a.exam_id = q.exam_id and a.question_number = q.question_number
   and (
     (v_team_id is not null and a.team_id = v_team_id)
     or (v_team_id is null and a.team_id is null and a.user_id = v_uid)
   )
  where q.exam_id = p_exam_id
  order by q.question_number;
end;
$$;
revoke all on function public.get_exam_review(uuid) from public, anon;
grant execute on function public.get_exam_review(uuid) to authenticated;

-- Admin can manage accounts through Auth; this deletes the Auth user and cascades their profile/data.
create or replace function public.admin_delete_user(p_user_id uuid)
returns void
language plpgsql security definer set search_path = ''
as $$
begin
  if not (select public.is_admin()) then raise exception 'فقط مدیر می‌تواند کاربر حذف کند.'; end if;
  if p_user_id = (select auth.uid()) then raise exception 'حذف حساب مدیر فعلی از داخل این بخش مجاز نیست.'; end if;
  delete from auth.users where id = p_user_id;
  if not found then raise exception 'کاربر پیدا نشد.'; end if;
end;
$$;
revoke all on function public.admin_delete_user(uuid) from public, anon;
grant execute on function public.admin_delete_user(uuid) to authenticated;

-- Add session validity to all team/result reads; stale devices lose protected data access.
drop policy if exists "teams_read_members" on public.teams;
create policy "teams_read_members" on public.teams for select to authenticated
using (
  (select public.is_my_single_session_active())
  and (
    (select public.is_team_member(id))
    or (select public.is_admin())
    or exists (
      select 1 from public.team_invitations ti
      where ti.team_id = teams.id and ti.invited_user_id = (select auth.uid()) and ti.status = 'pending'
    )
  )
);
drop policy if exists "team_members_read_team" on public.team_members;
create policy "team_members_read_team" on public.team_members for select to authenticated
using ((select public.is_my_single_session_active()) and ((select public.is_team_member(team_id)) or (select public.is_admin())));
drop policy if exists "team_invites_read_participants" on public.team_invitations;
create policy "team_invites_read_participants" on public.team_invitations for select to authenticated
using ((select public.is_my_single_session_active()) and (invited_user_id = (select auth.uid()) or invited_by = (select auth.uid()) or (select public.is_admin())));
drop policy if exists "exam_registrations_read_owner_admin" on public.exam_registrations;
create policy "exam_registrations_read_owner_admin" on public.exam_registrations for select to authenticated
using ((select public.is_my_single_session_active()) and (user_id = (select auth.uid()) or (select public.is_admin())));
drop policy if exists "exam_team_registrations_read_members" on public.exam_team_registrations;
create policy "exam_team_registrations_read_members" on public.exam_team_registrations for select to authenticated
using ((select public.is_my_single_session_active()) and ((select public.is_team_member(team_id)) or (select public.is_admin())));
drop policy if exists "answers_read_own_or_admin" on public.exam_answers;
create policy "answers_read_own_or_admin" on public.exam_answers for select to authenticated
using ((select public.is_my_single_session_active()) and (
  user_id = (select auth.uid())
  or (team_id is not null and (select public.is_team_member(team_id)))
  or (select public.is_admin())
));
drop policy if exists "results_read_after_release" on public.exam_results;
create policy "results_read_after_release" on public.exam_results for select to authenticated
using (
  (select public.is_my_single_session_active())
  and (
    (select public.is_admin())
    or (
      pg_catalog.now() >= coalesce(
        (select e.results_release_at from public.exams e where e.id = exam_results.exam_id),
        (select coalesce(e.end_at_override, e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes))
         from public.exams e where e.id = exam_results.exam_id)
      )
      and (user_id = (select auth.uid()) or (team_id is not null and (select public.is_team_member(team_id))))
    )
  )
);
drop policy if exists "attempts_read_own_or_admin" on public.exam_attempts;
create policy "attempts_read_own_or_admin" on public.exam_attempts for select to authenticated
using ((select public.is_my_single_session_active()) and (
  user_id = (select auth.uid())
  or (team_id is not null and (select public.is_team_member(team_id)))
  or (select public.is_admin())
));

-- Enable Supabase Realtime for shared team answers.
do $$
begin
  alter publication supabase_realtime add table public.exam_answers;
exception
  when duplicate_object then null;
  when undefined_object then null;
end;
$$;



-- Pending invites count toward the three-person team capacity as well.
create or replace function public.enforce_team_invitation_limit()
returns trigger
language plpgsql security definer set search_path = ''
as $
declare v_members integer; v_pending integer;
begin
  if new.status <> 'pending' then return new; end if;
  perform 1 from public.teams where id = new.team_id for update;
  select count(*) into v_members from public.team_members where team_id = new.team_id;
  select count(*) into v_pending from public.team_invitations
    where team_id = new.team_id and status = 'pending' and id is distinct from new.id;
  if v_members + v_pending >= 3 then
    raise exception 'ظرفیت تیم تکمیل است؛ هر تیم حداکثر سه نفر با احتساب کاپیتان دارد.';
  end if;
  return new;
end;
$;
drop trigger if exists team_invitation_limit on public.team_invitations;
create trigger team_invitation_limit
before insert or update of status on public.team_invitations
for each row execute function public.enforce_team_invitation_limit();


commit;
