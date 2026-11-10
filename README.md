# token_counter

Calcule combien de tokens il reste à consommer **par jour ouvrable** jusqu'à la fin du mois, comparé au rythme « normal » (total du mois ÷ jours ouvrables du mois).

Python 3.9+, aucune dépendance externe.

## Configuration

Copier l'exemple puis l'adapter :

```bash
cp config.example.json config.json
```

```json
{
  "total_tokens": 1000000,
  "holidays": ["2026-11-11", "2026-12-25"],
  "exclude_today": false,
  "debug_date": null
}
```

- `total_tokens` : total de tokens du mois (entier > 0).
- `holidays` : jours fériés, au format `AAAA-MM-JJ`. Les week-ends (samedi, dimanche) sont toujours exclus.
- `exclude_today` : facultatif, booléen, `false` par défaut. À `true`, la journée en cours est considérée comme terminée et les jours restants sont comptés à partir de demain (à utiliser en fin de journée, la consommation saisie incluant déjà aujourd'hui). Affecte `Par jour` et `À épargner`.
- `debug_date` : facultatif, `null` par défaut. Une date `AAAA-MM-JJ` remplace la date du jour pour tous les calculs (une ligne « Date simulée » est alors affichée). L'option `--debug_date AAAA-MM-JJ` fait de même et prime sur la config.

`config.json` est ignoré par git.

## Utilisation

```bash
python -m token_counter <tokens_utilises_depuis_le_debut_du_mois>
python -m token_counter 250000 --config autre_config.json
python -m token_counter 12,000    # séparateur de milliers accepté : 12000
```

Exemple de sortie :

```

                  Novembre 2026
+------+------+------+------+------+------+------+
|  Di  |  Lu  |  Ma  |  Me  |  Je  |  Ve  |  Sa  |
+------+------+------+------+------+------+------+
|  1.  |  2   |  3   |  4   |  5   |  6   |  7.  |
+------+------+------+------+------+------+------+
|  8.  |  9   | 10*  | 11&  | 12   | 13   | 14.  |
+------+------+------+------+------+------+------+
| 15.  | 16   | 17   | 18   | 19   | 20   | 21.  |
+------+------+------+------+------+------+------+
| 22.  | 23   | 24   | 25   | 26   | 27   | 28.  |
+------+------+------+------+------+------+------+
| 29.  | 30   |      |      |      |      |      |
+------+------+------+------+------+------+------+
(* aujourd'hui, & férié, . week-end)

Total           : 1 000 000
Utilisés        : 250 000
Restants        : 750 000
Jours ouvrables : 14 restants (aujourd'hui inclus) / 20 dans le mois
Par jour        : 53 571 / 50 000 (107 %)
À épargner      : 0 (rythme normal tenu)

```

La ligne `À épargner` donne le nombre de tokens à ne pas consommer pour tenir le quota normal par jour jusqu'à la fin du mois : `max(0, quota normal × jours ouvrables restants − restants)`.

La ligne `Par jour` se lit « quota restant par jour / quota normal par jour (ratio) » : au-dessus de 100 %, vous pouvez consommer plus que la normale ; en dessous, il faut ralentir. Par défaut le jour courant compte comme restant s'il est ouvrable (voir `exclude_today`). Si le total est dépassé, un avertissement est affiché et aucun quota par jour n'est calculé.

Aucun état n'est conservé : chaque exécution recalcule tout à partir du nombre saisi, de la config et de la date du jour.

## Tests

```bash
python -m unittest discover -s tests -t .
```

## Spécifications

Le comportement est décrit avec [OpenSpec](https://github.com/Fission-AI/OpenSpec) dans `openspec/`.
