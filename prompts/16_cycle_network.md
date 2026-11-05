# 16 – Radnetz entwerfen (Hierarchie und Lückenschluss)

**Ziel:** Soll-Radnetz mit Kategorien RSV, HAUPT, BASIS, ERSCHL für ganz Hamburg.
**Eingaben:** cycle_edges.parquet (Nachfrage), amtliches Radnetz Hamburg, Ziele, cat_final, config/cycling_rules.yaml.
**Ergebnis:** pipeline/c03_cycle_network.py, Spalten cycle_cat_proposed, cycle_cat_final, route_id, rule_trace_cycle; data/interim/cycle_routes.parquet; reports/cycle_network.md.
**Prüfschritt:** Karte Soll vs. amtliches Radnetz; Kennzahlen je Kategorie (km, Maschenweite, Abdeckung); Durchsicht mit Ortskundigen je Bezirk.

## Auftrag

Implementiere c03_cycle_network.py:
1. Korridore: Verbinde Bezirkszentren, Hochschulen, große Arbeitsplatzschwerpunkte und
   Schnellbahnknoten untereinander und mit der Innenstadt über Wege nach Soll-Widerstand
   (routing_impedance mit Soll-Führung: Annahme, dass die Route regelkonform ausgebaut wird).
   Bevorzuge Kanten mit hoher Nachfrage und Kanten des amtlichen Radnetzes (Bonus als assumption).
2. Hierarchie:
   - RSV: Korridore mit modellierter Nachfrage ≥ demand_trigger_cyclists_weekday und Länge ≥ min_route_length_km.
   - HAUPT: Netz so verdichten, dass keine Masche des HAUPT+RSV-Netzes größer als mesh_m.max ist.
   - BASIS: Verdichtung auf 200–300 m mit Bindung an Schulen und Nahversorgung.
   - ERSCHL: alle übrigen befahrbaren Kanten.
   Maschen als Flächen bilden (Polygonisierung des Netzes je Ebene, Wasser/Bahn/Parks als Barrieren
   beachten) und Größe als Seitenlänge des flächengleichen Quadrats messen.
3. Parallelregel P-ATT-03: Wenn eine HAUPT/RSV-Route an einer Straße mit DTV > Schwelle liegt und
   eine Parallelstraße innerhalb parallel_max_m den Umwegfaktor einhält, schlage die Parallelroute
   vor und behalte die Hauptstraße als BASIS (mit getrennten Radwegen nach Matrix).
4. Kontinuität: Routen erhalten route_id; Kategoriesprünge entlang einer Route werden geglättet
   oder als Flag gemeldet.
5. Korrekturebene overrides/cycle_network_overrides.csv anwenden (nur approved).

Jede Entscheidung in rule_trace_cycle (Regel-ID, Werte). Keine Schwellen im Code. Report mit
Karten je Ebene, Lückenliste, Vergleich zum amtlichen Radnetz (Überdeckung in km, fehlende und
zusätzliche Abschnitte).
