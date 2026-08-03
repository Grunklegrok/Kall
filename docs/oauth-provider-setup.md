# OAuth provider callback setup

Kall starts OAuth from the web application through `/api/kall`, but the API generates and handles the provider callback.

Use the public `kall-api` Render URL for every registered callback. Replace `<KALL_API_HOST>` with the exact public URL shown on the Render `kall-api` service page.

## Callback URLs

```text
Google
https://<KALL_API_HOST>/api/auth/oauth/google/callback

GitHub
https://<KALL_API_HOST>/api/auth/oauth/github/callback

LinkedIn
https://<KALL_API_HOST>/api/auth/oauth/linkedin/callback
```

For the current conventional Render hostname, these would be:

```text
https://kall-api.onrender.com/api/auth/oauth/google/callback
https://kall-api.onrender.com/api/auth/oauth/github/callback
https://kall-api.onrender.com/api/auth/oauth/linkedin/callback
```

The value must match exactly, including:

- `https`
- hostname
- `/api/auth/oauth/<provider>/callback`
- no `/api/kall` prefix
- no trailing slash

Do not register the OAuth start URL and do not use `/session`.

## Provider fields

### Google

Add the Google callback under **Authorized redirect URIs** for the OAuth 2.0 Web application. Add `https://kall-web.onrender.com` under **Authorized JavaScript origins** if Google requests an origin.

### GitHub

Set **Authorization callback URL** to the GitHub callback above. The homepage URL can be `https://kall-web.onrender.com`.

### LinkedIn

Add the LinkedIn callback above under the application's **Authorized redirect URLs for your app**. The URL is case-sensitive and must match exactly.

## Render environment

The `kall-api` service must contain the matching provider client IDs and secrets:

```env
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_CLIENT_SECRET=...
GITHUB_OAUTH_CLIENT_ID=...
GITHUB_OAUTH_CLIENT_SECRET=...
LINKEDIN_OAUTH_CLIENT_ID=...
LINKEDIN_OAUTH_CLIENT_SECRET=...
FRONTEND_URL=https://kall-web.onrender.com
```
