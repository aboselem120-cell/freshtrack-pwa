<!-- test -->
# FreshTrack (PWA Prototype)

Progressive Web App prototype: scans a grocery item or receipt photo, sends it
to an AI vision model (via a secure backend proxy) to identify products,
categories, and expiry dates — then sorts everything by urgency.

## Project structure

```
saleh-pwa/
├── index.html          # The app UI + logic (no build step needed)
├── api/
│   └── analyze.js       # Serverless function: proxies to Google Gemini API securely
├── manifest.json         # App name, icons, colors — makes it "installable"
├── service-worker.js     # Caches the app shell for offline loading
├── icons/
│   ├── icon-192.png
│   └── icon-512.png
└── README.md
```

## ⚠️ Required setup: free Gemini API key (no credit card)

The photo analysis calls Google's Gemini vision model through `api/analyze.js`.
Gemini has a genuine free tier — no credit card, no expiration — which is
why it's used here instead of a paid-only provider.

1. Go to **aistudio.google.com** → sign in with a Google account
2. Click **Get API key** → **Create API key** → copy it
3. In your Vercel project → **Settings → Environment Variables**
4. Add: `GEMINI_API_KEY` = `your-key-here` (scope: Production + Preview)
5. Redeploy the project (Vercel → Deployments → ⋯ → Redeploy) so the function
   picks up the new variable

Without this step, tapping "Scan Item" will fail with a server error that
tells you exactly this (check "Show raw OCR text" in the app to confirm).

**Free tier limits (subject to change — check aistudio.google.com for the
current numbers):** roughly 1,500 requests/day on the Flash model, which is
far more than enough for testing and early users. Google's terms note that
free-tier inputs may be used to improve their models — fine for prototyping
raw grocery photos, but keep that in mind for anything sensitive.

## Run it locally

PWAs require HTTPS (or localhost) to register a service worker. The `/api`
function specifically requires the **Vercel CLI** to run locally (a plain
static server like `python -m http.server` won't execute serverless
functions):

```bash
npm i -g vercel
vercel dev
```

You'll be prompted to link the project and it will pick up your
`GEMINI_API_KEY` from a local `.env` file — create one with:
```
GEMINI_API_KEY=your-key-here
```

## Deploy it for real (so you can install it on your phone)

- **Vercel**: import this folder as a project (drag-and-drop or connect a
  GitHub repo), then complete the API key setup above.
- **GitHub Pages** won't work for this version — it only serves static
  files and can't run the `/api` serverless function. Vercel or Netlify
  (with a Netlify Function equivalent) are needed.

Once deployed over HTTPS with the API key configured:
- **Android (Chrome)**: open the site → "Add to Home screen" (often an
  automatic install banner appears).
- **iPhone (Safari)**: open the site → Share button → "Add to Home Screen".

## Recipe suggestions

The "Suggest a recipe" button calls `api/recipe.js`, a second serverless
function using the same `GEMINI_API_KEY` — no extra setup needed if you
already configured photo analysis.

## Known limitations (prototype, not production)

- **Receipts never carry real per-item expiry dates**: this isn't a bug to
  fix, it's what receipts actually are — they print names and prices, not
  expiry dates. When scanning a multi-item receipt, every item gets an
  `estimated_days` guess (clearly marked "≈ Estimated" in the UI); the
  prompt explicitly forbids applying the receipt's own printed transaction
  date to any item. Real dates only come from photographing an individual
  product's own packaging.
- **Persistence and push notifications work, but need setup**: without
  configuring Supabase (see "Cloud sync setup" above), items still persist
  fine via localStorage — closing and reopening the app days later keeps
  them — but notifications only check when the app is opened, and there's
  no cross-device sync. Filling in `SUPABASE_URL`/`SUPABASE_ANON_KEY` and
  the Vercel environment variables turns on real accounts, cross-device
  sync, and true background push (arrives even with the app fully closed).
- **Free tier is for prototyping**: fine for testing with friends/family,
  but monitor Google AI Studio's quota page before wider public use — the
  app's own daily usage caps (25 scans/10 recipes per device) are a soft
  safety net, not abuse-proof server-side rate limiting.

## ☁️ Cloud sync + real push notifications (optional, advanced)

By default the app works exactly as before — items saved to the device only
(localStorage). Everything below is **optional**: skip it and the app keeps
working. Set it up only if you want accounts, cross-device sync, and real
background push notifications (the kind that arrive even with the app fully
closed).

### 1. Create a Supabase project
Go to **supabase.com** → New Project (free tier is enough). Wait ~2 minutes
for it to provision.

### 2. Run the database schema
Supabase dashboard → **SQL Editor** → New Query → paste the entire contents
of `supabase-schema.sql` from this project → **Run**.

### 3. Get your Supabase keys
Supabase dashboard → **Settings → API**:
- `Project URL` → this is your `SUPABASE_URL`
- `anon public` key → this is your `SUPABASE_ANON_KEY` (safe to expose in the
  browser — protected by the row-level security policies the schema created)
- `service_role` key → this is your `SUPABASE_SERVICE_ROLE_KEY` (⚠️ **secret**,
  server-side only, never put this in `index.html`)

### 4. Wire the frontend
Open `index.html`, find this block near the top of the `<script>` section:
```js
const SUPABASE_URL = '';
const SUPABASE_ANON_KEY = '';
```
Fill in your `Project URL` and `anon public` key.

### 5. Set environment variables in Vercel
Settings → Environment Variables → add all of these:

| Key | Value |
|---|---|
| `SUPABASE_URL` | same Project URL as above |
| `SUPABASE_SERVICE_ROLE_KEY` | the secret `service_role` key |
| `VAPID_PUBLIC_KEY` | `BP2HLUTxAS9ddHUTU-nm6gm75vbEijdOX5MASmI7Z9Segy86KPDFEi7oKrk8S-SIiOP04-0FlyeCpEhNMqBBFaw` |
| `VAPID_PRIVATE_KEY` | `mxy_ApfTwKtKyufN_nA7r-qbSYcmfX4iK6a7K5_vM0A` |
| `VAPID_SUBJECT` | `mailto:you@example.com` (any real-looking email) |

The VAPID keys above were generated specifically for this project and are
ready to use as-is — you don't need to generate your own unless you want to.

### 6. Enable Supabase email auth
Supabase dashboard → **Authentication → Providers** → make sure **Email** is
enabled (it is by default). Sign-in uses magic links (no password) — the
person taps "Send Magic Link" in Settings, gets an email, clicks it, done.

### 7. Redeploy
Vercel → Deployments → ⋯ → Redeploy, so the new environment variables and
`package.json` dependencies (`@supabase/supabase-js`, `web-push`) take effect.

### How it behaves once configured
- **Settings → Account & Sync** now shows a real sign-in box instead of the
  "cloud sync isn't set up" message.
- Signing in uploads whatever was in local storage to the cloud automatically,
  then everything syncs from there.
- Enabling notifications while signed in also subscribes the device to real
  push — `api/send-reminders.js` runs daily (see `vercel.json`, default 9am
  UTC — edit the cron schedule to your preferred time) and sends an actual
  push notification for anyone with items expiring within 3 days, even with
  the app fully closed.
- Signing out on a device reverts that device to local-only storage.
