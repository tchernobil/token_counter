import contextlib
import io
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from token_counter.budget import compute_budget
from token_counter.calendar_utils import (
    is_working_day,
    remaining_working_days,
    render_month,
    working_days_in_month,
)
from token_counter.cli import build_parser, parse_tokens, run
from token_counter.config import ConfigError, load_config


class ConfigTests(unittest.TestCase):
    def _load(self, content):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text(json.dumps(content), encoding="utf-8")
            return load_config(path)

    def test_valid(self):
        cfg = self._load({"total_tokens": 1000, "holidays": ["2026-12-25"]})
        self.assertEqual(cfg.total_tokens, 1000)
        self.assertIn(date(2026, 12, 25), cfg.holidays)

    def test_invalid_total(self):
        for bad in (0, -5, "10", 1.5, None, True):
            with self.assertRaises(ConfigError):
                self._load({"total_tokens": bad})
        with self.assertRaises(ConfigError):
            self._load({"holidays": []})

    def test_exclude_today(self):
        self.assertFalse(self._load({"total_tokens": 10}).exclude_today)
        self.assertFalse(self._load({"total_tokens": 10, "exclude_today": False}).exclude_today)
        self.assertTrue(self._load({"total_tokens": 10, "exclude_today": True}).exclude_today)

    def test_invalid_exclude_today(self):
        for bad in ("oui", 1, 0, None):
            with self.assertRaises(ConfigError):
                self._load({"total_tokens": 10, "exclude_today": bad})

    def test_invalid_holiday(self):
        with self.assertRaises(ConfigError):
            self._load({"total_tokens": 10, "holidays": ["25/12/2026"]})

    def test_missing_file(self):
        with self.assertRaises(ConfigError) as ctx:
            load_config(Path("/nonexistent/config.json"))
        self.assertIn("/nonexistent/config.json", str(ctx.exception))


class ParseTokensTests(unittest.TestCase):
    def test_accepted(self):
        for text, expected in [
            ("12000", 12000),
            ("12,000", 12000),
            ("1,234,567", 1234567),
            ("12 000", 12000),
            ("0", 0),
        ]:
            self.assertEqual(parse_tokens(text), expected)

    def test_rejected(self):
        for text in ("12,5", "1,23", "12,0000", "abc", "", "1.5"):
            with self.assertRaises(ValueError):
                parse_tokens(text)


class CalendarTests(unittest.TestCase):
    def test_weekend_and_holiday(self):
        self.assertFalse(is_working_day(date(2026, 11, 14), set()))  # samedi
        self.assertFalse(is_working_day(date(2026, 11, 11), {date(2026, 11, 11)}))
        self.assertTrue(is_working_day(date(2026, 11, 12), set()))

    def test_month_count(self):
        self.assertEqual(working_days_in_month(2026, 11, set()), 21)
        self.assertEqual(working_days_in_month(2026, 11, {date(2026, 11, 11)}), 20)

    def test_remaining_today_working(self):
        self.assertEqual(remaining_working_days(date(2026, 11, 30), set()), 1)
        self.assertEqual(remaining_working_days(date(2026, 11, 1), set()), 21)

    def test_remaining_today_not_working(self):
        self.assertEqual(remaining_working_days(date(2026, 11, 29), set()), 1)

    def test_render_markers(self):
        out = render_month(date(2026, 11, 10), {date(2026, 11, 11)})
        self.assertIn("10*", out)
        self.assertIn("11&", out)
        self.assertIn("Novembre 2026", out)
        self.assertIn("14.", out)


