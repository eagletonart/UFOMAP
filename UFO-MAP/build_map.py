#!/usr/bin/env python3
"""
Build ufo_map.html from cached ufo_data_export.json.
Run:  python3 build_map.py
No network requests, no API calls — instant rebuild from local data.
"""

import json
import os
import sys
from datetime import datetime

# Importing constants triggers the .env loader as a side effect, so
# MAPBOX_TOKEN from a repo-root .env file is available below.
import constants  # noqa: F401

EXPORT_FILE = "ufo_data_export.json"
OUTPUT_MAP  = "index.html"

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

def load_export(path=EXPORT_FILE):
    if not os.path.exists(path):
        print(f"❌  {path} not found. Run export_data.py first to generate it.")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    counts = data.get("counts", {})
    print(f"📂  Loaded {path}  (exported {data.get('exported_at','?')})")
    for k, v in counts.items():
        print(f"    {k}: {v}")
    return data


# ---------------------------------------------------------------------------
# Build the HTML map
# ---------------------------------------------------------------------------

def build_map(sightings, abduction_sightings, military_bases, cog_sites, uso_sites,
              missing_411=None, missing_scientists=None,
              parallel_33_sites=None, nuclear_sites=None,
              cattle_mutilation_sites=None, window_areas=None, ley_lines=None,
              water_anomaly_sites=None, mufon_reports=None, local_news=None):
    if missing_411 is None:
        missing_411 = []
    if missing_scientists is None:
        missing_scientists = []
    if parallel_33_sites is None:
        parallel_33_sites = []
    if nuclear_sites is None:
        nuclear_sites = []
    if cattle_mutilation_sites is None:
        cattle_mutilation_sites = []
    if window_areas is None:
        window_areas = []
    if ley_lines is None:
        ley_lines = []
    if water_anomaly_sites is None:
        water_anomaly_sites = []
    if mufon_reports is None:
        mufon_reports = []
    if local_news is None:
        local_news = []
    nuforc_count      = sum(1 for s in sightings if s["source"] == "NUFORC")
    reddit_count      = len(sightings) - nuforc_count
    abduction_count   = len(abduction_sightings)
    mufon_count       = len(mufon_reports)
    local_news_count  = len(local_news)

    print(f"\n🗺️   Building map …")
    print(f"     {len(sightings)} sightings  |  {abduction_count} abductions  "
          f"|  {len(military_bases)} bases  |  {len(cog_sites)} COG  "
          f"|  {len(uso_sites)} USO  |  {len(missing_411)} Missing 411  "
          f"|  {len(missing_scientists)} Missing Scientists")

    markers_json = json.dumps([{
        "lat":      s["lat"],
        "lon":      s["lon"],
        "source":   s["source"],
        "date":     s["date"],
        "location": s.get("location_label") or s.get("location") or "Unknown",
        "shape":    s.get("shape", "unknown"),
        "duration": s.get("duration", ""),
        "summary":  (s.get("summary") or "")[:200].replace('"', '&quot;').replace("'", "&#39;"),
        "url":      s.get("url", ""),
    } for s in sightings])

    abduction_json = json.dumps([{
        "lat":      s["lat"],
        "lon":      s["lon"],
        "source":   s["source"],
        "date":     s["date"],
        "location": s.get("location_label") or s.get("location") or "Unknown",
        "summary":  (s.get("summary") or "")[:200].replace('"', '&quot;').replace("'", "&#39;"),
        "url":      s.get("url", ""),
    } for s in abduction_sightings])

    bases_json      = json.dumps(military_bases)
    cog_json        = json.dumps(cog_sites)
    uso_json        = json.dumps(uso_sites)
    missing_json    = json.dumps(missing_411)
    scientists_json = json.dumps(missing_scientists)
    p33_json        = json.dumps(parallel_33_sites)
    nuclear_json    = json.dumps(nuclear_sites)
    cattle_json     = json.dumps(cattle_mutilation_sites)
    windows_json    = json.dumps(window_areas)
    leylines_json   = json.dumps(ley_lines)
    water_json      = json.dumps(water_anomaly_sites)
    mufon_json      = json.dumps(mufon_reports)
    local_news_json = json.dumps(local_news)

    # Read Mapbox token: prefer the MAPBOX_TOKEN env var (set via .env at the
    # repo root, loaded automatically by constants.py), fall back to the
    # legacy mapbox_token.txt file for backwards compatibility with existing
    # local installs.
    mapbox_token = os.environ.get('MAPBOX_TOKEN', '').strip()
    if not mapbox_token:
        _tok_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mapbox_token.txt')
        try:
            with open(_tok_path) as _tf:
                mapbox_token = _tf.read().strip()
        except FileNotFoundError:
            pass
    if mapbox_token:
        print(f"   Mapbox token: {mapbox_token[:16]}…")
    else:
        print("   ⚠  No Mapbox token (set MAPBOX_TOKEN in .env) — globe will be disabled")

    built_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>UAP Sighting Map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link  rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css"/>
<link  rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css"/>
<script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
<script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
<link href="https://api.mapbox.com/mapbox-gl-js/v3.3.0/mapbox-gl.css" rel="stylesheet"/>
<script src="https://api.mapbox.com/mapbox-gl-js/v3.3.0/mapbox-gl.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap" rel="stylesheet">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#040d14; color:#a0e8c8; font-family:'Rajdhani',sans-serif;
       height:100vh; display:flex; flex-direction:column; overflow:hidden; }}

/* ── header ─────────────────────────────────────────────── */
#header {{
  background:linear-gradient(180deg,#040d14 0%,rgba(4,13,20,.95) 100%);
  border-bottom:1px solid #0f4; padding:10px 20px;
  display:flex; align-items:center; justify-content:space-between;
  z-index:1000; flex-shrink:0;
}}
#header h1 {{ font-size:1.4rem; letter-spacing:.25em; color:#0f4;
              text-transform:uppercase; font-family:'Share Tech Mono',monospace; }}
#header h1 span {{ color:#fff; }}
#stats {{ font-size:.78rem; color:#5a9; letter-spacing:.1em;
          text-align:right; font-family:'Share Tech Mono',monospace; line-height:1.6; }}
#stats b {{ color:#0f4; }}

