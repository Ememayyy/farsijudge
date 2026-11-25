-- FarsiJudge feature migration 002
-- Run once in Supabase SQL Editor after 001_initial_schema.sql.
begin;

-- Usernames are public identifiers for invitations; authentication remains email/password.
alter table public.profiles add column if not exists username text;
update public.profiles
set username = 'user_' || substr(replace(id::text, '-', ''), 1, 12)
where username is null or btrim(username) = '';
create unique index if not exists profiles_username_lower_uidx
  on public.profiles (lower(username));
do $$
begin
  if not exists (
    select 1 from pg_constraint
    where conrelid = 'public.profiles'::regclass and conname = 'profiles_username_format'
  ) then
    alter table public.profiles add constraint profiles_username_format
      check (username ~ '^[a-zA-Z0-9_]{3,24}$');
  end if;
end;
$$;
alter table public.profiles alter column username set not null;
grant update (username) on public.profiles to authenticated;

-- Store question resources separately so unregistered users cannot query their URLs or paths.
create table if not exists public.exam_question_resources (
  exam_id uuid primary key references public.exams(id) on delete cascade,
  question_pdf_url text,
  question_file_path text,
  updated_at timestamptz not null default now()
);
alter table public.exam_question_resources enable row level security;
-- No direct table grants: the registration-aware SECURITY DEFINER RPCs below are the only access path.

-- One user may belong to at most one team. A team has one captain and at most three more members.
create table if not exists public.teams (
  id uuid primary key default gen_random_uuid(),
  name text not null check (char_length(btrim(name)) between 2 and 40),
  captain_id uuid not null references auth.users(id) on delete cascade,
  created_at timestamptz not null default now()
);

