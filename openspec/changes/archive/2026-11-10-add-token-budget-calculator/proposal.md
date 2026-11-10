# Proposal

## Why

Le quota de tokens est défini pour une période (le mois) mais consommé de façon irrégulière. Il manque un outil simple qui, à partir du calendrier et des jours fériés, indique combien de tokens il reste et combien on peut en utiliser par jour ouvrable restant.

## What Changes

- Nouvelle application Python en ligne de commande (CLI).
- Lecture d'un `config.json` contenant le total de tokens du mois et la liste des jours fériés.
- L'utilisateur fournit en argument les tokens utilisés depuis le début du mois (aucune persistance, pas de commande d'ajout).
- Calcul des jours ouvrables (lun-ven, hors jours fériés) du mois en cours, y compris les jours restants.
- Affichage du reste de tokens et de la projection par jour ouvrable restant, avec un calendrier du mois marquant week-ends, fériés et aujourd'hui.

## Capabilities

### New Capabilities

- `token-budget-config`: chargement et validation de `config.json` (total de tokens, jours fériés).
- `working-day-calendar`: calcul des jours ouvrables du mois en cours et affichage du calendrier.
- `token-budget-projection`: calcul du reste de tokens, du quota par jour ouvrable restant et de son ratio par rapport au quota normal par jour.

### Modified Capabilities

(aucune)

## Impact

- Nouveau code Python (package + point d'entrée CLI) dans ce dépôt, sans dépendance externe obligatoire (bibliothèque standard).
- Nouveau fichier utilisateur : `config.json` (exemple fourni).
- Aucun impact sur du code existant (dépôt vide hormis le README).

## Hypothèses

- Période = mois calendaire en cours ; la consommation saisie est cumulée depuis le 1er du mois.
- Week-ends exclus (lun-ven ouvrables).
- Le jour courant compte comme jour ouvrable restant s'il est ouvrable.
