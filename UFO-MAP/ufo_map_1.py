#!/usr/bin/env python3
"""
UFO Sighting Aggregator & Map Generator
Pulls from NUFORC + Reddit r/ufos and plots on an interactive map
"""

import json
import time
import csv
import re
import os
import urllib.request
import urllib.parse
from datetime import datetime

# ============================================================
# CONFIGURATION — paste your Anthropic API key here
# ============================================================
ANTHROPIC_API_KEY = "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"

# ============================================================
# DATA CONSTANTS (imported from constants.py)
# ============================================================
from constants import (
    NUFORC_CSV, OUTPUT_MAP, EXPORT_FILE,
    NUFORC_FIELDS, ABDUCTION_KEYWORDS,
    MILITARY_BASES, COG_SITES, USO_SITES, MISSING_411_SITES,
)

def fetch_nuforc_data(max_records=5000):
    print("📡 Fetching NUFORC sighting database...")
    sightings = []
    try:
        with open(NUFORC_CSV, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f, fieldnames=NUFORC_FIELDS)
            for i, row in enumerate(reader):
                if i >= max_records:
                    break
                try:
                    lat = float(row.get("latitude", 0) or 0)
                    lon = float(row.get("longitude", 0) or 0)
                    if lat == 0 and lon == 0:
                        continue
                    city  = row.get("city", "")
                    state = row.get("state", "")
                    sightings.append({
                        "source":         "NUFORC",
                        "lat":            lat,
                        "lon":            lon,
                        "date":           row.get("datetime", "Unknown"),
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
        print(f"   ✅ Loaded {len(sightings)} NUFORC sightings")
    except Exception as e:
        print(f"   ⚠️  Could not fetch NUFORC data: {e}")
    return sightings


def fetch_nuforc_abductions():
    """Filter the local NUFORC CSV for abduction-related reports."""
    print("👤 Mining NUFORC database for abduction reports...")
    sightings = []
    try:
        with open(NUFORC_CSV, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f, fieldnames=NUFORC_FIELDS)
            for row in reader:
                text = (row.get("comments") or "").lower()
                if not any(k in text for k in ABDUCTION_KEYWORDS):
                    continue
                try:
                    lat = float(row.get("latitude", 0) or 0)
                    lon = float(row.get("longitude", 0) or 0)
                    if lat == 0 and lon == 0:
                        continue
                    city = row.get("city", "")
                    state = row.get("state", "")
                    sightings.append({
                        "source": "NUFORC Abduction",
                        "lat": lat,
                        "lon": lon,
                        "date": row.get("datetime", "Unknown"),
                        "city": city,
                        "state": state,
                        "country": row.get("country", ""),
                        "shape": row.get("shape", "unknown"),
                        "duration": row.get("duration_seconds", ""),
                        "summary": row.get("comments", "")[:300],
                        "url": "",
                        "location_label": f"{city}, {state}".strip(", ")
                    })
                except (ValueError, KeyError):
                    continue
        print(f"   ✅ Found {len(sightings)} NUFORC abduction reports")
    except Exception as e:
        print(f"   ⚠️  Could not mine NUFORC abductions: {e}")
    return sightings


# ============================================================
# STEP 2: Fetch Reddit posts (no API key needed)
# ============================================================
def fetch_reddit_posts(subreddits=None, label="Reddit posts"):
    if subreddits is None:
        subreddits = REDDIT_SUBREDDITS
    print(f"🔴 Fetching {label}...")
    posts = []
    headers = {"User-Agent": "ufo-mapper/1.0 (research project)"}

    for sub in subreddits:
        url = f"https://www.reddit.com/r/{sub}/new.json?limit={REDDIT_POST_LIMIT}"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))

            for child in data.get("data", {}).get("children", []):
                p = child.get("data", {})
                title = p.get("title", "")
                body = p.get("selftext", "")
                text = f"{title} {body}".strip()
                if len(text) < 30:
                    continue
                posts.append({
                    "subreddit": sub,
                    "title": title,
                    "text": text[:600],
                    "url": f"https://reddit.com{p.get('permalink', '')}",
                    "date": datetime.utcfromtimestamp(p.get("created_utc", 0)).strftime("%Y-%m-%d")
                })

            print(f"   ✅ r/{sub}: {len(data.get('data',{}).get('children',[]))} posts")
            time.sleep(1)  # be polite to Reddit
        except Exception as e:
            print(f"   ⚠️  Could not fetch r/{sub}: {e}")

    print(f"   Total {label}: {len(posts)}")
    return posts


