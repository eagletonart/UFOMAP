#!/usr/bin/env python3
"""
fetch_data.py — collect and export all UFO map data.

Sources:
  1. Local NUFORC CSV (bulk historical sightings + abduction filter)
  2. NUFORC recent — tries subndx/?id=event, falls back to CSV sorted by date
  3. Reddit r/ufos and r/UFOs — JSON API with browser UA
  4. (MUFON removed — mufonlive.com DNS dead)
  5. Google News RSS — UFO/UAP queries, location extracted by regex

Run with: python3 fetch_data.py
"""

import csv
import json
import os
import re
import subprocess
import time
import urllib.request
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from html.parser import HTMLParser

from constants import (
    NUFORC_CSV, EXPORT_FILE,
    NUFORC_FIELDS, ABDUCTION_KEYWORDS,
    MILITARY_BASES, COG_SITES, USO_SITES, MISSING_411_SITES, MISSING_SCIENTISTS,
    PARALLEL_33_SITES, NUCLEAR_SITES, CATTLE_MUTILATION_SITES, WINDOW_AREAS, LEY_LINES,
    WATER_ANOMALY_SITES,
)

# ── US state → approximate center lat/lon ──────────────────────────────────
STATE_COORDS = {
    "AL": (32.8, -86.8), "AK": (64.2, -153.4), "AZ": (34.3, -111.1),
    "AR": (34.8, -92.2), "CA": (36.8, -119.4), "CO": (39.0, -105.5),
    "CT": (41.6, -72.7), "DE": (39.0, -75.5),  "FL": (27.8, -81.5),
    "GA": (32.2, -83.4), "HI": (20.3, -156.4), "ID": (44.4, -114.5),
    "IL": (40.3, -89.0), "IN": (40.3, -86.1),  "IA": (42.0, -93.2),
    "KS": (38.5, -98.4), "KY": (37.5, -85.3),  "LA": (31.1, -91.8),
    "ME": (44.7, -69.4), "MD": (39.1, -76.8),  "MA": (42.2, -71.5),
    "MI": (44.3, -85.4), "MN": (46.4, -93.1),  "MS": (32.7, -89.7),
    "MO": (38.5, -92.5), "MT": (47.0, -110.5), "NE": (41.5, -99.9),
    "NV": (38.5, -117.0),"NH": (43.2, -71.6),  "NJ": (40.1, -74.5),
    "NM": (34.5, -106.1),"NY": (42.9, -75.5),  "NC": (35.5, -79.4),
    "ND": (47.5, -100.5),"OH": (40.4, -82.8),  "OK": (35.6, -97.5),
    "OR": (44.0, -120.5),"PA": (40.9, -77.8),  "RI": (41.7, -71.5),
    "SC": (33.8, -81.2), "SD": (44.4, -100.3), "TN": (35.9, -86.7),
    "TX": (31.5, -99.3), "UT": (39.3, -111.1), "VT": (44.1, -72.7),
    "VA": (37.8, -78.2), "WA": (47.4, -120.6), "WV": (38.6, -80.6),
    "WI": (44.6, -89.8), "WY": (43.0, -107.6), "DC": (38.9, -77.0),
}

ANTHROPIC_API_KEY  = os.environ.get("ANTHROPIC_API_KEY", "")
REDDIT_CACHE_FILE  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reddit_cache.json")

ARCTIC_SHIFT_SUBS  = [
    # UFO/UAP sighting subs → go into main sightings layer
    "ufos", "UFOs", "UAP", "aliens", "HighStrangeness",
    "Paranormal", "UFOsighting", "Glitch_in_the_Matrix", "NightVision",
    # Humanoid/cryptid subs → humanoid_encounters layer
    "Humanoidencounters", "cryptids", "GhostStories",
    # Missing persons sub → reddit_missing layer
    "Missing411",
]
MISSING_SUBS   = {"Missing411"}
HUMANOID_SUBS  = {"Humanoidencounters", "cryptids"}

