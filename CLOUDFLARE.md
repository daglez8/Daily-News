# Private dashboard + live Refresh (Cloudflare)

This moves your dashboard to **Cloudflare Pages** so it's **private** (behind a login) and
the **Refresh button can trigger a live crawl**. One-time setup, then it's automatic.

All the code is already in this repo:
- `docs/` — the dashboard (served by Cloudflare Pages)
- `functions/api/trigger.js` — secure server-side function that fires the routine (holds the token, never exposed to the page)

## Step 1 — Get the routine's API trigger
1. Open your routine at **claude.ai/code/routines** → **Edit** → **Add another trigger** → **API**.
2. It shows a **URL** (like `https://api.anthropic.com/v1/claude_code/routines/<id>/fire`) and a **token** (`sk-ant-oat01-…`, shown once).
3. **Copy both** somewhere safe for the next steps. Save the routine.

## Step 2 — Create the Cloudflare Pages site
1. Sign up free at **dash.cloudflare.com**.
2. **Workers & Pages** → **Create** → **Pages** → **Connect to Git** → authorize GitHub → pick **`daglez8/Daily-News`**.
3. Build settings:
   - **Framework preset:** None
   - **Build command:** *(leave empty)*
   - **Build output directory:** `docs`
4. **Save and Deploy.** When it finishes you'll get a URL like `https://daily-news-xxx.pages.dev`.

## Step 3 — Add the trigger secrets
1. In your new Pages project → **Settings** → **Variables and secrets**.
2. Add two variables (set them for **Production**):
   - `ROUTINE_FIRE_URL` = the URL from Step 1
   - `ROUTINE_TOKEN` = the token from Step 1 — click **Encrypt** so it's a secret
3. **Save**, then **Deployments → Retry deployment** (so the function picks up the secrets).

## Step 4 — Make it private (Cloudflare Access)
1. In the Cloudflare dashboard → **Zero Trust** (free plan is fine) → **Access → Applications → Add an application → Self-hosted**.
2. **Application domain:** your `*.pages.dev` hostname.
3. **Add a policy:** Action **Allow**, rule **Emails** → your email (`daglez8@gmail.com`). Add family emails too if you want.
4. Save. Now opening the site prompts for an email login code — only you can see it.

## Step 5 — Use it
- **Bookmark the `*.pages.dev` URL** (works on laptop + phone, asks for your email login once).
- Tapping **Refresh** now fires the routine, shows "Fetching fresh news…", and updates the page when the run finishes (~1–2 min). There's a 90-second cooldown to protect your usage.
- The scheduled 7 AM (and 6 PM) runs still work exactly as before.

## Notes
- You can turn off GitHub Pages now (repo → Settings → Pages → Source: None) since Cloudflare serves the site. Your repo stays private either way.
- If the token is ever misused, regenerate it in the routine's API trigger and update `ROUTINE_TOKEN`.
- The Refresh button still works on plain GitHub Pages too — it just reloads the latest feed instead of triggering a crawl (no function there).