# ============================================================
# STEP 3: Reddit location cache + Claude API extraction
# ============================================================
CACHE_FILE = "reddit_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"   📂 Loaded {len(data)} cached results from {CACHE_FILE}")
            return data
        except Exception:
            pass
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

# Loaded once at module level, shared by all processing functions
_cache = load_cache()

def _cache_key(post):
    """Stable key: Reddit post URL (unique per post)."""
    return post.get("url", "")

def extract_location_with_claude(post_text):
    if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "YOUR_API_KEY_HERE":
        return None

    prompt = f"""Extract the geographic location from this UFO sighting post. 
Return ONLY a JSON object with these fields (no other text):
{{"city": "city name or empty string", "state": "state/province or empty string", "country": "country or empty string", "lat": latitude as number or null, "lon": longitude as number or null, "confidence": "high/medium/low"}}

If no clear location is mentioned, return: {{"city": "", "state": "", "country": "", "lat": null, "lon": null, "confidence": "low"}}

Post text: {post_text[:400]}"""

    try:
        payload = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 150,
            "messages": [{"role": "user", "content": prompt}]
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01"
            }
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
        
        text = result["content"][0]["text"].strip()
        # Strip markdown code fences if present
        text = re.sub(r"```json|```", "", text).strip()
        return json.loads(text)
    except Exception:
        return None


def process_reddit_posts(posts):
    print("🤖 Extracting locations from Reddit posts using Claude...")
    sightings = []
    cache_hits = 0

    if ANTHROPIC_API_KEY == "YOUR_API_KEY_HERE":
        print("   ⚠️  No API key set — skipping Reddit location extraction")
        print("   (Set ANTHROPIC_API_KEY at the top of this script)")
        return sightings

    for i, post in enumerate(posts):
        key = _cache_key(post)
        if key and key in _cache:
            location = _cache[key]
            cache_hits += 1
        else:
            print(f"   Processing post {i+1}/{len(posts)}: {post['title'][:50]}...")
            location = extract_location_with_claude(post["text"])
            if key:
                _cache[key] = location
                if len(_cache) % 50 == 0:
                    save_cache(_cache)
            time.sleep(0.3)

        if location and location.get("lat") and location.get("lon") and location.get("confidence") != "low":
            sightings.append({
                "source": f"Reddit r/{post['subreddit']}",
                "lat": location["lat"],
                "lon": location["lon"],
                "date": post["date"],
                "city": location.get("city", ""),
                "state": location.get("state", ""),
                "country": location.get("country", ""),
                "shape": "unknown",
                "duration": "",
                "summary": post["title"],
                "url": post["url"],
                "location_label": f"{location.get('city', '')}, {location.get('state', '')}".strip(", ")
            })

    save_cache(_cache)
    print(f"   ✅ Extracted {len(sightings)} located Reddit sightings ({cache_hits} from cache, {len(posts)-cache_hits} new API calls)")
    return sightings