# Rough country center coordinates for non-US sightings
_COUNTRY_COORDS = {
    "GB": (54.0,  -2.0), "CA": (56.0, -96.0), "AU": (-25.0, 133.0),
    "DE": (51.0,  10.0), "FR": (46.0,   2.0), "ES": ( 40.0,  -4.0),
    "IT": (42.0,  12.0), "NL": (52.0,   5.0), "BE": ( 50.5,   4.5),
    "SE": (62.0,  15.0), "NO": (62.0,  10.0), "FI": ( 64.0,  26.0),
    "DK": (56.0,  10.0), "CH": (47.0,   8.0), "AT": ( 47.5,  14.5),
    "PL": (52.0,  20.0), "NZ": (-41.0, 174.0),"ZA": (-29.0,  25.0),
    "BR": (-10.0,-55.0), "MX": (23.0, -102.0),"AR": (-34.0, -64.0),
    "IN": (20.0,  77.0), "JP": (36.0,  138.0),"KR": ( 36.0, 128.0),
}

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/json,*/*;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
}


def _fetch(url, timeout=12):
    """GET url with browser UA; returns text or None."""
    req = urllib.request.Request(url, headers=BROWSER_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  ⚠ fetch failed ({url}): {e}")
        return None


# ── 1. Local NUFORC CSV ────────────────────────────────────────────────────

def load_nuforc(max_records=5000):
    print(f"Loading NUFORC CSV sightings (up to {max_records})...")
    sightings = []
    with open(NUFORC_CSV, encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f, fieldnames=NUFORC_FIELDS)
        for i, row in enumerate(reader):
            if i >= max_records:
                break
            try:
                lat = float(row.get("latitude") or 0)
                lon = float(row.get("longitude") or 0)
                if lat == 0 and lon == 0:
                    continue
                city  = row.get("city", "")
                state = row.get("state", "")
                sightings.append({
                    "source":         "NUFORC",
                    "lat":            lat,
                    "lon":            lon,
                    "date":           row.get("datetime", ""),
                    "city":           city,
                    "state":          state,
                    "country":        row.get("country", ""),
                    "shape":          row.get("shape", "unknown"),
                    "duration":       row.get("duration_seconds", ""),
                    "summary":        row.get("comments", "")[:300],
                    "location_label": f"{city}, {state}".strip(", "),
                })
            except (ValueError, KeyError):
                continue
    print(f"  {len(sightings)} CSV sightings loaded")
    return sightings


def load_nuforc_abductions():
    print("Mining NUFORC CSV for abduction reports...")
    sightings = []
    with open(NUFORC_CSV, encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f, fieldnames=NUFORC_FIELDS)
        for row in reader:
            text = (row.get("comments") or "").lower()
            if not any(k in text for k in ABDUCTION_KEYWORDS):
                continue
            try:
                lat = float(row.get("latitude") or 0)
                lon = float(row.get("longitude") or 0)
                if lat == 0 and lon == 0:
                    continue
                city  = row.get("city", "")
                state = row.get("state", "")
                sightings.append({
                    "source":         "NUFORC Abduction",
                    "lat":            lat,
                    "lon":            lon,
                    "date":           row.get("datetime", ""),
                    "city":           city,
                    "state":          state,
                    "country":        row.get("country", ""),
                    "shape":          row.get("shape", "unknown"),
                    "summary":        row.get("comments", "")[:300],
                    "location_label": f"{city}, {state}".strip(", "),
                })
            except (ValueError, KeyError):
                continue
    print(f"  {len(sightings)} abduction reports found")
    return sightings


# ── 2. NUFORC recent web reports ───────────────────────────────────────────

class _NuforcTableParser(HTMLParser):
    """Pull (city, state, shape, date, summary) rows from ndxevent.html table."""
    def __init__(self):
        super().__init__()
        self.rows, self._row, self._cell, self._in_td = [], [], "", False
    def handle_starttag(self, tag, attrs):
        if tag == "tr":  self._row = []
        if tag == "td":  self._in_td = True; self._cell = ""
    def handle_endtag(self, tag):
        if tag == "td":
            self._row.append(self._cell.strip())
            self._in_td = False
        if tag == "tr" and len(self._row) >= 5:
            self.rows.append(self._row[:])
    def handle_data(self, data):
        if self._in_td:
            self._cell += data


def _parse_nuforc_html(html, max_rows=300):
    """Try to pull sighting rows out of a NUFORC HTML page."""
    import random
    parser = _NuforcTableParser()
    parser.feed(html)
    sightings = []
    for row, _ in (parser.rows if isinstance(parser.rows[0], tuple) else
                   [(r, "") for r in parser.rows]) if parser.rows else []:
        try:
            date  = row[0].strip()
            city  = row[1].strip()
            state = row[2].strip().upper()
            shape = row[3].strip().lower() or "unknown"
            summary = row[5].strip() if len(row) > 5 else ""
            coords = STATE_COORDS.get(state)
            if not coords:
                continue
            lat = round(coords[0] + random.uniform(-1.5, 1.5), 4)
            lon = round(coords[1] + random.uniform(-1.5, 1.5), 4)
            sightings.append({
                "source":         "NUFORC Recent",
                "lat":            lat,
                "lon":            lon,
                "date":           date,
                "city":           city,
                "state":          state,
                "country":        "US",
                "shape":          shape,
                "duration":       "",
                "summary":        summary[:300],
                "location_label": f"{city}, {state}".strip(", "),
            })
            if len(sightings) >= max_rows:
                break
        except (IndexError, KeyError):
            continue
    return sightings


def _nuforc_recent_from_csv(max_records=500):
    """Most recent NUFORC reports from local CSV, sorted newest-first."""
    print("  ↳ Falling back to local CSV (sorted by date desc)…")
    rows = []
    with open(NUFORC_CSV, encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f, fieldnames=NUFORC_FIELDS)
        for row in reader:
            try:
                lat = float(row.get("latitude") or 0)
                lon = float(row.get("longitude") or 0)
                if lat == 0 and lon == 0:
                    continue
                date_str = (row.get("datetime") or "").strip()
                if not date_str:
                    continue
                city  = row.get("city", "")
                state = row.get("state", "")
                rows.append({
                    "source":         "NUFORC Recent",
                    "lat":            lat,
                    "lon":            lon,
                    "date":           date_str,
                    "city":           city,
                    "state":          state,
                    "country":        row.get("country", ""),
                    "shape":          row.get("shape", "unknown"),
                    "duration":       row.get("duration_seconds", ""),
                    "summary":        row.get("comments", "")[:300],
                    "location_label": f"{city}, {state}".strip(", "),
                    "_dt":            date_str,
                })
            except (ValueError, KeyError):
                continue

    def _parse_dt(s):
        for fmt in ("%m/%d/%Y %H:%M", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y"):
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        return datetime.min

    rows.sort(key=lambda r: _parse_dt(r["_dt"]), reverse=True)
    result = rows[:max_records]
    for r in result:
        r.pop("_dt", None)
    return result


def fetch_nuforc_recent(max_rows=500):
    """Scrape the last 3 months of NUFORC reports from monthly sub-pages.

    Page structure (from test_nuforc_recent.py):
      cols: status, datetime, city, state, country, shape, summary, date, _, _
    Falls back to local CSV if all scrapes fail.
    """
    import random
    print("Fetching NUFORC recent reports…")

    # Build last-3-months IDs dynamically
    now = datetime.utcnow()
    month_ids = []
    y, m = now.year, now.month
    for _ in range(3):
        month_ids.append(f"e{y}{m:02d}")
        m -= 1
        if m == 0:
            m = 12
            y -= 1

    # Country → approximate coords for non-US sightings
    COUNTRY_APPROX = {
        "CANADA": (56.0, -96.0), "AUSTRALIA": (-25.0, 133.0),
        "UK": (54.0, -2.0), "UNITED KINGDOM": (54.0, -2.0),
        "GERMANY": (51.0, 10.0), "FRANCE": (46.0, 2.0),
        "MEXICO": (23.0, -102.0), "BRAZIL": (-14.0, -51.0),
        "NEW ZEALAND": (-41.0, 174.0), "INDIA": (20.0, 77.0),
        "SOUTH AFRICA": (-29.0, 25.0),
    }

    sightings = []
    for mid in month_ids:
        url = f"https://nuforc.org/subndx/?id={mid}"
        html = _fetch(url)
        if not html:
            print(f"  ⚠ fetch failed for {mid}")
            continue

        trs = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.DOTALL | re.IGNORECASE)
        count_before = len(sightings)
        for tr in trs:
            cells_raw = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.DOTALL | re.IGNORECASE)
            cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells_raw]
            if len(cells) < 7:
                continue
            # cols: status(0), datetime(1), city(2), state(3), country(4), shape(5), summary(6), date(7)
            city    = cells[2].strip()
            state   = cells[3].strip().upper()
            country = cells[4].strip().upper()
            shape   = cells[5].strip().lower() or "unknown"
            summary = cells[6].strip()
            date    = cells[7].strip() if len(cells) > 7 else cells[1][:10]

            coords = STATE_COORDS.get(state)
            jitter = 1.5
            if not coords:
                coords = COUNTRY_APPROX.get(country)
                jitter = 3.5
            if not coords:
                continue

            lat = round(coords[0] + random.uniform(-jitter, jitter), 4)
            lon = round(coords[1] + random.uniform(-jitter, jitter), 4)
            sightings.append({
                "source":         "NUFORC Recent",
                "lat":            lat,
                "lon":            lon,
                "date":           date,
                "city":           city,
                "state":          state,
                "country":        country,
                "shape":          shape,
                "summary":        summary[:300],
                "location_label": f"{city}, {state}".strip(", "),
            })
            if len(sightings) >= max_rows:
                break

        added = len(sightings) - count_before
        print(f"  {mid}: {added} reports parsed")
        if len(sightings) >= max_rows:
            break
        time.sleep(0.5)

    if sightings:
        print(f"  {len(sightings)} NUFORC recent reports from monthly pages")
        return sightings

    result = _nuforc_recent_from_csv(max_rows)
    print(f"  {len(result)} recent NUFORC reports (local CSV fallback)")
    return result


# ── 3. Reddit r/ufos ──────────────────────────────────────────────────────

# Rough regex patterns to extract US state or city from reddit post titles
_STATE_RE = re.compile(
    r'\b(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|'
    r'MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|'
    r'VA|WA|WV|WI|WY|DC)\b'
)
_SHAPE_WORDS = {
    "triangle", "triangular", "disk", "disc", "orb", "sphere", "light", "lights",
    "fireball", "cigar", "oval", "chevron", "boomerang", "cylinder", "diamond",
    "rectangle", "formation", "craft", "ufo", "uap", "object",
}


def _reddit_shape(title):
    words = title.lower().split()
    for w in words:
        w = w.strip(".,!?()[]")
        if w in _SHAPE_WORDS:
            return w
    return "unknown"


def fetch_reddit_ufos(max_posts=200):
    """Fetch r/ufos and r/UFOs JSON; extract posts with location hints."""
    print("Fetching Reddit r/ufos + r/UFOs recent posts...")
    sightings = []
    seen = set()
    for sub in ("ufos", "UFOs"):
        url = f"https://www.reddit.com/r/{sub}.json?limit=100&raw_json=1"
        text = _fetch(url)
        if not text:
            continue
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            continue
        posts = data.get("data", {}).get("children", [])
        for post in posts:
            p = post.get("data", {})
            title   = p.get("title", "")
            selftext = p.get("selftext", "")
            flair   = p.get("link_flair_text", "") or ""
            created = p.get("created_utc", 0)
            url_p   = p.get("url", "")
            post_id = p.get("id", "")
            if post_id in seen:
                continue
            seen.add(post_id)

            # Skip megathreads, memes, news articles
            low = title.lower()
            if any(x in low for x in ("weekly", "megathread", "meme", "humor", "discussion")):
                continue

            # Try to find a US state abbreviation
            m = _STATE_RE.search(title + " " + selftext[:200])
            if not m:
                continue
            state = m.group(1)
            coords = STATE_COORDS.get(state)
            if not coords:
                continue
            lat, lon = coords
            import random
            lat += random.uniform(-1.8, 1.8)
            lon += random.uniform(-1.8, 1.8)

            date_str = datetime.utcfromtimestamp(created).strftime("%m/%d/%Y") if created else ""
            summary  = (title + (" — " + selftext[:200] if selftext else ""))[:300]

            sightings.append({
                "source":         "Reddit",
                "lat":            round(lat, 4),
                "lon":            round(lon, 4),
                "date":           date_str,
                "city":           "",
                "state":          state,
                "country":        "US",
                "shape":          _reddit_shape(title),
                "duration":       "",
                "summary":        summary,
                "location_label": state,
                "url":            url_p,
            })
            if len(sightings) >= max_posts:
                break
        time.sleep(0.5)   # be polite

    print(f"  {len(sightings)} Reddit sightings extracted")
    return sightings


# ── 3b. Arctic Shift Reddit (Claude-assisted location extraction) ──────────

def _load_reddit_cache():
    """Load {post_id: sighting_dict_or_None} from reddit_cache.json."""
    if os.path.exists(REDDIT_CACHE_FILE):
        try:
            with open(REDDIT_CACHE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"processed": {}}


def _save_reddit_cache(cache):
    with open(REDDIT_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def _claude_extract_location(title, body_excerpt):
    """Ask Claude Haiku to extract location from a Reddit post.
    Returns dict {city, state, country, confidence} or None on failure."""
    if not ANTHROPIC_API_KEY:
        return None
    prompt = (
        "Extract the geographic location from this Reddit UFO/UAP sighting post.\n\n"
        f"Title: {title}\n"
        f"Body excerpt: {body_excerpt}\n\n"
        "Return ONLY a JSON object with these exact fields:\n"
        '  "city":       city name string or null\n'
        '  "state":      US state 2-letter code or null\n'
        '  "country":    ISO 2-letter country code (US, GB, CA, AU, FR, DE, etc.) or null\n'
        '  "confidence": "high" (explicit city/state named), "medium" (region/state only),'
        ' "low" (vague), or "none" (no location at all)\n\n'
        "Return ONLY the JSON object, no markdown, no explanation."
    )
    payload = json.dumps({
        "model":      "claude-haiku-4-5-20251001",
        "max_tokens": 120,
        "messages":   [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key":         ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type":      "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            resp = json.loads(r.read())
            text = resp["content"][0]["text"].strip()
            # Strip optional markdown fences
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
            return json.loads(text)
    except Exception as e:
        print(f"    ⚠ Claude API error: {e}")
        return None


def fetch_arctic_shift_reddit(max_per_sub=200):
    """Fetch Reddit sightings from Arctic Shift.

    Location extraction strategy:
      - With ANTHROPIC_API_KEY: Claude Haiku extracts city/state/country with
        medium-to-high confidence (international coverage, better accuracy).
      - Without API key: regex state-abbreviation fallback keeps sightings
        flowing even when the key is absent or the .env file is missing.
    """
    print("Fetching Reddit sightings via Arctic Shift API…")
    use_claude = bool(ANTHROPIC_API_KEY)
    if not use_claude:
        print("  ⚠ ANTHROPIC_API_KEY not set — using regex state fallback for location extraction")

    cache     = _load_reddit_cache()
    processed = cache.setdefault("processed", {})
    import random

    # ── 1. Collect candidate posts across all subreddits ──────────────────
    # Arctic Shift caps limit at 100; paginate with `before` timestamp for more.
    PAGE_SIZE = 100
    PAGES     = max(1, (max_per_sub + PAGE_SIZE - 1) // PAGE_SIZE)

    all_posts  = {}   # id → post dict
    for sub in ARCTIC_SHIFT_SUBS:
        sub_posts = []
        before    = ""
        for page in range(PAGES):
            qs  = f"subreddit={sub}&limit={PAGE_SIZE}&sort=desc"
            if before:
                qs += f"&before={before}"
            text = _fetch(
                f"https://arctic-shift.photon-reddit.com/api/posts/search?{qs}"
            )
            if not text:
                print(f"  ⚠ Arctic Shift fetch failed for r/{sub} page {page+1}")
                break
            try:
                batch = json.loads(text).get("data") or []
            except json.JSONDecodeError:
                print(f"  ⚠ JSON parse error for r/{sub} page {page+1}")
                break
            if not batch:
                break
            sub_posts.extend(batch)
            before = batch[-1].get("created_utc", "")
            time.sleep(0.3)

        kept = 0
        for p in sub_posts:
            pid   = p.get("id", "")
            if not pid or pid in all_posts:
                continue
            flair = (p.get("link_flair_text") or "").lower()
            title = (p.get("title") or "").lower()
            body  = (p.get("selftext") or "")

            # Skip obvious non-sighting content
            if any(x in title for x in
                   ("weekly thread", "megathread", "daily discussion",
                    "modpost", "mod post", "rules")):
                continue

            # Accept if: sighting flair, "sighting" in title, or state abbr hint in text
            is_sighting = ("sighting" in flair or "sighting" in title
                           or bool(_STATE_RE.search(p.get("title","") + " " + body[:300])))
            if is_sighting:
                all_posts[pid] = p
                kept += 1

        print(f"  r/{sub}: {len(sub_posts)} fetched → {kept} candidates")

    print(f"  Total unique candidates: {len(all_posts)}")

    # ── 2. Split into cached vs. new ──────────────────────────────────────
    cached_hits  = [(pid, processed[pid])
                    for pid in all_posts if pid in processed and processed[pid] is not None]
    new_posts    = [(pid, all_posts[pid])
                    for pid in all_posts if pid not in processed]

    print(f"  {len(cached_hits)} from cache  |  {len(new_posts)} new → sending to Claude")

    # ── 3. Build results from cache ───────────────────────────────────────
    sightings = [s for _, s in cached_hits]

    # ── 4. Process new posts: Claude when available, regex fallback otherwise ─
    for i, (pid, p) in enumerate(new_posts):
        if i > 0 and i % 25 == 0:
            print(f"    … {i}/{len(new_posts)} processed so far ({len(sightings)} located)")
            _save_reddit_cache(cache)   # checkpoint

        title       = (p.get("title")    or "").strip()
        body_excerpt= (p.get("selftext") or "").strip()[:400]
        subreddit   = p.get("subreddit", "")
        created_utc = p.get("created_utc", 0)

        if use_claude:
            loc = _claude_extract_location(title, body_excerpt)
            time.sleep(0.08)   # stay well under rate limit
            if not loc or loc.get("confidence") not in ("high", "medium"):
                processed[pid] = None
                continue
            state   = (loc.get("state")   or "").upper().strip()
            city    = (loc.get("city")    or "").strip()
            country = (loc.get("country") or "US").upper().strip()
        else:
            # Regex fallback: US state abbreviation only, no Claude call
            m = _STATE_RE.search(title + " " + body_excerpt[:300])
            if not m:
                processed[pid] = None
                continue
            state   = m.group(1)
            city    = ""
            country = "US"

        # Resolve coordinates
        if state and state in STATE_COORDS:
            base = STATE_COORDS[state]
            jitter = 1.8
        elif country and country in _COUNTRY_COORDS:
            base   = _COUNTRY_COORDS[country]
            state  = ""
            jitter = 3.5   # country-level only, wider jitter
        else:
            processed[pid] = None
            continue

        lat = round(base[0] + random.uniform(-jitter, jitter), 4)
        lon = round(base[1] + random.uniform(-jitter, jitter), 4)

        date_str = (datetime.utcfromtimestamp(created_utc).strftime("%m/%d/%Y")
                    if created_utc else "")
        summary  = (title + (" — " + body_excerpt[:200] if body_excerpt else ""))[:300]
        loc_lbl  = (f"{city}, {state}" if city and state
                    else state or city or country)
        permalink = p.get("permalink", "")
        url_str   = f"https://reddit.com{permalink}" if permalink else ""

        sighting = {
            "source":         "Reddit",
            "subreddit":      subreddit,
            "lat":            lat,
            "lon":            lon,
            "date":           date_str,
            "city":           city,
            "state":          state,
            "country":        country,
            "shape":          _reddit_shape(title),
            "summary":        summary,
            "location_label": loc_lbl,
            "url":            url_str,
        }
        processed[pid] = sighting
        sightings.append(sighting)

    _save_reddit_cache(cache)
    print(f"  {len(sightings)} Reddit sightings with confirmed locations "
          f"({len(new_posts)} new processed)")
    return sightings


# ── 4. (MUFON removed — mufonlive.com DNS dead) ───────────────────────────

# ── 5. Google News RSS ────────────────────────────────────────────────────

_GOOGLE_NEWS_QUERIES = [
    "UFO sighting",
    "UAP sighting",
    "unidentified flying object sighting",
    "strange lights in sky",
]

# Full US state name → 2-letter code
_STATE_NAMES = {
    "alabama":"AL","alaska":"AK","arizona":"AZ","arkansas":"AR","california":"CA",
    "colorado":"CO","connecticut":"CT","delaware":"DE","florida":"FL","georgia":"GA",
    "hawaii":"HI","idaho":"ID","illinois":"IL","indiana":"IN","iowa":"IA",
    "kansas":"KS","kentucky":"KY","louisiana":"LA","maine":"ME","maryland":"MD",
    "massachusetts":"MA","michigan":"MI","minnesota":"MN","mississippi":"MS",
    "missouri":"MO","montana":"MT","nebraska":"NE","nevada":"NV",
    "new hampshire":"NH","new jersey":"NJ","new mexico":"NM","new york":"NY",
    "north carolina":"NC","north dakota":"ND","ohio":"OH","oklahoma":"OK",
    "oregon":"OR","pennsylvania":"PA","rhode island":"RI","south carolina":"SC",
    "south dakota":"SD","tennessee":"TN","texas":"TX","utah":"UT","vermont":"VT",
    "virginia":"VA","washington":"WA","west virginia":"WV","wisconsin":"WI",
    "wyoming":"WY","district of columbia":"DC",
}

# Well-known city → state (enough to catch most news headlines)
_CITY_STATE = {
    "seattle":"WA","tacoma":"WA","spokane":"WA","bellevue":"WA","olympia":"WA",
    "portland":"OR","eugene":"OR","salem":"OR","bend":"OR","medford":"OR",
    "phoenix":"AZ","tucson":"AZ","scottsdale":"AZ","tempe":"AZ","mesa":"AZ",
    "los angeles":"CA","san francisco":"CA","san diego":"CA","sacramento":"CA",
    "fresno":"CA","oakland":"CA","san jose":"CA","bakersfield":"CA",
    "las vegas":"NV","reno":"NV","henderson":"NV",
    "denver":"CO","colorado springs":"CO","aurora":"CO","fort collins":"CO",
    "albuquerque":"NM","santa fe":"NM","roswell":"NM",
    "houston":"TX","dallas":"TX","austin":"TX","san antonio":"TX","el paso":"TX",
    "fort worth":"TX","lubbock":"TX","amarillo":"TX",
    "miami":"FL","orlando":"FL","tampa":"FL","jacksonville":"FL","tallahassee":"FL",
    "atlanta":"GA","savannah":"GA","macon":"GA",
    "chicago":"IL","springfield":"IL","rockford":"IL",
    "detroit":"MI","grand rapids":"MI","lansing":"MI",
    "minneapolis":"MN","st. paul":"MN","duluth":"MN",
    "new york":"NY","buffalo":"NY","albany":"NY","rochester":"NY","syracuse":"NY",
    "boston":"MA","worcester":"MA","springfield":"MA",
    "philadelphia":"PA","pittsburgh":"PA","harrisburg":"PA","allentown":"PA",
    "baltimore":"MD","annapolis":"MD",
    "cleveland":"OH","columbus":"OH","cincinnati":"OH","toledo":"OH","akron":"OH",
    "nashville":"TN","memphis":"TN","knoxville":"TN","chattanooga":"TN",
    "charlotte":"NC","raleigh":"NC","greensboro":"NC","durham":"NC",
    "louisville":"KY","lexington":"KY",
    "indianapolis":"IN","fort wayne":"IN",
    "milwaukee":"WI","madison":"WI","green bay":"WI",
    "kansas city":"MO","st. louis":"MO","springfield":"MO",
    "omaha":"NE","lincoln":"NE",
    "salt lake city":"UT","provo":"UT","ogden":"UT",
    "boise":"ID","nampa":"ID","meridian":"ID",
    "anchorage":"AK","fairbanks":"AK","juneau":"AK",
    "honolulu":"HI","hilo":"HI",
    "washington":"DC","washington dc":"DC",
    "new orleans":"LA","baton rouge":"LA","shreveport":"LA",
    "birmingham":"AL","montgomery":"AL","huntsville":"AL","mobile":"AL",
    "jackson":"MS","gulfport":"MS",
    "little rock":"AR","fayetteville":"AR",
    "charleston":"SC","columbia":"SC","greenville":"SC",
    "richmond":"VA","virginia beach":"VA","norfolk":"VA","roanoke":"VA",
    "charleston":"WV","huntington":"WV",
    "fargo":"ND","bismarck":"ND",
    "sioux falls":"SD","rapid city":"SD",
    "cheyenne":"WY","casper":"WY",
    "billings":"MT","missoula":"MT","great falls":"MT",
    "manchester":"NH","concord":"NH",
    "providence":"RI","cranston":"RI",
    "bridgeport":"CT","new haven":"CT","hartford":"CT",
    "burlington":"VT","montpelier":"VT",
    "portland":"ME","bangor":"ME",
    "dover":"DE","wilmington":"DE",
}

# Regex: "City, ST" pattern in text (catches "Phoenix, AZ" style)
_CITY_STATE_RE = re.compile(
    r'\b([A-Z][a-zA-Z\s]{2,20}),\s*([A-Z]{2})\b'
)
# Regex: standalone state abbreviation (word boundary, uppercase)
_STATE_ABBR_RE = re.compile(
    r'\b(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|'
    r'MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|'
    r'VA|WA|WV|WI|WY|DC)\b'
)


def _extract_location(text):
    """Return (city, state_abbr) from a news title/description, or (None, None)."""
    # 1. "City, ST" pattern — most reliable
    for m in _CITY_STATE_RE.finditer(text):
        city_cand = m.group(1).strip()
        state_cand = m.group(2).strip()
        if state_cand in STATE_COORDS:
            return city_cand, state_cand

    low = text.lower()

    # 2. Known city lookup
    for city, state in sorted(_CITY_STATE.items(), key=lambda x: -len(x[0])):
        if city in low:
            return city.title(), state

    # 3. Full state name
    for name, abbr in sorted(_STATE_NAMES.items(), key=lambda x: -len(x[0])):
        if name in low:
            return None, abbr

    # 4. Bare state abbreviation
    m = _STATE_ABBR_RE.search(text)
    if m and m.group(1) in STATE_COORDS:
        return None, m.group(1)

    return None, None


def fetch_local_news(max_results=150):
    """Query Google News RSS for UFO/UAP terms; extract US locations by regex."""
    print("Fetching Google News RSS (UFO/UAP queries)…")
    import random
    seen_urls = set()
    sightings = []

    for query in _GOOGLE_NEWS_QUERIES:
        url = (
            "https://news.google.com/rss/search?"
            + urllib.parse.urlencode({
                "q":    query,
                "hl":   "en-US",
                "gl":   "US",
                "ceid": "US:en",
            })
        )
        xml_text = _fetch(url)
        if not xml_text:
            print(f"  ⚠ RSS fetch failed: {query!r}")
            continue

        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as e:
            print(f"  ⚠ RSS parse error ({query!r}): {e}")
            continue

        items = root.findall(".//item")
        found_this_query = 0
        for item in items:
            title   = (item.findtext("title")       or "").strip()
            desc    = (item.findtext("description") or "").strip()
            link    = (item.findtext("link")        or "").strip()
            pub     = (item.findtext("pubDate")     or "").strip()

            # Skip non-US or meta articles
            combined = f"{title} {desc}"
            if any(skip in combined.lower() for skip in
                   ("uk ", "united kingdom", "canada", "australia", "india",
                    "china", "russia", "brazil", "mexico", "pentagon report",
                    "congress hearing", "declassified")):
                continue

            if link in seen_urls:
                continue
            seen_urls.add(link)

            city, state = _extract_location(combined)
            if not state:
                continue
            coords = STATE_COORDS.get(state)
            if not coords:
                continue

            # Parse pub date
            date_str = ""
            try:
                dt = datetime.strptime(pub, "%a, %d %b %Y %H:%M:%S %Z")
                date_str = dt.strftime("%m/%d/%Y")
            except ValueError:
                date_str = pub[:16] if pub else ""

            lat = round(coords[0] + random.uniform(-1.2, 1.2), 4)
            lon = round(coords[1] + random.uniform(-1.2, 1.2), 4)

            # Strip HTML tags from description
            clean_desc = re.sub(r"<[^>]+>", " ", desc)
            clean_desc = re.sub(r"\s{2,}", " ", clean_desc).strip()[:300]

            # Extract source outlet name from title (Google News appends " - Source")
            source_name = "News"
            if " - " in title:
                source_name = title.rsplit(" - ", 1)[-1].strip()
                title       = title.rsplit(" - ", 1)[0].strip()

            location_label = f"{city}, {state}" if city else state

            sightings.append({
                "source":         "Local News",
                "source_name":    source_name,
                "lat":            lat,
                "lon":            lon,
                "date":           date_str,
                "city":           city or "",
                "state":          state,
                "country":        "US",
                "shape":          "unknown",
                "summary":        (title + (f" — {clean_desc}" if clean_desc else ""))[:300],
                "location_label": location_label,
                "url":            link,
            })
            found_this_query += 1
            if len(sightings) >= max_results:
                break

        print(f"  {found_this_query:3d} results  ← {query!r}")
        time.sleep(0.4)

    # Deduplicate by (lat-rounded, date) in case queries overlap
    unique = []
    seen_sig = set()
    for s in sightings:
        sig = (round(s["lat"], 1), round(s["lon"], 1), s["date"][:7])
        if sig not in seen_sig:
            seen_sig.add(sig)
            unique.append(s)

    print(f"  {len(unique)} unique local news sightings after dedup")
    return unique


# ── USGS Earthquake feed ──────────────────────────────────────────────────

def fetch_usgs_earthquakes():
    """Fetch M2.5+ earthquakes from USGS GeoJSON feed (last ~30 days)."""
    print("Fetching USGS earthquake data…")
    url  = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_month.geojson"
    text = _fetch(url)
    if not text:
        print("  ⚠ USGS fetch failed — skipping")
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        print("  ⚠ USGS JSON parse error — skipping")
        return []

    quakes = []
    for feat in data.get("features", []):
        props  = feat.get("properties", {})
        coords = (feat.get("geometry") or {}).get("coordinates", [])
        if len(coords) < 2:
            continue
        lon, lat = coords[0], coords[1]
        mag = props.get("mag")
        if mag is None:
            continue
        ts       = props.get("time", 0)
        date_str = (datetime.utcfromtimestamp(ts / 1000).strftime("%m/%d/%Y")
                    if ts else "")
        quakes.append({
            "source":  "USGS",
            "name":    props.get("place", "Unknown"),
            "lat":     round(lat, 4),
            "lon":     round(lon, 4),
            "mag":     round(float(mag), 1),
            "date":    date_str,
            "url":     props.get("url", ""),
            "summary": f"M{mag} — {props.get('place', '')}",
        })

    print(f"  {len(quakes)} earthquakes (M2.5+)")
    return quakes


# ── NASA ASRS Pilot Reports ───────────────────────────────────────────────

# Common US airport IATA codes → (lat, lon, city, state)
_AIRPORT_COORDS = {
    "ATL": (33.6407, -84.4277, "Atlanta", "GA"),
    "LAX": (33.9425, -118.4081, "Los Angeles", "CA"),
    "ORD": (41.9742, -87.9073, "Chicago", "IL"),
    "DFW": (32.8998, -97.0403, "Dallas", "TX"),
    "DEN": (39.8561, -104.6737, "Denver", "CO"),
    "JFK": (40.6413, -73.7781, "New York", "NY"),
    "SFO": (37.6213, -122.3790, "San Francisco", "CA"),
    "SEA": (47.4502, -122.3088, "Seattle", "WA"),
    "LAS": (36.0840, -115.1537, "Las Vegas", "NV"),
    "MCO": (28.4312, -81.3081, "Orlando", "FL"),
    "MIA": (25.7959, -80.2870, "Miami", "FL"),
    "PHX": (33.4373, -112.0078, "Phoenix", "AZ"),
    "IAH": (29.9902, -95.3368, "Houston", "TX"),
    "HOU": (29.6454, -95.2789, "Houston", "TX"),
    "BOS": (42.3656, -71.0096, "Boston", "MA"),
    "MSP": (44.8848, -93.2223, "Minneapolis", "MN"),
    "DTW": (42.2162, -83.3554, "Detroit", "MI"),
    "PHL": (39.8744, -75.2424, "Philadelphia", "PA"),
    "CLT": (35.2144, -80.9473, "Charlotte", "NC"),
    "SLC": (40.7899, -111.9791, "Salt Lake City", "UT"),
    "BWI": (39.1754, -76.6683, "Baltimore", "MD"),
    "IAD": (38.9531, -77.4565, "Washington", "DC"),
    "DCA": (38.8512, -77.0402, "Washington", "DC"),
    "MDW": (41.7868, -87.7522, "Chicago", "IL"),
    "SAN": (32.7338, -117.1933, "San Diego", "CA"),
    "TPA": (27.9755, -82.5332, "Tampa", "FL"),
    "PDX": (45.5898, -122.5951, "Portland", "OR"),
    "STL": (38.7487, -90.3700, "St. Louis", "MO"),
    "HNL": (21.3187, -157.9225, "Honolulu", "HI"),
    "DAL": (32.8471, -96.8517, "Dallas", "TX"),
    "OAK": (37.7213, -122.2208, "Oakland", "CA"),
    "MCI": (39.2976, -94.7139, "Kansas City", "MO"),
    "RDU": (35.8776, -78.7875, "Raleigh", "NC"),
    "AUS": (30.1975, -97.6664, "Austin", "TX"),
    "MSY": (29.9934, -90.2580, "New Orleans", "LA"),
    "BNA": (36.1245, -86.6782, "Nashville", "TN"),
    "MEM": (35.0424, -89.9767, "Memphis", "TN"),
    "PIT": (40.4915, -80.2329, "Pittsburgh", "PA"),
    "IND": (39.7173, -86.2944, "Indianapolis", "IN"),
    "CMH": (39.9980, -82.8919, "Columbus", "OH"),
    "BDL": (41.9389, -72.6832, "Hartford", "CT"),
    "BUF": (42.9405, -78.7322, "Buffalo", "NY"),
    "ABQ": (35.0402, -106.6090, "Albuquerque", "NM"),
    "ELP": (31.8072, -106.3779, "El Paso", "TX"),
    "OMA": (41.3032, -95.8941, "Omaha", "NE"),
    "TUL": (36.1984, -95.8881, "Tulsa", "OK"),
    "OKC": (35.3931, -97.6007, "Oklahoma City", "OK"),
    "ALB": (42.7483, -73.8017, "Albany", "NY"),
    "BHM": (33.5629, -86.7535, "Birmingham", "AL"),
    "GRR": (42.8808, -85.5228, "Grand Rapids", "MI"),
    "BOI": (43.5644, -116.2228, "Boise", "ID"),
    "ONT": (34.0560, -117.6012, "Ontario", "CA"),
    "SMF": (38.6954, -121.5908, "Sacramento", "CA"),
    "SJC": (37.3626, -121.9290, "San Jose", "CA"),
    "SNA": (33.6757, -117.8682, "Orange County", "CA"),
    "DAY": (39.9024, -84.2194, "Dayton", "OH"),
    "EWR": (40.6895, -74.1745, "Newark", "NJ"),
    "LGA": (40.7772, -73.8726, "New York", "NY"),
}


# ── Notable hardcoded pilot UAP cases (replaces dead ASRS scraper) ───────────
_PILOT_UAP_CASES = [
    {
        "source":         "Pilot Reports (ASRS)",
        "source_name":    "FAA / United Airlines",
        "lat":            41.9742,
        "lon":            -87.9073,
        "date":           "11/07/2006",
        "city":           "Chicago",
        "state":          "IL",
        "country":        "US",
        "shape":          "disc",
        "summary":        (
            "United Airlines crew and ground personnel at Chicago O'Hare (ORD) reported "
            "a metallic disc-shaped object hovering silently below the 1,900 ft overcast. "
            "The object shot straight up through the clouds at high speed, leaving a circular "
            "hole in the cloud deck. Reported to FAA; FAA initially denied any record of the "
            "event. Chicago Tribune FOIA revealed tower controllers did receive the call."
        ),
        "location_label": "O'Hare International Airport, Chicago IL",
        "url":            "https://en.wikipedia.org/wiki/2006_O%27Hare_International_Airport_UFO_sighting",
    },
    {
        "source":         "Pilot Reports (ASRS)",
        "source_name":    "Multiple pilots / FAA radar",
        "lat":            32.2207,
        "lon":            -98.2025,
        "date":           "01/08/2008",
        "city":           "Stephenville",
        "state":          "TX",
        "country":        "US",
        "shape":          "unknown",
        "summary":        (
            "Over 200 witnesses including multiple pilots reported an enormous silent craft "
            "with bright lights near Stephenville, TX. FAA radar data later obtained via "
            "FOIA by the Mutual UFO Network confirmed an uncorrelated target tracked at "
            "speeds up to 1,900 mph, at times heading toward President Bush's Crawford ranch. "
            "Air Force initially denied aircraft in the area, then reversed the claim."
        ),
        "location_label": "Stephenville, TX",
        "url":            "https://en.wikipedia.org/wiki/Stephenville_UFO_sighting",
    },
    {
        "source":         "Pilot Reports (ASRS)",
        "source_name":    "US Navy F/A-18 pilots — USS Theodore Roosevelt",
        "lat":            36.8,
        "lon":            -74.9,
        "date":           "01/01/2015",
        "city":           "Virginia Beach",
        "state":          "VA",
        "country":        "US",
        "shape":          "sphere",
        "summary":        (
            "US Navy F/A-18 pilots operating off the USS Theodore Roosevelt off the Virginia "
            "coast recorded the now-declassified 'Gimbal' and 'GoFast' UAP videos. Objects "
            "displayed no visible propulsion, no IR exhaust signature, and performed maneuvers "
            "defying known aerodynamics. Encounters occurred repeatedly over several months "
            "2014–2015. Videos officially released by DoD in April 2020."
        ),
        "location_label": "Atlantic Ocean off Virginia Coast",
        "url":            "https://en.wikipedia.org/wiki/Pentagon_UFO_videos",
    },
    {
        "source":         "Pilot Reports (ASRS)",
        "source_name":    "Cmdr David Fravor — USS Nimitz CVN-68",
        "lat":            32.5,
        "lon":            -117.5,
        "date":           "11/14/2004",
        "city":           "San Diego",
        "state":          "CA",
        "country":        "US",
        "shape":          "sphere",
        "summary":        (
            "Commander David Fravor (F/A-18F pilot) encountered a white Tic-Tac-shaped "
            "object off the coast of San Diego during USS Nimitz carrier strike group "
            "operations. The object was first detected on ship radar descending from 80,000 ft "
            "to hover at 20,000 ft. Fravor descended to intercept; the object mirrored his "
            "movements then accelerated away in under a second. A second crew filmed the "
            "'FLIR1' video minutes later. Widely considered the most credible modern UAP case."
        ),
        "location_label": "Pacific Ocean off San Diego, CA (USS Nimitz)",
        "url":            "https://en.wikipedia.org/wiki/USS_Nimitz_UFO_incident",
    },
    {
        "source":         "Pilot Reports (ASRS)",
        "source_name":    "US Navy — USS Omaha CG-69",
        "lat":            32.7,
        "lon":            -117.2,
        "date":           "07/15/2019",
        "city":           "San Diego",
        "state":          "CA",
        "country":        "US",
        "shape":          "sphere",
        "summary":        (
            "US Navy personnel aboard USS Omaha filmed a dark spherical UAP transiting the "
            "ship at low altitude before descending and entering the ocean. No splash or "
            "debris was recovered despite a submarine search. Part of a series of incursions "
            "by unidentified objects near Navy vessels off the California coast in 2019. "
            "Video declassified and confirmed authentic by Pentagon in 2021."
        ),
        "location_label": "Pacific Ocean off San Diego, CA (USS Omaha)",
        "url":            "https://en.wikipedia.org/wiki/Pentagon_UFO_videos",
    },
    {
        "source":         "Pilot Reports (ASRS)",
        "source_name":    "Multiple commercial pilot reports",
        "lat":            7.0,
        "lon":            93.0,
        "date":           "03/08/2014",
        "city":           "Andaman Sea",
        "state":          "",
        "country":        "MY",
        "shape":          "unknown",
        "summary":        (
            "Multiple commercial pilots flying the MH370 corridor reported anomalous objects "
            "along the flight path in the months surrounding the MH370 disappearance. Pilot "
            "reports included unlit objects pacing aircraft and abrupt course changes tracked "
            "on ACARS data. Malaysian authorities acknowledged receiving UAP reports from "
            "crews operating the Kuala Lumpur–Beijing route. Connection to MH370 unconfirmed."
        ),
        "location_label": "MH370 Corridor — Andaman Sea / Indian Ocean",
        "url":            "https://en.wikipedia.org/wiki/Malaysia_Airlines_Flight_370",
    },
    {
        "source":         "Pilot Reports (ASRS)",
        "source_name":    "Peruvian commercial crew",
        "lat":            -12.0,
        "lon":            -77.0,
        "date":           "06/12/2023",
        "city":           "Lima",
        "state":          "",
        "country":        "PE",
        "shape":          "sphere",
        "summary":        (
            "A Peruvian commercial airline crew reported a luminous spherical object "
            "matching speed and altitude during approach into Jorge Chávez International "
            "Airport, Lima. Lima ATC tracked a primary return with no transponder. The "
            "object maintained a stable position relative to the aircraft for approximately "
            "four minutes before accelerating away. Crew filed an official DGAC report; "
            "Peru's Air Force acknowledged receipt of the incident report."
        ),
        "location_label": "Lima, Peru — Jorge Chávez International Airport",
        "url":            "https://x.com/SafeAerospace",
    },
    {
        "source":         "Pilot Reports (ASRS)",
        "source_name":    "American Airlines Flight 2292",
        "lat":            36.7,
        "lon":            -102.8,
        "date":           "02/21/2021",
        "city":           "Clayton",
        "state":          "NM",
        "country":        "US",
        "shape":          "cylinder",
        "summary":        (
            "American Airlines Flight 2292 (Airbus A320, Albuquerque–Cincinnati) crew "
            "reported a long cylindrical object flying above the aircraft at high speed near "
            "Clayton, NM. The pilot radioed Albuquerque Center: 'Do you have any targets up "
            "here? We just had something go right over the top of us.' The object had no "
            "wings, no exhaust, and was traveling in the same direction at high altitude. "
            "FAA and FBI declined to comment."
        ),
        "location_label": "Clayton, NM — AA Flight 2292 corridor",
        "url":            "https://thedebrief.org/american-airlines-pilot-reports-ufo-encounter-over-new-mexico/",
    },
    {
        "source":         "Pilot Reports (ASRS)",
        "source_name":    "Alaska Airlines / Air Canada crews — Pacific corridor",
        "lat":            58.0,
        "lon":            -145.0,
        "date":           "08/01/2017",
        "city":           "Gulf of Alaska",
        "state":          "AK",
        "country":        "US",
        "shape":          "unknown",
        "summary":        (
            "Two commercial airline crews flying the Seattle–Tokyo Pacific corridor "
            "simultaneously reported a fast-moving object with no transponder traveling "
            "against traffic at high altitude over the Gulf of Alaska. FAA Anchorage Center "
            "and the military confirmed the object on radar but could not identify it. "
            "Multiple ASRS safety reports were filed. The FAA report obtained via FOIA "
            "describes a ballistic trajectory inconsistent with any known aircraft."
        ),
        "location_label": "Gulf of Alaska — Pacific Corridor",
        "url":            "https://thedebrief.org/",
    },
    {
        "source":         "Pilot Reports (ASRS)",
        "source_name":    "US Navy F/A-18 pilots — USS Theodore Roosevelt",
        "lat":            24.0,
        "lon":            -81.5,
        "date":           "04/01/2014",
        "city":           "Key West",
        "state":          "FL",
        "country":        "US",
        "shape":          "sphere",
        "summary":        (
            "Prior to the well-known 2015 Atlantic encounters, Navy pilots from Naval Air "
            "Station Key West and operating from USS Theodore Roosevelt's earlier deployment "
            "reported a series of UAP encounters over the Florida Straits. Objects described "
            "as spherical, white, and approximately the size of a commercial drone but "
            "performing impossible maneuvers including stopping instantaneously from high "
            "speed. Confirmed in congressional UAP hearing testimony by Ryan Graves (Lt., USN ret.)."
        ),
        "location_label": "Florida Straits / NAS Key West, FL",
        "url":            "https://en.wikipedia.org/wiki/Pentagon_UFO_videos",
    },
]


def fetch_asrs_reports(max_rows=50):
    """Return hardcoded notable pilot UAP cases (replaces dead ASRS web scraper)."""
    print("Loading pilot UAP cases (hardcoded notable incidents)…")
    results = _PILOT_UAP_CASES[:max_rows]
    print(f"  {len(results)} pilot UAP cases")
    return results


# ── Americans for Safe Aerospace (ASA) Reports ────────────────────────────

# Manually pinned priority sighting — always included
HOUSTON_HOBBY_UAP = {
    "source":         "ASA Reports",
    "source_name":    "Americans for Safe Aerospace",
    "lat":            29.6454,
    "lon":            -95.2789,
    "date":           "04/10/2026",
    "city":           "Houston",
    "state":          "TX",
    "country":        "US",
    "shape":          "sphere",
    "summary":        (
        "Boeing 737 crew departing Houston Hobby Airport encountered a large metallic "
        "spheroid at 14,000 feet. ATC warned pilots of unidentified target that had been "
        "popping up all day on radar. First Officer was a retired F-18 pilot who estimated "
        "the object was roughly 737-sized. Reported by Americans for Safe Aerospace."
    ),
    "location_label": "Houston Hobby Airport, TX",
    "url":            "https://x.com/SafeAerospace",
    "priority":       "high",
}

_NITTER_INSTANCES = [
    "nitter.net",
    "nitter.cz",
    "nitter.privacydev.net",
    "nitter.poast.org",
    "nitter.1d4.us",
]


def _claude_extract_location_asa(text):
    """Like _claude_extract_location but tuned for aviation/ASA tweet text."""
    if not ANTHROPIC_API_KEY:
        return None
    prompt = (
        "Extract the geographic location from this aviation safety / UAP sighting report.\n\n"
        f"Text: {text}\n\n"
        "Return ONLY a JSON object:\n"
        '  "city":       city or airport name string or null\n'
        '  "state":      US state 2-letter code or null\n'
        '  "country":    ISO 2-letter country code or null\n'
        '  "confidence": "high", "medium", "low", or "none"\n\n'
        "Return ONLY the JSON, no markdown."
    )
    payload = json.dumps({
        "model":      "claude-haiku-4-5-20251001",
        "max_tokens": 100,
        "messages":   [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key":         ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type":      "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            resp = json.loads(r.read())
            text_out = resp["content"][0]["text"].strip()
            text_out = re.sub(r"^```(?:json)?\s*", "", text_out)
            text_out = re.sub(r"\s*```$", "", text_out)
            return json.loads(text_out)
    except Exception:
        return None


def fetch_asa_reports(max_rows=50):
    """Fetch Americans for Safe Aerospace (@SafeAerospace) posts via Nitter RSS.
    Always includes the manually pinned Houston Hobby UAP encounter."""
    print("Fetching Americans for Safe Aerospace (ASA) reports…")

    reports = [HOUSTON_HOBBY_UAP.copy()]
    fetched = False

    for instance in _NITTER_INSTANCES:
        url  = f"https://{instance}/SafeAerospace/rss"
        html = _fetch(url, timeout=12)
        if not html:
            continue

        try:
            root  = ET.fromstring(html)
        except ET.ParseError:
            continue

        items = root.findall(".//item")
        if not items:
            continue

        fetched = True
        for item in items:
            if len(reports) >= max_rows:
                break
            title   = (item.findtext("title")       or "").strip()
            desc    = (item.findtext("description") or "").strip()
            link    = (item.findtext("link")        or "").strip()
            pub     = (item.findtext("pubDate")     or "").strip()

            clean = re.sub(r"<[^>]+>", " ", f"{title} {desc}").strip()
            clean = re.sub(r"\s{2,}", " ", clean)[:400]

            # Only include posts that look like sighting reports
            if not any(k in clean.lower() for k in
                       ("uap", "ufo", "pilot", "crew", "aircraft", "radar",
                        "sighting", "object", "orb", "sphere", "encounter")):
                continue

            # Parse date
            date_str = ""
            try:
                dt = datetime.strptime(pub, "%a, %d %b %Y %H:%M:%S %Z")
                date_str = dt.strftime("%m/%d/%Y")
            except ValueError:
                date_str = pub[:16] if pub else ""

            # Extract location with Claude
            loc = _claude_extract_location_asa(clean)
            lat, lon, city, state, country = None, None, "", "", "US"

            # Try airport code lookup first
            arpt_m = re.search(r'\b([A-Z]{3})\b', clean)
            if arpt_m and arpt_m.group(1) in _AIRPORT_COORDS:
                arpt = arpt_m.group(1)
                lat, lon, city, state = _AIRPORT_COORDS[arpt]
            elif loc and loc.get("confidence") in ("high", "medium"):
                state   = loc.get("state") or ""
                country = loc.get("country") or "US"
                city    = loc.get("city") or ""
                if state and state in STATE_COORDS:
                    lat, lon = STATE_COORDS[state]
                elif country in _COUNTRY_COORDS:
                    lat, lon = _COUNTRY_COORDS[country]

            if lat is None:
                continue  # Skip posts with no extractable location

            import random
            lat = round(lat + random.uniform(-0.5, 0.5), 4)
            lon = round(lon + random.uniform(-0.5, 0.5), 4)
            loc_label = f"{city}, {state}".strip(", ") if city else (state or country)

            reports.append({
                "source":         "ASA Reports",
                "source_name":    "Americans for Safe Aerospace",
                "lat":            lat,
                "lon":            lon,
                "date":           date_str,
                "city":           city,
                "state":          state,
                "country":        country,
                "shape":          "unknown",
                "summary":        clean[:300],
                "location_label": loc_label,
                "url":            link or "https://x.com/SafeAerospace",
            })
            time.sleep(0.1)
        break  # Stop after first working Nitter instance

    if not fetched:
        print("  ⚠ All Nitter instances failed — only pinned sightings included")

    print(f"  {len(reports)} ASA reports ({len(reports) - 1} from RSS + 1 pinned)")
    return reports


# ── Export ────────────────────────────────────────────────────────────────

def export():
    sightings    = load_nuforc(max_records=5000)
    nuforc_recent= fetch_nuforc_recent(max_rows=500)
    reddit       = fetch_arctic_shift_reddit(max_per_sub=500)
    abductions   = load_nuforc_abductions()
    local_news   = fetch_local_news()
    earthquakes  = fetch_usgs_earthquakes()
    asrs_reports = fetch_asrs_reports(max_rows=50)
    asa_reports  = fetch_asa_reports(max_rows=50)

    # Separate reddit posts by category
    reddit_ufo       = [s for s in reddit
                        if s.get("subreddit") not in MISSING_SUBS | HUMANOID_SUBS]
    reddit_missing   = [s for s in reddit if s.get("subreddit") in MISSING_SUBS]
    humanoid_enc     = [s for s in reddit if s.get("subreddit") in HUMANOID_SUBS]

    # NUFORC Recent is its own layer (not merged into main sightings)
    all_sightings = sightings + reddit_ufo

    # Add Houston Hobby UAP to local_news layer too (as priority marker)
    local_news_with_pinned = local_news + [{
        **HOUSTON_HOBBY_UAP,
        "source":      "Local News",
        "source_name": "Americans for Safe Aerospace",
    }]

    data = {
        "exported_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "counts": {
            "sightings":              len(all_sightings),
            "nuforc_recent":          len(nuforc_recent),
            "abduction_reports":      len(abductions),
            "local_news":             len(local_news_with_pinned),
            "seismic_activity":       len(earthquakes),
            "humanoid_encounters":    len(humanoid_enc),
            "asrs_reports":           len(asrs_reports),
            "asa_reports":            len(asa_reports),
            "military_bases":         len(MILITARY_BASES),
            "cog_sites":              len(COG_SITES),
            "uso_sites":              len(USO_SITES),
            "missing_411":            len(MISSING_411_SITES),
            "reddit_missing":         len(reddit_missing),
            "missing_scientists":     len(MISSING_SCIENTISTS),
            "parallel_33_sites":      len(PARALLEL_33_SITES),
            "nuclear_sites":          len(NUCLEAR_SITES),
            "cattle_mutilation_sites":len(CATTLE_MUTILATION_SITES),
            "window_areas":           len(WINDOW_AREAS),
            "ley_lines":              len(LEY_LINES),
            "water_anomaly_sites":    len(WATER_ANOMALY_SITES),
        },
        "sightings":               all_sightings,
        "nuforc_recent":           nuforc_recent,
        "abduction_reports":       abductions,
        "local_news":              local_news_with_pinned,
        "seismic_activity":        earthquakes,
        "humanoid_encounters":     humanoid_enc,
        "asrs_reports":            asrs_reports,
        "asa_reports":             asa_reports,
        "reddit_missing":          reddit_missing,
        "military_bases":          MILITARY_BASES,
        "cog_sites":               COG_SITES,
        "uso_sites":               USO_SITES,
        "missing_411":             MISSING_411_SITES,
        "missing_scientists":      MISSING_SCIENTISTS,
        "parallel_33_sites":       PARALLEL_33_SITES,
        "nuclear_sites":           NUCLEAR_SITES,
        "cattle_mutilation_sites": CATTLE_MUTILATION_SITES,
        "window_areas":            WINDOW_AREAS,
        "ley_lines":               LEY_LINES,
        "water_anomaly_sites":     WATER_ANOMALY_SITES,
    }

    output_path = os.path.join(os.path.dirname(__file__), EXPORT_FILE)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    size_mb = os.path.getsize(output_path) / 1_048_576
    total   = sum(data["counts"].values())
    print(f"\nExported {total} total records to {EXPORT_FILE} ({size_mb:.1f} MB)")
    for k, v in data["counts"].items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    export()
    print("\nRunning build_map.py…")
    result = subprocess.run(
        ["python3", "build_map.py"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )
    if result.returncode != 0:
        print("⚠ build_map.py exited with an error")
