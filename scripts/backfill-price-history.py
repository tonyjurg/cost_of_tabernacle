#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from bisect import bisect_left, bisect_right
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

TROY_OUNCES_PER_KILOGRAM = 32.150746568627
POUNDS_PER_KILOGRAM = 2.2046226218
SHEKELS_PER_TALENT = 3000
GRAMS_PER_SHEKEL = 11.4
LITERS_PER_HIN = 3.66
BRONZE_FACTOR = 1.12

MATERIALS = [
    {
        "id": "gold",
        "name": "Gold",
        "verses": "Exod. 38:24; 39:2-3, 8, 15-20, 25, 30",
        "amount_kind": "weightKg",
        "amount_value": ((29 * SHEKELS_PER_TALENT) + 730) * GRAMS_PER_SHEKEL / 1000,
        "pricing_basis": "Historical gold futures close converted from troy ounces to kilograms.",
        "price_type": "live-metal",
    },
    {
        "id": "silver",
        "name": "Silver",
        "verses": "Exod. 38:25-28",
        "amount_kind": "weightKg",
        "amount_value": ((100 * SHEKELS_PER_TALENT) + 1775) * GRAMS_PER_SHEKEL / 1000,
        "pricing_basis": "Historical silver futures close converted from troy ounces to kilograms.",
        "price_type": "live-metal",
    },
    {
        "id": "bronze",
        "name": "Bronze",
        "verses": "Exod. 38:29-31; 39:39",
        "amount_kind": "weightKg",
        "amount_value": ((70 * SHEKELS_PER_TALENT) + 2400) * GRAMS_PER_SHEKEL / 1000,
        "pricing_basis": "Historical bronze estimate derived from historical copper futures closes.",
        "price_type": "derived-bronze",
    },
    {
        "id": "blue-yarn",
        "name": "Blue yarn",
        "verses": "Exod. 26:1-6, 31, 36; 27:16; 39:1-5, 8, 21-24, 29, 31",
        "amount_kind": "unspecified",
        "pricing_basis": "Current public retail proxy for blue wool yarn.",
        "price_type": "snapshot",
        "unit_price_usd": 7.3,
    },
    {
        "id": "purple-yarn",
        "name": "Purple yarn",
        "verses": "Exod. 26:1-6, 31, 36; 27:16; 39:1-5, 8, 21, 24, 29",
        "amount_kind": "unspecified",
        "pricing_basis": "Current public retail proxy for purple wool yarn.",
        "price_type": "snapshot",
        "unit_price_usd": 9.99,
    },
    {
        "id": "scarlet-yarn",
        "name": "Scarlet yarn",
        "verses": "Exod. 26:1-6, 31, 36; 27:16; 39:1-5, 8, 24, 29",
        "amount_kind": "unspecified",
        "pricing_basis": "Current public retail proxy for scarlet wool yarn.",
        "price_type": "snapshot",
        "unit_price_usd": 7.3,
    },
    {
        "id": "fine-linen",
        "name": "Fine twined linen",
        "verses": "Exod. 26:1-6; 27:9-18; 39:2-5, 8, 24, 27-29",
        "amount_kind": "unspecified",
        "pricing_basis": "Current public retail proxy for 100% linen fabric.",
        "price_type": "snapshot",
        "unit_price_usd": 21.83,
    },
    {
        "id": "onyx",
        "name": "Onyx shoulder stones",
        "verses": "Exod. 39:6-7",
        "amount_kind": "count",
        "amount_value": 2,
        "pricing_basis": "Current public retail proxy for a black onyx cabochon.",
        "price_type": "snapshot",
        "unit_price_usd": 1.95,
    },
    {
        "id": "breastpiece-stones",
        "name": "Breastpiece stones",
        "verses": "Exod. 39:10-14",
        "amount_kind": "count",
        "amount_value": 12,
        "pricing_basis": "Current public mixed-cabochon proxy; the biblical set spans multiple gemstones.",
        "price_type": "snapshot",
        "unit_price_usd": 1.0,
    },
    {
        "id": "acacia-wood",
        "name": "Acacia wood",
        "verses": "Exod. 25:10, 23; 26:15-29; 27:1; 30:1; 39:33-39",
        "amount_kind": "unspecified",
        "pricing_basis": "Current public retail proxy for acacia lumber.",
        "price_type": "snapshot",
        "unit_price_usd": 15.5,
    },
    {
        "id": "olive-oil",
        "name": "Olive oil for the light",
        "verses": "Exod. 27:20-21; 39:37",
        "amount_kind": "unspecified",
        "pricing_basis": "Current public grocery proxy for 1 liter olive oil.",
        "price_type": "snapshot",
        "unit_price_usd": 14.99,
    },
    {
        "id": "myrrh",
        "name": "Myrrh (anointing oil recipe)",
        "verses": "Exod. 30:23-25; 39:38",
        "amount_kind": "weightKg",
        "amount_value": 500 * GRAMS_PER_SHEKEL / 1000,
        "pricing_basis": "Current public retail proxy for myrrh gum used as a stand-in for the flowing myrrh in Exodus 30.",
        "price_type": "snapshot",
        "unit_price_usd": 143.30047,
    },
    {
        "id": "cinnamon",
        "name": "Sweet cinnamon (anointing oil recipe)",
        "verses": "Exod. 30:23-25; 39:38",
        "amount_kind": "weightKg",
        "amount_value": 250 * GRAMS_PER_SHEKEL / 1000,
        "pricing_basis": "Current public retail proxy for cinnamon sticks used as a stand-in for the spice in Exodus 30.",
        "price_type": "snapshot",
        "unit_price_usd": 17.262195,
    },
    {
        "id": "calamus",
        "name": "Aromatic cane / calamus (anointing oil recipe)",
        "verses": "Exod. 30:23-25; 39:38",
        "amount_kind": "weightKg",
        "amount_value": 250 * GRAMS_PER_SHEKEL / 1000,
        "pricing_basis": "Current public retail proxy for calamus root powder used as a stand-in for the aromatic cane in Exodus 30.",
        "price_type": "snapshot",
        "unit_price_usd": 57.320188,
    },
    {
        "id": "cassia",
        "name": "Cassia (anointing oil recipe)",
        "verses": "Exod. 30:24-25; 39:38",
        "amount_kind": "weightKg",
        "amount_value": 500 * GRAMS_PER_SHEKEL / 1000,
        "pricing_basis": "Current public retail proxy for cassia bark used as a stand-in for the cassia in Exodus 30.",
        "price_type": "snapshot",
        "unit_price_usd": 27.535737,
    },
    {
        "id": "anointing-oil-olive-oil",
        "name": "Olive oil (anointing oil recipe)",
        "verses": "Exod. 30:24-25; 39:38",
        "amount_kind": "volumeL",
        "amount_value": LITERS_PER_HIN,
        "pricing_basis": "Current public grocery proxy for olive oil; Exodus 30 specifies one hin in the anointing oil recipe.",
        "price_type": "snapshot",
        "unit_price_usd": 14.99,
    },
]


