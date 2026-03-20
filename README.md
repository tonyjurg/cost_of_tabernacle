[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)

# Cost of Tabernacle

This repository estimates the present-day cost of building the tabernacle using the materials named in Exodus 38:21-39:41. Its main quantified source is Exodus 38:21-39:32, and it also cross-references other Exodus passages when they give exact recipe quantities or other direct measurement details for those named items. It does not include the cost of labour.

The interactive GitHub Pages site lives in [`docs/`](docs/) so the repository root can stay focused on explanation, assumptions, and source transparency.

## Project structure

- [`docs/`](docs/): publishable static site for GitHub Pages
- [`docs/index.html`](docs/index.html): current calculator page
- [`docs/history.html`](docs/history.html): interactive historical chart view
- [`docs/data/price-history.json`](docs/data/price-history.json): stored snapshot history used by the chart page
- [`docs/data/price-history.js`](docs/data/price-history.js): browser-loadable mirror of the history data for local file viewing
- [`.github/workflows/record-price-history.yml`](.github/workflows/record-price-history.yml): monthly GitHub Actions snapshot recorder
- [`LICENCE`](LICENCE): repository license notice for CC BY 4.0 reuse
- [`METHODOLOGY.md`](METHODOLOGY.md): passage scope, conversions, pricing approach, and limits
- [`ARCHITECTURE.md`](ARCHITECTURE.md): code walkthrough and runtime data-flow diagram
- [`scripts/update-fallback-values.py`](scripts/update-fallback-values.py): refreshes the built-in fallback quote snapshot in `docs/app.js`
- [`scripts/record-price-history.py`](scripts/record-price-history.py): writes a monthly historical price snapshot for the chart page
- [`scripts/backfill-price-history.py`](scripts/backfill-price-history.py): backfills older historical snapshots for the chart page

## What the site does

- Lists the exact materials named in Exodus 38:21-39:41
- Shows the amount named in the passage where the verses actually quantify it
- Cross-references earlier Exodus instructions when they give an exact recipe quantity tied to a named item
- Pulls live public prices for gold, silver, copper, and USD/EUR
- Lets the user switch between USD and EUR
- Calculates a documented lower-bound total from the rows that are both quantified and priced
- Keeps named-but-unquantified materials visible instead of inventing precise amounts
- Publishes a separate history page that graphs recorded totals and material price movement over time
- Shows visible update and source summaries on both published pages

## Pages

### [`docs/index.html`](docs/index.html)

The calculator page includes:

- the current documented total table
- header-side live, update, and source summaries tied to the current live or fallback data

### [`docs/history.html`](docs/history.html)

The history page includes:

- the recorded history chart
- a latest-snapshot summary
- header-side status, update-range, and source summaries for the stored history data

## Why the total is a lower bound

The passage explicitly gives metal weights for gold, silver, and bronze, and explicit counts for the onyx shoulder stones and the twelve breastpiece stones. Earlier Exodus also gives a full ingredient recipe for the holy anointing oil in Exodus 30:23-25, so those ingredients are now broken out as quantified rows. Several other named materials still do not receive a complete measurable amount even after cross-referencing the rest of Exodus. The site therefore shows:

- Priced and totaled rows when the amount is explicit.
- Price references without a total when the verses name a material but do not quantify it.

## GitHub Pages

The GitHub repository is configured to serve the public accessable GitHub Pages from the `main` branch and the [`/docs`](/docs) folder. The page is accesable via [tonyjurg.github.io/cost_of_tabernacle](https://tonyjurg.github.io/cost_of_tabernacle).

## Maintenance

The site uses live public feeds in the browser, but it also carries a built-in fallback snapshot in [`docs/app.js`](docs/app.js) in case those requests fail.

To refresh that fallback snapshot from the repository root, run:

```bash
python3 ./scripts/update-fallback-values.py
```

That script fetches current gold, silver, copper, and USD/EUR data and rewrites the `FALLBACK_QUOTES` block in [`docs/app.js`](docs/app.js).

To write a monthly historical snapshot for the graph page, run:

```bash
python3 ./scripts/record-price-history.py --recorded-at 2026-04-01 --replace-existing
```

That command writes the snapshot under the explicit first-of-month timestamp you choose and replaces any existing entry for that same month. The result is stored in [`docs/data/price-history.json`](docs/data/price-history.json), which is then read by [`docs/history.html`](docs/history.html).
The scripts also keep [`docs/data/price-history.js`](docs/data/price-history.js) in sync so `history.html` can work when opened directly from disk as well as on GitHub Pages.

To rebuild the last few years so every point lands on the first day of the month, run:

```bash
python3 ./scripts/backfill-price-history.py --years 3 --frequency monthly --reset-history
```

You can change `--years` and `--frequency` (`daily`, `weekly`, or `monthly`) to control how much history is generated. For the published history chart, the repository now uses monthly first-of-month snapshots as the canonical interval.

The GitHub Actions workflow in [`.github/workflows/record-price-history.yml`](.github/workflows/record-price-history.yml) runs on the first day of each month at `06:00 UTC`. Manual workflow runs are guarded so they do not write off-interval points later in the month.

All history-writing scripts update both of these files together:

- [`docs/data/price-history.json`](docs/data/price-history.json)
- [`docs/data/price-history.js`](docs/data/price-history.js)

That keeps the history page usable both through GitHub Pages and when opened directly from disk.

## Data sources

Current calculator page:

- live metals: Gold-API
- live USD/EUR: Frankfurter
- non-metal rows: current public retail proxy listings linked in the table

History page:

- historical gold, silver, copper: Yahoo Finance futures chart data
- historical USD/EUR: Frankfurter historical range data
- non-metal rows: static proxy values carried forward because a trustworthy historical series is not currently wired in

Example monthly cron entry:

```cron
0 6 1 * * cd /path/to/cost_of_tabernacle && python3 ./scripts/record-price-history.py --recorded-at "$(date -u +\%Y-\%m-01)" --replace-existing
```

## Diagrams

The architecture diagram in [`ARCHITECTURE.md`](ARCHITECTURE.md) is written in Mermaid. GitHub renders Mermaid directly inside Markdown files on the repository website. The published static Pages app in `docs/` does not currently render Mermaid by itself (it could if we would add the Mermaid browser library to the site).

## Image source

The published page includes a public-domain Holman Bible tabernacle illustration from Wikimedia Commons. The image file is stored locally in `docs/assets/` so the GitHub Pages site does not depend on external hotlinking.

## Disclosure

This code in this repository was developed with assistance from OpenAI Codex.

## Feedback and Suggestions

If you encounter any issues, or if you have suggestions for improvements or additional feeds, please feel free to open an [issues](https://github.com/tonyjurg/cost_of_tabernacle/issues) in this repository.

## Copyright and license

Copyright © 2026 Tony Jurg.

This repository content is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). See [`LICENCE`](LICENCE). You are free to reuse it with reference to the author.
