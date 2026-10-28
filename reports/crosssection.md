# Querschnittsbericht – Stufe 7

Erzeugt: 2026-10-28T11:38:31+00:00 von `pipeline/s07_crosssection.py`, rules.yaml 0.7.0. Nicht amtlicher Entwurf.

## Kennzahlen

- Abschnitte im Arbeitsgebiet: 4 787 (562.0 km); im Bezirk Eimsbüttel: 3 876
- Transekte: 28 039 (alle 20 m, ± 40 m, Tangente ± 10 m, Mittellinie vereinfacht 2 m)
- Verworfen: nahe Knoten (≤ 20 m) 30.8 %, Brücke/Tunnel 1.1 %
- Verkehrsfläche: gültig 61.0 %; Mittelpunkt außerhalb der ALKIS-Verkehrsfläche 2.8 %; offen/Platz (keine Grenze in 40 m) 4.4 %
- Fassade: gültig 27.6 %; offen 40.6 %; Mittelpunkt in Gebäude 0.0 %
- Abschnitte mit width_p10_m: 61.0 % (Länge: 86.0 %); mit Fassadenbreite 46.4 %
- Engstellen (≥ 3 Transekte unter p10): 31 in 31 Abschnitten
- ALKIS: 5 193 Verkehrsflächen (Platz, Strassenverkehr, Weg), 52 528 oberirdische Gebäude

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 34502 Abschnitte |
| Breiten positiv | ok | 17102 gültige Transekte Verkehrsfläche |
| min ≤ p10 ≤ Median | ok | 2918 Abschnitte mit Breite |
| transect_id eindeutig | ok | 28039 Transekte |

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
| GOW50 | 16.50 m | 34.9 % | 10.2 % | 40.9 % | 14.0 % |
| GOW30_narrow | 10.80 m | 63.4 % | 9.6 % | 13.0 % | 14.0 % |
| ETW30 | 10.80 m | 63.4 % | 9.6 % | 13.0 % | 14.0 % |

## width_p10_m nach highway-Klasse (Median über Abschnitte)

| highway | Abschnitte | mit Breite | p10 Verkehrsfläche | p10 Fassade | GOW50 fits |
| --- | ---: | ---: | ---: | ---: | ---: |
| living_street | 159 | 47.8 % | 9.0 | 25.7 | 7.5 % |
| motorway | 29 | 44.8 % | 51.1 | 49.7 | 44.8 % |
| motorway_link | 90 | 25.6 % | 35.8 | 44.2 | 22.2 % |
| pedestrian | 97 | 23.7 % | 14.3 | 19.7 | 9.3 % |
| primary | 641 | 47.6 % | 32.0 | 40.9 | 47.0 % |
| primary_link | 30 | 3.3 % | 33.1 | 37.9 | 3.3 % |
| residential | 2487 | 74.7 % | 12.4 | 27.9 | 20.5 % |
| secondary | 424 | 40.1 % | 24.3 | 36.9 | 34.2 % |
| secondary_link | 24 | 20.8 % | 45.0 | 63.2 | 20.8 % |
| tertiary | 672 | 56.1 % | 19.1 | 34.1 | 38.8 % |
| tertiary_link | 17 | 5.9 % | 69.1 | nan | 5.9 % |
| trunk | 3 | 66.7 % | 44.4 | nan | 66.7 % |
| unclassified | 114 | 55.3 % | 11.5 | 23.4 | 13.2 % |

## Verteilungen

### Breite Verkehrsfläche je Transekt (m)

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 2.49 | 10.2 | 3592 | ██████████████ |
| 10.2 | 17.9 | 7930 | ██████████████████████████████ |
| 17.9 | 25.5 | 2686 | ██████████ |
| 25.5 | 33.2 | 1406 | █████ |
| 33.2 | 40.9 | 931 | ████ |
| 40.9 | 48.6 | 233 | █ |
| 48.6 | 56.2 | 226 | █ |
| 56.2 | 63.9 | 66 |  |
| 63.9 | 71.6 | 21 |  |
| 71.6 | 79.3 | 11 |  |

### Breite Fassade je Transekt (m)

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 5.69 | 13 | 87 | █ |
| 13 | 20.3 | 912 | ██████████████ |
| 20.3 | 27.6 | 1524 | ████████████████████████ |
| 27.6 | 34.9 | 1888 | ██████████████████████████████ |
| 34.9 | 42.2 | 1499 | ████████████████████████ |
| 42.2 | 49.5 | 969 | ███████████████ |
| 49.5 | 56.8 | 552 | █████████ |
| 56.8 | 64.1 | 213 | ███ |
| 64.1 | 71.4 | 82 | █ |
| 71.4 | 78.8 | 13 |  |

