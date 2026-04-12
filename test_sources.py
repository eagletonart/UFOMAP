#!/usr/bin/env python3
"""
test_sources.py — probe external data sources for reachability and content.
Run with: python3 test_sources.py
"""

import urllib.request
import urllib.error

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml,*/*;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch(url, timeout=10):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
            return r.status, data
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:
        return None, str(e).encode()


def probe(label, url):
    print(f"\n{'─'*60}")
    print(f"  {label}")
    print(f"  {url}")
    status, data = fetch(url)
    if status is None:
        print(f"  ❌ FAILED: {data.decode()}")
    else:
        print(f"  ✅ HTTP {status} — {len(data):,} bytes")
        # Show first 400 chars of content (tags stripped roughly)
        snippet = data.decode("utf-8", errors="ignore")[:600]
        # Print a brief peek
        print(f"  Preview: {snippet[:400]!r}")


# ── MUFON candidates ──────────────────────────────────────────────────────────
probe("MUFON live cases",     "https://mufonlive.com/cases/")
probe("MUFON main site",      "https://mufon.com/")
probe("MUFON CMS query",      "https://mufoncms.com/cgi-bin/report_handler.pl?req=query_latest_reports")
probe("MUFON cases page alt", "https://mufon.com/cases/")

# ── Google News RSS ───────────────────────────────────────────────────────────
probe("Google News RSS — UFO sighting",
      "https://news.google.com/rss/search?q=UFO+sighting&hl=en-US&gl=US&ceid=US:en")
probe("Google News RSS — UAP sighting Pacific Northwest",
      "https://news.google.com/rss/search?q=UAP+sighting+Washington+Oregon&hl=en-US&gl=US&ceid=US:en")

# ── News Tribune RSS ──────────────────────────────────────────────────────────
probe("News Tribune search (raw HTML)",
      "https://www.thenewstribune.com/search?q=ufo+sighting")

# ── NUFORC recent (HTML parse issue) ─────────────────────────────────────────
probe("NUFORC ndxevent.html",
      "https://nuforc.org/webreports/ndxevent.html")

print(f"\n{'─'*60}")
print("Done.")
