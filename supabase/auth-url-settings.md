# Supabase Auth URL and confirmation email settings

Open the Supabase Dashboard for this project.

## Authentication → URL Configuration

Set **Site URL** to:

`https://ememayyy.github.io/farsijudge/`

Add these entries to **Redirect URLs**:

- `https://ememayyy.github.io/farsijudge/`
- `https://ememayyy.github.io/farsijudge/**`

For local Vite development only, optionally add `http://localhost:5173/**`. Do not use `http://localhost:3000` for the deployed app.

## Authentication → Email Templates → Confirm signup

The confirmation link must use Supabase's generated confirmation URL, not a hard-coded localhost URL. Use this form:

`<a href="{{ .ConfirmationURL }}">Confirm your email</a>`

If a custom template builds a link from `{{ .SiteURL }}`, update it to use the intended redirect or Supabase's `{{ .ConfirmationURL }}`. The `.SiteURL` value comes from the Site URL setting; `.RedirectTo` is the redirect supplied by the app.

## Email confirmation

For the intended signup flow, email verification must be required. In **Authentication → Providers → Email**, turn **Confirm email** on. New accounts must use the confirmation link sent by Supabase before they can sign in normally. The confirmation template should use `{{ .ConfirmationURL }}` and the Site URL / Redirect URLs above must be correct.

## Why a link may say otp_expired

Confirmation links are single-use and expire. Some email security systems scan links before the user opens them, which can consume a one-time link. Supabase documents OTP or confirmation-button alternatives if link prefetching is a recurring problem. Disable click tracking in a mail provider if it rewrites confirmation links.
