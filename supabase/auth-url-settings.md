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

## Whether email confirmation should be required

The owner requested immediate sign-in without email verification. In **Authentication → Providers → Email**, turn **Confirm email** off. Supabase then confirms new email accounts automatically and does not send signup confirmation emails. Turn this on only if verification is desired.

## Why a link may say otp_expired

Confirmation links are single-use and expire. Some email security systems scan links before the user opens them, which can consume a one-time link. Supabase documents OTP or confirmation-button alternatives if link prefetching is a recurring problem. Disable click tracking in a mail provider if it rewrites confirmation links.