create table if not exists public.team_members (
  team_id uuid not null references public.teams(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null check (role in ('captain', 'member')),
  joined_at timestamptz not null default now(),
  primary key (team_id, user_id),
  unique (user_id)
);

create table if not exists public.team_invitations (
  id uuid primary key default gen_random_uuid(),
  team_id uuid not null references public.teams(id) on delete cascade,
  invited_user_id uuid not null references auth.users(id) on delete cascade,
  invited_by uuid not null references auth.users(id) on delete cascade,
  status text not null default 'pending' check (status in ('pending', 'accepted', 'declined', 'cancelled')),
  created_at timestamptz not null default now(),
  responded_at timestamptz,
  unique (team_id, invited_user_id)
);
create index if not exists team_invitations_user_status_idx
  on public.team_invitations(invited_user_id, status);

-- Registration is separate from entering the exam. It must happen before starts_at.
create table if not exists public.exam_registrations (
  exam_id uuid not null references public.exams(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  registered_at timestamptz not null default now(),
  primary key (exam_id, user_id)
);
create table if not exists public.exam_team_registrations (
  exam_id uuid not null references public.exams(id) on delete cascade,
  team_id uuid not null references public.teams(id) on delete cascade,
  registered_by uuid not null references auth.users(id),
  registered_at timestamptz not null default now(),
  primary key (exam_id, team_id)
);

alter table public.exam_attempts add column if not exists team_id uuid references public.teams(id) on delete cascade;
create unique index if not exists exam_attempts_exam_team_uidx
  on public.exam_attempts(exam_id, team_id) where team_id is not null;

alter table public.exam_answers add column if not exists team_id uuid references public.teams(id) on delete cascade;
create unique index if not exists exam_answers_exam_team_question_uidx
  on public.exam_answers(exam_id, team_id, question_number) where team_id is not null;
alter table public.exam_results add column if not exists team_id uuid references public.teams(id) on delete cascade;
create index if not exists exam_results_team_idx on public.exam_results(team_id, graded_at desc);

-- Keep usernames populated for new Supabase Auth signups.
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_username text;
begin
  v_username := coalesce(
    nullif(lower(btrim(new.raw_user_meta_data ->> 'username')), ''),
    'user_' || substr(replace(new.id::text, '-', ''), 1, 12)
  );
  if v_username !~ '^[a-zA-Z0-9_]{3,24}$' then
    raise exception 'نام کاربری باید ۳ تا ۲۴ حرف انگلیسی، عدد یا زیرخط باشد.';
  end if;
  insert into public.profiles (id, full_name, username)
  values (
    new.id,
    coalesce(nullif(btrim(new.raw_user_meta_data ->> 'full_name'), ''), 'کاربر جدید'),
    v_username
  )
  on conflict (id) do update
    set username = coalesce(public.profiles.username, excluded.username);
  return new;
end;
$$;

-- SECURITY DEFINER helpers prevent recursive RLS policies on team membership.
create or replace function public.is_team_member(p_team_id uuid)
returns boolean
language sql stable security definer set search_path = ''
as $$
  select exists (
    select 1 from public.team_members tm
    where tm.team_id = p_team_id and tm.user_id = (select auth.uid())
  );
$$;

create or replace function public.is_teammate(p_user_id uuid)
returns boolean
language sql stable security definer set search_path = ''
as $$
  select exists (
    select 1
    from public.team_members mine
    join public.team_members theirs on theirs.team_id = mine.team_id
    where mine.user_id = (select auth.uid()) and theirs.user_id = p_user_id
  );
$$;

revoke all on function public.is_team_member(uuid) from public, anon;
revoke all on function public.is_teammate(uuid) from public, anon;
grant execute on function public.is_team_member(uuid) to authenticated;
grant execute on function public.is_teammate(uuid) to authenticated;

-- Team creation: creator becomes captain and membership is exclusive.
create or replace function public.create_team(p_name text)
returns uuid
language plpgsql security definer set search_path = ''
as $$
declare v_team_id uuid;
begin
  if (select auth.uid()) is null then raise exception 'ابتدا وارد حساب کاربری شوید.'; end if;
  if nullif(btrim(p_name), '') is null or char_length(btrim(p_name)) > 40 then
    raise exception 'نام تیم باید بین ۲ تا ۴۰ کاراکتر باشد.';
  end if;
  if exists (select 1 from public.team_members where user_id = (select auth.uid())) then
    raise exception 'شما هم‌اکنون عضو یک تیم هستید.';
  end if;
  insert into public.teams(name, captain_id) values (btrim(p_name), (select auth.uid()))
  returning id into v_team_id;
  insert into public.team_members(team_id, user_id, role)
  values (v_team_id, (select auth.uid()), 'captain');
  return v_team_id;
end;
$$;
revoke all on function public.create_team(text) from public, anon;
grant execute on function public.create_team(text) to authenticated;

-- Invite by username or exact email without exposing email addresses through profile queries.
create or replace function public.invite_team_member(p_identifier text)
returns uuid
language plpgsql security definer set search_path = ''
as $$
declare
  v_team_id uuid;
  v_target uuid;
  v_invitation_id uuid;
  v_member_count integer;
  v_pending_count integer;
begin
  select tm.team_id into v_team_id
  from public.team_members tm
  where tm.user_id = (select auth.uid()) and tm.role = 'captain';
  if v_team_id is null then raise exception 'فقط کاپیتان تیم می‌تواند دعوت‌نامه بفرستد.'; end if;

  perform 1 from public.teams where id = v_team_id for update;
  select p.id into v_target
  from public.profiles p
  join auth.users u on u.id = p.id
  where lower(p.username) = lower(btrim(p_identifier))
     or lower(u.email) = lower(btrim(p_identifier))
  limit 1;
  if v_target is null then raise exception 'کاربری با این نام کاربری یا ایمیل پیدا نشد.'; end if;
  if v_target = (select auth.uid()) then raise exception 'نمی‌توانید خودتان را دعوت کنید.'; end if;
  if exists (select 1 from public.team_members where user_id = v_target) then
    raise exception 'این کاربر هم‌اکنون عضو یک تیم است.';
  end if;

  select count(*) into v_member_count from public.team_members where team_id = v_team_id;
  select count(*) into v_pending_count from public.team_invitations
    where team_id = v_team_id and status = 'pending';
  if v_member_count + v_pending_count >= 4 then
    raise exception 'ظرفیت تیم تکمیل است؛ هر تیم حداکثر ۴ عضو دارد.';
  end if;

  insert into public.team_invitations(team_id, invited_user_id, invited_by)
  values (v_team_id, v_target, (select auth.uid()))
  on conflict (team_id, invited_user_id) do update
    set status = 'pending', invited_by = excluded.invited_by, created_at = pg_catalog.now(), responded_at = null
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
declare v_team_id uuid; v_member_count integer;
begin
  select i.team_id into v_team_id
  from public.team_invitations i
  where i.id = p_invitation_id and i.invited_user_id = (select auth.uid()) and i.status = 'pending'
  for update;
  if v_team_id is null then raise exception 'این دعوت‌نامه معتبر یا فعال نیست.'; end if;

  perform 1 from public.teams where id = v_team_id for update;
  if p_accept then
    if exists (
      select 1
      from public.exam_team_registrations etr
      join public.exams e on e.id = etr.exam_id
      where etr.team_id = v_team_id
        and pg_catalog.now() < e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes)
    ) then
      raise exception 'پس از ثبت‌نام تیم در یک آزمون پیش‌رو، ترکیب اعضا تا پایان آن آزمون قفل می‌شود.';
    end if;
    if exists (select 1 from public.team_members where user_id = (select auth.uid())) then
      raise exception 'ابتدا باید از تیم فعلی خارج شوید.';
    end if;
    select count(*) into v_member_count from public.team_members where team_id = v_team_id;
    if v_member_count >= 4 then raise exception 'ظرفیت تیم تکمیل شده است.'; end if;
    insert into public.team_members(team_id, user_id, role)
    values (v_team_id, (select auth.uid()), 'member');
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

-- Register individually or as a team, only before the scheduled start.
create or replace function public.register_for_exam(p_exam_id uuid, p_team_id uuid default null)
returns void
language plpgsql security definer set search_path = ''
as $$
declare v_uid uuid := (select auth.uid());
begin
  if v_uid is null then raise exception 'ابتدا وارد حساب کاربری شوید.'; end if;
  if not exists (select 1 from public.exams e where e.id = p_exam_id and e.is_published) then
    raise exception 'آزمون پیدا نشد یا منتشر نشده است.';
  end if;
  if not exists (select 1 from public.exams e where e.id = p_exam_id and pg_catalog.now() < e.starts_at) then
    raise exception 'مهلت ثبت‌نام این آزمون به پایان رسیده است.';
  end if;

  if p_team_id is null then
    if exists (select 1 from public.team_members where user_id = v_uid) then
      raise exception 'شما عضو تیم هستید؛ ثبت‌نام این آزمون باید از طریق کاپیتان تیم انجام شود.';
    end if;
    if exists (
      select 1 from public.exam_team_registrations etr
      join public.team_members tm on tm.team_id = etr.team_id
      where etr.exam_id = p_exam_id and tm.user_id = v_uid
    ) then raise exception 'تیم شما قبلاً در این آزمون ثبت‌نام کرده است.'; end if;
    insert into public.exam_registrations(exam_id, user_id)
    values (p_exam_id, v_uid) on conflict do nothing;
  else
    if not exists (
      select 1 from public.team_members tm
      where tm.team_id = p_team_id and tm.user_id = v_uid and tm.role = 'captain'
    ) then raise exception 'ثبت‌نام تیمی فقط توسط کاپیتان امکان‌پذیر است.'; end if;
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

-- Replace start_exam: registration is mandatory and the team has one shared attempt.
create or replace function public.start_exam(p_exam_id uuid)
returns void
language plpgsql security definer set search_path = ''
as $$
declare v_uid uuid := (select auth.uid()); v_team_id uuid; v_captain_id uuid;
begin
  if v_uid is null then raise exception 'ورود به حساب کاربری الزامی است.'; end if;
  if not exists (
    select 1 from public.exams e
    where e.id = p_exam_id and e.is_published
      and pg_catalog.now() >= e.starts_at
      and pg_catalog.now() < e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes)
  ) then raise exception 'این آزمون در حال حاضر فعال نیست.'; end if;

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
    ) then raise exception 'برای شرکت در آزمون باید قبل از شروع آن ثبت‌نام کنید.'; end if;
    insert into public.exam_attempts(exam_id, user_id)
    values (p_exam_id, v_uid) on conflict (exam_id, user_id) do nothing;
  end if;
