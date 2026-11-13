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
        nargs="?",
        metavar="tokens_utilises",
        help="tokens utilisés depuis le début du mois (demandé en boucle si omis)",
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


LIMIT_REACHED = 2


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

    if budget.remaining <= 0:
        next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
        wait = (next_month - today).days
        unit = "jour" if wait == 1 else "jours"
        print()
        print(
            "* Votre limite de token est déjà dépassée. "
            f"Veuillez attendre {wait} {unit} pour le début du prochain mois."
        )
        print()
        return LIMIT_REACHED

    print(render_month(today, config.holidays, strike=sys.stdout.isatty()))
    print()
    if simulated is not None:
        print(f"Date simulée    : {simulated.isoformat()}")
    print(f"Total           : {_fmt(config.total_tokens)}")
    print(f"Utilisés        : {_fmt(used)}")
    print(f"Restants        : {_fmt(budget.remaining)}")
    scope = "aujourd'hui exclu" if config.exclude_today else "aujourd'hui inclus"
    print(f"Jours ouvrables : {left_days} restants ({scope}) / {month_days} dans le mois")
    if budget.normal_per_day is None:
        print("Aucun jour ouvrable dans le mois.")
        print()
        return 0
    if budget.remaining_per_day is None:
        print(f"Quota normal par jour : {_fmt(budget.normal_per_day)}")
    else:
        print(
            f"Par jour        : {_fmt(budget.remaining_per_day)} / "
            f"{_fmt(budget.normal_per_day)} (quota normal) : {budget.ratio_percent:.0f} %"
        )
    if budget.to_save:
        print(
            f"À épargner      : {_fmt(budget.to_save)} tokens à rattraper "
            f"pour revenir à {_fmt(budget.normal_per_day)}/jour"
        )
        missing = min(budget.to_save / budget.normal_per_day, left_days)
        print(f"Il manquera     : ≈ {missing:.1f} jours avec le quota normal")
    elif budget.to_save == 0:
        print("À épargner      : 0 (rythme normal tenu)")
    print()
    return 0


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    first_prompt = "Nombre de tokens dépensés (q pour quitter) : "
    if args.used is not None:
        status = run(args.used, args.config, date.today(), args.debug_date)
        if status != 0:
            return 0 if status == LIMIT_REACHED else status
        first_prompt = UPDATE_PROMPT
    return interactive(args.config, args.debug_date, first_prompt)


UPDATE_PROMPT = "Update des tokens dépensés (q pour quitter) : "


def interactive(
    config_path: Path, debug_date: Optional[date], prompt: str = UPDATE_PROMPT
) -> int:
    while True:
        try:
            answer = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if answer.lower() in ("q", "quit", "quitter"):
            return 0
        try:
            used = _non_negative_int(answer)
        except argparse.ArgumentTypeError as exc:
            print(f"Erreur : {exc}", file=sys.stderr)
            continue
        status = run(used, config_path, date.today(), debug_date)
        if status != 0:
            return 0 if status == LIMIT_REACHED else status
        prompt = UPDATE_PROMPT
