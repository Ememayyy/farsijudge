# فارسی جاج | Farsi-Judge

پلتفرم برگزاری مسابقه‌های علمی و برنامه‌نویسی؛ رابط کاربری روی GitHub Pages و احراز هویت، داده‌ها، نشست امن و تصحیح پاسخ‌ها روی Supabase.

## نسخه زنده

https://ememayyy.github.io/farsijudge/

## راه‌اندازی Supabase

1. در Supabase از **Authentication → URL Configuration** مقدار **Site URL** را روی `https://ememayyy.github.io/farsijudge/` قرار بده.
2. در **Redirect URLs** این دو مقدار را اضافه کن:
   - `https://ememayyy.github.io/farsijudge/`
   - `https://ememayyy.github.io/farsijudge/**`
3. در **Authentication → Email Templates → Confirm signup** مطمئن شو لینک از `{{ .ConfirmationURL }}` استفاده می‌کند و آدرس `localhost` به‌صورت ثابت در قالب نوشته نشده است.
4. گزینه **Confirm email** را در **Authentication → Providers → Email** روشن نگه دار تا تأیید ایمیل واقعی انجام شود.
5. محتوای [قالب فارسی تأیید ایمیل](supabase/email-templates/confirm-signup.html) را در **Authentication → Email Templates → Confirm signup** قرار بده. متغیر `{{ .ConfirmationURL }}` را بدون تغییر نگه دار.

راهنمای کامل‌تر: [تنظیم URL و ایمیل Supabase](supabase/auth-url-settings.md).

## نصب پایگاه داده و قابلیت‌های پلتفرم

پس از انتشار این نسخه، فایل زیر را **یک‌بار** در Supabase → SQL Editor اجرا کنید:

- [supabase/migrations/002_teams_registration_admin_features.sql](supabase/migrations/002_teams_registration_admin_features.sql)

این migration ستون نام کاربری، امکان تغییر نام کاربری از صفحه تیم، تیم‌ها، دعوت‌نامه‌ها، ثبت‌نام فردی/تیمی، پاسخ‌های مشترک، لینک یا فایل خصوصی PDF و RPCهای امن مدیریت و تصحیح مجدد را اضافه می‌کند. همچنین `pg_cron` را فعال می‌کند و هر دقیقه آزمون‌های پایان‌یافته و تصحیح‌نشده را به‌طور خودکار تصحیح می‌کند. بدون اجرای migration، رابط جدید به جداول و توابعی اشاره می‌کند که هنوز در دیتابیس وجود ندارند.

سپس فایل [003_farsijudge_platform_upgrade.sql](supabase/migrations/003_farsijudge_platform_upgrade.sql) را **یک‌بار** اجرا کن. این Migration سقف سه نفر برای تیم با احتساب کاپیتان، خروج و انتقال کاپیتانی، نشست تک‌دستگاهی، تنظیمات زنده مسابقه، زمان انتشار کارنامه، تگ‌ها، حذف کاربر و بررسی سؤال‌به‌سؤال را اضافه می‌کند.

## مدیر کردن حساب مالک

بعد از ثبت‌نام با ایمیل موردنظر، فایل [supabase/promote-admin.sql](supabase/promote-admin.sql) را در Supabase → SQL Editor اجرا کن. این فایل برای ایمیلی که مالک پروژه در گفتگو داده از پیش تنظیم شده است و در پایان نقش و وضعیت تأیید ایمیل را نمایش می‌دهد. پس از اجرای موفق، از سایت خارج شو و دوباره وارد شو تا منوی مدیریت نمایش داده شود.

## ضدربات و انتشار

برای فعال‌کردن Cloudflare Turnstile، یک Site Key و Secret Key بساز. `VITE_TURNSTILE_SITE_KEY` را در GitHub Actions Variables قرار بده و Secret Key را در تنظیمات CAPTCHA پروژه Supabase ثبت کن (**Authentication → Bot and Abuse Protection → CAPTCHA**). تا وقتی هر دو سمت تنظیم نشده باشند، CAPTCHA واقعی فعال نیست. محدودیت نرخ درخواست Supabase نیز باید روشن بماند.

هر Push روی شاخه `main`، پروژه را با GitHub Actions می‌سازد و روی GitHub Pages منتشر می‌کند. متغیرهای Repository زیر باید در **Settings → Secrets and variables → Actions → Variables** تعریف شده باشند:

- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_PUBLISHABLE_KEY`
- `VITE_TURNSTILE_SITE_KEY` (کلید عمومی Cloudflare؛ اختیاری تا زمان پیکربندی CAPTCHA)

کلیدهای Secret یا `service_role` را هرگز در فرانت‌اند قرار نده.