/* ── controls ────────────────────────────────────────────── */
#controls {{
  background:rgba(4,13,20,.97); border-bottom:1px solid #093;
  padding:8px 20px; display:flex; gap:16px; align-items:center;
  flex-wrap:wrap; flex-shrink:0; z-index:999;
}}
.filter-group {{ display:flex; align-items:center; gap:8px; }}
.filter-group label {{ font-size:.75rem; letter-spacing:.12em; color:#5a9; text-transform:uppercase; }}
select, input[type=text] {{
  background:#071a10; border:1px solid #0a3; color:#a0e8c8;
  padding:4px 10px; font-family:'Share Tech Mono',monospace; font-size:.8rem;
  border-radius:2px; outline:none; cursor:pointer;
}}
select:focus, input[type=text]:focus {{ border-color:#0f4; }}
#result-count {{ font-size:.75rem; color:#5a9; font-family:'Share Tech Mono',monospace; margin-left:auto; }}

/* ── map ─────────────────────────────────────────────────── */
#map {{ flex:1; }}

/* ── popups ──────────────────────────────────────────────── */
/* ── tap-to-read mobile hint ─────────────────────────────── */
#tap-hint {{
  display:none; position:absolute; bottom:70px; left:50%;
  transform:translateX(-50%); z-index:900; pointer-events:none;
  background:rgba(4,13,20,.88); border:1px solid #093;
  color:#5a9; font-family:'Share Tech Mono',monospace;
  font-size:.65rem; letter-spacing:.12em; padding:5px 12px;
  border-radius:2px; white-space:nowrap; opacity:.85;
  animation: fadeout 3.5s ease 3s forwards;
}}
@keyframes fadeout {{ to {{ opacity:0; }} }}
@media (max-width:768px) {{ #tap-hint {{ display:block; }} }}

.leaflet-popup-content-wrapper {{
  background:#040d14; border:1px solid #0a3; border-radius:4px; color:#a0e8c8;
  font-family:'Rajdhani',sans-serif; box-shadow:0 0 20px rgba(0,255,68,.15);
}}
.leaflet-popup-tip {{ background:#040d14; }}
.leaflet-popup-content {{ margin:14px 18px; }}
.popup-source {{ font-size:.65rem; letter-spacing:.15em; text-transform:uppercase;
                 color:#0a3; font-family:'Share Tech Mono',monospace; margin-bottom:4px; }}
.popup-title  {{ font-size:1rem; font-weight:700; color:#0f4; margin-bottom:6px; line-height:1.3; }}
.popup-meta   {{ font-size:.78rem; color:#5a9; margin-bottom:8px; }}
.popup-summary {{ font-size:.82rem; color:#8cc; line-height:1.5; margin-bottom:8px; }}
.popup-link   {{ font-size:.75rem; color:#0a3; text-decoration:none; letter-spacing:.05em; }}
.popup-link:hover {{ color:#0f4; }}

/* ── custom layer panel ──────────────────────────────────── */
#layer-panel {{
  position:absolute; top:12px; right:12px; z-index:1000;
  width:210px; background:rgba(4,13,20,.97); border:1px solid #093;
  border-radius:3px; font-family:'Share Tech Mono',monospace;
  font-size:.72rem; display:flex; flex-direction:column;
  max-height:calc(100vh - 140px);
}}
#lp-header {{
  display:flex; align-items:center; justify-content:space-between;
  padding:7px 10px; border-bottom:1px solid #093; flex-shrink:0;
  cursor:default;
}}
#lp-title {{ color:#0f4; letter-spacing:.18em; text-transform:uppercase; font-size:.7rem; }}
#lp-collapse {{
  background:none; border:none; color:#5a9; cursor:pointer;
  font-size:11px; padding:0 2px; line-height:1;
}}
#lp-collapse:hover {{ color:#a0e8c8; }}
#lp-body {{ overflow-y:auto; flex:1; }}
/* accordion group */
.lp-group {{ border-bottom:1px solid #052; }}
.lp-group-hdr {{
  display:flex; align-items:center; gap:6px; padding:6px 10px;
  cursor:pointer; color:#5a9; user-select:none;
  transition:color .15s, background .15s;
}}
.lp-group-hdr:hover {{ background:rgba(0,255,68,.06); color:#a0e8c8; }}
.lp-group-icon {{ font-size:12px; }}
.lp-group-name {{ flex:1; letter-spacing:.1em; font-size:.68rem; text-transform:uppercase; }}
.lp-chevron {{ font-size:10px; transition:transform .2s; color:#3a7; }}
.lp-group.open .lp-chevron {{ transform:rotate(180deg); }}
.lp-group-items {{ display:none; padding:3px 0 5px 0; background:rgba(0,255,68,.02); }}
.lp-group.open .lp-group-items {{ display:block; }}
/* individual layer row */
.lp-item {{
  display:flex; align-items:center; gap:7px;
  padding:4px 10px 4px 22px; cursor:pointer; color:#5a9;
  transition:color .12s;
}}
.lp-item:hover {{ color:#a0e8c8; }}
.lp-item input[type=checkbox] {{ accent-color:#0f4; cursor:pointer; flex-shrink:0; }}
.lp-dot {{
  width:8px; height:8px; border-radius:50%; flex-shrink:0;
}}
.lp-name {{ letter-spacing:.07em; }}
/* show button (when panel is collapsed) */
#lp-show {{
  position:absolute; top:12px; right:12px; z-index:1000; display:none;
  background:rgba(4,13,20,.95); border:1px solid #093; color:#5a9;
  font-family:'Share Tech Mono',monospace; font-size:.7rem;
  letter-spacing:.12em; padding:6px 10px; cursor:pointer;
  text-transform:uppercase; border-radius:3px;
}}
#lp-show:hover {{ color:#a0e8c8; border-color:#0a3; }}

/* ── cluster bubbles — override Leaflet defaults ─────────── */
.marker-cluster, .marker-cluster div,
.marker-cluster-small, .marker-cluster-medium, .marker-cluster-large {{
  background:transparent !important; box-shadow:none !important;
}}

/* ── legend (dynamic — shows only active layers) ─────────── */
#legend {{
  position:absolute; bottom:30px; left:10px; z-index:1000;
  background:rgba(4,13,20,.92); border:1px solid #093;
  padding:8px 12px; font-size:.72rem;
  font-family:'Share Tech Mono',monospace; border-radius:2px;
  display:none;
}}
.legend-item {{ display:flex; align-items:center; gap:7px; margin-bottom:4px; color:#5a9; }}
.legend-item:last-child {{ margin-bottom:0; }}

/* ── ley line labels ─────────────────────────────────────── */
.ley-label {{
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
  pointer-events: none;
}}
.ley-label::before {{ display: none !important; }}

/* ── mode toggle button ──────────────────────────────────── */
#mode-toggle {{
  background: rgba(0,255,68,.08);
  border: 1px solid #0f4; color: #0f4;
  font-family: 'Share Tech Mono', monospace;
  font-size: .78rem; letter-spacing: .15em;
  padding: 6px 16px; cursor: pointer;
  text-transform: uppercase; white-space: nowrap;
  transition: background .2s, color .2s; flex-shrink:0;
  border-radius:2px;
}}
#mode-toggle:hover  {{ background: rgba(0,255,68,.22); color:#fff; }}
#mode-toggle.active {{ background: rgba(0,255,68,.3);  color:#fff; box-shadow:0 0 10px #0f430; }}

/* ── controls hamburger (mobile only) ───────────────────── */
#controls-toggle {{
  display:none;
  background: rgba(0,153,51,.1); border:1px solid #093; color:#5a9;
  font-family:'Share Tech Mono',monospace; font-size:.75rem;
  letter-spacing:.1em; padding:6px 14px; cursor:pointer;
  text-transform:uppercase; white-space:nowrap; border-radius:2px;
}}
#controls-toggle:hover {{ background:rgba(0,153,51,.25); color:#a0e8c8; }}

/* ── view wrapper: globe + map overlap ──────────────────── */
#view-wrapper {{ flex:1; position:relative; min-height:0; overflow:hidden; }}
#map {{
  position:absolute; top:0; left:0; width:100%; height:100%;
  transition: opacity .3s ease;
}}
/* Globe container — hidden until toggled; shown before Mapbox init
   so the canvas receives real pixel dimensions on first render. */
#globe-container {{
  position:absolute; top:0; left:0; width:100%; height:100%;
  display:none;
}}

/* ── Mapbox GL popup theming ─────────────────────────────── */
.mb-popup .mapboxgl-popup-content {{
  background:#040d14; border:1px solid #0a3; border-radius:4px;
  color:#a0e8c8; font-family:'Rajdhani',sans-serif;
  padding:10px 14px; box-shadow:0 0 20px rgba(0,255,68,.2);
  font-size:.88rem; line-height:1.5;
}}
.mb-popup .mapboxgl-popup-tip {{ border-top-color:#0a3 !important; border-bottom-color:#0a3 !important; }}
.mb-popup .mapboxgl-popup-close-button {{ color:#5a9; font-size:16px; }}
.mb-popup .mapboxgl-popup-close-button:hover {{ color:#0f4; background:none; }}

/* ── mobile responsive ───────────────────────────────────── */
@media (max-width:768px) {{
  #header {{
    padding:8px 12px; gap:8px; flex-wrap:wrap;
  }}
  #header h1 {{ font-size:1rem; letter-spacing:.1em; }}
  #stats {{
    font-size:.62rem; line-height:1.5; order:4;
    flex-basis:100%; border-top:1px solid #093; padding-top:6px; margin-top:2px;
  }}
  #controls {{ display:none; }}
  #controls.open {{ display:flex; flex-direction:column; align-items:flex-start; gap:10px; padding:10px 14px; }}
  #controls-toggle {{ display:inline-flex !important; }}
  #mode-toggle {{ font-size:.72rem; padding:6px 12px; }}
  #result-count {{ display:none; }}
  #legend {{ display:none; }}
  #built-at {{ display:none; }}
  /* Layer panel: compact on small screens */
  #layer-panel {{ width:185px; font-size:.68rem; }}
  /* Popups: larger text + wider box for mobile reading */
  .leaflet-popup-content-wrapper {{ min-width:270px !important; max-width:88vw !important; }}
  .leaflet-popup-content {{ margin:16px 18px !important; font-size:16px !important; }}
  .popup-source  {{ font-size:12px !important; }}
  .popup-title   {{ font-size:18px !important; }}
  .popup-meta    {{ font-size:16px !important; }}
  .popup-summary {{ font-size:16px !important; line-height:1.6 !important; }}
  .popup-link    {{ font-size:16px !important; }}
  /* Mapbox globe popup on mobile */
  .mb-popup .mapboxgl-popup-content {{
    min-width:240px !important; font-size:.95rem !important;
    padding:14px 16px !important;
  }}
}}
@media (min-width:769px) {{
  #controls-toggle {{ display:none !important; }}
}}

/* ── built-at watermark ──────────────────────────────────── */
#built-at {{
  position:absolute; bottom:8px; left:10px; z-index:1000;
  font-size:.6rem; color:#1a4; font-family:'Share Tech Mono',monospace; opacity:.6;
}}

/* ── about panel ─────────────────────────────────────────── */
#about-btn {{
  background: rgba(0,255,68,.06); border:1px solid #093; color:#5a9;
  font-family:'Share Tech Mono',monospace; font-size:.72rem;
  letter-spacing:.1em; padding:5px 12px; cursor:pointer;
  text-transform:uppercase; white-space:nowrap; border-radius:2px;
  transition: background .2s, color .2s;
}}
#about-btn:hover {{ background:rgba(0,255,68,.16); color:#a0e8c8; }}
#about-overlay {{
  display:none; position:fixed; inset:0; z-index:9000;
  background:rgba(0,0,0,.72); align-items:center; justify-content:center;
}}
#about-overlay.open {{ display:flex; }}
#about-modal {{
  background:#060f18; border:1px solid #0a3;
  border-radius:4px; max-width:640px; width:92%; max-height:85vh;
  overflow-y:auto; padding:28px 32px;
  font-family:'Rajdhani',sans-serif; color:#a0e8c8;
  box-shadow:0 0 40px rgba(0,255,68,.2);
}}
#about-modal h2 {{
  color:#0f4; font-family:'Share Tech Mono',monospace;
  font-size:1rem; letter-spacing:.22em; text-transform:uppercase;
  margin-bottom:20px; border-bottom:1px solid #093; padding-bottom:10px;
}}
#about-modal h3 {{
  color:#0f4; font-size:.82rem; letter-spacing:.15em;
  text-transform:uppercase; margin:18px 0 8px;
  font-family:'Share Tech Mono',monospace;
}}
#about-modal p, #about-modal li {{
  font-size:.9rem; color:#7aaf94; line-height:1.65; margin-bottom:6px;
}}
#about-modal ul {{ padding-left:18px; }}
#about-modal .stat {{ color:#0f4; font-weight:700; }}
#about-modal .hotspot {{ color:#ff8800; font-weight:700; }}
#about-close {{
  float:right; background:none; border:1px solid #0a3; color:#5a9;
  font-family:'Share Tech Mono',monospace; font-size:.72rem;
  padding:4px 12px; cursor:pointer; border-radius:2px;
  letter-spacing:.1em; text-transform:uppercase;
}}
#about-close:hover {{ color:#a0e8c8; border-color:#0f4; }}

/* ── search clear button ─────────────────────────────────── */
.search-wrap {{ position:relative; display:flex; align-items:center; }}
.search-wrap input {{ padding-right:24px; }}
#clear-search {{
  position:absolute; right:6px; background:none; border:none;
  color:#5a9; cursor:pointer; font-size:14px; line-height:1;
  padding:0; display:none;
}}
#clear-search:hover {{ color:#a0e8c8; }}

/* ── globe hint overlay ──────────────────────────────────── */
#globe-hint {{
  position:absolute; bottom:18px; left:50%; transform:translateX(-50%);
  z-index:500; display:none;
  color:#3a7; font-family:'Share Tech Mono',monospace; font-size:.72rem;
  letter-spacing:.12em; opacity:.7; pointer-events:none;
  text-shadow:0 0 8px #0f4;
}}
</style>
</head>
<body>

<div id="header">
  <h1>UAP <span>SIGHTING</span> MAP</h1>
  <button id="controls-toggle" aria-label="Toggle filters">☰&nbsp;FILTERS</button>
  <button id="about-btn">ℹ About</button>
  <button id="mode-toggle">🗺️&nbsp;2D MAP</button>
  <div id="stats">
    NUFORC <b>{nuforc_count:,}</b> &nbsp;|&nbsp;
    REDDIT <b>{reddit_count:,}</b> &nbsp;|&nbsp;
    ABDUCTIONS <b>{abduction_count:,}</b> &nbsp;|&nbsp;
    BASES <b>{len(military_bases):,}</b> &nbsp;|&nbsp;
    MISSING 411 <b>{len(missing_411):,}</b> &nbsp;|&nbsp;
    SCIENTISTS <b>{len(missing_scientists):,}</b> &nbsp;|&nbsp;
    NUCLEAR <b>{len(nuclear_sites):,}</b> &nbsp;|&nbsp;
    WINDOWS <b>{len(window_areas):,}</b> &nbsp;|&nbsp;
    MUFON <b>{mufon_count:,}</b> &nbsp;|&nbsp;
    LOCAL NEWS <b>{local_news_count:,}</b>
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
    <label>Year</label>
    <select id="filter-year">
      <option value="all">All Years</option>
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
    <div class="search-wrap">
      <input type="text" id="filter-search" placeholder="city, state, keyword…" style="width:180px;">
      <button id="clear-search" title="Clear search">✕</button>
    </div>
  </div>
  <span id="result-count"></span>
</div>

