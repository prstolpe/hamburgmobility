# Export – Stufe 9

Erzeugt: 2026-11-15T22:12:48+00:00 von `pipeline/s09_export.py`, Version 0.24.0+2026-10-28. Nicht amtlicher Entwurf.

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| nur Bezirke des Arbeitsgebiets | ok | 33712 Abschnitte in 7 Bezirken |
| Tabelle je Bezirk | ok | table/altona.json, table/bergedorf.json, table/eimsbuettel.json, table/hamburg-mitte.json, table/hamburg-nord.json, table/harburg.json, table/wandsbek.json |
| Seite unter 1 GB (GitHub Pages) | ok | data/out zusammen 513 MB |
| segment_id eindeutig und unverändert | ok | Reihenfolge wie discrepancy.parquet |
| Export in EPSG:4326 | ok | EPSG:4326 |
| keine Einzelunfälle oder Rohspuren | ok | Spalten aus PUBLIC_COLUMNS |
| Steckbrief je Abschnitt | ok | 33712 Dateien |
| Begründung je Abschnitt | ok | 0 ohne Klartext |
| Steckbrief je Knotenpunkt | ok | 14312 Dateien |
| Radnetz-Block je Abschnitt | ok | 33712/33712 Abschnitte |
| Radnetz-Kacheln | ok | tiles/cycling.pmtiles, tiles/junctions.pmtiles |
| Radnetz-Robustheit aus c08 übernommen | ok | 50838 Einträge |
| Radnetz-Downloads ohne Rohspuren | ok | Spalten aus plain_language.yaml cycling.columns |
| Robustheit aus make validate übernommen | ok | 33712/33712 Abschnitte, rules.yaml 0.24.0 |

## Kennzahlen

- Abschnitte: 33 712 in Hamburg (7 Bezirke) (4240.4 km)
- Gesamtgröße data/out: 513 MB (Grenze GitHub Pages 1 GB)
- Suchindex: 8 396 Straßennamen; Schulen/Kitas in den Kacheln: 1 545
- Steckbriefe: 33 712 Dateien, zusammen 217.8 MB
- Robustheit (make validate, 500 Läufe): 2 247 Abschnitte „unsicher“ (246.6 km)

- Radnetz (Prompt 21): 33 712 Abschnitte mit Radnetz-Block, 14 312 Knoten-Steckbriefe; Kacheln tiles/cycling.pmtiles und tiles/junctions.pmtiles werden erst geladen, wenn eine Radnetz-Ebene gewählt ist

| Bezirk | Abschnitte | km |
| --- | ---: | ---: |
| Altona | 4 886 | 620.5 |
| Bergedorf | 1 957 | 209.3 |
| Eimsbüttel | 4 004 | 470.4 |
| Hamburg-Mitte | 6 839 | 881.3 |
| Hamburg-Nord | 5 136 | 563.3 |
| Harburg | 3 348 | 465.2 |
| Wandsbek | 7 542 | 1030.4 |

