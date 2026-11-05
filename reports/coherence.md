# Kohärenzbericht – Stufe 6

Erzeugt: 2026-11-04T22:30:12+00:00 von `pipeline/s06_coherence.py`, rules.yaml 0.13.0. Nicht amtlicher Entwurf: Die Regeln markieren nur; nichts wird umklassifiziert. Entscheidungen über overrides/overrides.csv.

## Kennzahlen

- Geprüft: 34 702 Abschnitte im Arbeitsgebiet (4387.3 km), 24 767 Knoten. Knoten = OSM-Knoten; getrennte Richtungsfahrbahnen sind nicht zusammengefasst (mehrere Knoten je Kreuzung).
- Abschnitte mit mindestens einem Flag: 16 748.

| Regel | Bedeutung | Abschnitte (Arbeitsgebiet) | km | Abschnitte Hamburg (7 Bezirke) | km Hamburg (7 Bezirke) |
| --- | --- | ---: | ---: | ---: | ---: |
| N1 | Durchgängigkeit (GOW-Zug endet ohne Anschluss) | 284 | 33.2 | 283 | 32.8 |
| N2 | Kurze Kategorie-Insel | 75 | 4.8 | 74 | 4.8 |
| N3 | Kleiner Aufenthaltsbereich | 1 271 | 51.2 | 1 271 | 51.2 |
| N4 | Schleichverkehr über ETW | 8 652 | 949.1 | 8 624 | 946.3 |
| N5 | Direkter Übergang ≥ 70 → 30 | 42 | 10.0 | 41 | 9.9 |
| N6 | Knotentyp Soll ≠ Ist | 11 342 | 1148.0 | 11 185 | 1133.5 |
| N7 | Glättungsvorschlag | 75 | 4.8 | 74 | 4.8 |

km mit Flag je Bezirk und Regel:

| Bezirk | km geprüft | N1 | N2 | N3 | N4 | N5 | N6 | N7 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Altona | 620.5 | 2.6 | 0.3 | 4.7 | 151.2 | 0.0 | 138.3 | 0.3 |
| Bergedorf | 209.3 | 4.1 | 0.1 | 0.3 | 17.9 | 0.1 | 35.7 | 0.1 |
| Eimsbüttel | 470.4 | 1.9 | 0.3 | 4.9 | 126.1 | 0.0 | 142.8 | 0.3 |
| Hamburg-Mitte | 881.3 | 9.8 | 1.2 | 24.2 | 144.4 | 6.9 | 275.8 | 1.2 |
| Hamburg-Nord | 563.3 | 5.6 | 0.9 | 9.2 | 195.5 | 1.3 | 207.3 | 0.9 |
| Harburg | 465.2 | 4.5 | 1.3 | 5.9 | 50.1 | 1.5 | 92.7 | 1.3 |
| Wandsbek | 1030.4 | 4.4 | 0.7 | 2.0 | 261.2 | 0.0 | 241.0 | 0.7 |
| ohne Bezirk | 146.9 | 0.4 | 0.1 | 0.0 | 2.8 | 0.1 | 14.5 | 0.1 |

Karte: `reports/coherence_flags.geojson` (EPSG:4326; Ebenen segment, node, area; Eigenschaft `rule`), z. B. in QGIS oder geojson.io öffnen.

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 36526 Abschnitte |
| cat_proposed unverändert (keine Umklassifizierung) | ok | Vergleich mit Eingabe |
| flags nur im Arbeitsgebiet, gültiges JSON mit bekannten Regel-IDs | ok | N1, N2, N3, N4, N5, N6, N7 |

## N1 Durchgängigkeit

Enden von GOW-Zügen (GOW80, GOW50, GOW30): Knoten mit genau einem GOW-Abschnitt. In Ordnung, wenn dort SW anschließt oder die Stadtgrenze höchstens 50 m entfernt ist; am Rand des Arbeitsgebiets nicht prüfbar.

| Status | Enden |
| --- | ---: |
| ok_sw | 23 |
| ok_city_boundary | 20 |
| unknown_area_edge | 11 |
| dead_end | 293 |

Häufigste Straßen mit offenem GOW-Ende:

| Name | Kategorie | Enden |
| --- | --- | ---: |
| Schiffbeker Weg | GOW30 | 5 |
| Hammer Straße | GOW30 | 5 |
| St. Benedictstraße | GOW30 | 4 |
| – | GOW30 | 4 |
| Hannoversche Straße | GOW50 | 4 |
| Langenfelder Damm | GOW30 | 4 |
| Fuhlsbüttler Straße | GOW30 | 4 |
| Möllner Landstraße | GOW30 | 4 |
| Sengelmannstraße | GOW30 | 3 |
| Finkenwerder Straße | GOW50 | 3 |
| Osdorfer Weg | GOW30 | 3 |
| Reinbeker Redder | GOW30 | 3 |
| Stresemannstraße | GOW30 | 3 |
| Pillauer Straße | GOW30 | 2 |
| Osdorfer Weg | GOW50 | 2 |

## N2 Kategorie-Inseln und N7 Glättungsvorschläge

Straßenzug: an Knoten mit Grad 2 immer weiter, an Kreuzungen zum gegenseitig besten Abschnitt mit höchstens 30° Richtungsänderung. Insel = Lauf einer Kategorie unter 200 m zwischen zwei Läufen gleicher anderer Kategorie. 75 Abschnitte (4.8 km).

| Vorschlag (N7) neu ← bisher | Abschnitte |
| --- | ---: |
| ETW30 ← ETW_ERF | 59 |
| ETW_ERF ← ETW30 | 14 |
| GOW30 ← ETW_ERF | 2 |

## N3 Aufenthaltsbereiche

Flächen aus GOW/SW-Linien und Stadtgrenze innerhalb des Arbeitsgebiets: 1175. Davon enthalten 481 mindestens einen ETW-Abschnitt (Aufenthaltsbereiche); die übrigen 694 sind Verkehrsinseln zwischen Richtungsfahrbahnen oder Grünflächen ohne Erschließung und werden nicht bewertet. Vollständig (berühren den Rand des Arbeitsgebiets nicht): 480; davon unter 25 ha: 360 mit 1 271 ETW-Abschnitten. Kompaktheit = 4π·Fläche/Umfang² (1 = Kreis); dafür gibt es noch keine Schwelle (docs/open_questions.md).

