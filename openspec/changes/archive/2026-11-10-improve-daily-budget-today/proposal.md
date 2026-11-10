## Why

« Par jour » et « À épargner » comptent aujourd'hui comme un jour ouvrable entier à venir, alors que la consommation saisie inclut déjà ce qui a été consommé aujourd'hui. Le quota du jour courant est donc sous-estimé en fin de journée (ou surestimé en début de journée), et la projection devient trompeuse quand la journée est terminée.

## What Changes

- Ajouter le champ booléen facultatif `exclude_today` dans `config.json` : s'il vaut `true`, la journée en cours est considérée comme terminée et les jours restants sont comptés à partir de demain.
- Absent ou `false`, le comportement actuel est conservé (aujourd'hui compte comme jour restant). Aucune option CLI n'est ajoutée.
- Afficher dans la sortie quelle hypothèse est appliquée (« aujourd'hui inclus » / « aujourd'hui exclu »), pour « Par jour » comme pour « À épargner ».
- « À épargner » utilise le même nombre de jours restants que « Par jour ».
- Valider le champ dans la configuration, mettre à jour `config.example.json` et le README.

Hors périmètre : suivi de la consommation par jour (le programme reste sans état), détection automatique de l'heure.

## Capabilities

### New Capabilities
- `today-handling`: choix de compter ou non le jour courant dans les jours ouvrables restants, et son effet sur « Par jour » et « À épargner ».

### Modified Capabilities

## Impact

- `token_counter/config.py` (nouveau champ), `token_counter/cli.py` (passage à `remaining_working_days`, affichage), `config.example.json`, README, tests associés.
- Le spec `token-budget-projection` n'est pas encore synchronisé dans `openspec/specs/` ; ce change le complète via une nouvelle capacité.
