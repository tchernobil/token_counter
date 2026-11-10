## Context

Dépôt vide (README uniquement). Besoin : CLI Python locale pour suivre un quota mensuel de tokens. Bibliothèque standard suffisante (`json`, `datetime`, `calendar`, `argparse`).

## Goals / Non-Goals

**Goals:** CLI simple, calculs purs testables, aucune dépendance externe.
**Non-Goals:** interface graphique/web, jours fériés calculés automatiquement, multi-périodes, lecture automatique de la consommation réelle.

## Decisions

- **Structure** : package `token_counter/` avec `config.py` (chargement/validation), `calendar_utils.py` (jours ouvrables, rendu du calendrier), `budget.py` (reste, quota par jour), `cli.py` (argparse), `__main__.py`.
- **Commande unique** : `python -m token_counter <tokens_utilises>` (argument positionnel obligatoire, entier ≥ 0). Option `--config` (défaut `config.json`).
- **Sans état** : aucune persistance ; chaque exécution recalcule tout à partir de l'argument, de la config et de la date du jour.
- **Fonctions pures** : la date du jour est injectée (paramètre `today`) pour tester sans horloge réelle.
- **Calendrier** : rendu texte en tableau (lignes et colonnes `+-|`) via `calendar.monthcalendar`, nom du mois en français (table interne, indépendante de la locale), marqueurs `*` (aujourd'hui), `&` (férié), `.` (week-end) ; pas de couleurs pour rester portable.
- **Arrondi** : quota/jour = division entière du reste positif ; reste négatif => pas de quota, avertissement.
- **Quota normal** : `total_tokens // jours ouvrables du mois entier`. Le ratio affiché est `quota restant / quota normal` (en %), sous la forme `X / Y (Z %)` ; > 100 % signifie qu'on peut consommer plus que la normale, < 100 % qu'il faut ralentir.
- **Tests** : `pytest` ou `unittest` sur les fonctions pures ; `unittest` retenu pour éviter une dépendance.

## Risks / Trade-offs

- Jours fériés saisis à la main : à mettre à jour chaque année (acceptable, choix utilisateur).
- Consommation saisie manuellement à chaque exécution : à l'utilisateur de fournir la valeur à jour.
- `config.json` à la racine : l'ajouter au `.gitignore` et fournir `config.example.json`.
