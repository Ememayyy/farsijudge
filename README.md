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

**نکتهٔ مهم:** انتشار GitHub Pages فقط رابط کاربری را Build و منتشر می‌کند؛ هیچ‌کدام از SQL migrationها را روی پروژهٔ Supabase اجرا نمی‌کند. برای فعال شدن قابلیت‌ها، فایل‌های زیر را در Supabase → SQL Editor **به همین ترتیب و هرکدام فقط یک‌بار** اجرا کن. پیش از رفتن به فایل بعدی، مطمئن شو اجرای فایل قبلی با موفقیت تمام شده است.

1. [002_teams_registration_admin_features.sql](supabase/migrations/002_teams_registration_admin_features.sql) — ساخت تیم، دعوت اعضا، ثبت‌نام فردی/تیمی، پاسخ‌ها و تصحیح خودکار.
2. [003_farsijudge_platform_upgrade.sql](supabase/migrations/003_farsijudge_platform_upgrade.sql) — کنترل زمان مسابقه، ثبت نشست، ظرفیت و مدیریت تیم، انتشار نتایج و دسترسی به فایل سؤال.
3. [004_profile_edit.sql](supabase/migrations/004_profile_edit.sql) — امکان تغییر نام نمایشی.
4. [005_remove_single_device_restriction.sql](supabase/migrations/005_remove_single_device_restriction.sql) — حذف محدودیت ورود تک‌دستگاهی.
5. [006_public_contest_feed.sql](supabase/migrations/006_public_contest_feed.sql) — فهرست عمومی مسابقه‌های منتشرشده.
6. [007_contest_participants.sql](supabase/migrations/007_contest_participants.sql) — نمایش و مدیریت شرکت‌کنندگان مسابقه.
7. [008_contest_unregistration.sql](supabase/migrations/008_contest_unregistration.sql) — لغو ثبت‌نام در مسابقه.
8. [009_restore_four_person_teams.sql](supabase/migrations/009_restore_four_person_teams.sql) — ظرفیت چهار نفر برای هر تیم، با احتساب کاپیتان.
9. [010_public_review_leaderboard_designers.sql](supabase/migrations/010_public_review_leaderboard_designers.sql) — مشاهدهٔ عمومی سؤال‌ها و جدول امتیازات پس از مسابقه، و نقش طراح مسابقه.
10. [011_problem_engine_foundation.sql](supabase/migrations/011_problem_engine_foundation.sql) — پایهٔ بانک سؤال مستقل، انواع پاسخ، اتصال سؤال به مسابقه، سابمیشن‌ها، اطلاعات تکمیلی پروفایل و تنظیمات نوع/امتیازدهی مسابقه.

Migrationهای جدید فقط بعد از موفقیت همهٔ migrationهای قبلی اجرا شوند. Migration شمارهٔ 011 ساختار نسل جدید را به‌صورت افزایشی اضافه می‌کند و جدول‌های قدیمی را حذف یا تبدیل نمی‌کند. اجرای GitHub Pages همچنان هیچ SQLای را خودکار روی Supabase اجرا نمی‌کند.

## مدیر کردن حساب مالک

بعد از ثبت‌نام با ایمیل موردنظر، فایل [supabase/promote-admin.sql](supabase/promote-admin.sql) را در Supabase → SQL Editor اجرا کن. این فایل برای ایمیلی که مالک پروژه در گفتگو داده از پیش تنظیم شده است و در پایان نقش و وضعیت تأیید ایمیل را نمایش می‌دهد. پس از اجرای موفق، از سایت خارج شو و دوباره وارد شو تا منوی مدیریت نمایش داده شود.

## ضدربات و انتشار

**وضعیت فعلی ضدربات:** اتصال ویجت Turnstile در فرانت‌اند هنوز در نسخه منتشرشده فعال نشده است. فعلاً Site Key یا Secret را تنظیم نکن و روی این نسخه CAPTCHA فعال فرض نکن. وقتی اتصال فرانت‌اند کامل شد، Site Key در GitHub Actions Variables و Secret Key در Supabase → Authentication → Bot and Abuse Protection → CAPTCHA ثبت می‌شوند. محدودیت نرخ درخواست Supabase باید روشن بماند.

هر Push روی شاخه `main`، پروژه را با GitHub Actions می‌سازد و روی GitHub Pages منتشر می‌کند. متغیرهای Repository زیر باید در **Settings → Secrets and variables → Actions → Variables** تعریف شده باشند:

- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_PUBLISHABLE_KEY`
- `VITE_TURNSTILE_SITE_KEY` (کلید عمومی Cloudflare؛ اختیاری تا زمان پیکربندی CAPTCHA)

کلیدهای Secret یا `service_role` را هرگز در فرانت‌اند قرار نده.
