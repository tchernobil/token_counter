# today-handling Specification

## Purpose
Permettre à l'utilisateur de préciser si le jour courant doit être compté parmi les jours ouvrables restants, afin que « Par jour » et « À épargner » reflètent la réalité de la consommation déjà saisie.

## Requirements

### Requirement: Champ exclude_today dans config.json
Le système SHALL lire le champ booléen facultatif `exclude_today` de `config.json` (défaut `false`); lorsqu'il vaut `true`, les jours ouvrables restants sont comptés à partir du lendemain, aujourd'hui exclu. Sinon, aujourd'hui est compté s'il est ouvrable.

#### Scenario: Champ absent ou false
- **WHEN** aujourd'hui est un jour ouvrable avec 10 jours ouvrables restants aujourd'hui inclus et que `exclude_today` est absent ou `false`
- **THEN** 10 jours restants sont utilisés

#### Scenario: Champ true
- **WHEN** même situation avec `"exclude_today": true`
- **THEN** 9 jours restants sont utilisés

#### Scenario: Aujourd'hui non ouvrable
- **WHEN** aujourd'hui est un week-end ou un férié, quelle que soit la valeur de `exclude_today`
- **THEN** le nombre de jours restants est identique

### Requirement: Valeur invalide
Le système SHALL rejeter un `exclude_today` non booléen.

#### Scenario: Valeur non booléenne
- **WHEN** `exclude_today` vaut `"oui"` ou `1`
- **THEN** le système affiche un message d'erreur explicite et se termine avec un code de sortie non nul

### Requirement: Cohérence Par jour et À épargner
Le système SHALL utiliser le même nombre de jours restants pour « Par jour » et « À épargner ».

#### Scenario: Calcul avec jour terminé
- **WHEN** le reste est 90000, le quota normal 10000 et `exclude_today` à `true` laisse 8 jours
- **THEN** « Par jour » vaut 11250 et « À épargner » vaut 0

### Requirement: Hypothèse affichée
Le système SHALL indiquer dans la sortie si aujourd'hui est inclus ou exclu du décompte des jours restants.

#### Scenario: Affichage
- **WHEN** le programme est lancé avec `exclude_today` à `true`
- **THEN** la sortie mentionne que aujourd'hui est exclu
