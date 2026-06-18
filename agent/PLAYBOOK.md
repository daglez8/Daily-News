# News Agent Playbook

This is the exact procedure Claude Code runs on every refresh — manual or scheduled.
It does the fetching **and** the summarizing in one run, with **no separate LLM API**.

## Steps

### 1. Fetch (mechanical — Python)
Run the fetcher:
```
python3 agent/fetch_feeds.py
```
It reads `agent/config.json`, pulls recent articles from every enabled RSS source,
cleans them, removes duplicates, skips any source that fails, and writes
`agent/raw_candidates.json` (with a `run_log` showing what succeeded/failed).

### 2. Curate & summarize (judgment — Claude, this same run)
Read `agent/raw_candidates.json`. For **each** candidate, decide:

- **Relevance (0–100)** against the `interest_profile` in `config.json`.
  - Tier 1 topics → can score 80–100. Tier 2 → up to ~80. Tier 3 → up to ~75.
  - Reward direct hits on: Mexican financial services, mortgage/housing finance,
    HIR Casa / Creditaria / competitors, FIG & fintech M&A, AI in financial services,
    AI agents/governance. These are the core.
  - **Ignore the noise.** Real feeds carry sports, general politics, celebrity,
    crime, gaming, etc. Score those near zero. Substring keyword matching is NOT
    enough — use judgment (e.g. "día" is not "AI").
- **Drop** anything below `settings.min_relevance` (default 60).
- **Category** — assign exactly ONE of the 9 labels in `config.json.categories`.
- **Summary** — 2–3 sentences, concise, in the article's own language (es/en).
  - For full-text feeds, summarize the body.
  - For paywalled / headline-only feeds, summarize from the blurb and set `light: true`.
    Do not invent facts not present in the blurb.
- **light** — `true` if the source is paywalled (`paywall: true` in config), else `false`.

### 3. Apply learned preferences (feedback loop)
If `briefing-feedback.json` exists (exported from the dashboard's thumbs up/down):
- Nudge relevance **up** for articles similar to 👍 items (same category/source/themes).
- Nudge relevance **down** for those similar to 👎 items.
Keep nudges modest (±10–15) so one vote doesn't dominate.

### 4. Write the feed
Write the final array to `docs/news.json` (the file the dashboard reads and that
GitHub Pages serves), newest first.
Each item must have exactly these fields:
```
title, summary, link, source, published, category, relevance_score, language, light
```
Cap at `settings.target_count` (default 30) if there are more qualifying stories;
keep the highest-relevance ones.

Then publish so the Pages site updates:
```
git add docs/news.json && git commit -m "feed: refresh" && git push
```

### 5. Report
Print a one-line summary: how many sources ran, how many failed (from `run_log`),
how many candidates, how many made the cut, and note any category that came up empty
(e.g. "no HIR/Creditaria stories this run") — that's expected on quiet days, not a bug.

## Manual refresh (for testing)
Tell Claude Code: **"refresh my news"** — it runs steps 1–5, then click **Refresh**
in the dashboard to reload the updated `news.json`.

## Editing sources & interests
Everything tunable lives in `agent/config.json`:
- `sources` — add/remove feeds (set `"disabled": true` to mute one).
- `interest_profile` — edit your topics; this drives relevance scoring.
- `settings` — `min_relevance`, `max_age_hours`, `target_count`, etc.

## Known source notes
- **WSJ** free RSS is often stale (returns old articles) — it will usually contribute
  little. Harmless; it's skipped by the age filter.
- **El Economista** needs the browser User-Agent in `config.json` (already set) to avoid
  being blocked.
- **Reuters** has no public RSS and is disabled by design.
