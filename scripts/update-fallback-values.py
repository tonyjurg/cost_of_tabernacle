#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen


def fetch_json(url: str) -> dict:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; TabernacleFallbackUpdater/1.0)",
            "Accept": "application/json",
        },
    )
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def format_number_literal(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh the FALLBACK_QUOTES block in docs/app.js.")
    parser.add_argument(
        "--app-js-path",
        help="Override the docs/app.js path. Defaults to docs/app.js inside the repo.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    app_js_path = Path(args.app_js_path) if args.app_js_path else repo_root / "docs" / "app.js"
    app_js_content = app_js_path.read_text(encoding="utf-8")

    # Pull fresh values from the same public feeds the browser app uses.
    gold = fetch_json("https://api.gold-api.com/price/XAU")
    silver = fetch_json("https://api.gold-api.com/price/XAG")
    copper = fetch_json("https://api.gold-api.com/price/HG")
    fx = fetch_json("https://api.frankfurter.dev/v1/latest?base=USD&symbols=EUR")

    # Rebuild the object literal exactly as it appears in docs/app.js.
    replacement_block = f"""  const FALLBACK_QUOTES = {{
    XAU: {{ price: {format_number_literal(float(gold["price"]))}, updatedAt: "{gold["updatedAt"]}" }},
    XAG: {{ price: {format_number_literal(float(silver["price"]))}, updatedAt: "{silver["updatedAt"]}" }},
    HG: {{ price: {format_number_literal(float(copper["price"]))}, updatedAt: "{copper["updatedAt"]}" }},
    usdToEur: {format_number_literal(float(fx["rates"]["EUR"]))},
    fxDate: "{fx["date"]}",
  }};"""

    # Replace only the first fallback block so the rest of the app stays untouched.
    updated_content, replacements = re.subn(
        r"(?ms)^  const FALLBACK_QUOTES = \{.*?^  \};",
        replacement_block,
        app_js_content,
        count=1,
    )

    if replacements != 1:
        raise RuntimeError(f"Could not locate the FALLBACK_QUOTES block in {app_js_path}.")

    # Write UTF-8 text back to app.js so the static site can keep serving the file normally.
    app_js_path.write_text(updated_content, encoding="utf-8")

    print(f"Updated FALLBACK_QUOTES in {app_js_path}")
    print(f"Gold updatedAt:   {gold['updatedAt']}")
    print(f"Silver updatedAt: {silver['updatedAt']}")
    print(f"Copper updatedAt: {copper['updatedAt']}")
    print(f"FX date:          {fx['date']}")


if __name__ == "__main__":
    main()
