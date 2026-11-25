# آزمون‌یار | FarsiJudge

سامانه آنلاین آزمون‌های عددی فارسی؛ رابط کاربری روی GitHub Pages و احراز هویت، داده‌ها و تصحیح پاسخ‌ها روی Supabase.

## نسخه زنده

https://ememayyy.github.io/farsijudge/

## راه‌اندازی Supabase

1. در Supabase از **Authentication → URL Configuration** مقدار **Site URL** را روی `https://ememayyy.github.io/farsijudge/` قرار بده.
2. در **Redirect URLs** این دو مقدار را اضافه کن:
   - `https://ememayyy.github.io/farsijudge/`
   - `https://ememayyy.github.io/farsijudge/**`
3. در **Authentication → Email Templates → Confirm signup** مطمئن شو لینک از `{{ .ConfirmationURL }}` استفاده می‌کند و آدرس `localhost` به‌صورت ثابت در قالب نوشته نشده است.
4. چون ورود بدون تأیید ایمیل را انتخاب کرده‌ای، در **Authentication → Providers → Email** گزینه **Confirm email** را خاموش کن. وقتی این گزینه خاموش باشد، ثبت‌نام با تأیید خودکار ایمیل انجام می‌شود و ایمیل تأیید ثبت‌نام ارسال نمی‌شود.

راهنمای کامل‌تر: [تنظیم URL و ایمیل Supabase](supabase/auth-url-settings.md).

## مدیر کردن حساب مالک

بعد از ثبت‌نام با ایمیل موردنظر، فایل [supabase/promote-admin.sql](supabase/promote-admin.sql) را در Supabase → SQL Editor اجرا کن. این فایل برای ایمیلی که مالک پروژه در گفتگو داده از پیش تنظیم شده است و در پایان نقش و وضعیت تأیید ایمیل را نمایش می‌دهد. پس از اجرای موفق، از سایت خارج شو و دوباره وارد شو تا منوی مدیریت نمایش داده شود.

## انتشار

هر Push روی شاخه `main`، پروژه را با GitHub Actions می‌سازد و روی GitHub Pages منتشر می‌کند. متغیرهای Repository زیر باید در **Settings → Secrets and variables → Actions → Variables** تعریف شده باشند:

- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_PUBLISHABLE_KEY`

کلیدهای Secret یا `service_role` را هرگز در فرانت‌اند قرار نده.
