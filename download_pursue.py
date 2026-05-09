#!/usr/bin/env python3
"""
download_pursue.py — Download, extract, and geoparse PURSUE UAP files.

Steps:
  1. Download all known PDFs from war.gov/medialink/ufo/release_1/
  2. Discover additional filenames by scraping war.gov/UFO pages 1–17
  3. Extract text from each PDF with pdfplumber → pursue_text/
  4. Analyze extracted text for location mentions → pursue_locations.json
"""

import os, re, json, time, subprocess, urllib.request, urllib.parse, html
from pathlib import Path

BASE_URL   = "https://www.war.gov/medialink/ufo/release_1/"
UFO_PAGE   = "https://www.war.gov/UFO/"
OUT_PDF    = Path(__file__).parent / "pursue_files"
OUT_TEXT   = Path(__file__).parent / "pursue_text"
LOC_FILE   = Path(__file__).parent / "pursue_locations.json"

OUT_PDF.mkdir(exist_ok=True)
OUT_TEXT.mkdir(exist_ok=True)

HEADERS = [
    "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "-H", "Accept-Language: en-US,en;q=0.9",
    "-H", "Referer: https://www.war.gov/UFO/",
]

# ── Known filenames from page 1 ──────────────────────────────
KNOWN_STEMS = [
    "65_hs1-834228961_62-hq-83894_section_10",
    "65_hs1-834228961_62-hq-83894_section_2",
    "65_hs1-834228961_62-hq-83894_section_3",
    "65_hs1-834228961_62-hq-83894_section_4",
    "65_hs1-834228961_62-hq-83894_section_5",
    "65_hs1-834228961_62-hq-83894_section_6",
    "65_hs1-834228961_62-hq-83894_section_7",
    "65_hs1-834228961_62-hq-83894_section_9",
    "65_hs1-834228961_62-hq-83894_serial_130",
    "65_hs1-834228961_62-hq-83894_serial_153",
]

# ── Step 1: Scrape war.gov/UFO pages 1-17 for additional filenames ───────────

