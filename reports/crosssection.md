# Querschnittsbericht – Stufe 7

Erzeugt: 2026-11-04T20:36:13+00:00 von `pipeline/s07_crosssection.py`, rules.yaml 0.12.0. Nicht amtlicher Entwurf.

## Kennzahlen

- Abschnitte im Arbeitsgebiet: 4 947 (573.4 km); im Bezirk Eimsbüttel: 4 004
- Transekte: 28 618 (alle 20 m, ± 40 m, Tangente ± 10 m, Mittellinie vereinfacht 2 m)
- Verworfen: nahe Knoten (≤ 20 m) 31.1 %, Brücke/Tunnel 1.1 %
- Verkehrsfläche: gültig 60.4 %; Mittelpunkt außerhalb der ALKIS-Verkehrsfläche 3.1 %; offen/Platz (keine Grenze in 40 m) 4.4 %
- Fassade: gültig 27.4 %; offen 40.6 %; Mittelpunkt in Gebäude 0.0 %
- Abschnitte mit width_p10_m: 60.3 % (Länge: 85.4 %); mit Fassadenbreite 45.8 %
- Engstellen (≥ 3 Transekte unter p10): 31 in 31 Abschnitten
- ALKIS: 5 193 Verkehrsflächen (Platz, Strassenverkehr, Weg), 52 528 oberirdische Gebäude

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 36526 Abschnitte |
| Breiten positiv | ok | 17291 gültige Transekte Verkehrsfläche |
| min ≤ p10 ≤ Median | ok | 2982 Abschnitte mit Breite |
| transect_id eindeutig | ok | 28618 Transekte |

## Validierung im Orthophoto (Prüfschritt)

50 zufällige gültige Transekte im Bezirk Eimsbüttel (Seed 42) stehen in `reports/transect_sample.geojson` (EPSG:4326, Breite Verkehrsfläche Grenze zu Grenze). Messung im DOP20 eintragen in `reports/transect_measurements.csv` (Spalten `transect_id`, `measured_m`) und Stufe neu laufen lassen.

| Kennzahl | Wert |
| --- | --- |
| gemessene Transekte | _offen_ |
| mittlere absolute Abweichung (Ziel < 1 m, Annahme) | _offen – nach manueller Messung_ |

## Methode

- **Transekte (S-XS-01):** Mittellinie vereinfacht, Transekt alle spacing_m ab spacing_m/2, Richtung senkrecht zur Sehne über ± tangent_half_m.
- **Verkehrsfläche (S-XS-02):** zusammenhängende Strecke des Transekts in ALKIS-Flächen Platz, Strassenverkehr, Weg um den Mittelpunkt; aneinandergrenzende Flächen zählen als eine. `width_p10_m` (für C-G30-02) kommt aus dieser Variante.
- **Fassade (S-XS-03):** Abstand der ersten oberirdischen ALKIS-Gebäude (wie S-FEAT-03) links und rechts.
- **Sonderfälle (S-XS-04):** Knoten = Abschnittsenden mit Grad ≠ 2; Brücken/Tunnel: Mittelpunkt auf einem OSM-Way des Abschnitts mit bridge/tunnel. Offene Transekte gehen nicht in die Statistik ein.
- **Aggregation (S-XS-05):** Median, Quantil 0.1, Minimum; Engstelle = mindestens 3 aufeinanderfolgende gültige Transekte unter dem p10 des Abschnitts.
- **Machbarkeit (S-XS-06):** width_ratio = width_p10_m / erforderliche Breite; GOW50 16.50 m, GOW30_narrow 10.80 m, ETW30 10.80 m (bei Bereichen die Untergrenze). Klassen: fits ≥ 1.00, tight ≥ 0.85, sonst does_not_fit.
- **Fehlerquellen (guide.md 4.3 a):** Straßenflurstücke enthalten Böschungen und Grün; Vorgärten fehlen in der Variante Verkehrsfläche; Versatz der OSM-Mittellinie (→ centre_outside); Arkaden und Durchfahrten.

## Machbarkeit je Soll-Kategorie (Arbeitsgebiet, Anteil der Länge)

| Ziel | erforderlich | fits | tight | does_not_fit | ohne Breite |
| --- | ---: | ---: | ---: | ---: | ---: |
| GOW50 | 16.50 m | 34.4 % | 10.1 % | 40.8 % | 14.6 % |
| GOW30_narrow | 10.80 m | 62.4 % | 9.5 % | 13.5 % | 14.6 % |
| ETW30 | 10.80 m | 62.4 % | 9.5 % | 13.5 % | 14.6 % |