def fetch_json(url: str) -> dict:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; TabernacleHistoryBackfill/1.0)",
            "Accept": "application/json",
        },
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def to_money(value: float) -> float:
    return round(value, 6)


def write_history_files(history_path: Path, history: dict) -> None:
    json_text = json.dumps(history, indent=2) + "\n"
    js_text = "window.TABERNACLE_PRICE_HISTORY = " + json.dumps(history, indent=2) + ";\n"

    history_path.write_text(json_text, encoding="utf-8")
    history_path.with_suffix(".js").write_text(js_text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill historical tabernacle price snapshots.")
    parser.add_argument("--years", type=int, default=3, help="How many years to backfill. Default: 3.")
    parser.add_argument(
        "--frequency",
        choices=("daily", "weekly", "monthly"),
        default="monthly",
        help="Snapshot frequency for the backfill. Default: monthly.",
    )
    parser.add_argument(
        "--history-path",
        help="Override the output history JSON path. Defaults to docs/data/price-history.json inside the repo.",
    )
    parser.add_argument(
        "--replace-existing",
        action="store_true",
        help="Replace existing entries that use the same recordedAt timestamp.",
    )
    parser.add_argument(
        "--reset-history",
        action="store_true",
        help="Discard existing history entries and rebuild the file from the generated backfill only.",
    )
    return parser.parse_args()


def fetch_yahoo_series(symbol: str, start_date: date, end_date: date) -> dict[date, float]:
    start_ts = int(datetime.combine(start_date, time.min, tzinfo=timezone.utc).timestamp())
    end_ts = int(datetime.combine(end_date + timedelta(days=1), time.min, tzinfo=timezone.utc).timestamp())
    query = urlencode(
        {
            "period1": start_ts,
            "period2": end_ts,
            "interval": "1d",
            "includePrePost": "false",
            "events": "div,splits",
        }
    )
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?{query}"
    payload = fetch_json(url)
    result = payload["chart"]["result"][0]
    timestamps = result.get("timestamp", [])
    closes = result["indicators"]["quote"][0]["close"]

    series: dict[date, float] = {}
    for timestamp, close in zip(timestamps, closes):
        if close is None:
            continue
        series[datetime.fromtimestamp(timestamp, tz=timezone.utc).date()] = float(close)

    if not series:
        raise RuntimeError(f"No historical data returned for {symbol}.")

    return series


def fetch_fx_series(start_date: date, end_date: date) -> dict[date, float]:
    url = f"https://api.frankfurter.dev/v1/{start_date.isoformat()}..{end_date.isoformat()}?base=USD&symbols=EUR"
    payload = fetch_json(url)
    rates = payload.get("rates", {})
    if not rates:
        raise RuntimeError("No historical FX data returned from Frankfurter.")
    return {date.fromisoformat(day): float(values["EUR"]) for day, values in rates.items()}


def next_month_start(current_date: date) -> date:
    if current_date.month == 12:
        return date(current_date.year + 1, 1, 1)
    return date(current_date.year, current_date.month + 1, 1)


def select_sample_dates(base_dates: list[date], frequency: str, start_date: date, end_date: date) -> list[date]:
    if frequency == "daily":
        return base_dates

    if frequency == "monthly":
        selected: list[date] = []
        current_date = date(start_date.year, start_date.month, 1)
        final_date = date(end_date.year, end_date.month, 1)

        while current_date <= final_date:
            selected.append(current_date)
            current_date = next_month_start(current_date)

        return selected

    selected: list[date] = []
    last_bucket = None
    for current_date in base_dates:
        if frequency == "weekly":
            bucket = current_date.isocalendar()[:2]
        else:
            bucket = (current_date.year, current_date.month)

        if selected and bucket == last_bucket:
            selected[-1] = current_date
        else:
            selected.append(current_date)
            last_bucket = bucket

    return selected


def build_lookup(series: dict[date, float]) -> tuple[list[date], list[float]]:
    keys = sorted(series.keys())
    values = [series[key] for key in keys]
    return keys, values


def value_on_or_before(keys: list[date], values: list[float], target_date: date) -> float:
    index = bisect_right(keys, target_date) - 1
    if index < 0:
        raise RuntimeError(f"No source value available on or before {target_date.isoformat()}.")
    return values[index]


def value_on_or_after(keys: list[date], values: list[float], target_date: date) -> tuple[date, float]:
    index = bisect_left(keys, target_date)
    if index >= len(keys):
        raise RuntimeError(f"No source value available on or after {target_date.isoformat()}.")
    return keys[index], values[index]


def build_snapshot(
    snapshot_date: date,
    gold: float,
    silver: float,
    copper: float,
    usd_to_eur: float,
    fx_date: date,
) -> dict:
    materials = {}
    documented_total_usd = 0.0

    for material in MATERIALS:
        if material["price_type"] == "live-metal":
            symbol_price = gold if material["id"] == "gold" else silver
            unit_price_usd = symbol_price * TROY_OUNCES_PER_KILOGRAM
        elif material["price_type"] == "derived-bronze":
            unit_price_usd = copper * POUNDS_PER_KILOGRAM * BRONZE_FACTOR
        else:
            unit_price_usd = material["unit_price_usd"]

        if material["amount_kind"] == "unspecified":
            row_total_usd = None
        else:
            row_total_usd = unit_price_usd * material["amount_value"]
            documented_total_usd += row_total_usd

        materials[material["id"]] = {
            "name": material["name"],
            "verses": material["verses"],
            "pricingBasis": material["pricing_basis"],
            "amountKind": material["amount_kind"],
            "unitPriceUsd": to_money(unit_price_usd),
            "unitPriceEur": to_money(unit_price_usd * usd_to_eur),
            "rowTotalUsd": None if row_total_usd is None else to_money(row_total_usd),
            "rowTotalEur": None if row_total_usd is None else to_money(row_total_usd * usd_to_eur),
        }

    return {
        "recordedAt": datetime.combine(snapshot_date, time.min, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
        "fxDate": fx_date.isoformat(),
        "usdToEur": to_money(usd_to_eur),
        "bronzeFactor": BRONZE_FACTOR,
        "documentedTotalUsd": to_money(documented_total_usd),
        "documentedTotalEur": to_money(documented_total_usd * usd_to_eur),
        "materials": materials,
    }


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    history_path = Path(args.history_path) if args.history_path else repo_root / "docs" / "data" / "price-history.json"
    history_path.parent.mkdir(parents=True, exist_ok=True)

    end_date = date.today() - timedelta(days=1)
    if args.frequency == "monthly":
        start_date = date(end_date.year - max(args.years, 1), end_date.month, 1)
    else:
        start_date = end_date - timedelta(days=max(args.years, 1) * 365)

    gold_series = fetch_yahoo_series("GC=F", start_date, end_date)
    silver_series = fetch_yahoo_series("SI=F", start_date, end_date)
    copper_series = fetch_yahoo_series("HG=F", start_date, end_date)
    fx_series = fetch_fx_series(start_date, end_date)

    sample_dates = select_sample_dates(sorted(gold_series.keys()), args.frequency, start_date, end_date)

    gold_keys, gold_values = build_lookup(gold_series)
    silver_keys, silver_values = build_lookup(silver_series)
    copper_keys, copper_values = build_lookup(copper_series)
    fx_keys, fx_values = build_lookup(fx_series)

    if args.reset_history:
        history = {"version": 1, "entries": []}
    elif history_path.exists():
        history = json.loads(history_path.read_text(encoding="utf-8"))
    else:
        history = {"version": 1, "entries": []}

    history.setdefault("version", 1)
    history.setdefault("entries", [])
    existing_by_timestamp = {entry["recordedAt"]: entry for entry in history["entries"]}

    added = 0
    replaced = 0
    for snapshot_date in sample_dates:
        if args.frequency == "monthly":
            _, gold_price = value_on_or_after(gold_keys, gold_values, snapshot_date)
            _, silver_price = value_on_or_after(silver_keys, silver_values, snapshot_date)
            _, copper_price = value_on_or_after(copper_keys, copper_values, snapshot_date)
            fx_date, usd_to_eur = value_on_or_after(fx_keys, fx_values, snapshot_date)
        else:
            gold_price = value_on_or_before(gold_keys, gold_values, snapshot_date)
            silver_price = value_on_or_before(silver_keys, silver_values, snapshot_date)
            copper_price = value_on_or_before(copper_keys, copper_values, snapshot_date)
            fx_date = snapshot_date
            usd_to_eur = value_on_or_before(fx_keys, fx_values, snapshot_date)

        snapshot = build_snapshot(
            snapshot_date=snapshot_date,
            gold=gold_price,
            silver=silver_price,
            copper=copper_price,
            usd_to_eur=usd_to_eur,
            fx_date=fx_date,
        )

        timestamp = snapshot["recordedAt"]
        if timestamp in existing_by_timestamp and not args.replace_existing:
            continue

        if timestamp in existing_by_timestamp:
            replaced += 1
        else:
            added += 1

        existing_by_timestamp[timestamp] = snapshot

    history["entries"] = sorted(existing_by_timestamp.values(), key=lambda entry: entry["recordedAt"])
    write_history_files(history_path, history)

    print(f"Updated {history_path}")
    print(f"Range: {start_date.isoformat()} to {end_date.isoformat()}")
    print(f"Frequency: {args.frequency}")
    print(f"Added snapshots: {added}")
    print(f"Replaced snapshots: {replaced}")


if __name__ == "__main__":
    main()