### width_p10_m je Abschnitt (m)

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 2.49 | 9.95 | 451 | ██████████ |
| 9.95 | 17.4 | 1417 | ██████████████████████████████ |
| 17.4 | 24.9 | 458 | ██████████ |
| 24.9 | 32.3 | 290 | ██████ |
| 32.3 | 39.8 | 190 | ████ |
| 39.8 | 47.2 | 65 | █ |
| 47.2 | 54.7 | 31 | █ |
| 54.7 | 62.1 | 9 |  |
| 62.1 | 69.6 | 5 |  |
| 69.6 | 77 | 2 |  |

Fassade schmaler als Verkehrsfläche bei 0.6 % der Transekte mit beiden Werten (Hinweis auf Gebäude im Straßenflurstück, Arkaden oder Versatz).

## Stichprobe (30 zufällige Abschnitte im Bezirk Eimsbüttel, Seed 42)

Links auf OSM-Karte und OSM-Way; Orthophoto-/Panoramax-Links folgen, sobald das Linkformat geklärt ist.

| segment_id | Name | highway | Länge m | Transekte | gültig | p10 Verkehrsfl. | Median | p10 Fassade | GOW50 | GOW30 | Karte | Way |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `seg_074cd95a035a05c4` | Papendamm | residential | 111 | 6.0 | 4.0 | 17.2 | 17.2 | 33.1 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.566680&mlon=9.976908#map=18/53.566680/9.976908) | [Way](https://www.openstreetmap.org/way/4004664) |
| `seg_0817c77e740f6f6c` | – | motorway_link | 255 | 13.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.593640&mlon=9.922273#map=18/53.593640/9.922273) | [Way](https://www.openstreetmap.org/way/1276595268) |
| `seg_08c8ff2f0960effa` | Holsteiner Chaussee | primary | 10 | 1.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.620392&mlon=9.908264#map=18/53.620392/9.908264) | [Way](https://www.openstreetmap.org/way/408642295) |
| `seg_094a4278a1b7df0b` | Redingskamp | residential | 33 | 2.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.612511&mlon=9.890739#map=18/53.612511/9.890739) | [Way](https://www.openstreetmap.org/way/42413679) |
| `seg_1795d520ce96094f` | Hallerstraße | tertiary | 355 | 18.0 | 15.0 | 24.3 | 31.4 | 39.4 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.572680&mlon=9.991315#map=18/53.572680/9.991315) | [Way](https://www.openstreetmap.org/way/39095469) |
| `seg_191011c181a9eccc` | Nordalbingerweg | residential | 161 | 8.0 | 6.0 | 13.0 | 13.0 | 40.1 | does_not_fit | fits | [Karte](https://www.openstreetmap.org/?mlat=53.647269&mlon=9.953846#map=18/53.647269/9.953846) | [Way](https://www.openstreetmap.org/way/1168136673) |
| `seg_1b9a3cddb28e88fc` | Baarkamp | residential | 121 | 6.0 | 4.0 | 12.0 | 12.0 | 31.2 | does_not_fit | fits | [Karte](https://www.openstreetmap.org/?mlat=53.606061&mlon=9.940001#map=18/53.606061/9.940001) | [Way](https://www.openstreetmap.org/way/496601616) |
| `seg_1e51b72f49183c5f` | Rütersbarg | residential | 51 | 3.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.601577&mlon=9.955145#map=18/53.601577/9.955145) | [Way](https://www.openstreetmap.org/way/26628741) |
| `seg_25fff5cebc7b74d3` | – | primary_link | 42 | 2.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.599118&mlon=9.964975#map=18/53.599118/9.964975) | [Way](https://www.openstreetmap.org/way/30091973) |
| `seg_358f1bb94bb81ef1` | Halstenbeker Straße | residential | 80 | 4.0 | 2.0 | 11.0 | 11.0 | – | does_not_fit | fits | [Karte](https://www.openstreetmap.org/?mlat=53.625667&mlon=9.903495#map=18/53.625667/9.903495) | [Way](https://www.openstreetmap.org/way/23711969) |
| `seg_3ac1a8795499671f` | Oldesloer Straße | secondary | 47 | 2.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.638312&mlon=9.923200#map=18/53.638312/9.923200) | [Way](https://www.openstreetmap.org/way/1150429542) |
| `seg_3bb44606e4a813d2` | Siemersplatz | primary | 60 | 3.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.599520&mlon=9.964413#map=18/53.599520/9.964413) | [Way](https://www.openstreetmap.org/way/308317374) |
| `seg_3e4ed57d7c923cd1` | Paul-Sorge-Straße | tertiary | 225 | 11.0 | 9.0 | 14.4 | 14.4 | 29.7 | tight | fits | [Karte](https://www.openstreetmap.org/?mlat=53.638593&mlon=9.951169#map=18/53.638593/9.951169) | [Way](https://www.openstreetmap.org/way/605866503) |
| `seg_414f382c4d6e32b5` | Kleiner Kielort | residential | 135 | 7.0 | 5.0 | 17.2 | 17.3 | 17.2 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.571620&mlon=9.975728#map=18/53.571620/9.975728) | [Way](https://www.openstreetmap.org/way/3930845) |
| `seg_49ff6b4f33e0a2d0` | Spanische Furt | residential | 124 | 6.0 | 4.0 | 15.0 | 15.0 | 42.1 | tight | fits | [Karte](https://www.openstreetmap.org/?mlat=53.623372&mlon=9.911985#map=18/53.623372/9.911985) | [Way](https://www.openstreetmap.org/way/1311146889) |
| `seg_703176e854c5b77e` | Randstraße | tertiary | 53 | 3.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.590651&mlon=9.919021#map=18/53.590651/9.919021) | [Way](https://www.openstreetmap.org/way/38613476) |
| `seg_88daa65dfa11532b` | Alsterchaussee | residential | 138 | 7.0 | 5.0 | 20.5 | 20.5 | 27.2 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.573195&mlon=9.998363#map=18/53.573195/9.998363) | [Way](https://www.openstreetmap.org/way/3927749) |
| `seg_9484862e440e4b51` | Doormannsweg | primary | 42 | 2.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.570567&mlon=9.956429#map=18/53.570567/9.956429) | [Way](https://www.openstreetmap.org/way/80992110) |
| `seg_99a68ad44edd39cc` | Goldnesselweg | residential | 149 | 7.0 | 5.0 | 8.0 | 8.0 | 37.1 | does_not_fit | does_not_fit | [Karte](https://www.openstreetmap.org/?mlat=53.610652&mlon=9.885212#map=18/53.610652/9.885212) | [Way](https://www.openstreetmap.org/way/7565287) |
| `seg_a0de84542f4d9127` | Lokstedter Steindamm | primary | 99 | 5.0 | 3.0 | 30.0 | 30.0 | – | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.591450&mlon=9.967251#map=18/53.591450/9.967251) | [Way](https://www.openstreetmap.org/way/1567673937) |
| `seg_a3e092073b821941` | Bei der Lutherbuche | residential | 162 | 8.0 | 6.0 | 14.0 | 14.0 | 35.0 | does_not_fit | fits | [Karte](https://www.openstreetmap.org/?mlat=53.597134&mlon=9.959851#map=18/53.597134/9.959851) | [Way](https://www.openstreetmap.org/way/16322436) |
| `seg_ae2e7d12bd43b1cc` | Eidelstedter Weg | tertiary | 27 | 1.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.582355&mlon=9.948107#map=18/53.582355/9.948107) | [Way](https://www.openstreetmap.org/way/55955783) |
| `seg_b0b2030ddcdc431f` | Hagendeel | residential | 23 | 1.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.607190&mlon=9.942861#map=18/53.607190/9.942861) | [Way](https://www.openstreetmap.org/way/411157231) |
| `seg_b88b298d46679b5e` | Vereinsstraße | residential | 88 | 4.0 | 2.0 | 14.3 | 14.3 | 14.3 | tight | fits | [Karte](https://www.openstreetmap.org/?mlat=53.565824&mlon=9.962228#map=18/53.565824/9.962228) | [Way](https://www.openstreetmap.org/way/736612811) |
| `seg_bfbed037447cf248` | Oldesloer Straße | secondary | 121 | 6.0 | 4.0 | 13.5 | 13.6 | 35.7 | does_not_fit | fits | [Karte](https://www.openstreetmap.org/?mlat=53.635950&mlon=9.917132#map=18/53.635950/9.917132) | [Way](https://www.openstreetmap.org/way/844555843) |
| `seg_c341ebfaec60354c` | Lokstedter Steindamm | primary | 35 | 2.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.586365&mlon=9.968433#map=18/53.586365/9.968433) | [Way](https://www.openstreetmap.org/way/682409935) |
| `seg_c8d453129f45f45c` | Wullwisch | residential | 250 | 13.0 | 10.0 | 4.1 | 8.0 | 25.7 | does_not_fit | does_not_fit | [Karte](https://www.openstreetmap.org/?mlat=53.606371&mlon=9.950303#map=18/53.606371/9.950303) | [Way](https://www.openstreetmap.org/way/23417329) |
| `seg_c9a61940cb1ab15c` | Stellinger Weg | residential | 21 | 1.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.580453&mlon=9.947393#map=18/53.580453/9.947393) | [Way](https://www.openstreetmap.org/way/1188162855) |
| `seg_c9e7fa8f21ab0779` | Wördemanns Weg | tertiary | 146 | 7.0 | 5.0 | 16.9 | 17.3 | 26.7 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.597422&mlon=9.932331#map=18/53.597422/9.932331) | [Way](https://www.openstreetmap.org/way/1417927680) |
| `seg_f14ff48e916757c4` | Goslarer Weg | residential | 115 | 6.0 | 4.0 | 10.1 | 10.3 | 37.1 | does_not_fit | tight | [Karte](https://www.openstreetmap.org/?mlat=53.636626&mlon=9.945053#map=18/53.636626/9.945053) | [Way](https://www.openstreetmap.org/way/10060140) |

## Lizenz

ALKIS (tatsächliche Nutzung, Gebäude): Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung (LGV), dl-de/by-2.0. Abschnitte und Brücken/Tunnel aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0.