def fetch_page(url):
    cmd = ["curl", "-s", "-L", "--max-time", "20"] + HEADERS + [url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def scrape_filenames_from_page(html_text):
    """Extract record-title hrefs or any .pdf links pointing to the medialink pattern."""
    stems = set()

    # Pattern 1: direct .pdf links in the page
    for m in re.finditer(
        r'href=["\']([^"\']*medialink/ufo/[^"\']+\.pdf)["\']', html_text, re.I
    ):
        path = m.group(1)
        stem = Path(urllib.parse.unquote(path)).stem.lower()
        stems.add(stem)

    # Pattern 2: record-title or data-filename attributes
    for m in re.finditer(
        r'(?:record-title|data-filename|data-file|href)[=:]["\']([^"\']+\.pdf)["\']',
        html_text, re.I
    ):
        raw = m.group(1)
        stem = Path(urllib.parse.unquote(raw)).stem.lower()
        if stem:
            stems.add(stem)

    # Pattern 3: any bare filename that looks like a PURSUE file in JS/JSON blobs
    for m in re.finditer(r'"([a-z0-9_\-]{10,}\.pdf)"', html_text, re.I):
        stem = Path(m.group(1)).stem.lower()
        stems.add(stem)

    return stems

discovered = set(KNOWN_STEMS)

print("🔍  Scraping war.gov/UFO pages 1–17 for additional filenames…")
for page_num in range(1, 18):
    page_url = UFO_PAGE if page_num == 1 else f"{UFO_PAGE}?page={page_num}"
    page_html = fetch_page(page_url)
    if not page_html or "Access Denied" in page_html or len(page_html) < 200:
        print(f"   page {page_num:2d}: blocked ({len(page_html)} bytes)")
        continue
    found = scrape_filenames_from_page(page_html)
    new = found - discovered
    print(f"   page {page_num:2d}: {len(page_html):,} bytes  +{len(new)} new filenames")
    # Also save full HTML for inspection on page 1
    if page_num == 1:
        (OUT_PDF.parent / "pursue_page1.html").write_text(page_html[:50000], encoding="utf-8")
        # Try to find any JSON data source URLs too
        api_hits = re.findall(r'(https?://[^\s"\'<>]+(?:json|api)[^\s"\'<>]*)', page_html, re.I)
        if api_hits:
            print(f"   API candidates: {api_hits[:5]}")
    discovered |= found
    time.sleep(0.5)

all_stems = sorted(discovered)
print(f"\n📋  Total filenames to attempt: {len(all_stems)}")

# ── Step 2: Download each PDF ────────────────────────────────────────────────

downloaded = []
failed     = []

for stem in all_stems:
    url     = BASE_URL + stem + ".pdf"
    out_path = OUT_PDF / (stem + ".pdf")

    if out_path.exists() and out_path.stat().st_size > 1000:
        print(f"   ✓ already exists  {stem[:60]}")
        downloaded.append(out_path)
        continue

    cmd = ["curl", "-s", "-L", "--max-time", "30", "--output", str(out_path)] + HEADERS + [url]
    result = subprocess.run(cmd, capture_output=True)

    if out_path.exists():
        sz = out_path.stat().st_size
        # Check if we got a real PDF (starts with %PDF) or an error page
        first = out_path.read_bytes()[:10]
        if first.startswith(b"%PDF") and sz > 1000:
            print(f"   ✅ {sz//1024:4d} KB  {url}")
            downloaded.append(out_path)
        else:
            snippet = first.decode("utf-8", errors="ignore")
            print(f"   ✗  {sz:6d} B  NOT PDF ({snippet!r})  {stem[:50]}")
            out_path.unlink(missing_ok=True)
            failed.append(url)
    else:
        print(f"   ✗  no output  {url}")
        failed.append(url)

    time.sleep(0.3)

print(f"\n📥  Downloaded: {len(downloaded)}   Failed: {len(failed)}")

# ── Step 3: Extract text with pdfplumber ────────────────────────────────────

try:
    import pdfplumber
except ImportError:
    print("❌  pdfplumber not installed. Run: pip3 install pdfplumber")
    raise SystemExit(1)

extracted = {}

for pdf_path in downloaded:
    txt_path = OUT_TEXT / (pdf_path.stem + ".txt")
    if txt_path.exists():
        extracted[pdf_path.stem] = txt_path.read_text(encoding="utf-8", errors="ignore")
        print(f"   ↩ already extracted  {pdf_path.stem[:55]}")
        continue

    try:
        pages_text = []
        with pdfplumber.open(pdf_path) as pdf:
            for pg in pdf.pages:
                t = pg.extract_text()
                if t:
                    pages_text.append(t)
        full = "\n\n".join(pages_text)
        txt_path.write_text(full, encoding="utf-8")
        extracted[pdf_path.stem] = full
        words = len(full.split())
        print(f"   📄 {words:5d} words  {pdf_path.stem[:55]}")
    except Exception as e:
        print(f"   ⚠  extract failed for {pdf_path.name}: {e}")

print(f"\n✏️   Extracted text from {len(extracted)} PDFs")

# ── Step 4: Geoparse — find location mentions ────────────────────────────────

# US states
US_STATES = [
    "Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut",
    "Delaware","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa",
    "Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan",
    "Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada",
    "New Hampshire","New Jersey","New Mexico","New York","North Carolina",
    "North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island",
    "South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont",
    "Virginia","Washington","West Virginia","Wisconsin","Wyoming",
    # abbrevs
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
    "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
    "VA","WA","WV","WI","WY",
]

# Countries / regions likely to appear
COUNTRIES = [
    "Afghanistan","Africa","Alaska","Belgium","Canada","China","Cuba",
    "Egypt","England","France","Germany","Greece","Guam","Hawaii",
    "Hungary","India","Iran","Iraq","Israel","Italy","Japan","Jordan",
    "Kazakhstan","Korea","Kuwait","Lebanon","Libya","Mediterranean",
    "Mexico","Morocco","Netherlands","North Korea","Norway","Pakistan",
    "Panama","Peru","Philippines","Poland","Portugal","Puerto Rico",
    "Romania","Russia","Saudi Arabia","South Korea","Spain","Syria",
    "Tajikistan","Turkey","Turkmenistan","Ukraine","United Kingdom",
    "Vietnam","Yemen","Yugoslavia",
]

# Military / geographic keywords that signal a location context
LOCATION_KEYWORDS = [
    "sighted over","observed over","reported over","detected over",
    "spotted over","seen over","flying over","appeared over",
    "incident in","sighting in","occurred in","reported in",
    "location:","coordinates","latitude","longitude","lat ","lon ",
    "miles from","miles north","miles south","miles east","miles west",
    "air force base","naval air station","army base","radar station",
    "airspace","corridor","vicinity of","region of",
]

locations_by_file = {}

for stem, text in extracted.items():
    hits = []
    lines = text.split("\n")

    for i, line in enumerate(lines):
        line_l = line.lower()

        # Check for state mentions
        for st in US_STATES:
            if re.search(r'\b' + re.escape(st) + r'\b', line, re.I):
                ctx = " ".join(lines[max(0,i-1):i+2]).strip()[:200]
                hits.append({"type": "US_STATE", "match": st, "context": ctx, "line": i})
                break

        # Check for country mentions
        for country in COUNTRIES:
            if re.search(r'\b' + re.escape(country) + r'\b', line, re.I):
                ctx = " ".join(lines[max(0,i-1):i+2]).strip()[:200]
                hits.append({"type": "COUNTRY", "match": country, "context": ctx, "line": i})
                break

        # Check for explicit lat/lon
        coord_m = re.search(
            r'(\d{1,3})[°\s](\d{1,2})[\'"\s]?[NS]?\s*[,/]?\s*(\d{1,3})[°\s](\d{1,2})[\'"\s]?[EW]?',
            line
        )
        if coord_m:
            hits.append({"type": "COORDS", "match": coord_m.group(0), "context": line.strip()[:200], "line": i})

        # Check for location keywords
        for kw in LOCATION_KEYWORDS:
            if kw in line_l:
                ctx = " ".join(lines[max(0,i-1):i+2]).strip()[:200]
                hits.append({"type": "KEYWORD", "match": kw, "context": ctx, "line": i})
                break

    if hits:
        locations_by_file[stem] = hits
        print(f"   📍 {len(hits):3d} location hits  {stem[:55]}")
    else:
        print(f"       {0:3d} location hits  {stem[:55]}")

LOC_FILE.write_text(json.dumps(locations_by_file, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\n✅  Location data saved → {LOC_FILE}")
print(f"    Files with location hits: {len(locations_by_file)} / {len(extracted)}")

total_hits = sum(len(v) for v in locations_by_file.values())
print(f"    Total location mentions: {total_hits}")

# Print summary of top location matches
from collections import Counter
all_matches = [h["match"] for hits in locations_by_file.values() for h in hits]
top = Counter(all_matches).most_common(20)
if top:
    print("\n📊  Top location mentions across all files:")
    for loc, count in top:
        print(f"    {count:4d}×  {loc}")
