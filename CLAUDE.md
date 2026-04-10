# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Pure-Python (stdlib-only, no `requirements.txt`) pipeline that aggregates UFO/UAP sighting data from several public sources and renders it as a single standalone `index.html` file containing a Leaflet 2D map and a Mapbox GL 3D globe. All Python sources live in `UFO-MAP/`.

## Commands

All commands run from `UFO-MAP/` (the Python scripts use `os.path.dirname(__file__)` for file paths, so running them from any cwd works, but data files are written next to the scripts):

```bash
cd UFO-MAP

# Full pipeline: fetch from all network sources + local CSV, write
# ufo_data_export.json, then subprocess into build_map.py to render index.html
python3 fetch_data.py

# Offline-only export: rebuild ufo_data_export.json from the local NUFORC CSV
# and the static constants (no network calls)
python3 export_data.py

# Rebuild only the HTML map from an existing ufo_data_export.json (instant,
# no network, no CSV parsing)
python3 build_map.py

# Probe scripts (NOT unit tests — they hit live external endpoints and print
# status codes / response previews for manual inspection)
python3 test_sources.py   # MUFON, Google News RSS, NUFORC web reports
python3 test_cia.py       # Arctic Shift API, CIA CREST reading room
```

There are no unit tests, no linter config, no package manager, and no build system. Dependencies are stdlib only (`urllib.request`, `csv`, `json`, `html.parser`, `xml.etree`). Python 3 is assumed.

## Pipeline architecture

The data flow is deliberately split into three stages so that iteration on the HTML/JS is fast and network-free:

```
  Network sources ─┐
  NUFORC CSV ──────┼──► fetch_data.py ──► ufo_data_export.json ──► build_map.py ──► index.html
  constants.py ────┘         │                                          ▲
                             ▼                                          │
                     (auto-subprocesses build_map.py at the end) ───────┘

  NUFORC CSV ──┐
  constants.py ┴──► export_data.py ──► ufo_data_export.json   (offline subset)
```

- **`constants.py`** is the single source of truth for all static "known site" datasets: `MILITARY_BASES`, `COG_SITES`, `USO_SITES`, `MISSING_411_SITES`, `MISSING_SCIENTISTS`, `PARALLEL_33_SITES`, `NUCLEAR_SITES`, `CATTLE_MUTILATION_SITES`, `WINDOW_AREAS`, `LEY_LINES`, `WATER_ANOMALY_SITES`, plus `NUFORC_CSV` path, `NUFORC_FIELDS` column ordering, and `ABDUCTION_KEYWORDS`. Imported by `fetch_data.py`, `export_data.py`, and `build_map.py`. Edit data here and all pipelines pick it up. **Also runs a tiny stdlib `.env` loader at import time** (`_load_dotenv`) that reads `.env` from the repo root and populates `os.environ.setdefault` — this is why every script that needs env vars must `import constants` (even just for the side effect, as `build_map.py` does).

- **`fetch_data.py`** is the canonical ingestion script. Sources it pulls:
  1. Local NUFORC CSV bulk load (`load_nuforc`, capped at 5000 rows by default)
  2. NUFORC abduction filter — scans CSV `comments` against `ABDUCTION_KEYWORDS`
  3. NUFORC "recent" web reports (`fetch_nuforc_recent`) with a local-CSV fallback sorted newest-first when the web endpoint fails
  4. Reddit r/ufos + r/UFOs via the public JSON API and Arctic Shift (`fetch_arctic_shift_reddit`), with a browser User-Agent — location hints are extracted from post titles via regex against `STATE_COORDS` + `_COUNTRY_COORDS` and jittered with `random.uniform` since Reddit has no coordinates
  5. MUFON cases scraped from `mufonlive.com` (`fetch_mufon_cases`) — may be unavailable
  6. Google News RSS (`fetch_local_news`) — parses `<item>` entries, extracts state via regex, geocodes via `STATE_COORDS` with jitter, dedupes by `(round(lat,1), round(lon,1), date[:7])`

  When run as `__main__` it writes `ufo_data_export.json` and then subprocesses `python3 build_map.py` automatically.

- **`export_data.py`** is a minimal offline alternative used when the network is unavailable or for fast iteration. It only loads NUFORC CSV + abductions and re-exports the static constants. Imports from `constants.py`.