end;
$$;
revoke all on function public.start_exam(uuid) from public, anon;
grant execute on function public.start_exam(uuid) to authenticated;

-- All team members read the same answer rows. Saves are accepted only during the exam window.
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
  if not exists (
    select 1 from public.exams e
    where e.id = p_exam_id and e.is_published
      and pg_catalog.now() >= e.starts_at
      and pg_catalog.now() < e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes)
  ) then raise exception 'زمان پاسخ‌دهی این آزمون به پایان رسیده یا هنوز شروع نشده است.'; end if;
  if not exists (select 1 from public.exam_questions q where q.exam_id = p_exam_id and q.question_number = p_question_number) then
    raise exception 'شماره سؤال نامعتبر است.';
  end if;

  select etr.team_id, t.captain_id into v_team_id, v_captain_id
  from public.exam_team_registrations etr
  join public.teams t on t.id = etr.team_id
  join public.team_members tm on tm.team_id = etr.team_id
  where etr.exam_id = p_exam_id and tm.user_id = v_uid
  limit 1;

  if p_answer is null then
    if v_team_id is not null then
      delete from public.exam_answers where exam_id = p_exam_id and team_id = v_team_id and question_number = p_question_number;
    else
      delete from public.exam_answers where exam_id = p_exam_id and team_id is null and user_id = v_uid and question_number = p_question_number;
    end if;
    return;
  end if;

  if v_team_id is not null then
    if not exists (select 1 from public.exam_attempts a where a.exam_id = p_exam_id and a.team_id = v_team_id) then
      raise exception 'ابتدا آزمون را باز کنید.';
    end if;
    insert into public.exam_answers(exam_id, user_id, team_id, question_number, answer)
    values (p_exam_id, v_captain_id, v_team_id, p_question_number, p_answer)
    on conflict (exam_id, team_id, question_number) where team_id is not null
    do update set answer = excluded.answer, updated_at = pg_catalog.now();
  else
    if not exists (select 1 from public.exam_attempts a where a.exam_id = p_exam_id and a.user_id = v_uid and a.team_id is null) then
      raise exception 'ابتدا آزمون را باز کنید.';
    end if;
    insert into public.exam_answers(exam_id, user_id, question_number, answer)
    values (p_exam_id, v_uid, p_question_number, p_answer)
    on conflict (exam_id, user_id, question_number)
    do update set answer = excluded.answer, updated_at = pg_catalog.now();
  end if;
