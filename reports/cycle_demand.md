# Radverkehrsnachfrage (Stufe c02)

Erzeugt 2026-11-11T21:09:01+00:00 mit pipeline/c02_cycle_demand.py · cycling_rules.yaml 0.11.0 · nicht amtlicher Entwurf. Alle Modellparameter sind Annahmen (source_type assumption, status draft) und vor fachlicher Nutzung zu prüfen.

## Kurzfassung

- Kalibrierfaktor k = 0.243 (ein Faktor für Hamburg, C-DEM-06) aus 87 Zählquerschnitten.
- Güte: Spearman 0.57, Pearson (log) 0.50, Pearson 0.59, mittlere relative Abweichung 117%, 48% der Querschnitte innerhalb Faktor 2.
- 534 km mit Konfidenz hoch, 1 761 km mittel, 4 136 km niedrig.
- Werte sind modelliert, nicht gezählt. Sie dienen als Grundlage für Hierarchie (Prompt 16) und Breiten (Prompt 18).

## Modell

- Zonen: 2 620 Quadrate zu 500 m im Zensus-Gitter (EPSG:3035), davon 2 223 mit Einwohnern (1 808 530 Einwohner in Hamburg) und 2 509 mit Zielen (C-DEM-01). Zonenpunkt an den nächsten Graphknoten angebunden (Median 74 m, Maximum 1376 m).
- Ziele (C-DEM-02/03), Gewicht × Anteil der Zone an der Hamburger Summe:

| Zieltyp | Gewicht | Objekte | Summe | Quelle |
| --- | ---: | ---: | ---: | --- |
| jobs_floor_area | 0.40 | 56 530 | 74 117 933 | ALKIS Gebäude (Geschossfläche Nichtwohnen, m²) |
| shops | 0.20 | 10 447 | 10 447 | OSM shop=* |
| schools | 0.15 | 557 | 557 | OSM amenity=school (Fallback) |
| universities | 0.10 | 110 | 110 | OSM amenity=university|college (Fallback) |
| rapid_transit_stops | 0.15 | 375 | 375 | HVV-GTFS, route_type [1, 2, 109, 402] |

- Verteilung (C-DEM-04): produktionsgebundenes Gravitationsmodell, f(d) = exp(−0.25 · d), d = wahrgenommener Widerstand in km, nur Relationen 0.5–15.0 km.
- Umlegung (C-DEM-05): stochastic, 3 Lauf/Läufe, Störung σ = 0.1, Seed 42; Graph 44 627 Knoten, 111 357 gerichtete Bögen (größte stark zusammenhängende Komponente).

| Lauf | Laufzeit s | Fahrten (Modell) | mittlere Weglänge km (Widerstand) | Quellzonen ohne Ziel im Band |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 25 | 1 808 530 | 6.35 | 0 |
| 2 | 25 | 1 808 530 | 6.35 | 0 |
| 3 | 25 | 1 808 530 | 6.35 | 0 |

Modellfahrten haben keine absolute Einheit (1 Fahrt je Einwohner); erst der Kalibrierfaktor macht daraus Rad/Werktag.

## Kalibrierung an Zählstellen

- Zählstellen: 312, davon 104 ohne Richtung. Nur diese gehen ein; sie sind die Summe der zwei richtungsbezogenen Zählstellen am selben Querschnitt (Median-Verhältnis 1,00; geprüft 2026-11-05), so wird nichts doppelt gezählt.
- Zählwert: Mittel Mo–Fr 2025 über Tage mit count > 0, mindestens 150 gültige Werktage: 97 Querschnitte. Modellwert: Summe beider Richtungen aller Kanten, die ein Querschnitt von ±25 m schneidet (≥ 45°).
- Mit Modellwert > 0: 87; ohne Kante im Umkreis von 30 m oder ohne Modellfluss: 10.
- k = geometrisches Mittel von Zählwert/Modellwert = **0.243**.

| Kennzahl | Wert |
| --- | ---: |
| Querschnitte | 87 |
| Pearson r (linear) | 0.59 |
| Pearson r (log) | 0.50 |
| Spearman ρ | 0.57 |
| mittlere relative Abweichung | 117% |
| Median Zählwert/Modell | 0.74 |
| Anteil innerhalb Faktor 2 | 48% |

![Modell vs. Zählstellen](cycle_demand_scatter.png)

