#!/usr/bin/env python3
"""audit_layers.py — Count records in every data layer from ufo_data_export.json
and from hardcoded datasets in build_map.py."""

import json
import re
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# ── 1. ufo_data_export.json ───────────────────────────────────────────────────
with open(os.path.join(BASE, "ufo_data_export.json"), encoding="utf-8") as f:
    data = json.load(f)

exported_at = data.get("exported_at", "unknown")

sightings          = data.get("sightings",               [])
nuforc_recent      = data.get("nuforc_recent",            [])
abductions         = data.get("abduction_reports",        [])
mufon              = data.get("mufon_reports",            [])
local_news         = data.get("local_news",               [])
seismic            = data.get("seismic_activity",         [])
humanoid           = data.get("humanoid_encounters",      [])
asrs               = data.get("asrs_reports",             [])
asa                = data.get("asa_reports",              [])
reddit_missing     = data.get("reddit_missing",           [])
military_bases     = data.get("military_bases",           [])
cog_sites          = data.get("cog_sites",                [])
uso_sites          = data.get("uso_sites",                [])
missing_411        = data.get("missing_411",              [])
missing_scientists = data.get("missing_scientists",       [])
parallel_33        = data.get("parallel_33_sites",        [])
nuclear_sites      = data.get("nuclear_sites",            [])
cattle             = data.get("cattle_mutilation_sites",  [])
window_areas       = data.get("window_areas",             [])
ley_lines          = data.get("ley_lines",                [])
water              = data.get("water_anomaly_sites",      [])

nuforc_count = sum(1 for s in sightings if s.get("source") == "NUFORC")
reddit_count = sum(1 for s in sightings if s.get("source") != "NUFORC")

# ── 2. Hardcoded datasets in build_map.py ─────────────────────────────────────
bmp = os.path.join(BASE, "build_map.py")
with open(bmp, encoding="utf-8") as f:
    src = f.read()

def count_list_items(varname, source):
    """Rough count of dicts inside a Python list literal assigned to varname."""
    m = re.search(rf'{varname}\s*=\s*\[', source)
    if not m:
        return None
    start = m.end()
    depth = 1
    i = start
    while i < len(source) and depth > 0:
        if source[i] == '[':
            depth += 1
        elif source[i] == ']':
            depth -= 1
        i += 1
    block = source[start:i-1]
    return len(re.findall(r'\{[^{}]*"lat"', block))

power_count   = count_list_items("power_sites",       src)
skulls_count  = count_list_items("elongated_skulls",  src)
spheres_count = count_list_items("anomalous_spheres", src)
mummies_count = count_list_items("alien_mummies",     src)

# ── Report ────────────────────────────────────────────────────────────────────
SEP = "─" * 56

def row(label, count, source_tag="JSON"):
    status = "✅" if count > 0 else "❌"
    print(f"  {status}  {label:<36} {count:>6,}  [{source_tag}]")

print()
print("╔" + "═"*56 + "╗")
print(f"║  WEAVING SPIDERS — Layer Audit  (export: {exported_at[:10]})  ")
print("╚" + "═"*56 + "╝")
print()

print(f"  {'LAYER':<36} {'COUNT':>6}  [SOURCE]")
print(SEP)

print("  🛸  SIGHTINGS")
row("NUFORC (historical CSV)",       nuforc_count)
row("Reddit UFO sightings",          reddit_count)
row("NUFORC Recent (live scrape)",   len(nuforc_recent))
row("MUFON Reports",                 len(mufon))
row("Local News",                    len(local_news))
print()

print("  ✈️   PILOT REPORTS")
row("NASA ASRS Pilot Reports",       len(asrs))
row("ASA Reports (@SafeAerospace)",  len(asa))
print()

print("  👤  PEOPLE")
row("Missing Scientists",            len(missing_scientists))
row("Missing 411",                   len(missing_411))
row("Reddit Missing Reports",        len(reddit_missing))
print()

print("  🏛️   INFRASTRUCTURE")
row("Military Bases",                len(military_bases))
row("COG Sites",                     len(cog_sites))
row("Nuclear Sites",                 len(nuclear_sites))
row("USO Sites",                     len(uso_sites))
print()

print("  🦉  POWER")
row("Power & Secrecy Sites",         power_count or 0, "hardcoded")
print()

print("  🌊  ENVIRONMENT")
row("Seismic Activity (USGS)",       len(seismic))
row("Water & Aquifers",              len(water))
row("Cattle Mutilations",            len(cattle))
row("Window Areas",                  len(window_areas))
print()

print("  🔺  PATTERNS")
row("Ley Lines",                     len(ley_lines))
row("33rd Parallel",                 len(parallel_33))
print()

print("  🏺  ANOMALOUS ARTIFACTS")
row("Humanoid Encounters",           len(humanoid))
row("Elongated Skulls",              skulls_count or 0, "hardcoded")
row("Anomalous Spheres",             spheres_count or 0, "hardcoded")
row("Alien Mummies",                 mummies_count or 0, "hardcoded")
print()

print(SEP)
total = (nuforc_count + reddit_count + len(nuforc_recent) + len(mufon) +
         len(local_news) + len(asrs) + len(asa) + len(missing_scientists) +
         len(missing_411) + len(reddit_missing) + len(military_bases) +
         len(cog_sites) + len(nuclear_sites) + len(uso_sites) +
         (power_count or 0) + len(seismic) + len(water) + len(cattle) +
         len(window_areas) + len(ley_lines) + len(parallel_33) +
         len(humanoid) + (skulls_count or 0) + (spheres_count or 0) +
         (mummies_count or 0) + len(abductions))
print(f"  {'TOTAL RECORDS (all layers):':<36} {total:>6,}")
print()

# ── Zero-count recommendations ────────────────────────────────────────────────
zeros = []
checks = [
    ("Reddit UFO sightings",         reddit_count,         "Run fetch_data.py with ANTHROPIC_API_KEY set"),
    ("MUFON Reports",                len(mufon),           "mufonlive.com DNS fails — remove layer or replace with hardcoded notable cases"),
    ("NASA ASRS Pilot Reports",      len(asrs),            "ASRS search form requires POST/session — replace scraper or add hardcoded notable reports"),
    ("Reddit Missing Reports",       len(reddit_missing),  "No API key set — will populate when fetch_data.py runs with key"),
    ("Humanoid Encounters",          len(humanoid),        "No API key set — will populate when fetch_data.py runs with key"),
]
for label, count, rec in checks:
    if count == 0:
        zeros.append((label, rec))

if zeros:
    print("  ⚠️   ZERO-COUNT LAYERS — Recommendations:")
    print(SEP)
    for label, rec in zeros:
        print(f"  ❌  {label}")
        print(f"      → {rec}")
        print()