| Datei | Größe |
| --- | ---: |
| `data/out/basemap/basemap.pmtiles` | 58.33 MB |
| `data/out/basemap/extract.json` | 0.00 MB |
| `data/out/basemap/sprites/light.json` | 0.00 MB |
| `data/out/basemap/sprites/light.png` | 0.02 MB |
| `data/out/basemap/sprites/light@2x.json` | 0.00 MB |
| `data/out/basemap/sprites/light@2x.png` | 0.03 MB |
| `data/out/cycle_mesh_gaps.geojson` | 0.64 MB |
| `data/out/districts/altona.json` | 0.00 MB |
| `data/out/districts/bergedorf.json` | 0.00 MB |
| `data/out/districts/eimsbuettel.json` | 0.00 MB |
| `data/out/districts/hamburg-mitte.json` | 0.00 MB |
| `data/out/districts/hamburg-nord.json` | 0.00 MB |
| `data/out/districts/harburg.json` | 0.00 MB |
| `data/out/districts/wandsbek.json` | 0.00 MB |
| `data/out/districts.geojson` | 0.19 MB |
| `data/out/downloads/cycle_network.parquet` | 9.38 MB |
| `data/out/downloads/cycle_segments.geojson` | 38.42 MB |
| `data/out/downloads/cycle_segments.parquet` | 6.03 MB |
| `data/out/downloads/cycling_rules.yaml` | 0.08 MB |
| `data/out/downloads/datenbeschreibung.md` | 0.01 MB |
| `data/out/downloads/design_rules.yaml` | 0.05 MB |
| `data/out/downloads/junctions.geojson` | 11.12 MB |
| `data/out/downloads/junctions.parquet` | 0.86 MB |
| `data/out/downloads/overrides.csv` | 0.00 MB |
| `data/out/downloads/rules.yaml` | 0.10 MB |
| `data/out/downloads/segments.csv` | 15.54 MB |
| `data/out/downloads/segments.geojson` | 59.40 MB |
| `data/out/downloads/segments.parquet` | 8.15 MB |
| `data/out/junction_redirects.json` | 0.12 MB |
| `data/out/licenses.md` | 0.00 MB |
| `data/out/meta.json` | 0.04 MB |
| `data/out/rules.json` | 0.23 MB |
| `data/out/rural_excluded.geojson` | 0.13 MB |
| `data/out/search.json` | 1.67 MB |
| `data/out/search_junctions.json` | 1.58 MB |
| `data/out/tiles/cycling.pmtiles` | 27.08 MB |
| `data/out/tiles/junctions.pmtiles` | 2.80 MB |
| `data/out/tiles/segments.pmtiles` | 13.56 MB |
| `data/out/basemap/fonts/ (768 Glyphen-Dateien)` | 11.08 MB |
| `data/out/junctions/ (14312 Knoten-Steckbriefe)` | 23.06 MB |
| `data/out/table/ (7 Dateien, je Bezirk)` | 5.68 MB |

## Stichprobe (30 zufällige Steckbriefe, Seed 42)

Klartext-Begründung wie im Steckbrief. Bitte gegen Orthophoto/Panoramax prüfen.

