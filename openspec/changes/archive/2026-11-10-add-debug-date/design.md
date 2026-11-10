## Context

`cli.main` passe `date.today()` à `run(used, config_path, today)`, qui dérive tout de cette date. `Config` est chargé dans `run`, après le calcul de `today` dans `main`.

## Goals / Non-Goals

**Goals:**
- Date simulée par option CLI ou JSON, sans changer les fonctions de calcul.

**Non-Goals:**
- Simuler l'heure ou plusieurs dates.

## Decisions

- Précédence CLI > JSON > date réelle, usuelle pour une option qui surcharge un fichier.
- `Config` gagne `debug_date: Optional[date] = None`, validé via `date.fromisoformat` (chaîne uniquement).
- `run` reçoit `today` (date réelle) et `debug_date` (option CLI) ; la date effective est résolue après chargement de la config. Les tests existants appelant `run(used, path, today)` restent valides.
- L'option `--debug_date` est typée par un parseur argparse qui rejette les dates invalides.

## Risks / Trade-offs

- Une `debug_date` oubliée dans `config.json` fausse silencieusement les résultats ; atténué par l'avertissement affiché.
