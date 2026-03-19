#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, time, timezone
from pathlib import Path
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
        "pricing_basis": "Live Gold-API spot quote, converted from troy ounces to kilograms.",
        "price_type": "live-metal",
        "live_symbol": "XAU",
    },
    {
        "id": "silver",
        "name": "Silver",
        "verses": "Exod. 38:25-28",
        "amount_kind": "weightKg",
        "amount_value": ((100 * SHEKELS_PER_TALENT) + 1775) * GRAMS_PER_SHEKEL / 1000,
        "pricing_basis": "Live Gold-API spot quote, converted from troy ounces to kilograms.",
        "price_type": "live-metal",
        "live_symbol": "XAG",
    },
    {
        "id": "bronze",
        "name": "Bronze",
        "verses": "Exod. 38:29-31; 39:39",
        "amount_kind": "weightKg",
        "amount_value": ((70 * SHEKELS_PER_TALENT) + 2400) * GRAMS_PER_SHEKEL / 1000,
        "pricing_basis": "Estimated from live copper because there is no widely quoted public bronze spot feed.",
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
            "User-Agent": "Mozilla/5.0 (compatible; TabernacleHistoryRecorder/1.0)",
            "Accept": "application/json",
        },
    )
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def to_money(value: float) -> float:
    return round(value, 6)


def write_history_files(history_path: Path, history: dict) -> None:
    json_text = json.dumps(history, indent=2) + "\n"
    js_text = "window.TABERNACLE_PRICE_HISTORY = " + json.dumps(history, indent=2) + ";\n"

    history_path.write_text(json_text, encoding="utf-8")
    history_path.with_suffix(".js").write_text(js_text, encoding="utf-8")


def build_snapshot(recorded_at: datetime | None = None) -> dict:
    # Pull the same live feeds used by the published calculator page.
    gold = fetch_json("https://api.gold-api.com/price/XAU")
    silver = fetch_json("https://api.gold-api.com/price/XAG")
    copper = fetch_json("https://api.gold-api.com/price/HG")
    fx = fetch_json("https://api.frankfurter.dev/v1/latest?base=USD&symbols=EUR")

    usd_to_eur = float(fx["rates"]["EUR"])
    live_quotes = {
        "XAU": float(gold["price"]),
        "XAG": float(silver["price"]),
        "HG": float(copper["price"]),
    }

    materials = {}
    documented_total_usd = 0.0

    for material in MATERIALS:
        if material["price_type"] == "live-metal":
            unit_price_usd = live_quotes[material["live_symbol"]] * TROY_OUNCES_PER_KILOGRAM
        elif material["price_type"] == "derived-bronze":
            unit_price_usd = live_quotes["HG"] * POUNDS_PER_KILOGRAM * BRONZE_FACTOR
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

    effective_recorded_at = recorded_at or datetime.now(timezone.utc).replace(microsecond=0)

    return {
        "recordedAt": effective_recorded_at.isoformat().replace("+00:00", "Z"),
        "fxDate": fx["date"],
        "usdToEur": to_money(usd_to_eur),
        "bronzeFactor": BRONZE_FACTOR,
        "documentedTotalUsd": to_money(documented_total_usd),
        "documentedTotalEur": to_money(documented_total_usd * usd_to_eur),
        "materials": materials,
    }


def parse_recorded_at(value: str) -> datetime:
    parsed_date = date.fromisoformat(value)
    return datetime.combine(parsed_date, time.min, tzinfo=timezone.utc)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write one historical price snapshot for the tabernacle site.")
    parser.add_argument(
        "--history-path",
        help="Override the output history JSON path. Defaults to docs/data/price-history.json inside the repo.",
    )
    parser.add_argument(
        "--recorded-at",
        type=parse_recorded_at,
        help="Override the recordedAt timestamp using a UTC date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--replace-existing",
        action="store_true",
        help="Replace an existing entry that has the same recordedAt timestamp instead of appending a duplicate.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    history_path = Path(args.history_path) if args.history_path else repo_root / "docs" / "data" / "price-history.json"
    history_path.parent.mkdir(parents=True, exist_ok=True)

    if history_path.exists():
        history = json.loads(history_path.read_text(encoding="utf-8"))
    else:
        history = {"version": 1, "entries": []}

    history.setdefault("version", 1)
    history.setdefault("entries", [])
    snapshot = build_snapshot(recorded_at=args.recorded_at)

    if args.replace_existing:
        history["entries"] = [entry for entry in history["entries"] if entry["recordedAt"] != snapshot["recordedAt"]]

    history["entries"].append(snapshot)
    history["entries"].sort(key=lambda entry: entry["recordedAt"])

    write_history_files(history_path, history)
    print(f"Wrote snapshot to {history_path}")


if __name__ == "__main__":
    main()
