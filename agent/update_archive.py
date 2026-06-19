#!/usr/bin/env python3
"""
update_archive.py — merge the current feed (docs/news.json) into the rolling
history (docs/archive.json): dedupe by link, keep the newest 500. Run this right
after writing docs/news.json so the dashboard's History / Liked views stay complete.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
news_path = os.path.join(HERE, "..", "docs", "news.json")
arch_path = os.path.join(HERE, "..", "docs", "archive.json")

news = json.load(open(news_path, encoding="utf-8"))
archive = []
if os.path.exists(arch_path):
    try: archive = json.load(open(arch_path, encoding="utf-8"))
    except Exception: archive = []

by = {a["link"]: a for a in archive}
for a in news:
    by.setdefault(a["link"], a)
archive = sorted(by.values(), key=lambda a: a.get("published") or "", reverse=True)[:500]

json.dump(archive, open(arch_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"archive.json now holds {len(archive)} articles")
