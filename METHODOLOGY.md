# Methodology

## Scope

The inventory is restricted to materials named in Exodus 38:21-39:41. The main quantified source inside that scope is Exodus 38:21-39:32, which includes the exact metal amounts listed in Exodus 38:24-29. The inventory also includes the named materials used in the priestly garments and tabernacle furnishings through Exodus 39:41.

When one of those named items receives a direct recipe quantity or other explicit measurement elsewhere in Exodus, the site now cites and uses that detail as well. The clearest example is the holy anointing oil in Exodus 30:23-25, whose ingredient list is quantified by shekel weights and one hin of olive oil.

## Weight conversions

The calculator uses these common biblical-weight assumptions:

- `1 talent = 3,000 shekels`
- `1 shekel = 11.4 grams`
- `1 hin = about 3.66 liters`

That yields:

- gold: `29 talents + 730 shekels = 1,000.122 kg`
- silver: `100 talents + 1,775 shekels = 3,440.235 kg`
- bronze: `70 talents + 2,400 shekels = 2,421.36 kg`

## Pricing model

### Live public feeds

- gold: Gold-API spot quote for `XAU`
- silver: Gold-API spot quote for `XAG`
- copper: Gold-API quote for `HG`
- exchange rate: Frankfurter USD to EUR

Gold and silver are converted from troy ounces to kilograms. Copper is quoted per pound; the calculator converts it to kilograms.

The app also stores a fallback snapshot for these feeds inside `docs/app.js`. That snapshot can be refreshed with `scripts/update-fallback-values.py`.

For historical tracking, `scripts/record-price-history.py` stores monthly snapshots in `docs/data/price-history.json`, with the published workflow anchored to the first day of each month in UTC.

For older historical seeding, `scripts/backfill-price-history.py` can generate past snapshots from historical gold, silver, copper, and USD/EUR source data. In the current implementation, the historical metals come from Yahoo Finance futures chart data and the historical FX series comes from Frankfurter. The non-metal proxy rows remain static in that backfill. The monthly reset mode now rebuilds the stored history so each visible point is recorded at the first of the month.

Because some month starts fall on weekends or market holidays, a monthly entry may have a `recordedAt` value like `2026-02-01T00:00:00Z` while its `fxDate` reflects the next source date that actually returned market data. Both history-writing scripts also maintain `docs/data/price-history.js` as a browser-loadable mirror of `docs/data/price-history.json` so the history page works when opened directly from disk.

### Bronze

There is no widely quoted public bronze spot feed comparable to gold, silver, or copper. The site therefore estimates bronze as:

`live copper price x adjustable bronze factor`

The default bronze factor is `1.12`, and the user can change it in the interface.

### Snapshot retail proxies

For several non-metal materials, the site uses current public product pages as transparent retail proxies, for example:

- wool yarn colors for blue, purple, and scarlet
- linen fabric for fine twined linen
- cabochon listings for onyx and mixed gemstones
- acacia lumber and olive oil listings
- myrrh, cinnamon, calamus, and cassia listings for the quantified anointing-oil recipe ingredients

These are not claims that the biblical materials were bought in these exact modern forms. They are simply visible present-day proxy prices from public sources.

## Cross-referenced Exodus quantities

The calculator now uses the rest of Exodus in two different ways:

1. to add directly quantifiable rows where Exodus gives exact ingredient amounts
2. to improve the explanatory text for still-open rows when Exodus gives partial counts or dimensions but not enough for a full cost total

Examples:

- `Exod. 30:23-25` gives `500 shekels` of myrrh, `250 shekels` of cinnamon, `250 shekels` of aromatic cane, `500 shekels` of cassia, and `1 hin` of olive oil for the holy anointing oil
- `Exod. 26:1-6` and `Exod. 27:9-18` give exact fabric panel dimensions that help describe the linen and colored-yarn rows, even though they do not provide fiber weights
- `Exod. 26:15-29` gives board and bar counts for acacia wood, but not enough dimensions to derive a reliable full wood volume

## Important limitation

The total shown by the site is not a complete reconstruction cost. It is a documented lower bound based on the rows where both of these are true:

1. the material is named in Exodus 38:21-39:41
2. the amount is explicitly quantifiable from those verses or from a directly tied earlier Exodus recipe reference

Materials named without an explicit quantity remain in the table, but their totals are intentionally left open.