<div id="view-wrapper">
  <div id="globe-container">
    <div id="globe-hint">⬆ Switch to 2D for detailed exploration</div>
  </div>
  <div id="map"></div>
  <div id="tap-hint">👆 Tap any marker to read details</div>
  <div id="layer-panel">
    <div id="lp-header">
      <span id="lp-title">&#9632; Layers</span>
      <button id="lp-collapse" title="Collapse panel">&#9664;</button>
    </div>
    <div id="lp-body"></div>
  </div>
  <button id="lp-show" title="Show layers">&#9654; LAYERS</button>
</div>

<div id="legend"></div>

<div id="about-overlay">
  <div id="about-modal">
    <button id="about-close">✕ Close</button>
    <h2>About This Map</h2>

    <h3>Data Sources</h3>
    <ul>
      <li><b>NUFORC</b> — National UFO Reporting Center civilian hotline reports (bulk CSV)</li>
      <li><b>NUFORC Recent</b> — Live scrape of nuforc.org/webreports for current reports</li>
      <li><b>Reddit</b> — r/ufos and r/UFOs community sighting posts (JSON API)</li>
      <li><b>Curated reference layers</b> — Military bases, COG sites, USO locations, Missing 411 cases, Missing Scientists, 33rd Parallel sites, Nuclear sites, Cattle mutilation hotspots, UAP Window Areas, Ley Lines, Water &amp; Aquifer systems (manually researched)</li>
    </ul>

    <h3>Record Counts</h3>
    <ul>
      <li>UFO Sightings: <span class="stat">{nuforc_count:,} NUFORC + {reddit_count:,} Reddit</span></li>
      <li>Abduction Reports: <span class="stat">{abduction_count:,}</span></li>
      <li>Military Bases: <span class="stat">{len(military_bases):,}</span></li>
      <li>Missing 411 Cases: <span class="stat">{len(missing_411):,}</span></li>
      <li>Missing Scientists: <span class="stat">{len(missing_scientists):,}</span></li>
      <li>Water / Aquifer Sites: <span class="stat">{len(water_anomaly_sites):,}</span> (13 surface + 5 aquifer systems)</li>
    </ul>

    <h3>Key Findings</h3>
    <p><span class="hotspot">Pacific Northwest Hotspot Triangle</span><br>
    The densest UAP cluster in the dataset centers on eastern Washington and northern Idaho — directly above the Spokane Valley–Rathdrum Prairie Aquifer. Fairchild Air Force Base (heavy bomber/refueling hub) sits at the aquifer's western edge. The Hanford Nuclear Site is 130 miles south. Kenneth Arnold's first modern "flying saucer" sighting (June 24, 1947, over Mt. Rainier) and the Maury Island incident (June 21, 1947) both originate within 60 miles of this cluster. The correlation between the aquifer boundary, the military infrastructure, and the sighting density is the single most striking pattern in the dataset.</p>

    <p><span class="hotspot">New England Concentration</span><br>
    A secondary cluster appears across Massachusetts, Connecticut, and Rhode Island — consistent with decades of documented sightings in the Hudson Valley and Cape Cod corridors. The region contains high population density (increasing reporting rate), multiple military installations, and proximity to the Atlantic USO corridor.</p>

    <p><span class="hotspot">33rd Parallel Alignment</span><br>
    A disproportionate number of major UFO incidents, government facilities, ancient sacred sites, and anomalous phenomena cluster within a few degrees of 33° North latitude globally. Roswell (33.4°N), Area 51 (37°N but within the Southwest cluster), Phoenix Lights (33.4°N), Baghdad, and Damascus all sit on or near this line.</p>

    <h3>About</h3>
    <p>Built as an independent research visualization. All data is from public sources. This map is for educational and research purposes. Toggle layers to explore correlations between sighting density, infrastructure, and geography.</p>
    <p style="color:#3a7;font-size:.78rem;margin-top:16px">Last updated: {built_at}</p>
  </div>
</div>

<div id="built-at">Built {built_at}</div>

<script>
// ── Data ────────────────────────────────────────────────────
const ALL_SIGHTINGS    = {markers_json};
const ABDUCTION_REPORTS = {abduction_json};
const MILITARY_BASES   = {bases_json};
const COG_SITES        = {cog_json};
const USO_SITES        = {uso_json};
const MISSING_411        = {missing_json};
const MISSING_SCIENTISTS = {scientists_json};
const PARALLEL_33_SITES  = {p33_json};
const NUCLEAR_SITES      = {nuclear_json};
const CATTLE_SITES       = {cattle_json};
const WINDOW_AREAS       = {windows_json};
const LEY_LINES          = {leylines_json};
const WATER_ANOMALY_SITES = {water_json};
const MUFON_REPORTS       = {mufon_json};
const LOCAL_NEWS          = {local_news_json};
const MAPBOX_TOKEN        = '{mapbox_token}';

// ── Map init ────────────────────────────────────────────────
const map = L.map('map', {{
  center: [39.5, -98.35], zoom: 4,
  zoomControl: true, attributionControl: false,
  maxBounds: [[-85, -220], [85, 220]],
  maxBoundsViscosity: 1.0,
  minZoom: 2,
}});

L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  attribution: '&copy; OpenStreetMap &copy; CARTO', maxZoom: 19
}}).addTo(map);

// ── Year filter population ───────────────────────────────────
const yearSelect = document.getElementById('filter-year');
const years = [...new Set(ALL_SIGHTINGS.map(s => {{
  const m = (s.date || '').match(/\b(19|20)\d{{2}}\b/);
  return m ? m[0] : null;
}}).filter(Boolean))].sort((a,b) => b - a);
years.forEach(y => {{
  const opt = document.createElement('option');
  opt.value = y; opt.textContent = y;
  yearSelect.appendChild(opt);
}});

// ── Shape filter population ─────────────────────────────────
const shapes = [...new Set(ALL_SIGHTINGS.map(s => s.shape).filter(Boolean))].sort();
const shapeSelect = document.getElementById('filter-shape');
shapes.forEach(shape => {{
  if (shape && shape !== 'unknown') {{
    const opt = document.createElement('option');
    opt.value = shape; opt.textContent = shape;
    shapeSelect.appendChild(opt);
  }}
}});

// ── Emoji icon map ──────────────────────────────────────────
const SHAPE_EMOJI = {{
  light:'💡', circle:'🔵', triangle:'🔺', disk:'🛸', saucer:'🛸',
  fireball:'🔥', cylinder:'🛢️', sphere:'⚪', chevron:'✈️', diamond:'💎',
  cross:'✝️', rectangle:'⬜', formation:'🔷', other:'❓', unknown:'❓',
  changing:'🌀', cone:'🔺', cigar:'🛢️', egg:'⚪', teardrop:'💧',
  flash:'⚡', oval:'🔵',
}};

// Touch target wrapper: 44×44px transparent hit area (Apple HIG minimum),
// with the visual indicator centered inside.
function _touchWrap(innerHtml, visualSize) {{
  const pad = Math.max(0, Math.round((44 - visualSize) / 2));
  return `<div style="width:44px;height:44px;display:flex;align-items:center;
             justify-content:center;cursor:pointer;">${{innerHtml}}</div>`;
}}

function makeIcon(source, shape) {{
  const isNuforc = source === 'NUFORC' || source === 'NUFORC Recent';
  if (isNuforc) {{
    // NUFORC — tiny dim green dot (8px), 50% opacity, no emoji: background reference layer
    const dot = `<div style="width:8px;height:8px;border-radius:50%;
                   background:#00ff44;opacity:0.5;flex-shrink:0;"></div>`;
    return L.divIcon({{
      className: '',
      html: _touchWrap(dot, 8),
      iconSize: [44,44], iconAnchor: [22,22],
    }});
  }} else {{
    // Reddit / other — shape-based emoji on gold-glowing dark circle
    const emoji = SHAPE_EMOJI[(shape||'').toLowerCase()] || '🛸';
    return emojiIcon(emoji, '#ffaa00', 18);
  }}
}}

// ── Emoji icon helper — 44px touch target, 22px emoji on dark circle ─────────
function emojiIcon(emoji, color, size) {{
  size = size || 22;
  const box  = Math.max(32, size + 10);   // visual circle diameter
  const glow = `drop-shadow(0 0 5px ${{color}}) drop-shadow(0 0 10px ${{color}}55)`;
  const inner = `<div style="width:${{box}}px;height:${{box}}px;border-radius:50%;
    background:rgba(4,13,20,.75);border:1.5px solid ${{color}}66;
    display:flex;align-items:center;justify-content:center;
    filter:${{glow}};flex-shrink:0;">
    <span style="font-size:${{size}}px;line-height:1">${{emoji}}</span>
  </div>`;
  return L.divIcon({{
    className: '',
    html: _touchWrap(inner, box),
    iconSize: [44, 44], iconAnchor: [22, 22],
  }});
}}

// ── Branch colours for military ─────────────────────────────
const BRANCH_COLORS = {{
  Army:'#4caf50', Navy:'#2196f3', Marines:'#f44336',
  'Air Force':'#03a9f4', 'Space Force':'#9c27b0', Special:'#ff5722',
}};

function makeMilIcon(branch) {{
  const c = BRANCH_COLORS[branch] || '#ff4444';
  const inner = `<div style="width:32px;height:32px;border-radius:50%;
    background:rgba(4,13,20,.72);border:1.5px solid ${{c}}88;
    display:flex;align-items:center;justify-content:center;
    filter:drop-shadow(0 0 5px ${{c}});">
    <div style="width:0;height:0;border-left:9px solid transparent;
      border-right:9px solid transparent;border-bottom:16px solid ${{c}};"></div>
  </div>`;
  return L.divIcon({{
    className:'', html:_touchWrap(inner,32), iconSize:[44,44], iconAnchor:[22,22]
  }});
}}

function makeCogIcon() {{
  const inner = `<div style="width:32px;height:32px;border-radius:50%;
    background:rgba(4,13,20,.72);border:1.5px solid #ffe03388;
    display:flex;align-items:center;justify-content:center;
    filter:drop-shadow(0 0 5px #ffe033);">
    <div style="width:18px;height:18px;background:#ffe033;
      clip-path:polygon(50% 0%,61% 35%,98% 35%,68% 57%,79% 91%,50% 70%,21% 91%,32% 57%,2% 35%,39% 35%);"></div>
  </div>`;
  return L.divIcon({{
    className:'', html:_touchWrap(inner,32), iconSize:[44,44], iconAnchor:[22,22]
  }});
}}