## width_p10_m nach highway-Klasse (Median über Abschnitte)

| highway | Abschnitte | mit Breite | p10 Verkehrsfläche | p10 Fassade | GOW50 fits |
| --- | ---: | ---: | ---: | ---: | ---: |
| living_street | 159 | 47.8 % | 9.0 | 25.7 | 7.5 % |
| motorway | 29 | 44.8 % | 51.1 | 49.7 | 44.8 % |
| motorway_link | 90 | 25.6 % | 35.8 | 44.2 | 22.2 % |
| pedestrian | 97 | 23.7 % | 14.3 | 19.7 | 9.3 % |
| primary | 646 | 47.4 % | 32.0 | 40.9 | 46.7 % |
| primary_link | 31 | 3.2 % | 33.1 | 37.9 | 3.2 % |
| residential | 2524 | 74.5 % | 12.3 | 28.0 | 20.3 % |
| secondary | 434 | 39.2 % | 24.1 | 37.2 | 33.2 % |
| secondary_link | 24 | 16.7 % | 43.1 | 63.2 | 16.7 % |
| service | 66 | 39.4 % | 8.4 | 29.5 | 13.6 % |
| tertiary | 685 | 55.5 % | 19.1 | 34.0 | 38.5 % |
| tertiary_link | 17 | 5.9 % | 69.1 | nan | 5.9 % |
| track | 21 | 47.6 % | 7.0 | 33.1 | 0.0 % |
| trunk | 3 | 66.7 % | 44.4 | nan | 66.7 % |
| unclassified | 121 | 54.5 % | 11.3 | 23.7 | 11.6 % |

## Verteilungen

### Breite Verkehrsfläche je Transekt (m)

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 2.45 | 10.1 | 3704 | ██████████████ |
| 10.1 | 17.8 | 7969 | ██████████████████████████████ |
| 17.8 | 25.5 | 2690 | ██████████ |
| 25.5 | 33.2 | 1408 | █████ |
| 33.2 | 40.9 | 966 | ████ |
| 40.9 | 48.5 | 227 | █ |
| 48.5 | 56.2 | 228 | █ |
| 56.2 | 63.9 | 67 |  |
| 63.9 | 71.6 | 21 |  |
| 71.6 | 79.3 | 11 |  |

### Breite Fassade je Transekt (m)

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 5.69 | 13 | 94 | █ |
| 13 | 20.3 | 922 | ██████████████ |
| 20.3 | 27.6 | 1536 | ████████████████████████ |
| 27.6 | 34.9 | 1917 | ██████████████████████████████ |
| 34.9 | 42.2 | 1513 | ████████████████████████ |
| 42.2 | 49.5 | 982 | ███████████████ |
| 49.5 | 56.8 | 553 | █████████ |
| 56.8 | 64.1 | 216 | ███ |
| 64.1 | 71.4 | 85 | █ |
| 71.4 | 78.8 | 13 |  |

### width_p10_m je Abschnitt (m)

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 2.49 | 9.95 | 482 | ██████████ |
| 9.95 | 17.4 | 1439 | ██████████████████████████████ |
| 17.4 | 24.9 | 467 | ██████████ |
| 24.9 | 32.3 | 291 | ██████ |
| 32.3 | 39.8 | 191 | ████ |
| 39.8 | 47.2 | 64 | █ |
| 47.2 | 54.7 | 30 | █ |
| 54.7 | 62.1 | 11 |  |
| 62.1 | 69.6 | 5 |  |
| 69.6 | 77 | 2 |  |

Fassade schmaler als Verkehrsfläche bei 0.6 % der Transekte mit beiden Werten (Hinweis auf Gebäude im Straßenflurstück, Arkaden oder Versatz).

## Stichprobe (30 zufällige Abschnitte im Bezirk Eimsbüttel, Seed 42)

Links auf OSM-Karte und OSM-Way; Orthophoto-/Panoramax-Links folgen, sobald das Linkformat geklärt ist.

