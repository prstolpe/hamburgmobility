# Hamburger Straßenfunktionsplan mit Claude Code – Schritt-für-Schritt-Anleitung

Oct 27, 2026 · @Raphael Stolpe

## Kurzüberblick

Ein Team aus zwei bis drei Personen kann mit Claude Code in rund 25–40 Personentagen einen nachvollziehbaren Entwurf eines Hamburger Straßenfunktionsplans für einen Pilotbezirk erzeugen und als statische Karte veröffentlichen \[B\]. Die Automatik schlägt je Straßenabschnitt eine Soll-Kategorie vor und begründet sie; Fachleute korrigieren über eine versionierte Datei, und jeder Lauf ist reproduzierbar.

**Was am Ende entsteht**

- Ein Git-Repository mit Pipeline (Python), Regelwerk `config/rules.yaml`, Korrekturebene `overrides/overrides.csv` und automatisierten Tests.
- Ein Datensatz je Straßenabschnitt (GeoParquet, GeoJSON) mit Soll-Kategorie, Ist-Tempo, Diskrepanztyp, Querschnittsbreite, Machbarkeit, gegriffenen Regeln und Unsicherheit.
- Eine öffentliche, serverlose Webseite (MapLibre GL JS mit PMTiles) mit Ebenen, Steckbriefen, Filtern, Methodenseite, Download und Rückmeldelink, deutlich gekennzeichnet als nicht amtlicher Diskussionsentwurf.

**Aufwand je Phase (Schätzung \[B\])**

| Phase | Personentage | Wer vor allem |
| --- | --- | --- |
| Regelwerk abstimmen (Teil 1) | 3–5 | Verkehrsplaner\*in |
| Daten beschaffen und prüfen (Teil 2) | 3–5 | GIS-Person mit Claude Code |
| Netz, Conflation, Merkmale (Teil 3, Stufen 1–4) | 5–8 | GIS-Person mit Claude Code |
| Klassifikation, Kohärenz, Diskrepanz (Stufen 5–8) | 4–6 | beide |
| Querschnitt Stufe a (Teil 4) | 3–5 | GIS-Person |
| Webseite (Teil 5) | 4–6 | Web-affine Person mit Claude Code |
| Validierung und Korrekturrunde (Teil 7) | 5–10 | Verkehrsplaner\*in, Ortskundige |

**Benötigte Kenntnisse:** eine Person mit sicherem Python- und GIS-Grundwissen (geopandas, Koordinatensysteme, Git), eine Verkehrsplaner\*in, die Regeln und Korrekturen verantwortet, optional eine Person für Webseite und Barrierefreiheit. Claude Code schreibt den Großteil des Codes; Menschen prüfen Stichproben und entscheiden strittige Fälle.

**Fünf Befunde aus der Recherche (Stand 27.10.2026)**

