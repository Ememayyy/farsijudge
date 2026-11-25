# FarsiJudge | آزمون‌یار

سامانه آزمون آنلاین فارسی با ثبت‌نام کاربران، پاسخ‌دهی عددی، زمان‌بندی آزمون و تصحیح خودکار با Supabase.

## انتشار در GitHub Pages

کد کامل برنامه در آرشیو `farsijudge-source.tar.gz` قرار دارد. گردش‌کار GitHub Actions آرشیو را استخراج، وابستگی‌ها را نصب، برنامه را build و خروجی را در GitHub Pages منتشر می‌کند.

پیش از اولین انتشار، این دو **Repository Variable** را از مسیر **Settings → Secrets and variables → Actions → Variables** اضافه کنید:

- `VITE_SUPABASE_URL`: آدرس پروژه Supabase
- `VITE_SUPABASE_PUBLISHABLE_KEY`: کلید Publishable پروژه Supabase

سپس از **Settings → Pages → Build and deployment → Source** گزینه **GitHub Actions** را انتخاب کنید. بعد از هر push روی شاخه `main`، سایت به‌صورت خودکار build و deploy می‌شود.

## امنیت

فقط کلید عمومی Publishable را در متغیر فرانت‌اند قرار دهید. کلیدهای `sb_secret_...`، `service_role` و رمز دیتابیس را هرگز در کد سایت یا متغیرهای قابل‌دسترسی به فرانت‌اند قرار ندهید. امنیت داده‌ها باید با RLS و توابع امن دیتابیس تأمین شود.

## محتوای پروژه

- رابط فارسی و واکنش‌گرا
- ثبت‌نام و ورود با Supabase Auth
- داشبورد شرکت‌کننده و پنل مدیریت
- زمان‌بندی آزمون و پاسخ‌دهی عددی
- تصحیح سمت پایگاه داده
- تم روشن و تیره
- فایل‌های SQL و راهنمای راه‌اندازی در آرشیو منبع
