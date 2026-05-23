#!/usr/bin/env python3
"""
download_pursue_videos.py — Extract individual MP4s from the PURSUE Release 02
video zip using HTTP range requests (no full zip download needed).

The CloudFront URL is publicly accessible. We:
  1. Read the ZIP central directory (last ~1 MB)
  2. For each MP4, fetch its local file header to find exact data start
  3. Download and deflate-decompress the compressed payload
  4. Write to pursue_videos/<filename>
  5. Write pursue_videos.json with metadata catalog

Usage:
  python3 download_pursue_videos.py              # download all
  python3 download_pursue_videos.py --list       # list files only (no download)
  python3 download_pursue_videos.py --id 111719709  # download one specific DOD ID
"""

import os, sys, zlib, struct, json, time, urllib.request
from pathlib import Path

ZIP_URL   = "https://d34w7g4gy10iej.cloudfront.net/uap052226.zip"
OUT_DIR   = Path(__file__).parent / "pursue_videos"
META_FILE = Path(__file__).parent / "pursue_videos.json"

OUT_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "*/*",
}


# ── HTTP helpers ─────────────────────────────────────────────────────────────

def http_range(url, start, end):
    """Fetch bytes [start, end] inclusive from url."""
    req = urllib.request.Request(url, headers={
        **HEADERS, "Range": f"bytes={start}-{end}"
    })
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def get_zip_size():
    req = urllib.request.Request(ZIP_URL, headers=HEADERS, method="HEAD")
    with urllib.request.urlopen(req, timeout=15) as r:
        return int(r.headers["Content-Length"])


# ── ZIP parsing ───────────────────────────────────────────────────────────────

def read_central_directory(zip_size):
    """Return list of dicts: {name, comp_size, uncomp_size, local_header_offset, method}.
    Handles both standard ZIP and ZIP64 (files >4 GB).
    """
    # Fetch last 1 MB to capture EOCD + ZIP64 records + central directory
    chunk_size = min(1_048_576, zip_size)
    chunk = http_range(ZIP_URL, zip_size - chunk_size, zip_size - 1)

    # Find End-of-Central-Directory signature
    eocd_off = chunk.rfind(b"PK\x05\x06")
    if eocd_off == -1:
        raise RuntimeError("EOCD not found — try increasing chunk_size")

    # --- ZIP64 support ---
    # Check for ZIP64 EOCD record (PK\x06\x06) before the regular EOCD
    zip64_eocd_off = chunk.rfind(b"PK\x06\x06", 0, eocd_off)
    if zip64_eocd_off != -1:
        # ZIP64: read 8-byte fields
        total_entries = struct.unpack_from("<Q", chunk, zip64_eocd_off + 32)[0]
        cd_size       = struct.unpack_from("<Q", chunk, zip64_eocd_off + 40)[0]
        cd_offset     = struct.unpack_from("<Q", chunk, zip64_eocd_off + 48)[0]
    else:
        # Standard ZIP
        eocd = chunk[eocd_off:]
        total_entries = struct.unpack_from("<H", eocd, 10)[0]
        cd_size       = struct.unpack_from("<I", eocd, 12)[0]
        cd_offset     = struct.unpack_from("<I", eocd, 16)[0]

    # Fetch central directory (may already be in chunk, or need a separate fetch)
    chunk_file_offset = zip_size - chunk_size   # byte position of chunk[0] in the file
    if cd_offset >= chunk_file_offset:
        offset_in_chunk = cd_offset - chunk_file_offset
        cd_data = chunk[offset_in_chunk: offset_in_chunk + cd_size]
    else:
        cd_data = http_range(ZIP_URL, cd_offset, cd_offset + cd_size - 1)

    entries = []
    pos = 0
    while pos < len(cd_data) - 4:
        sig = cd_data[pos:pos+4]
        if sig != b"PK\x01\x02":
            break
        method        = struct.unpack_from("<H", cd_data, pos + 10)[0]
        comp_size     = struct.unpack_from("<I", cd_data, pos + 20)[0]
        uncomp_size   = struct.unpack_from("<I", cd_data, pos + 24)[0]
        fname_len     = struct.unpack_from("<H", cd_data, pos + 28)[0]
        extra_len     = struct.unpack_from("<H", cd_data, pos + 30)[0]
        comment_len   = struct.unpack_from("<H", cd_data, pos + 32)[0]
        lh_offset     = struct.unpack_from("<I", cd_data, pos + 42)[0]
        fname         = cd_data[pos+46: pos+46+fname_len].decode("utf-8", errors="replace")
        entries.append({
            "name": fname,
            "comp_size": comp_size,
            "uncomp_size": uncomp_size,
            "local_header_offset": lh_offset,
            "method": method,
        })
        pos += 46 + fname_len + extra_len + comment_len

    return entries


