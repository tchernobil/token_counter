## 1. Structure du projet

- [x] 1.1 Créer le package `token_counter/` (`__init__.py`, `__main__.py`) et `config.example.json` (`total_tokens`, `holidays`)
- [x] 1.2 Ajouter `config.json` au `.gitignore`

## 2. Configuration

- [x] 2.1 Implémenter `config.py` : chargement de `config.json`, validation de `total_tokens` et `holidays`, erreurs explicites
- [x] 2.2 Tests unitaires : config valide, total invalide, date invalide, fichier absent

## 3. Calendrier

- [x] 3.1 Implémenter `calendar_utils.py` : jour ouvré, jours ouvrés restants (aujourd'hui inclus), rendu du calendrier du mois
- [x] 3.2 Tests unitaires : week-end, férié, aujourd'hui ouvré / non ouvré, fin de mois

## 4. Budget

- [x] 4.1 Implémenter `budget.py` : reste, quota par jour restant, quota normal par jour, ratio et tokens à épargner (fonctions pures)
- [x] 4.2 Tests unitaires : reste positif, dépassement, aucun jour restant, arrondi, ratio, mois sans jour ouvré

## 5. CLI

- [x] 5.1 Implémenter `cli.py` : argument positionnel `<tokens_utilises>` (entier ≥ 0, validé), option `--config`, codes de sortie
- [x] 5.2 Réécrire entièrement le README (présentation, installation, configuration, usage, exemple de sortie)
- [x] 5.3 Vérification manuelle de bout en bout avec un `config.json` d'exemple
