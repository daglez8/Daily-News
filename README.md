# Daniel's Briefing — Personal News Dashboard

A news dashboard that pulls the latest stories from your trusted sources, keeps only
the ones that match your interests (summarized, tagged, and scored), and shows them in
a clean UI. It refreshes automatically twice a day in the cloud — **even when your
laptop is closed** — and you read it from a **bookmark URL** that works on any device.

No external AI API and no API keys: the same scheduled Claude Code run that fetches
the news also writes the summaries.

> **Privacy note:** the dashboard is published with GitHub Pages, which serves a
> **public** page (anyone with the link can see your feed and topic tags). To limit
> exposure, only `docs/index.html` and `docs/news.json` are published — your interest
> profile (`agent/config.json`) and all agent code stay in the private repo and are
> **never** served. If you ever want the page itself private too, the free
> "Cloudflare login" route is in §6.

---

## 1. Daily use

### See your news
Open your **bookmark** (your Pages URL, e.g. `https://<username>.github.io/daniels-briefing/`).
It always shows the latest cloud refresh — on your laptop or phone, nothing to run.

Inside the dashboard:
- **Filter** by topic, source, or language (ES/EN); **sort** by Recent or Relevant; **search**.
- **👍 / 👎** each story — this teaches the agent what you like (see §4).
- **Refresh** reloads the feed; toggle **light/dark** top-right.

### Refresh the news right now (manual)
Tell Claude Code: **"refresh my news"**. It runs the fetch + curation, rewrites
`docs/news.json`, and pushes — your bookmark updates within a minute. (You normally
don't need this; the cloud routine does it automatically.)

### Preview locally before publishing (optional)
Double-click **`update.command`** to pull the latest and open the dashboard at
`localhost:8000` (handy for testing edits before they go live).

---

## 2. How it works (three simple pieces)

1. **The fetcher** — `agent/fetch_feeds.py` (pure Python, no installs) visits each RSS
   feed, pulls recent articles, cleans and de-duplicates them, and skips any source
   that fails.
2. **The curator** — Claude (during the same run) reads those articles, scores each
   against your interests, drops the irrelevant ones, tags and summarizes the rest,
   and writes **`docs/news.json`**.
3. **The dashboard** — `docs/index.html` reads `docs/news.json` and displays it.

The full procedure lives in `agent/PLAYBOOK.md`.

---

## 3. Editing your sources & interests

Everything is in **`agent/config.json`** (private — never published):
- **`sources`** — add or remove feeds. To mute one, add `"disabled": true`.
- **`interest_profile`** — your topics by tier; this drives the relevance scoring.
- **`settings`** — `min_relevance` (cutoff, default 60), `max_age_hours`,
  `target_count` (max stories), etc.

Not sure how? Tell Claude Code what you want ("add Milenio as a source", "care more
about RMBS deals") and it edits the config for you.

---

## 4. The thumbs up/down feedback

Every story has 👍 / 👎. Votes are saved in your browser; the footer's
**"Export my feedback"** button downloads `briefing-feedback.json`. Drop that file in
the project root and the agent uses it on the next run to nudge similar stories up or
down. The more you vote, the sharper your feed gets.

---

## 5. Phase 3 — Set up the twice-daily cloud refresh

One-time setup. The project is already a git repository with an initial commit.

### Step 1 — Create a **private** GitHub repo and push
1. On GitHub: **New repository** → name it `daniels-briefing` → **Private** →
   don't add a README → **Create repository**.
2. Run the "push an existing repository" lines GitHub shows:
   ```
   git remote add origin https://github.com/<your-username>/daniels-briefing.git
   git branch -M main
   git push -u origin main
   ```
   (Or paste me the repo URL and say "push it" — I'll do it.)

### Step 2 — Turn on GitHub Pages (this is what your Pro plan enables for a private repo)
1. Repo → **Settings** → **Pages**.
2. **Build and deployment → Source:** *Deploy from a branch*.
3. **Branch:** `main`, **Folder:** `/docs` → **Save**.
4. After a minute, the page goes live at the URL shown there. **Bookmark it.**
   (Only `docs/` is served — your config and agent code stay private.)

### Step 3 — Create the scheduled cloud routine
Routines run on Anthropic's cloud (so they work with your laptop closed). They require
a **Claude Pro / Max / Team / Enterprise** plan. They are NOT the same as the local
desktop `/schedule` task, which only runs while the app is open.

1. Go to **https://claude.ai/code/routines** → **New routine**. Name it `Daily News Curator`.
2. **Instructions:** paste the contents of **`agent/ROUTINE.md`**.
3. **Add repository** → select **`daglez8/Daily-News`**. If prompted, install the
   **Claude GitHub App** on that repo (lets the routine clone and push).
4. **Permissions tab → enable "Allow unrestricted branch pushes"** for `Daily-News`.
   Required — otherwise it can only push to `claude/...` branches and won't update `main`/Pages.
5. **Trigger → Schedule → Daily at 07:00** (enter in your local America/Mexico_City time).
   Save, then **Edit routine → Add another trigger → Schedule → Daily at 18:00**.
6. Click **Create**.

### Step 4 — Test it
On the routine page, click **Run now**. When it finishes, `docs/news.json` has fresh
stories, a new commit lands on `main`, and your Pages bookmark updates within ~1 minute.
Open the run's session to confirm it pushed successfully.

### Managing the routine (claude.ai/code/routines)
- **Pause / Resume**, **Run now**, **Edit** (prompt, triggers, repo), **Delete**.

---

## 6. Want the page itself private later? (free, optional)

Pages is public. If you later want it behind a login (still free), put **Cloudflare
Access** in front: connect Cloudflare Pages to this repo and add an Access policy
(email login). Ask Claude Code to walk you through it. This needs no paid plan.

---

## 7. Source notes & troubleshooting

- **Reuters** — no public RSS; intentionally disabled.
- **WSJ** — its free RSS is often stale; usually contributes little (age filter skips it).
- **El Economista** — needs the browser User-Agent already set in `config.json`.
- **A category shows nothing** (e.g. no HIR/Creditaria) — normal on a quiet day; the
  agent reports empties instead of padding the feed.
- **A source stops working** — feeds change; tell Claude Code and it'll fix the URL.

---

## File map
```
docs/
  index.html            the dashboard  ← published (public)
  news.json             the curated feed  ← published (public), written by the agent
server.js               tiny local web server (serves docs/ for local preview)
update.command          double-click: pull latest + preview locally
README.md               this file
agent/                  ← all private, never published
  config.json           your sources, interests, settings  ← edit this
  fetch_feeds.py        the fetcher
  PLAYBOOK.md           the agent's step-by-step procedure
  ROUTINE.md            the prompt for the cloud routine
  curate.py             demo of the curation step (Claude does this for real)
```