| segment_id | Bezirk | Name | Soll | Begründung | Datenunsicherheit | Links |
| --- | --- | --- | --- | --- | --- | --- |
| `seg_034a64bb91378060` | Hamburg-Mitte | An der Alster | GOW50 | steht auf der Liste der Hauptverkehrsstraßen; zu viel Verkehr für eine Hauptstraße mit Tempo 30: 26 000 Autos am Tag, möglich sind 10 000; keine Schule oder Kita direkt an der Straße und wenige Läden; genug Platz für einen eigenen Radweg: Straße 39,7 m breit (nötig 16,2 m); kein Grund für Tempo 30 auf dieser Hauptstraße | mittel: Straßenraumbreite: Ersatzquelle oder Standardwert | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566497,5934734]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.557269/10.003844) · [OSM](https://www.openstreetmap.org/way/51200772) |
| `seg_0ce2aef9f71b0ffd` | Harburg | Jägerfeldweg | ETW30 | für Wege quer durch die Stadt nicht wichtig: Verbindungswert 0,40 (unter 0,87), keine Hauptverkehrsstraße; darum Wohnstraße: Die Straße führt vor allem zu den Häusern im Viertel | mittel: Verbindungswert (nicht alle Merkmale bekannt): Ersatzquelle oder Standardwert | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564805,5920991]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.433967/9.975475) · [OSM](https://www.openstreetmap.org/way/153142386) |
| `seg_0d9f26b2d012b75b` | Wandsbek | Am Hegen | ETW30 | für Wege quer durch die Stadt nicht wichtig: Verbindungswert 0,11 (unter 0,87), keine Hauptverkehrsstraße; darum Wohnstraße: Die Straße führt vor allem zu den Häusern im Viertel | mittel: Verbindungswert (nicht alle Merkmale bekannt): Ersatzquelle oder Standardwert | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577262,5939007]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.594196/10.167388) · [OSM](https://www.openstreetmap.org/way/42411278) |
| `seg_0f3e521c39c53787` | Eimsbüttel | Magdalenenstraße | ETW30 | für Wege quer durch die Stadt nicht wichtig: Verbindungswert 0,05 (unter 0,87), keine Hauptverkehrsstraße; darum Wohnstraße: Die Straße führt vor allem zu den Häusern im Viertel | mittel: Verbindungswert (nicht alle Merkmale bekannt): Ersatzquelle oder Standardwert | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566073,5936119]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.569771/9.997746) · [OSM](https://www.openstreetmap.org/way/4048170) |
| `seg_1027420b2a15fc1d` | Wandsbek | Turnierstieg | ETW30 | für Wege quer durch die Stadt nicht wichtig: Verbindungswert 0,33 (unter 0,87), keine Hauptverkehrsstraße; darum Wohnstraße: Die Straße führt vor allem zu den Häusern im Viertel | mittel: Verbindungswert (nicht alle Merkmale bekannt): Ersatzquelle oder Standardwert | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572768,5939636]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.600491/10.099639) · [OSM](https://www.openstreetmap.org/way/151996921) |
| `seg_2afdc3606c9bc994` | Hamburg-Mitte | – | SW | Autobahn oder Kraftfahrstraße, nur für Autos | hoch | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572876,5935633]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.564500/10.100332) · [OSM](https://www.openstreetmap.org/way/316907867) |
| `seg_2e4755bd181b2cb1` | Eimsbüttel | – | SW | Autobahn oder Kraftfahrstraße, nur für Autos | hoch | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561057,5938950]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.595827/9.922557) · [OSM](https://www.openstreetmap.org/way/329485054) |
| `seg_322370b4a4ef1c59` | Wandsbek | Hammer Straße | ETW30 | für Wege quer durch die Stadt nicht wichtig: Verbindungswert 0,40 (unter 0,87), keine Hauptverkehrsstraße; darum Wohnstraße: Die Straße führt vor allem zu den Häusern im Viertel | mittel: Verbindungswert (nicht alle Merkmale bekannt): Ersatzquelle oder Standardwert | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570635,5935510]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.563704/10.066487) · [OSM](https://www.openstreetmap.org/way/253868088) |
| `seg_325344502fe378a5` | Eimsbüttel | Kronsaalsweg | ETW30 | für Wege quer durch die Stadt nicht wichtig: Verbindungswert 0,40 (unter 0,87), keine Hauptverkehrsstraße; darum Wohnstraße: Die Straße führt vor allem zu den Häusern im Viertel | mittel: Verbindungswert (nicht alle Merkmale bekannt): Ersatzquelle oder Standardwert | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560251,5939037]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.596700/9.910398) · [OSM](https://www.openstreetmap.org/way/284807347) |
| `seg_36bfb2befbdb7f15` | Harburg | Dampfschiffsweg | ETW30 | für Wege quer durch die Stadt nicht wichtig: Verbindungswert 0,27 (unter 0,87), keine Hauptverkehrsstraße; darum Wohnstraße: Die Straße führt vor allem zu den Häusern im Viertel | mittel: Verbindungswert (nicht alle Merkmale bekannt): Ersatzquelle oder Standardwert | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565302,5925361]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.473183/9.983857) · [OSM](https://www.openstreetmap.org/way/8075392) |
| `seg_44cd0158ff0fe3ac` | Altona | Gaußstraße | ETW30 | für Wege quer durch die Stadt nicht wichtig: Verbindungswert 0,14 (unter 0,87), keine Hauptverkehrsstraße; darum Wohnstraße: Die Straße führt vor allem zu den Häusern im Viertel | mittel: Verbindungswert (nicht alle Merkmale bekannt): Ersatzquelle oder Standardwert | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561821,5934521]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.555925/9.933223) · [OSM](https://www.openstreetmap.org/way/177885800) |
| `seg_4cf621c0dd496c0d` | Hamburg-Mitte | Budapester Straße | GOW50 | steht auf der Liste der Hauptverkehrsstraßen; zu viel Verkehr für eine Hauptstraße mit Tempo 30: 26 000 Autos am Tag, möglich sind 10 000; keine Schule oder Kita direkt an der Straße und wenige Läden; genug Platz für einen eigenen Radweg neben der Busspur: Straße 32,8 m breit (nötig 16,7 m); kein Grund für Tempo 30 auf dieser Hauptstraße | mittel: Straßenraumbreite: Ersatzquelle oder Standardwert | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563971,5934253]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.553262/9.965622) · [OSM](https://www.openstreetmap.org/way/1347561646) |
| `seg_4ef85332091f96c5` | Eimsbüttel | Niendorfer Straße | ETW30 | für Wege quer durch die Stadt nicht wichtig: Verbindungswert 0,81 (unter 0,87), keine Hauptverkehrsstraße; darum Wohnstraße: Die Straße führt vor allem zu den Häusern im Viertel | niedrig: Verbindungswert (nicht alle Merkmale bekannt): Ersatzquelle oder Standardwert, Verbindungswert (nicht alle Merkmale bekannt): nahe an der Schwelle; unsicher (Sensitivität) | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563220,5940089]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.605804/9.955476) · [OSM](https://www.openstreetmap.org/way/338299759) |
| `seg_62cfe34d43c51995` | Eimsbüttel | Hildesheimer Stieg | ETW30 | für Wege quer durch die Stadt nicht wichtig: Verbindungswert 0,06 (unter 0,87), keine Hauptverkehrsstraße; darum Wohnstraße: Die Straße führt vor allem zu den Häusern im Viertel | mittel: Verbindungswert (nicht alle Merkmale bekannt): Ersatzquelle oder Standardwert | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562691,5942797]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.630206/9.948029) · [OSM](https://www.openstreetmap.org/way/10060133) |
| `seg_6af3149ffb1f92b1` | Hamburg-Mitte | Neuhöfer Straße | GOW50 | steht auf der Liste der Hauptverkehrsstraßen; wichtig für Wege quer durch die Stadt: Verbindungswert 0,88 (ab 0,87); keine Schule oder Kita direkt an der Straße und wenige Läden; genug Platz für einen eigenen Radweg neben der Busspur: Straße 31,4 m breit (nötig 16,7 m); kein Grund für Tempo 30 auf dieser Hauptstraße | hoch | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564493,5929688]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.512175/9.972554) · [OSM](https://www.openstreetmap.org/way/23495340) |
| `seg_6c8bb1994fcde7da` | Harburg | Fischbeker Moor | ETW30 | für Wege quer durch die Stadt nicht wichtig: Verbindungswert 0,38 (unter 0,87), keine Hauptverkehrsstraße; darum Wohnstraße: Die Straße führt vor allem zu den Häusern im Viertel | mittel: Verbindungswert (nicht alle Merkmale bekannt): Ersatzquelle oder Standardwert | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[555418,5925249]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.473308/9.834947) · [OSM](https://www.openstreetmap.org/way/8320279) |
| `seg_6d5977fd43d3ba6c` | Eimsbüttel | Burgwedeltwiete | ETW30 | für Wege quer durch die Stadt nicht wichtig: Verbindungswert 0,15 (unter 0,87), keine Hauptverkehrsstraße; darum Wohnstraße: Die Straße führt vor allem zu den Häusern im Viertel | mittel: Verbindungswert (nicht alle Merkmale bekannt): Ersatzquelle oder Standardwert | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560268,5944159]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.642727/9.911655) · [OSM](https://www.openstreetmap.org/way/23780951) |
| `seg_6ebbb6e74dbaf000` | Wandsbek | Hofstückenstieg | ETW30 | für Wege quer durch die Stadt nicht wichtig: Verbindungswert 0,15 (unter 0,87), keine Hauptverkehrsstraße; darum Wohnstraße: Die Straße führt vor allem zu den Häusern im Viertel | mittel: Verbindungswert (nicht alle Merkmale bekannt): Ersatzquelle oder Standardwert | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577451,5942335]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.624076/10.171067) · [OSM](https://www.openstreetmap.org/way/298785871) |
| `seg_73b53ad9cbd4df75` | Hamburg-Mitte | St. Petersburger Straße | ETW30 | für Wege quer durch die Stadt nicht wichtig: Verbindungswert 0,36 (unter 0,87), keine Hauptverkehrsstraße; darum Wohnstraße: Die Straße führt vor allem zu den Häusern im Viertel | mittel: Verbindungswert (nicht alle Merkmale bekannt): Ersatzquelle oder Standardwert | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564671,5935268]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.562296/9.976395) · [OSM](https://www.openstreetmap.org/way/252843150) |
| `seg_79cd6e49486c1736` | Altona | Luruper Hauptstraße | GOW50 | steht auf der Liste der Hauptverkehrsstraßen; zu viel Verkehr für eine Hauptstraße mit Tempo 30: 24 000 Autos am Tag, möglich sind 10 000; genug Platz für einen eigenen Radweg neben der Busspur: Straße 21,5 m breit (nötig 16,7 m); Schule, Kita oder Läden an der Straße, aber 24 000 Autos am Tag. Tempo 30 passt nur bis 10 000 Autos am Tag. Darum Tempo 50 mit eigenem Radweg. Ein kurzes Stück mit Tempo 30 vor Ort prüfen | hoch | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558329,5937558]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.583620/9.881084) · [OSM](https://www.openstreetmap.org/way/5026686) |
| `seg_88f48a925ede893f` | Wandsbek | Walddörferstraße | ETW30 | für Wege quer durch die Stadt nicht wichtig: Verbindungswert 0,77 (unter 0,87), keine Hauptverkehrsstraße; darum Wohnstraße: Die Straße führt vor allem zu den Häusern im Viertel | mittel: Verbindungswert (nicht alle Merkmale bekannt): Ersatzquelle oder Standardwert | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572392,5937536]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.581669/10.093474) · [OSM](https://www.openstreetmap.org/way/615261610) |
| `seg_8a65e2308009995d` | Altona | Grönenweg | ETW30 | für Wege quer durch die Stadt nicht wichtig: Verbindungswert 0,04 (unter 0,87), keine Hauptverkehrsstraße; darum Wohnstraße: Die Straße führt vor allem zu den Häusern im Viertel | mittel: Verbindungswert (nicht alle Merkmale bekannt): Ersatzquelle oder Standardwert | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556161,5937030]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.579111/9.848244) · [OSM](https://www.openstreetmap.org/way/1221360789) |
| `seg_8a9636415b35c5cd` | Hamburg-Mitte | Finkenwerder Straße | GOW50 | steht auf der Liste der Hauptverkehrsstraßen; zu viel Verkehr für eine Hauptstraße mit Tempo 30: 28 000 Autos am Tag, möglich sind 10 000; keine Schule oder Kita direkt an der Straße und wenige Läden; genug Platz für einen eigenen Radweg neben der Busspur: Straße 30,4 m breit (nötig 16,7 m); kein Grund für Tempo 30 auf dieser Hauptstraße | hoch | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561448,5930218]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.517300/9.926746) · [OSM](https://www.openstreetmap.org/way/633864638) |
| `seg_a6d869d46da424f7` | Altona | Klövensteenweg | ETW30 | für Wege quer durch die Stadt nicht wichtig: Verbindungswert 0,45 (unter 0,87), keine Hauptverkehrsstraße; darum Wohnstraße: Die Straße führt vor allem zu den Häusern im Viertel | mittel: Verbindungswert (nicht alle Merkmale bekannt): Ersatzquelle oder Standardwert | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[550554,5938020]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.588584/9.763726) · [OSM](https://www.openstreetmap.org/way/132414981) |
| `seg_a8a040ce7519d057` | Hamburg-Nord | Krohnstieg | GOW50 | steht auf der Liste der Hauptverkehrsstraßen; zu viel Verkehr für eine Hauptstraße mit Tempo 30: 33 000 Autos am Tag, möglich sind 10 000; genug Platz für einen eigenen Radweg neben der Busspur: Straße 57,3 m breit (nötig 16,7 m); Schule, Kita oder Läden an der Straße, aber 33 000 Autos am Tag. Tempo 30 passt nur bis 10 000 Autos am Tag. Darum Tempo 50 mit eigenem Radweg. Ein kurzes Stück mit Tempo 30 vor Ort prüfen | hoch | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567214,5944991]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.649362/10.016889) · [OSM](https://www.openstreetmap.org/way/26572251) |
| `seg_d05f61db966ecf50` | Bergedorf | Felix-Jud-Ring | ETW_ERF | heute schon eine Spielstraße (verkehrsberuhigter Bereich) | hoch | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576020,5926734]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.484084/10.145637) · [OSM](https://www.openstreetmap.org/way/26130987) |
| `seg_d1b80af39fe31a09` | Eimsbüttel | Langenfelder Damm | ETW30 | für Wege quer durch die Stadt nicht wichtig: Verbindungswert 0,70 (unter 0,87), keine Hauptverkehrsstraße; darum Wohnstraße: Die Straße führt vor allem zu den Häusern im Viertel | mittel: Verbindungswert (nicht alle Merkmale bekannt): Ersatzquelle oder Standardwert | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561814,5937572]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.583350/9.933730) · [OSM](https://www.openstreetmap.org/way/80992104) |
| `seg_d20cf44f0ab4a172` | Eimsbüttel | Waldrebenweg | ETW30 | für Wege quer durch die Stadt nicht wichtig: Verbindungswert 0,13 (unter 0,87), keine Hauptverkehrsstraße; darum Wohnstraße: Die Straße führt vor allem zu den Häusern im Viertel | mittel: Verbindungswert (nicht alle Merkmale bekannt): Ersatzquelle oder Standardwert | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557996,5941183]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.616240/9.876738) · [OSM](https://www.openstreetmap.org/way/4974282) |
| `seg_df3f794ec87eef42` | Wandsbek | Oldenfelder Stieg | GOW50 | steht auf der Liste der Hauptverkehrsstraßen; zu viel Verkehr für eine Hauptstraße mit Tempo 30: 26 000 Autos am Tag, möglich sind 10 000; genug Platz für einen eigenen Radweg: Straße 25,8 m breit (nötig 16,2 m); Schule, Kita oder Läden an der Straße, aber 26 000 Autos am Tag. Tempo 30 passt nur bis 10 000 Autos am Tag. Darum Tempo 50 mit eigenem Radweg. Ein kurzes Stück mit Tempo 30 vor Ort prüfen | hoch | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576535,5941224]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.614233/10.156940) · [OSM](https://www.openstreetmap.org/way/222320594) |
| `seg_fb505f767108b67f` | Bergedorf | Bergedorfer Straße | GOW50 | steht auf der Liste der Hauptverkehrsstraßen; wichtig für Wege quer durch die Stadt: Verbindungswert 0,90 (ab 0,87); zu viel Verkehr für eine Hauptstraße mit Tempo 30: 34 000 Autos am Tag, möglich sind 10 000; keine Schule oder Kita direkt an der Straße und wenige Läden; genug Platz für einen eigenen Radweg neben der Busspur: Straße 40,5 m breit (nötig 16,7 m); kein Grund für Tempo 30 auf dieser Hauptstraße | hoch | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578222,5929414]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.507845/10.179478) · [OSM](https://www.openstreetmap.org/way/229835368) |

## Lizenz

Abschnittsdatensatz: ODbL 1.0 (© OpenStreetMap-Beitragende); amtliche Quellen dl-de/by-2.0 bzw. laut Quelle; Unfälle: © Statistische Ämter des Bundes und der Länder, Unfallatlas (nur Summen). Siehe docs/licenses.md.

