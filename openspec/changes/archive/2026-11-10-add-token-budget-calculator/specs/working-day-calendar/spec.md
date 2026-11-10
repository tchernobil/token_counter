## Purpose

Déterminer les jours ouvrables du mois en cours et les présenter sous forme de calendrier.

## ADDED Requirements

### Requirement: Calcul des jours ouvrables
Le système SHALL considérer comme ouvrable tout jour du lundi au vendredi qui n'est pas dans la liste des jours fériés.

#### Scenario: Week-end exclu
- **WHEN** un jour tombe un samedi ou un dimanche
- **THEN** il n'est pas compté comme ouvrable

#### Scenario: Jour férié en semaine exclu
- **WHEN** un jour de semaine figure dans `holidays`
- **THEN** il n'est pas compté comme ouvrable

### Requirement: Jours ouvrables restants
Le système SHALL compter les jours ouvrables restants du mois en cours, aujourd'hui inclus s'il est ouvrable, jusqu'au dernier jour du mois.

#### Scenario: Aujourd'hui est ouvrable
- **WHEN** la date du jour est un jour ouvrable
- **THEN** il est inclus dans les jours ouvrables restants

#### Scenario: Aujourd'hui est un jour non ouvrable
- **WHEN** la date du jour est un week-end ou un férié
- **THEN** seuls les jours ouvrables strictement postérieurs sont comptés

### Requirement: Affichage du calendrier du mois
Le système SHALL afficher un calendrier du mois en cours où les week-ends, les jours fériés et la date du jour sont distinguables.

#### Scenario: Calendrier affiché
- **WHEN** l'utilisateur lance le programme
- **THEN** le calendrier du mois est affiché avec un marqueur distinct pour chaque catégorie de jour
