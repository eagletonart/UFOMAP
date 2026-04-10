# UFO-MAP

Aggregates UFO/UAP sighting data from public sources (NUFORC database, Reddit
r/ufos, MUFON, Google News) and renders an interactive map as a single
standalone `index.html` file with both a 2D Leaflet view and a 3D Mapbox GL
globe view.

The Python pipeline is **stdlib-only at runtime** — there are no `pip`
packages to install just to generate the map. Pre-commit + GitHub Actions are
the only dev-time dependencies.

## Quick start (first time setup)

You need:
- **Python 3.11+** (check with `python3 --version`)
- **git** (check with `git --version`)
- A free **Mapbox account** if you want the 3D globe (the 2D map works without)
- *(Optional)* an **Anthropic API key** if you want Claude-powered location
  extraction in `fetch_data.py`. The pipeline runs fine without it.

```bash
# 1. Clone the repo
git clone https://github.com/eagletonart/UFOMAP.git
cd UFOMAP

# 2. Copy the env template and fill in your tokens
cp .env.example .env
# Open .env in your editor and paste in real values for ANTHROPIC_API_KEY
# and MAPBOX_TOKEN. Both are optional — leave blank to skip those features.

# 3. (Recommended) install the dev tools so commits get checked automatically
python3 -m pip install -r requirements-dev.txt
pre-commit install

# 4. Generate the map
cd UFO-MAP
python3 fetch_data.py    # full pipeline: fetch every source + build map
# OR
python3 build_map.py     # rebuild only from existing ufo_data_export.json
```

Open `UFO-MAP/index.html` in a browser to view the map.

## What's where

```
UFOMAP/
├── README.md             ← you are here
├── CLAUDE.md             ← guidance for Claude Code sessions
├── .env.example          ← template for local env vars (copy → .env)
├── .gitignore            ← ignores .env, secrets, and generated artifacts
├── .pre-commit-config.yaml
├── requirements-dev.txt  ← `pre-commit` only — runtime is stdlib
├── .github/
│   └── workflows/
│       └── ci.yml        ← runs pre-commit on every PR
└── UFO-MAP/
    ├── constants.py      ← static data + .env loader (single source of truth)
    ├── fetch_data.py     ← main pipeline: fetch all sources → JSON → map
    ├── export_data.py    ← offline subset (no network calls)
    ├── build_map.py      ← renders index.html from ufo_data_export.json
    ├── test_sources.py   ← probe scripts (NOT unit tests — hit live URLs)
    ├── test_cia.py       ← ditto
    ├── nuforc_test.csv   ← bulk NUFORC sightings dataset (input, ~14 MB)
    ├── ufo_data_export.json  ← generated, git-ignored
    ├── reddit_cache.json     ← generated, git-ignored
    └── index.html            ← generated, git-ignored
```

## Common commands

| Command | What it does |
| --- | --- |
| `python3 UFO-MAP/fetch_data.py` | Full pipeline: pull every data source, write `ufo_data_export.json`, then auto-rebuild `index.html`. Hits the network. |
| `python3 UFO-MAP/export_data.py` | Offline export — writes `ufo_data_export.json` from the local CSV + static constants only. No network. |
| `python3 UFO-MAP/build_map.py` | Rebuild `index.html` from an existing `ufo_data_export.json`. Instant, no network, no CSV parsing. |
| `pre-commit run --all-files` | Manually run all pre-commit hooks across the whole repo. |
| `pre-commit autoupdate` | Bump the pinned hook versions in `.pre-commit-config.yaml`. |

## Environment variables

Both are read from `.env` at the repo root (loaded automatically by
`UFO-MAP/constants.py`). Real shell exports take precedence over `.env`.

| Variable | Required for | Where to get one |
| --- | --- | --- |
| `MAPBOX_TOKEN` | The 3D globe view in `index.html`. Falls back to `UFO-MAP/mapbox_token.txt` if unset. | https://account.mapbox.com/access-tokens/ — restrict the token to URLs you control in the dashboard |
| `ANTHROPIC_API_KEY` | Claude-powered location extraction in `fetch_data.py` (optional — regex fallback works). | https://console.anthropic.com/settings/keys |

## Pre-commit hooks

The hooks in `.pre-commit-config.yaml` run on every `git commit` and block
the commit if any of them fail:

- **gitleaks** — scans for leaked API keys, tokens, private keys, etc.
- **detect-private-key** — second-line defence against committing SSH/SSL keys
- **check-added-large-files** — blocks files larger than 500 KB (the bulk
  NUFORC CSV is whitelisted as a legitimate input dataset)
- **trailing-whitespace**, **end-of-file-fixer** — formatting hygiene
- **check-yaml**, **check-json**, **check-toml** — config file validation
- **check-merge-conflict** — blocks accidentally committed `<<<<<<<` markers

If a hook ever blocks a legitimate commit, fix the underlying issue rather
than bypassing with `--no-verify`.

## Continuous integration

`.github/workflows/ci.yml` runs the same `pre-commit` hooks on every pull
request and on every push to `main`. The CI workflow does **not** run the
data pipeline and does **not** need any GitHub Actions secrets — it only
checks that staged content is clean.

If you ever want to schedule automated map rebuilds (e.g. nightly), you'd
add a separate cron workflow that runs `python3 UFO-MAP/fetch_data.py` and
commits the new `index.html`. *That* workflow would need `ANTHROPIC_API_KEY`
and `MAPBOX_TOKEN` configured in **Settings → Secrets and variables →
Actions** on GitHub.

## Security notes

- Never commit a real `.env` — it's in `.gitignore`. If you accidentally do,
  rotate the leaked credentials immediately at the provider's console
  (Anthropic / Mapbox).
- The Mapbox token is a *public* token that ships embedded inside the
  generated `index.html`. Restrict it to your allowed URLs in the Mapbox
  dashboard so a leak is harmless.
- The Anthropic key is a *secret* — never embed it in client-side code or
  commit it. The pipeline only ever uses it server-side in `fetch_data.py`.

## Troubleshooting

- **`mapbox_token.txt not found` warning** → either set `MAPBOX_TOKEN` in
  your `.env` or accept that the 3D globe is disabled (the 2D map still
  works).
- **`fetch failed` errors during `fetch_data.py`** → individual sources are
  allowed to fail; the pipeline continues with whatever it could fetch.
- **Pre-commit hook failures on first install** → run
  `pre-commit run --all-files` once to fix any pre-existing whitespace issues.
