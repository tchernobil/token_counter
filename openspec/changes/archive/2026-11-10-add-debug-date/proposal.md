## Why

Le résultat dépend de la date du jour (jours restants, calendrier, `exclude_today`). Il est impossible de vérifier un scénario (fin de mois, férié, week-end) sans attendre la date réelle.

## What Changes

- Ajouter l'option CLI `--debug_date AAAA-MM-JJ` qui remplace la date du jour pour tous les calculs et le rendu du calendrier.
- Ajouter la clé `debug_date` dans `config.json` (`null` par défaut) avec la même sémantique.
- Précédence : l'option CLI prime sur la clé JSON, qui prime sur la date réelle.
- Afficher un avertissement « Date simulée : AAAA-MM-JJ » quand une date simulée est utilisée.
- Mettre à jour `config.example.json` et le README.

Hors périmètre : simulation de l'heure, dates multiples.

## Capabilities

### New Capabilities
- `debug-date`: simulation de la date du jour via option CLI ou configuration.

### Modified Capabilities

## Impact

`token_counter/config.py`, `token_counter/cli.py`, `config.example.json`, README, tests.