end;
$$;
revoke all on function public.save_exam_answer(uuid, integer, numeric) from public, anon;
grant execute on function public.save_exam_answer(uuid, integer, numeric) to authenticated;

-- Team result rows use the captain's user_id and team_id; every team member can read them.
drop policy if exists "results_read_after_end" on public.exam_results;
create policy "results_read_after_end"
on public.exam_results for select to authenticated
using (
  (select public.is_admin())
  or (
    pg_catalog.now() >= (
      select e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes)
      from public.exams e where e.id = exam_results.exam_id
    )
    and (
      user_id = (select auth.uid())
      or (team_id is not null and (select public.is_team_member(team_id)))
    )
  )
);

-- Participants can read their own answers and all answers of their registered team.
drop policy if exists "answers_read_own_or_admin" on public.exam_answers;
create policy "answers_read_own_or_admin"
on public.exam_answers for select to authenticated
using (
  user_id = (select auth.uid())
  or (team_id is not null and (select public.is_team_member(team_id)))
  or (select public.is_admin())
);
drop policy if exists "answers_insert_during_exam" on public.exam_answers;
drop policy if exists "answers_update_during_exam" on public.exam_answers;
drop policy if exists "answers_delete_during_exam" on public.exam_answers;
revoke insert, update, delete on public.exam_answers from authenticated;

-- Admins can inspect registrations and manage user roles; members can inspect team registrations.
alter table public.teams enable row level security;
alter table public.team_members enable row level security;
alter table public.team_invitations enable row level security;
alter table public.exam_registrations enable row level security;
alter table public.exam_team_registrations enable row level security;

grant select on public.teams, public.team_members, public.team_invitations,
  public.exam_registrations, public.exam_team_registrations to authenticated;

drop policy if exists "profiles_read_self_or_admin" on public.profiles;
create policy "profiles_read_self_or_admin"
on public.profiles for select to authenticated
using (id = (select auth.uid()) or (select public.is_admin()) or (select public.is_teammate(id)));

drop policy if exists "teams_read_members" on public.teams;
create policy "teams_read_members" on public.teams for select to authenticated
using (
  (select public.is_team_member(id))
  or (select public.is_admin())
  or exists (
    select 1 from public.team_invitations ti
    where ti.team_id = teams.id and ti.invited_user_id = (select auth.uid()) and ti.status = 'pending'
  )
);

drop policy if exists "team_members_read_team" on public.team_members;
create policy "team_members_read_team" on public.team_members for select to authenticated
using ((select public.is_team_member(team_id)) or (select public.is_admin()));

drop policy if exists "team_invites_read_participants" on public.team_invitations;
create policy "team_invites_read_participants" on public.team_invitations for select to authenticated
using (invited_user_id = (select auth.uid()) or invited_by = (select auth.uid()) or (select public.is_admin()));

drop policy if exists "exam_registrations_read_owner_admin" on public.exam_registrations;
create policy "exam_registrations_read_owner_admin" on public.exam_registrations for select to authenticated
using (user_id = (select auth.uid()) or (select public.is_admin()));

