-- Promote the already-registered owner account to administrator.
-- Run in Supabase Dashboard -> SQL Editor after this email has registered.
-- The email below is copied exactly from the project owner's message.
do $$
declare
  affected_rows integer;
begin
  update public.profiles as p
  set role = 'admin'
  from auth.users as u
  where p.id = u.id
    and lower(u.email) = lower('mohammdmahdi.afshar2010@gmail.com');

  get diagnostics affected_rows = row_count;

  if affected_rows <> 1 then
    raise exception 'Expected to promote exactly one profile, but updated % rows. Verify the exact email and that registration created a profile.', affected_rows;
  end if;
end;
$$;

-- Verify the role and Supabase's current email-confirmation status.
select
  u.email,
  p.full_name,
  p.role,
  u.email_confirmed_at,
  u.created_at
from auth.users as u
join public.profiles as p on p.id = u.id
where lower(u.email) = lower('mohammdmahdi.afshar2010@gmail.com');
