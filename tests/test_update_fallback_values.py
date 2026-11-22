import argparse
import contextlib
import copy
import importlib.util
import io
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "update_fallback_values", REPO_ROOT / "scripts" / "update-fallback-values.py"
)
updater = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(updater)


class FallbackUpdaterTests(unittest.TestCase):
    def setUp(self):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        self.target = Path(temporary_directory.name) / "app.js"
        self.original = (REPO_ROOT / "docs" / "app.js").read_text(encoding="utf-8")
        self.target.write_text(self.original, encoding="utf-8")
        self.responses = [
            {"price": 4988.8999024, "updatedAt": "2026-11-01T09:31:35Z"},
            {"price": 78.862999, "updatedAt": "2026-11-01T09:31:34+00:00"},
            {"price": 5.787914, "updatedAt": "2026-11-01T09:31:38Z"},
            {"rates": {"EUR": 0.87138}, "date": "2026-11-01"},
        ]

    def run_updater(self, responses):
        with (
            patch.object(updater, "parse_args", return_value=argparse.Namespace(app_js_path=str(self.target))),
            patch.object(updater, "fetch_json", side_effect=responses),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            updater.main()

    def read_quotes(self):
        content = self.target.read_text(encoding="utf-8")
        match = re.search(r"(?ms)^  const FALLBACK_QUOTES = (\{.*?^  \});", content)
        self.assertIsNotNone(match)
        return json.loads(match.group(1))

    def test_valid_update_preserves_application_code_and_can_be_repeated(self):
        self.run_updater(copy.deepcopy(self.responses))
        first_update = self.target.read_text(encoding="utf-8")
        quotes = self.read_quotes()
        self.assertEqual(quotes["XAU"]["price"], 4988.899902)
        self.assertEqual(quotes["XAG"]["updatedAt"], "2026-11-01T09:31:34Z")
        self.assertEqual(quotes["usdToEur"], 0.87138)
        self.assertEqual(quotes["fxDate"], "2026-11-01")
        block = r"(?ms)^  const FALLBACK_QUOTES = \{.*?^  \};"
        self.assertEqual(re.sub(block, "FALLBACK_BLOCK", first_update), re.sub(block, "FALLBACK_BLOCK", self.original))
        self.run_updater(copy.deepcopy(self.responses))
        self.assertEqual(self.target.read_text(encoding="utf-8"), first_update)

    def test_code_injection_in_each_date_field_is_rejected_without_writing(self):
        payloads = [
            '2026-11-01", injected: (globalThis.__SECURITY_POC__ = true), ignored: "',
            '2026-11-01"; globalThis.__SECURITY_POC__ = true; //',
            "2026-11-01\\g<1>",
            "2026-11-01\nmalicious",
        ]
        for response_index in range(4):
            field = "date" if response_index == 3 else "updatedAt"
            for payload in payloads:
                with self.subTest(response=response_index, payload=payload):
                    responses = copy.deepcopy(self.responses)
                    responses[response_index][field] = payload
                    with self.assertRaises(ValueError):
                        self.run_updater(responses)
                    self.assertEqual(self.target.read_text(encoding="utf-8"), self.original)

    def test_timezone_free_and_invalid_calendar_dates_are_rejected(self):
        for index, field, value in [
            (0, "updatedAt", "2026-11-01T09:31:35"),
            (1, "updatedAt", "2026-02-30T09:31:35Z"),
            (2, "updatedAt", None),
            (3, "date", "2026-02-30"),
        ]:
            with self.subTest(response=index, value=value):
                responses = copy.deepcopy(self.responses)
                responses[index][field] = value
                with self.assertRaises(ValueError):
                    self.run_updater(responses)
                self.assertEqual(self.target.read_text(encoding="utf-8"), self.original)

    def test_non_finite_and_non_positive_prices_never_reach_the_output(self):
        for index in range(4):
            for value in [float("nan"), float("inf"), float("-inf"), "NaN", "Infinity", 0, -1, True, 0.00000001]:
                with self.subTest(response=index, value=value):
                    responses = copy.deepcopy(self.responses)
                    if index == 3:
                        responses[index]["rates"]["EUR"] = value
                    else:
                        responses[index]["price"] = value
                    with self.assertRaises(ValueError):
                        self.run_updater(responses)
                    self.assertEqual(self.target.read_text(encoding="utf-8"), self.original)

    def test_missing_fallback_block_does_not_overwrite_the_target(self):
        self.target.write_text("const unrelated = true;\n", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "Could not locate"):
            self.run_updater(copy.deepcopy(self.responses))
        self.assertEqual(self.target.read_text(encoding="utf-8"), "const unrelated = true;\n")


if __name__ == "__main__":
    unittest.main()