# State/territory centroids for fallback when only a state name is known
STATE_CENTROIDS = {
    "alabama": (32.806671, -86.791130), "alaska": (61.370716, -152.404419),
    "arizona": (33.729759, -111.431221), "arkansas": (34.969704, -92.373123),
    "california": (36.116203, -119.681564), "colorado": (39.059811, -105.311104),
    "connecticut": (41.597782, -72.755371), "delaware": (39.318523, -75.507141),
    "florida": (27.766279, -81.686783), "georgia": (33.040619, -83.643074),
    "hawaii": (21.094318, -157.498337), "idaho": (44.240459, -114.478828),
    "illinois": (40.349457, -88.986137), "indiana": (39.849426, -86.258278),
    "iowa": (42.011539, -93.210526), "kansas": (38.526600, -96.726486),
    "kentucky": (37.668140, -84.670067), "louisiana": (31.169960, -91.867805),
    "maine": (44.693947, -69.381927), "maryland": (39.063946, -76.802101),
    "massachusetts": (42.230171, -71.530106), "michigan": (43.326618, -84.536095),
    "minnesota": (45.694454, -93.900192), "mississippi": (32.741646, -89.678696),
    "missouri": (38.456085, -92.288368), "montana": (46.921925, -110.454353),
    "nebraska": (41.125370, -98.268082), "nevada": (38.313515, -117.055374),
    "new hampshire": (43.452492, -71.563896), "new jersey": (40.298904, -74.521011),
    "new mexico": (34.840515, -106.248482), "new york": (42.165726, -74.948051),
    "north carolina": (35.630066, -79.806419), "north dakota": (47.528912, -99.784012),
    "ohio": (40.388783, -82.764915), "oklahoma": (35.565342, -96.928917),
    "oregon": (44.572021, -122.070938), "pennsylvania": (40.590752, -77.209755),
    "rhode island": (41.680893, -71.511780), "south carolina": (33.856892, -80.945007),
    "south dakota": (44.299782, -99.438828), "tennessee": (35.747845, -86.692345),
    "texas": (31.054487, -97.563461), "utah": (40.150032, -111.862434),
    "vermont": (44.045876, -72.710686), "virginia": (37.769337, -78.169968),
    "washington": (47.400902, -121.490494), "west virginia": (38.491226, -80.954453),
    "wisconsin": (44.268543, -89.616508), "wyoming": (42.755966, -107.302490),
    "district of columbia": (38.897438, -77.026817), "dc": (38.897438, -77.026817),
    # Canadian provinces
    "ontario": (51.253775, -85.232212), "british columbia": (53.726669, -127.647621),
    "quebec": (52.939916, -73.549136), "alberta": (53.933271, -116.576503),
    "nova scotia": (44.681988, -63.744311), "manitoba": (53.760860, -98.813874),
    # UK/other common
    "england": (52.355518, -1.174320), "scotland": (56.490671, -4.202646),
    "wales": (52.130661, -3.783712), "ireland": (53.176440, -8.468800),
    "australia": (-25.274398, 133.775136), "canada": (56.130366, -106.346771),
    "uk": (55.378051, -3.435973), "united kingdom": (55.378051, -3.435973),
}

def extract_abduction_location_with_claude(post_text):
    """Looser location extraction — accepts any geographic mention, returns state centroid if no city."""
    if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "YOUR_API_KEY_HERE":
        return None

    prompt = f"""Extract the best available geographic location from this post. Accept ANY location mention — a specific city, a state, a country, a general region, or even a vague reference like "the midwest" or "rural Tennessee".

Return ONLY a JSON object (no other text):
{{"city": "city or empty string", "state": "US state name or province or empty string", "country": "country or empty string", "lat": best latitude as number or null, "lon": best longitude as number or null}}

Rules:
- If only a state is mentioned (e.g. "Texas", "Ohio"), return the geographic center of that state as lat/lon.
- If only a country is mentioned, return the country center.
- If a general region is mentioned (e.g. "the Pacific Northwest", "rural Appalachia"), return a representative lat/lon for that region.
- Only return null lat/lon if the post has absolutely no geographic information whatsoever.

Post text: {post_text[:500]}"""

    try:
        payload = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 150,
            "messages": [{"role": "user", "content": prompt}]
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01"
            }
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))

        text = result["content"][0]["text"].strip()
        text = re.sub(r"```json|```", "", text).strip()
        location = json.loads(text)

        # Fallback: if Claude returned no lat/lon but gave us a state, use state centroid
        if (not location.get("lat") or not location.get("lon")):
            state_key = (location.get("state") or location.get("country") or "").lower().strip()
            if state_key in STATE_CENTROIDS:
                location["lat"], location["lon"] = STATE_CENTROIDS[state_key]

        return location
    except Exception:
        return None


def process_abduction_posts(posts):
    print("🤖 Extracting locations from abduction posts using Claude...")
    sightings = []
    cache_hits = 0

    if ANTHROPIC_API_KEY == "YOUR_API_KEY_HERE":
        print("   ⚠️  No API key set — skipping abduction location extraction")
        return sightings

    for i, post in enumerate(posts):
        key = _cache_key(post)
        # Use a prefix so abduction prompts don't collide with UFO prompts for the same URL
        abduction_key = f"abd::{key}" if key else ""
        if abduction_key and abduction_key in _cache:
            location = _cache[abduction_key]
            cache_hits += 1
        else:
            print(f"   Processing abduction post {i+1}/{len(posts)}: {post['title'][:50]}...")
            location = extract_abduction_location_with_claude(post["text"])
            if abduction_key:
                _cache[abduction_key] = location
                if len(_cache) % 50 == 0:
                    save_cache(_cache)
            time.sleep(0.3)

        if location and location.get("lat") and location.get("lon"):
            city = location.get("city", "")
            state = location.get("state", "")
            country = location.get("country", "")
            label = ", ".join(filter(None, [city, state, country])) or "Unknown Location"
            sightings.append({
                "source": f"Abduction r/{post['subreddit']}",
                "lat": location["lat"],
                "lon": location["lon"],
                "date": post["date"],
                "city": city,
                "state": state,
                "country": country,
                "shape": "unknown",
                "duration": "",
                "summary": post["title"],
                "url": post["url"],
                "location_label": label
            })

    save_cache(_cache)
    print(f"   ✅ Extracted {len(sightings)} located abduction reports ({cache_hits} from cache, {len(posts)-cache_hits} new API calls)")
    return sightings


