import argparse
import re
import sys
from datetime import date
from pathlib import Path

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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="token_counter",
        description="Tokens restants à consommer par jour ouvré jusqu'à la fin du mois.",
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
    return parser


def run(used: int, config_path: Path, today: date) -> int:
    try:
        config = load_config(config_path)
    except ConfigError as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 1

    month_days = working_days_in_month(today.year, today.month, config.holidays)
    left_days = remaining_working_days(today, config.holidays)
    budget = compute_budget(config.total_tokens, used, month_days, left_days)

    print(render_month(today, config.holidays))
    print()
    print(f"Total        : {_fmt(config.total_tokens)}")
    print(f"Utilisés     : {_fmt(used)}")
    print(f"Restants     : {_fmt(budget.remaining)}")
    print(f"Jours ouvrés : {left_days} restants / {month_days} dans le mois")
    if budget.overrun:
        print("ATTENTION : le total de tokens du mois est dépassé.")
    if budget.normal_per_day is None:
        print("Aucun jour ouvré dans le mois.")
        print()
        return 0
    if budget.remaining_per_day is None:
        print(f"Quota normal par jour : {_fmt(budget.normal_per_day)}")
    else:
        print(
            f"Par jour     : {_fmt(budget.remaining_per_day)} / "
            f"{_fmt(budget.normal_per_day)} ({budget.ratio_percent:.0f} %)"
        )
    if budget.to_save:
        print(
            f"À épargner   : {_fmt(budget.to_save)} tokens "
            f"pour tenir {_fmt(budget.normal_per_day)}/jour"
        )
    elif budget.to_save == 0:
        print("À épargner   : 0 (rythme normal tenu)")
    print()
    return 0


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return run(args.used, args.config, date.today())
