# FarsiJudge | آزمون‌یار

سامانه آزمون آنلاین فارسی با ثبت‌نام کاربران، پاسخ‌دهی عددی، زمان‌بندی آزمون و تصحیح خودکار با Supabase.

## وضعیت پروژه

کد اصلی پروژه در آرشیو `farsijudge-source.zip.b64` قرار دارد. گردش‌کار GitHub Actions آن را استخراج و برای GitHub Pages می‌سازد.

## راه‌اندازی

1. در تنظیمات Repository به **Settings → Secrets and variables → Actions → Variables** بروید.
2. این دو Repository Variable را تعریف کنید:
   - `VITE_SUPABASE_URL`: آدرس پروژه Supabase
   - `VITE_SUPABASE_PUBLISHABLE_KEY`: کلید Publishable پروژه Supabase
3. از **Settings → Pages**، گزینه **GitHub Actions** را به‌عنوان Build and deployment انتخاب کنید.
4. در **Actions** اجرای گردش‌کار **Deploy FarsiJudge to GitHub Pages** را بررسی کنید.

فقط کلید Publishable را در متغیرهای فرانت‌اند استفاده کنید. کلیدهای Secret یا service_role را هرگز در کد یا متغیرهای قابل‌دسترسی به فرانت‌اند قرار ندهید.

## محتوای آرشیو

- رابط فارسی و واکنش‌گرا
- ثبت‌نام و ورود با Supabase Auth
- پنل کاربر و مدیر
- مدیریت آزمون‌ها و پاسخ‌های عددی
- تصحیح سمت پایگاه داده
- تم روشن و تیره
- فایل‌های SQL و راهنمای راه‌اندازی
