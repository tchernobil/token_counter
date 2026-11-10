## 1. Configuration

- [x] 1.1 Dans `config.py`, ajouter `exclude_today` (booléen, défaut `false`) à `Config` avec validation stricte du type
- [x] 1.2 Ajouter `exclude_today` à `config.example.json`
- [x] 1.3 Tests : absent, `true`, `false`, valeur non booléenne (`"oui"`, `1`)

## 2. Calcul

- [x] 2.1 Dans `cli.py`, compter les jours restants depuis demain si `exclude_today` est vrai, en retournant 0 si demain change de mois
- [x] 2.2 Vérifier que « Par jour » et « À épargner » utilisent le même nombre de jours

## 3. Affichage et documentation

- [x] 3.1 Afficher l'hypothèse (aujourd'hui inclus / exclu) dans la sortie
- [x] 3.2 Tests : jour non ouvrable, dernier jour du mois, cohérence Par jour / À épargner, affichage
- [x] 3.3 Mettre à jour le README (clé `exclude_today` et exemple de sortie)
