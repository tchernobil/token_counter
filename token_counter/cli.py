import argparse
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from .budget import compute_budget
from .calendar_utils import remaining_working_days, render_month, working_days_in_month
from .config import ConfigError, load_config


def _fmt(n: int) -> str:
    return f"{n:,}".replace(",", " ")


_GROUPED = re.compile(r"\d{1,3}(?:[, \u00a0\u202f]\d{3})+")


def parse_tokens(value: str) -> int:
    """Entier, avec séparateur de milliers optionnel (12,000 ou 12 000)."""
    text = value.strip()
    if _GROUPED.fullmatch(text):
        text = re.sub(r"[, \u00a0\u202f]", "", text)
    return int(text)


def _non_negative_int(value: str) -> int:
    try:
        number = parse_tokens(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"entier attendu, reçu {value!r}") from None
    if number < 0:
        raise argparse.ArgumentTypeError("la valeur doit être positive ou nulle")
    return number


def _iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"date AAAA-MM-JJ attendue, reçu {value!r}"
        ) from None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="token_counter",
        description="Tokens restants à consommer par jour ouvrable jusqu'à la fin du mois.",
    )
    parser.add_argument(
        "used",
        type=_non_negative_int,
        metavar="tokens_utilises",
        help="tokens utilisés depuis le début du mois",
    )
    parser.add_argument(
        "--config", type=Path, default=Path("config.json"), help="défaut : config.json"
    )
    parser.add_argument(
        "--debug_date",
        type=_iso_date,
        metavar="AAAA-MM-JJ",
        help="simule la date du jour (prime sur debug_date de config.json)",
    )
    return parser


def run(
    used: int, config_path: Path, today: date, debug_date: Optional[date] = None
) -> int:
    try:
        config = load_config(config_path)
    except ConfigError as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 1

    simulated = debug_date or config.debug_date
    if simulated is not None:
        today = simulated

    month_days = working_days_in_month(today.year, today.month, config.holidays)
    start = today + timedelta(days=1) if config.exclude_today else today
    left_days = (
        remaining_working_days(start, config.holidays)
        if start.month == today.month
        else 0
    )
    budget = compute_budget(config.total_tokens, used, month_days, left_days)

    print(render_month(today, config.holidays))
    print()
    if simulated is not None:
        print(f"Date simulée    : {simulated.isoformat()}")
    print(f"Total           : {_fmt(config.total_tokens)}")
    print(f"Utilisés        : {_fmt(used)}")
    print(f"Restants        : {_fmt(budget.remaining)}")
    scope = "aujourd'hui exclu" if config.exclude_today else "aujourd'hui inclus"
    print(f"Jours ouvrables : {left_days} restants ({scope}) / {month_days} dans le mois")
    if budget.overrun:
        print("ATTENTION : le total de tokens du mois est dépassé.")
    if budget.normal_per_day is None:
        print("Aucun jour ouvrable dans le mois.")
        print()
        return 0
    if budget.remaining_per_day is None:
        print(f"Quota normal par jour : {_fmt(budget.normal_per_day)}")
    else:
        print(
            f"Par jour        : {_fmt(budget.remaining_per_day)} / "
            f"{_fmt(budget.normal_per_day)} ({budget.ratio_percent:.0f} %)"
        )
    if budget.to_save:
        print(
            f"À épargner      : {_fmt(budget.to_save)} tokens "
            f"pour tenir {_fmt(budget.normal_per_day)}/jour"
        )
    elif budget.to_save == 0:
        print("À épargner      : 0 (rythme normal tenu)")
    print()
    return 0


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return run(args.used, args.config, date.today(), args.debug_date)
