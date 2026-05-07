#!/usr/bin/env python3
"""
Offline export: rebuild ufo_data_export.json from the local NUFORC CSV
and all static constants. No network calls. Fast iteration path.
"""

import json
import csv
import os
from datetime import datetime

from constants import (
    NUFORC_CSV, NUFORC_FIELDS, ABDUCTION_KEYWORDS, EXPORT_FILE,
    MILITARY_BASES, COG_SITES, USO_SITES,
    MISSING_411_SITES, MISSING_SCIENTISTS, PARALLEL_33_SITES,
    NUCLEAR_SITES, CATTLE_MUTILATION_SITES, WINDOW_AREAS,
    LEY_LINES, WATER_ANOMALY_SITES,
)


def load_nuforc(max_records=5000):
    print(f"📡 Loading NUFORC sightings (up to {max_records})...")
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
                    "source":   "NUFORC",
                    "lat":      lat,
                    "lon":      lon,
                    "date":     row.get("datetime", ""),
                    "city":     city,
                    "state":    state,
                    "country":  row.get("country", ""),
                    "shape":    row.get("shape", "unknown"),
                    "duration": row.get("duration_seconds", ""),
                    "summary":  row.get("comments", "")[:300],
                    "location": f"{city}, {state}".strip(", "),
                })
            except (ValueError, KeyError):
                continue
    print(f"   ✅ {len(sightings)} sightings loaded")
    return sightings


def load_nuforc_abductions():
    print("👤 Mining NUFORC for abduction reports...")
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
                    "source":   "NUFORC Abduction",
                    "lat":      lat,
                    "lon":      lon,
                    "date":     row.get("datetime", ""),
                    "city":     city,
                    "state":    state,
                    "country":  row.get("country", ""),
                    "shape":    row.get("shape", "unknown"),
                    "summary":  row.get("comments", "")[:300],
                    "location": f"{city}, {state}".strip(", "),
                })
            except (ValueError, KeyError):
                continue
    print(f"   ✅ {len(sightings)} abduction reports found")
    return sightings


def export(output_path=None):
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), EXPORT_FILE)

    sightings  = load_nuforc(max_records=5000)
    abductions = load_nuforc_abductions()

    data = {
        "exported_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "counts": {
            "sightings":               len(sightings),
            "abduction_reports":       len(abductions),
            "military_bases":          len(MILITARY_BASES),
            "cog_sites":               len(COG_SITES),
            "uso_sites":               len(USO_SITES),
            "missing_411":             len(MISSING_411_SITES),
            "missing_scientists":      len(MISSING_SCIENTISTS),
            "parallel_33_sites":       len(PARALLEL_33_SITES),
            "nuclear_sites":           len(NUCLEAR_SITES),
            "cattle_mutilation_sites": len(CATTLE_MUTILATION_SITES),
            "window_areas":            len(WINDOW_AREAS),
            "ley_lines":               len(LEY_LINES),
            "water_anomaly_sites":     len(WATER_ANOMALY_SITES),
        },
        "sightings":               sightings,
        "abduction_reports":       abductions,
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
        # network-sourced layers: empty in offline mode
        "nuforc_recent":           [],
        "local_news":              [],
        "seismic_activity":        [],
        "humanoid_encounters":     [],
        "asrs_reports":            [],
        "asa_reports":             [],
        "reddit_missing":          [],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    size_mb = os.path.getsize(output_path) / 1_048_576
    total   = sum(data["counts"].values())
    print(f"\n✅ Exported {total} total records to {output_path} ({size_mb:.1f} MB)")
    for k, v in data["counts"].items():
        print(f"   {k}: {v}")


if __name__ == "__main__":
    export()
