# debug-date Specification

## Purpose
Permettre de simuler la date du jour afin de vérifier le comportement du calcul à une date arbitraire sans attendre cette date.

## Requirements

### Requirement: Clé debug_date dans config.json
Le système SHALL lire la clé facultative `debug_date` de `config.json`, valant `null` (défaut) ou une date `AAAA-MM-JJ`; lorsqu'elle contient une date, celle-ci remplace la date du jour.

#### Scenario: Clé absente ou null
- **WHEN** `debug_date` est absent ou `null`
- **THEN** la date réelle du jour est utilisée

#### Scenario: Date simulée
- **WHEN** `debug_date` vaut `"2026-11-30"`
- **THEN** les jours restants, le calendrier et `exclude_today` sont évalués au 30 novembre 2026

#### Scenario: Valeur invalide
- **WHEN** `debug_date` n'est ni `null` ni une date `AAAA-MM-JJ` valide
- **THEN** le système affiche un message d'erreur explicite et se termine avec un code de sortie non nul

### Requirement: Option --debug_date
Le système SHALL accepter l'option `--debug_date AAAA-MM-JJ` qui prime sur la clé `debug_date` de `config.json`.

#### Scenario: Option et clé présentes
- **WHEN** `config.json` contient `"debug_date": "2026-11-01"` et que l'option vaut `2026-11-20`
- **THEN** la date utilisée est le 20 novembre 2026

#### Scenario: Option invalide
- **WHEN** la valeur de l'option n'est pas une date valide
- **THEN** le système affiche un message d'usage et se termine avec un code de sortie non nul

### Requirement: Avertissement de date simulée
Le système SHALL indiquer dans la sortie la date simulée lorsqu'elle est utilisée.

#### Scenario: Affichage
- **WHEN** une date simulée est utilisée
- **THEN** la sortie contient « Date simulée » suivie de la date