Verhältnis Zählwert/Modell je Bezirk (nur Diagnose; kalibriert wird mit einem Faktor für Hamburg):

| Bezirk | Querschnitte | geom. Mittel Zählwert/Modell |
| --- | ---: | ---: |
| Altona | 12 | 1.48 |
| Bergedorf | 4 | 0.59 |
| Eimsbüttel | 18 | 1.33 |
| Hamburg-Mitte | 20 | 1.08 |
| Hamburg-Nord | 17 | 1.03 |
| Harburg | 7 | 0.34 |
| Wandsbek | 9 | 0.78 |

Größte Abweichungen (je 5 über- und unterschätzt):

| Zählstelle | Bezirk | Zählwert | Modell | Zählwert/Modell | Kanten | Prüfen |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Verkehrszählstelle 6779940 | Hamburg-Nord | 677 | 9 531 | 0.07 | 1 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567549,5935741]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.566185/10.019947) · [OSM](https://www.openstreetmap.org/?mlat=53.566185&mlon=10.019947#map=18/53.566185/10.019947) |
| Verkehrszählstelle 0117930 | Hamburg-Mitte | 937 | 4 917 | 0.19 | 2 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568093,5932088]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.533288/10.027366) · [OSM](https://www.openstreetmap.org/?mlat=53.533288&mlon=10.027366#map=18/53.533288/10.027366) |
| Verkehrszählstelle 0333960 | Hamburg-Mitte | 126 | 658 | 0.19 | 1 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567750,5932059]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.533071/10.022181) · [OSM](https://www.openstreetmap.org/?mlat=53.533071&mlon=10.022181#map=18/53.533071/10.022181) |
| Verkehrszählstelle 6848980 | Harburg | 605 | 3 123 | 0.19 | 2 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565459,5924593]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.466262/9.986063) · [OSM](https://www.openstreetmap.org/?mlat=53.466262&mlon=9.986063#map=18/53.466262/9.986063) |
| Verkehrszählstelle 7462910 | Wandsbek | 222 | 988 | 0.23 | 1 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575891,5939103]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.595264/10.146695) · [OSM](https://www.openstreetmap.org/?mlat=53.595264&mlon=10.146695#map=18/53.595264/10.146695) |
| Verkehrszählstelle 6111920 | Hamburg-Nord | 1 197 | 16 | 74.60 | 1 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568903,5939488]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.599690/10.041213) · [OSM](https://www.openstreetmap.org/?mlat=53.599690&mlon=10.041213#map=18/53.599690/10.041213) |
| Verkehrszählstelle 7786960 | Hamburg-Mitte | 1 393 | 35 | 39.57 | 1 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566082,5933388]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.545228/9.997300) · [OSM](https://www.openstreetmap.org/?mlat=53.545228&mlon=9.997300#map=18/53.545228/9.997300) |
| Verkehrszählstelle 6381910 | Eimsbüttel | 1 676 | 75 | 22.28 | 1 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561715,5939105]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.597140/9.932533) · [OSM](https://www.openstreetmap.org/?mlat=53.597140&mlon=9.932533#map=18/53.597140/9.932533) |
| Verkehrszählstelle 7438910 | Eimsbüttel | 1 214 | 67 | 18.00 | 1 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564473,5936073]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.569558/9.973575) · [OSM](https://www.openstreetmap.org/?mlat=53.569558&mlon=9.973575#map=18/53.569558/9.973575) |
| Verkehrszählstelle 7462970 | Wandsbek | 530 | 56 | 9.41 | 1 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575887,5939062]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.594891/10.146629) · [OSM](https://www.openstreetmap.org/?mlat=53.594891&mlon=10.146629#map=18/53.594891/10.146629) |

## Vergleich mit DB Rad+ (nur Plausibilität)

- 150 778 Linien 2025 (App-Stichprobe, nicht repräsentativ; drei Datensätze vom Server nicht lieferbar, siehe data/manifest.json skipped_records). Linienmitte an die nächste Kante ≤ 15 m: 121 118 Linien auf 34 067 Kanten (Maximum je Kante).
- Spearman ρ (Modell kalibriert vs. DB-Rad+-Fahrten): 0.37; Pearson (log): 0.33.
- DB Rad+ geht nicht in die Kalibrierung ein.

## Karte

![Radverkehrsstärke je Kante](cycle_demand_map.png)

## demand_confidence (C-DEM-07)

- hoch: ≤ 500 m von einem Querschnitt mit Zählwert/Modell in [0.5, 2.0]
- niedrig: ≤ 2 km von der Landesgrenze (Wege über die Grenze fehlen), in ländlichen Stadtteilen, unter 50 Rad/Tag oder ohne Modellwert (außerhalb der Hauptkomponente)
- sonst mittel

| Konfidenz | Kanten | km |
| --- | ---: | ---: |
| hoch | 7 224 | 534.1 |
| mittel | 20 645 | 1 760.7 |
| niedrig | 38 104 | 4 135.6 |

## Die 30 stärksten Kanten (Prüfung durch Ortskundige)

| # | edge_id | Bezirk | Name | Art | Rad/Werktag | Spitzenstunde | Konfidenz | Prüfen |
| ---: | --- | --- | --- | --- | ---: | ---: | --- | --- |
| 1 | `ce_8038f2e3cf316d79` | Hamburg-Mitte | – | path | 16 137 | 2 421 | mittel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566533,5934788]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.557755/10.004409) · [OSM](https://www.openstreetmap.org/?mlat=53.557755&mlon=10.004409#map=18/53.557755/10.004409) |
| 2 | `ce_a52c09c1bd3724c8` | Hamburg-Mitte | neben An der Alster | path | 16 137 | 2 421 | mittel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566615,5934832]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558141/10.005644) · [OSM](https://www.openstreetmap.org/?mlat=53.558141&mlon=10.005644#map=18/53.558141/10.005644) |
| 3 | `ce_cfcb338858308d70` | Hamburg-Mitte | – | path | 16 137 | 2 421 | mittel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566694,5934888]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558630/10.006858) · [OSM](https://www.openstreetmap.org/?mlat=53.558630&mlon=10.006858#map=18/53.558630/10.006858) |
| 4 | `ce_8ae9294e64f381c1` | Hamburg-Mitte | neben Kennedybrücke | path | 16 130 | 2 420 | hoch | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566205,5934753]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.557484/9.999448) · [OSM](https://www.openstreetmap.org/?mlat=53.557484&mlon=9.999448#map=18/53.557484/9.999448) |
| 5 | `ce_2dd614b279c81a05` | Hamburg-Mitte | neben An der Alster | path | 15 890 | 2 384 | mittel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566768,5934932]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.559019/10.007979) · [OSM](https://www.openstreetmap.org/?mlat=53.559019&mlon=10.007979#map=18/53.559019/10.007979) |
| 6 | `ce_c5e4650005b0a6c9` | Hamburg-Mitte | neben An der Alster | path | 15 890 | 2 384 | mittel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566799,5934953]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.559199/10.008457) · [OSM](https://www.openstreetmap.org/?mlat=53.559199&mlon=10.008457#map=18/53.559199/10.008457) |
| 7 | `ce_f823aac7a9b0a893` | Hamburg-Mitte | – | path | 15 890 | 2 384 | mittel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566862,5935008]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.559690/10.009418) · [OSM](https://www.openstreetmap.org/?mlat=53.559690&mlon=10.009418#map=18/53.559690/10.009418) |
| 8 | `ce_7394c93f5562b841` | Hamburg-Mitte | – | path | 15 805 | 2 371 | mittel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566948,5935076]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.560290/10.010725) · [OSM](https://www.openstreetmap.org/?mlat=53.560290&mlon=10.010725#map=18/53.560290/10.010725) |
| 9 | `ce_76d874ca9bcbd707` | Hamburg-Mitte | neben An der Alster | path | 15 805 | 2 371 | hoch | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567106,5935167]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.561088/10.013134) · [OSM](https://www.openstreetmap.org/?mlat=53.561088&mlon=10.013134#map=18/53.561088/10.013134) |
| 10 | `ce_8bb203f92cc25299` | Hamburg-Mitte | – | path | 15 805 | 2 371 | mittel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567068,5935131]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.560768/10.012555) · [OSM](https://www.openstreetmap.org/?mlat=53.560768&mlon=10.012555#map=18/53.560768/10.012555) |
| 11 | `ce_e55f2d101f35deb2` | Hamburg-Mitte | – | path | 15 805 | 2 371 | mittel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567020,5935092]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.560425/10.011818) · [OSM](https://www.openstreetmap.org/?mlat=53.560425&mlon=10.011818#map=18/53.560425/10.011818) |
| 12 | `ce_22f6f1144a4740e1` | Hamburg-Mitte | – | path | 15 173 | 2 276 | hoch | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566442,5934753]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.557453/10.003016) · [OSM](https://www.openstreetmap.org/?mlat=53.557453&mlon=10.003016#map=18/53.557453/10.003016) |
| 13 | `ce_4366aea3d6d6e0a1` | Hamburg-Mitte | neben An der Alster | path | 14 002 | 2 100 | hoch | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567178,5935259]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.561899/10.014239) · [OSM](https://www.openstreetmap.org/?mlat=53.561899&mlon=10.014239#map=18/53.561899/10.014239) |
| 14 | `ce_98138626bf96eee0` | Hamburg-Nord | – | path | 14 002 | 2 100 | hoch | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567243,5935375]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.562942/10.015240) · [OSM](https://www.openstreetmap.org/?mlat=53.562942&mlon=10.015240#map=18/53.562942/10.015240) |
| 15 | `ce_b47e8ab5607ff44b` | Hamburg-Nord | neben Schwanenwik | path | 14 002 | 2 100 | hoch | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567310,5935454]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.563637/10.016274) · [OSM](https://www.openstreetmap.org/?mlat=53.563637&mlon=10.016274#map=18/53.563637/10.016274) |
| 16 | `ce_4895db27155a88a8` | Hamburg-Nord | neben Schwanenwik | path | 11 993 | 1 799 | hoch | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567335,5935665]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.565535/10.016705) · [OSM](https://www.openstreetmap.org/?mlat=53.565535&mlon=10.016705#map=18/53.565535/10.016705) |
| 17 | `ce_bb63d64ad95f65c9` | Hamburg-Nord | neben Schwanenwik | path | 11 975 | 1 796 | hoch | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567338,5935620]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.565128/10.016731) · [OSM](https://www.openstreetmap.org/?mlat=53.565128&mlon=10.016731#map=18/53.565128/10.016731) |
| 18 | `ce_bbf126f6b13d1a42` | Hamburg-Nord | neben Schwanenwik | path | 11 975 | 1 796 | hoch | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567341,5935559]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.564576/10.016757) · [OSM](https://www.openstreetmap.org/?mlat=53.564576&mlon=10.016757#map=18/53.564576/10.016757) |
| 19 | `ce_a0936140a3a5d423` | Hamburg-Mitte | neben Bürgerweide | path | 10 822 | 1 623 | mittel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568187,5934679]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.556560/10.029340) · [OSM](https://www.openstreetmap.org/?mlat=53.556560&mlon=10.029340#map=18/53.556560/10.029340) |
| 20 | `ce_f706abd236d129e5` | Hamburg-Mitte | – | path | 10 822 | 1 623 | mittel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568071,5934620]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.556049/10.027573) · [OSM](https://www.openstreetmap.org/?mlat=53.556049&mlon=10.027573#map=18/53.556049/10.027573) |
| 21 | `ce_8d4a94e4b404216f` | Hamburg-Mitte | – | path | 10 749 | 1 612 | mittel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568065,5934627]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.556112/10.027499) · [OSM](https://www.openstreetmap.org/?mlat=53.556112&mlon=10.027499#map=18/53.556112/10.027499) |
| 22 | `ce_ea537a5afcc62f4e` | Eimsbüttel | neben Kennedybrücke | path | 10 592 | 1 589 | hoch | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565878,5934892]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558766/9.994545) · [OSM](https://www.openstreetmap.org/?mlat=53.558766&mlon=9.994545#map=18/53.558766/9.994545) |
| 23 | `ce_1f36317abc34ec77` | Eimsbüttel | – | path | 10 556 | 1 583 | hoch | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565848,5934901]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558852/9.994084) · [OSM](https://www.openstreetmap.org/?mlat=53.558852&mlon=9.994084#map=18/53.558852/9.994084) |
| 24 | `ce_89e7f1ab678e29bb` | Eimsbüttel | neben Kennedybrücke | path | 10 556 | 1 583 | hoch | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565872,5934894]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558788/9.994445) · [OSM](https://www.openstreetmap.org/?mlat=53.558788&mlon=9.994445#map=18/53.558788/9.994445) |
| 25 | `ce_f2e7166a1fa05760` | Eimsbüttel | neben Kennedybrücke | path | 10 556 | 1 583 | hoch | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565860,5934896]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558810/9.994267) · [OSM](https://www.openstreetmap.org/?mlat=53.558810&mlon=9.994267#map=18/53.558810/9.994267) |
| 26 | `ce_1e9ddb9cf5afbee9` | Eimsbüttel | neben Kennedybrücke | path | 10 478 | 1 572 | hoch | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565888,5934888]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558733/9.994682) · [OSM](https://www.openstreetmap.org/?mlat=53.558733&mlon=9.994682#map=18/53.558733/9.994682) |
| 27 | `ce_8cdb7e2c79be118e` | Eimsbüttel | neben Kennedybrücke | path | 10 478 | 1 572 | hoch | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565884,5934890]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558749/9.994627) · [OSM](https://www.openstreetmap.org/?mlat=53.558749&mlon=9.994627#map=18/53.558749/9.994627) |
| 28 | `ce_a6e811f0c5e04a11` | Eimsbüttel | neben Kennedybrücke | path | 10 421 | 1 563 | hoch | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565898,5934884]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558694/9.994842) · [OSM](https://www.openstreetmap.org/?mlat=53.558694&mlon=9.994842#map=18/53.558694/9.994842) |
| 29 | `ce_b26d265a55eeb7c6` | Eimsbüttel | neben Kennedybrücke | path | 10 421 | 1 563 | hoch | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565914,5934877]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558632/9.995085) · [OSM](https://www.openstreetmap.org/?mlat=53.558632&mlon=9.995085#map=18/53.558632/9.995085) |
| 30 | `ce_fe1f6f3c06b1bae6` | Eimsbüttel | neben Kennedybrücke | path | 10 421 | 1 563 | hoch | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565979,5934849]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558372/9.996052) · [OSM](https://www.openstreetmap.org/?mlat=53.558372&mlon=9.996052#map=18/53.558372/9.996052) |

## 30 Zufallsstichproben (Seed 42)

| edge_id | Bezirk | Name | Art | Rad/Werktag | hin/zurück | Konfidenz | Prüfen |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| `ce_0e5e566d2eefc99b` | Altona | Bei der Rolandsmühle | road | 126 | 35/91 | mittel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560654,5933759]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.549216/9.915458) · [OSM](https://www.openstreetmap.org/?mlat=53.549216&mlon=9.915458#map=18/53.549216/9.915458) |
| `ce_3aef5a2940e76ac7` | Altona | Pieperweg | road | 99 | 26/73 | niedrig | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[554305,5937212]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.580950/9.820257) · [OSM](https://www.openstreetmap.org/?mlat=53.580950&mlon=9.820257#map=18/53.580950/9.820257) |
| `ce_7e73d7e10ec38b1d` | Altona | Flerrentwiete | road | 19 | 19/0 | niedrig | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[549776,5937405]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.583135/9.751882) · [OSM](https://www.openstreetmap.org/?mlat=53.583135&mlon=9.751882#map=18/53.583135/9.751882) |
| `ce_8d15e20340fef49d` | Altona | – | path | 246 | 246/0 | niedrig | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[554510,5936727]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.576566/9.823264) · [OSM](https://www.openstreetmap.org/?mlat=53.576566&mlon=9.823264#map=18/53.576566/9.823264) |
| `ce_2cc60ecda14db6a9` | Bergedorf | – | road | 0 | 0/0 | niedrig | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580674,5927047]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.486205/10.215837) · [OSM](https://www.openstreetmap.org/?mlat=53.486205&mlon=10.215837#map=18/53.486205/10.215837) |
| `ce_3c98c6fc8894efb6` | Bergedorf | Wentorfer Straße | road | 310 | 276/34 | niedrig | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[581487,5927268]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.488067/10.228152) · [OSM](https://www.openstreetmap.org/?mlat=53.488067&mlon=10.228152#map=18/53.488067/10.228152) |
| `ce_5cce82fb4356b329` | Bergedorf | neben Ebner-Eschenbach-Weg | path | 0 | 0/0 | niedrig | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577876,5926626]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.482846/10.173581) · [OSM](https://www.openstreetmap.org/?mlat=53.482846&mlon=10.173581#map=18/53.482846/10.173581) |
| `ce_8d5147dd24a922c4` | Eimsbüttel | – | path | 90 | 52/38 | mittel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563695,5935540]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.564867/9.961727) · [OSM](https://www.openstreetmap.org/?mlat=53.564867&mlon=9.961727#map=18/53.564867/9.961727) |
| `ce_ae9110d2a6ca511b` | Eimsbüttel | Graf-Otto-Weg | road | 136 | 121/15 | niedrig | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560136,5944402]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.644927/9.909706) · [OSM](https://www.openstreetmap.org/?mlat=53.644927&mlon=9.909706#map=18/53.644927/9.909706) |
| `ce_c114f44771e0e957` | Eimsbüttel | Jaarsmoor | road | 781 | 657/124 | niedrig | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559081,5940384]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.608935/9.892975) · [OSM](https://www.openstreetmap.org/?mlat=53.608935&mlon=9.892975#map=18/53.608935/9.892975) |
| `ce_ea44be57b420b190` | Eimsbüttel | – | path | 0 | 0/0 | niedrig | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559519,5940971]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.614168/9.899714) · [OSM](https://www.openstreetmap.org/?mlat=53.614168&mlon=9.899714#map=18/53.614168/9.899714) |
| `ce_0a460b6afff1a8aa` | Hamburg-Mitte | Hein-Hoyer-Straße | road | 86 | 86/0 | mittel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563776,5934123]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.552117/9.962660) · [OSM](https://www.openstreetmap.org/?mlat=53.552117&mlon=9.962660#map=18/53.552117/9.962660) |
| `ce_0af7274411d3047f` | Hamburg-Mitte | Mannesallee | road | 130 | 5/125 | mittel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565572,5929933]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.514242/9.988875) · [OSM](https://www.openstreetmap.org/?mlat=53.514242&mlon=9.988875#map=18/53.514242/9.988875) |
| `ce_1d10470f7aea4b22` | Hamburg-Mitte | Bethesdastraße | road | 1 633 | 1 222/411 | mittel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568613,5934742]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.557068/10.035791) · [OSM](https://www.openstreetmap.org/?mlat=53.557068&mlon=10.035791#map=18/53.557068/10.035791) |
| `ce_921ccd51799780ce` | Hamburg-Mitte | Süderstraße | road | 537 | 537/0 | mittel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568319,5933452]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.545517/10.031070) · [OSM](https://www.openstreetmap.org/?mlat=53.545517&mlon=10.031070#map=18/53.545517/10.031070) |
| `ce_cc364527de2587d1` | Hamburg-Mitte | Kandinskyallee | road | 0 | 0/0 | niedrig | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576193,5931235]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.524506/10.149345) · [OSM](https://www.openstreetmap.org/?mlat=53.524506&mlon=10.149345#map=18/53.524506/10.149345) |
| `ce_25415a5cca91710d` | Hamburg-Nord | Falkenried | road | 0 | 0/0 | hoch | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564248,5937935]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.586316/9.970568) · [OSM](https://www.openstreetmap.org/?mlat=53.586316&mlon=9.970568#map=18/53.586316/9.970568) |
| `ce_592ef5ab74bf950b` | Hamburg-Nord | Heerwisch | road | 294 | 130/165 | niedrig | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566084,5945661]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.655526/9.999936) · [OSM](https://www.openstreetmap.org/?mlat=53.655526&mlon=9.999936#map=18/53.655526/9.999936) |
| `ce_5f0fc89729abe2b1` | Hamburg-Nord | Herzmoor | road | 0 | 0/0 | niedrig | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568348,5946433]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.662176/10.034358) · [OSM](https://www.openstreetmap.org/?mlat=53.662176&mlon=10.034358#map=18/53.662176/10.034358) |
| `ce_cdf3b4911c7ed331` | Hamburg-Nord | – | path | 5 | 5/0 | niedrig | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566883,5939137]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.596792/10.010613) · [OSM](https://www.openstreetmap.org/?mlat=53.596792&mlon=10.010613#map=18/53.596792/10.010613) |
| `ce_0b972cbad9999e38` | Harburg | Friedhofstraße | road | 269 | 61/208 | mittel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563553,5922833]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.450673/9.957001) · [OSM](https://www.openstreetmap.org/?mlat=53.450673&mlon=9.957001#map=18/53.450673/9.957001) |
| `ce_d9bd88c7fb1410f3` | Harburg | Cuxhavener Straße | road | 1 224 | 352/872 | niedrig | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558906,5925145]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.472002/9.887460) · [OSM](https://www.openstreetmap.org/?mlat=53.472002&mlon=9.887460#map=18/53.472002/9.887460) |
| `ce_e8eeb80056cdd35e` | Harburg | Hasselwerder Straße | road | 224 | 48/176 | niedrig | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[553795,5930571]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.521314/9.811399) · [OSM](https://www.openstreetmap.org/?mlat=53.521314&mlon=9.811399#map=18/53.521314/9.811399) |
| `ce_3b49b2ddb01ff9b3` | Wandsbek | Wellingsbüttler Weg | road | 42 | 42/0 | niedrig | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570085,5943685]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.637244/10.060013) · [OSM](https://www.openstreetmap.org/?mlat=53.637244&mlon=10.060013#map=18/53.637244/10.060013) |
| `ce_7de91f5fefcd1b86` | Wandsbek | Ohlstedter Stieg | road | 61 | 6/55 | niedrig | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575512,5949373]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.687605/10.143461) · [OSM](https://www.openstreetmap.org/?mlat=53.687605&mlon=10.143461#map=18/53.687605/10.143461) |
| `ce_a2c0f99a848e7ac3` | Wandsbek | – | path | 743 | 178/565 | mittel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573659,5941430]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.616492/10.113526) · [OSM](https://www.openstreetmap.org/?mlat=53.616492&mlon=10.113526#map=18/53.616492/10.113526) |
| `ce_c266c3b5fad1e338` | Wandsbek | – | path | 0 | 0/0 | niedrig | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570894,5937510]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.581647/10.070843) · [OSM](https://www.openstreetmap.org/?mlat=53.581647&mlon=10.070843#map=18/53.581647/10.070843) |
| `ce_d0c6947e06722549` | Wandsbek | Pillauer Straße | road | 10 | 6/4 | niedrig | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572027,5938971]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.594616/10.088293) · [OSM](https://www.openstreetmap.org/?mlat=53.594616&mlon=10.088293#map=18/53.594616/10.088293) |
| `ce_d589dc4f7c5191d2` | Wandsbek | Wiesenhof | road | 0 | 0/0 | niedrig | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577638,5940917]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.611311/10.173536) · [OSM](https://www.openstreetmap.org/?mlat=53.611311&mlon=10.173536#map=18/53.611311/10.173536) |
| `ce_5241f0f7183abf0e` | nan | Fliegenberg | road | 0 | 0/0 | niedrig | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575949,5919007]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.414656/10.142706) · [OSM](https://www.openstreetmap.org/?mlat=53.414656&mlon=10.142706#map=18/53.414656/10.142706) |

## Grenzen

- Einfaches Modell: ein Zweck, keine Tageszeiten, keine Verkehrsmittelwahl; Quellen nur Einwohner, Ziele über Proxys. Parameter (β, Gewichte, Widerstandsfaktoren) sind Setzungen und nicht geschätzt.
- Wege über die Landesgrenze und Freizeitverkehr fehlen; deshalb Konfidenz niedrig am Rand.
- Routenwahl nur über den wahrgenommenen Widerstand im Ist-Zustand; Abbiegewiderstände fehlen, Wartezeiten sind pauschal.
- Getrennt erfasste Radwege tragen den Fluss neben der Fahrbahnkante; je Straßenabschnitt sind Fahrbahn und Seitenwege (sidepath_of) zusammen zu lesen.
- Zählstellen messen nur an 100 Querschnitten, vor allem an Hauptstraßen; Werte in Nebenstraßen sind kaum geprüft.
- DB Rad+ ist eine App-Stichprobe und nicht repräsentativ.

## Quellen und Lizenzen

- © OpenStreetMap-Beitragende (ODbL): Radgraph, Geschäfte, Schulen, Hochschulen; abgeleitete Daten unter ODbL.
- Zensus 2022 Gitter 100 m © Statistische Ämter des Bundes und der Länder (dl-de/by-2.0).
- ALKIS © Freie und Hansestadt Hamburg, LGV (dl-de/by-2.0); HVV-GTFS © Hamburger Verkehrsverbund GmbH (dl-de/by-2.0).
- Rad-Zählstellen © Freie und Hansestadt Hamburg (dl-de/by-2.0); DB Rad+ (ODbL).