- **`build_map.py`** is a pure renderer: reads `ufo_data_export.json`, serializes each layer to a `*_json` string via `json.dumps`, and interpolates them into a single giant f-string that contains the full HTML + CSS + JS of the output page. All browser-side logic (layer toggles, clustering, heatmap, globe mode, popups) lives inside that template. The Mapbox GL globe view is initialized lazily on first `setMode('globe')` from a token read out of `os.environ['MAPBOX_TOKEN']` (loaded from `.env` via `constants.py`'s `_load_dotenv`), with a fallback to `mapbox_token.txt` for back-compat. If neither is set, globe mode is silently disabled but 2D still works. **Note:** `build_map.py` defines its own local `OUTPUT_MAP = "index.html"` at the top of the file, overriding `constants.OUTPUT_MAP = "ufo_map.html"` — the canonical output filename is `index.html`.

## Data files

- `UFO-MAP/nuforc_test.csv` (~14 MB) — **tracked input**. Bulk NUFORC sightings database; fields are positional and declared in `constants.NUFORC_FIELDS` (the CSV has no header row, so `csv.DictReader` is given explicit `fieldnames`). Whitelisted from the pre-commit large-file hook.
- `UFO-MAP/ufo_data_export.json` (~2.5 MB) — **git-ignored, generated**. The intermediate artifact written by `fetch_data.py` / `export_data.py` and read by `build_map.py`.
- `UFO-MAP/reddit_cache.json` — **git-ignored, generated**. Cache of Reddit API responses keyed by subreddit.
- `UFO-MAP/index.html` (~1.8 MB) — **git-ignored, generated**. The output map. Rebuild with `python3 build_map.py`, don't hand-edit.
- `UFO-MAP/mapbox_token.txt` — **git-ignored**. Legacy local-dev fallback for the Mapbox token; prefer setting `MAPBOX_TOKEN` in `.env` instead.
- `.env` (repo root) — **git-ignored**. Contains real `ANTHROPIC_API_KEY` and `MAPBOX_TOKEN` values. Loaded automatically by `constants.py`. Template lives at `.env.example`.

## Dev tooling

- **Pre-commit** is configured at `.pre-commit-config.yaml` (gitleaks for secret scanning, `check-added-large-files --maxkb=500` with `nuforc_test.csv` excluded, plus standard hygiene hooks). Install once with `pre-commit install` after `pip install -r requirements-dev.txt`. Hooks run on every `git commit`.
- **CI** is at `.github/workflows/ci.yml` and just runs `pre-commit run --all-files` on PRs and pushes to `main`. It does NOT run the data pipeline and needs no GitHub Actions secrets.
- Runtime is **stdlib-only** (Python 3.11+). `requirements-dev.txt` contains only `pre-commit`.

## Git workflow

- **Never commit directly to `main`.** Always work on a topic branch and open a PR — even for tiny changes. This makes the change reviewable and lets CI run before the change lands.
- **Branch naming convention** — every branch must start with one of these prefixes followed by a short kebab-case description:
  - `feat/` — new user-facing functionality (e.g. `feat/abduction-heatmap`)
  - `fix/` — bug fix (e.g. `fix/nuforc-csv-encoding`)
  - `chore/` — tooling, dependencies, CI, repo housekeeping (e.g. `chore/setup-best-practices`)
  - `docs/` — documentation only, no code changes (e.g. `docs/clarify-env-setup`)
  - `refactor/` — restructuring without behaviour change (e.g. `refactor/extract-geocoder`)
  - `ci/` — CI/CD pipeline changes (e.g. `ci/add-nightly-rebuild`)
  - `test/` — adding or updating tests (e.g. `test/cover-reddit-parser`)
- **Commit messages** should follow the same prefix style on the first line (`feat: …`, `chore: …`) so the history is grep-able. Wrap the body at ~72 chars and explain the *why*, not the *what* — `git diff` already shows the what.
- **PR titles** mirror the commit-message convention. Keep them under ~70 chars. Put detail in the PR body (Summary + Test plan sections).

## Conventions

- All frontend code (Leaflet, MarkerCluster, Leaflet.heat, Mapbox GL, Rajdhani/Share Tech Mono fonts) is loaded from CDNs inside the generated HTML — there is no build step, no bundler, and no `node_modules`.
- Because `build_map.py` uses a Python f-string for the entire HTML template, every literal `{` and `}` in the JS/CSS must be doubled (`{{` / `}}`). When editing the template, do NOT introduce single `{`/`}` unless you intend an f-string interpolation.
- Reddit and Google-News sightings don't have real coordinates — they are jittered around `STATE_COORDS` / `_COUNTRY_COORDS` centroids. This is intentional; don't "fix" it by dropping records without coordinates.
- Network fetches use a spoofed Chrome desktop `User-Agent` (`BROWSER_HEADERS` in `fetch_data.py`, `HEADERS` in the test scripts). Several endpoints (Reddit, MUFON) return 403 without this.
- Failures in individual data sources are caught and logged but never raise — a partial export is always preferable to no export.

## Security history

The legacy `UFO-MAP/ufo_map_1.py` (deleted in the best-practices cleanup) previously contained a hardcoded `ANTHROPIC_API_KEY`. The leaked value is **still present in commit `021fc3b` ("Add files via upload")** of git history because the cleanup did not force-push a history rewrite. The owner of the repo (Lucas / `eagletonart`) needs to rotate the key at https://console.anthropic.com/settings/keys; until then, treat the value as compromised. Once rotated, the historical leak is harmless but the commit can optionally be rewritten with `git filter-repo --replace-text` if maximum scrubbing is desired.

The Mapbox token is a *public* client-side token that's intentionally embedded in the generated `index.html`. Restrict it to allowed URLs in the Mapbox dashboard rather than treating it as a secret.
