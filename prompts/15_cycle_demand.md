# 15 – Radverkehrsnachfrage schätzen

**Ziel:** Radverkehrsstärke (Rad/Tag und Spitzenstunde) je Kante als Grundlage für Hierarchie und Breiten.
**Eingaben:** Kandidatennetz (Straßenabschnitte + eigenständige Radwege aus OSM), Zensus-Gitter, Ziele, Zählstellen, DB Rad+, config/cycling_rules.yaml (routing_impedance, demand).
**Ergebnis:** pipeline/c01_cycle_graph.py, pipeline/c02_cycle_demand.py, data/interim/cycle_edges.parquet mit cyc_day_model, cyc_peak_h, cyc_calibrated, demand_confidence; reports/cycle_demand.md.
**Prüfschritt:** Vergleich Modell vs. Zählstellen (Streudiagramm, Korrelation, mittlere relative Abweichung); Plausibilität der 30 stärksten Kanten mit Ortskundigen.

## Auftrag

1. c01_cycle_graph.py: Baue einen gerichteten Radgraphen für ganz Hamburg aus
   - den bestehenden Straßenabschnitten (segment_id, cat_final, Ist-Radführung),
   - eigenständigen Rad- und Fußwegen mit Radfreigabe aus OSM (highway=cycleway, path/footway mit bicycle=yes|designated),
   - Fähren mit Radmitnahme als Kanten mit Wartezeit (Annahme in cycling_rules.yaml ergänzen).
   Kanten-ID stabil (edge_id), Bezug zu segment_id, wo vorhanden. Einbahnstraßen: Radverkehr in
   Gegenrichtung nur, wenn OSM es erlaubt (oneway:bicycle=no).
   Widerstand = Länge × Faktor aus routing_impedance (Ist-Zustand) + Knotenverzögerungen.
2. c02_cycle_demand.py: einfaches, dokumentiertes Nachfragemodell
   - Quellen: Einwohner im 100-m-Gitter (zu Zonen von ca. 500 m aggregiert);
   - Ziele: Arbeitsplätze-Proxy (Gebäudefläche Nichtwohnen aus ALKIS), Schulen, Hochschulen,
     Schnellbahnhalte, Einzelhandel (OSM shop);
   - Gravitationsmodell mit Distanzverfall für Radwege 0,5–15 km (Funktion und Parameter als
     assumption in cycling_rules.yaml, Abschnitt demand_model);
   - Umlegung auf kürzeste Wege nach wahrgenommenem Widerstand (alles-oder-nichts oder 3 Iterationen
     mit leichter Streuung; Laufzeit dokumentieren);
   - Kalibrierung: ein Skalierungsfaktor (ggf. je Bezirk) an Dauerzählstellen; DB Rad+ nur als
     Plausibilitätsvergleich, nicht zur Kalibrierung (nicht repräsentativ).
   - cyc_peak_h = cyc_day × peak_hour_share_of_day.
3. Speichere demand_confidence (hoch nahe Zählstellen, sonst mittel/niedrig).

Keine Parameter im Code. Report mit Karte, Kalibrierungsgüte und Grenzen. Wenn Zählstellendaten
nicht erreichbar sind: abbrechen und berichten.