- Die BVM stellt das Hauptverkehrsstraßennetz weiterhin mit Kartenstand September 2023 bereit; es kennt nur Hauptverkehrs- und Bezirksstraßen ([BVM](https://www.hamburg.de/politik-und-verwaltung/behoerden/bvm/hauptverkehrsstrassen-193350)) \[F\]. Eine neuere funktionale Netzkategorisierung ließ sich nicht finden \[Wissenslücke\].
- Die zulässigen Höchstgeschwindigkeiten (u. a. Tempo-30-Zonen, verkehrsberuhigte Bereiche) sind als OGC API Features offen abrufbar ([api.hamburg.de](https://api.hamburg.de/datasets/v1/zulaessige_hoechstgeschwindigkeiten/collections/tempo30zonen)) \[F\]. Das Ist-Tempo ist damit die am besten belegte Ist-Größe.
- Für die GOW30 gibt es seit Mai 2023 vorläufige CROW-Gestaltungsmerkmale mit konkreten Fahrbahnbreiten und Kfz-Obergrenzen; sie sind ausdrücklich vorläufig ([CROW 2023](https://www.amersfoort.nl/sites/default/files/2025-09/2023-crow-handreiking-voorlopige-inrichtingskenmerken-gow30.pdf)) \[F\].
- Die RASt 06 ist weiterhin die aktuelle Ausgabe ([DIN Media](https://www.dinmedia.de/en/technical-rule/fgsv-200/100597805)) \[F\]; Neufassungen von RASt, ERA und EFA sind in Arbeit \[D\]. Das Regelwerk muss deshalb versioniert sein.
- Hamburg ersetzt seit 2025 die Velorouten schrittweise durch das „Radnetz Hamburg“ ([OSM-Wiki](https://wiki.openstreetmap.org/wiki/DE:Tag:cycle_network%3DDE:HH:Radnetz_Hamburg)) \[F\]; das Radnetz-Overlay muss diese Umstellung abbilden.

**Grundsatz:** Der Entwurf ist kein amtlicher Plan und keine Anordnungsgrundlage. Er macht eine Netzlogik prüfbar und lädt Verwaltung und Politik ein, sie zu übernehmen oder begründet abzuweichen \[B\].

## Architekturübersicht der Pipeline

&#91;embedded content: Pipeline · 9 Stufen, 2 Eingabedateien\]

Die Stufen 1–4 erzeugen Abschnitte mit Merkmalen, 5–8 klassifizieren, prüfen, korrigieren und bewerten, Stufe 9 baut die Webseite. Fachliche Entscheidungen stecken ausschließlich in `rules.yaml` und `overrides.csv`; Stufe 4 enthält die Querschnittsbreite aus Teil 4.

| Stufe | Eingabe | Ausgabe | Werkzeug |
| --- | --- | --- | --- |
| 1 Beschaffung | Anhang B | `data/raw/*.parquet`, `manifest.json` | pyogrio, requests |
| 2 Netz | OSM-PBF | `segments.parquet` | pyrosm, OSMnx, networkx |
| 3 Conflation | HH-SIB, Tempo, HVS | Attribute, `match_quality` | geopandas, DuckDB |
| 4 Merkmale | GTFS, ALKIS, Zensus, OSM | `features.parquet` | igraph, DuckDB |
| 5 Klassifikation | `rules.yaml` | `cat_proposed`, `rule_trace` | pydantic, Python |
| 6 Kohärenz | Graph | `flags` | networkx |
| 7 Korrektur | `overrides.csv` | `cat_final` | Python, Git-Review |
| 8 Diskrepanz | Unfallatlas, Merkmale | Typ, Stärke, Priorität | DuckDB |
| 9 Export | alles | PMTiles, GeoJSON, JSON | tippecanoe |

## Teil 1 – Fachliches Regelwerk: SWOV und Duurzaam Veilig maschinenlesbar machen

Das Regelwerk übersetzt Duurzaam Veilig in fünf Hamburger Kategorien, klare Anforderungen je Kategorie, sechs Netzregeln und drei Diskrepanzdimensionen. Jede Regel steht mit Schwellenwert, Quelle und Herkunftskennzeichnung in `config/rules.yaml` (Anhang A). Herkunft: `swov_crow` (niederländische Primärquelle), `de_regelwerk` (FGSV, StVO/VwV), `hamburg` (ReStra, Hamburger Daten), `assumption` (eigene Annahme, zu prüfen).

### 1.1 Grundlagen und Stand

- **Duurzaam Veilig 3 (DV3, 2018)**: Die Visie 2018–2030 nennt fünf Prinzipien; drei davon sind Gestaltungsprinzipien – Funktionalität, die (bio)mechanischen Prinzipien Homogenität und physische Fehlerverzeihlichkeit sowie die psychologischen Prinzipien Erkennbarkeit und Zustandsbewusstsein (statusonderkenning); dazu kommen die Organisationsprinzipien Verantwortung sowie Lernen und Innovieren ([SWOV R-2018-6B](https://swov.nl:443/node/16907)) \[F\].
- **SWOV-Factsheet Prinzipien für ein sicheres Straßennetz (April 2023)**: drei Kategorien, zwölf funktionale Anforderungen auf Netz-, Routen- und Entwurfsebene, Empfehlung von Tempo 30 auf Verbindungsstraßen, an denen kein getrennter Radweg realisierbar ist ([SWOV 2023](https://swov.nl/en/fact-sheet/principles-safe-road-network), vom Nutzer bereitgestellt) \[F\].
- **CROW Afwegingskader 30 km/h (2021)** und **Handreiking voorlopige inrichtingskenmerken GOW30 (Mai 2023, Version 1.0)**: Entscheidungsschema ETW30/GOW50/GOW30 und vorläufige Gestaltungsmerkmale ([CROW 2023](https://www.amersfoort.nl/sites/default/files/2025-09/2023-crow-handreiking-voorlopige-inrichtingskenmerken-gow30.pdf)) \[F\]. CROW will die Merkmale erst nach Evaluationen in die ASVV übernehmen \[F\].
- **Erkennbarkeit (EHK)**: Die essentiellen Erkennbarkeitsmerkmale stehen in CROW-Publikation 315 „Basiskenmerken wegontwerp“ (2012) und unterscheiden Zonenbeschilderung und Markierung je Straßentyp (Factsheet 2023, Tabelle 1) \[F\].
- **Risiko-Indikatoren des Kennisnetwerk SPV**: „Veilige wegen“ ist der Anteil der Kfz-Fahrleistung auf Straßen, die als ausreichend sicher gelten; „Veilige snelheid“ ist der Anteil des Kfz-Verkehrs, der je Straßentyp nicht schneller fährt als die sichere Geschwindigkeit und das Tempolimit ([KN SPV 2023](https://swov.nl/sites/default/files/bestanden/downloads/2023_SWOV_Risico-indicatoren-april2023_KennisnetwerkSPV.pdf)) \[F\]. Die Operationalisierung je Tempoklasse liegt seit 2021 vor ([RWS/Sweco 2021](https://www.ndw.nu/binaries/ndw/documenten/publicaties/2021/7/23/operationalisatie-definitie-van-voldoende-veilige-wegen-en-fietsinfrastructuur/Operationalisatie+Definitie+KN+SPV+30-50-70-60-80-fietspaden+definitief+def.pdf)) \[F\].
- **Grijze wegen**: Straßen, bei denen Funktion, Gestaltung und Gebrauch nicht eindeutig sind oder nicht zusammenpassen ([SWOV R-2021-27](https://swov.nl:443/system/files/publication-downloads/R-2021-27.pdf)) \[F\]. Die SPV-Factsheets halten fest, dass das Tempolimit dort nicht die sichere Geschwindigkeit sein muss ([KN SPV 2020](https://swov.nl:443/sites/default/files/bestanden/downloads/2020_SWOV_Factsheet-infra-voldoende-veilig_KennnisnetwerkSPV.pdf)) \[F\].
- **VSGS (Veilige Snelheden, Geloofwaardige Snelheidslimieten)**: SWOV-Methode zur Bewertung der Glaubwürdigkeit eines Limits aus Straßen- und Umfeldmerkmalen, validiert in R-2022-5 \[F\]. CROW stützt darauf, dass Fahrbahnbreite, kurze Geraden und vertikale Elemente die Glaubwürdigkeit von 30 nachweislich erhöhen \[F\].

### 1.2 Was die Prinzipien für die Automatik bedeuten

| Prinzip | Kern \[F\] | Umsetzung in der Klassifikation \[B\] |
| --- | --- | --- |
| Funktionalität | Fließen und Austauschen trennen; eine Straße hat eine Funktion | Je Abschnitt zwei Scores (Verbindung, Aufenthalt/Erschließung); genau eine Soll-Kategorie; sind beide hoch, entsteht GOW30 oder ein Konfliktflag |
| Homogenität | geringe Unterschiede in Masse, Tempo, Richtung | Radverkehr auf der Fahrbahn → Soll-Tempo höchstens 30; bei 50 getrennte Radwege Pflicht; ab 2×2 Fahrstreifen bauliche Richtungstrennung |
| Erkennbarkeit | einheitliches Bild je Kategorie | Ist-Gestaltungsmerkmale (Mittelmarkierung, Radführung, Belag, Parken) gegen ein Soll-Merkmalsset prüfen; Abweichung = Diskrepanz „Erkennbarkeit“ |
| Fehlerverzeihlichkeit | verzeihende Seitenräume, keine harten Hindernisse | Innerorts geringes Gewicht; Hindernisprüfung nur bei Soll ≥ 50 (Bäume, Masten nahe Fahrbahnrand) |
| Zustandsbewusstsein | Fähigkeiten der Nutzenden beachten | Nicht aus Geodaten ableitbar; nur indirekt über Gewichte für Schulen, Kitas, Senioreneinrichtungen in der Priorisierung |

### 1.3 Kategoriensystem für Hamburg

Fünf Kategorien plus zwei Außerorts-Varianten; die Klassen K1–K4 aus Bericht 2 bleiben als Kommunikationsbegriffe erhalten \[B\].

| Code | NL-Vorbild | Arbeitsbegriff Hamburg | Bericht 2 | RIN-Kategoriengruppe (Näherung) \[B\] | RASt-Entwurfssituationen (Näherung) \[B\] | Regeltempo |
| --- | --- | --- | --- | --- | --- | --- |
| SW | Stroomweg | Schnellverkehrsstraße (Autobahn, anbaufreie Kfz-Straße) | – | AS, VS I–II | – (RAA) | nach StVO, ≥ 60 |
| GOW50 | Gebiedsontsluitingsweg 50 | Stadtmagistrale | K1 | VS II–III, HS III | Verbindungsstraße, Anbaufreie Straße, Örtliche Einfahrtsstraße | 50 |
| GOW30 | Gebiedsontsluitingsweg 30 | Stadtstraße 30 | K2 | HS III–IV, ES IV | Örtliche Geschäftsstraße, Hauptgeschäftsstraße, Quartiersstraße, Sammelstraße | 30 |
| ETW30 | Erftoegangsweg 30 | Quartiersstraße | K3 | ES IV–V | Wohnstraße, Sammelstraße, Gewerbestraße | 30 (Zone) |
| ETW-ERF | Erf (15 km/h) | Aufenthaltsstraße | K4 | ES V | Wohnweg, Wohnstraße als verkehrsberuhigter Bereich, Fußgängerzone, Schulstraße | Schrittgeschwindigkeit |
| GOW80 / ETW60 | Außerorts | Landstraße Vier- und Marschlande, Süderelbe | – | LS | – (RAL) | 80 / 60 bzw. Annahme |

Die Bezeichnungen der RIN-Gruppen (AS, LS, VS, HS, ES) und der RASt-Entwurfssituationen folgen RIN 2008 und RASt 06 \[F\]; die Zuordnung ist eine Näherung und vor Gebrauch am Original zu prüfen \[B\]. In den Niederlanden sind Stroomwege nur außerhalb bebauter Gebiete vorgesehen (Factsheet 2023) \[F\]; in Hamburg betrifft SW deshalb vor allem Autobahnen und autobahnähnliche Abschnitte \[B\].

### 1.4 Anforderungen je Kategorie

| Merkmal | GOW50 / K1 | GOW30 / K2 | ETW30 / K3 | ETW-ERF / K4 |
| --- | --- | --- | --- | --- |
| Regeltempo | 50 \[F\] | 30, Vorfahrt gegenüber ETW \[F CROW\] | 30-Zone, rechts vor links \[F\] | Schritt \[F StVO\] |
| Rad–Kfz | getrennter, benutzungspflichtiger Radweg oder Parallelroute; keine Radfahr- oder Schutzstreifen (CROW-Verschärfung) \[F\]; DE-Regelmaß Radweg 2,00 m plus Sicherheitstrennstreifen 0,75 m (min. 0,50 m) \[F ERA 2010\] | Radfahrstreifen bzw. fietsstroken mind. 1,70 m, ideal 2,20 m, oder vorhandener Radweg; keine Fahrradstraße \[F CROW\]; DE: Radfahrstreifen 1,85 m inkl. Breitstrich, E Klima: 2,25 m \[F\] | Mischverkehr; keine Radstreifen, Hauptradroute als Fahrradstraße \[F CROW\] | Mischfläche \[F\] |
| Querungen | konzentriert; Zebrastreifen auf Plateau oder Mittelinsel, alternativ Signal \[F\] | überall erlaubt, gebündelte Querungen mit Tempodämpfung fördern \[F CROW\] | überall ohne Anlage \[F\] | ganze Fläche \[F\] |
| Knoten | mit GOW: Kreisverkehr, sonst Signal mit Plateau; mit ETW: Vorfahrt GOW, Gehwegüberfahrt \[F\] | mit ETW: Gehwegüberfahrt oder Vorfahrtknoten mit Plateau; mit GOW: Kreisverkehr \[F CROW\] | gleichrangig; Plateaus an Knoten \[F\] | Ein- und Ausfahrt als Gehwegüberfahrt \[F CROW\] |
| Radfurten an Knoten | 2–5 m abgesetzt, Mittelinsel; Einrichtungsradwege \[F SWOV\] | wie GOW50, soweit Radweg vorhanden \[B\] | – | – |
| Parken | nicht auf oder längs der Fahrbahn (KN SPV); kein Schräg- oder Senkrechtparken (CROW) \[F\] | nicht auf der Fahrbahn; längs nur mit Puffer zum Radstreifen \[F CROW\] | auf Fahrbahn oder Buchten zulässig \[F\] | nur markiert \[B\] |
| Fahrbahn / Profil | ab 2×2 bauliche Richtungstrennung \[F CROW\]; Busroute 7,00 m \[F CROW\] | schmales Profil mit Radstreifen 5,80–8,40 m bis 6.000 Kfz/Tag; breites Profil 8,40–10,70 m bis 10.000 Kfz/Tag; mit Radweg ≥ 5,80 m \[F CROW\] | 5,80 m ideal für Mischverkehr, Busroute 6,50 m \[F CROW\]; Tempodämpfer etwa alle 100 m (KN SPV, „optimal“) \[F\] | Gestaltung als Aufenthaltsfläche \[B\] |
| Erschließung | Grundstückszufahrten möglichst gebündelt \[B\] | Zufahrten zulässig \[F CROW\] | uneingeschränkt \[F\] | uneingeschränkt \[F\] |
| Aufenthalt | untergeordnet, aber Gehwege und Bäume vorgesehen \[B\] | hoch: Querbarkeit, Lieferzonen, Bäume \[B, Bericht 2\] | hoch \[F\] | vorrangig \[F\] |

### 1.5 Regeln für die Netzkohärenz

Die Netzregeln setzen die vier SWOV-Anforderungen auf Netzebene um: große zusammenhängende Wohngebiete, wenig Fahrleistung auf unsichereren Straßen, kurze Wege, kürzester gleich sicherster Weg (Factsheet 2023) \[F\]. Prüfbar werden sie so \[B\]:

1. **N1 Durchgängigkeit:** Jeder GOW-Zug endet an beiden Enden an GOW, SW oder der Stadtgrenze.
2. **N2 Keine Inseln:** Ein Kategoriewechsel für einen Abschnitt kürzer als 200 m zwischen zwei Abschnitten gleicher Kategorie wird markiert (Schwellenwert = Annahme).
3. **N3 Aufenthaltsbereiche:** Flächen, die von GOW/SW umschlossen sind, werden gebildet; Bereiche unter 25 ha oder mit sehr langer Grenze im Verhältnis zur Fläche werden markiert (Annahme).
4. **N4 Kürzester gleich sicherster Weg:** Für Knotenpaare des GOW-Netzes wird der zeitkürzeste Weg bei Soll-Tempo mit dem auf GOW/SW beschränkten Weg verglichen; führt der kürzeste über mehr als 300 m ETW, entsteht ein Schleichverkehrsflag (Annahme).
5. **N5 Übergänge:** Wechsel GOW50→GOW30 und GOW→ETW erfordern eine Torsituation; ein direkter Übergang 70/80→30 ist nicht vorgesehen \[F CROW-Tabelle 4\].
6. **N6 Knotenkatalog:** Aus dem Kategoriepaar am Knoten wird der Soll-Knotentyp abgeleitet (Tabelle 1.4); Abweichungen vom Ist (z. B. Ampel statt Gehwegüberfahrt) werden gelistet.

### 1.6 Kriterien für die Diskrepanzanalyse

Die Diskrepanz vergleicht Soll-Funktion und Ist-Zustand in drei Dimensionen, angelehnt an die SPV-Indikatoren „Veilige wegen“ und „Veilige snelheid“ \[B\]:

| Dimension | Ist-Merkmal | Diskrepanz, wenn … | Quelle der Regel |
| --- | --- | --- | --- |
| Tempo | angeordnete Höchstgeschwindigkeit | Ist-Limit > Soll-Tempo (z. B. 50 auf Soll-GOW30) | KN SPV, Veilige snelheid \[F\]; Schwelle \[B\] |
| Gestaltung | Radführung, Mittelmarkierung, Parken, Querungen, Breite | Soll-Merkmal fehlt oder Merkmal einer anderen Kategorie vorhanden (z. B. Radstreifen auf Soll-GOW50) | CROW 2023, KN SPV \[F\] |
| Nutzung | DTV, Buslinien, Durchgangsanteil | DTV außerhalb der Spanne der Soll-Kategorie (z. B. > 10.000 Kfz/Tag auf GOW30 mit Radstreifen) | CROW 2023 \[F\] |

Daraus ergeben sich drei Typen „grauer Straßen“, wie sie auch in der niederländischen Praxis beschrieben werden ([CVS 2015](https://www.cvs-congres.nl/cvspdfdocs_2015/cvs15_085.pdf)) \[F\]: D1 Erschließungsstraße mit Durchfluss-Gestaltung, D2 sparsam gestaltete Verbindungsstraße, D3 Mischform mit Merkmalen beider Kategorien. Jede Diskrepanz erhält einen Typ, eine Stärke (0–3) und die verursachenden Merkmale \[B\].

### 1.7 Das Regelwerk als Datei

Jede Regel hat eine ID, eine Bedingung, Schwellenwerte, eine Quelle mit Seitenangabe, den Herkunftstyp, einen Prüfstatus und eine Version. Die Pipeline schreibt für jeden Abschnitt die IDs der gegriffenen Regeln und die Eingangswerte mit; damit ist jede Einstufung erklärbar und eine Sensitivitätsanalyse möglich (Teil 7). Der vollständige Entwurf steht in Anhang A.

## Teil 2 – Datengrundlagen

Für Netz, Ist-Tempo, Nutzung, Gebäude, Flächen, Bäume, ÖPNV und Unfälle gibt es offene Daten unter Datenlizenz Deutschland Namensnennung 2.0 (dl-de/by-2.0) oder ODbL; die größten Lücken sind Kfz-Verkehrsstärken auf Bezirksstraßen und die Aufteilung des Querschnitts \[B\]. Die vollständige Datenliste mit Zugriff, Lizenz, Aktualität, Zweck und Prüfstatus steht in Anhang B.

### 2.1 Prüfung des Referenznetzes

- **Hauptverkehrsstraßennetz:** Die BVM-Seite bietet weiterhin die Karte mit Stand September 2023 und Listen je Bezirk an; das Netz unterscheidet nur Hauptverkehrs- und Bezirksstraßen und regelt Zuständigkeiten ([BVM](https://www.hamburg.de/politik-und-verwaltung/behoerden/bvm/hauptverkehrsstrassen-193350)) \[F\]. Grundlage ist ein Senatsbeschluss von 2005 mit Kriterienraster ([BSU 2005](https://epub.sub.uni-hamburg.de/epub/volltexte/2009/4062/pdf/kriterien_hauptverkehrsstrassen.pdf)) \[F\].
- **Maschinenlesbar** liegt das klassifizierte und kommunale Netz im WFS „Strategisches Straßennetz Hamburg“ (HH-SIB) vor; die Metadaten nennen als letzte Revision Dezember 2019 ([GDI-DE](https://gdk.gdi-de.org/geonetwork/srv/api/records/2BAA8BEB-5C50-401A-BA06-DF20F4D4EBBE)) \[F\]. Ob es ein Attribut „Hauptverkehrsstraße“ mit Stand 2023 enthält, ist per `DescribeFeatureType` zu prüfen \[Wissenslücke\]; sonst wird das HVS-Netz aus der PDF-Karte bzw. den Bezirkslisten digitalisiert.
- **Weitergehende Kategorisierungen:** Eine neuere funktionale Kategorisierung des Gesamtnetzes ließ sich nicht finden \[Wissenslücke\]. Verwandte Netze, die als Overlays dienen: die zwölf „Hamburger Magistralen“ der BSW als städtebauliche Kategorie ([BSW](https://www.hamburg.de/politik-und-verwaltung/behoerden/behoerde-fuer-stadtentwicklung-und-wohnen/hintergrund-864874)) \[F\] und das „Radnetz Hamburg“ mit Radrouten und Radrouten+, das seit 2025 die Velorouten ersetzt ([OSM-Wiki](https://wiki.openstreetmap.org/wiki/DE:Tag:cycle_network%3DDE:HH:Radnetz_Hamburg)) \[F\]. Ein Lkw- und Hafenvorrangnetz als Geodatensatz wurde nicht gefunden \[Wissenslücke\].

### 2.2 Was die wichtigsten Quellen leisten

| Bedarf | Beste offene Quelle | Befund |
| --- | --- | --- |
| Netzgeometrie, Topologie | OSM (Geofabrik-Auszug) plus HH-SIB-WFS | OSM ist topologisch sauber und attributreich; HH-SIB liefert amtliche Zuordnung \[B\] |
| Ist-Tempo | OGC API „Zulässige Höchstgeschwindigkeiten Hamburg“ | Collections u. a. Tempo-30-Zonen (19.469 Objekte) und verkehrsberuhigte Bereiche (1.470 Objekte) beim Abruf am 27.10.2026 \[F\] |
| Kfz-Verkehrsstärke | OGC API „Verkehrsmengen auf Hauptverkehrsstraßen“ | Datensatz vorhanden; geprüfte Collection: DTV Autobahnen 2019 (575 Objekte) \[F\]; aktuellere Jahrgänge und Bezirksstraßen im Projekt prüfen \[Wissenslücke\] |
| Radverkehrsstärke | OGC API „Radverkehrsmengen (DB Rad+)“ | Collection „Jahr 2022“ vorhanden \[F\]; Stichprobe aus App-Nutzenden, nicht repräsentativ \[B\] |
| Flächen, Straßenraum | ALKIS (WFS Liegenschaften, NAS-Download), tatsächliche Nutzung | offen unter dl-de/by-2.0 ([GDI-DE](https://gdk.gdi-de.org/geonetwork/srv/api/records/00F5606E-4563-49C6-960A-72617C9E5256)) \[F\] |
| Gebäude | 3D-Gebäudemodell LoD2-DE (ab 2016), LoD3.0-HH | LoD2 ab 2016 verfügbar, LoD3.0 auf Basis 2020 ([GDI-DE](https://gdk.gdi-de.org/geonetwork/srv/api/records/D63EFF3A-B354-4C21-8248-2F3F989AFF8C)) \[F\] |
| Orthophotos | DOP20 | jährliche Frühjahrsbefliegung, 20 cm Bodenauflösung ([LGV](https://www.hamburg.de/politik-und-verwaltung/behoerden/behoerde-fuer-stadtentwicklung-und-wohnen/aemter-und-landesbetrieb/landesbetrieb-geoinformation-und-vermessung/produkte-und-dienstleistungen/geodaten-des-lgv/digitaleorthophotos-244130)) \[F\] |
| Straßenbäume | Straßenbaumkataster | rund 227.000 Straßenbäume, offen im Transparenzportal ([BUKEA 2023](https://www.hamburg.de/politik-und-verwaltung/behoerden/bukea/aktuelles/pressemeldungen/2023-11-10-bukea-25-jahre-digitales-baumkataster-235658)) \[F\] |
| ÖPNV | HVV-GTFS im Transparenzportal | Feed mit 872 Linien, gültig 08.04.–12.12.2026, dl-de/by-2.0 ([Mobility Database](https://mobilitydatabase.org/feeds/mdb-3362), [OSM-Wiki](https://wiki.openstreetmap.org/wiki/DE:Permissions/hvv)) \[F\] |
| Bevölkerung | Zensus 2022, 100-m-Gitter | als CSV-Gitter offen ([Zensus 2022](https://zensus2022.de/EN/Census_results/02-release-of-results.html?nn=470744)) \[F\] |
| Unfälle | Unfallatlas der Statistischen Ämter | Unfälle mit Personenschaden, dl-de/by-2.0 \[F\]; Abdeckung Hamburgs je Jahr im Download prüfen \[Wissenslücke\] |
| Zustand, Belag | WFS ZEB-Zustandsklassen; WFS Straßendeckschichttypen (RLS-19) | vorhanden \[F\]; Belag hilft bei Erkennbarkeit (Pflaster vs. Asphalt) \[B\] |

### 2.3 Datenlücken und wie man sie schließt

| Lücke | Wirkung | Schließen durch \[B\] |
| --- | --- | --- |
| Kfz-DTV auf Bezirksstraßen | Nutzungsdimension unsicher; GOW30-Profilgrenzen (6.000/10.000 Kfz/Tag) nicht prüfbar | Proxy aus Netzzentralität und Busfrequenz; Transparenzanfrage nach Zählungen der Bezirke; eigene Querschnittszählungen an 20–30 Stellen (Telraam o. ä.) zur Kalibrierung |
| Aufteilung Fahrbahn/Radweg/Gehweg/Parken | Machbarkeit nur grob | OSM-Tags `cycleway:*`, `sidewalk:*`, `parking:*`; Orthophoto-Segmentierung in Stufe c (Teil 4); Transparenzanfrage nach LSBG/Bezirks-Bestandsplänen |
| Unfallorte nur polizeilich erfasst | Unterschätzung von Rad-Alleinunfällen | Hinweis auf Rettungsdienstdaten wie in Amsterdam (Bericht 2); Unfälle als Gewicht, nicht als Kriterium |
| Schulwege | Priorisierung unscharf | Schulstandorte als Puffer; Schulwegpläne der Schulen sammeln (Bericht 2, M6) |
| HVS-Netz 2023 nicht als Vektordatensatz bestätigt | Vergleichsebene | WFS prüfen; sonst Digitalisierung aus PDF und Bezirkslisten |
| Lkw-/Hafenvorrangnetz | Overlay fehlt | HPA- und BVM-Anfrage; bis dahin `hgv=designated` aus OSM |

### 2.4 Lizenzen in einem Satz

Amtliche Hamburger Daten (dl-de/by-2.0) verlangen Namensnennung; OSM-Daten (ODbL) verlangen Namensnennung und machen eine aus OSM abgeleitete Datenbank weitergabepflichtig unter ODbL – das Projekt veröffentlicht seinen Abschnittsdatensatz deshalb insgesamt unter ODbL mit Quellenvermerken für alle amtlichen Quellen \[B; juristische Feinheiten vor Veröffentlichung prüfen\].

## Teil 3 – Automatisierte Pipeline

Die Pipeline ist eine Kette aus neun Python-Stufen, die über GeoParquet-Dateien kommunizieren, von einem `Makefile` (oder `snakemake`) gesteuert werden und bei gleichem Datenstand und gleicher Regelversion dasselbe Ergebnis liefern \[B\]. Alle Berechnungen laufen in ETRS89/UTM 32N (EPSG:25832), erst der Export rechnet in WGS 84 um.

### 3.1 Werkzeugwahl

| Aufgabe | Werkzeug | Begründung \[B\] |
| --- | --- | --- |
| Umgebung | Python 3.12, `uv` mit Lockfile | reproduzierbare Abhängigkeiten |
| Vektordaten | geopandas, shapely 2, pyogrio | Standard, schnell genug für eine Stadt |
| OSM-Import | pyrosm oder osmium + OSMnx | pyrosm liest PBF-Auszüge direkt; OSMnx vereinfacht den Graphen |
| Netzwerk | networkx, für Zentralität igraph oder networkit | networkx ist lesbar; Betweenness auf \~100.000 Kanten braucht schnellere Bibliotheken oder Stichproben |
| Große Joins | DuckDB Spatial | räumliche Joins und Aggregationen auf GeoParquet ohne Datenbankserver |
| Optional | PostGIS | erst nötig, wenn mehrere Personen parallel editieren |
| Konfiguration | YAML + pydantic | Regelwerk wird beim Laden gegen ein Schema geprüft |
| Tests | pytest, hypothesis (optional) | Regeln und Geometrie testbar |
| Kacheln | tippecanoe → PMTiles | eine Datei, statisch hostbar |

### 3.2 Die neun Stufen

**1. Datenbeschaffung und -bereinigung (`pipeline/s01_fetch.py`).** Ein Downloader pro Quelle, gesteuert über `config/sources.yaml` (URL, Typ, Lizenz, erwartete Felder). WFS-Abrufe mit Paging (`count`/`startIndex`) und Ablage als GeoParquet mit Abrufdatum und Hash. Bereinigung: Geometrien reparieren (`make_valid`), Duplikate entfernen, Felder vereinheitlichen. Jede Quelle erhält einen Eintrag in `data/manifest.json`.

**2. Topologisches Netz und Segmentierung (`s02_network.py`).** Basis ist der OSM-Fahrzeuggraph (highway-Klassen bis `living_street`, ohne `service`), vereinfacht auf Kanten zwischen Knoten mit Grad ≠ 2. Ein **Abschnitt** ist eine Kante zwischen zwei Knoten; Abschnitte über 400 m werden geteilt, wenn sich Tempo oder Querschnitt ändert (Annahme). Jeder Abschnitt erhält eine stabile ID aus dem Hash der OSM-Way-IDs und der Knotenkoordinaten, damit Korrekturen Updates überleben.

**3. Conflation amtlich ↔ OSM (`s03_conflate.py`).** Linienabgleich je amtlichem Objekt: Kandidaten im 15-m-Puffer, Filter nach Richtungswinkel (< 20°) und Überdeckungsanteil (> 60 %), Zuordnung nach Hausdorff-Abstand (Schwellen = Annahmen, per Stichprobe kalibrieren). Ergebnis je Abschnitt: `match_quality` (exakt, teilweise, keiner). Flächenhafte Quellen (Tempo-30-Zonen, ALKIS) werden über den Anteil der Abschnittslänge innerhalb der Fläche zugeordnet.

**4. Merkmale je Abschnitt (`s04_features.py`).**

- *Verbindungsfunktion:* Edge-Betweenness (zeitgewichtet, ggf. auf 2.000 Stichprobenknoten), Lage im HVS-Netz, Anzahl Busfahrten pro Werktag aus GTFS (Shapes auf Abschnitte gematcht), DTV wo vorhanden, Erreichbarkeit von Zentren (Entfernung zu zentralen Standorten, z. B. Bezirkszentren).
- *Erschließung und Aufenthalt:* Gebäudedichte und Erdgeschossnutzung (ALKIS-Gebäudefunktion, OSM `shop`/`amenity`), Einwohner im 100-m-Gitter, sensible Einrichtungen im Umkreis (Schulen, Kitas, Senioreneinrichtungen, Krankenhäuser), Radnetz-Zugehörigkeit.
- *Ist-Tempo:* amtliche Daten zuerst, OSM `maxspeed` als Rückfall; Konflikt beider Quellen wird als Unsicherheit gespeichert.
- *Ist-Gestaltung:* Radführung (`cycleway*`), Mittelmarkierung (`lane_markings`, Fahrstreifen), Parken (`parking:*`), Belag (WFS Deckschicht, OSM `surface`), Querungen (`crossing`), Ampeln, Plateaus (`traffic_calming`).

**5. Regelbasierte Soll-Kategorie (`s05_classify.py`).** Eine Entscheidungskaskade liest `rules.yaml` (Anhang A): erst Ausschlüsse (SW, Außerorts), dann Verbindungs-Score gegen Schwellen, dann die beiden GOW30-Auslöser nach CROW (Umfeld spricht für 30; 50 ist nicht sicher gestaltbar), dann ETW30/ETW-ERF. Jede Regel liefert `(rule_id, passed, inputs)`. Ergebnis: `cat_proposed`, `cat_confidence` (hoch/mittel/niedrig je nach Datenlage und Abstand zur Schwelle), `rule_trace`.

**6. Netzkohärenz (`s06_coherence.py`).** Die Regeln N1–N6 laufen auf dem Graphen der vorgeschlagenen Kategorien. Verstöße werden nicht automatisch „repariert“, sondern als `flags` gespeichert; eine optionale Glättung (z. B. kurze ETW-Lücke zwischen zwei GOW50) erscheint als Vorschlag mit eigener Regel-ID.

**7. Korrekturebene (`overrides/overrides.csv`).** Spalten: `segment_id, cat_final, reason, author, date, source, review_status`. Die Pipeline übernimmt nur Einträge mit `review_status = approved` und speichert `cat_proposed` und `cat_final` nebeneinander. Fällt eine `segment_id` nach einem Datenupdate weg, meldet ein Test die verwaiste Korrektur. Änderungen laufen per Pull Request mit Vier-Augen-Prinzip.

**8. Diskrepanz und Priorisierung (`s08_discrepancy.py`).** Diskrepanztyp D1–D3 und Stärke 0–3 je Dimension (Tempo, Gestaltung, Nutzung). Priorität = Diskrepanzstärke × Risiko, Risiko aus Unfällen mit Fuß- und Radbeteiligung (Unfallatlas, gewichtet nach Schwere, 3–5 Jahre), Exposition ungeschützter Verkehrsteilnehmender (Radnetz, Einwohner, Ziele) und Schulumfeld. Gewichte sind Annahmen und Teil der Sensitivitätsanalyse.

**9. Export (`s09_export.py`).** GeoParquet und GeoJSON für den Download, PMTiles für die Karte (Zoomstufen 10–16), eine schlanke JSON-Datei je Abschnitt für den Steckbrief, eine Suchindexdatei mit Straßennamen und Bezirken, `CHANGELOG` der Regelversion.

### 3.3 Erklärbarkeit

Jeder Abschnitt trägt einen maschinenlesbaren Entscheidungspfad, z. B.:

```json
{"segment_id": "seg_8f3a…", "cat_proposed": "GOW30", "cat_final": "GOW30",
 "rules_version": "0.3.0",
 "rule_trace": [
  {"id": "C-GOW-01", "passed": true,  "inputs": {"conn_score": 0.71, "in_hvs": true}},
  {"id": "C-G30-02", "passed": true,  "inputs": {"separated_cycle_track_feasible": false, "width_median_m": 16.4}},
  {"id": "C-G30-01", "passed": true,  "inputs": {"schools_150m": 1, "shop_frontage_share": 0.48}}],
 "flags": ["N4_shortcut_risk_low"], "confidence": "mittel",
 "sources": ["osm_2026-10-20", "hh_tempo_2026-10-27", "alkis_2026-10"]}
```

### 3.4 Tests und Plausibilitätsprüfungen

- **Schema-Tests:** `rules.yaml` validiert; jede Regel hat Quelle und Herkunftstyp; keine Schwelle ohne Einheit.
- **Regel-Tests:** kleine synthetische Abschnitte mit erwarteter Kategorie je Regelpfad („goldene Fälle“), z. B. HVS mit Radweg und 20 m Breite → GOW50.
- **Geometrie-Tests:** alle Geometrien gültig, alle in EPSG:25832, Abschnittslängen > 0, keine doppelten IDs.
- **Netz-Tests:** GOW-Netz zusammenhängend (bis auf markierte Ausnahmen); Anteil der Abschnitte ohne Ist-Tempo < 5 % (Annahme).
- **Plausibilität gegen Referenz:** Anteil der HVS-Kilometer, die als GOW50 oder GOW30 eingestuft werden, als Kennzahl im Report; starker Rückgang zwischen zwei Läufen bricht den Build ab.
- **Stichproben-Report:** Jeder Lauf zieht 30 zufällige Abschnitte je Kategorie mit Links auf Orthophoto und Panoramax-Bilder für die manuelle Durchsicht (Teil 7).

Die Stufen und Datenflüsse sind in der Architekturübersicht oben zusammengefasst.

## Teil 4 – Straßenquerschnitt: Bewertung und Berechnung

Der Querschnitt lohnt sich: Er entscheidet über die wichtigste SWOV/CROW-Regel – passt bei 50 ein getrennter Radweg in den Raum, sonst GOW30 – und macht Machbarkeit und Glaubwürdigkeit sichtbar \[B\]. Ein belastbarer Einstieg ist die Straßenraumbreite aus ALKIS und Gebäuden in wenigen Tagen; die Aufteilung in Fahrbahn, Radweg und Gehweg bleibt zunächst grob.

### 4.1 Wofür der Querschnitt aufschlussreich ist

| Frage | Benötigte Größe | Aussagekraft \[B\] |
| --- | --- | --- |
| Machbarkeit der Soll-Kategorie | Straßenraumbreite (Grenze zu Grenze) | hoch: steuert direkt die GOW30-Regel „50 nicht sicher gestaltbar“ (CROW-Auslöser b) \[F\] |
| Glaubwürdigkeit des Tempos (VSGS) | Fahrbahnbreite, Geradenlänge, Abstand der Bebauung, Belag | mittel: CROW nennt Fahrbahnbreite als nachweislich wirksam \[F\]; Fahrbahnbreite ist ohne Stufe b nur geschätzt |
| Aufenthaltsfunktion | Seitenraumbreite, Bäume | mittel: Bäume sind gut belegt, Gehwegbreiten nicht |
| RASt-Entwurfssituation | Breite, Nutzungen, DTV | mittel: Entwurfssituation ist eine Näherung |
| Umverteilungsbedarf | heutige Flächen für Kfz-Fahren und -Parken | hoch, aber erst mit Stufe b belastbar |

### 4.2 Erforderliche Straßenraumbreiten je Soll-Kategorie

Die Mindestbreiten sind aus belegten Einzelmaßen zusammengesetzt; die Summen sind eigene Rechnung \[B\]. Einzelmaße: Gehweg 2,50 m (RASt 06, am Original prüfen), Radweg 2,00 m und Sicherheitstrennstreifen 0,50–0,75 m (ERA 2010), GOW30-Fahrbahnprofile und Busbreiten (CROW 2023) \[F\].

| Soll-Profil | Zusammensetzung | Erforderliche Breite |
| --- | --- | --- |
| GOW50, 2 Fahrstreifen, ohne Parken | 2 × 2,50 Gehweg + 2 × 2,00 Radweg + 2 × 0,50 Trennstreifen + 6,50 Fahrbahn | ≈ 16,50 m |
| GOW50 mit Bus (CROW 7,00 m) | wie oben, Fahrbahn 7,00 | ≈ 17,00 m |
| GOW50 mit Baumstreifen/Lieferzone beidseitig | + 2 × 2,00 und Trennstreifen 0,75 statt 0,50 | ≈ 21,50 m |
| GOW30 schmal (bis 6.000 Kfz/Tag) | 2 × 2,50 Gehweg + 5,80–8,40 Fahrbahn inkl. Radstreifen | 10,80–13,40 m |
| GOW30 breit (bis 10.000 Kfz/Tag) | 2 × 2,50 Gehweg + 8,40–10,70 Fahrbahn | 13,40–15,70 m |
| ETW30 Mischverkehr | 2 × 2,50 Gehweg + 5,80 Fahrbahn (+ 2,00 Parken einseitig) | 10,80 (12,80) m |

Alle Werte gehören als Annahmen mit Quellenbezug in `rules.yaml` und werden von einer Verkehrsplaner\*in vor dem ersten Lauf geprüft. Die Fahrbahnbreite 6,50 m für zwei Fahrstreifen mit Begegnungsverkehr Lkw/Bus ist aus der Erinnerung an RASt 06 übernommen und am Original zu verifizieren \[Annahme\].

### 4.3 Methoden in steigender Genauigkeit

**a) Straßenraumbreite aus Transekten (Einstieg, 3–5 Tage).**

1. Mittellinie je Abschnitt glätten (Vereinfachung 2 m), alle 20 m eine Senkrechte von ± 40 m erzeugen; Tangente über ± 10 m gemittelt, damit Kurven keine schrägen Schnitte erzeugen.
2. Variante „Verkehrsfläche“: Schnitt mit ALKIS-Flächen der tatsächlichen Nutzung Straßenverkehr, Weg und Platz; Breite = Abstand der ersten Grenzen links und rechts. Variante „Fassade zu Fassade“: Schnitt mit Gebäudegrundrissen (ALKIS oder LoD2); liefert den wahrgenommenen Raum inklusive Vorgärten.
3. Sonderfälle: Transekte innerhalb 20 m um Knoten verwerfen; findet ein Transekt auf einer Seite keine Grenze innerhalb 40 m, Flag „offen/Platz“; Brücken und Tunnel über OSM `bridge`/`tunnel` ausschließen.
4. Aggregation je Abschnitt: Median, 10-%-Quantil, Minimum und Engstellen (mindestens drei aufeinanderfolgende Transekte unter dem 10-%-Quantil des Abschnitts).
5. Fehlerquellen: Straßenflurstücke enthalten Böschungen und Grün; Vorgärten fehlen in der Variante „Verkehrsfläche“; Versatz der OSM-Mittellinie; Arkaden und Durchfahrten.
6. Validierung: 50 zufällige Transekte im DOP20 manuell messen; Ziel: mittlere absolute Abweichung unter 1 m (Annahme).

**b) Aufteilung des Querschnitts (Ausbaustufe, je Quelle 1–4 Wochen).**

- *Amtliche Flächen:* Ob HH-SIB oder andere Hamburger Daten Fahrbahn-, Rad- und Gehwegflächen getrennt führen, ist zu klären (Transparenzanfrage an LSBG und Bezirke) \[Wissenslücke\].
- *OSM:* `cycleway*`, `sidewalk*`, `parking:*`, `lanes`, `width`; Fahrbahnbreite ersatzweise als Fahrstreifenzahl × Annahme. Abdeckung stadtteilweise sehr unterschiedlich; Vollständigkeit je Bezirk ausweisen.
- *Orthophotos und Laserscan:* Bordsteinkanten aus Höhensprüngen im Laserscan, Markierungen und parkende Autos aus DOP20 per Bildsegmentierung; Aufwand für Training und Prüfung hoch, Ergebnisse pro Stadtteil validieren.
- *Straßenbilder:* Panoramax (offen) und Mapillary für Stichproben und Objekterkennung (Radstreifen, Parken); Lizenzen beachten.

**c) Abgleich und Machbarkeitsindikator.** Je Abschnitt: `width_ratio = width_p10 / required_width(Soll)`. Klassen: ≥ 1,0 „passt“, 0,85–1,0 „eng – Umverteilung nötig“, < 0,85 „passt nicht“ (Grenzen = Annahmen). Passt GOW50 nicht, prüft die Regel `C-G30-02` automatisch GOW30 (CROW-Auslöser b) \[F für die Logik, B für die Schwellen\]. Mit Stufe b kommt der Konfliktindikator hinzu: Fläche, die heute für Kfz-Fahren und -Parken genutzt wird, gegen Fläche, die das Soll-Profil verlangt.

### 4.4 Pragmatischer Einstieg und Ausbaupfad

1. **Woche 1:** Methode a (beide Varianten), Breitenklassen auf der Karte, Machbarkeit nur für GOW50 vs. GOW30.
2. **Woche 2:** Validierung im DOP20, Fehlerkarte, Korrekturen für systematische Fälle (Plätze, Brücken).
3. **Ausbau 1:** OSM-Aufteilung mit Vollständigkeitsangabe; VSGS-Kurzindikator aus Fahrbahnbreite und Geradenlänge.
4. **Ausbau 2:** Bordsteinerkennung aus Laserscan im Pilotbezirk, Vergleich mit Stichproben vor Ort.
5. **Ausbau 3:** Orthophoto-Segmentierung oder amtliche Bestandsflächen, wenn verfügbar.

## Teil 5 – Webseite

Die Webseite ist eine statische Single-Page-Anwendung mit MapLibre GL JS und einer PMTiles-Datei, gebaut aus demselben Repository und bei jedem Release automatisch neu veröffentlicht \[B\]. Sie braucht keinen eigenen Server; Voraussetzung ist ein Hosting, das HTTP-Range-Anfragen unterstützt (vor dem Start mit der PMTiles-Datei testen).

### 5.1 Aufbau

| Baustein | Umsetzung \[B\] |
| --- | --- |
| Hosting | GitHub Pages oder Codeberg Pages für die Seite; PMTiles bei Bedarf auf einem Objektspeicher mit Range-Support und CORS |
| Karte | MapLibre GL JS, `pmtiles`-Protokoll, Hintergrund aus offenen Vektorkacheln (z. B. Protomaps-Basemap, eigene PMTiles); kein Tracking |
| Daten | `segments.pmtiles` (Zoom 10–16), `segments/{id}.json` für Steckbriefe, `search.json` für Straßennamen, `downloads/` mit GeoParquet, GeoJSON, CSV |
| Build | GitHub Action: Pipeline-Artefakte prüfen → Kacheln bauen → Seite deployen; Versionsnummer = Regelversion + Datenstand |
| Framework | bewusst schlank: Vite + Vanilla JS oder Svelte; keine Laufzeit-Abhängigkeit von Drittservern |

### 5.2 Ebenen

Umschaltbar, je mit Legende und Kurzerklärung: Soll-Kategorie (5 Farben, farbsehschwächen-tauglich, zusätzlich Linienstil), Ist-Tempo, Diskrepanz (Typ und Stärke), Straßenraumbreite (Klassen), Machbarkeit, Hauptverkehrsstraßennetz der BVM als Vergleich, Overlays Bus (Fahrten/Werktag), Radnetz, Schulen und Kitas, Unfälle (aggregiert je Abschnitt, keine Einzelpunkte mit Personendaten).

### 5.3 Steckbrief je Abschnitt

Beim Anklicken öffnet ein Seitenpanel (mobil: Bottom Sheet) mit:

- Straßenname, Bezirk, Abschnitts-ID, Länge
- **Soll-Kategorie** mit Klartext („Stadtstraße 30 – verbindet Quartiere, Radverkehr auf Radstreifen“) und ggf. Hinweis „fachlich korrigiert: Begründung …“
- **Begründung:** gegriffene Regeln in verständlicher Sprache mit Werten, z. B. „Kein getrennter Radweg möglich: Straßenraum 14,2 m, nötig 16,5 m (Regel C-G30-02)“
- Ist-Zustand: Tempo, Radführung, Busfahrten, DTV (falls vorhanden)
- Querschnitt: Median/Engstelle, Machbarkeitsklasse, kleine Skizze der Soll-Aufteilung
- Diskrepanz und Priorität
- **Datenunsicherheit:** Ampel (hoch/mittel/niedrig) mit Grund, z. B. „Ist-Tempo nur aus OSM“
- Datenquellen mit Stand und Lizenz
- Knopf „Rückmeldung zu diesem Abschnitt“

### 5.4 Filter, Suche, Rückmeldung

- Filter nach Bezirk, Soll-Kategorie, Diskrepanztyp, Priorität; URL spiegelt Filter und Kartenausschnitt (teilbare Links).
- Suchfeld mit Autovervollständigung aus `search.json` (fuse.js o. ä.), springt auf den Straßenzug.
- Rückmeldung ohne eigenen Server: vorausgefülltes GitHub-Issue-Formular mit Abschnitts-ID und Kategorie; Alternative ohne Konto: `mailto:` mit vorausgefülltem Betreff oder ein datensparsames Formular eines Dienstleisters mit Auftragsverarbeitungsvertrag \[B\]. Rückmeldungen fließen nie automatisch in `overrides.csv`, sondern nur nach fachlicher Prüfung.

### 5.5 Methodenseite, Download, Lizenzen

- Methodenseite in einfacher Sprache: Ziel, fünf Kategorien mit Fotos aus Panoramax, Entscheidungsbaum, Grenzen, Änderungshistorie.
- Download aller Daten mit Datenbeschreibung, Regelwerk als YAML, Korrekturdatei als CSV.
- Lizenz- und Quellenseite: ODbL für den Abschnittsdatensatz, dl-de/by-2.0-Quellenvermerke für alle amtlichen Quellen, CC BY 4.0 für Texte (Vorschlag).

### 5.6 Barrierefreiheit, Mobilgeräte, Kennzeichnung

- Ziel WCAG 2.2 AA: Kontraste, Tastaturbedienung der Karte und Panels, sichtbarer Fokus, Alternativtexte; Karteninhalte zusätzlich als sortierbare Tabelle je Bezirk.
- Mobil zuerst: Bottom Sheet, große Touch-Ziele, PMTiles-Datei je Bezirk optional für geringe Datenmengen.
- Dauerhaftes Band oben: „Nicht amtlicher Diskussionsentwurf zivilgesellschaftlicher Akteure – keine Anordnung, keine Planung der Stadt Hamburg“, plus Datum des Datenstands. Keine Hamburg-Wappen oder Behördenlogos.

## Teil 6 – Umsetzung mit Claude Code

Claude Code arbeitet am besten in kleinen, prüfbaren Schritten: eine Phase je Sitzung, erst Plan, dann Tests, dann Code, dann Stichprobe und Commit \[B\]. Die kopierbaren Prompts stehen gesammelt in Anhang C; hier stehen Struktur, Arbeitsweise und Stolpersteine.

### 6.1 Repository-Struktur

```text
hh-strassenfunktionsplan/
├── CLAUDE.md                 # Projektgedächtnis für Claude Code
├── README.md
├── pyproject.toml / uv.lock
├── Makefile                  # make fetch | network | classify | export | web | test
├── config/
│   ├── rules.yaml            # Regelwerk (Anhang A), versioniert
│   ├── sources.yaml          # Datenquellen (Anhang B)
│   └── schema/               # pydantic-Modelle für rules/sources
├── overrides/
│   └── overrides.csv         # fachliche Korrekturen mit Begründung
├── pipeline/
│   ├── s01_fetch.py … s09_export.py
│   └── lib/                  # geo, network, rules, io
├── tests/
│   ├── golden/               # synthetische Abschnitte mit Soll-Ergebnis
│   └── test_*.py
├── data/                     # nicht im Git (nur manifest.json)
│   ├── raw/ interim/ out/
├── reports/                  # Stichproben, Sensitivität, Vergleich HVS
├── web/                      # statische Seite (Vite)
├── docs/                     # Methodenseite, Entscheidungsprotokolle
└── .claude/commands/         # wiederverwendbare Prompts (optional)
```

### 6.2 CLAUDE.md (Vorlage)

```markdown
# Hamburger Straßenfunktionsplan – Entwurf (nicht amtlich)

## Ziel
Jedem Straßenabschnitt in Hamburg eine Soll-Kategorie (SW, GOW50, GOW30, ETW30, ETW-ERF)
nach Duurzaam Veilig zuordnen, Diskrepanzen zum Ist zeigen, alles erklärbar und reproduzierbar.
Automatik schlägt vor, Menschen entscheiden (overrides/overrides.csv).

## Fachliche Quelle der Wahrheit
- config/rules.yaml ist das einzige Regelwerk. Keine Schwellenwerte im Code.
- Jede neue Regel braucht: id, source, source_type (swov_crow|de_regelwerk|hamburg|assumption), status.
- Erfinde keine Schwellenwerte, Endpunkte oder Datensätze. Unbekanntes als TODO markieren und fragen.

## Konventionen
- Python 3.12, uv, geopandas/shapely 2, DuckDB Spatial; Code und Namen auf Englisch, Doku auf Deutsch.
- Rechnen immer in EPSG:25832; nur s09_export transformiert nach EPSG:4326.
- Zwischenergebnisse als GeoParquet in data/interim, mit Quelle und Abrufdatum in data/manifest.json.
- segment_id ist stabil (Hash aus OSM-Way-IDs und Knotenkoordinaten). Nie neu nummerieren.
- Jede Klassifikation schreibt rule_trace (Regel-ID, Ergebnis, Eingangswerte).

## Qualitätsregeln
- Erst Tests (tests/golden), dann Code. make test muss grün sein vor jedem Commit.
- Keine Daten in Git außer kleinen Testfixtures und manifest.json.
- Nach jeder Stufe: kurzer Report in reports/ mit Kennzahlen und 30 Zufallsstichproben.
- Lizenzen: dl-de/by-2.0-Quellenvermerke und ODbL beachten (docs/licenses.md).
- Bei Unklarheit fachlicher Art: anhalten und die Frage in docs/open_questions.md eintragen.

## Befehle
make fetch | make network | make features | make classify | make export | make web | make test
```

### 6.3 Arbeitsweise

- **Planungsmodus** zu Beginn jeder Phase: Claude liest Regelwerk, Daten und vorhandenen Code und legt einen Plan vor, bevor es Dateien ändert. Der Plan wird gegen Teil 1–4 dieser Anleitung geprüft und erst dann freigegeben.
- **Tests zuerst** für Regeln und Netzlogik: goldene Fälle beschreiben fachliche Erwartungen in Daten; Claude implementiert, bis sie grün sind.
- **Zwischen-Commits** nach jedem grünen Testlauf, mit sprechender Nachricht und Regelversion; größere Schritte als Pull Request mit Review durch die Verkehrsplaner\*in.
- **Stichproben statt Vertrauen:** Nach Stufen 3, 5, 6 und 8 je 30 Zufallsabschnitte pro Kategorie im Orthophoto und in Straßenbildern ansehen; Fehlerrate und Fehlertypen in `reports/` festhalten. Fehler führen zu einer Regeländerung oder einer Korrektur mit Begründung – nie zu stillem Nachjustieren.
- **Kontext klein halten:** eine Phase pro Sitzung; große Dateien nicht in den Chat laden, sondern Claude Kennzahlen und Schemas berechnen lassen.

### 6.4 Phasenplan

| Phase | Ziel | Prompt (Anhang C) | Prüfschritt |
| --- | --- | --- | --- |
| 0 Setup | Repository, CLAUDE.md, Tooling | P0 | `make test` läuft leer grün |
| 1 Regelwerk | `rules.yaml` + Schema + goldene Fälle | P1 | Verkehrsplaner\*in prüft jede Regel und Quelle |
| 2 Daten | Downloader, Manifest, Datenbericht | P2 | Vollständigkeit, Lizenzen, CRS im Report |
| 3a Netz | Segmentierung, stabile IDs | P3 | Längensumme vs. OSM, keine Duplikate |
| 3b Conflation | Amtlich ↔ OSM | P4 | 50 Stichproben, Trefferquote |
| 3c Merkmale | Verbindung, Aufenthalt, Ist | P5 | Verteilungen plausibel, Nullwerte < Schwelle |
| 3d Klassifikation | Kaskade + rule\_trace | P6 | goldene Fälle grün, HVS-Abgleich |
| 3e Kohärenz + Korrektur | Flags, overrides | P7 | Flag-Liste fachlich durchsehen |
| 3f Diskrepanz | Typen, Priorität | P8 | Top-30-Liste vor Ort plausibel |
| 4 Querschnitt | Transekte, Machbarkeit | P9 | 50 Transekte im DOP20 gemessen |
| 5 Web | Karte, Steckbrief, Download | P10 | Barrierefreiheits- und Mobiltest |
| 7 Validierung | Sensitivität, Vergleich | P11 | Bericht mit Kennzahlen |

### 6.5 Typische Stolpersteine

| Problem | Lösung \[B\] |
| --- | --- |
| WFS liefert nur Teilmengen | Paging mit `count`/`startIndex`; Anzahl über `resultType=hits` prüfen; OGC API Features mit `limit` und `next`-Links |
| GML-Eigenheiten, Achsenreihenfolge | `pyogrio` nutzen, CRS explizit setzen, nach dem Lesen Bounding Box gegen Hamburg prüfen |
| Gemischte Koordinatensysteme | eine Funktion `to_work_crs()` am Eingang jeder Stufe; Test, der alle Zwischenergebnisse auf EPSG:25832 prüft |
| Große Datenmengen (Gebäude, Laserscan) | auf Pilotbezirk zuschneiden; DuckDB für Joins; Laserscan nur kachelweise |
| Netzwerkzugriff in Sandboxen | Downloads lokal ausführen oder freigeschaltete Domains konfigurieren; Rohdaten mit Hash versionieren, damit Läufe offline reproduzierbar sind |
| OSM-Änderungen brechen IDs | Auszug mit Datum einfrieren; stabile IDs; Test auf verwaiste Overrides |
| Betweenness zu langsam | igraph/networkit, Stichprobenknoten, Ergebnis cachen |
| Lizenzmischung OSM + amtlich | Datensatz unter ODbL, Quellenvermerke in Metadaten und Webseite; vor Veröffentlichung juristisch prüfen lassen |
| Halluzinierte Endpunkte oder Schwellen | CLAUDE.md-Regel „nichts erfinden“; `sources.yaml` nur mit geprüften URLs; Schema erzwingt Quelle je Regel |
| Stilles Überanpassen an Stichproben | jede Regeländerung mit Begründung und neuer Version; Sensitivitätsreport vor und nach der Änderung |

## Teil 7 – Validierung und Grenzen

Der Entwurf gilt erst als veröffentlichungsreif, wenn vier Prüfungen dokumentiert sind: Abgleich mit dem HVS-Netz, Stichproben vor Ort, Sensitivitätsanalyse und eine Rückmelderunde mit Ortskundigen \[B\]. Auch dann bleibt er ein Diskussionsentwurf.

### 7.1 Prüfschritte

| Prüfung | Vorgehen | Erwartung / Abbruchkriterium \[B\] |
| --- | --- | --- |
| Abgleich HVS-Netz | Kreuztabelle Soll-Kategorie × HVS ja/nein, in km und je Bezirk | Fast alle HVS-km sollten GOW50 oder GOW30 sein; HVS als ETW30 und Bezirksstraßen als GOW50 einzeln begründen |
| Abgleich mit Ist-Tempo | Anteil Soll-ETW30 mit heutigem Tempo 30 | hoher Anteil erwartet; Ausreißer sind Kandidaten für Datenfehler |
| Stichproben vor Ort | 30 Abschnitte je Kategorie im Pilotbezirk, Begehung mit Prüfbogen (Funktion, Nutzung, Querschnitt, Gestaltung) | Fehlerrate je Kategorie; Ziel: unter 15 % fachlich strittig (Annahme) |
| Sensitivitätsanalyse | jede Schwelle ± 20 %, Gewichte der Priorisierung variiert; Monte-Carlo über alle Annahmen | Anteil der Abschnitte, die die Kategorie wechseln; Abschnitte, die oft wechseln, werden als „unsicher“ markiert |
| Datenqualität | Vollständigkeit OSM-Tags je Bezirk, Conflation-Trefferquote, fehlende DTV | in Karte als Unsicherheit sichtbar |
| Ortskundige | moderierte Durchsicht mit Bezirksgruppen der Verbände, Feuerwehr, Busbetrieben (Bericht 2: Deventer-Verfahren) | jede Rückmeldung erhält Antwort und Status; Übernahme nur mit Begründung |
| Externe Fachprüfung | Review durch Hochschule oder Planungsbüro | schriftliche Stellungnahme vor Veröffentlichung |

### 7.2 Fachliche Grenzen

- Die niederländischen Kategorien passen nicht eins zu eins auf deutsche Regelwerke; die RIN/RASt-Zuordnung ist eine Näherung \[B\].
- Die GOW30-Merkmale der CROW sind ausdrücklich vorläufig; Wirkungen werden erst evaluiert ([CROW 2023](https://www.amersfoort.nl/sites/default/files/2025-09/2023-crow-handreiking-voorlopige-inrichtingskenmerken-gow30.pdf)) \[F\].
- SWOV zeigt, dass Richtlinien oft nicht umgesetzt werden, etwa sind 60 % der Radstreifen an 50er-Straßen schmaler als empfohlen (Factsheet 2023) \[F\]. Ein Soll-Plan sagt also wenig über die Umsetzung.
- Multifunktionale Hamburger Hauptstraßen (Bus, Handel, Wohnen, Durchgang) landen konsequent angewandt oft in GOW30; das ist fachlich folgerichtig, politisch aber der härteste Punkt (Bericht 2) \[B\].
- Busbetrieb, Rettungswege und Wirtschaftsverkehr sind nur als Overlays abgebildet; Fahrzeitwirkungen werden nicht modelliert \[B\].

### 7.3 Rechtliche Grenzen

- Der Plan ist kein Verwaltungsakt und keine Anordnung; Tempo auf Hauptverkehrsstraßen setzt weiterhin die Voraussetzungen der StVO voraus (Bericht 2) \[F\].
- Eine Soll-Kategorie GOW30 begründet in Deutschland derzeit kein flächiges Tempo 30 auf Hauptverkehrsstraßen; sie kann Begründungen für Einzelfälle und für ein Gesamtkonzept liefern (Bericht 2) \[B\].
- Lizenzen: Namensnennungspflichten (dl-de/by-2.0) und ODbL-Pflichten müssen erfüllt sein; Unfalldaten nur aggregiert darstellen \[B\].

### 7.4 Methodische Grenzen

- Kfz-Verkehrsstärken fehlen auf den meisten Bezirksstraßen; Proxys aus Netzzentralität bilden Verkehr nicht ab \[B\].
- OSM-Attribute sind ungleich vollständig; die Ist-Gestaltung ist in schwach kartierten Stadtteilen unsicherer \[B\].
- Unfallatlas erfasst nur polizeilich registrierte Unfälle mit Personenschaden \[F\]; Alleinunfälle von Radfahrenden sind untererfasst \[B\].
- Schwellenwerte mit Herkunft `assumption` sind Setzungen; die Sensitivitätsanalyse zeigt ihren Einfluss, ersetzt aber keine fachliche Abstimmung \[B\].

### 7.5 Was nur ein Diskussionsentwurf sein kann

Die Soll-Kategorien, Prioritäten und Machbarkeitsklassen sind Vorschläge zur Verhandlung. Belastbar sind die Datengrundlagen, die offengelegte Methode und die Diskrepanzen zwischen Ist-Zustand und einer ausdrücklich genannten Netzlogik. Die Webseite muss das auf jeder Ebene sagen \[B\].

## Anhang A – Regelwerk als YAML-Entwurf

Der Entwurf `config/rules.yaml` (Version 0.1.0) ist syntaktisch geprüft (PyYAML) und enthält 8 Klassifikationsregeln, 6 Kohärenzregeln, Anforderungen je Kategorie, Breiten, Diskrepanz und Priorisierung. Alle Werte mit `source_type: assumption` sind Setzungen und vor dem ersten Lauf von einer Verkehrsplaner\*in zu prüfen \[B\].

```yaml
# Hamburger Straßenfunktionsplan – Regelwerk (Entwurf, nicht amtlich)
# source_type: swov_crow | de_regelwerk | hamburg | assumption
# status: draft | reviewed | approved
meta:
  version: 0.1.0
  date: 2026-10-27
  crs_work: EPSG:25832
  owner: 'Allianz / Fachgruppe Methodik'
  note: 'Schwellen mit source_type=assumption sind Setzungen und vor dem ersten Lauf fachlich zu prüfen.'

sources:
  SWOV_FS_2023: {title: 'Principles for a safe road network, SWOV fact sheet', date: 2023-04, url: 'https://swov.nl/en/fact-sheet/principles-safe-road-network'}
  SWOV_DV3_2018: {title: 'DV3 – Achtergronden en uitwerking (R-2018-6B)', date: 2018, url: 'https://swov.nl/node/16907'}
  CROW_GOW30_2023: {title: 'Handreiking voorlopige inrichtingskenmerken GOW30, v1.0', date: 2023-05, url: 'https://www.amersfoort.nl/sites/default/files/2025-09/2023-crow-handreiking-voorlopige-inrichtingskenmerken-gow30.pdf'}
  CROW_AFW30_2021: {title: 'Afwegingskader 30 km/h', date: 2021, url: null}
  KNSPV_OPS_2021: {title: 'Operationalisatie voldoende veilige wegen en fietsinfrastructuur (RWS/Sweco)', date: 2021-07, url: 'https://www.ndw.nu/...Operationalisatie+Definitie+KN+SPV...pdf'}
  KNSPV_RI_2023: {title: 'Risico-indicatoren, Kennisnetwerk SPV', date: 2023-04, url: 'https://swov.nl/sites/default/files/bestanden/downloads/2023_SWOV_Risico-indicatoren-april2023_KennisnetwerkSPV.pdf'}
  ERA_2010: {title: 'Empfehlungen für Radverkehrsanlagen (FGSV)', date: 2010, url: null}
  RAST_06: {title: 'Richtlinien für die Anlage von Stadtstraßen (FGSV 200)', date: 2006, url: null}
  RIN_2008: {title: 'Richtlinien für integrierte Netzgestaltung (FGSV)', date: 2008, url: null}
  HH_HVS_2023: {title: 'Hauptverkehrsstraßen Hamburg, Karte Stand Sept. 2023 (BVM)', date: 2023-09, url: 'https://www.hamburg.de/politik-und-verwaltung/behoerden/bvm/hauptverkehrsstrassen-193350'}

categories:
  SW:      {label_de: 'Schnellverkehrsstraße', class_report2: null, speed_kmh: null, nl: 'stroomweg'}
  GOW50:   {label_de: 'Stadtmagistrale', class_report2: K1, speed_kmh: 50, nl: 'gebiedsontsluitingsweg 50'}
  GOW30:   {label_de: 'Stadtstraße 30', class_report2: K2, speed_kmh: 30, nl: 'gebiedsontsluitingsweg 30'}
  ETW30:   {label_de: 'Quartiersstraße', class_report2: K3, speed_kmh: 30, nl: 'erftoegangsweg 30'}
  ETW_ERF: {label_de: 'Aufenthaltsstraße', class_report2: K4, speed_kmh: 7, nl: 'erf', note: 'Schrittgeschwindigkeit; 7 nur als Rechenwert'}
  GOW80:   {label_de: 'Landstraße (Verbindung)', rural: true, speed_kmh: 80}
  ETW60:   {label_de: 'Landstraße (Erschließung)', rural: true, speed_kmh: 60}

# Klassifikationskaskade: Reihenfolge = Priorität. Erste zutreffende Endregel gewinnt.
classification:
  - id: C-SW-01
    if: 'highway in [motorway, motorway_link, trunk] and access_motor_only'
    then: SW
    source: SWOV_FS_2023
    source_type: swov_crow
    status: draft
    note: 'Stroomwegen nur anbaufrei; in Hamburg v. a. Autobahnen.'
  - id: C-RUR-01
    if: 'outside_builtup_area'
    then: 'GOW80 if conn_score >= thresholds.conn_gow else ETW60'
    source: SWOV_FS_2023
    source_type: swov_crow
    status: draft
  - id: C-ERF-01
    if: 'ist_verkehrsberuhigt or pedestrian_zone or override_school_street'
    then: ETW_ERF
    source: SWOV_FS_2023
    source_type: swov_crow
    status: draft
  - id: C-GOW-01
    description: 'Verbindungsfunktion hoch -> Gebiedsontsluitingsweg'
    if: 'conn_score >= thresholds.conn_gow or in_hvs'
    then: 'GOW (weiter mit C-G30-*)'
    thresholds:
      conn_gow: {value: 0.6, unit: 'score 0-1', source_type: assumption, check: 'Sensitivität ±20 %, Abgleich HVS'}
    source: [SWOV_FS_2023, HH_HVS_2023]
    source_type: swov_crow
    status: draft
  - id: C-G30-01
    description: 'GOW30-Auslöser a: Umfeld spricht für 30 (Schule, Leben, Querbarkeit)'
    applies_to: GOW
    if: 'schools_or_kitas_within_m <= thresholds.sensitive_radius or shop_frontage_share >= thresholds.frontage or crossing_demand == high'
    then: GOW30
    thresholds:
      sensitive_radius: {value: 150, unit: m, source_type: assumption}
      frontage:         {value: 0.4, unit: 'Anteil Erdgeschoss mit Publikumsnutzung', source_type: assumption}
    source: [CROW_AFW30_2021, CROW_GOW30_2023]
    source_type: swov_crow
    status: draft
  - id: C-G30-02
    description: 'GOW30-Auslöser b: 50 nicht sicher gestaltbar (kein getrennter Radweg möglich)'
    applies_to: GOW
    if: 'not separated_cycle_track_present and width_p10_m < required_width.GOW50'
    then: GOW30
    source: [SWOV_FS_2023, CROW_GOW30_2023]
    source_type: swov_crow
    status: draft
  - id: C-G50-01
    applies_to: GOW
    if: 'no C-G30-* passed'
    then: GOW50
    source: SWOV_FS_2023
    source_type: swov_crow
    status: draft
  - id: C-ETW-01
    if: 'default'
    then: ETW30
    source: SWOV_FS_2023
    source_type: swov_crow
    status: draft

# Verbindungs- und Aufenthaltsscore (gewichtete Summe normierter Merkmale)
scores:
  conn_score:
    weights:  # source_type: assumption (Sensitivitätsanalyse)
      betweenness_norm: 0.35
      in_hvs: 0.25
      bus_trips_weekday_norm: 0.20
      dtv_norm: 0.20
    missing_value_policy: 'Gewicht auf übrige Merkmale umlegen, confidence herabsetzen'
  place_score:
    weights:
      building_density_norm: 0.3
      population_100m_norm: 0.3
      frontage_share: 0.2
      sensitive_facilities_norm: 0.2

# Anforderungen je Kategorie (für Diskrepanz und Machbarkeit)
requirements:
  GOW50:
    cycling: {value: separated_mandatory_track_or_parallel_route, source: CROW_GOW30_2023, source_type: swov_crow}
    cycle_lanes_allowed: {value: false, source: CROW_GOW30_2023, source_type: swov_crow}
    cycle_track_width_m: {value: 2.00, source: ERA_2010, source_type: de_regelwerk}
    buffer_to_parking_m: {value: 0.75, min: 0.50, source: ERA_2010, source_type: de_regelwerk}
    median_if_lanes_per_dir_gte: {value: 2, source: CROW_GOW30_2023, source_type: swov_crow}
    parking_along_carriageway: {value: false, source: KNSPV_OPS_2021, source_type: swov_crow}
    angle_parking: {value: false, source: CROW_GOW30_2023, source_type: swov_crow}
    carriageway_bus_m: {value: 7.00, source: CROW_GOW30_2023, source_type: swov_crow}
    crossings: {value: 'concentrated; zebra on plateau or refuge, or signal', source: KNSPV_OPS_2021, source_type: swov_crow}
  GOW30:
    cycling: {value: cycle_lanes_or_existing_track, source: CROW_GOW30_2023, source_type: swov_crow}
    cycle_lane_width_m: {min: 1.70, ideal: 2.20, source: CROW_GOW30_2023, source_type: swov_crow}
    cycle_lane_width_de_m: {value: 1.85, note: 'inkl. Breitstrich; E Klima 2022 empfiehlt 2.25', source: ERA_2010, source_type: de_regelwerk}
    centre_line: {value: false, source: CROW_GOW30_2023, source_type: swov_crow}
    bicycle_street_allowed: {value: false, source: CROW_GOW30_2023, source_type: swov_crow}
    profiles:
      narrow: {carriageway_m: [5.80, 8.40], max_dtv: 6000, centre_runner_max_m: 3.80, avoid_runner_m: [3.80, 4.80], source: CROW_GOW30_2023, source_type: swov_crow}
      wide:   {carriageway_m: [8.40, 10.70], max_dtv: 10000, source: CROW_GOW30_2023, source_type: swov_crow}
      track:  {carriageway_min_m: 5.80, source: CROW_GOW30_2023, source_type: swov_crow}
    parking_on_carriageway: {value: false, source: CROW_GOW30_2023, source_type: swov_crow}
    priority_over_ETW: {value: true, source: CROW_GOW30_2023, source_type: swov_crow}
  ETW30:
    cycling: {value: mixed, source: SWOV_FS_2023, source_type: swov_crow}
    cycle_lanes_allowed: {value: false, exception: 'Hauptradroute -> Fahrradstraße', source: CROW_GOW30_2023, source_type: swov_crow}
    carriageway_mixed_ideal_m: {value: 5.80, source: CROW_GOW30_2023, source_type: swov_crow}
    carriageway_bus_m: {value: 6.50, source: CROW_GOW30_2023, source_type: swov_crow}
    speed_reducer_spacing_m: {value: 100, note: 'Option optimal', source: KNSPV_OPS_2021, source_type: swov_crow}
    junction_priority: {value: equal_right_before_left, source: SWOV_FS_2023, source_type: swov_crow}
  ETW_ERF:
    cycling: {value: mixed, source: SWOV_FS_2023, source_type: swov_crow}

# Erforderliche Straßenraumbreite (Grenze zu Grenze) – Summen aus Einzelmaßen
required_width:
  sidewalk_m: {value: 2.50, source: RAST_06, source_type: de_regelwerk, status: 'am Original prüfen'}
  carriageway_2lane_m: {value: 6.50, source: RAST_06, source_type: assumption, status: 'aus Erinnerung, am Original prüfen'}
  GOW50: {value: 16.50, formula: '2*sidewalk + 2*cycle_track + 2*0.50 + carriageway_2lane', source_type: assumption}
  GOW50_bus: {value: 17.00, source_type: assumption}
  GOW30_narrow: {range: [10.80, 13.40], source_type: assumption}
  GOW30_wide: {range: [13.40, 15.70], source_type: assumption}
  ETW30: {value: 10.80, source_type: assumption}

feasibility_classes:  # width_ratio = width_p10 / required_width
  fits: {min: 1.00, source_type: assumption}
  tight: {min: 0.85, max: 1.00, source_type: assumption}
  does_not_fit: {max: 0.85, source_type: assumption}

# Netzkohärenz
coherence:
  - {id: N1, rule: 'GOW-Züge enden an GOW, SW oder Stadtgrenze', source: SWOV_FS_2023, source_type: swov_crow}
  - {id: N2, rule: 'Kategoriewechsel < min_run_m zwischen gleichen Kategorien markieren', min_run_m: 200, source_type: assumption}
  - {id: N3, rule: 'Aufenthaltsbereiche (von GOW/SW umschlossen) < min_area_ha markieren', min_area_ha: 25, source: SWOV_FS_2023, source_type: assumption}
  - {id: N4, rule: 'Kürzester Weg zwischen GOW-Knoten nutzt > max_etw_m ETW -> Schleichverkehrsflag', max_etw_m: 300, source: SWOV_FS_2023, source_type: assumption}
  - {id: N5, rule: 'Übergang GOW50->GOW30 und GOW->ETW braucht Torsituation; kein direkter Übergang 70/80->30', source: CROW_GOW30_2023, source_type: swov_crow}
  - {id: N6, rule: 'Soll-Knotentyp aus Kategoriepaar ableiten (Kreisverkehr, Signal mit Plateau, Gehwegüberfahrt, gleichrangig)', source: [SWOV_FS_2023, CROW_GOW30_2023], source_type: swov_crow}

# Diskrepanz ('grijze wegen') und Priorisierung
discrepancy:
  speed:
    rule: 'ist_limit_kmh > categories[soll].speed_kmh'
    severity: {'+20': 2, '+30_or_more': 3}
    source: KNSPV_RI_2023
    source_type: swov_crow
  design:
    checks: [cycling, cycle_lanes_allowed, centre_line, parking_along_carriageway, median_if_lanes_per_dir_gte]
    severity: 'Anzahl verletzter Anforderungen, gekappt bei 3'
    source: [CROW_GOW30_2023, KNSPV_OPS_2021]
    source_type: swov_crow
  use:
    rule: 'dtv > requirements[soll].profiles.*.max_dtv'
    source: CROW_GOW30_2023
    source_type: swov_crow
  types:
    D1: 'Erschließungsfunktion, aber Durchfluss-Gestaltung'
    D2: 'Verbindungsfunktion, sparsame Gestaltung (z. B. Radverkehr auf Fahrbahn bei 50)'
    D3: 'Mischform mit Merkmalen beider Kategorien'

priority:
  formula: 'max(severity) * risk'
  risk_weights:  # source_type: assumption
    injury_crashes_ped_cyc_per_km_5y: 0.4
    severe_or_fatal_weight: 3
    cycle_network: 0.2
    population_100m: 0.2
    school_kita_within_150m: 0.2
```

**Prüfhinweise:** Die Schwellen `conn_gow`, `sensitive_radius`, `frontage`, N2–N4 und alle Gewichte sind Annahmen; sie werden über die Sensitivitätsanalyse (Teil 7) und den HVS-Abgleich kalibriert und erst danach auf `status: reviewed` gesetzt. Die Logik `C-G30-01`/`C-G30-02` folgt den beiden GOW30-Auslösern des CROW-Afwegingskaders \[F\].

## Anhang B – Datenliste

Prüfstatus am 27.10.2026: „geprüft“ = Endpunkt oder Metadaten in dieser Recherche geöffnet; „Katalog“ = Existenz über Katalog oder Behördenseite belegt, Endpunkt im Projekt zu prüfen; „offen“ = nicht belegt. Endpunkte stehen nur dort, wo sie in Quellen gesehen wurden.

| Datensatz | Anbieter | Zugriff / Endpunkt | Format | Lizenz | Aktualität | Zweck | Prüfstatus |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Hauptverkehrsstraßennetz (Karte, Listen je Bezirk) | BVM | [Webseite](https://www.hamburg.de/politik-und-verwaltung/behoerden/bvm/hauptverkehrsstrassen-193350), PDF | PDF | nicht angegeben | Stand Sept. 2023 | Vergleichsebene, Merkmal `in_hvs` | geprüft |
| Strategisches Straßennetz (HH-SIB) | BVM / LGV | WFS `https://geodienste.hamburg.de/HH_WFS_Strategisches_Strassennetz` | GML | dl-de/by-2.0 | Revision Metadaten 2019 | amtliches Netz, Klassifizierung, Conflation | geprüft (Metadaten) |
| Widmungen nach HWG | LGV | WFS `https://geodienste.hamburg.de/HH_WFS_Widmungen` | GML | dl-de/by-2.0 (prüfen) | laufend | Straßenstatus, Fußgängerzonen | Katalog |
| Zulässige Höchstgeschwindigkeiten | Hamburg | OGC API `https://api.hamburg.de/datasets/v1/zulaessige_hoechstgeschwindigkeiten` | GeoJSON | im Projekt prüfen | Abruf 27.10.2026 (19.469 Tempo-30-Zonen-Objekte) | Ist-Tempo | geprüft |
| Verkehrsmengen (DTV) | BVM | OGC API `https://api.hamburg.de/datasets/v1/verkehrsmengen` | GeoJSON | im Projekt prüfen | geprüft: Collection DTV BAB 2019; weitere Jahrgänge offen | Nutzung, conn\_score | geprüft (Teil) |
| Verkehrszählstellen Kfz/Rad (Dauerzählstellen) | BVM / UDP | SensorThings `https://iot.hamburg.de/v1.1` (Inhalt prüfen) | JSON | im Projekt prüfen | laufend | Kalibrierung DTV | offen |
| Radverkehrsmengen DB Rad+ | Hamburg | OGC API `https://api.hamburg.de/datasets/v1/dbradplus` | GeoJSON | im Projekt prüfen | Jahr 2022 geprüft | Radverkehr-Exposition | geprüft |
| Radnetz Hamburg (Radrouten, Radrouten+) | BVM | Geoportal „Fachdaten/Verkehr/Radnetz Hamburg“; Dienst prüfen | WMS/WFS | prüfen | seit 2025 im Aufbau | Overlay Radnetz | Katalog |
| ALKIS Flurstücke, Gebäude, tatsächliche Nutzung | LGV | WFS „ALKIS – Liegenschaften und Verwaltungseinheiten“; NAS-Download Transparenzportal | GML, NAS | dl-de/by-2.0 | tagesaktuell (WMS) | Straßenraumbreite, Nutzungen | geprüft (Metadaten) |
| 3D-Gebäudemodell LoD2-DE, LoD3.0-HH | LGV | Transparenzportal | CityGML | dl-de/by-2.0 | LoD2 ab 2016, LoD3.0 Basis 2020 | Fassade-zu-Fassade, Bebauungsabstand | geprüft (Metadaten) |
| Digitale Orthophotos DOP20 | LGV | Transparenzportal, WMS | GeoTIFF/JPEG | dl-de/by-2.0 | jährliche Frühjahrsbefliegung | Validierung, Segmentierung | geprüft |
| Laserscandaten / DGM / DOM | LGV | Transparenzportal | LAS/XYZ | dl-de/by-2.0 (prüfen) | prüfen | Bordsteinerkennung | Katalog |
| Straßenbaumkataster | BUKEA | Transparenzportal, WFS | GML/CSV | dl-de/by-2.0 (prüfen) | laufend, \~227.000 Bäume (2023) | Aufenthalt, Hindernisse | geprüft (Behördenseite) |
| Zustand (ZEB), Deckschichttypen RLS-19 | BVM / LGV | WFS `HH_WFS_ZEB_Zustandsklassen`, `HH_WFS_Strassendecke` | GML | prüfen | seit 2014 | Belag, Erkennbarkeit | geprüft (Metadaten) |
| Schulen | BSB / LGV | Schulinfosystem; WFS im Projekt suchen | GML | prüfen | laufend | sensible Einrichtungen | Katalog |
| Kitas | Sozialbehörde / LGV | WFS im Projekt suchen | GML | prüfen | laufend | sensible Einrichtungen | offen |
| Bevölkerung 100-m-Gitter | Zensus 2022 | [Download](https://zensus2022.de/EN/Census_results/02-release-of-results.html?nn=470744) | CSV | prüfen (amtliche Statistik, frei) | Stichtag 15.05.2022 | Exposition, place\_score | geprüft |
| Lärmkartierung, Ruhige Gebiete | BUKEA | WFS `HH_WFS_Ruhige_Gebiete`; Lärmkarten-WFS suchen | GML | prüfen | 4. Stufe | Kontext, Begründung Tempo 30 | geprüft (Ruhige Gebiete) |
| HVV-Fahrplandaten | HVV | Transparenzportal, ZIP | GTFS | dl-de/by-2.0 | gültig 08.04.–12.12.2026, 872 Linien | Busnetz, Fahrten/Werktag | geprüft |
| Unfallatlas | Statistische Ämter | Opendata-Download unfallatlas.statistikportal.de | CSV/Shape | dl-de/by-2.0 | jährlich | Risiko, Priorisierung | geprüft (Lizenz), Abdeckung HH prüfen |
| OpenStreetMap | OSM-Beitragende | Geofabrik-Auszug Hamburg (PBF), Overpass für Stichproben | PBF | ODbL | täglich | Netz, maxspeed, lanes, width, cycleway, sidewalk, parking | allgemein bekannt |
| Straßenbilder | Panoramax, Mapillary | APIs | Bilder | Panoramax offen; Mapillary CC BY-SA | ungleich | Stichproben, Erkennung | Lizenz im Projekt prüfen |
| Hamburger Magistralen | BSW | Webseite | – | – | – | Overlay Stadtentwicklung | geprüft |

## Anhang C – Claude-Code-Prompts

Zwölf Prompts, je eine Sitzung; jede beginnt im Planungsmodus und endet mit grünen Tests, Report und Commit. Platzhalter in spitzen Klammern ersetzen.

### P0 – Setup

**Ziel:** lauffähiges Repository. **Eingaben:** CLAUDE.md (Teil 6.2), diese Anleitung als `docs/guide.md`. **Ergebnis:** Struktur aus Teil 6.1, `uv`-Projekt, `Makefile`, leere Tests. **Prüfschritt:** `make test` grün, `uv.lock` committet.

```text
Lies CLAUDE.md und docs/guide.md. Lege die Repository-Struktur aus guide.md Teil 6.1 an.
Richte ein uv-Projekt (Python 3.12) mit geopandas, shapely>=2, pyogrio, pyrosm, osmnx, networkx,
igraph, duckdb, pydantic, pyyaml, pytest ein. Schreibe ein Makefile mit den Zielen
fetch, network, features, classify, coherence, discrepancy, crosssection, export, web, test.
Noch keine Fachlogik. Zeige mir zuerst den Plan, dann umsetzen, dann make test ausführen.
```

### P1 – Regelwerk und Schema

**Ziel:** `config/rules.yaml` als geprüfte Datenquelle. **Eingaben:** Anhang A. **Ergebnis:** pydantic-Schema, Loader, goldene Fälle. **Prüfschritt:** Verkehrsplaner\*in liest jede Regel gegen ihre Quelle.

```text
Übernimm Anhang A aus docs/guide.md als config/rules.yaml. Schreibe in config/schema/ ein
pydantic-Modell, das jede Regel, jede Schwelle und jede Anforderung validiert: Pflichtfelder
source und source_type (swov_crow|de_regelwerk|hamburg|assumption), Einheit bei Zahlen.
Schreibe tests/test_rules_schema.py. Lege in tests/golden/ 12 synthetische Abschnitte
(GeoJSON, EPSG:25832) mit erwarteter Kategorie an – je Regelpfad mindestens einen Fall,
u. a. HVS mit Radweg und 20 m Breite -> GOW50; HVS ohne Radweg, 13 m -> GOW30;
Wohnstraße -> ETW30. Erfinde keine neuen Schwellen; fehlt etwas, trage es in
docs/open_questions.md ein.
```

### P2 – Datenbeschaffung

**Ziel:** reproduzierbarer Download aller Quellen aus Anhang B. **Eingaben:** Anhang B, Pilotbezirk. **Ergebnis:** `config/sources.yaml`, `s01_fetch.py`, `data/manifest.json`, `reports/data_report.md`. **Prüfschritt:** Report zeigt je Quelle Objektanzahl, CRS, Bounding Box, Lizenz, Abrufdatum.

```text
Erzeuge config/sources.yaml aus Anhang B in docs/guide.md. Übernimm nur Endpunkte, die dort
stehen; für Einträge mit Prüfstatus 'offen' oder 'Katalog' schreibe url: null und ein TODO.
Implementiere pipeline/s01_fetch.py: WFS mit Paging (count/startIndex, resultType=hits zur
Kontrolle), OGC API Features mit next-Links, Datei-Downloads mit Hash. Zuschnitt auf den
Bezirk <Pilotbezirk> (Bezirksgrenze aus ALKIS-Verwaltungseinheiten). Speichere GeoParquet in
data/raw/, alles in EPSG:25832. Schreibe data/manifest.json und reports/data_report.md.
Teste das Paging mit einem gemockten WFS. Brich ab und frage, wenn ein Endpunkt nicht antwortet.
```

### P3 – Netz und Segmentierung

**Ziel:** Abschnitte mit stabilen IDs. **Ergebnis:** `data/interim/segments.parquet`. **Prüfschritt:** Längensumme vs. OSM-Ausgangsnetz (Abweichung < 1 %), keine doppelten IDs, Karte der Abschnitte im Report.

```text
Implementiere pipeline/s02_network.py nach guide.md Teil 3.2 Stufe 2: OSM-Fahrzeuggraph aus
dem PBF-Auszug, highway-Klassen bis living_street ohne service, Vereinfachung auf Kanten
zwischen Knoten mit Grad != 2, Teilung langer Kanten bei Tempo- oder Querschnittswechsel.
segment_id = stabiler Hash aus sortierten OSM-Way-IDs und gerundeten Knotenkoordinaten.
Tests: Gültigkeit, CRS, Eindeutigkeit, Stabilität der IDs bei zweimaligem Lauf.
Report: Anzahl, Längenverteilung, 30 Zufallsabschnitte mit Link auf openstreetmap.org.
```

### P4 – Conflation

**Ziel:** amtliche Attribute je Abschnitt. **Ergebnis:** `match_quality`, `in_hvs`, Ist-Tempo amtlich. **Prüfschritt:** 50 Stichproben manuell; Trefferquote im Report.

```text
Implementiere pipeline/s03_conflate.py: Linienabgleich HH-SIB/HVS -> Abschnitte mit Puffer,
Winkel- und Überdeckungsfilter und Hausdorff-Abstand; Schwellen aus rules.yaml (lege sie dort
als source_type: assumption an, falls nicht vorhanden). Flächenquellen (Tempo-30-Zonen,
verkehrsberuhigte Bereiche) über Längenanteil zuordnen. Schreibe match_quality und die
zugeordneten Attribute. Erzeuge reports/conflation_sample.csv mit 50 Zufallsfällen und
Links für die manuelle Prüfung. Keine Schwellen im Code.
```

### P5 – Merkmale

**Ziel:** alle Eingangswerte für die Regeln. **Ergebnis:** `features.parquet`. **Prüfschritt:** Verteilungen plausibel; Anteil fehlender Werte je Merkmal im Report.

```text
Implementiere pipeline/s04_features.py nach guide.md Teil 3.2 Stufe 4: edge betweenness
(zeitgewichtet, igraph, ggf. Stichprobe), Busfahrten pro Werktag aus GTFS (shapes auf
Abschnitte matchen), DTV wo vorhanden, Gebäudedichte, Einwohner aus Zensus-Gitter,
Publikumsnutzung im Erdgeschoss (OSM shop/amenity, ALKIS Gebäudefunktion), Schulen/Kitas
im Radius, Radnetz, Ist-Tempo (amtlich vor OSM, Konflikt als Unsicherheit), Ist-Gestaltung aus
OSM-Tags. Normierung auf 0–1 dokumentieren. Report mit Histogrammen und Nullwertanteilen.
```

### P6 – Klassifikation

**Ziel:** Soll-Kategorie mit Begründung. **Ergebnis:** `cat_proposed`, `confidence`, `rule_trace`. **Prüfschritt:** goldene Fälle grün; Kreuztabelle gegen HVS.

```text
Implementiere pipeline/s05_classify.py als Interpreter der Kaskade in rules.yaml
(classification). Jede Regel liefert (rule_id, passed, inputs); speichere rule_trace als JSON.
confidence: niedrig, wenn Eingangswerte fehlen oder der Wert innerhalb ±10 % einer Schwelle
liegt. Alle tests/golden müssen grün sein. Erzeuge reports/classification.md mit km je
Kategorie, Kreuztabelle Soll x HVS und 30 Zufallsabschnitten je Kategorie mit DOP- und
Panoramax-Links. Ändere keine Schwellen, um Tests grün zu bekommen – frage stattdessen.
```

### P7 – Kohärenz und Korrekturebene

**Ziel:** Flags N1–N6, Overrides. **Ergebnis:** `flags`, `cat_final`, `overrides/overrides.csv`. **Prüfschritt:** Flag-Liste fachlich durchsehen; Test auf verwaiste Overrides.

```text
Implementiere pipeline/s06_coherence.py mit den Regeln N1–N6 aus rules.yaml auf dem Graphen
der vorgeschlagenen Kategorien. Nichts automatisch umklassifizieren; Glättungsvorschläge als
eigene flags. Implementiere die Korrekturebene: overrides/overrides.csv mit segment_id,
cat_final, reason, author, date, source, review_status; nur approved wird übernommen.
Tests: verwaiste segment_ids, ungültige Kategorien, fehlende Begründung -> Fehler.
Report: Liste aller Flags mit Karte.
```

### P8 – Diskrepanz und Priorisierung

**Ziel:** graue Straßen und Prioritätenliste. **Ergebnis:** Typ D1–D3, Stärke, Priorität. **Prüfschritt:** Top-30-Liste von Ortskundigen gegenlesen.

```text
Implementiere pipeline/s08_discrepancy.py nach rules.yaml (discrepancy, priority): Tempo-,
Gestaltungs- und Nutzungsdiskrepanz je Abschnitt, Typ D1–D3, Stärke 0–3, Priorität mit
Unfallatlas (Fuß/Rad, Schwere gewichtet, 5 Jahre), Radnetz, Bevölkerung, Schulen/Kitas.
Unfälle nur aggregiert je Abschnitt speichern. Report: Top 30 mit Begründung in Klartext.
```

### P9 – Querschnitt

**Ziel:** Straßenraumbreite und Machbarkeit. **Ergebnis:** `width_median`, `width_p10`, Engstellen, `feasibility`. **Prüfschritt:** 50 Transekte im DOP20 gemessen, mittlere Abweichung im Report.

```text
Implementiere pipeline/s07_crosssection.py nach guide.md Teil 4.3 a und c: Transekte alle
20 m, ±40 m, Tangente über ±10 m, Varianten 'Verkehrsfläche' (ALKIS tatsächliche Nutzung
Straßenverkehr/Weg/Platz) und 'Fassade' (Gebäude). Knotenbereiche ausschließen, Flags für
offen/Platz, Brücken/Tunnel. Aggregation Median, p10, Minimum, Engstellen. Machbarkeit über
required_width und feasibility_classes aus rules.yaml. Exportiere 50 Zufallstransekte als
GeoJSON für die manuelle Messung. Danach Klassifikation erneut laufen lassen (C-G30-02).
```

### P10 – Webseite

**Ziel:** statische Karte nach Teil 5. **Ergebnis:** `web/`, PMTiles, Steckbrief-JSON, Downloads, Deployment-Workflow. **Prüfschritt:** Lighthouse/axe-Bericht, Test auf Smartphone, Range-Requests des Hostings geprüft.

```text
Implementiere pipeline/s09_export.py (GeoParquet, GeoJSON, CSV, segments/{id}.json,
search.json, PMTiles via tippecanoe, Zoom 10–16) und in web/ eine Vite-Seite mit MapLibre GL JS
und pmtiles nach guide.md Teil 5: Ebenen, Steckbrief, Filter Bezirk/Kategorie, Suche,
Methodenseite, Downloads, Lizenzen, Rückmeldung per vorausgefülltem GitHub-Issue-Link.
Barrierefreiheit WCAG 2.2 AA, Mobil zuerst, dauerhafter Hinweis 'nicht amtlicher Entwurf'.
Kein Tracking, keine Drittanbieter-Schriften. GitHub Action für Build und Deployment.
Führe axe-core-Prüfung aus und berichte die Ergebnisse.
```

### P11 – Validierung

**Ziel:** Bericht nach Teil 7. **Ergebnis:** `reports/validation.md`. **Prüfschritt:** externe Fachperson liest den Bericht.

```text
Schreibe pipeline/validate.py: (1) Kreuztabelle Soll x HVS in km je Bezirk, (2) Soll-ETW30 vs.
Ist-Tempo 30, (3) Sensitivitätsanalyse: jede Schwelle mit source_type assumption ±20 %,
Gewichte zufällig variiert (500 Läufe), Anteil Kategoriewechsel je Abschnitt, Markierung
'unsicher' bei Wechselquote > 0,3 (Annahme in rules.yaml), (4) Datenqualität je Bezirk.
Erzeuge reports/validation.md mit Tabellen, Karten und einer Liste der offenen Fragen.
```

## Quellenverzeichnis

Geöffnet bzw. geprüft am 27.10.2026. Nicht online geprüft und deshalb am Original zu verifizieren: RIN 2008, RASt 06 (Inhalt), ERA 2010 (Original), CROW 315, CROW Afwegingskader 30 km/h, SWOV R-2022-5 (VSGS).

**SWOV, CROW, Kennisnetwerk SPV**

- [SWOV (2023): Principles for a safe road network, Fact sheet April 2023](https://swov.nl/en/fact-sheet/principles-safe-road-network) (vom Nutzer bereitgestellt)
- [SWOV (2018): DV3 – Achtergronden en uitwerking van de verkeersveiligheidsvisie, R-2018-6B](https://swov.nl:443/node/16907)
- [SWOV (2018): DV3 – Visie Duurzaam Veilig Wegverkeer 2018–2030 (Kurzfassung)](https://swov.nl:443/system/files/publication-downloads/dv3_kort_rapport.pdf)
- [SWOV (2021): Concept-opzet evaluatie GOW30, R-2021-27](https://swov.nl:443/system/files/publication-downloads/R-2021-27.pdf)
- [CROW (2023): Handreiking voorlopige inrichtingskenmerken GOW30, Eindrapport v1.0](https://www.amersfoort.nl/sites/default/files/2025-09/2023-crow-handreiking-voorlopige-inrichtingskenmerken-gow30.pdf)
- [Kennisnetwerk SPV (2023): Risico-indicatoren](https://swov.nl/sites/default/files/bestanden/downloads/2023_SWOV_Risico-indicatoren-april2023_KennisnetwerkSPV.pdf)
- [Kennisnetwerk SPV (2020): Wanneer zijn wegen en fietspaden voldoende veilig?](https://swov.nl:443/sites/default/files/bestanden/downloads/2020_SWOV_Factsheet-infra-voldoende-veilig_KennnisnetwerkSPV.pdf)
- [Kennisnetwerk SPV (2023): Veilige infrastructuur](https://swov.nl/sites/default/files/bestanden/downloads/2023_SWOV_Veilige-infrastructuur_KennisnetwerkSPV.pdf) (Abruf durch Bot-Schutz blockiert)
- [Rijkswaterstaat/Sweco (2021): Operationalisatie van de definitie van voldoende veilige wegen en fietsinfrastructuur](https://www.ndw.nu/binaries/ndw/documenten/publicaties/2021/7/23/operationalisatie-definitie-van-voldoende-veilige-wegen-en-fietsinfrastructuur/Operationalisatie+Definitie+KN+SPV+30-50-70-60-80-fietspaden+definitief+def.pdf)
- [Kennisnetwerk SPV (2019): Meetinstrumenten risicogestuurd beleid](https://swov.nl/sites/default/files/bestanden/downloads/2019_SWOV_Meetinstrumenten-risicogestuurd-beleid_KennisnetwerkSPV.pdf)
- [CVS (2015): Grijze wegen in de agglomeratie Amsterdam](https://www.cvs-congres.nl/cvspdfdocs_2015/cvs15_085.pdf)
- [Goudappel/DTV (2021): Het nieuwe 30, Eindrapport](https://www.goudappel.nl/sites/default/files/2022-03/Eindrapport%20%27Het%20nieuwe%2030%27%20%28005496.20200708.R1.05%29_.pdf)

**Deutsche Regelwerke**

- [DIN Media: RASt 06 (FGSV 200), Status aktuell](https://www.dinmedia.de/en/technical-rule/fgsv-200/100597805)
- [FGSV (2022): Pressemitteilung neue Entwurfsregelwerke Fuß- und Radverkehr](https://www.fgsv.de/fileadmin/PRESSE/Pressemitteilungen/2022-12-12_Neue_Entwurfsregelwerke_Fuss_und_Radverkehr.pdf)
- [Niedersachsen: Übersicht Regel- und Mindestbreiten nach ERA 2010 und VwV-StVO](https://www.mw.niedersachsen.de/download/217280/3_Uebersicht_zu_Massnahmen_der_Radverkehrsfuehrung.pdf)
- [Stadt Bayreuth: Erkenntnisstand Radverkehrsführung (ERA-Breiten, Sicherheitstrennstreifen)](https://www.bayreuth.de/wp-content/uploads/2015/06/RVK_Kap2_Erkenntnisstand_Radverkehrsfuehrung.pdf)
- [Gwiasda (2023): Fortschreibung der ERA, Nationaler Radverkehrskongress](https://www.adfc.de/fileadmin/Gliederungen/Pedale/aachen/user_upload/pdf/2023/D3-Peter-Gwiasda.pdf)
- [BVM: ReStra – Hamburger Regelwerke für Planung und Entwurf von Stadtstraßen](https://www.hamburg.de/politik-und-verwaltung/behoerden/bvm/die-themen-der-behoerde/grundlagen-strassenwesen/restra-193078)

**Hamburg: Netz und Daten**

- [BVM: Hauptverkehrsstraßen (Karte Stand Sept. 2023)](https://www.hamburg.de/politik-und-verwaltung/behoerden/bvm/hauptverkehrsstrassen-193350)
- [BSU (2005): Hauptverkehrsstraßen in Hamburg – Kriterienraster](https://epub.sub.uni-hamburg.de/epub/volltexte/2009/4062/pdf/kriterien_hauptverkehrsstrassen.pdf)
- [GDI-DE: WFS Strategisches Straßennetz Hamburg](https://gdk.gdi-de.org/geonetwork/srv/api/records/2BAA8BEB-5C50-401A-BA06-DF20F4D4EBBE)
- [api.hamburg.de: Zulässige Höchstgeschwindigkeiten, Tempo-30-Zonen](https://api.hamburg.de/datasets/v1/zulaessige_hoechstgeschwindigkeiten/collections/tempo30zonen)
- [api.hamburg.de: Verkehrsberuhigte Bereiche](https://api.hamburg.de/datasets/v1/zulaessige_hoechstgeschwindigkeiten/collections/verkehrsberuhigte_bereiche)
- [api.hamburg.de: Verkehrsmengen DTV Bundesautobahnen 2019](https://api.hamburg.de/datasets/v1/verkehrsmengen/collections/verkehrsmengen_dtv_bab_2019)
- [api.hamburg.de: Radverkehrsmengen DB Rad+, Jahr 2022](https://api.hamburg.de/datasets/v1/dbradplus/collections/jahr2022)
- [GDI-DE: WFS ALKIS Liegenschaften Hamburg](https://gdk.gdi-de.org/geonetwork/srv/api/records/00F5606E-4563-49C6-960A-72617C9E5256)
- [GDI-DE: 3D-Stadtmodell Hamburg](https://gdk.gdi-de.org/geonetwork/srv/api/records/D63EFF3A-B354-4C21-8248-2F3F989AFF8C)
- [LGV: Digitale Orthophotos](https://www.hamburg.de/politik-und-verwaltung/behoerden/behoerde-fuer-stadtentwicklung-und-wohnen/aemter-und-landesbetrieb/landesbetrieb-geoinformation-und-vermessung/produkte-und-dienstleistungen/geodaten-des-lgv/digitaleorthophotos-244130)
- [GDI-DE: WFS ZEB Zustandsklassen](https://gdk.gdi-de.org/geonetwork/srv/api/records/EA228C50-F461-4750-944F-09D049533C38)
- [GDI-DE: WFS Straßendeckschichttypen RLS-19](https://gdk.gdi-de.org/geonetwork/srv/api/records/09D4B9B6-B3C9-4F0B-B378-DD736F6A2F03)
- [INSPIRE: WFS Ruhige Gebiete Hamburg](https://inspire-geoportal.ec.europa.eu/srv/api/records/7E2D8291-3DC5-4BB6-80E8-A9947F211A88)
- [BUKEA (2023): 25 Jahre digitales Baumkataster](https://www.hamburg.de/politik-und-verwaltung/behoerden/bukea/aktuelles/pressemeldungen/2023-11-10-bukea-25-jahre-digitales-baumkataster-235658)
- [OSM-Wiki: Radnetz Hamburg](https://wiki.openstreetmap.org/wiki/DE:Tag:cycle_network%3DDE:HH:Radnetz_Hamburg)
- [BSW: Hamburger Magistralen](https://www.hamburg.de/politik-und-verwaltung/behoerden/behoerde-fuer-stadtentwicklung-und-wohnen/hintergrund-864874)
- [Mobility Database: HVV GTFS-Feed](https://mobilitydatabase.org/feeds/mdb-3362); [OSM-Wiki: Lizenzauskunft hvv](https://wiki.openstreetmap.org/wiki/DE:Permissions/hvv)
- [Zensus 2022: Gitterdaten](https://zensus2022.de/EN/Census_results/02-release-of-results.html?nn=470744)
- [Unfallatlas-Daten am Beispiel Köln (Lizenzvermerk dl-de/by-2.0)](https://ckan-open-nrw.nrw.de/ne/dataset/unfallatlas-koln-2021-k/resource/fe256079-b9bd-4f25-8b38-2aa7dff0eedd)

**Vorbericht**

- Hamburger Straßenfunktionsplan – Strategie für die Zivilgesellschaft (27.10.2026), vom Nutzer bereitgestellt; darin u. a. [Gemeenteblad Deventer 2026-326071](https://zoek.officielebekendmakingen.nl/gmb-2026-326071.pdf) und [Baumeister/Ringena 2026](https://www.hamburg.de/resource/blob/1157010/6d07bc535e1c44b21a18b5ad6a4d03bb/mobiforum-26-input-1-baumeister-ringena-data.pdf)