# ============================================================
# STEP 4: Export data as JSON
# ============================================================
def export_data(sightings, bases, cog_sites, uso_sites, abduction_sightings, path="ufo_data_export.json"):
    print(f"💾 Exporting data to {path}...")
    export = {
        "exported_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "counts": {
            "sightings": len(sightings),
            "abduction_reports": len(abduction_sightings),
            "military_bases": len(bases),
            "cog_sites": len(cog_sites),
            "uso_sites": len(uso_sites),
        },
        "sightings": sightings,
        "abduction_reports": abduction_sightings,
        "military_bases": bases,
        "cog_sites": cog_sites,
        "uso_sites": uso_sites,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2, ensure_ascii=False)
    size_mb = os.path.getsize(path) / 1_048_576
    print(f"   ✅ Exported {sum(export['counts'].values())} total records ({size_mb:.1f} MB)")


# ============================================================
# STEP 5: Build the interactive HTML map
# ============================================================
def build_map(sightings, bases=None, cog_sites=None, uso_sites=None, abduction_sightings=None):
    if bases is None:
        bases = []
    if cog_sites is None:
        cog_sites = []
    if uso_sites is None:
        uso_sites = []
    if abduction_sightings is None:
        abduction_sightings = []
    print(f"🗺️  Building interactive map with {len(sightings)} sightings + {len(bases)} military bases + {len(cog_sites)} COG sites + {len(uso_sites)} USO sites + {len(abduction_sightings)} abduction reports...")

    nuforc_count = sum(1 for s in sightings if s["source"] == "NUFORC")
    reddit_count = len(sightings) - nuforc_count

    bases_json = json.dumps(bases)
    cog_json = json.dumps(cog_sites)
    uso_json = json.dumps(uso_sites)
    abduction_json = json.dumps([{
        "lat": s["lat"],
        "lon": s["lon"],
        "source": s["source"],
        "date": s["date"],
        "location": s.get("location_label", "Unknown"),
        "summary": s.get("summary", "")[:200].replace('"', '&quot;').replace("'", "&#39;"),
        "url": s.get("url", "")
    } for s in abduction_sightings])

    # Build marker data as JSON
    markers_json = json.dumps([{
        "lat": s["lat"],
        "lon": s["lon"],
        "source": s["source"],
        "date": s["date"],
        "location": s.get("location_label", "Unknown"),
        "shape": s.get("shape", "unknown"),
        "summary": s.get("summary", "")[:200].replace('"', '&quot;').replace("'", "&#39;"),
        "url": s.get("url", "")
    } for s in sightings])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>UAP Sighting Map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css"/>
