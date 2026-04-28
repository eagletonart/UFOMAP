#!/usr/bin/env python3
"""
fetch_data.py — collect and export all UFO map data.

Sources:
  1. Local NUFORC CSV (bulk historical sightings + abduction filter)
  2. NUFORC recent — tries subndx/?id=event, falls back to CSV sorted by date
  3. Reddit r/ufos and r/UFOs — JSON API with browser UA
  4. MUFON — scraped from mufonlive.com (may be unavailable)
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
    "ufos", "UFOs", "UAP", "aliens", "HighStrangeness",
    "Paranormal", "UFOsighting", "Missing411", "Glitch_in_the_Matrix", "NightVision",
]

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
    """Try NUFORC web endpoints; fall back to local CSV sorted newest-first."""
    print("Fetching NUFORC recent reports…")
    for url in [
        "https://nuforc.org/subndx/?id=event",
        "https://nuforc.org/webreports/ndxevent.html",
    ]:
        html = _fetch(url)
        if html:
            sightings = _parse_nuforc_html(html, max_rows)
            if sightings:
                print(f"  {len(sightings)} recent NUFORC reports scraped ({url})")
                return sightings
            print(f"  ⚠ Page loaded but 0 rows parsed ({url})")

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
    """Fetch Reddit sightings from Arctic Shift; use Claude to extract locations.
    Caches results in reddit_cache.json to avoid re-processing on repeat runs."""
    print("Fetching Reddit sightings via Arctic Shift API…")
    if not ANTHROPIC_API_KEY:
        print("  ⚠ ANTHROPIC_API_KEY not set — skipping (Claude required for location extraction)")
        return []

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

    # ── 4. Process new posts with Claude ──────────────────────────────────
    for i, (pid, p) in enumerate(new_posts):
        if i > 0 and i % 25 == 0:
            print(f"    … {i}/{len(new_posts)} processed so far ({len(sightings)} located)")
            _save_reddit_cache(cache)   # checkpoint

        title       = (p.get("title")    or "").strip()
        body_excerpt= (p.get("selftext") or "").strip()[:400]
        subreddit   = p.get("subreddit", "")
        created_utc = p.get("created_utc", 0)

        loc = _claude_extract_location(title, body_excerpt)
        time.sleep(0.08)   # stay well under rate limit

        if not loc or loc.get("confidence") not in ("high", "medium"):
            processed[pid] = None
            continue

        state   = (loc.get("state")   or "").upper().strip()
        city    = (loc.get("city")    or "").strip()
        country = (loc.get("country") or "US").upper().strip()

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


# ── 4. MUFON scraper ──────────────────────────────────────────────────────

class _MufonTableParser(HTMLParser):
    """Extract rows from mufonlive.com/cases/ table or list."""
    def __init__(self):
        super().__init__()
        self.rows, self._row, self._cell, self._in_td = [], [], "", False
        self._in_link = False

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        if tag == "tr":
            self._row = []
        if tag in ("td", "th"):
            self._in_td = True
            self._cell = ""
        if tag == "a":
            self._in_link = True
            self._link_href = attrs_d.get("href", "")

    def handle_endtag(self, tag):
        if tag in ("td", "th"):
            self._row.append(self._cell.strip())
            self._in_td = False
        if tag == "a":
            self._in_link = False
        if tag == "tr" and len(self._row) >= 4:
            self.rows.append((self._row[:], getattr(self, "_link_href", "")))

    def handle_data(self, data):
        if self._in_td:
            self._cell += data


def fetch_mufon_cases(max_rows=300):
    """Scrape recent MUFON case list; returns list of sighting dicts."""
    print("Fetching MUFON recent cases (mufonlive.com/cases/)...")
    html = _fetch("https://mufonlive.com/cases/")
    if not html:
        print("  ⚠ MUFON fetch failed — skipping")
        return []

    parser = _MufonTableParser()
    parser.feed(html)

    sightings = []
    import random

    # Detect column layout from first header row
    # Typical MUFON columns: Case#, Date, City, State, Country, Shape, Summary
    # We try a few known layouts
    for row_data, href in parser.rows:
        try:
            # Skip rows that look like headers
            if any(h in (row_data[0] or "").lower() for h in ("case", "date", "#")):
                continue

            # Try to find a date (MM/DD/YYYY or YYYY-MM-DD patterns)
            date_val = ""
            city_val = ""
            state_val = ""
            shape_val = "unknown"
            summary_val = ""

            for cell in row_data:
                cell = cell.strip()
                # Date patterns
                if re.match(r"\d{1,2}/\d{1,2}/\d{4}", cell) or re.match(r"\d{4}-\d{2}-\d{2}", cell):
                    if not date_val:
                        date_val = cell
                # Shape keywords
                low = cell.lower()
                if low in {"triangle", "disk", "disc", "orb", "sphere", "light", "fireball",
                           "cigar", "cylinder", "oval", "chevron", "diamond", "circle",
                           "formation", "other", "unknown", "changing", "boomerang"}:
                    shape_val = low
                # US state abbreviation (2 caps)
                if re.fullmatch(r"[A-Z]{2}", cell) and cell in STATE_COORDS:
                    state_val = cell
                # Longer text → probable city or summary
                if 3 < len(cell) < 40 and not re.search(r"\d", cell) and not state_val == cell:
                    if not city_val and cell.replace(" ", "").isalpha():
                        city_val = cell
                elif len(cell) > 40:
                    summary_val = cell[:200]

            if not state_val:
                # Try regex over joined row text
                m = _STATE_RE.search(" ".join(row_data))
                if m:
                    state_val = m.group(1)

            if not state_val:
                continue

            coords = STATE_COORDS.get(state_val)
            if not coords:
                continue

            lat = round(coords[0] + random.uniform(-1.5, 1.5), 4)
            lon = round(coords[1] + random.uniform(-1.5, 1.5), 4)

            url = href if href and href.startswith("http") else (
                "https://mufonlive.com" + href if href else "")

            sightings.append({
                "source":         "MUFON",
                "lat":            lat,
                "lon":            lon,
                "date":           date_val,
                "city":           city_val,
                "state":          state_val,
                "country":        "US",
                "shape":          shape_val,
                "summary":        summary_val,
                "location_label": f"{city_val}, {state_val}".strip(", "),
                "url":            url,
            })
            if len(sightings) >= max_rows:
                break
        except Exception:
            continue

    print(f"  {len(sightings)} MUFON cases extracted")
    return sightings


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


# ── Export ────────────────────────────────────────────────────────────────

def export():
    sightings  = load_nuforc(max_records=5000)
    recent     = fetch_nuforc_recent(max_rows=300)
    reddit     = fetch_arctic_shift_reddit(max_per_sub=500)
    abductions = load_nuforc_abductions()
    mufon      = fetch_mufon_cases(max_rows=300)
    local_news = fetch_local_news()

    # Merge fresh sources into sightings
    all_sightings = sightings + recent + reddit

    data = {
        "exported_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "counts": {
            "sightings":              len(all_sightings),
            "abduction_reports":      len(abductions),
            "mufon_reports":          len(mufon),
            "local_news":             len(local_news),
            "military_bases":         len(MILITARY_BASES),
            "cog_sites":              len(COG_SITES),
            "uso_sites":              len(USO_SITES),
            "missing_411":            len(MISSING_411_SITES),
            "missing_scientists":     len(MISSING_SCIENTISTS),
            "parallel_33_sites":      len(PARALLEL_33_SITES),
            "nuclear_sites":          len(NUCLEAR_SITES),
            "cattle_mutilation_sites":len(CATTLE_MUTILATION_SITES),
            "window_areas":           len(WINDOW_AREAS),
            "ley_lines":              len(LEY_LINES),
            "water_anomaly_sites":    len(WATER_ANOMALY_SITES),
        },
        "sightings":               all_sightings,
        "abduction_reports":       abductions,
        "mufon_reports":           mufon,
        "local_news":              local_news,
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
