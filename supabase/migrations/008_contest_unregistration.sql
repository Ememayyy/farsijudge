-- Allow a registered user (or the team captain) to cancel a registration before the contest starts.
begin;

create or replace function public.unregister_from_exam(p_exam_id uuid)
returns void
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_uid uuid := (select auth.uid());
  v_team_id uuid;
  v_role text;
begin
  if v_uid is null then
    raise exception 'ابتدا وارد حساب کاربری شوید.';
  end if;

  perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(v_uid::text, 0));

  if not exists (
    select 1 from public.exams e
    where e.id = p_exam_id and e.is_published is true
  ) then
    raise exception 'مسابقه پیدا نشد یا منتشر نشده است.';
  end if;

  if not exists (
    select 1 from public.exams e
    where e.id = p_exam_id and pg_catalog.now() < e.starts_at
  ) then
    raise exception 'لغو ثبت‌نام فقط پیش از شروع مسابقه امکان‌پذیر است.';
  end if;

  select etr.team_id, tm.role
  into v_team_id, v_role
  from public.exam_team_registrations etr
  join public.team_members tm on tm.team_id = etr.team_id
  where etr.exam_id = p_exam_id
    and tm.user_id = v_uid
  limit 1;

  if v_team_id is not null then
    if v_role <> 'captain' then
      raise exception 'لغو ثبت‌نام تیمی فقط توسط کاپیتان تیم امکان‌پذیر است.';
    end if;

    perform 1 from public.teams where id = v_team_id for update;

    if exists (
      select 1 from public.exam_attempts a
      where a.exam_id = p_exam_id and a.team_id = v_team_id
    ) then
      raise exception 'پس از شروع آزمون، لغو ثبت‌نام امکان‌پذیر نیست.';
    end if;

    delete from public.exam_team_registrations
    where exam_id = p_exam_id and team_id = v_team_id;

    if not found then
      raise exception 'ثبت‌نام تیم برای این مسابقه پیدا نشد.';
    end if;
  else
    if exists (
      select 1 from public.exam_attempts a
      where a.exam_id = p_exam_id
        and a.user_id = v_uid
        and a.team_id is null
    ) then
      raise exception 'پس از شروع آزمون، لغو ثبت‌نام امکان‌پذیر نیست.';
    end if;

    delete from public.exam_registrations
    where exam_id = p_exam_id and user_id = v_uid;

    if not found then
      raise exception 'ثبت‌نامی برای این مسابقه پیدا نشد.';
    end if;
  end if;
end;
$$;

revoke all on function public.unregister_from_exam(uuid) from public, anon;
grant execute on function public.unregister_from_exam(uuid) to authenticated;

commit;
