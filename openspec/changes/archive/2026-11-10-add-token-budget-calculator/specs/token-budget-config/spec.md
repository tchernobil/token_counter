## Purpose

Définir comment l'application lit sa configuration : le total de tokens du mois et la liste des jours fériés.

## ADDED Requirements

### Requirement: Total de tokens dans config.json
Le système SHALL lire le total de tokens du mois dans le champ `total_tokens` de `config.json`, entier strictement positif.

#### Scenario: Configuration valide
- **WHEN** `config.json` contient `"total_tokens": 1000000`
- **THEN** le total utilisé pour les calculs est 1000000

#### Scenario: Total invalide
- **WHEN** `total_tokens` est absent, non entier ou inférieur ou égal à 0
- **THEN** le système affiche un message d'erreur explicite et se termine avec un code de sortie non nul

### Requirement: Jours fériés dans config.json
Le système SHALL lire la liste des jours fériés dans le champ `holidays` de `config.json`, sous forme de dates `AAAA-MM-JJ`.

#### Scenario: Liste valide
- **WHEN** `holidays` contient `["2026-12-25"]`
- **THEN** le 25 décembre 2026 est traité comme non ouvrable

#### Scenario: Date invalide
- **WHEN** une entrée de `holidays` n'est pas une date `AAAA-MM-JJ` valide
- **THEN** le système signale l'entrée fautive et se termine avec un code de sortie non nul

### Requirement: Fichier de configuration introuvable
Le système SHALL signaler l'absence de `config.json` sans produire de trace d'exécution.

#### Scenario: Fichier absent
- **WHEN** `config.json` n'existe pas au chemin utilisé
- **THEN** le système affiche un message indiquant le chemin attendu et se termine avec un code de sortie non nul