| Fläche | ha | Umfang m | Kompaktheit | ETW-Abschnitte | vollständig | unter Schwelle |
| ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1042 | 0.0 | 31 | 0.40 | 1 | ja | ja |
| 936 | 0.0 | 51 | 0.55 | 1 | ja | ja |
| 87 | 0.0 | 46 | 0.71 | 1 | ja | ja |
| 1003 | 0.0 | 51 | 0.64 | 1 | ja | ja |
| 206 | 0.0 | 67 | 0.47 | 1 | ja | ja |
| 217 | 0.0 | 62 | 0.63 | 1 | ja | ja |
| 889 | 0.0 | 76 | 0.46 | 1 | ja | ja |
| 142 | 0.0 | 64 | 0.67 | 2 | ja | ja |
| 764 | 0.0 | 69 | 0.58 | 1 | ja | ja |
| 859 | 0.0 | 65 | 0.67 | 1 | ja | ja |
| 410 | 0.0 | 62 | 0.72 | 1 | ja | ja |
| 492 | 0.0 | 74 | 0.57 | 2 | ja | ja |
| 238 | 0.0 | 64 | 0.79 | 2 | ja | ja |
| 343 | 0.0 | 124 | 0.30 | 1 | ja | ja |
| 964 | 0.0 | 116 | 0.36 | 1 | ja | ja |
| 420 | 0.0 | 80 | 0.76 | 2 | ja | ja |
| 826 | 0.0 | 147 | 0.23 | 1 | ja | ja |
| 379 | 0.0 | 99 | 0.52 | 1 | ja | ja |
| 221 | 0.0 | 144 | 0.25 | 1 | ja | ja |
| 151 | 0.0 | 101 | 0.52 | 7 | ja | ja |
| 491 | 0.0 | 141 | 0.28 | 1 | ja | ja |
| 972 | 0.0 | 87 | 0.77 | 1 | ja | ja |
| 1052 | 0.0 | 172 | 0.21 | 2 | ja | ja |
| 845 | 0.1 | 180 | 0.19 | 1 | ja | ja |
| 691 | 0.1 | 120 | 0.44 | 1 | ja | ja |
| 865 | 0.1 | 125 | 0.41 | 1 | ja | ja |
| 291 | 0.1 | 99 | 0.69 | 1 | ja | ja |
| 911 | 0.1 | 165 | 0.26 | 1 | ja | ja |
| 145 | 0.1 | 157 | 0.29 | 2 | ja | ja |
| 944 | 0.1 | 172 | 0.24 | 1 | ja | ja |
| 909 | 0.1 | 217 | 0.15 | 1 | ja | ja |
| 1090 | 0.1 | 171 | 0.26 | 1 | ja | ja |
| 1148 | 0.1 | 220 | 0.16 | 1 | ja | ja |
| 639 | 0.1 | 201 | 0.20 | 2 | ja | ja |
| 693 | 0.1 | 135 | 0.45 | 1 | ja | ja |
| 586 | 0.1 | 143 | 0.40 | 1 | ja | ja |
| 569 | 0.1 | 157 | 0.33 | 1 | ja | ja |
| 773 | 0.1 | 167 | 0.29 | 1 | ja | ja |
| 1121 | 0.1 | 173 | 0.28 | 1 | ja | ja |
| 479 | 0.1 | 200 | 0.21 | 1 | ja | ja |
| 117 | 0.1 | 175 | 0.27 | 3 | ja | ja |
| 884 | 0.1 | 166 | 0.31 | 1 | ja | ja |
| 900 | 0.1 | 150 | 0.38 | 1 | ja | ja |
| 161 | 0.1 | 144 | 0.41 | 1 | ja | ja |
| 373 | 0.1 | 111 | 0.70 | 12 | ja | ja |
| 893 | 0.1 | 153 | 0.37 | 1 | ja | ja |
| 465 | 0.1 | 176 | 0.28 | 1 | ja | ja |
| 618 | 0.1 | 207 | 0.21 | 2 | ja | ja |
| 301 | 0.1 | 157 | 0.36 | 1 | ja | ja |
| 472 | 0.1 | 166 | 0.33 | 1 | ja | ja |
| 248 | 0.1 | 155 | 0.39 | 1 | ja | ja |
| 678 | 0.1 | 182 | 0.29 | 1 | ja | ja |
| 929 | 0.1 | 164 | 0.36 | 1 | ja | ja |
| 821 | 0.1 | 240 | 0.17 | 1 | ja | ja |
| 950 | 0.1 | 171 | 0.33 | 1 | ja | ja |
| 787 | 0.1 | 200 | 0.24 | 1 | ja | ja |
| 715 | 0.1 | 208 | 0.23 | 2 | ja | ja |
| 104 | 0.1 | 220 | 0.21 | 1 | ja | ja |
| 537 | 0.1 | 224 | 0.21 | 2 | ja | ja |
| 804 | 0.1 | 275 | 0.14 | 2 | ja | ja |
| 470 | 0.1 | 247 | 0.17 | 2 | ja | ja |
| 672 | 0.1 | 180 | 0.32 | 2 | ja | ja |
| 658 | 0.1 | 225 | 0.21 | 1 | ja | ja |
| 432 | 0.1 | 187 | 0.31 | 2 | ja | ja |
| 530 | 0.1 | 203 | 0.26 | 2 | ja | ja |
| 415 | 0.1 | 200 | 0.27 | 2 | ja | ja |
| 207 | 0.1 | 200 | 0.28 | 3 | ja | ja |
| 973 | 0.1 | 210 | 0.25 | 2 | ja | ja |
| 927 | 0.1 | 274 | 0.15 | 3 | ja | ja |
| 863 | 0.1 | 312 | 0.12 | 2 | ja | ja |
| 52 | 0.1 | 273 | 0.16 | 1 | ja | ja |
| 1035 | 0.1 | 310 | 0.13 | 1 | ja | ja |
| 795 | 0.1 | 217 | 0.27 | 1 | ja | ja |
| 723 | 0.1 | 301 | 0.14 | 1 | ja | ja |
| 274 | 0.1 | 252 | 0.20 | 2 | ja | ja |
| 313 | 0.1 | 233 | 0.24 | 1 | ja | ja |
| 663 | 0.1 | 223 | 0.26 | 1 | ja | ja |
| 641 | 0.1 | 269 | 0.18 | 2 | ja | ja |
| 730 | 0.1 | 217 | 0.28 | 1 | ja | ja |
| 697 | 0.1 | 280 | 0.17 | 1 | ja | ja |
| 1097 | 0.1 | 288 | 0.16 | 1 | ja | ja |
| 876 | 0.1 | 220 | 0.28 | 1 | ja | ja |
| 583 | 0.1 | 250 | 0.22 | 1 | ja | ja |
| 664 | 0.1 | 288 | 0.17 | 2 | ja | ja |
| 798 | 0.1 | 264 | 0.20 | 1 | ja | ja |
| 401 | 0.1 | 261 | 0.21 | 1 | ja | ja |
| 775 | 0.1 | 249 | 0.23 | 2 | ja | ja |
| 656 | 0.1 | 290 | 0.17 | 3 | ja | ja |
| 948 | 0.1 | 290 | 0.17 | 1 | ja | ja |
| 1125 | 0.1 | 143 | 0.71 | 1 | ja | ja |
| 398 | 0.1 | 197 | 0.38 | 1 | ja | ja |
| 615 | 0.1 | 265 | 0.21 | 1 | ja | ja |
| 233 | 0.1 | 281 | 0.19 | 1 | ja | ja |
| 947 | 0.1 | 379 | 0.11 | 2 | ja | ja |
| 1091 | 0.1 | 331 | 0.14 | 1 | ja | ja |
| 448 | 0.1 | 274 | 0.21 | 2 | ja | ja |
| 777 | 0.1 | 324 | 0.15 | 2 | ja | ja |
| 585 | 0.1 | 297 | 0.18 | 2 | ja | ja |
| 879 | 0.1 | 202 | 0.39 | 2 | ja | ja |
| 78 | 0.1 | 314 | 0.16 | 1 | ja | ja |
| 351 | 0.1 | 228 | 0.31 | 1 | ja | ja |
| 949 | 0.1 | 347 | 0.13 | 1 | ja | ja |
| 581 | 0.1 | 312 | 0.17 | 2 | ja | ja |
| 62 | 0.1 | 302 | 0.18 | 2 | ja | ja |
| 638 | 0.1 | 271 | 0.22 | 1 | ja | ja |
| 1085 | 0.1 | 300 | 0.18 | 1 | ja | ja |
| 616 | 0.1 | 295 | 0.19 | 1 | ja | ja |
| 793 | 0.1 | 260 | 0.24 | 1 | ja | ja |
| 566 | 0.1 | 264 | 0.24 | 1 | ja | ja |
| 606 | 0.1 | 265 | 0.23 | 1 | ja | ja |
| 877 | 0.1 | 185 | 0.48 | 2 | ja | ja |
| 505 | 0.1 | 248 | 0.27 | 2 | ja | ja |
| 882 | 0.1 | 284 | 0.21 | 1 | ja | ja |
| 1102 | 0.1 | 273 | 0.23 | 1 | ja | ja |
| 126 | 0.1 | 298 | 0.20 | 1 | ja | ja |
| 961 | 0.1 | 251 | 0.28 | 1 | ja | ja |
| 540 | 0.1 | 331 | 0.16 | 1 | ja | ja |
| 637 | 0.1 | 323 | 0.17 | 1 | ja | ja |
| 513 | 0.1 | 323 | 0.17 | 2 | ja | ja |
| 685 | 0.1 | 234 | 0.33 | 1 | ja | ja |
| 342 | 0.1 | 294 | 0.21 | 2 | ja | ja |
| 1006 | 0.1 | 348 | 0.15 | 1 | ja | ja |
| 385 | 0.1 | 296 | 0.21 | 2 | ja | ja |
| 280 | 0.1 | 313 | 0.18 | 2 | ja | ja |
| 462 | 0.1 | 273 | 0.25 | 1 | ja | ja |
| 817 | 0.1 | 322 | 0.18 | 1 | ja | ja |
| 273 | 0.2 | 317 | 0.19 | 1 | ja | ja |
| 712 | 0.2 | 279 | 0.25 | 1 | ja | ja |
| 653 | 0.2 | 306 | 0.21 | 1 | ja | ja |
| 645 | 0.2 | 360 | 0.15 | 1 | ja | ja |
| 194 | 0.2 | 321 | 0.19 | 1 | ja | ja |
| 42 | 0.2 | 340 | 0.17 | 2 | ja | ja |
| 943 | 0.2 | 314 | 0.20 | 2 | ja | ja |
| 57 | 0.2 | 373 | 0.15 | 2 | ja | ja |
| 63 | 0.2 | 349 | 0.17 | 3 | ja | ja |
| 709 | 0.2 | 456 | 0.10 | 1 | ja | ja |
| 694 | 0.2 | 331 | 0.19 | 2 | ja | ja |
| 763 | 0.2 | 366 | 0.16 | 2 | ja | ja |
| 55 | 0.2 | 356 | 0.17 | 2 | ja | ja |
| 844 | 0.2 | 360 | 0.16 | 1 | ja | ja |
| 400 | 0.2 | 467 | 0.10 | 2 | ja | ja |
| 714 | 0.2 | 284 | 0.27 | 1 | ja | ja |
| 480 | 0.2 | 319 | 0.22 | 2 | ja | ja |
| 1126 | 0.2 | 389 | 0.15 | 1 | ja | ja |
| 89 | 0.2 | 356 | 0.17 | 1 | ja | ja |
| 412 | 0.2 | 359 | 0.17 | 3 | ja | ja |
| 237 | 0.2 | 264 | 0.32 | 2 | ja | ja |
| 833 | 0.2 | 413 | 0.13 | 2 | ja | ja |
| 970 | 0.2 | 383 | 0.15 | 4 | ja | ja |
| 731 | 0.2 | 387 | 0.15 | 1 | ja | ja |
| 683 | 0.2 | 353 | 0.18 | 2 | ja | ja |
| 1089 | 0.2 | 317 | 0.23 | 1 | ja | ja |
| 766 | 0.2 | 324 | 0.22 | 1 | ja | ja |
| 83 | 0.2 | 432 | 0.13 | 2 | ja | ja |
| 257 | 0.2 | 393 | 0.15 | 1 | ja | ja |
| 528 | 0.2 | 357 | 0.19 | 3 | ja | ja |
| 489 | 0.2 | 441 | 0.12 | 1 | ja | ja |
| 556 | 0.2 | 392 | 0.15 | 1 | ja | ja |
| 362 | 0.2 | 325 | 0.23 | 3 | ja | ja |
| 852 | 0.2 | 426 | 0.14 | 1 | ja | ja |
| 796 | 0.2 | 465 | 0.12 | 1 | ja | ja |
| 389 | 0.2 | 182 | 0.76 | 1 | ja | ja |
| 701 | 0.2 | 419 | 0.14 | 2 | ja | ja |
| 348 | 0.2 | 398 | 0.16 | 1 | ja | ja |
| 405 | 0.2 | 337 | 0.23 | 1 | ja | ja |
| 309 | 0.2 | 417 | 0.15 | 1 | ja | ja |
| 11 | 0.2 | 414 | 0.16 | 2 | ja | ja |
| 60 | 0.2 | 445 | 0.14 | 1 | ja | ja |
| 387 | 0.2 | 541 | 0.10 | 2 | ja | ja |
| 1083 | 0.2 | 523 | 0.11 | 1 | ja | ja |
| 164 | 0.2 | 623 | 0.07 | 3 | ja | ja |
| 655 | 0.2 | 356 | 0.23 | 1 | ja | ja |
| 236 | 0.2 | 412 | 0.17 | 1 | ja | ja |
| 399 | 0.2 | 497 | 0.12 | 2 | ja | ja |
| 939 | 0.2 | 467 | 0.14 | 2 | ja | ja |
| 90 | 0.3 | 246 | 0.52 | 1 | ja | ja |
| 953 | 0.3 | 459 | 0.15 | 2 | ja | ja |
| 276 | 0.3 | 591 | 0.09 | 1 | ja | ja |
| 433 | 0.3 | 711 | 0.07 | 2 | ja | ja |
| 755 | 0.3 | 603 | 0.09 | 2 | ja | ja |
| 861 | 0.3 | 561 | 0.11 | 2 | ja | ja |
| 94 | 0.3 | 405 | 0.21 | 4 | ja | ja |
| 753 | 0.3 | 559 | 0.11 | 2 | ja | ja |
| 392 | 0.3 | 583 | 0.10 | 2 | ja | ja |
| 1040 | 0.3 | 583 | 0.10 | 2 | ja | ja |
| 360 | 0.3 | 600 | 0.10 | 3 | ja | ja |
| 806 | 0.3 | 463 | 0.17 | 2 | ja | ja |
| 108 | 0.3 | 514 | 0.14 | 1 | ja | ja |
| 452 | 0.3 | 524 | 0.14 | 4 | ja | ja |
| 657 | 0.3 | 706 | 0.08 | 5 | ja | ja |
| 138 | 0.3 | 542 | 0.13 | 2 | ja | ja |
| 295 | 0.3 | 674 | 0.09 | 4 | ja | ja |
| 544 | 0.3 | 742 | 0.07 | 2 | ja | ja |
| 820 | 0.3 | 448 | 0.20 | 2 | ja | ja |
| 722 | 0.3 | 623 | 0.11 | 1 | ja | ja |
| 560 | 0.3 | 650 | 0.10 | 3 | ja | ja |
| 413 | 0.3 | 487 | 0.18 | 1 | ja | ja |
| 154 | 0.3 | 706 | 0.09 | 4 | ja | ja |
| 903 | 0.4 | 578 | 0.13 | 4 | ja | ja |
| 67 | 0.4 | 642 | 0.11 | 3 | ja | ja |
| 1018 | 0.4 | 532 | 0.16 | 1 | ja | ja |
| 597 | 0.4 | 694 | 0.10 | 1 | ja | ja |
| 562 | 0.4 | 484 | 0.20 | 2 | ja | ja |
| 127 | 0.4 | 556 | 0.15 | 2 | ja | ja |
| 99 | 0.4 | 686 | 0.10 | 7 | ja | ja |
| 192 | 0.4 | 660 | 0.11 | 3 | ja | ja |
| 102 | 0.4 | 843 | 0.07 | 2 | ja | ja |
| 919 | 0.4 | 822 | 0.07 | 1 | ja | ja |
| 438 | 0.4 | 723 | 0.10 | 2 | ja | ja |
| 353 | 0.4 | 961 | 0.06 | 1 | ja | ja |
| 588 | 0.4 | 634 | 0.13 | 1 | ja | ja |
| 896 | 0.4 | 277 | 0.69 | 1 | ja | ja |
| 559 | 0.4 | 626 | 0.14 | 4 | ja | ja |
| 1023 | 0.4 | 306 | 0.57 | 2 | ja | ja |
| 471 | 0.4 | 726 | 0.10 | 6 | ja | ja |
| 498 | 0.4 | 757 | 0.10 | 7 | ja | ja |
| 486 | 0.4 | 993 | 0.06 | 1 | ja | ja |
| 289 | 0.4 | 1204 | 0.04 | 1 | ja | ja |
| 632 | 0.4 | 795 | 0.09 | 2 | ja | ja |
| 129 | 0.4 | 532 | 0.20 | 1 | ja | ja |
| 582 | 0.4 | 682 | 0.12 | 1 | ja | ja |
| 214 | 0.4 | 878 | 0.07 | 3 | ja | ja |
| 886 | 0.5 | 759 | 0.10 | 2 | ja | ja |
| 322 | 0.5 | 1234 | 0.04 | 1 | ja | ja |
| 478 | 0.5 | 1020 | 0.06 | 2 | ja | ja |
| 19 | 0.5 | 987 | 0.06 | 2 | ja | ja |
| 329 | 0.5 | 679 | 0.13 | 5 | ja | ja |
| 333 | 0.5 | 957 | 0.07 | 3 | ja | ja |
| 475 | 0.5 | 807 | 0.10 | 2 | ja | ja |
| 464 | 0.5 | 918 | 0.08 | 1 | ja | ja |
| 211 | 0.5 | 1140 | 0.05 | 2 | ja | ja |
| 37 | 0.5 | 829 | 0.09 | 8 | ja | ja |
| 945 | 0.5 | 790 | 0.11 | 3 | ja | ja |
| 278 | 0.5 | 774 | 0.11 | 5 | ja | ja |
| 367 | 0.6 | 988 | 0.07 | 7 | ja | ja |
| 109 | 0.6 | 902 | 0.09 | 1 | ja | ja |
| 315 | 0.6 | 937 | 0.08 | 4 | ja | ja |
| 671 | 0.6 | 943 | 0.08 | 1 | ja | ja |
| 203 | 0.6 | 1014 | 0.07 | 4 | ja | ja |
| 532 | 0.6 | 921 | 0.09 | 6 | ja | ja |
| 378 | 0.6 | 1304 | 0.04 | 3 | ja | ja |
| 414 | 0.6 | 1357 | 0.04 | 2 | ja | ja |
| 818 | 0.6 | 867 | 0.11 | 1 | ja | ja |
| 48 | 0.7 | 1209 | 0.06 | 2 | ja | ja |
| 168 | 0.7 | 997 | 0.08 | 1 | ja | ja |
| 511 | 0.7 | 1368 | 0.05 | 2 | ja | ja |
| 33 | 0.7 | 2112 | 0.02 | 2 | ja | ja |
| 1011 | 0.7 | 341 | 0.78 | 1 | ja | ja |
| 222 | 0.7 | 1313 | 0.05 | 5 | ja | ja |
| 314 | 0.8 | 1231 | 0.06 | 2 | ja | ja |
| 43 | 0.8 | 1529 | 0.04 | 7 | ja | ja |
| 711 | 0.8 | 1445 | 0.05 | 2 | ja | ja |
| 409 | 0.8 | 1912 | 0.03 | 3 | ja | ja |
| 230 | 0.8 | 605 | 0.28 | 1 | ja | ja |
| 457 | 0.8 | 1028 | 0.10 | 3 | ja | ja |
| 735 | 0.8 | 1578 | 0.04 | 1 | ja | ja |
| 339 | 0.8 | 1758 | 0.03 | 2 | ja | ja |
| 914 | 0.8 | 1555 | 0.04 | 2 | ja | ja |
| 219 | 0.9 | 963 | 0.12 | 4 | ja | ja |
| 70 | 0.9 | 1919 | 0.03 | 3 | ja | ja |
| 163 | 0.9 | 1388 | 0.06 | 4 | ja | ja |
| 518 | 0.9 | 1366 | 0.06 | 6 | ja | ja |
| 97 | 0.9 | 1535 | 0.05 | 4 | ja | ja |
| 159 | 0.9 | 1476 | 0.05 | 8 | ja | ja |
| 178 | 0.9 | 1488 | 0.05 | 3 | ja | ja |
| 271 | 0.9 | 1284 | 0.07 | 1 | ja | ja |
| 416 | 0.9 | 865 | 0.16 | 5 | ja | ja |
| 801 | 1.0 | 1819 | 0.04 | 5 | ja | ja |
| 247 | 1.0 | 1276 | 0.08 | 7 | ja | ja |
| 350 | 1.0 | 1988 | 0.03 | 4 | ja | ja |
| 539 | 1.0 | 1789 | 0.04 | 3 | ja | ja |
| 789 | 1.0 | 834 | 0.18 | 1 | ja | ja |
| 318 | 1.0 | 1585 | 0.05 | 5 | ja | ja |
| 8 | 1.0 | 1732 | 0.04 | 6 | ja | ja |
| 13 | 1.1 | 2039 | 0.03 | 7 | ja | ja |
| 334 | 1.1 | 2005 | 0.03 | 4 | ja | ja |
| 828 | 1.1 | 1459 | 0.06 | 3 | ja | ja |
| 468 | 1.1 | 1358 | 0.07 | 2 | ja | ja |
| 587 | 1.1 | 2009 | 0.03 | 6 | ja | ja |
| 231 | 1.1 | 493 | 0.56 | 2 | ja | ja |
| 316 | 1.2 | 776 | 0.24 | 2 | ja | ja |
| 352 | 1.2 | 2230 | 0.03 | 5 | ja | ja |
| 100 | 1.2 | 2717 | 0.02 | 10 | ja | ja |
| 96 | 1.3 | 622 | 0.41 | 3 | ja | ja |
| 18 | 1.3 | 2082 | 0.04 | 3 | ja | ja |
| 193 | 1.3 | 1510 | 0.07 | 4 | ja | ja |
| 396 | 1.3 | 2034 | 0.04 | 7 | ja | ja |
| 429 | 1.3 | 1814 | 0.05 | 3 | ja | ja |
| 218 | 1.4 | 2616 | 0.03 | 9 | ja | ja |
| 388 | 1.4 | 1522 | 0.08 | 1 | ja | ja |
| 215 | 1.4 | 2685 | 0.03 | 6 | ja | ja |
| 196 | 1.5 | 2137 | 0.04 | 2 | ja | ja |
| 195 | 1.5 | 1521 | 0.08 | 3 | ja | ja |
| 554 | 1.5 | 1506 | 0.08 | 2 | ja | ja |
| 188 | 1.6 | 1060 | 0.18 | 1 | ja | ja |
| 201 | 1.7 | 2762 | 0.03 | 6 | ja | ja |
| 887 | 1.7 | 570 | 0.66 | 1 | ja | ja |
| 692 | 1.8 | 1820 | 0.07 | 4 | ja | ja |
| 568 | 1.8 | 1430 | 0.11 | 2 | ja | ja |
| 605 | 1.9 | 3610 | 0.02 | 11 | ja | ja |
| 466 | 1.9 | 676 | 0.53 | 2 | ja | ja |
| 191 | 2.0 | 3262 | 0.02 | 9 | ja | ja |
| 144 | 2.1 | 3020 | 0.03 | 5 | ja | ja |
| 456 | 2.2 | 2567 | 0.04 | 10 | ja | ja |
| 47 | 2.3 | 3657 | 0.02 | 5 | ja | ja |
| 504 | 2.3 | 822 | 0.43 | 3 | ja | ja |
| 363 | 2.3 | 3207 | 0.03 | 1 | ja | ja |
| 137 | 2.5 | 2157 | 0.07 | 6 | ja | ja |
| 335 | 2.6 | 1652 | 0.12 | 12 | ja | ja |
| 269 | 2.6 | 687 | 0.70 | 2 | ja | ja |
| 213 | 2.7 | 4731 | 0.02 | 9 | ja | ja |
| 345 | 2.8 | 4161 | 0.02 | 11 | ja | ja |
| 561 | 2.8 | 2410 | 0.06 | 5 | ja | ja |
| 648 | 2.9 | 836 | 0.52 | 2 | ja | ja |
| 749 | 2.9 | 1815 | 0.11 | 1 | ja | ja |
| 1067 | 3.0 | 698 | 0.77 | 1 | ja | ja |
| 267 | 3.0 | 3339 | 0.03 | 5 | ja | ja |
| 825 | 3.3 | 4132 | 0.02 | 1 | ja | ja |
| 476 | 3.3 | 1317 | 0.24 | 3 | ja | ja |
| 157 | 3.3 | 2742 | 0.06 | 17 | ja | ja |
| 774 | 3.4 | 6112 | 0.01 | 7 | ja | ja |
| 377 | 3.6 | 6609 | 0.01 | 14 | ja | ja |
| 525 | 3.8 | 884 | 0.61 | 3 | ja | ja |
| 924 | 3.8 | 4152 | 0.03 | 2 | ja | ja |
| 254 | 3.8 | 5748 | 0.01 | 1 | ja | ja |
| 533 | 4.3 | 1506 | 0.24 | 10 | ja | ja |
| 765 | 4.9 | 906 | 0.75 | 3 | ja | ja |
| 266 | 5.4 | 2104 | 0.15 | 5 | ja | ja |
| 481 | 5.5 | 1747 | 0.23 | 2 | ja | ja |
| 819 | 5.8 | 1127 | 0.58 | 1 | ja | ja |
| 84 | 6.2 | 2612 | 0.11 | 4 | ja | ja |
| 198 | 7.2 | 1271 | 0.56 | 7 | ja | ja |
| 874 | 7.6 | 1307 | 0.56 | 3 | ja | ja |
| 30 | 7.9 | 1365 | 0.53 | 3 | ja | ja |
| 469 | 7.9 | 1241 | 0.65 | 9 | ja | ja |
| 853 | 8.6 | 1343 | 0.60 | 5 | ja | ja |
| 403 | 8.8 | 1666 | 0.40 | 12 | ja | ja |
| 288 | 9.3 | 1412 | 0.59 | 1 | ja | ja |
| 162 | 9.5 | 1326 | 0.68 | 16 | ja | ja |
| 122 | 9.6 | 1331 | 0.68 | 15 | ja | ja |
| 149 | 10.1 | 1534 | 0.54 | 13 | ja | ja |
| 593 | 10.3 | 1525 | 0.56 | 11 | ja | ja |
| 564 | 10.7 | 1453 | 0.63 | 1 | ja | ja |
| 495 | 11.3 | 1432 | 0.69 | 27 | ja | ja |
| 111 | 11.6 | 1660 | 0.53 | 25 | ja | ja |
| 546 | 12.5 | 1549 | 0.65 | 8 | ja | ja |
| 140 | 12.6 | 2498 | 0.25 | 29 | ja | ja |
| 110 | 12.8 | 1729 | 0.54 | 12 | ja | ja |
| 547 | 13.0 | 1466 | 0.76 | 6 | ja | ja |
| 298 | 14.3 | 1653 | 0.66 | 68 | ja | ja |
| 727 | 14.6 | 1612 | 0.71 | 4 | ja | ja |
| 285 | 15.3 | 2769 | 0.25 | 6 | ja | ja |
| 268 | 15.5 | 1669 | 0.70 | 43 | ja | ja |
| 326 | 16.2 | 1907 | 0.56 | 11 | ja | ja |
| 553 | 16.4 | 2821 | 0.26 | 1 | ja | ja |
| 39 | 16.4 | 2322 | 0.38 | 25 | ja | ja |
| 220 | 18.8 | 1989 | 0.60 | 36 | ja | ja |
| 256 | 19.7 | 2055 | 0.59 | 21 | ja | ja |
| 148 | 19.7 | 2407 | 0.43 | 17 | ja | ja |
| 354 | 21.8 | 2326 | 0.51 | 17 | ja | ja |
| 204 | 25.5 | 2428 | 0.54 | 33 | ja | nein |
| 158 | 26.4 | 2375 | 0.59 | 25 | ja | nein |
| 226 | 27.2 | 2291 | 0.65 | 28 | ja | nein |
| 71 | 27.7 | 2451 | 0.58 | 22 | ja | nein |
| 61 | 28.2 | 2479 | 0.58 | 18 | ja | nein |
| 397 | 29.1 | 2448 | 0.61 | 9 | ja | nein |
| 493 | 29.5 | 2660 | 0.52 | 20 | ja | nein |
| 455 | 29.5 | 2955 | 0.42 | 33 | ja | nein |
| 72 | 34.4 | 3387 | 0.38 | 38 | ja | nein |
| 674 | 34.6 | 2876 | 0.53 | 14 | ja | nein |
| 463 | 35.0 | 2590 | 0.66 | 17 | ja | nein |
| 330 | 35.5 | 2890 | 0.53 | 23 | ja | nein |
| 307 | 36.9 | 2493 | 0.75 | 3 | ja | nein |
| 73 | 37.0 | 3182 | 0.46 | 35 | ja | nein |
| 439 | 40.3 | 3181 | 0.50 | 44 | ja | nein |
| 270 | 40.9 | 2703 | 0.70 | 63 | ja | nein |
| 485 | 41.1 | 2942 | 0.60 | 15 | ja | nein |
| 40 | 41.9 | 2978 | 0.59 | 97 | ja | nein |
| 147 | 42.2 | 3035 | 0.57 | 22 | ja | nein |
| 263 | 43.0 | 2733 | 0.72 | 25 | ja | nein |
| 36 | 46.0 | 2919 | 0.68 | 43 | ja | nein |
| 467 | 46.8 | 2782 | 0.76 | 70 | ja | nein |
| 24 | 47.1 | 2763 | 0.78 | 59 | ja | nein |
| 107 | 47.7 | 3000 | 0.67 | 72 | ja | nein |
| 229 | 50.3 | 3005 | 0.70 | 54 | ja | nein |
| 509 | 51.6 | 2848 | 0.80 | 7 | ja | nein |
| 234 | 52.5 | 3412 | 0.57 | 91 | ja | nein |
| 210 | 54.4 | 3380 | 0.60 | 43 | ja | nein |
| 519 | 55.8 | 3152 | 0.71 | 7 | ja | nein |
| 31 | 56.8 | 3553 | 0.56 | 44 | ja | nein |
| 66 | 57.1 | 3196 | 0.70 | 28 | ja | nein |
| 49 | 57.7 | 3297 | 0.67 | 72 | ja | nein |
| 245 | 57.9 | 3127 | 0.74 | 12 | ja | nein |
| 376 | 61.2 | 3923 | 0.50 | 28 | ja | nein |
| 240 | 63.1 | 3079 | 0.84 | 18 | ja | nein |
| 133 | 64.5 | 3235 | 0.77 | 37 | ja | nein |
| 287 | 67.0 | 3174 | 0.84 | 57 | ja | nein |
| 262 | 67.8 | 3568 | 0.67 | 46 | ja | nein |
| 484 | 73.3 | 3747 | 0.66 | 46 | ja | nein |
| 150 | 74.0 | 3763 | 0.66 | 46 | ja | nein |
| 228 | 75.6 | 3473 | 0.79 | 116 | ja | nein |
| 23 | 76.4 | 3835 | 0.65 | 31 | ja | nein |
| 141 | 83.3 | 3944 | 0.67 | 145 | ja | nein |
| 46 | 84.9 | 5413 | 0.36 | 21 | ja | nein |
| 366 | 92.0 | 4117 | 0.68 | 19 | ja | nein |
| 160 | 92.7 | 3990 | 0.73 | 195 | ja | nein |
| 77 | 100.1 | 4650 | 0.58 | 52 | ja | nein |
| 282 | 107.3 | 4644 | 0.62 | 166 | ja | nein |
| 112 | 108.2 | 4623 | 0.64 | 219 | ja | nein |
| 38 | 111.1 | 4347 | 0.74 | 69 | ja | nein |
| 98 | 113.4 | 4675 | 0.65 | 36 | ja | nein |
| 232 | 116.2 | 5231 | 0.53 | 68 | ja | nein |
| 29 | 119.0 | 5036 | 0.59 | 60 | ja | nein |
| 56 | 122.8 | 5076 | 0.60 | 56 | ja | nein |
| 281 | 127.5 | 5183 | 0.60 | 39 | ja | nein |
| 299 | 129.0 | 5177 | 0.61 | 96 | ja | nein |
| 165 | 130.5 | 5217 | 0.60 | 62 | ja | nein |
| 21 | 133.6 | 4952 | 0.68 | 68 | ja | nein |
| 4 | 135.3 | 5455 | 0.57 | 152 | ja | nein |
| 265 | 135.6 | 4767 | 0.75 | 14 | ja | nein |
| 136 | 141.5 | 5346 | 0.62 | 91 | ja | nein |
| 5 | 141.7 | 5750 | 0.54 | 140 | ja | nein |
| 531 | 154.2 | 5070 | 0.75 | 164 | ja | nein |
| 26 | 158.5 | 5354 | 0.69 | 124 | ja | nein |
| 272 | 159.6 | 5181 | 0.75 | 61 | ja | nein |
| 86 | 165.5 | 6625 | 0.47 | 185 | ja | nein |
| 319 | 165.9 | 5905 | 0.60 | 107 | ja | nein |
| 118 | 172.1 | 6101 | 0.58 | 176 | ja | nein |
| 82 | 178.9 | 5827 | 0.66 | 139 | ja | nein |
| 224 | 183.8 | 5972 | 0.65 | 133 | ja | nein |
| 139 | 185.5 | 7193 | 0.45 | 88 | ja | nein |
| 17 | 187.1 | 5900 | 0.68 | 158 | ja | nein |
| 92 | 199.2 | 7612 | 0.43 | 165 | ja | nein |
| 384 | 204.3 | 6017 | 0.71 | 38 | ja | nein |
| 45 | 208.3 | 7079 | 0.52 | 147 | ja | nein |
| 239 | 210.2 | 5773 | 0.79 | 112 | ja | nein |
| 176 | 220.5 | 6065 | 0.75 | 70 | ja | nein |
| 185 | 245.2 | 7054 | 0.62 | 94 | ja | nein |
| 79 | 266.8 | 6800 | 0.72 | 218 | ja | nein |
| 6 | 270.9 | 9249 | 0.40 | 244 | ja | nein |
| 123 | 273.4 | 8944 | 0.43 | 325 | ja | nein |
| 41 | 277.1 | 6840 | 0.74 | 208 | ja | nein |
| 173 | 285.1 | 10019 | 0.36 | 101 | ja | nein |
| 524 | 288.2 | 7034 | 0.73 | 111 | ja | nein |
| 180 | 294.8 | 9094 | 0.45 | 182 | ja | nein |
| 35 | 303.6 | 8038 | 0.59 | 320 | ja | nein |
| 135 | 315.7 | 8258 | 0.58 | 298 | ja | nein |
| 341 | 316.4 | 8383 | 0.57 | 239 | ja | nein |
| 320 | 327.6 | 8551 | 0.56 | 112 | ja | nein |
| 80 | 366.2 | 8356 | 0.66 | 186 | ja | nein |
| 14 | 380.2 | 9639 | 0.51 | 223 | ja | nein |
| 338 | 382.0 | 8062 | 0.74 | 55 | ja | nein |
| 32 | 393.7 | 18312 | 0.15 | 137 | ja | nein |
| 358 | 397.4 | 7963 | 0.79 | 34 | ja | nein |
| 9 | 398.7 | 9214 | 0.59 | 343 | ja | nein |
| 346 | 406.0 | 8161 | 0.77 | 155 | ja | nein |
| 223 | 410.1 | 8801 | 0.67 | 267 | ja | nein |
| 91 | 424.2 | 10398 | 0.49 | 290 | ja | nein |
| 106 | 426.8 | 9589 | 0.58 | 145 | ja | nein |
| 76 | 429.1 | 12075 | 0.37 | 228 | ja | nein |
| 51 | 433.1 | 8516 | 0.75 | 379 | ja | nein |
| 121 | 464.9 | 12582 | 0.37 | 143 | ja | nein |
| 64 | 466.4 | 8790 | 0.76 | 275 | ja | nein |
| 132 | 481.0 | 10419 | 0.56 | 338 | ja | nein |
| 20 | 491.5 | 10424 | 0.57 | 296 | ja | nein |
| 22 | 537.4 | 9671 | 0.72 | 459 | ja | nein |
| 131 | 541.8 | 9452 | 0.76 | 178 | ja | nein |
| 25 | 560.3 | 10044 | 0.70 | 261 | ja | nein |
| 3 | 566.0 | 10658 | 0.63 | 330 | ja | nein |
| 260 | 616.6 | 11710 | 0.57 | 249 | ja | nein |
| 303 | 666.1 | 19473 | 0.22 | 31 | ja | nein |
| 75 | 679.8 | 10603 | 0.76 | 418 | ja | nein |
| 177 | 681.8 | 18720 | 0.24 | 207 | ja | nein |
| 74 | 865.9 | 12586 | 0.69 | 371 | ja | nein |
| 209 | 1002.4 | 13179 | 0.73 | 500 | ja | nein |
| 328 | 1021.9 | 12957 | 0.76 | 531 | ja | nein |
| 10 | 1051.5 | 14682 | 0.61 | 742 | ja | nein |
| 59 | 1906.2 | 26480 | 0.34 | 509 | ja | nein |
| 105 | 3212.3 | 48501 | 0.17 | 1260 | ja | nein |
| 54 | 7287.9 | 65545 | 0.21 | 2316 | ja | nein |
| 44 | 18069.1 | 259832 | 0.03 | 5483 | nein | nein |

