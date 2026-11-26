-- Restore the four-person team capacity advertised by the application.
-- This also updates older pending invitations so they can be accepted
-- whenever the team still has an available place.
begin;

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
  if v_count >= 4 then
    raise exception 'هر تیم حداکثر چهار عضو دارد؛ کاپیتان هم جزو همین چهار نفر است.';
  end if;
  return new;
end;
$$;

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
  select count(*) into v_pending_count
  from public.team_invitations
  where team_id = v_team_id and status = 'pending';

  if v_member_count + v_pending_count >= 4 then
    raise exception 'ظرفیت تیم تکمیل است؛ هر تیم حداکثر چهار عضو با احتساب کاپیتان دارد.';
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

  perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(v_uid::text, 0));

  select i.team_id into v_team_id
  from public.team_invitations i
  where i.id = p_invitation_id
    and i.invited_user_id = v_uid
    and i.status = 'pending'
  for update;

  if v_team_id is null then raise exception 'این دعوت‌نامه معتبر یا فعال نیست.'; end if;

  perform 1 from public.teams where id = v_team_id for update;

  if p_accept then
    if exists (
      select 1
      from public.exam_team_registrations etr
      join public.exams e on e.id = etr.exam_id
      where etr.team_id = v_team_id
        and pg_catalog.now() < coalesce(e.end_at_override, e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes))
    ) then
      raise exception 'تا پایان مسابقه‌ای که تیم در آن ثبت‌نام کرده، ترکیب اعضا قابل تغییر نیست.';
    end if;

    if exists (select 1 from public.team_members where user_id = v_uid) then
      raise exception 'ابتدا باید از تیم فعلی خارج شوید.';
    end if;

    if exists (
      select 1
      from public.exam_registrations er
      join public.exams e on e.id = er.exam_id
      where er.user_id = v_uid
        and pg_catalog.now() < coalesce(e.end_at_override, e.starts_at + pg_catalog.make_interval(mins => e.duration_minutes))
    ) then
      raise exception 'تا پایان آزمونی که به‌صورت انفرادی در آن ثبت‌نام کرده‌اید، نمی‌توانید عضو تیم دیگری شوید.';
    end if;

    select count(*) into v_member_count
    from public.team_members
    where team_id = v_team_id;

    if v_member_count >= 4 then
      raise exception 'ظرفیت تیم تکمیل است؛ هر تیم حداکثر چهار عضو دارد.';
    end if;

    insert into public.team_members(team_id, user_id, role)
    values (v_team_id, v_uid, 'member');

    update public.team_invitations
    set status = 'accepted', responded_at = pg_catalog.now()
    where id = p_invitation_id;
  else
    update public.team_invitations
    set status = 'declined', responded_at = pg_catalog.now()
    where id = p_invitation_id;
  end if;
end;
$$;
revoke all on function public.respond_team_invitation(uuid, boolean) from public, anon;
grant execute on function public.respond_team_invitation(uuid, boolean) to authenticated;

create or replace function public.enforce_team_invitation_limit()
returns trigger
language plpgsql security definer set search_path = ''
as $$
declare
  v_members integer;
  v_pending integer;
begin
  if new.status <> 'pending' then return new; end if;

  perform 1 from public.teams where id = new.team_id for update;

  select count(*) into v_members
  from public.team_members
  where team_id = new.team_id;

  select count(*) into v_pending
  from public.team_invitations
  where team_id = new.team_id
    and status = 'pending'
    and id is distinct from new.id;

  if v_members + v_pending >= 4 then
    raise exception 'ظرفیت تیم تکمیل است؛ هر تیم حداکثر چهار عضو با احتساب کاپیتان دارد.';
  end if;

  return new;
end;
$$;

drop trigger if exists team_invitation_limit on public.team_invitations;
create trigger team_invitation_limit
before insert or update of status on public.team_invitations
for each row execute function public.enforce_team_invitation_limit();

commit;