<script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #040d14; color: #a0e8c8; font-family: 'Rajdhani', sans-serif; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }}

  #header {{
    background: linear-gradient(180deg, #040d14 0%, rgba(4,13,20,0.95) 100%);
    border-bottom: 1px solid #0f4; 
    padding: 10px 20px;
    display: flex; align-items: center; justify-content: space-between;
    z-index: 1000;
    flex-shrink: 0;
  }}
  #header h1 {{ font-size: 1.4rem; letter-spacing: 0.25em; color: #0f4; text-transform: uppercase; font-family: 'Share Tech Mono', monospace; }}
  #header h1 span {{ color: #fff; }}
  #stats {{ font-size: 0.8rem; color: #5a9; letter-spacing: 0.1em; text-align: right; font-family: 'Share Tech Mono', monospace; }}
  #stats b {{ color: #0f4; }}

  #controls {{
    background: rgba(4,13,20,0.97);
    border-bottom: 1px solid #093;
    padding: 8px 20px;
    display: flex; gap: 16px; align-items: center; flex-wrap: wrap;
    flex-shrink: 0;
    z-index: 999;
  }}
  .filter-group {{ display: flex; align-items: center; gap: 8px; }}
  .filter-group label {{ font-size: 0.75rem; letter-spacing: 0.12em; color: #5a9; text-transform: uppercase; }}
  select, input[type=text] {{
    background: #071a10; border: 1px solid #0a3; color: #a0e8c8;
    padding: 4px 10px; font-family: 'Share Tech Mono', monospace; font-size: 0.8rem;
    border-radius: 2px; outline: none; cursor: pointer;
  }}
  select:focus, input[type=text]:focus {{ border-color: #0f4; }}
  #result-count {{ font-size: 0.75rem; color: #5a9; font-family: 'Share Tech Mono', monospace; margin-left: auto; }}

  #map {{ flex: 1; }}

  .leaflet-popup-content-wrapper {{
    background: #040d14; border: 1px solid #0a3; border-radius: 4px; color: #a0e8c8;
    font-family: 'Rajdhani', sans-serif; box-shadow: 0 0 20px rgba(0,255,68,0.15);
  }}
  .leaflet-popup-tip {{ background: #040d14; }}
  .leaflet-popup-content {{ margin: 14px 18px; }}
  .popup-source {{ font-size: 0.65rem; letter-spacing: 0.15em; text-transform: uppercase; color: #0a3; font-family: 'Share Tech Mono', monospace; margin-bottom: 4px; }}
  .popup-title {{ font-size: 1rem; font-weight: 700; color: #0f4; margin-bottom: 6px; line-height: 1.3; }}
  .popup-meta {{ font-size: 0.78rem; color: #5a9; margin-bottom: 8px; }}
  .popup-summary {{ font-size: 0.82rem; color: #8cc; line-height: 1.5; margin-bottom: 8px; }}
  .popup-link {{ font-size: 0.75rem; color: #0a3; text-decoration: none; letter-spacing: 0.05em; }}
  .popup-link:hover {{ color: #0f4; }}

  #legend {{
    position: absolute; bottom: 30px; right: 10px; z-index: 1000;
    background: rgba(4,13,20,0.92); border: 1px solid #093;
    padding: 10px 14px; font-size: 0.75rem; font-family: 'Share Tech Mono', monospace;
    border-radius: 2px;
  }}
  .legend-item {{ display: flex; align-items: center; gap: 8px; margin-bottom: 5px; color: #5a9; }}
  .legend-dot {{ width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }}
  .marker-cluster {{ background: transparent !important; box-shadow: none !important; }}
  .marker-cluster div {{ background: transparent !important; }}
  .marker-cluster-small, .marker-cluster-medium, .marker-cluster-large {{
    background: transparent !important;
  }}
  .leaflet-control-layers {{
    background: rgba(4,13,20,0.95) !important; border: 1px solid #093 !important;
    border-radius: 2px !important; color: #a0e8c8 !important;
    font-family: 'Share Tech Mono', monospace !important; font-size: 0.75rem !important;
  }}
  .leaflet-control-layers-toggle {{ background-color: #040d14 !important; }}
  .leaflet-control-layers label {{ color: #a0e8c8 !important; }}
  .leaflet-control-layers-separator {{ border-top-color: #093 !important; }}
</style>
</head>
<body>

<div id="header">
  <h1>UAP <span>SIGHTING</span> MAP</h1>
  <div id="stats">
    TOTAL <b id="total-count">{len(sightings)}</b> &nbsp;|&nbsp;
    NUFORC <b>{nuforc_count}</b> &nbsp;|&nbsp;
    REDDIT <b>{reddit_count}</b>
  </div>
</div>

<div id="controls">
  <div class="filter-group">
    <label>Source</label>
    <select id="filter-source">
      <option value="all">All Sources</option>
      <option value="NUFORC">NUFORC</option>
      <option value="Reddit">Reddit</option>
    </select>
  </div>
  <div class="filter-group">
    <label>Shape</label>
    <select id="filter-shape">
      <option value="all">All Shapes</option>
    </select>
  </div>
  <div class="filter-group">
    <label>Search</label>
    <input type="text" id="filter-search" placeholder="city, state, keyword..." style="width:180px;">
  </div>
  <span id="result-count"></span>
</div>

<div id="map"></div>

<div id="legend">
  <div class="legend-item"><span style="font-size:13px;">🛸💡🔵🔺</span> &nbsp;NUFORC/Reddit</div>
  <div class="legend-item"><div style="width:12px;height:12px;flex-shrink:0;display:flex;align-items:center;justify-content:center;color:#f44;font-size:14px;line-height:1;">&#9670;</div> Military Base</div>
  <div class="legend-item"><div style="width:12px;height:12px;flex-shrink:0;display:flex;align-items:center;justify-content:center;color:#ffe033;font-size:14px;line-height:1;">&#9733;</div> COG Site</div>
  <div class="legend-item"><span style="font-size:13px;">🌊</span> &nbsp;USO Site</div>
  <div class="legend-item"><span style="font-size:13px;">👤</span> &nbsp;NUFORC Abduction</div>
  <div class="legend-item"><span style="font-size:13px;">👽</span> &nbsp;Reddit Abduction</div>
</div>

<script>
const ALL_SIGHTINGS = {markers_json};
const MILITARY_BASES = {bases_json};
const COG_SITES = {cog_json};
const USO_SITES = {uso_json};
const ABDUCTION_REPORTS = {abduction_json};

const map = L.map('map', {{
  center: [39.5, -98.35],
  zoom: 4,
  zoomControl: true,
  attributionControl: false
}});

L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  attribution: '&copy; OpenStreetMap &copy; CARTO',
  maxZoom: 18
}}).addTo(map);

// Populate shape filter
const shapes = [...new Set(ALL_SIGHTINGS.map(s => s.shape).filter(Boolean))].sort();
const shapeSelect = document.getElementById('filter-shape');
shapes.forEach(shape => {{
  if (shape && shape !== 'unknown') {{
    const opt = document.createElement('option');
    opt.value = shape; opt.textContent = shape;
    shapeSelect.appendChild(opt);
  }}
}});

const SHAPE_EMOJI = {{
  'light':      '💡',
  'circle':     '🔵',
  'triangle':   '🔺',
  'disk':       '🛸',
  'saucer':     '🛸',
  'fireball':   '🔥',
  'cylinder':   '🛢️',
  'sphere':     '⚪',
  'chevron':    '✈️',
  'diamond':    '💎',
  'cross':      '✝️',
  'rectangle':  '⬜',
  'formation':  '🔷',
  'other':      '❓',
  'unknown':    '❓',
  'changing':   '🌀',
  'cone':       '🔺',
  'cigar':      '🛢️',
  'egg':        '⚪',
  'teardrop':   '💧',
  'flash':      '⚡',
  'oval':       '🔵',
}};

function makeIcon(source, shape) {{
  const emoji = SHAPE_EMOJI[(shape || '').toLowerCase()] || '❓';
  const isReddit = source !== 'NUFORC';
  return L.divIcon({{
    className: '',
    html: `<div style="font-size:16px;line-height:1;filter:drop-shadow(0 0 3px ${{isReddit ? '#ff8800' : '#00ff44'}});">${{emoji}}</div>`,
    iconSize: [18, 18], iconAnchor: [9, 9]
  }});
}}

const BRANCH_COLORS = {{
  'Army':       '#4caf50',
  'Navy':       '#2196f3',
  'Marines':    '#f44336',
  'Air Force':  '#03a9f4',
  'Space Force':'#9c27b0',
  'Special':    '#ff5722',
}};

function makeMilIcon(branch) {{
  const color = BRANCH_COLORS[branch] || '#ff4444';
  return L.divIcon({{
    className: '',
    html: `<div style="width:0;height:0;
             border-left:7px solid transparent;
             border-right:7px solid transparent;
             border-bottom:13px solid ${{color}};
             filter:drop-shadow(0 0 4px ${{color}});
             position:relative;top:-6px;">
           </div>`,
    iconSize: [14, 13], iconAnchor: [7, 13]
  }});
}}

// ── Cluster factory ─────────────────────────────────────────
function makeClusterGroup(color) {{
  return L.markerClusterGroup({{
    chunkedLoading: true,
    removeOutsideVisibleBounds: true,
    maxClusterRadius: 50,
    iconCreateFunction: function(cluster) {{
      const n = cluster.getChildCount();
      const size = n < 10 ? 28 : n < 100 ? 34 : 42;
      const fs   = n < 10 ? 12 : n < 100 ? 11 : 10;
      return L.divIcon({{
        className: '',
        html: `<div style="
          width:${{size}}px;height:${{size}}px;border-radius:50%;
          background:${{color}}18;border:2px solid ${{color}};
          display:flex;align-items:center;justify-content:center;
          color:${{color}};font-family:'Share Tech Mono',monospace;
          font-size:${{fs}}px;font-weight:bold;
          box-shadow:0 0 10px ${{color}}55,inset 0 0 6px ${{color}}22;">
            ${{n}}
          </div>`,
        iconSize: [size, size], iconAnchor: [size/2, size/2]
      }});
    }}
  }});
}}

// ── Sightings layer (viewport lazy-loading) ─────────────────
const markerLayer = makeClusterGroup('#00ff44');
markerLayer.addTo(map);

// Track which sighting indices have been added so panning only adds new ones
let addedIndices = new Set();
let activeFilters = {{ src: 'all', shape: 'all', search: '' }};

function matchesSighting(s) {{
  if (activeFilters.src !== 'all' && !s.source.includes(activeFilters.src)) return false;
  if (activeFilters.shape !== 'all' && s.shape !== activeFilters.shape) return false;
  if (activeFilters.search) {{
    const hay = `${{s.location}} ${{s.summary}} ${{s.shape}}`.toLowerCase();
    if (!hay.includes(activeFilters.search)) return false;
  }}
  return true;
}}

function loadVisibleSightings() {{
  const bounds = map.getBounds().pad(0.4);
  const batch = [];
  ALL_SIGHTINGS.forEach((s, i) => {{
    if (addedIndices.has(i)) return;
    if (!bounds.contains([s.lat, s.lon])) return;
    if (!matchesSighting(s)) return;
    addedIndices.add(i);
    const marker = L.marker([s.lat, s.lon], {{icon: makeIcon(s.source, s.shape)}});
    const linkHtml = s.url ? `<a href="${{s.url}}" target="_blank" class="popup-link">→ View post</a>` : '';
    marker.bindPopup(`
      <div class="popup-source">${{s.source}}</div>
      <div class="popup-title">${{s.location || 'Unknown Location'}}</div>
      <div class="popup-meta">📅 ${{s.date}} &nbsp;·&nbsp; 🔷 ${{s.shape || 'unknown'}}</div>
      <div class="popup-summary">${{s.summary}}</div>
      ${{linkHtml}}
    `, {{maxWidth: 280}});
    batch.push(marker);
  }});
  if (batch.length) markerLayer.addLayers(batch);
  document.getElementById('result-count').textContent =
    `Showing ${{markerLayer.getLayers().length.toLocaleString()}} / ${{ALL_SIGHTINGS.filter(matchesSighting).length.toLocaleString()}} sightings`;
}}

function renderMarkers() {{
  markerLayer.clearLayers();
  addedIndices.clear();
  activeFilters = {{
    src:   document.getElementById('filter-source').value,
    shape: document.getElementById('filter-shape').value,
    search: document.getElementById('filter-search').value.toLowerCase().trim()
  }};
  loadVisibleSightings();
}}

map.on('moveend zoomend', loadVisibleSightings);

// ── Military bases layer ────────────────────────────────────
const militaryLayer = makeClusterGroup('#ff4444');
MILITARY_BASES.forEach(b => {{
  const color = BRANCH_COLORS[b.branch] || '#ff4444';
  const marker = L.marker([b.lat, b.lon], {{icon: makeMilIcon(b.branch)}});
  marker.bindPopup(`
    <div class="popup-source" style="color:${{color}}">&#9650; ${{b.branch}}</div>
    <div class="popup-title" style="color:${{color}}">${{b.name}}</div>
    <div class="popup-meta">${{b.state}}</div>
  `, {{maxWidth: 220}});
  militaryLayer.addLayer(marker);
}});

// ── COG sites layer ─────────────────────────────────────────
function makeCogIcon() {{
  return L.divIcon({{
    className: '',
    html: `<div style="
      width:14px;height:14px;background:#ffe033;
      clip-path:polygon(50% 0%,61% 35%,98% 35%,68% 57%,79% 91%,50% 70%,21% 91%,32% 57%,2% 35%,39% 35%);
      filter:drop-shadow(0 0 5px #ffe033);">
    </div>`,
    iconSize: [14, 14], iconAnchor: [7, 7]
  }});
}}

const cogLayer = makeClusterGroup('#ffe033');
COG_SITES.forEach(site => {{
  const marker = L.marker([site.lat, site.lon], {{icon: makeCogIcon()}});
  marker.bindPopup(`
    <div class="popup-source" style="color:#ffe033;">&#9733; CONTINUITY OF GOVERNMENT</div>
    <div class="popup-title" style="color:#ffe033;">${{site.name}}</div>
    <div class="popup-meta" style="color:#cc9;">${{site.location}}</div>
    <div class="popup-summary">${{site.description}}</div>
  `, {{maxWidth: 320}});
  cogLayer.addLayer(marker);
}});

// ── USO sites layer ─────────────────────────────────────────
const usoLayer = makeClusterGroup('#00bfff');
USO_SITES.forEach(site => {{
  const marker = L.marker([site.lat, site.lon], {{icon: L.divIcon({{
    className: '',
    html: '<div style="font-size:20px;line-height:1;filter:drop-shadow(0 0 4px #00bfff);">🌊</div>',
    iconSize: [22, 22], iconAnchor: [11, 11]
  }})}});
  marker.bindPopup(`
    <div class="popup-source" style="color:#00bfff;">🌊 UNIDENTIFIED SUBMERGED OBJECT</div>
    <div class="popup-title" style="color:#00bfff;">${{site.name}}</div>
    <div class="popup-meta" style="color:#7ce;">${{site.location}}</div>
    <div class="popup-summary">${{site.description}}</div>
  `, {{maxWidth: 320}});
  usoLayer.addLayer(marker);
}});

// ── Abduction reports layer ─────────────────────────────────
const abductionLayer = makeClusterGroup('#cc44ff');
ABDUCTION_REPORTS.forEach(s => {{
  const isNuforc = s.source === 'NUFORC Abduction';
  const emoji = isNuforc ? '👤' : '👽';
  const color = isNuforc ? '#ff44aa' : '#cc44ff';
  const marker = L.marker([s.lat, s.lon], {{icon: L.divIcon({{
    className: '',
    html: `<div style="font-size:16px;line-height:1;filter:drop-shadow(0 0 4px ${{color}});">${{emoji}}</div>`,
    iconSize: [18, 18], iconAnchor: [9, 9]
  }})}});
  const linkHtml = s.url ? `<a href="${{s.url}}" target="_blank" class="popup-link">→ View post</a>` : '';
  marker.bindPopup(`
    <div class="popup-source" style="color:${{color}};">${{emoji}} ${{s.source}}</div>
    <div class="popup-title" style="color:${{color}}">${{s.location || 'Unknown Location'}}</div>
    <div class="popup-meta">📅 ${{s.date}}</div>
    <div class="popup-summary">${{s.summary}}</div>
    ${{linkHtml}}
  `, {{maxWidth: 300}});
  abductionLayer.addLayer(marker);
}});

// ── Layer control ───────────────────────────────────────────
L.control.layers(null, {{
  'UFO Sightings':     markerLayer,
  'Military Bases':    militaryLayer,
  'COG Sites':         cogLayer,
  'USO Sites':         usoLayer,
  'Abduction Reports': abductionLayer,
}}, {{collapsed: false, position: 'topright'}}).addTo(map);

document.getElementById('filter-source').addEventListener('change', renderMarkers);
document.getElementById('filter-shape').addEventListener('change', renderMarkers);
document.getElementById('filter-search').addEventListener('input', renderMarkers);

renderMarkers();
</script>
</body>
</html>"""

    with open(OUTPUT_MAP, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"   ✅ Map saved as: {OUTPUT_MAP}")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("\n🛸 UFO Sighting Aggregator — starting up...\n")

    all_sightings = []

    # NUFORC (no API key needed)
    nuforc = fetch_nuforc_data(max_records=5000)
    all_sightings.extend(nuforc)

    # Reddit UFO posts
    reddit_posts = fetch_reddit_posts(label="Reddit UFO posts")
    reddit_sightings = process_reddit_posts(reddit_posts)
    all_sightings.extend(reddit_sightings)

    # Abduction subreddits
    abduction_posts = fetch_reddit_posts(subreddits=ABDUCTION_SUBREDDITS, label="abduction posts")
    abduction_sightings = process_abduction_posts(abduction_posts)

    # NUFORC abduction reports (mined from local CSV)
    nuforc_abductions = fetch_nuforc_abductions()
    abduction_sightings.extend(nuforc_abductions)

    if not all_sightings:
        print("❌ No sightings loaded. Check your internet connection.")
    else:
        export_data(all_sightings, MILITARY_BASES, COG_SITES, USO_SITES, abduction_sightings)
        build_map(all_sightings, bases=MILITARY_BASES, cog_sites=COG_SITES,
                  uso_sites=USO_SITES, abduction_sightings=abduction_sightings)
        print(f"\n✅ Done! Open '{OUTPUT_MAP}' in your browser to view the map.")
        print(f"   Total sightings plotted: {len(all_sightings)}")
        print(f"   Abduction reports plotted: {len(abduction_sightings)} ({len(nuforc_abductions)} NUFORC + {len(abduction_sightings)-len(nuforc_abductions)} Reddit)")
        print("\n   Tip: double-click ufo_map.html to open it in your browser!\n")