// ── Cluster factory ─────────────────────────────────────────
function clusterGroup(color) {{
  return L.markerClusterGroup({{
    chunkedLoading: true,
    removeOutsideVisibleBounds: true,
    maxClusterRadius: 38,          // tighter clusters → expand sooner
    disableClusteringAtZoom: 10,   // individual markers at zoom 10+
    zoomToBoundsOnClick: true,     // click cluster → zoom in to expand
    iconCreateFunction(cluster) {{
      const n    = cluster.getChildCount();
      const size = n < 10 ? 34 : n < 50 ? 42 : n < 200 ? 50 : 58;
      const fs   = n < 10 ? 14 : n < 100 ? 13 : 11;
      return L.divIcon({{
        className:'',
        html:`<div style="
          width:${{size}}px;height:${{size}}px;border-radius:50%;
          background:${{color}}22;border:2.5px solid ${{color}};
          display:flex;align-items:center;justify-content:center;
          color:${{color}};font-family:'Share Tech Mono',monospace;
          font-size:${{fs}}px;font-weight:bold;letter-spacing:-.5px;
          box-shadow:0 0 12px ${{color}}66,inset 0 0 8px ${{color}}22;">
            ${{n}}
          </div>`,
        iconSize:[size,size], iconAnchor:[size/2,size/2]
      }});
    }}
  }});
}}

// ── Sightings layer — viewport lazy-loading ─────────────────
const markerLayer = clusterGroup('#00ff44');
// markerLayer starts OFF — user enables via layer panel

let addedIdx = new Set();
let activeFilters = {{ src:'all', year:'all', shape:'all', search:'' }};

function matches(s) {{
  if (activeFilters.src !== 'all' && !s.source.includes(activeFilters.src)) return false;
  if (activeFilters.shape !== 'all' && s.shape !== activeFilters.shape) return false;
  if (activeFilters.year !== 'all') {{
    const m = (s.date || '').match(/\b(19|20)\d{{2}}\b/);
    if (!m || m[0] !== activeFilters.year) return false;
  }}
  if (activeFilters.search) {{
    const hay = `${{s.location}} ${{s.summary}} ${{s.shape}}`.toLowerCase();
    if (!hay.includes(activeFilters.search)) return false;
  }}
  return true;
}}

// ── Duration formatter ───────────────────────────────────────
function fmtDuration(secs) {{
  const n = parseInt(secs);
  if (!secs || isNaN(n) || n <= 0) return '';
  if (n < 60)   return `${{n}}s`;
  if (n < 3600) return `${{Math.round(n/60)}}m`;
  return `${{(n/3600).toFixed(1)}}h`;
}}

function loadVisible() {{
  const bounds = map.getBounds().pad(0.4);
  const batch  = [];
  ALL_SIGHTINGS.forEach((s, i) => {{
    if (addedIdx.has(i) || !bounds.contains([s.lat, s.lon]) || !matches(s)) return;
    addedIdx.add(i);
    const m = L.marker([s.lat, s.lon], {{icon: makeIcon(s.source, s.shape)}});
    const linkHtml = s.url ? `<a href="${{s.url}}" target="_blank" class="popup-link">→ View post</a>` : '';
    const durStr   = fmtDuration(s.duration);
    const metaExtra = durStr ? ` &nbsp;·&nbsp; ⏱ ${{durStr}}` : '';
    m.bindPopup(`
      <div class="popup-source" style="color:${{(s.source==='NUFORC'||s.source==='NUFORC Recent')?'#00ff44':'#ffaa00'}}">${{s.source}}</div>
      <div class="popup-title">${{s.location || 'Unknown Location'}}</div>
      <div class="popup-meta">📅 ${{s.date}} &nbsp;·&nbsp; 🔷 ${{s.shape || 'unknown'}}${{metaExtra}}</div>
      <div class="popup-summary">${{s.summary}}</div>
      ${{linkHtml}}
    `, {{maxWidth:290}});
    batch.push(m);
  }});
  if (batch.length) markerLayer.addLayers(batch);
  const total   = ALL_SIGHTINGS.filter(matches).length;
  const visible = markerLayer.getLayers().length;
  document.getElementById('result-count').textContent =
    `Showing ${{visible.toLocaleString()}} / ${{total.toLocaleString()}} sightings`;
}}

function renderMarkers() {{
  markerLayer.clearLayers();
  addedIdx.clear();
  const searchVal = document.getElementById('filter-search').value.toLowerCase().trim();
  document.getElementById('clear-search').style.display = searchVal ? 'block' : 'none';
  activeFilters = {{
    src:   document.getElementById('filter-source').value,
    year:  document.getElementById('filter-year').value,
    shape: document.getElementById('filter-shape').value,
    search: searchVal,
  }};
  loadVisible();
}}

map.on('moveend zoomend', loadVisible);

// ── Military bases ──────────────────────────────────────────
const militaryLayer = clusterGroup('#ff4444');
MILITARY_BASES.forEach(b => {{
  const c = BRANCH_COLORS[b.branch] || '#ff4444';
  const m = L.marker([b.lat, b.lon], {{icon: makeMilIcon(b.branch)}});
  m.bindPopup(`
    <div class="popup-source" style="color:${{c}}">&#9650; ${{b.branch}}</div>
    <div class="popup-title"  style="color:${{c}}">${{b.name}}</div>
    <div class="popup-meta">${{b.state}}</div>
  `, {{maxWidth:220}});
  militaryLayer.addLayer(m);
}});

// ── COG sites ───────────────────────────────────────────────
const cogLayer = clusterGroup('#ffe033');
COG_SITES.forEach(site => {{
  const m = L.marker([site.lat, site.lon], {{icon: makeCogIcon()}});
  m.bindPopup(`
    <div class="popup-source" style="color:#ffe033;">&#9733; CONTINUITY OF GOVERNMENT</div>
    <div class="popup-title"  style="color:#ffe033;">${{site.name}}</div>
    <div class="popup-meta"   style="color:#cc9;">${{site.location}}</div>
    <div class="popup-summary">${{site.description}}</div>
  `, {{maxWidth:320}});
  cogLayer.addLayer(m);
}});

// ── USO sites ───────────────────────────────────────────────
const usoLayer = clusterGroup('#00bfff');
USO_SITES.forEach(site => {{
  const m = L.marker([site.lat, site.lon], {{icon: emojiIcon('🌊','#00bfff',22)}});
  m.bindPopup(`
    <div class="popup-source" style="color:#00bfff;">🌊 UNIDENTIFIED SUBMERGED OBJECT</div>
    <div class="popup-title"  style="color:#00bfff;">${{site.name}}</div>
    <div class="popup-meta"   style="color:#7ce;">${{site.location}}</div>
    <div class="popup-summary">${{site.description}}</div>
  `, {{maxWidth:320}});
  usoLayer.addLayer(m);
}});

// ── Abduction reports ───────────────────────────────────────
const abductionLayer = clusterGroup('#cc44ff');
ABDUCTION_REPORTS.forEach(s => {{
  const isNuforc = s.source === 'NUFORC Abduction';
  const emoji = isNuforc ? '👤' : '👽';
  const color = isNuforc ? '#ff44aa' : '#cc44ff';
  const m = L.marker([s.lat, s.lon], {{icon: emojiIcon(emoji, color, 18)}});
  const linkHtml = s.url ? `<a href="${{s.url}}" target="_blank" class="popup-link">→ View post</a>` : '';
  m.bindPopup(`
    <div class="popup-source" style="color:${{color}}">${{emoji}} ${{s.source}}</div>
    <div class="popup-title"  style="color:${{color}}">${{s.location || 'Unknown Location'}}</div>
    <div class="popup-meta">📅 ${{s.date}}</div>
    <div class="popup-summary">${{s.summary}}</div>
    ${{linkHtml}}
  `, {{maxWidth:300}});
  abductionLayer.addLayer(m);
}});

// ── Missing 411 layer ───────────────────────────────────────
const missing411Layer = clusterGroup('#cc0044');
MISSING_411.forEach(site => {{
  const m = L.marker([site.lat, site.lon], {{icon: emojiIcon('🔴','#cc0044',20)}});
  const linkHtml = site.url
    ? `<a href="${{site.url}}" target="_blank" class="popup-link">→ Full case details</a>`
    : '';
  m.bindPopup(`
    <div class="popup-source" style="color:#ff3366;">🔴 MISSING 411</div>
    <div class="popup-title"  style="color:#ff3366;">${{site.name}}</div>
    <div class="popup-meta"   style="color:#c88;">${{site.location}}</div>
    <div class="popup-summary" style="color:#daa;">Unexplained wilderness disappearance documented by researcher David Paulides. Source: vanished.us</div>
    ${{linkHtml}}
  `, {{maxWidth:300}});
  missing411Layer.addLayer(m);
}});

// ── 33rd Parallel layer ─────────────────────────────────────
const parallel33Layer = L.layerGroup();

L.polyline([[33.0, -200], [33.0, 200]], {{
  color: '#ff2222', weight: 2, dashArray: '10,7', opacity: 0.75
}}).addTo(parallel33Layer);

L.marker([33.0, -148], {{icon: L.divIcon({{
  className: '',
  html: '<div style="color:#ff4444;font-family:Share Tech Mono,monospace;font-size:10px;white-space:nowrap;text-shadow:0 0 8px #ff0000;letter-spacing:.1em;">— 33° PARALLEL —</div>',
  iconSize: [130, 16], iconAnchor: [65, 8]
}})}}).addTo(parallel33Layer);

PARALLEL_33_SITES.forEach(site => {{
  const m = L.marker([site.lat, site.lon], {{icon: L.divIcon({{
    className: '',
    html: '<div style="font-size:15px;line-height:1;filter:drop-shadow(0 0 5px #ff2222);">🔺</div>',
    iconSize: [18,18], iconAnchor: [9,9]
  }})}});
  m.bindPopup(`
    <div class="popup-source" style="color:#ff4444;">🔺 33RD PARALLEL SITE</div>
    <div class="popup-title"  style="color:#ff4444;">${{site.name}}</div>
    <div class="popup-summary">${{site.note}}</div>
  `, {{maxWidth:300}});
  parallel33Layer.addLayer(m);
}});

// ── Nuclear Sites layer ─────────────────────────────────────
const nuclearLayer = clusterGroup('#00ff99');
NUCLEAR_SITES.forEach(site => {{
  const typeColor = site.type === 'Incident' ? '#ff4400'
    : site.type === 'Testing' ? '#ffaa00' : '#00ff99';
  const m = L.marker([site.lat, site.lon], {{icon: emojiIcon('⚛️', typeColor, 20)}});
  m.bindPopup(`
    <div class="popup-source" style="color:${{typeColor}};">⚛️ NUCLEAR — ${{site.type.toUpperCase()}}</div>
    <div class="popup-title"  style="color:${{typeColor}};">${{site.name}}</div>
    <div class="popup-meta"   style="color:#8cc;">📍 ${{site.location}}</div>
    <div class="popup-summary">${{site.description}}</div>
  `, {{maxWidth:320}});
  nuclearLayer.addLayer(m);
}});

// ── Cattle Mutilation layer ──────────────────────────────────
const cattleLayer = clusterGroup('#cc6600');
CATTLE_SITES.forEach(site => {{
  const m = L.marker([site.lat, site.lon], {{icon: emojiIcon('🐄','#cc6600',20)}});
  m.bindPopup(`
    <div class="popup-source" style="color:#cc6600;">🐄 CATTLE MUTILATION HOTSPOT</div>
    <div class="popup-title"  style="color:#cc6600;">${{site.name}}</div>
    <div class="popup-meta"   style="color:#a85;">📍 ${{site.location}}</div>
    <div class="popup-summary">${{site.description}}</div>
  `, {{maxWidth:320}});
  cattleLayer.addLayer(m);
}});