| segment_id | Name | highway | Länge m | Transekte | gültig | p10 Verkehrsfl. | Median | p10 Fassade | GOW50 | GOW30 | Karte | Way |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `seg_06c51c323ecec35f` | Sachsenweg | residential | 136 | 7.0 | 5.0 | 20.7 | 20.7 | – | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.643495&mlon=9.960601#map=18/53.643495/9.960601) | [Way](https://www.openstreetmap.org/way/1018232732) |
| `seg_0796a6ac6a25cf94` | Bogenstraße | tertiary | 10 | 0.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.571076&mlon=9.978445#map=18/53.571076/9.978445) | [Way](https://www.openstreetmap.org/way/238921530) |
| `seg_085fcf760eb5e9c1` | Lohkampstraße | tertiary | 137 | 7.0 | 5.0 | 18.0 | 18.0 | 28.5 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.615241&mlon=9.877703#map=18/53.615241/9.877703) | [Way](https://www.openstreetmap.org/way/4919897) |
| `seg_0906305a37756fb1` | Krähenweg | tertiary | 36 | 2.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.633004&mlon=9.954534#map=18/53.633004/9.954534) | [Way](https://www.openstreetmap.org/way/1165983748) |
| `seg_16df18fb7177523d` | Alte Rabenstraße | residential | 82 | 4.0 | 2.0 | 21.0 | 22.0 | 34.7 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.567259&mlon=10.000605#map=18/53.567259/10.000605) | [Way](https://www.openstreetmap.org/way/16232763) |
| `seg_1885bcb6c1f638e2` | Heketweg | service | 212 | 11.0 | 9.0 | 6.0 | 6.8 | 66.0 | does_not_fit | does_not_fit | [Karte](https://www.openstreetmap.org/?mlat=53.650543&mlon=9.908991#map=18/53.650543/9.908991) | [Way](https://www.openstreetmap.org/way/186967128) |
| `seg_1abf10d7274d8422` | Rahweg | residential | 324 | 16.0 | 14.0 | 12.0 | 12.0 | 32.7 | does_not_fit | fits | [Karte](https://www.openstreetmap.org/?mlat=53.641256&mlon=9.977482#map=18/53.641256/9.977482) | [Way](https://www.openstreetmap.org/way/148170157) |
| `seg_1d42b16a862590fe` | Bei der Lutherbuche | residential | 94 | 5.0 | 3.0 | 9.6 | 10.5 | 25.8 | does_not_fit | tight | [Karte](https://www.openstreetmap.org/?mlat=53.597870&mlon=9.962414#map=18/53.597870/9.962414) | [Way](https://www.openstreetmap.org/way/465938393) |
| `seg_25316f77fd2a2a9c` | Heußweg | tertiary | 34 | 2.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.577094&mlon=9.951971#map=18/53.577094/9.951971) | [Way](https://www.openstreetmap.org/way/367080898) |
| `seg_33cb6ed3e7ffbd56` | Doormannsweg | primary | 17 | 1.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.570394&mlon=9.955995#map=18/53.570394/9.955995) | [Way](https://www.openstreetmap.org/way/143710276) |
| `seg_38926833099b9b94` | Schlüterstraße | pedestrian | 77 | 4.0 | 4.0 | 20.0 | 20.0 | 45.9 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.567025&mlon=9.986511#map=18/53.567025/9.986511) | [Way](https://www.openstreetmap.org/way/738633624) |
| `seg_3a464de2b19a6893` | Vielohweg | tertiary | 28 | 1.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.638404&mlon=9.923778#map=18/53.638404/9.923778) | [Way](https://www.openstreetmap.org/way/1018245714) |
| `seg_3c7f89d9293122a6` | Gandersheimer Weg | residential | 308 | 15.0 | 13.0 | 7.5 | 7.5 | 26.2 | does_not_fit | does_not_fit | [Karte](https://www.openstreetmap.org/?mlat=53.630804&mlon=9.942861#map=18/53.630804/9.942861) | [Way](https://www.openstreetmap.org/way/1182341953) |
| `seg_3fadede7b82f43f3` | Lauterberger Weg | residential | 284 | 14.0 | 12.0 | 10.0 | 11.7 | 20.1 | does_not_fit | tight | [Karte](https://www.openstreetmap.org/?mlat=53.625898&mlon=9.942608#map=18/53.625898/9.942608) | [Way](https://www.openstreetmap.org/way/4302356) |
| `seg_4837b087ed325fa2` | Vogt-Kölln-Straße | tertiary | 299 | 15.0 | 12.0 | 15.9 | 16.0 | 35.9 | tight | fits | [Karte](https://www.openstreetmap.org/?mlat=53.607743&mlon=9.927913#map=18/53.607743/9.927913) | [Way](https://www.openstreetmap.org/way/167262195) |
| `seg_6d5977fd43d3ba6c` | Burgwedeltwiete | residential | 168 | 8.0 | 6.0 | 10.0 | 10.0 | 28.2 | does_not_fit | tight | [Karte](https://www.openstreetmap.org/?mlat=53.642727&mlon=9.911655#map=18/53.642727/9.911655) | [Way](https://www.openstreetmap.org/way/23780951) |
| `seg_84ea9801ae9fdb64` | Kollaustraße | primary | 152 | 8.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.604111&mlon=9.961662#map=18/53.604111/9.961662) | [Way](https://www.openstreetmap.org/way/650779284) |
| `seg_8f5c71cc17760317` | Levkojenweg | service | 14 | 1.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.614969&mlon=9.878638#map=18/53.614969/9.878638) | [Way](https://www.openstreetmap.org/way/1346846914) |
| `seg_9393b66447f464b6` | Bei der Apostelkirche | residential | 34 | 2.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.575495&mlon=9.943669#map=18/53.575495/9.943669) | [Way](https://www.openstreetmap.org/way/1071074636) |
| `seg_9bd1744203202163` | Wunderbrunnen | unclassified | 108 | 5.0 | 2.0 | 21.0 | 21.3 | – | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.643433&mlon=9.927441#map=18/53.643433/9.927441) | [Way](https://www.openstreetmap.org/way/22651253) |
| `seg_9eb122117042b96b` | Garstedter Weg | secondary | 9 | 0.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.622682&mlon=9.954858#map=18/53.622682/9.954858) | [Way](https://www.openstreetmap.org/way/159656516) |
| `seg_a869cf09b6234160` | Vogt-Wells-Straße | primary | 11 | 1.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.599762&mlon=9.963777#map=18/53.599762/9.963777) | [Way](https://www.openstreetmap.org/way/230609914) |
| `seg_aac2b2469aadbb68` | Harvestehuder Weg | residential | 31 | 2.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.578321&mlon=9.997483#map=18/53.578321/9.997483) | [Way](https://www.openstreetmap.org/way/710544692) |
| `seg_b14dd9d1cd005339` | Herulerweg | unclassified | 19 | 1.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.650258&mlon=9.949240#map=18/53.650258/9.949240) | [Way](https://www.openstreetmap.org/way/25739516) |
| `seg_b88b298d46679b5e` | Vereinsstraße | residential | 88 | 4.0 | 2.0 | 14.3 | 14.3 | 14.3 | tight | fits | [Karte](https://www.openstreetmap.org/?mlat=53.565824&mlon=9.962228#map=18/53.565824/9.962228) | [Way](https://www.openstreetmap.org/way/736612811) |
| `seg_bc75c394f223eb26` | Vielohwisch | unclassified | 348 | 17.0 | 15.0 | 7.9 | 8.5 | – | does_not_fit | does_not_fit | [Karte](https://www.openstreetmap.org/?mlat=53.638235&mlon=9.933887#map=18/53.638235/9.933887) | [Way](https://www.openstreetmap.org/way/8379199) |
| `seg_c232d0e509b97fa5` | Burgwedelkamp | residential | 62 | 3.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.641930&mlon=9.911588#map=18/53.641930/9.911588) | [Way](https://www.openstreetmap.org/way/4089419) |
| `seg_c330d48355534e10` | Hohe Weide | residential | 266 | 13.0 | 11.0 | 23.0 | 23.0 | 23.3 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.576150&mlon=9.973005#map=18/53.576150/9.973005) | [Way](https://www.openstreetmap.org/way/137037866) |
| `seg_c36cd78befbd0aa8` | Lüttenredder | residential | 84 | 4.0 | 2.0 | 18.0 | 18.0 | 29.5 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.645107&mlon=9.914883#map=18/53.645107/9.914883) | [Way](https://www.openstreetmap.org/way/23780954) |
| `seg_e9677794317ea023` | Niendorfer Straße | secondary | 29 | 1.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.610757&mlon=9.957467#map=18/53.610757/9.957467) | [Way](https://www.openstreetmap.org/way/586238234) |

## Lizenz

ALKIS (tatsächliche Nutzung, Gebäude): Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung (LGV), dl-de/by-2.0. Abschnitte und Brücken/Tunnel aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0.
