# 07 – Querschnitt: Straßenraumbreite und Machbarkeit

**Ziel:** width_median, width_p10, Engstellen und Machbarkeitsklasse je Abschnitt.
**Eingaben:** features.parquet, ALKIS (tatsächliche Nutzung, Gebäude), LoD2, docs/guide.md Teil 4.
**Ergebnis:** pipeline/s07_crosssection.py, Spalten width_*, narrow_points, feasibility_*, reports/crosssection.md, reports/transect_sample.geojson.
**Prüfschritt:** 50 Zufallstransekte im Orthophoto DOP20 messen; mittlere absolute Abweichung im Report (Ziel < 1 m, assumption).

## Auftrag

Implementiere pipeline/s07_crosssection.py nach docs/guide.md Teil 4.3 a und c:
- Mittellinie glätten (2 m), alle 20 m Senkrechte von ±40 m, Tangente über ±10 m gemittelt.
- Variante „Verkehrsfläche“: Schnitt mit ALKIS-Flächen der tatsächlichen Nutzung
  Straßenverkehr, Weg, Platz. Variante „Fassade“: Schnitt mit Gebäudegrundrissen.
  Ermittle die tatsächlichen ALKIS-Objektart-Bezeichnungen aus den Daten, nicht aus dem Gedächtnis.
- Transekte innerhalb 20 m um Knoten verwerfen; Flag „open_space“, wenn auf einer Seite keine
  Grenze innerhalb 40 m; Brücken/Tunnel ausschließen.
- Aggregation: Median, p10, Minimum, Engstellen (≥ 3 aufeinanderfolgende Transekte unter p10).
- Machbarkeit: width_ratio = width_p10 / required_width je möglicher Soll-Kategorie
  (GOW50, GOW30_narrow, ETW30) mit Klassen aus feasibility_classes in rules.yaml.
- Alle Abstände und Längen aus rules.yaml (Abschnitt crosssection, als assumption ergänzen).

Exportiere 50 Zufallstransekte als reports/transect_sample.geojson für die manuelle Messung.