drop policy if exists "exam_team_registrations_read_members" on public.exam_team_registrations;
create policy "exam_team_registrations_read_members" on public.exam_team_registrations for select to authenticated
using ((select public.is_team_member(team_id)) or (select public.is_admin()));

drop policy if exists "attempts_read_own_or_admin" on public.exam_attempts;
create policy "attempts_read_own_or_admin" on public.exam_attempts for select to authenticated
using (user_id = (select auth.uid()) or (team_id is not null and (select public.is_team_member(team_id))) or (select public.is_admin()));

-- Allow a user to see teammates' public profile details only.
drop policy if exists "profiles_read_teammates" on public.profiles;
create policy "profiles_read_teammates" on public.profiles for select to authenticated
using ((select public.is_teammate(id)));

-- Update grading so registered users and teams are graded, even if they submitted no answers.
create or replace function public.finalize_exam_internal(p_exam_id uuid)
returns void
language plpgsql security definer set search_path = ''
as $$
begin
  if not exists (
    select 1 from public.exams e
    where e.id = p_exam_id and e.is_published
      and pg_catalog.now() >= e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes)
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
    p_exam_id,
    p.user_id,
    p.team_id,
    coalesce(sum(case when a.answer = k.correct_answer then q.points else 0 end), 0),
    coalesce(sum(q.points), 0),
    count(*) filter (where a.answer = k.correct_answer)::integer,
    count(*)::integer,
    pg_catalog.now()
  from participants p
  cross join public.exam_questions q
  left join public.exam_answers a
    on a.exam_id = p_exam_id
   and a.question_number = q.question_number
   and (
     (p.team_id is null and a.team_id is null and a.user_id = p.user_id)
     or (p.team_id is not null and a.team_id = p.team_id)
   )
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
      and pg_catalog.now() >= e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes)
      and (
        exists (select 1 from public.exam_registrations er where er.exam_id = e.id)
        or exists (select 1 from public.exam_team_registrations etr where etr.exam_id = e.id)
      )
  loop
    perform public.finalize_exam_internal(v_exam_id);
  end loop;
end;
$$;
revoke all on function public.finalize_all_expired_exams() from public, anon, authenticated;

-- Admin editing replaces metadata, points and answer keys atomically, then regrades ended exams.
create or replace function public.edit_exam_with_answer_key(
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
language plpgsql security definer set search_path = ''
as $$
declare v_item jsonb; v_q integer; v_points numeric; v_answer numeric;
begin
  if not (select public.is_admin()) then raise exception 'فقط مدیر سامانه اجازه ویرایش آزمون را دارد.'; end if;
  if nullif(btrim(p_title), '') is null then raise exception 'عنوان آزمون الزامی است.'; end if;
  if p_starts_at is null then raise exception 'زمان شروع نامعتبر است.'; end if;
  if p_duration_minutes is null or p_duration_minutes < 1 or p_duration_minutes > 600 then
    raise exception 'مدت آزمون باید بین ۱ تا ۶۰۰ دقیقه باشد.';
  end if;
  if pg_catalog.jsonb_typeof(p_questions) <> 'array'
     or pg_catalog.jsonb_array_length(p_questions) < 1
     or pg_catalog.jsonb_array_length(p_questions) > 300 then
    raise exception 'آزمون باید بین ۱ تا ۳۰۰ سؤال داشته باشد.';
  end if;

  update public.exams set
    title = btrim(p_title),
    description = coalesce(p_description, ''),
    starts_at = p_starts_at,
    duration_minutes = p_duration_minutes
  where id = p_exam_id;
  if not found then raise exception 'آزمون پیدا نشد.'; end if;

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
revoke all on function public.edit_exam_with_answer_key(uuid, text, text, timestamptz, integer, jsonb, text, text) from public, anon;
grant execute on function public.edit_exam_with_answer_key(uuid, text, text, timestamptz, integer, jsonb, text, text) to authenticated;

create or replace function public.set_exam_question_resource(
  p_exam_id uuid, p_question_pdf_url text, p_question_file_path text
)
returns void
language plpgsql security definer set search_path = ''
as $$
begin
  if not (select public.is_admin()) then raise exception 'فقط مدیر سامانه اجازه تغییر فایل سؤال را دارد.'; end if;
  if not exists (select 1 from public.exams where id = p_exam_id) then
    raise exception 'آزمون پیدا نشد.';
  end if;
  insert into public.exam_question_resources(exam_id, question_pdf_url, question_file_path, updated_at)
  values (p_exam_id, nullif(btrim(p_question_pdf_url), ''), nullif(btrim(p_question_file_path), ''), pg_catalog.now())
  on conflict (exam_id) do update set
    question_pdf_url = excluded.question_pdf_url,
    question_file_path = excluded.question_file_path,
    updated_at = excluded.updated_at;
end;
$$;
revoke all on function public.set_exam_question_resource(uuid, text, text) from public, anon;
grant execute on function public.set_exam_question_resource(uuid, text, text) to authenticated;

-- Expose the question PDF only to registered examinees during the live exam window.
-- Admins can inspect it at any time. The URL/path columns themselves are not directly selectable.
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
        and pg_catalog.now() < e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes)
    ) then
      raise exception 'فایل سؤال فقط در زمان برگزاری آزمون قابل مشاهده است.';
    end if;
    if not exists (
      select 1 from public.exam_registrations er
      where er.exam_id = p_exam_id and er.user_id = v_uid
    ) and not exists (
      select 1
      from public.exam_team_registrations etr
      join public.team_members tm on tm.team_id = etr.team_id
      where etr.exam_id = p_exam_id and tm.user_id = v_uid
    ) then
      raise exception 'برای مشاهده صورت سؤال باید پیش از شروع آزمون ثبت‌نام کرده باشید.';
    end if;
  end if;

  return query
    select r.question_pdf_url, r.question_file_path
    from public.exam_question_resources r
    where r.exam_id = p_exam_id;
