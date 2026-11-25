-- Public homepage feed: expose only published contest metadata to logged-out visitors.
begin;

create or replace function public.get_public_contests()
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
  select
    e.id,
    e.title,
    e.description,
    e.starts_at,
    e.duration_minutes,
    e.is_published,
    e.end_at_override,
    coalesce(e.tags, '{}'::text[])
  from public.exams e
  where e.is_published is true
  order by e.starts_at asc
  limit 50;
$$;

revoke all on function public.get_public_contests() from public, anon;
grant execute on function public.get_public_contests() to anon, authenticated;

commit;
