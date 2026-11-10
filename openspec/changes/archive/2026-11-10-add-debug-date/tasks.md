## 1. Configuration

- [x] 1.1 Dans `config.py`, ajouter `debug_date` (`None` par défaut) à `Config` avec validation `AAAA-MM-JJ`
- [x] 1.2 Ajouter `"debug_date": null` à `config.example.json`
- [x] 1.3 Tests : absent, `null`, date valide, valeurs invalides

## 2. CLI

- [x] 2.1 Ajouter l'option `--debug_date` (validation de date) et la précédence CLI > JSON > date réelle dans `run`
- [x] 2.2 Afficher « Date simulée : AAAA-MM-JJ » quand une date simulée est utilisée
- [x] 2.3 Tests : précédence, option invalide, avertissement

## 3. Documentation

- [x] 3.1 Documenter la clé et l'option dans le README