// ── Window Areas layer ───────────────────────────────────────
const windowLayer = clusterGroup('#aa44ff');
WINDOW_AREAS.forEach(site => {{
  const m = L.marker([site.lat, site.lon], {{icon: emojiIcon('👁️','#aa44ff',20)}});
  m.bindPopup(`
    <div class="popup-source" style="color:#aa44ff;">👁️ WINDOW AREA — MULTI-PHENOMENON</div>
    <div class="popup-title"  style="color:#aa44ff;">${{site.name}}</div>
    <div class="popup-meta"   style="color:#99a;">📍 ${{site.location}}</div>
    <div class="popup-summary">${{site.description}}</div>
  `, {{maxWidth:340}});
  windowLayer.addLayer(m);
}});

// ── Ley Lines layer ──────────────────────────────────────────
const leyLineLayer = L.layerGroup();

LEY_LINES.forEach(line => {{
  // ── main polyline ────────────────────────────────────────
  const poly = L.polyline(line.points, {{
    color:     line.color,
    weight:    2.5,
    dashArray: '10,6',
    opacity:   0.75,
  }});
  poly.bindPopup(`
    <div class="popup-source" style="color:${{line.color}};">✦ LEY LINE</div>
    <div class="popup-title"  style="color:${{line.color}};">${{line.name}}</div>
    <div class="popup-summary">${{line.description}}</div>
  `, {{maxWidth:340}});
  poly.addTo(leyLineLayer);

  // ── glow layer (wider, lower opacity) ───────────────────
  L.polyline(line.points, {{
    color:     line.color,
    weight:    6,
    dashArray: '10,6',
    opacity:   0.18,
    interactive: false,
  }}).addTo(leyLineLayer);

  // ── inline label at label_at position ───────────────────
  if (line.label_at) {{
    const labelEl = `<div style="
      color:${{line.color}};
      font-family:'Share Tech Mono',monospace;
      font-size:9px;
      letter-spacing:.14em;
      white-space:nowrap;
      text-shadow:0 0 6px ${{line.color}},0 0 12px ${{line.color}};
      background:rgba(4,13,20,.6);
      padding:1px 5px;
      border-left:2px solid ${{line.color}};
      pointer-events:none;
    ">${{line.short || line.name}}</div>`;

    L.marker(line.label_at, {{
      icon: L.divIcon({{
        className: 'ley-label',
        html: labelEl,
        iconSize:   [160, 16],
        iconAnchor: [0, 8],
      }}),
      interactive: false,
      zIndexOffset: -1000,
    }}).addTo(leyLineLayer);
  }}

  // ── waypoint markers ─────────────────────────────────────
  (line.waypoints || []).forEach(wp => {{
    const m = L.marker([wp.lat, wp.lon], {{
      icon: L.divIcon({{
        className: '',
        html: `<div style="
          width:9px;height:9px;border-radius:50%;
          background:${{line.color}};
          border:1.5px solid #fff2;
          box-shadow:0 0 6px ${{line.color}},0 0 12px ${{line.color}}44;
        "></div>`,
        iconSize:   [9, 9],
        iconAnchor: [4.5, 4.5],
      }}),
    }});
    m.bindPopup(`
      <div class="popup-source" style="color:${{line.color}};">✦ ${{line.name}}</div>
      <div class="popup-title"  style="color:${{line.color}};">${{wp.name}}</div>
      <div class="popup-summary">${{wp.note}}</div>
    `, {{maxWidth:320}});
    leyLineLayer.addLayer(m);
  }});
}});

// ── Missing Scientists layer ────────────────────────────────
const scientistsLayer = clusterGroup('#ffffff');
MISSING_SCIENTISTS.forEach(s => {{
  const statusColor = s.status.toLowerCase().startsWith('murder') ? '#ff2222'
    : s.status.toLowerCase().startsWith('dead') ? '#ff6600'
    : '#ffffff';
  const m = L.marker([s.lat, s.lon], {{icon: emojiIcon('☢️','#ffffff',20)}});
  m.bindPopup(`
    <div class="popup-source" style="color:#fff;letter-spacing:.15em;">☢️ MISSING SCIENTIST</div>
    <div class="popup-title"  style="color:#fff;">${{s.name}}</div>
    <div class="popup-meta"   style="color:#aaa;">📅 ${{s.date}} &nbsp;·&nbsp; 📍 ${{s.location}}</div>
    <div class="popup-meta"   style="color:#8cf;margin-bottom:6px;">🏛 ${{s.affiliation}}</div>
    <div class="popup-meta"   style="color:${{statusColor}};font-weight:700;margin-bottom:8px;">⚠️ ${{s.status}}</div>
    <div class="popup-summary" style="color:#ccc;">${{s.notes}}</div>
  `, {{maxWidth:320}});
  scientistsLayer.addLayer(m);
}});

// ── Water & Aquifer layer ────────────────────────────────────
const waterLayer = clusterGroup('#00cfff');
WATER_ANOMALY_SITES.forEach(site => {{
  const isAquifer = site.type === 'aquifer';
  const col       = isAquifer ? '#00aaff' : '#00eeff';
  const emoji     = isAquifer ? '🌊' : '💧';
  const glow      = isAquifer ? '#0088ff' : '#00cfff';
  // Spokane Valley gets extra glow — highlighted hotspot
  const isHotspot = site.name.includes('Spokane');
  const sz = isHotspot ? 24 : 20;
  const hotGlow = isHotspot ? `drop-shadow(0 0 10px #00cfff) drop-shadow(0 0 20px #00cfff88)` : '';
  const box = sz + 8;
  const m = L.marker([site.lat, site.lon], {{icon: L.divIcon({{
    className: '',
    html: `<div style="width:${{box}}px;height:${{box}}px;border-radius:50%;
             background:rgba(4,13,20,.68);border:1px solid ${{glow}}44;
             display:flex;align-items:center;justify-content:center;
             filter:drop-shadow(0 0 4px ${{glow}}) ${{hotGlow}};">
             <span style="font-size:${{sz}}px;line-height:1">${{emoji}}</span>
           </div>`,
    iconSize: [box, box], iconAnchor: [box/2, box/2],
  }})}});
  const typeLabel = isAquifer ? 'UNDERGROUND AQUIFER' : 'WATER ANOMALY SITE';
  const hotspotNote = isHotspot
    ? `<div class="popup-meta" style="color:#ff4;font-weight:700;">⚠️ SITS WITHIN PACIFIC NW UAP HOTSPOT TRIANGLE</div>`
    : '';
  m.bindPopup(`
    <div class="popup-source" style="color:${{col}};">${{emoji}} ${{typeLabel}}</div>
    <div class="popup-title"  style="color:${{col}};">${{site.name}}</div>
    <div class="popup-meta"   style="color:#7ce;">📍 ${{site.location}}</div>
    ${{hotspotNote}}
    <div class="popup-summary">${{site.description}}</div>
  `, {{maxWidth:340}});
  waterLayer.addLayer(m);
}});

// ── Heatmap layers ───────────────────────────────────────────
// Must be declared before LAYER_REGISTRY so the const bindings exist.
const heatAllLayer = L.heatLayer(
  ALL_SIGHTINGS.map(s => [s.lat, s.lon, 0.5]),
  {{ radius:20, blur:14, maxZoom:10,
     gradient:{{ 0.2:'#003322', 0.45:'#00ff44', 0.7:'#ffff00', 0.9:'#ff8800', 1:'#ff2222' }} }}
);
const heatAbductionLayer = L.heatLayer(
  ABDUCTION_REPORTS.map(s => [s.lat, s.lon, 1.0]),
  {{ radius:35, blur:22, maxZoom:10, minOpacity:0.35,
     gradient:{{ 0.0:'#0d0020', 0.25:'#2d0060', 0.5:'#7700cc', 0.72:'#cc44ff', 0.88:'#ff99ff', 1:'#ffffff' }} }}
);

// ── MUFON Reports layer ──────────────────────────────────────
const mufonLayer = clusterGroup('#ff8800');
MUFON_REPORTS.forEach(s => {{
  const m = L.marker([s.lat, s.lon], {{icon: emojiIcon('🛸','#ff8800',18)}});
  const linkHtml = s.url ? `<a href="${{s.url}}" target="_blank" class="popup-link">→ View case</a>` : '';
  m.bindPopup(`
    <div class="popup-source" style="color:#ff8800;">🛸 MUFON REPORT</div>
    <div class="popup-title"  style="color:#ff8800;">${{s.location || 'Unknown Location'}}</div>
    <div class="popup-meta">📅 ${{s.date}} &nbsp;·&nbsp; 🔷 ${{s.shape || 'unknown'}}</div>
    <div class="popup-summary">${{s.summary}}</div>
    ${{linkHtml}}
  `, {{maxWidth:300}});
  mufonLayer.addLayer(m);
}});
// mufonLayer NOT added to map here — added by layer panel when toggled ON

// ── Local News layer ─────────────────────────────────────────
const localNewsLayer = clusterGroup('#00ffcc');
LOCAL_NEWS.forEach(s => {{
  const m = L.marker([s.lat, s.lon], {{icon: emojiIcon('📡','#00ffcc',18)}});
  const linkHtml = s.url ? `<a href="${{s.url}}" target="_blank" class="popup-link">→ Read article</a>` : '';
  m.bindPopup(`
    <div class="popup-source" style="color:#00ffcc;">📡 LOCAL NEWS</div>
    <div class="popup-title"  style="color:#00ffcc;">${{s.location || 'Unknown Location'}}</div>
    <div class="popup-meta">📅 ${{s.date}} &nbsp;·&nbsp; 🗞️ ${{s.source_name || 'Local Report'}}</div>
    <div class="popup-summary">${{s.summary}}</div>
    ${{linkHtml}}
  `, {{maxWidth:300}});
  localNewsLayer.addLayer(m);
}});
// localNewsLayer NOT added to map here — added by layer panel when toggled ON

// ── Custom layer panel ───────────────────────────────────────
// Replaces Leaflet's built-in control. Each group is collapsible;
// checkboxes call map.addLayer / removeLayer directly.
const LAYER_REGISTRY = {{
  'UFO Sightings':               markerLayer,
  'Abduction Reports':           abductionLayer,
  'Heat Map (All Sightings)':    heatAllLayer,
  'Heat Map (Abductions Only)':  heatAbductionLayer,
  'Military Bases':              militaryLayer,
  'COG Sites':                   cogLayer,
  'Nuclear Sites':               nuclearLayer,
  'USO Sites':                   usoLayer,
  'Missing Scientists':          scientistsLayer,
  'Missing 411':                 missing411Layer,
  'Water & Aquifers':            waterLayer,
  'Cattle Mutilations':          cattleLayer,
  'Window Areas':                windowLayer,
  'Ley Lines':                   leyLineLayer,
  '33rd Parallel':               parallel33Layer,
  'MUFON Reports':               mufonLayer,
  'Local News':                  localNewsLayer,
}};

