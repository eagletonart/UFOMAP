#!/usr/bin/env python3
"""test_cia.py — probe Arctic Shift API and CIA CREST database."""

import urllib.request
import urllib.error
import json
import re

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml,*/*;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
}

SEP = "─" * 60


def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:
        return None, str(e).encode()


# ── 1. Arctic Shift ───────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("  Arctic Shift — r/UFOs recent posts")
url = "https://arctic-shift.photon-reddit.com/api/posts/search?subreddit=ufos&limit=5&sort=desc"
print(f"  {url}")

status, data = fetch(url)
if status is None:
    print(f"  FAILED: {data.decode()}")
else:
    print(f"  HTTP {status} — {len(data):,} bytes")
    try:
        d = json.loads(data)
        posts = d.get("data") or []
        print(f"  Posts returned: {len(posts)}")
        print(f"  Top-level keys in response: {list(d.keys())}")
        print(f"  Keys in each post: {list(posts[0].keys()) if posts else 'none'}")
        print()
        for i, p in enumerate(posts, 1):
            print(f"  [{i}] title:  {p.get('title', '')[:80]}")
            print(f"       flair:  {p.get('link_flair_text', 'none')}")
            print(f"       body:   {(p.get('selftext') or '')[:120]!r}")
            print(f"       score:  {p.get('score')}  |  created_utc: {p.get('created_utc')}")
            print()
    except Exception as e:
        print(f"  JSON parse error: {e}")
        print(f"  Raw: {data[:300]!r}")

# ── 2. CIA CREST ──────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("  CIA CREST — UFO document search")
url = "https://www.cia.gov/readingroom/search/site/UFO"
print(f"  {url}")

status, data = fetch(url)
if status is None:
    print(f"  FAILED: {data.decode()}")
else:
    text = data.decode("utf-8", errors="ignore")
    print(f"  HTTP {status} — {len(text):,} chars")
    print(f"\n  First 500 chars:\n  {text[:500]!r}")

    # Try various title patterns
    patterns = [
        r'<h3[^>]*>(.*?)</h3>',
        r'<h2[^>]*>(.*?)</h2>',
        r'"title"\s*:\s*"([^"]{10,})"',
        r'class="[^"]*title[^"]*"[^>]*>(.*?)<',
        r'<a[^>]+href="[^"]*readingroom/document[^"]*"[^>]*>(.*?)</a>',
    ]
    found = []
    for pat in patterns:
        matches = re.findall(pat, text, re.DOTALL | re.IGNORECASE)
        clean = [re.sub(r'<[^>]+>', '', m).strip() for m in matches]
        clean = [c for c in clean if len(c) > 5]
        if clean:
            print(f"\n  Pattern {pat[:40]!r} → {len(clean)} matches:")
            for t in clean[:5]:
                print(f"    • {t[:120]}")
            found.extend(clean)

    if not found:
        print("\n  No document titles found — page may be JS-rendered or blocked.")
        # Show a broader sample to understand the structure
        print(f"\n  Chars 500-1500:\n  {text[500:1500]!r}")

print(f"\n{SEP}")
print("Done.")