class BudgetTests(unittest.TestCase):
    def test_standard(self):
        b = compute_budget(1_000_000, 250_000, 20, 15)
        self.assertEqual(b.remaining, 750_000)
        self.assertEqual(b.normal_per_day, 50_000)
        self.assertEqual(b.remaining_per_day, 50_000)
        self.assertEqual(b.ratio_percent, 100)

    def test_ratio(self):
        b = compute_budget(1_000_000, 400_000, 20, 15)
        self.assertEqual(b.remaining_per_day, 40_000)
        self.assertEqual(b.ratio_percent, 80)

    def test_rounding(self):
        self.assertEqual(compute_budget(100, 0, 3, 3).remaining_per_day, 33)

    def test_overrun(self):
        b = compute_budget(1000, 1500, 20, 10)
        self.assertTrue(b.overrun)
        self.assertEqual(b.remaining, -500)
        self.assertIsNone(b.remaining_per_day)
        self.assertIsNone(b.ratio_percent)
        self.assertEqual(b.normal_per_day, 50)

    def test_no_remaining_days(self):
        b = compute_budget(1000, 100, 20, 0)
        self.assertEqual(b.remaining, 900)
        self.assertIsNone(b.remaining_per_day)

    def test_to_save_when_behind(self):
        b = compute_budget(30_000, 10_000, 20, 14)  # 20 000 restants, 21 000 nécessaires
        self.assertEqual(b.to_save, 1_000)

    def test_to_save_when_ahead(self):
        self.assertEqual(compute_budget(30_000, 0, 20, 14).to_save, 0)

    def test_to_save_overrun(self):
        self.assertEqual(compute_budget(30_000, 31_000, 20, 14).to_save, 22_000)

    def test_to_save_unavailable(self):
        self.assertIsNone(compute_budget(1000, 100, 20, 0).to_save)

    def test_no_working_day_in_month(self):
        b = compute_budget(1000, 100, 0, 0)
        self.assertIsNone(b.normal_per_day)


class ExcludeTodayTests(unittest.TestCase):
    def _run(self, today, **extra):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text(json.dumps({"total_tokens": 20000, **extra}), encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(run(0, path, today), 0)
            return out.getvalue()

    def test_today_included_by_default(self):
        out = self._run(date(2026, 11, 10))
        self.assertIn("15 restants (aujourd'hui inclus)", out)

    def test_today_excluded(self):
        out = self._run(date(2026, 11, 10), exclude_today=True)
        self.assertIn("14 restants (aujourd'hui exclu)", out)

    def test_non_working_today_unchanged(self):
        saturday = date(2026, 11, 14)
        inc = self._run(saturday).split("Jours ouvrables : ")[1].split(" ")[0]
        exc = self._run(saturday, exclude_today=True).split("Jours ouvrables : ")[1].split(" ")[0]
        self.assertEqual(inc, exc)

    def test_last_day_of_month(self):
        out = self._run(date(2026, 11, 30), exclude_today=True)
        self.assertIn("0 restants (aujourd'hui exclu)", out)
        self.assertNotIn("À épargner   : 0 (rythme", out)


class DebugDateTests(unittest.TestCase):
    def _run(self, config, debug_date=None):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text(json.dumps({"total_tokens": 20000, **config}), encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                run(0, path, date(2026, 11, 10), debug_date)
            return out.getvalue()

    def test_default_real_date(self):
        for cfg in ({}, {"debug_date": None}):
            out = self._run(cfg)
            self.assertNotIn("Date simulée", out)
            self.assertIn("Novembre 2026", out)

    def test_config_date(self):
        out = self._run({"debug_date": "2026-12-15"})
        self.assertIn("Date simulée    : 2026-12-15", out)
        self.assertIn("Décembre 2026", out)

    def test_cli_overrides_config(self):
        out = self._run({"debug_date": "2026-11-01"}, date(2026, 12, 20))
        self.assertIn("Date simulée    : 2026-12-20", out)

    def test_invalid_config_date(self):
        for bad in ("25/12/2026", 20261225, True):
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "c.json"
                path.write_text(json.dumps({"total_tokens": 1, "debug_date": bad}))
                with self.assertRaises(ConfigError):
                    load_config(path)

    def test_invalid_cli_date(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            build_parser().parse_args(["1", "--debug_date", "nope"])


if __name__ == "__main__":
    unittest.main()