const LAYER_GROUPS = [
  {{ icon:'🛸', name:'SIGHTINGS', open:true, items:[
    {{ name:'MUFON Reports',              color:'#ff8800', on:false }},
    {{ name:'Local News',                 color:'#00ffcc', on:false }},
    {{ name:'UFO Sightings',              color:'#00ff44', on:true  }},
    {{ name:'Abduction Reports',          color:'#ff44aa', on:false }},
    {{ name:'Heat Map (All Sightings)',   color:'#ff6600', on:false }},
    {{ name:'Heat Map (Abductions Only)', color:'#ff44aa', on:false }},
  ]}},
  {{ icon:'🏛️', name:'INFRASTRUCTURE', open:false, items:[
    {{ name:'Military Bases', color:'#ff4444', on:false }},
    {{ name:'COG Sites',      color:'#ffe033', on:false }},
    {{ name:'Nuclear Sites',  color:'#00ff99', on:false }},
    {{ name:'USO Sites',      color:'#00bfff', on:false }},
  ]}},
  {{ icon:'👤', name:'PEOPLE', open:false, items:[
    {{ name:'Missing Scientists', color:'#ffffff', on:false }},
    {{ name:'Missing 411',        color:'#ff2255', on:false }},
  ]}},
  {{ icon:'🌊', name:'ENVIRONMENT', open:false, items:[
    {{ name:'Water & Aquifers',   color:'#00cfff', on:false }},
    {{ name:'Cattle Mutilations', color:'#cc6600', on:false }},
    {{ name:'Window Areas',       color:'#aa44ff', on:false }},
  ]}},
  {{ icon:'🔺', name:'PATTERNS', open:false, items:[
    {{ name:'Ley Lines',     color:'#ffaa00', on:false }},
    {{ name:'33rd Parallel', color:'#ff2222', on:false }},
  ]}},
];

// ── Legend definitions (shown only when layer is active) ────
const LEGEND_DEFS = {{
  'UFO Sightings':      {{ ico:'<span style="font-size:12px">🛸💡🔵🔺</span>',          lbl:'UFO Sighting'       }},
  'Abduction Reports':  {{ ico:'<span style="font-size:12px">👤👽</span>',               lbl:'Abduction Report'   }},
  'Military Bases':     {{ ico:'<span style="color:#f44;font-size:13px">▲</span>',       lbl:'Military Base'      }},
  'COG Sites':          {{ ico:'<span style="color:#ffe033;font-size:13px">★</span>',    lbl:'COG Site'           }},
  'Nuclear Sites':      {{ ico:'<span style="font-size:12px">⚛️</span>',                 lbl:'Nuclear Site'       }},
  'USO Sites':          {{ ico:'<span style="font-size:12px">🌊</span>',                 lbl:'USO Site'           }},
  'Missing Scientists': {{ ico:'<span style="font-size:12px">☢️</span>',                 lbl:'Missing Scientist'  }},
  'Missing 411':        {{ ico:'<span style="font-size:12px">🔴</span>',                 lbl:'Missing 411'        }},
  'Water & Aquifers':   {{ ico:'<span style="font-size:12px">💧🌊</span>',               lbl:'Water / Aquifer'    }},
  'Cattle Mutilations': {{ ico:'<span style="font-size:12px">🐄</span>',                 lbl:'Cattle Mutilation'  }},
  'Window Areas':       {{ ico:'<span style="font-size:12px">👁️</span>',                 lbl:'Window Area'        }},
  'Ley Lines':          {{ ico:'<span style="color:#ffaa00;font-size:10px">———</span>',  lbl:'Ley Line'           }},
  '33rd Parallel':               {{ ico:'<span style="color:#ff2222;font-size:10px">— —</span>',  lbl:'33rd Parallel'            }},
  'Heat Map (All Sightings)':    {{ ico:'<span style="font-size:12px">🔥</span>',                  lbl:'Heatmap — All Sightings'  }},
  'Heat Map (Abductions Only)':  {{ ico:'<span style="font-size:12px">🔥</span>',                  lbl:'Heatmap — Abductions'     }},
  'MUFON Reports':               {{ ico:'<span style="font-size:12px">🛸</span>',                  lbl:'MUFON Report'             }},
  'Local News':                  {{ ico:'<span style="font-size:12px">📡</span>',                  lbl:'Local News Sighting'      }},
}};

// ── Layer state ───────────────────────────────────────────────────────────────
// Declared before updateLegend/buildLayerPanel so both can reference it.
// Only names listed here are added to the map on startup.
const activeLayerNames = new Set(['UFO Sightings']);

// Sync map to initial activeLayerNames: add only layers that should start ON,
// leave all others off the map entirely (layer panel adds them when toggled).
// Runs after LAYER_REGISTRY is defined (see above) and after activeLayerNames.
setTimeout(() => {{
  Object.entries(LAYER_REGISTRY).forEach(([name, layer]) => {{
    if (activeLayerNames.has(name)) {{
      if (!map.hasLayer(layer)) map.addLayer(layer);
    }} else {{
      if (map.hasLayer(layer)) map.removeLayer(layer);
    }}
  }});
}}, 0);

function updateLegend() {{
  const leg = document.getElementById('legend');
  const order = LAYER_GROUPS.flatMap(g => g.items.map(i => i.name));
  const rows  = order
    .filter(n => activeLayerNames.has(n) && LEGEND_DEFS[n])
    .map(n => `<div class="legend-item">${{LEGEND_DEFS[n].ico}}&nbsp; ${{LEGEND_DEFS[n].lbl}}</div>`)
    .join('');
  leg.innerHTML = rows;
  leg.style.display = rows ? '' : 'none';
}}

(function buildLayerPanel() {{
  const body = document.getElementById('lp-body');
  LAYER_GROUPS.forEach(group => {{
    const groupEl = document.createElement('div');
    groupEl.className = 'lp-group' + (group.open ? ' open' : '');

    const hdr = document.createElement('div');
    hdr.className = 'lp-group-hdr';
    hdr.innerHTML = `<span class="lp-group-icon">${{group.icon}}</span>
      <span class="lp-group-name">${{group.name}}</span>
      <span class="lp-chevron">▾</span>`;
    hdr.addEventListener('click', () => groupEl.classList.toggle('open'));
    groupEl.appendChild(hdr);

    const items = document.createElement('div');
    items.className = 'lp-group-items';
    group.items.forEach(item => {{
      const lbl = document.createElement('label');
      lbl.className = 'lp-item';
      lbl.innerHTML = `
        <input type="checkbox" ${{item.on ? 'checked' : ''}} data-layer="${{item.name}}">
        <span class="lp-dot" style="background:${{item.color}};box-shadow:0 0 5px ${{item.color}}66;"></span>
        <span class="lp-name">${{item.name}}</span>`;
      lbl.querySelector('input').addEventListener('change', e => {{
        const layer = LAYER_REGISTRY[item.name];
        if (!layer) return;
        if (e.target.checked) {{
          map.addLayer(layer);
          activeLayerNames.add(item.name);
        }} else {{
          map.removeLayer(layer);
          activeLayerNames.delete(item.name);
        }}
        updateLegend();
        if (currentMode === 'globe') updateGlobe();
      }});
      items.appendChild(lbl);
    }});
    groupEl.appendChild(items);
    body.appendChild(groupEl);
  }});
}})();

// ── Panel collapse / expand ──────────────────────────────────
document.getElementById('lp-collapse').addEventListener('click', () => {{
  document.getElementById('layer-panel').style.display = 'none';
  document.getElementById('lp-show').style.display     = 'block';
}});
document.getElementById('lp-show').addEventListener('click', () => {{
  document.getElementById('layer-panel').style.display = '';
  document.getElementById('lp-show').style.display     = 'none';
}});

// ── Filter events ───────────────────────────────────────────
document.getElementById('filter-source').addEventListener('change', renderMarkers);
document.getElementById('filter-year').addEventListener('change',   renderMarkers);
document.getElementById('filter-shape').addEventListener('change',  renderMarkers);
document.getElementById('filter-search').addEventListener('input',  renderMarkers);
document.getElementById('clear-search').addEventListener('click', () => {{
  document.getElementById('filter-search').value = '';
  renderMarkers();
  document.getElementById('filter-search').focus();
}});

updateLegend();
renderMarkers();

// ════════════════════════════════════════════════════════════
// GLOBE / FLAT MODE
// ════════════════════════════════════════════════════════════

const globeEl     = document.getElementById('globe-container');
const mapEl       = document.getElementById('map');
let   currentMode = 'flat';
let   mbMap       = null;
let   mbLoaded    = false;

