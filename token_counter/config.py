import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Config:
    total_tokens: int
    holidays: frozenset[date]


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

    return Config(total_tokens=total, holidays=frozenset(holidays))
