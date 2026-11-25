begin;

create or replace function public.update_my_display_name(p_full_name text)
returns void
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_uid uuid := (select auth.uid());
begin
  if v_uid is null then
    raise exception 'ابتدا وارد حساب کاربری شوید.';
  end if;

  perform public.require_my_single_session();

  if p_full_name is null
     or char_length(btrim(p_full_name)) < 2
     or char_length(btrim(p_full_name)) > 60 then
    raise exception 'نام نمایشی باید بین ۲ تا ۶۰ نویسه باشد.';
  end if;

  update public.profiles
  set full_name = btrim(p_full_name)
  where id = v_uid;

  if not found then
    raise exception 'پروفایل کاربر پیدا نشد.';
  end if;
end;
$$;

revoke all on function public.update_my_display_name(text) from public, anon;
grant execute on function public.update_my_display_name(text) to authenticated;

commit;
