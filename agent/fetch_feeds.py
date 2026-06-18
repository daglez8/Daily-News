#!/usr/bin/env python3
"""
fetch_feeds.py — Phase 2 fetcher for the personal news dashboard.

Mechanical step only: visit each RSS feed in config.json, pull recent articles,
clean them, deduplicate, skip any source that fails, and write the raw candidates
to agent/raw_candidates.json for the summarization step (done by Claude) to process.

Pure Python standard library — no pip installs, nothing to break.

Usage:  python3 agent/fetch_feeds.py
"""

import json
import os
import re
import ssl
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from html import unescape
from html.parser import HTMLParser
from xml.etree import ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "config.json")
OUT_PATH = os.path.join(HERE, "raw_candidates.json")

# RSS/Atom namespaces we care about
NS = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "atom": "http://www.w3.org/2005/Atom",
}


def log(msg):
    print(f"[fetch] {msg}", file=sys.stderr)


class _Stripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, d):
        self.parts.append(d)


def strip_html(text):
    if not text:
        return ""
    s = _Stripper()
    try:
        s.feed(text)
        text = "".join(s.parts)
    except Exception:
        text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def parse_date(raw):
    """Parse RFC822 (RSS) or ISO8601 (Atom) dates -> aware datetime in UTC, or None."""
    if not raw:
        return None
    raw = raw.strip()
    # RFC822 e.g. "Wed, 18 Jun 2026 13:10:00 -0600"
    try:
        dt = parsedate_to_datetime(raw)
        if dt:
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        pass
    # ISO8601 e.g. "2026-06-18T13:10:00-06:00" / "...Z"
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def fetch(url, user_agent, timeout=20):
    req = urllib.request.Request(url, headers={
        "User-Agent": user_agent,
        "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
    })
    # Try verified TLS first; fall back to unverified if the system cert store is incomplete.
    for ctx in (ssl.create_default_context(), ssl._create_unverified_context()):
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                return r.read()
        except (ssl.SSLError, urllib.error.URLError) as e:
            last = e
            continue
    raise last


def text_of(el):
    return (el.text or "").strip() if el is not None else ""


def parse_feed(xml_bytes, source, default_lang):
    """Return a list of normalized entries from RSS or Atom XML."""
    # Some feeds (e.g. Feedburner) emit a BOM or leading whitespace before <?xml,
    # which breaks the parser — trim everything before the first '<'.
    lt = xml_bytes.find(b"<")
    if lt > 0:
        xml_bytes = xml_bytes[lt:]
    root = ET.fromstring(xml_bytes)
    items = []

    # RSS: <rss><channel><item>...   /   RDF: <item> at top level
    rss_items = root.findall(".//item")
    if rss_items:
        for it in rss_items:
            link = text_of(it.find("link")) or text_of(it.find("guid"))
            summary = text_of(it.find("description"))
            content = it.find("content:encoded", NS)
            if content is not None and text_of(content):
                summary = text_of(content)
            pub = text_of(it.find("pubDate")) or text_of(it.find("dc:date", NS))
            items.append({
                "title": strip_html(text_of(it.find("title"))),
                "link": link.strip(),
                "raw_summary": strip_html(summary),
                "published": pub,
            })
        return items

    # Atom: <feed><entry>...
    for it in root.findall("atom:entry", NS) or root.findall(".//{http://www.w3.org/2005/Atom}entry"):
        link = ""
        for l in it.findall("atom:link", NS):
            if l.get("rel", "alternate") == "alternate":
                link = l.get("href", "")
                break
        if not link:
            le = it.find("atom:link", NS)
            link = le.get("href", "") if le is not None else ""
        summary = text_of(it.find("atom:content", NS)) or text_of(it.find("atom:summary", NS))
        pub = text_of(it.find("atom:published", NS)) or text_of(it.find("atom:updated", NS))
        items.append({
            "title": strip_html(text_of(it.find("atom:title", NS))),
            "link": link.strip(),
            "raw_summary": strip_html(summary),
            "published": pub,
        })
    return items


def norm_title(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def main():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        cfg = json.load(f)

    s = cfg["settings"]
    ua = s["user_agent"]
    max_age = timedelta(hours=s.get("max_age_hours", 48))
    max_per = s.get("max_per_source", 20)
    now = datetime.now(timezone.utc)

    candidates = []
    seen_links = set()
    seen_titles = set()
    run_log = []

    for src in cfg["sources"]:
        if src.get("disabled"):
            run_log.append({"source": src["name"], "url": src["url"], "status": "skipped (disabled)", "kept": 0})
            continue
        name, url, lang = src["name"], src["url"], src.get("lang", "en")
        try:
            raw = fetch(url, ua)
            entries = parse_feed(raw, name, lang)
        except Exception as e:
            log(f"FAIL {name}: {type(e).__name__}: {e}")
            run_log.append({"source": name, "url": url, "status": f"error: {type(e).__name__}", "kept": 0})
            continue

        kept = 0
        for e in entries:
            if not e["title"] or not e["link"]:
                continue
            dt = parse_date(e["published"])
            if dt and (now - dt) > max_age:
                continue  # too old
            link_key = e["link"].split("?")[0].rstrip("/")
            title_key = norm_title(e["title"])
            if link_key in seen_links or (title_key and title_key in seen_titles):
                continue  # duplicate
            seen_links.add(link_key)
            if title_key:
                seen_titles.add(title_key)
            candidates.append({
                "title": e["title"],
                "link": e["link"],
                "raw_summary": e["raw_summary"][:1200],
                "source": name,
                "published": dt.isoformat() if dt else None,
                "language": lang,
                "paywall": bool(src.get("paywall", False)),
            })
            kept += 1
            if kept >= max_per:
                break
        run_log.append({"source": name, "url": url, "status": "ok", "kept": kept})
        log(f"OK   {name}: kept {kept}")

    # newest first
    candidates.sort(key=lambda c: c["published"] or "", reverse=True)

    out = {
        "generated_at": now.isoformat(),
        "settings": s,
        "run_log": run_log,
        "candidate_count": len(candidates),
        "candidates": candidates,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    ok = sum(1 for r in run_log if r["status"] == "ok")
    fail = sum(1 for r in run_log if r["status"].startswith("error"))
    log(f"DONE {len(candidates)} candidates from {ok} sources ({fail} failed). Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