## N4 Schleichverkehr

OD-Knoten: alle 6 378 Knoten des GOW/SW-Netzes (SW, GOW80, GOW50, GOW30) im Arbeitsgebiet; OD-Paare (ungerichtet, verbunden): 20 323 501. Reisezeit mit Soll-Tempo je Kategorie, SW mit travel_speed_kmh; pedestrian gesperrt; ohne Einbahnstraßen (Abschnitte tragen keine Richtung). Wege nur innerhalb des Arbeitsgebiets.

- OD-Paare, deren kürzester Weg mehr als 300 m ETW nutzt: 12 121 990 (59.6 %), obwohl ein Weg nur auf GOW/SW besteht.
- Weitere 4 151 529 OD-Paare sind nur über ETW verbunden (Lücke im GOW/SW-Netz, siehe N1); sie werden gezählt, aber nicht als Schleichverkehr markiert.
- Median Umwegfaktor (Zeit GOW/SW-Weg ÷ kürzester Weg) dieser Paare: 1.06.
- Markierte ETW-Abschnitte: 8 652 (949.1 km). Verteilung der OD-Paare je Abschnitt: 1–99: 1 044, 100–999: 1 641, 1 000–9 999: 3 032, ≥ 10 000: 2 935.
- GOW30 und ETW30 haben dasselbe Soll-Tempo; jeder kürzere Weg durch ETW gewinnt dann. Die Zahl ist deshalb ein Maß für die Durchlässigkeit der Quartiere, kein Verkehrsmodell.