// ── Mapbox layer config — per-layer paint for visual hierarchy ───────────────
// UFO Sightings handled separately as a clustered source (see initMapboxGlobe).
// Each remaining entry carries its own `paint` object; the loop uses it directly.
const MB_LAYERS = [
  // Abductions: vivid purple, medium size, bright stroke
  {{ id:'abductions', data:() => ABDUCTION_REPORTS,
     name:'Abduction Reports', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,2.5, 3,4.5, 7,9],
       'circle-color':             '#9900ff',
       'circle-opacity':           0.88,
       'circle-stroke-width':      1.5,
       'circle-stroke-color':      '#dd88ff',
       'circle-emissive-strength': 1,
     }}}},
  // MUFON: amber-orange
  {{ id:'mufon', data:() => MUFON_REPORTS,
     name:'MUFON Reports', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,2.5, 3,4.5, 7,9],
       'circle-color':             '#ff8800',
       'circle-opacity':           0.88,
       'circle-stroke-width':      1.2,
       'circle-stroke-color':      '#ffaa44',
       'circle-emissive-strength': 1,
     }}}},
  // Local news: teal
  {{ id:'local-news', data:() => LOCAL_NEWS,
     name:'Local News', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,2.5, 3,4.5, 7,9],
       'circle-color':             '#00ffcc',
       'circle-opacity':           0.88,
       'circle-stroke-width':      1.2,
       'circle-stroke-color':      '#66ffee',
       'circle-emissive-strength': 1,
     }}}},
  // Military bases: large bright blue — high-importance infrastructure
  {{ id:'military', data:() => MILITARY_BASES,
     name:'Military Bases', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,5, 3,8, 7,14],
       'circle-color':             '#0077ff',
       'circle-opacity':           0.92,
       'circle-stroke-width':      2.5,
       'circle-stroke-color':      '#55aaff',
       'circle-emissive-strength': 1,
     }}}},
  // COG sites: large blood-red, thick ring
  {{ id:'cog', data:() => COG_SITES,
     name:'COG Sites', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,5, 3,8, 7,14],
       'circle-color':             '#ff1111',
       'circle-opacity':           0.92,
       'circle-stroke-width':      2.5,
       'circle-stroke-color':      '#ff6666',
       'circle-emissive-strength': 1,
     }}}},
  // Nuclear sites: large yellow, white stroke — hazard marker feel
  {{ id:'nuclear', data:() => NUCLEAR_SITES,
     name:'Nuclear Sites', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,5, 3,8, 7,14],
       'circle-color':             '#ffee00',
       'circle-opacity':           0.92,
       'circle-stroke-width':      2.5,
       'circle-stroke-color':      '#ffffff',
       'circle-emissive-strength': 1,
     }}}},
  // USO sites: cyan, medium-large
  {{ id:'uso', data:() => USO_SITES,
     name:'USO Sites', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,4, 3,6.5, 7,13],
       'circle-color':             '#00ddff',
       'circle-opacity':           0.9,
       'circle-stroke-width':      2,
       'circle-stroke-color':      '#88eeff',
       'circle-emissive-strength': 1,
     }}}},
  // Missing scientists: large white core + wide semi-transparent ring (simulates pulse)
  {{ id:'scientists', data:() => MISSING_SCIENTISTS,
     name:'Missing Scientists', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,6, 3,10, 7,18],
       'circle-color':             '#ffffff',
       'circle-opacity':           0.95,
       'circle-stroke-width':      5,
       'circle-stroke-color':      'rgba(255,255,255,0.3)',
       'circle-emissive-strength': 1,
     }}}},
  // Missing 411: crimson, medium
  {{ id:'missing411', data:() => MISSING_411,
     name:'Missing 411', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,2.5, 3,4.5, 7,9],
       'circle-color':             '#ff2244',
       'circle-opacity':           0.88,
       'circle-stroke-width':      1.2,
       'circle-stroke-color':      '#ff8888',
       'circle-emissive-strength': 1,
     }}}},
  // Cattle mutilations: warm brown
  {{ id:'cattle', data:() => CATTLE_SITES,
     name:'Cattle Mutilations', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,3, 3,5.5, 7,11],
       'circle-color':             '#cc6600',
       'circle-opacity':           0.88,
       'circle-stroke-width':      1.5,
       'circle-stroke-color':      '#ee9944',
       'circle-emissive-strength': 0.9,
     }}}},
  // Water anomalies: sky blue
  {{ id:'water', data:() => WATER_ANOMALY_SITES,
     name:'Water & Aquifers', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,3, 3,5.5, 7,11],
       'circle-color':             '#00bbff',
       'circle-opacity':           0.85,
       'circle-stroke-width':      1.5,
       'circle-stroke-color':      '#66ddff',
       'circle-emissive-strength': 0.9,
     }}}},
  // Window areas: burnt orange, medium-large
  {{ id:'windows', data:() => WINDOW_AREAS,
     name:'Window Areas', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,4, 3,7, 7,13],
       'circle-color':             '#ff9900',
       'circle-opacity':           0.9,
       'circle-stroke-width':      2,
       'circle-stroke-color':      '#ffcc66',
       'circle-emissive-strength': 1,
     }}}},
  // 33rd Parallel sites: red, medium
  {{ id:'p33pts', data:() => PARALLEL_33_SITES,
     name:'33rd Parallel', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,3, 3,5.5, 7,11],
       'circle-color':             '#ff2222',
       'circle-opacity':           0.88,
       'circle-stroke-width':      1.5,
       'circle-stroke-color':      '#ff8888',
       'circle-emissive-strength': 1,
     }}}},
];

function _toGeoJSON(items) {{
  return {{
    type: 'FeatureCollection',
    features: (items || []).filter(d => d.lat && (d.lon ?? d.lng)).map(d => ({{
      type: 'Feature',
      geometry: {{ type:'Point', coordinates:[+(d.lon ?? d.lng), +d.lat] }},
      properties: {{
        name:    d.name || d.location_label || d.location || '',
        date:    d.date    || '',
        summary: (d.summary || '').slice(0, 200),
        source:  d.source  || '',
        shape:   d.shape   || '',
      }},
    }})),
  }};
}}

function _mbPopup(props, color) {{
  const dt   = props.date    ? `<div style="color:#5a9;font-size:.78rem">📅 ${{props.date}}${{props.shape ? ' · ' + props.shape : ''}}</div>` : '';
  const body = props.summary ? `<div style="color:#8cc;font-size:.82rem;margin-top:4px">${{props.summary.slice(0,160)}}</div>` : '';
  return `<div style="font-family:'Rajdhani',sans-serif;max-width:260px">
    <div style="font-weight:700;color:${{color}};font-size:1rem">${{props.name || 'Unknown'}}</div>
    ${{dt}}${{body}}</div>`;
}}

function syncGlobeLayers() {{
  if (!mbMap || !mbLoaded) return;
  // UFO Sightings cluster layers
  const sVis = activeLayerNames.has('UFO Sightings') ? 'visible' : 'none';
  ['lyr-sightings-clusters','lyr-sightings-count','lyr-sightings-pts'].forEach(lid => {{
    if (mbMap.getLayer(lid)) mbMap.setLayoutProperty(lid, 'visibility', sVis);
  }});
  // Circle layers
  MB_LAYERS.forEach(({{ id, name }}) => {{
    const vis = activeLayerNames.has(name) ? 'visible' : 'none';
    if (mbMap.getLayer('lyr-' + id)) mbMap.setLayoutProperty('lyr-' + id, 'visibility', vis);
  }});
  // Heatmaps
  if (mbMap.getLayer('lyr-heat-all'))
    mbMap.setLayoutProperty('lyr-heat-all', 'visibility',
      activeLayerNames.has('Heat Map (All Sightings)') ? 'visible' : 'none');
  if (mbMap.getLayer('lyr-heat-abduct'))
    mbMap.setLayoutProperty('lyr-heat-abduct', 'visibility',
      activeLayerNames.has('Heat Map (Abductions Only)') ? 'visible' : 'none');
  // Line layers
  [['lyr-p33-line','33rd Parallel'],['lyr-ley','Ley Lines']].forEach(([lid, lname]) => {{
    if (mbMap.getLayer(lid))
      mbMap.setLayoutProperty(lid, 'visibility', activeLayerNames.has(lname) ? 'visible' : 'none');
  }});
}}

function updateGlobe() {{ syncGlobeLayers(); }}

