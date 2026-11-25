-- Remove the single-device login restriction from existing Farsi-Judge databases.
-- Safe to run once after migration 003. It preserves normal account authentication.

begin;

-- Older versions inserted this guard into several public RPC functions.
-- Rewrite those functions without the guard before dropping the guard function.
do $remove_device_guard$
declare
  fn record;
  definition text;
begin
  for fn in
    select p.oid
    from pg_catalog.pg_proc p
    join pg_catalog.pg_namespace n on n.oid = p.pronamespace
    where n.nspname = 'public'
      and p.prokind = 'f'
      and pg_catalog.pg_get_functiondef(p.oid) like '%require_my_single_session%'
  loop
    definition := pg_catalog.pg_get_functiondef(fn.oid);
    definition := regexp_replace(
      definition,
      E'^[ \t]*perform public\\.require_my_single_session\\(\\);[ \t]*$',
      '',
      'gm'
    );
    execute definition;
  end loop;
end;
$remove_device_guard$;

-- Restore the ordinary participant/admin read policies without session checks.
drop policy if exists "teams_read_members" on public.teams;
create policy "teams_read_members" on public.teams for select to authenticated
using (
  (select public.is_team_member(id))
  or (select public.is_admin())
  or exists (
    select 1 from public.team_invitations ti
    where ti.team_id = teams.id
      and ti.invited_user_id = (select auth.uid())
      and ti.status = 'pending'
  )
);

drop policy if exists "team_members_read_team" on public.team_members;
create policy "team_members_read_team" on public.team_members for select to authenticated
using ((select public.is_team_member(team_id)) or (select public.is_admin()));

drop policy if exists "team_invites_read_participants" on public.team_invitations;
create policy "team_invites_read_participants" on public.team_invitations for select to authenticated
using (
  invited_user_id = (select auth.uid())
  or invited_by = (select auth.uid())
  or (select public.is_admin())
);

drop policy if exists "exam_registrations_read_owner_admin" on public.exam_registrations;
create policy "exam_registrations_read_owner_admin" on public.exam_registrations for select to authenticated
using (user_id = (select auth.uid()) or (select public.is_admin()));

drop policy if exists "exam_team_registrations_read_members" on public.exam_team_registrations;
create policy "exam_team_registrations_read_members" on public.exam_team_registrations for select to authenticated
using ((select public.is_team_member(team_id)) or (select public.is_admin()));

drop policy if exists "answers_read_own_or_admin" on public.exam_answers;
create policy "answers_read_own_or_admin" on public.exam_answers for select to authenticated
using (
  user_id = (select auth.uid())
  or (team_id is not null and (select public.is_team_member(team_id)))
  or (select public.is_admin())
);

drop policy if exists "results_read_after_release" on public.exam_results;
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

drop policy if exists "attempts_read_own_or_admin" on public.exam_attempts;
create policy "attempts_read_own_or_admin" on public.exam_attempts for select to authenticated
using (
  user_id = (select auth.uid())
  or (team_id is not null and (select public.is_team_member(team_id)))
  or (select public.is_admin())
);

drop function if exists public.activate_my_single_session();
drop function if exists public.is_my_single_session_active();
drop function if exists public.require_my_single_session();
drop table if exists public.user_active_sessions;

commit;