Meistgenutzte ETW-Abschnitte:

| segment_id | Name | Kategorie | OD-Paare |
| --- | --- | --- | ---: |
| `seg_e9ec3c9e7a129798` | Glockengießerwall | ETW30 | 1 052 686 |
| `seg_e08001af1dc9d2aa` | Neuer Jungfernstieg | ETW30 | 862 000 |
| `seg_6d66f592f689dab7` | Alsterglacis | ETW30 | 851 704 |
| `seg_e68acbd4b5e94833` | Hamburger Straße | ETW30 | 771 429 |
| `seg_aa044e1d337211f8` | Hamburger Straße | ETW30 | 767 882 |
| `seg_ccee6b421f935296` | Hamburger Straße | ETW30 | 767 552 |
| `seg_79f13553f9ddf3dc` | Hamburger Straße | ETW30 | 767 552 |
| `seg_4bd7dfa147015be2` | Nedderfeld | ETW30 | 757 148 |
| `seg_16a1ccb1f72e9fa9` | Nedderfeld | ETW30 | 756 199 |
| `seg_a3cb5c6c43a1681a` | Hamburger Straße | ETW30 | 750 609 |
| `seg_0c452a0bae1befeb` | Hamburger Straße | ETW30 | 750 609 |
| `seg_09cfefaad26f45df` | Traute-Lafrenz-Straße | ETW30 | 735 624 |
| `seg_77f8965028a780be` | Suhrenkamp | ETW30 | 725 708 |
| `seg_672fd419ce92319f` | Suhrenkamp | ETW30 | 725 708 |
| `seg_571787c7fb7dac1b` | Suhrenkamp | ETW30 | 725 708 |

