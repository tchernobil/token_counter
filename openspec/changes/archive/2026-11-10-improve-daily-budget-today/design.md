## Context

`cli.run` appelle `remaining_working_days(today, holidays)` (aujourd'hui inclus) puis `compute_budget`, qui calcule « Par jour » et « À épargner » à partir de ce même nombre de jours. La consommation saisie contient déjà la consommation partielle du jour. Le programme est sans état. `config.py` valide `total_tokens` et `holidays` et expose un `Config` immuable.

## Goals / Non-Goals

**Goals:**
- Laisser l'utilisateur choisir l'hypothèse sur le jour courant, de façon explicite et visible.
- Garder `compute_budget` inchangé (fonction pure).

**Non-Goals:**
- Suivre la consommation quotidienne ou l'heure de la journée.
- Changer le comportement par défaut.

## Decisions

- Champ `exclude_today` de `config.json` (booléen, défaut `false`, rejet des autres types, `1` compris) plutôt qu'une option CLI ou une heuristique horaire : déterministe, testable, sans état. Conséquence : l'utilisateur modifie le fichier pour changer d'hypothèse. Alternative écartée : basculer automatiquement après une certaine heure (arbitraire).
- Implémentation : `Config` gagne `exclude_today: bool` ; si vrai, le comptage part de `today + 1 jour` (réutilise `remaining_working_days` avec cette date, en restant dans le mois ; au dernier jour du mois, résultat 0).
- Le rendu du calendrier garde la date réelle du jour.

## Risks / Trade-offs

- Le défaut reste « aujourd'hui inclus » : la valeur de début de journée est exacte, celle de fin de journée est sous-estimée tant que `exclude_today` n'est pas activé.
- Passer au mois suivant avec `today + 1` : vérifier que le comptage retourne 0 et non les jours du mois suivant.
