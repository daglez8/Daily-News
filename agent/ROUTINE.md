# Cloud Routine Prompt

Paste this as the prompt when creating the scheduled cloud routine (see README → Phase 3).
It is what Claude Code runs in the cloud twice a day.

---

You are refreshing the personal news feed in this repository. Do this and nothing else.

1. Run: `python3 agent/fetch_feeds.py`
2. Read `agent/raw_candidates.json`. Following `agent/PLAYBOOK.md`:
   - Score each candidate 0–100 for relevance against the `interest_profile` in `agent/config.json`. Use judgment, not keyword matching — ignore sports, general politics, celebrity, crime, and gaming noise.
   - Drop anything below `settings.min_relevance`.
   - Assign exactly ONE category from `config.json.categories`.
   - Write a concise 2–3 sentence summary in the article's own language (es/en).
   - Set `light: true` for paywalled sources (`paywall: true`), summarizing from the blurb only.
   - Keep at most `settings.target_count`, newest first.
3. If `briefing-feedback.json` exists, apply the learned preferences (nudge ±10–15) per the playbook.
4. Write the result to `news.json` with exactly these fields per item:
   `title, summary, link, source, published, category, relevance_score, language, light`
5. Commit and push:
   `git add news.json && git commit -m "feed: scheduled refresh" && git push`
6. Print a one-line summary: sources ok/failed, candidate count, kept count, and any category that came up empty (that's expected, not an error).

Do NOT call any external LLM API or use any API key — you perform the summarization yourself as part of this run.