## N5 Übergänge

Übergänge, die eine Torsituation brauchen, je Kategoriepaar (Knoten). Ob eine Torsituation vorhanden ist, lässt sich aus den Daten nicht ablesen; die Liste dient der Durchsicht.

| von → nach | Knoten |
| --- | ---: |
| GOW30 → ETW30 | 3 634 |
| GOW50 → ETW30 | 1 415 |
| GOW50 → GOW30 | 666 |
| GOW30 → ETW_ERF | 55 |
| GOW50 → ETW_ERF | 26 |

Direkter Übergang ≥ 70 km/h → 30-km/h-Kategorie (Flag auf der 30-Seite): 39 Knoten, 42 Abschnitte.

## N6 Knotentypen

Knoten mit Grad ≥ 3: 19 984. Ergebnis: not_checkable 14 113, mismatch 4 980, not_defined 813, match 78. Ist aus OSM (5 536 Ampelknoten, 111 Plateaus, 375 Kreisverkehrs-Ways im Umkreis 30 m); none_mapped = nichts davon erfasst. Gehwegüberfahrten sind in OSM nicht erfasst → not_checkable. Eine Ampel im Umkreis kann zur Nachbarkreuzung gehören (v. a. bei ETW-Knoten nahe einer Hauptstraße); Kreisverkehre haben mehrere Knoten.