def get_data_start(lh_offset):
    """Read local file header at lh_offset, return offset of compressed data."""
    lh = http_range(ZIP_URL, lh_offset, lh_offset + 29)
    fname_len = struct.unpack_from("<H", lh, 26)[0]
    extra_len = struct.unpack_from("<H", lh, 28)[0]
    return lh_offset + 30 + fname_len + extra_len


def download_entry(entry, out_path):
    """Download and decompress a single ZIP entry to out_path."""
    data_start = get_data_start(entry["local_header_offset"])
    data_end   = data_start + entry["comp_size"] - 1
    compressed = http_range(ZIP_URL, data_start, data_end)

    if entry["method"] == 0:          # stored (no compression)
        raw = compressed
    elif entry["method"] == 8:        # deflated
        raw = zlib.decompress(compressed, -15)  # raw deflate (no header)
    else:
        raise ValueError(f"Unsupported compression method {entry['method']}")

    with open(out_path, "wb") as f:
        f.write(raw)


# ── DOW document cross-reference ─────────────────────────────────────────────

def build_dow_location_map():
    """
    Build a rough map of DOW document locations from pursue_intelligence.json.
    Returns dict keyed by short label e.g. 'arabian gulf' → {lat, lon, label}.
    """
    intel_path = Path(__file__).parent / "pursue_intelligence.json"
    if not intel_path.exists():
        return {}

    with open(intel_path, encoding="utf-8") as f:
        intel = json.load(f)

    # documents is a list of dicts with pdf_file as key
    docs_list = intel.get("documents", [])
    if isinstance(docs_list, dict):
        docs_list = list(docs_list.values())

    LOC_COORDS = {
        "arabian gulf":       (26.0, 53.5),
        "persian gulf":       (26.5, 52.5),
        "strait of hormuz":   (26.6, 56.3),
        "gulf of aden":       (12.0, 45.0),
        "arabian sea":        (17.0, 65.0),
        "middle east":        (28.0, 43.0),
        "iraq":               (33.2, 43.7),
        "syria":              (35.0, 38.5),
        "mediterranean sea":  (36.0, 18.0),
        "greece":             (39.0, 22.0),
        "united arab emirates": (24.4, 54.4),
        "east china sea":     (29.0, 124.0),
        "japan":              (36.0, 138.0),
        "djibouti":           (11.8, 42.6),
        "southern united states": (32.0, -96.0),
        "indopacom":          (20.0, 170.0),
        "pacific":            (25.0, -150.0),
        "western us":         (38.5, -115.0),
    }

    docs = {}
    for doc in docs_list:
        pdf_file = doc.get("pdf_file", "")
        if "dow-uap-d" not in pdf_file.lower():
            continue
        stem = pdf_file.lower().replace(".pdf", "")
        # Derive location from filename
        loc = None
        stem_l = stem.lower()
        for key, coords in LOC_COORDS.items():
            if key in stem_l:
                loc = {"lat": coords[0], "lon": coords[1], "label": key.title()}
                break
        # Also check AI-extracted locations
        if not loc:
            ai_locs = doc.get("analysis", {}).get("locations", [])
            if ai_locs:
                name = ai_locs[0].get("name", "")
                name_l = name.lower()
                for key, coords in LOC_COORDS.items():
                    if key in name_l:
                        loc = {"lat": coords[0], "lon": coords[1], "label": name}
                        break
        docs[stem] = {
            "stem": stem,
            "pdf_file": pdf_file,
            "title": doc.get("title", stem),
            "location": loc,
            "summary": doc.get("analysis", {}).get("summary", ""),
        }
    return docs


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    list_only = "--list" in sys.argv
    filter_id = None
    for arg in sys.argv[1:]:
        if arg.startswith("--id="):
            filter_id = arg.split("=")[1]
        elif arg == "--id" and sys.argv.index(arg) + 1 < len(sys.argv):
            filter_id = sys.argv[sys.argv.index(arg) + 1]

    print("📡  Reading ZIP central directory…")
    zip_size = get_zip_size()
    print(f"    ZIP size: {zip_size / 1e9:.2f} GB")
    entries = read_central_directory(zip_size)

    # Filter to MP4s only, skip macOS metadata
    videos = [e for e in entries
              if e["name"].lower().endswith(".mp4")
              and not e["name"].startswith("__MACOSX")]
    print(f"    Found {len(videos)} video files")

    if filter_id:
        videos = [v for v in videos if filter_id in v["name"]]
        print(f"    Filtered to {len(videos)} matching --id={filter_id}")

    # Print manifest
    print(f"\n{'FILE':<65} {'SIZE_MB':>8}  {'UNCOMP_MB':>9}")
    print("─" * 85)
    for v in videos:
        print(f"  {v['name']:<63} {v['comp_size']//1024//1024:>7} MB  {v['uncomp_size']//1024//1024:>8} MB")

    if list_only:
        print(f"\n✅  Listed {len(videos)} videos (no download)")
        return

    # Build DOW location cross-reference
    dow_locs = build_dow_location_map()

    # Download loop
    catalog = []
    total = len(videos)
    for i, entry in enumerate(videos, 1):
        fname = Path(entry["name"]).name
        out_path = OUT_DIR / fname

        # Extract DOD ID from filename
        dod_id = fname.replace("video_2605_DOD_", "").replace("_DOD_" + fname.split("_DOD_")[-1], "")
        # Cleaner: grab the numeric part
        import re
        m = re.search(r"DOD_(\d+)", fname)
        dod_id = m.group(1) if m else fname

        size_mb = entry["uncomp_size"] / 1024 / 1024

        if out_path.exists() and out_path.stat().st_size == entry["uncomp_size"]:
            print(f"[{i:2d}/{total}] ✓ skip  {fname}  ({size_mb:.0f} MB)")
        else:
            print(f"[{i:2d}/{total}] ⬇  {fname}  ({size_mb:.0f} MB)…", end="", flush=True)
            t0 = time.time()
            try:
                download_entry(entry, out_path)
                elapsed = time.time() - t0
                actual_mb = out_path.stat().st_size / 1024 / 1024
                print(f" ✅  {actual_mb:.0f} MB in {elapsed:.1f}s")
            except Exception as e:
                print(f" ❌  {e}")
                if out_path.exists():
                    out_path.unlink()
                catalog.append({"dod_id": dod_id, "filename": fname,
                                 "size_mb": round(size_mb, 1), "error": str(e)})
                continue

        catalog.append({
            "dod_id": dod_id,
            "filename": fname,
            "size_mb": round(size_mb, 1),
            "local_path": str(out_path),
            "source_zip": ZIP_URL,
        })
        time.sleep(0.1)

    # Save catalog
    META_FILE.write_text(json.dumps({
        "release": "2026-05",
        "source_zip": ZIP_URL,
        "total_videos": len(catalog),
        "videos": catalog,
    }, indent=2), encoding="utf-8")
    print(f"\n✅  pursue_videos.json written  ({len(catalog)} videos)")
    print(f"    Videos saved to {OUT_DIR}/")


if __name__ == "__main__":
    main()
