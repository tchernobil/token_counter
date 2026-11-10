import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Config:
    total_tokens: int
    holidays: frozenset[date]
    exclude_today: bool = False
    debug_date: Optional[date] = None


def load_config(path: Path) -> Config:
    path = Path(path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ConfigError(f"Fichier de configuration introuvable : {path}") from None
    except json.JSONDecodeError as exc:
        raise ConfigError(f"JSON invalide dans {path} : {exc}") from None

    if not isinstance(raw, dict):
        raise ConfigError(f"{path} doit contenir un objet JSON")

    total = raw.get("total_tokens")
    if isinstance(total, bool) or not isinstance(total, int) or total <= 0:
        raise ConfigError("'total_tokens' doit être un entier strictement positif")

    holidays_raw = raw.get("holidays", [])
    if not isinstance(holidays_raw, list):
        raise ConfigError("'holidays' doit être une liste de dates AAAA-MM-JJ")

    holidays = set()
    for entry in holidays_raw:
        try:
            if not isinstance(entry, str):
                raise ValueError
            holidays.add(date.fromisoformat(entry))
        except ValueError:
            raise ConfigError(
                f"Jour férié invalide : {entry!r} (format attendu AAAA-MM-JJ)"
            ) from None

    exclude_today = raw.get("exclude_today", False)
    if not isinstance(exclude_today, bool):
        raise ConfigError("'exclude_today' doit être un booléen (true ou false)")

    debug_raw = raw.get("debug_date")
    debug_date = None
    if debug_raw is not None:
        try:
            if not isinstance(debug_raw, str):
                raise ValueError
            debug_date = date.fromisoformat(debug_raw)
        except ValueError:
            raise ConfigError(
                f"'debug_date' invalide : {debug_raw!r} (format attendu AAAA-MM-JJ ou null)"
            ) from None

    return Config(
        total_tokens=total,
        holidays=frozenset(holidays),
        exclude_today=exclude_today,
        debug_date=debug_date,
    )
