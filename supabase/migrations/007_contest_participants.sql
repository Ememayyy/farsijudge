-- Public participant counts and participant directory for published contests.
-- Counts individual competitors, including every member of a registered team.
begin;

create or replace function public.get_contest_participant_counts()
returns table (exam_id uuid, participant_count bigint)
language sql
stable
security definer
set search_path = ''
as $$
  with registered_people as (
    select er.exam_id, er.user_id
    from public.exam_registrations er
    join public.exams e on e.id = er.exam_id
    where e.is_published is true

    union all

    select etr.exam_id, tm.user_id
    from public.exam_team_registrations etr
    join public.exams e on e.id = etr.exam_id
    join public.team_members tm on tm.team_id = etr.team_id
    where e.is_published is true
  )
  select e.id, count(rp.user_id)
  from public.exams e
  left join registered_people rp on rp.exam_id = e.id
  where e.is_published is true
  group by e.id;
$$;

create or replace function public.get_contest_participants(p_exam_id uuid)
returns table (
  display_name text,
  username text,
  team_name text,
  registered_at timestamptz
)
language sql
stable
security definer
set search_path = ''
as $$
  select
    coalesce(nullif(btrim(p.full_name), ''), nullif(p.username, ''), 'شرکت‌کننده'),
    coalesce(nullif(p.username, ''), 'user'),
    null::text,
    er.registered_at
  from public.exam_registrations er
  join public.exams e on e.id = er.exam_id and e.is_published is true
  join public.profiles p on p.id = er.user_id
  where er.exam_id = p_exam_id

  union all

  select
    coalesce(nullif(btrim(p.full_name), ''), nullif(p.username, ''), 'شرکت‌کننده'),
    coalesce(nullif(p.username, ''), 'user'),
    t.name,
    etr.registered_at
  from public.exam_team_registrations etr
  join public.exams e on e.id = etr.exam_id and e.is_published is true
  join public.teams t on t.id = etr.team_id
  join public.team_members tm on tm.team_id = etr.team_id
  join public.profiles p on p.id = tm.user_id
  where etr.exam_id = p_exam_id
  order by 4 asc, 2 asc;
$$;

revoke all on function public.get_contest_participant_counts() from public;
revoke all on function public.get_contest_participants(uuid) from public;
grant execute on function public.get_contest_participant_counts() to anon, authenticated;
grant execute on function public.get_contest_participants(uuid) to anon, authenticated;

commit;
