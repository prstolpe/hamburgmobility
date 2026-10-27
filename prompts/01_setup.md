# 01 – Setup

**Ziel:** lauffähiges Repository-Gerüst, ohne vorhandene Dateien zu überschreiben.
**Eingaben:** CLAUDE.md, README.md, docs/guide.md (Teil 6.1), config/*.yaml.
**Ergebnis:** uv-Projekt, Makefile, Ordner pipeline/, pipeline/lib/, tests/, tests/golden/, reports/, web/, data/manifest.json (leer).
**Prüfschritt:** `make test` läuft grün; `git status` zeigt keine Änderungen an config/, docs/, overrides/.

## Auftrag

Lies CLAUDE.md, README.md und docs/guide.md (vor allem Teil 6.1 und 6.2).
Lege die fehlende Repository-Struktur aus Teil 6.1 an. Überschreibe keine vorhandenen Dateien
in config/, docs/, overrides/, prompts/ und nicht CLAUDE.md oder README.md.

Richte ein uv-Projekt (Python 3.12) ein mit: geopandas, shapely>=2, pyogrio, pyproj, pyrosm,
osmnx, networkx, python-igraph, duckdb, pydantic, pyyaml, requests, pytest.
Schreibe ein Makefile mit den Zielen aus CLAUDE.md (Abschnitt „Befehle“); Ziele ohne Skript
geben vorerst eine Meldung „noch nicht implementiert“ aus.
Lege pipeline/lib/crs.py mit einer Funktion to_work_crs(gdf) an (EPSG:25832) und einen Test dafür.

Zeige mir zuerst den Plan. Nach Freigabe umsetzen und `make test` ausführen.
Noch keine Fachlogik und keine Downloads.
