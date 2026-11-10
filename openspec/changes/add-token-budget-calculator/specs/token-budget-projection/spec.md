## Purpose

Calculer le reste de tokens du mois à partir de la consommation cumulée saisie par l'utilisateur, et le quota utilisable par jour ouvré restant.

## ADDED Requirements

### Requirement: Saisie de la consommation cumulée
Le système SHALL recevoir en argument le nombre total de tokens utilisés depuis le début du mois, entier positif ou nul, et ne conserver aucun état entre deux exécutions.

#### Scenario: Consommation fournie
- **WHEN** l'utilisateur lance le programme avec 250000 comme tokens utilisés
- **THEN** 250000 est utilisé comme consommation du mois pour les calculs

#### Scenario: Séparateur de milliers
- **WHEN** la valeur est saisie avec un séparateur de milliers régulier, par exemple `12,000` ou `12 000`
- **THEN** elle est interprétée comme 12000

#### Scenario: Valeur invalide ou absente
- **WHEN** la valeur est absente, non entière, négative ou avec un groupement irrégulier (par exemple `12,5`)
- **THEN** le système affiche un message d'usage et se termine avec un code de sortie non nul

### Requirement: Calcul du reste de tokens
Le système SHALL calculer le reste comme `total_tokens` moins la consommation fournie.

#### Scenario: Reste positif
- **WHEN** le total est 1000000 et la consommation 250000
- **THEN** le reste affiché est 750000

#### Scenario: Dépassement
- **WHEN** la consommation dépasse le total
- **THEN** le reste est affiché comme négatif avec un avertissement de dépassement

### Requirement: Quota par jour ouvré restant
Le système SHALL afficher le nombre de tokens à consommer par jour ouvré restant jusqu'à la fin du mois, égal au reste divisé par le nombre de jours ouvrés restants, arrondi à l'entier inférieur.

#### Scenario: Projection standard
- **WHEN** le reste est 750000 et il reste 15 jours ouvrés
- **THEN** le quota par jour affiché est 50000

#### Scenario: Aucun jour ouvré restant
- **WHEN** il ne reste aucun jour ouvré dans le mois
- **THEN** le système affiche le reste sans quota par jour et sans erreur de division

#### Scenario: Reste négatif
- **WHEN** le reste est négatif
- **THEN** aucun quota par jour n'est affiché et l'avertissement de dépassement est montré

### Requirement: Quota normal par jour et ratio
Le système SHALL afficher le quota normal par jour, égal à `total_tokens` divisé par le nombre de jours ouvrés du mois entier (arrondi à l'entier inférieur), et le présenter sous la forme `quota restant par jour / quota normal par jour` accompagnée du ratio en pourcentage.

#### Scenario: Rythme supérieur à la normale
- **WHEN** le total est 1000000, le mois compte 20 jours ouvrés (quota normal 50000) et le quota restant par jour est 40000
- **THEN** le système affiche `40000 / 50000 (80 %)`

#### Scenario: Quota restant indisponible
- **WHEN** aucun quota restant par jour n'est calculable (reste négatif ou aucun jour ouvré restant)
- **THEN** le quota normal par jour est tout de même affiché, sans ratio

#### Scenario: Aucun jour ouvré dans le mois
- **WHEN** le mois entier ne compte aucun jour ouvré
- **THEN** le système l'indique sans erreur de division

### Requirement: Tokens à épargner
Le système SHALL afficher le nombre de tokens à épargner pour tenir le quota normal par jour sur les jours ouvrés restants, égal à `max(0, quota normal × jours ouvrés restants − reste)`.

#### Scenario: En retard sur le rythme normal
- **WHEN** le quota normal est 1500, il reste 14 jours ouvrés et le reste est 20000
- **THEN** le système affiche 1000 tokens à épargner

#### Scenario: Rythme normal tenu
- **WHEN** le reste est supérieur ou égal au quota normal × jours ouvrés restants
- **THEN** le système indique 0 token à épargner

#### Scenario: Reste négatif
- **WHEN** le reste est négatif
- **THEN** le nombre à épargner inclut le dépassement (quota normal × jours ouvrés restants − reste)

#### Scenario: Aucun jour ouvré restant
- **WHEN** il ne reste aucun jour ouvré
- **THEN** aucune information d'épargne n'est affichée