| Soll \ Ist | none_mapped | plateau | roundabout | signal | signal_plateau |
| --- | ---: | ---: | ---: | ---: | ---: |
| equal_right_before_left | 11 083 | 44 | 350 | 909 | 0 |
| not_defined | 657 | 3 | 5 | 148 | 0 |
| priority_gow_sidewalk_crossover | 391 | 2 | 11 | 501 | 4 |
| roundabout | 366 | 1 | 7 | 651 | 0 |
| roundabout_or_signal_plateau | 400 | 1 | 11 | 446 | 1 |
| sidewalk_crossover | 958 | 4 | 8 | 17 | 1 |
| sidewalk_crossover_or_priority_plateau | 1 229 | 15 | 53 | 1 699 | 8 |

Abweichungen Soll ≠ Ist:

| Soll | Ist | Knoten |
| --- | --- | ---: |
| sidewalk_crossover_or_priority_plateau | signal | 1 699 |
| equal_right_before_left | signal | 909 |
| roundabout | signal | 651 |
| priority_gow_sidewalk_crossover | signal | 501 |
| roundabout_or_signal_plateau | none_mapped | 400 |
| roundabout | none_mapped | 366 |
| equal_right_before_left | roundabout | 350 |
| sidewalk_crossover_or_priority_plateau | roundabout | 53 |
| sidewalk_crossover | signal | 17 |
| priority_gow_sidewalk_crossover | roundabout | 11 |
| sidewalk_crossover | roundabout | 8 |
| sidewalk_crossover_or_priority_plateau | signal_plateau | 8 |
| priority_gow_sidewalk_crossover | signal_plateau | 4 |
| roundabout | plateau | 1 |
| roundabout_or_signal_plateau | plateau | 1 |
| sidewalk_crossover | signal_plateau | 1 |

