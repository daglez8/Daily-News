# Daniel's Briefing — Personal News Dashboard

A private news dashboard that pulls the latest stories from your trusted sources,
keeps only the ones that match your interests (summarized, tagged, and scored),
and shows them in a clean UI. It refreshes automatically twice a day in the cloud —
**even when your laptop is closed** — and costs **$0/month**.

No external AI API and no API keys: the same scheduled Claude Code run that fetches
the news also writes the summaries.

---

## 1. Daily use

### See your news (on your Mac)
Double-click **`update.command`** in Finder. It pulls the latest feed, opens the
dashboard in your browser, and starts a tiny local server. Leave the little Terminal
window open while you read; press **Ctrl+C** there when done.

> First time only: macOS may warn about an unidentified developer. Right-click
> `update.command` → **Open** → **Open**. After that, double-click works.

Inside the dashboard:
- **Filter** by topic, source, or language (ES/EN); **sort** by Recent or Relevant; **search**.
- **👍 / 👎** each story — this teaches the agent what you like (see §4).
- **Refresh** reloads the feed file (use after a manual refresh below).
- Toggle **light/dark** top-right.

### Refresh the news right now (manual)
Tell Claude Code: **"refresh my news"**. It runs the fetch + curation and rewrites
`news.json`. Then click **Refresh** in the dashboard. (You normally don't need this —
the cloud routine does it automatically — but it's handy for testing.)

---

## 2. How it works (three simple pieces)

1. **The fetcher** — `agent/fetch_feeds.py` (pure Python, no installs) visits each RSS
   feed, pulls recent articles, cleans and de-duplicates them, and skips any source
   that fails.
2. **The curator** — Claude (during the same run) reads those articles, scores each
   against your interests, drops the irrelevant ones, tags and summarizes the rest,
   and writes **`news.json`**.
3. **The dashboard** — `index.html` reads `news.json` and displays it.

The full procedure lives in `agent/PLAYBOOK.md`.

---

## 3. Editing your sources & interests

Everything is in **`agent/config.json`**:
- **`sources`** — add or remove feeds. To mute one without deleting it, add `"disabled": true`.
- **`interest_profile`** — your topics, grouped by tier. This is what the relevance
  scoring is based on — edit freely.
- **`settings`** — `min_relevance` (cutoff, default 60), `max_age_hours`,
  `target_count` (max stories), etc.

Not sure how? Just tell Claude Code what you want ("add Milenio as a source",
"care more about RMBS deals") and it will edit the config for you.

---

## 4. The thumbs up/down feedback

Every story has 👍 / 👎. Your votes are saved in your browser, and the footer's
**"Export my feedback"** button downloads them as `briefing-feedback.json`.
Drop that file into the project folder and the agent will use it on the next run to
nudge similar stories up or down. The more you vote, the sharper your feed gets.

---

## 5. Phase 3 — Set up the twice-daily cloud refresh

One-time setup. The project is already a git repository with an initial commit.

### Step 1 — Create a **private** GitHub repo and push
1. On GitHub, click **New repository** → name it e.g. `daniels-briefing` →
   set **Private** → **do not** add a README/license → **Create repository**.
2. GitHub shows a "push an existing repository" box. In a Terminal, from this folder, run
   the two lines it gives you (they look like):
   ```
   git remote add origin https://github.com/<your-username>/daniels-briefing.git
   git branch -M main
   git push -u origin main
   ```
   (Or tell Claude Code "push this to my new GitHub repo <url>" and it will do it.)

### Step 2 — Create the scheduled cloud routine
1. Go to **claude.ai/code** → **Scheduled** (routines).
2. **New routine** → connect it to your `daniels-briefing` repo.
3. **Prompt:** paste the contents of **`agent/ROUTINE.md`**.
4. **Schedule:** twice daily — `0 7,18 * * *`, timezone **America/Mexico_City**
   (7:00 AM and 6:00 PM).
5. Save. (Prefer to let me do it? Once the repo is pushed, ask Claude Code to
   "set up the scheduled routine" and I'll run `/schedule` for you.)

### Step 3 — Test it
In the routine, click **Run now**. When it finishes, your repo's `news.json` should
have fresh stories and a new commit. On your Mac, double-click `update.command` to
pull and view them.

### Managing the routine (on claude.ai/code → Scheduled)
- **Pause / Resume** — temporarily stop or restart the schedule.
- **Run now** — trigger an extra refresh anytime.
- **Edit** — change the schedule or the prompt.
- **Delete** — remove it entirely.

---

## 6. Source notes & troubleshooting

- **Reuters** — no public RSS exists; intentionally disabled.
- **WSJ** — its free RSS is often stale (old articles); it will usually contribute
  little. Harmless — the age filter skips old items.
- **El Economista** — needs the browser User-Agent already set in `config.json`.
- **A category shows nothing** (e.g. no HIR/Creditaria stories) — normal on a quiet
  day. The agent reports empties instead of padding the feed.
- **Dashboard looks empty when you double-click `index.html` directly** — open it via
  `update.command` instead (a browser blocks local file reads without the small server).
- **A source stops working** — feeds change. Tell Claude Code and it'll find the new
  feed URL or flag the source.

---

## File map
```
index.html              the dashboard
news.json               the curated feed (written by the agent, read by the dashboard)
update.command          double-click: pull latest + open dashboard
server.js               tiny local web server
README.md               this file
agent/
  config.json           your sources, interests, settings  ← edit this
  fetch_feeds.py        the fetcher
  PLAYBOOK.md           the agent's step-by-step procedure
  ROUTINE.md            the prompt for the cloud routine
  curate.py             demo of the curation step (Claude does this for real)
```