function initMapboxGlobe() {{
  console.log('[Globe] initMapboxGlobe — mbMap:', mbMap ? 'exists' : 'null',
              '| token:', MAPBOX_TOKEN ? MAPBOX_TOKEN.slice(0,12)+'...' : 'MISSING');
  if (mbMap) {{ mbMap.resize(); syncGlobeLayers(); return; }}
  if (!MAPBOX_TOKEN) {{
    globeEl.innerHTML = '<div style="color:#f55;font-family:monospace;padding:40px;text-align:center">Mapbox token missing — add mapbox_token.txt and rebuild.</div>';
    return;
  }}
  mapboxgl.accessToken = MAPBOX_TOKEN;
  mbMap = new mapboxgl.Map({{
    container: 'globe-container',
    style:      'mapbox://styles/mapbox/dark-v11',
    projection: 'globe',
    zoom:       1.5,
    center:     [-98.35, 39.5],
    antialias:  true,
  }});
  mbMap.addControl(new mapboxgl.NavigationControl({{ visualizePitch:false }}), 'bottom-right');

  mbMap.on('load', () => {{
    console.log('[Globe] ✅ map loaded — adding layers');
    mbLoaded = true;
    mbMap.setFog({{
      color:            'rgb(4,13,20)',
      'high-color':     'rgb(0,50,15)',
      'horizon-blend':  0.04,
      'star-intensity': 0.9,
      'space-color':    'rgb(2,6,12)',
    }});

    // ── Heatmap — all sightings (added first so circles render on top) ─────────
    mbMap.addSource('src-heat-all', {{ type:'geojson', data:_toGeoJSON(ALL_SIGHTINGS) }});
    mbMap.addLayer({{
      id:'lyr-heat-all', type:'heatmap', source:'src-heat-all',
      layout:{{ visibility: activeLayerNames.has('Heat Map (All Sightings)') ? 'visible' : 'none' }},
      paint:{{
        'heatmap-weight':     ['interpolate',['linear'],['zoom'], 0,0.4, 9,1.5],
        'heatmap-intensity':  ['interpolate',['linear'],['zoom'], 2,0.3, 6,0.8, 9,2],
        'heatmap-radius':     ['interpolate',['linear'],['zoom'], 2,4, 4,8, 6,15, 8,25],
        'heatmap-opacity':    ['interpolate',['linear'],['zoom'], 2,0.7, 9,0.55],
        'heatmap-color': [
          'interpolate', ['linear'], ['heatmap-density'],
          0,   'rgba(0,0,0,0)',
          0.2, '#0000ff',
          0.4, '#9900ff',
          0.6, '#ff0000',
          0.8, '#ff6600',
          1.0, '#ffffff',
        ],
      }},
    }});

    // ── Heatmap — abductions only ──────────────────────────────────────────────
    mbMap.addSource('src-heat-abduct', {{ type:'geojson', data:_toGeoJSON(ABDUCTION_REPORTS) }});
    mbMap.addLayer({{
      id:'lyr-heat-abduct', type:'heatmap', source:'src-heat-abduct',
      layout:{{ visibility: activeLayerNames.has('Heat Map (Abductions Only)') ? 'visible' : 'none' }},
      paint:{{
        'heatmap-weight':     ['interpolate',['linear'],['zoom'], 0,0.8, 9,2.5],
        'heatmap-intensity':  ['interpolate',['linear'],['zoom'], 0,0.8, 9,2.5],
        'heatmap-radius':     ['interpolate',['linear'],['zoom'], 0,18,  3,28, 9,45],
        'heatmap-opacity':    ['interpolate',['linear'],['zoom'], 2,0.88, 9,0.65],
        'heatmap-color': [
          'interpolate', ['linear'], ['heatmap-density'],
          0,   'rgba(0,0,0,0)',
          0.2, '#1a0040',
          0.4, '#4400aa',
          0.6, '#9900ff',
          0.8, '#dd66ff',
          1.0, '#ffffff',
        ],
      }},
    }});

    // ── UFO Sightings — clustered ──────────────────────────────────────────────
    const sVis = activeLayerNames.has('UFO Sightings') ? 'visible' : 'none';
    mbMap.addSource('src-sightings', {{
      type: 'geojson',
      data: _toGeoJSON(ALL_SIGHTINGS),
      cluster: true,
      clusterMaxZoom: 14,
      clusterRadius: 50,
    }});
    // Cluster bubble — maxzoom matches clusterMaxZoom so clusters show all the way to zoom 14
    mbMap.addLayer({{
      id:'lyr-sightings-clusters', type:'circle', source:'src-sightings',
      filter:['has','point_count'],
      maxzoom: 14,
      layout:{{ visibility:sVis }},
      paint:{{
        'circle-color':['step',['get','point_count'],
          '#003a1a', 10, '#005522', 50, '#007a33', 200, '#00aa44'],
        'circle-radius':['step',['get','point_count'],
          13, 10,18, 50,24, 200,30],
        'circle-opacity': 0.88,
        'circle-stroke-width': 1.5,
        'circle-stroke-color': '#00ff44',
        'circle-emissive-strength': 1,
      }},
    }});
    // Cluster count label; maxzoom matches cluster bubble
    mbMap.addLayer({{
      id:'lyr-sightings-count', type:'symbol', source:'src-sightings',
      filter:['has','point_count'],
      maxzoom: 14,
      layout:{{
        visibility: sVis,
        'text-field': '{{point_count_abbreviated}}',
        'text-font':  ['DIN Offc Pro Medium','Arial Unicode MS Bold'],
        'text-size':  11,
      }},
      paint:{{
        'text-color':       '#00ff44',
        'text-halo-color':  '#000000',
        'text-halo-width':  1.2,
      }},
    }});
    // Individual points — always visible across all zoom levels
    mbMap.addLayer({{
      id:'lyr-sightings-pts', type:'circle', source:'src-sightings',
      filter:['!',['has','point_count']],
      minzoom: 0,
      maxzoom: 24,
      layout:{{ visibility:sVis }},
      paint:{{
        'circle-radius': ['interpolate',['linear'],['zoom'], 0,3, 5,6, 8,10, 12,14, 16,18],
        'circle-color':  ['match',['get','source'],'NUFORC','#00ff44','#ffaa00'],
        'circle-opacity': 1.0,
        'circle-stroke-width': ['match',['get','source'],'NUFORC',0,1.2],
        'circle-stroke-color': '#ffaa00',
        'circle-emissive-strength': 1,
      }},
    }});
    mbMap.on('click','lyr-sightings-pts', e => {{
      // Bail if a cluster bubble is also at this point — let the cluster handler win
      if (mbMap.queryRenderedFeatures(e.point, {{ layers:['lyr-sightings-clusters'] }}).length) return;
      new mapboxgl.Popup({{ className:'mb-popup', maxWidth:'300px' }})
        .setLngLat(e.lngLat)
        .setHTML(_mbPopup(e.features[0].properties, '#00ff44'))
        .addTo(mbMap);
    }});
    mbMap.on('mouseenter','lyr-sightings-pts',  () => {{ mbMap.getCanvas().style.cursor='pointer'; }});
    mbMap.on('mouseleave','lyr-sightings-pts',  () => {{ mbMap.getCanvas().style.cursor=''; }});

    // Click cluster bubble → zoom in to expand
    mbMap.on('click', 'lyr-sightings-clusters', function(e) {{
      const features = mbMap.queryRenderedFeatures(e.point, {{ layers: ['lyr-sightings-clusters'] }});
      if (!features.length) return;
      const clusterId = features[0].properties.cluster_id;
      mbMap.getSource('src-sightings').getClusterExpansionZoom(clusterId, function(err, zoom) {{
        if (err) return;
        mbMap.easeTo({{
          center: features[0].geometry.coordinates,
          zoom: zoom + 1,
          duration: 500,
        }});
      }});
    }});
    // Click count label — symbol layer sits on top of bubble and swallows the click
    mbMap.on('click', 'lyr-sightings-count', function(e) {{
      const features = mbMap.queryRenderedFeatures(e.point, {{ layers: ['lyr-sightings-clusters'] }});
      if (!features.length) return;
      const clusterId = features[0].properties.cluster_id;
      mbMap.getSource('src-sightings').getClusterExpansionZoom(clusterId, function(err, zoom) {{
        if (err) return;
        mbMap.easeTo({{
          center: features[0].geometry.coordinates,
          zoom: zoom + 1,
          duration: 500,
        }});
      }});
    }});
    mbMap.on('mouseenter', 'lyr-sightings-clusters', function() {{ mbMap.getCanvas().style.cursor = 'pointer'; }});
    mbMap.on('mouseleave', 'lyr-sightings-clusters', function() {{ mbMap.getCanvas().style.cursor = ''; }});
    mbMap.on('mouseenter', 'lyr-sightings-count',    function() {{ mbMap.getCanvas().style.cursor = 'pointer'; }});
    mbMap.on('mouseleave', 'lyr-sightings-count',    function() {{ mbMap.getCanvas().style.cursor = ''; }});
    // Zoom diagnostics — fires when globe zoom ≥ 10
    mbMap.on('zoom', () => {{
      const z = mbMap.getZoom();
      if (z >= 10) console.log('[Globe] zoom:', z.toFixed(2),
        '| pts visibility:', mbMap.getLayoutProperty('lyr-sightings-pts','visibility'),
        '| pts features:', mbMap.queryRenderedFeatures({{layers:['lyr-sightings-pts']}}).length);
    }});

    // ── Circle layers ──────────────────────────────────────────────────────────
    MB_LAYERS.forEach(cfg => {{
      const fc  = _toGeoJSON(cfg.data());
      const vis = activeLayerNames.has(cfg.name) ? 'visible' : 'none';
      mbMap.addSource('src-' + cfg.id, {{ type:'geojson', data:fc }});
      mbMap.addLayer({{
        id:'lyr-' + cfg.id, type:'circle', source:'src-' + cfg.id,
        layout:{{ visibility:vis }},
        paint: cfg.paint,
      }});
      mbMap.on('click', 'lyr-' + cfg.id, e => {{
        new mapboxgl.Popup({{ className:'mb-popup', maxWidth:'300px' }})
          .setLngLat(e.lngLat)
          .setHTML(_mbPopup(e.features[0].properties, cfg.paint['circle-color']))
          .addTo(mbMap);
      }});
      mbMap.on('mouseenter', 'lyr-' + cfg.id, () => {{ mbMap.getCanvas().style.cursor = 'pointer'; }});
      mbMap.on('mouseleave', 'lyr-' + cfg.id, () => {{ mbMap.getCanvas().style.cursor = ''; }});
    }});

    // ── 33rd Parallel line ─────────────────────────────────────────────────────
    mbMap.addSource('src-p33-line', {{
      type:'geojson',
      data:{{ type:'Feature', geometry:{{ type:'LineString', coordinates:[[-180,33],[180,33]] }} }},
    }});
    mbMap.addLayer({{
      id:'lyr-p33-line', type:'line', source:'src-p33-line',
      layout:{{ visibility: activeLayerNames.has('33rd Parallel') ? 'visible' : 'none' }},
      paint:{{ 'line-color':'#ff2222','line-width':1.5,'line-dasharray':[5,3],'line-opacity':0.8 }},
    }});

    // ── Ley lines ──────────────────────────────────────────────────────────────
    const leyFC = {{
      type:'FeatureCollection',
      features: LEY_LINES.map(l => ({{
        type:'Feature', properties:{{ color:l.color }},
        geometry:{{ type:'LineString', coordinates:l.points.map(([la,lo]) => [lo,la]) }},
      }})),
    }};
    mbMap.addSource('src-ley', {{ type:'geojson', data:leyFC }});
    mbMap.addLayer({{
      id:'lyr-ley', type:'line', source:'src-ley',
      layout:{{ visibility: activeLayerNames.has('Ley Lines') ? 'visible' : 'none' }},
      paint:{{ 'line-color':['get','color'],'line-width':1.5,'line-dasharray':[6,4],'line-opacity':0.75 }},
    }});

    syncGlobeLayers();
  }});
  mbMap.on('error', e => console.error('[Globe] ❌ Mapbox error:', e.error || e));
}}

// ── Mode switch ───────────────────────────────────────────
function setMode(mode) {{
  console.log('[Globe] setMode("' + mode + '") — was:', currentMode);
  currentMode = mode;
  const btn  = document.getElementById('mode-toggle');
  const hint = document.getElementById('globe-hint');
  const bar  = document.getElementById('controls');

  if (mode === 'globe') {{
    globeEl.style.display     = 'block';
    mapEl.style.opacity       = '0';
    mapEl.style.pointerEvents = 'none';
    btn.innerHTML             = '🌐&nbsp;GLOBE';
    btn.classList.add('active');
    hint.style.display        = 'block';
    bar.style.opacity         = '0.25';
    bar.style.pointerEvents   = 'none';
    console.log('[Globe] container display=block, queuing rAF for init');
    requestAnimationFrame(() => {{ console.log('[Globe] rAF fired → initMapboxGlobe'); initMapboxGlobe(); }});
  }} else {{
    globeEl.style.display     = 'none';
    mapEl.style.opacity       = '1';
    mapEl.style.pointerEvents = 'all';
    btn.innerHTML             = '🗺️&nbsp;2D MAP';
    btn.classList.remove('active');
    hint.style.display        = 'none';
    bar.style.opacity         = '';
    bar.style.pointerEvents   = '';
    setTimeout(() => {{
      map.invalidateSize({{ animate: false }});
      renderMarkers();
      loadVisible();
    }}, 350);
  }}
}}

document.getElementById('mode-toggle').addEventListener('click', () => {{
  console.log('[Globe] toggle clicked — currentMode:', currentMode);
  setMode(currentMode === 'globe' ? 'flat' : 'globe');
}});

// ── About panel ──────────────────────────────────────────────
document.getElementById('about-btn').addEventListener('click', () =>
  document.getElementById('about-overlay').classList.add('open'));
document.getElementById('about-close').addEventListener('click', () =>
  document.getElementById('about-overlay').classList.remove('open'));
document.getElementById('about-overlay').addEventListener('click', e => {{
  if (e.target === document.getElementById('about-overlay'))
    document.getElementById('about-overlay').classList.remove('open');
}});

// ── Mobile: hamburger to show/hide filter controls ────────
document.getElementById('controls-toggle').addEventListener('click', () => {{
  const bar = document.getElementById('controls');
  bar.classList.toggle('open');
}});

</script>
</body>
</html>"""

    with open(OUTPUT_MAP, "w", encoding="utf-8") as f:
        f.write(html)
    size_kb = os.path.getsize(OUTPUT_MAP) / 1024
    print(f"   ✅ Saved {OUTPUT_MAP}  ({size_kb:.0f} KB)")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    data = load_export()
    build_map(
        sightings           = data.get("sightings", []),
        abduction_sightings = data.get("abduction_reports", []),
        military_bases      = data.get("military_bases", []),
        cog_sites           = data.get("cog_sites", []),
        uso_sites           = data.get("uso_sites", []),
        missing_411              = data.get("missing_411", []),
        missing_scientists       = data.get("missing_scientists", []),
        parallel_33_sites        = data.get("parallel_33_sites", []),
        nuclear_sites            = data.get("nuclear_sites", []),
        cattle_mutilation_sites  = data.get("cattle_mutilation_sites", []),
        window_areas             = data.get("window_areas", []),
        ley_lines                = data.get("ley_lines", []),
        water_anomaly_sites      = data.get("water_anomaly_sites", []),
        mufon_reports            = data.get("mufon_reports", []),
        local_news               = data.get("local_news", []),
    )
    print(f"\n✅  Done — open {OUTPUT_MAP} in your browser.")