end;
$$;
revoke all on function public.get_exam_question_resource(uuid) from public, anon;
grant execute on function public.get_exam_question_resource(uuid) to authenticated;

create or replace function public.admin_set_profile_role(p_user_id uuid, p_role text)
returns void
language plpgsql security definer set search_path = ''
as $$
begin
  if not (select public.is_admin()) then raise exception 'فقط مدیر سامانه اجازه تغییر نقش را دارد.'; end if;
  if p_role not in ('participant', 'admin') then raise exception 'نقش نامعتبر است.'; end if;
  if p_user_id = (select auth.uid()) and p_role <> 'admin' then
    raise exception 'نمی‌توانید نقش مدیر خود را از این بخش حذف کنید.';
  end if;
  update public.profiles set role = p_role where id = p_user_id;
  if not found then raise exception 'کاربر پیدا نشد.'; end if;
end;
$$;
revoke all on function public.admin_set_profile_role(uuid, text) from public, anon;
grant execute on function public.admin_set_profile_role(uuid, text) to authenticated;

-- Private bucket for uploaded question PDFs. Registered examinees and admins can read.
insert into storage.buckets(id, name, public)
values ('exam-question-files', 'exam-question-files', false)
on conflict (id) do nothing;

drop policy if exists "question_files_admin_upload" on storage.objects;
create policy "question_files_admin_upload" on storage.objects for insert to authenticated
with check (bucket_id = 'exam-question-files' and (select public.is_admin()));

drop policy if exists "question_files_admin_update" on storage.objects;
create policy "question_files_admin_update" on storage.objects for update to authenticated
using (bucket_id = 'exam-question-files' and (select public.is_admin()))
with check (bucket_id = 'exam-question-files' and (select public.is_admin()));

drop policy if exists "question_files_admin_delete" on storage.objects;
create policy "question_files_admin_delete" on storage.objects for delete to authenticated
using (bucket_id = 'exam-question-files' and (select public.is_admin()));

drop policy if exists "question_files_registered_read" on storage.objects;
create policy "question_files_registered_read" on storage.objects for select to authenticated
using (
  bucket_id = 'exam-question-files'
  and (
    (select public.is_admin())
    or (
      exists (
        select 1 from public.exams e
        where e.id::text = split_part(storage.objects.name, '/', 1)
          and pg_catalog.now() >= e.starts_at
          and pg_catalog.now() < e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes)
      )
      and (
        exists (
          select 1 from public.exam_registrations er
          where er.exam_id::text = split_part(storage.objects.name, '/', 1)
            and er.user_id = (select auth.uid())
        )
        or exists (
          select 1 from public.exam_team_registrations etr
          join public.team_members tm on tm.team_id = etr.team_id
          where etr.exam_id::text = split_part(storage.objects.name, '/', 1)
            and tm.user_id = (select auth.uid())
        )
      )
    )
  )
);
commit;