Kategoriepaare ohne Soll-Knotentyp (Tabelle 1.4 deckt sie nicht ab): ETW_ERF, ETW_ERF (467), SW, SW (165), SW, GOW50 (103), SW, GOW30 (42), SW, ETW30 (36).

## Stichprobe: 30 zufällige markierte Abschnitte in Hamburg (7 Bezirke), nach Bezirk geschichtet (Seed 42)

Fachlich durchsehen: Ist das Flag berechtigt? **Durchsicht: offen.**

| segment_id | Bezirk | Name | Kategorie | m | Flags | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| `seg_0b50233486bb86c5` | Altona | Luruper Hauptstraße | ETW30 | 73 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556564,5939164]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.598248/9.854724) | [Way](https://www.openstreetmap.org/way/759539872) |
| `seg_2fe37e4fd9f94860` | Altona | Plöner Straße | ETW30 | 20 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562191,5935419]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.563954/9.938991) | [Way](https://www.openstreetmap.org/way/407541372) |
| `seg_6a85304a3d431d1f` | Altona | Bahrenfelder Straße | ETW30 | 76 | N4_shortcut | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561517,5934340]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.554341/9.928603) | [Way](https://www.openstreetmap.org/way/1303919985) |
| `seg_77f3d9069a763486` | Altona | Sülldorfer Mühlenweg | ETW30 | 171 | N4_shortcut | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[552377,5936059]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.570779/9.790934) | [Way](https://www.openstreetmap.org/way/22753569) |
| `seg_264968e99847f38a` | Bergedorf | Am Langberg | ETW30 | 39 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577337,5930134]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.514444/10.166325) | [Way](https://www.openstreetmap.org/way/229835347) |
| `seg_3828106cf6d8d11b` | Bergedorf | Lohbrügger Landstraße | ETW30 | 11 | N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578536,5929234]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.506185/10.184179) | [Way](https://www.openstreetmap.org/way/144834318) |
| `seg_1139ca0f7dab9a2a` | Eimsbüttel | Im Gehölz | GOW30 | 199 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563605,5936776]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.575982/9.960618) | [Way](https://www.openstreetmap.org/way/142768217) |
| `seg_29952aa75892f85e` | Eimsbüttel | Harvestehuder Weg | ETW30 | 13 | N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565817,5937216]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.579660/9.994106) | [Way](https://www.openstreetmap.org/way/951751351) |
| `seg_3079fd33586084dd` | Eimsbüttel | Große Bahnstraße | ETW30 | 166 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562023,5936495]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.573650/9.936661) | [Way](https://www.openstreetmap.org/way/1442795377) |
| `seg_caadfc974482539b` | Eimsbüttel | Heußweg | ETW30 | 88 | N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563004,5936739]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.575718/9.951524) | [Way](https://www.openstreetmap.org/way/362847835) |
| `seg_083b5dce2894e98f` | Hamburg-Mitte | Bauerberg | ETW30 | 91 | N4_shortcut | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571539,5934158]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.551430/10.079822) | [Way](https://www.openstreetmap.org/way/22605389) |
| `seg_18ae666ce561e88b` | Hamburg-Mitte | Châu-und-Lân-Straße | ETW30 | 351 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572260,5929923]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.513272/10.089726) | [Way](https://www.openstreetmap.org/way/5012515) |
| `seg_3b69937271eea4df` | Hamburg-Mitte | Speersort | ETW30 | 106 | N3_small_area | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566055,5933913]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.549951/9.997006) | [Way](https://www.openstreetmap.org/way/142944461) |
| `seg_3f6a15d3ca6b40b1` | Hamburg-Mitte | Schmuckstraße | ETW30 | 158 | N3_small_area, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563533,5934024]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.551255/9.958972) | [Way](https://www.openstreetmap.org/way/8816471) |
| `seg_9065481208a2f068` | Hamburg-Mitte | Koreastraße | ETW_ERF | 10 | N3_small_area | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566272,5933155]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.543109/10.000125) | [Way](https://www.openstreetmap.org/way/240286626) |
| `seg_abf56fe99956f9c1` | Hamburg-Mitte | Große Bleichen | ETW30 | 62 | N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565336,5934129]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.551983/9.986197) | [Way](https://www.openstreetmap.org/way/252378410) |
| `seg_080b961ca68ce807` | Hamburg-Nord | Poßmoorweg | GOW30 | 93 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566673,5937906]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.585760/10.007180) | [Way](https://www.openstreetmap.org/way/3752938) |
| `seg_3c354f2ec55cb903` | Hamburg-Nord | Kuhmühle | GOW30 | 41 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567842,5935542]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.564366/10.024325) | [Way](https://www.openstreetmap.org/way/76372086) |
| `seg_b28216c96dd966f8` | Hamburg-Nord | Wilhelm-Metzger-Straße | ETW30 | 67 | N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565987,5940044]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.605054/9.997278) | [Way](https://www.openstreetmap.org/way/39517065) |
| `seg_cfb951046ad2fb39` | Hamburg-Nord | Dorotheenstraße | GOW30 | 72 | N1_dead_end, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566580,5937956]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.586222/10.005792) | [Way](https://www.openstreetmap.org/way/598145080) |
| `seg_e6ff2a1f5ca22a3d` | Hamburg-Nord | Löwenstraße | ETW30 | 108 | N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564514,5937903]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.585998/9.974566) | [Way](https://www.openstreetmap.org/way/1427554145) |
| `seg_62752fce169bd5d2` | Harburg | Bremer Straße | ETW_ERF | 75 | N3_small_area | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565225,5923747]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.458684/9.982357) | [Way](https://www.openstreetmap.org/way/21730104) |
| `seg_bfa6f44537eb7ee1` | Harburg | Kleiner Schippsee | ETW30 | 161 | N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565261,5924060]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.461500/9.982964) | [Way](https://www.openstreetmap.org/way/1103379676) |
| `seg_f9be3683e77d3192` | Harburg | Harburger Rathausplatz | ETW30 | 80 | N3_small_area, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564963,5923763]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.458864/9.978424) | [Way](https://www.openstreetmap.org/way/4845119) |
| `seg_025f1bdc9b7b0dd8` | Wandsbek | Saseler Weg | ETW30 | 51 | N4_shortcut | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575724,5945045]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.648680/10.145624) | [Way](https://www.openstreetmap.org/way/1194829208) |
| `seg_577f4d0e43cd1491` | Wandsbek | Wandsbeker Chaussee | GOW30 | 176 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570034,5936176]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.569770/10.057562) | [Way](https://www.openstreetmap.org/way/24273347) |
| `seg_8c6ea891cb7436db` | Wandsbek | Rahlstedter Weg | GOW30 | 185 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574607,5939952]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.603076/10.127500) | [Way](https://www.openstreetmap.org/way/1139026495) |
| `seg_b4de8134a1d652a8` | Wandsbek | Richardstraße | ETW30 | 108 | N4_shortcut | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568813,5935991]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.568274/10.039079) | [Way](https://www.openstreetmap.org/way/52888266) |
| `seg_e68aee8d82f76452` | Wandsbek | Berner Brücke | GOW50 | 11 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575626,5942671]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.627362/10.143556) | [Way](https://www.openstreetmap.org/way/1481639925) |
| `seg_f59d618e5513bc04` | Wandsbek | Tegelweg | ETW30 | 102 | N4_shortcut | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573386,5939884]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.602640/10.109036) | [Way](https://www.openstreetmap.org/way/41761536) |

## Grenzen

- Alle Parameter mit source_type assumption (rules.yaml coherence, thresholds) sind fachlich freizugeben.
- Wege, Flächen und Knoten nur im Arbeitsgebiet (Hamburg (7 Bezirke) + Puffer, ohne Neuwerk); Randeffekte sind ausgewiesen.
- Ungerichteter Graph; Abbiegeverbote, Einbahnstraßen und Zufahrtsbeschränkungen fehlen (N4).
- N3 berücksichtigt keine Barrieren wie Bahn, Gewässer oder Parks.

## Korrekturebene (Stufe 6b)

Erzeugt: 2026-11-04T22:30:15+00:00 von `pipeline/s06b_overrides.py`, rules.yaml 0.13.0. Quelle: `overrides/overrides.csv`; übernommen wird nur review_status = approved. cat_proposed bleibt unverändert, cat_final steht daneben.

| review_status | Einträge |
| --- | ---: |
| draft | 0 |
| approved | 7 |
| rejected | 0 |

Alle 7 Einträge geprüft: keine verwaisten segment_id, gültige Kategorien, Begründung, Autor*in und Datum vorhanden.

Übernommene Korrekturen: 7.

| segment_id | Name | cat_proposed | cat_final | Begründung | Autor*in | Datum | Quelle |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `seg_1f198f1e1b5d0780` | – | ETW_ERF | ETW_ERF | Fußweg (highway=pedestrian, 14 m) an einer Hauptverkehrsstraße in Hamburg-Mitte: ETW_ERF bestätigt. in_hvs ist ein Abgleichfehler mit der DTV-Linie der benachbarten Fahrbahn. Befund aus Datenanalyse, Ortsprüfung offen. | prstolpe | 2026-11-04 | reports/classification.md; tests/test_classification_data.py::test_hvs_is_never_etw |
| `seg_3129d58aeb9c8e41` | Reeperbahn | ETW_ERF | GOW30 | Reeperbahn (HVS, DTV 32 000): verkehrsberuhigt stammt aus einem benachbarten verkehrsberuhigten Bereich im Abgleichspuffer (S-CONF-02); ohne diesen Auslöser ergibt die Kaskade GOW30 (C-GOW-01, C-G30-01). Befund aus Datenanalyse, Ortsprüfung offen. | prstolpe | 2026-11-04 | reports/classification.md; tests/test_classification_data.py::test_hvs_is_never_etw |
| `seg_3b1d68013e44c2c9` | Sengelmannstraße | ETW_ERF | GOW30 | Sengelmannstraße Hauptfahrbahn (primary, HVS, DTV 37 000): verkehrsberuhigt stammt von der parallelen Nebenfahrbahn (living_street) im Abgleichspuffer; ohne diesen Auslöser ergibt die Kaskade GOW30 (Schule/Kita 33 m, C-G30-01). Befund aus Datenanalyse, Ortsprüfung offen. | prstolpe | 2026-11-04 | reports/classification.md; tests/test_classification_data.py::test_hvs_is_never_etw |
| `seg_40851df2d6b8c9c6` | – | ETW_ERF | ETW_ERF | Fußweg (highway=pedestrian, 18 m) an einer Hauptverkehrsstraße in Hamburg-Mitte: ETW_ERF bestätigt. in_hvs ist ein Abgleichfehler mit der DTV-Linie der benachbarten Fahrbahn. Befund aus Datenanalyse, Ortsprüfung offen. | prstolpe | 2026-11-04 | reports/classification.md; tests/test_classification_data.py::test_hvs_is_never_etw |
| `seg_59a776f5fc709026` | Sengelmannstraße | ETW_ERF | ETW_ERF | Sengelmannstraße Nebenfahrbahn (living_street, amtlich verkehrsberuhigter Bereich): ETW_ERF bestätigt. in_hvs ist ein Abgleichfehler mit der DTV-Linie der parallelen Hauptfahrbahn. Befund aus Datenanalyse, Ortsprüfung offen. | prstolpe | 2026-11-04 | reports/classification.md; tests/test_classification_data.py::test_hvs_is_never_etw |
| `seg_d3f1c9d7bc9154ef` | – | ETW_ERF | ETW_ERF | Fußweg (highway=pedestrian, 35 m) an einer Hauptverkehrsstraße in Hamburg-Mitte: ETW_ERF bestätigt. in_hvs ist ein Abgleichfehler mit der DTV-Linie der benachbarten Fahrbahn. Befund aus Datenanalyse, Ortsprüfung offen. | prstolpe | 2026-11-04 | reports/classification.md; tests/test_classification_data.py::test_hvs_is_never_etw |
| `seg_db46e742a775ea22` | – | ETW_ERF | ETW_ERF | Fußweg (highway=pedestrian, 22 m) an einer Hauptverkehrsstraße in Hamburg-Mitte: ETW_ERF bestätigt. in_hvs ist ein Abgleichfehler mit der DTV-Linie der benachbarten Fahrbahn. Befund aus Datenanalyse, Ortsprüfung offen. | prstolpe | 2026-11-04 | reports/classification.md; tests/test_classification_data.py::test_hvs_is_never_etw |

Neue Korrekturen: `make override-template IDS="seg_… seg_…"` erzeugt Zeilen mit review_status draft; Begründung eintragen und per Pull Request (Vier-Augen-Prinzip) auf approved setzen.

## Lizenz

Netz, Ampeln, Plateaus, Kreisverkehre, Stadtgrenze: © OpenStreetMap-Beitragende, ODbL 1.0; Kategorien beruhen auf amtlichen Daten der Freien und Hansestadt Hamburg, dl-de/by-2.0 (siehe reports/classification.md). Orthophotos: LGV Hamburg, dl-de/by-2.0.
