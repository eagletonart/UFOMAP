#!/usr/bin/env python3
"""Quick connectivity test for three new data sources."""

import re
import urllib.request
import urllib.error

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}


def fetch(url, method="GET", timeout=12):
    req = urllib.request.Request(url, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, {}, b""
    except Exception as e:
        return None, {}, str(e).encode()


# ── 1. FAA wildlife ZIP ────────────────────────────────────────────────────
print("=" * 60)
print("1. FAA Wildlife Strike Database ZIP")
print("   URL: https://wildlife.faa.gov/downloads/wildlife.zip")
status, hdrs, _ = fetch("https://wildlife.faa.gov/downloads/wildlife.zip", method="HEAD")
if status:
    print(f"   HTTP {status}")
    for h in ("Content-Length", "Content-Type", "Last-Modified", "Content-Disposition"):
        if h in hdrs:
            print(f"   {h}: {hdrs[h]}")
else:
    print(f"   FAILED: {_.decode()}")

# ── 2. NUFORC recent events page ──────────────────────────────────────────
print()
print("=" * 60)
print("2. NUFORC Recent Events")
print("   URL: https://nuforc.org/webreports/ndxevent.html")
status, hdrs, body = fetch("https://nuforc.org/webreports/ndxevent.html")
if status and body:
    html = body.decode("utf-8", errors="replace")
    print(f"   HTTP {status}  |  page size: {len(html):,} bytes")
    trs  = re.findall(r"<tr[\s>]", html, re.IGNORECASE)
    tds  = re.findall(r"<td[\s>]", html, re.IGNORECASE)
    links = re.findall(r'href="([^"]*ndxe[^"]*)"', html, re.IGNORECASE)
    print(f"   <tr> tags: {len(trs)}  |  <td> tags: {len(tds)}  |  event links: {len(links)}")
    # Show a snippet of raw HTML around first table
    idx = html.lower().find("<table")
    if idx >= 0:
        print(f"   First <table> snippet: {html[idx:idx+300]!r}")
    else:
        print("   No <table> tag found — may be JS-rendered")
    if links:
        print(f"   Sample links: {links[:3]}")
else:
    print(f"   FAILED: status={status}  body={_.decode()[:200]}")

# ── 3. NICAP Blue Book index ──────────────────────────────────────────────
print()
print("=" * 60)
print("3. NICAP Blue Book Index")
print("   URL: http://www.nicap.org/BB/BBindex.htm")
status, hdrs, body = fetch("http://www.nicap.org/BB/BBindex.htm")
if status and body:
    html = body.decode("utf-8", errors="replace")
    print(f"   HTTP {status}  |  page size: {len(html):,} bytes")
    all_links = re.findall(r'href="([^"]+)"', html, re.IGNORECASE)
    bb_links  = [l for l in all_links if "BB" in l or ".htm" in l.lower()]
    print(f"   Total links: {len(all_links)}  |  BB/htm links: {len(bb_links)}")
    # Look for location/date patterns
    dates = re.findall(r'\b(19[4-9]\d|20[0-2]\d)\b', html)
    print(f"   Year mentions: {len(dates)}  range: {min(dates) if dates else 'n/a'}–{max(dates) if dates else 'n/a'}")
    if bb_links:
        print(f"   Sample BB links: {bb_links[:5]}")
    # Show raw snippet
    print(f"   HTML snippet: {html[200:500]!r}")
else:
    print(f"   FAILED: status={status}")

print()
print("=" * 60)
print("Done.")
