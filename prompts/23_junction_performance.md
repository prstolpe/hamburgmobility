# 23 – Leistungsfähigkeit der Knotenpunkte: Wartezeiten Ist und Soll

**Ziel:** zeigen, wie einfachere und effizientere Knotenpunkte den Verkehrsfluss verbessern: Wartezeit je Knotenpunkt für
Kfz, Rad und Fuß, Ist gegen Soll, heute und im Zieljahr (Prompt 22). Ergebnis sind Größenordnungen, klar als Schätzung
gekennzeichnet.
**Eingaben:** data/interim/junctions.parquet (Arme, entering_dtv_sum, junction_type_ist/soll, signal_present_ist),
Spitzenstundenanteil (C-FAC-03 motor_peak_hour_share), Radverkehr je Arm (c02 bzw. Szenario), HBS 2015 (FGSV) – Verfahren für
Knotenpunkte mit LSA, Kreisverkehre und Vorfahrtknoten am Original, Webster (1958) für die LSA-Wartezeit; optional
Signalprogramme der BVM (Anfrage aus Prompt 22).
**Ergebnis:** design_rules.yaml Abschnitt `junction_performance` (neue meta.version), pipeline/c10_junction_performance.py,
data/interim/junction_performance.parquet (node_id, delay_car_ist_s, delay_car_soll_s, delay_cycle_ist_s,
delay_cycle_soll_s, saturation_ist, saturation_soll, qsv_ist, qsv_soll, performance_flags, rule_trace_performance),
reports/junction_performance.md.
**Prüfschritt:** Formeln gegen Rechenbeispiele aus HBS bzw. Literatur (goldene Fälle in tests/golden/cycling/);
Sensitivität ±20 % aller Annahmen; 30 Knotenpunkte mit Ortskenntnis plausibilisiert.

## Auftrag

1. **Parameter** in design_rules.yaml `junction_performance`: Verfahren je Knotentyp (LSA: Webster bzw. HBS; Kreisverkehr
   einstreifig und Turbo: HBS-Kapazität; Vorfahrt mit Wartepflicht: HBS-Zeitlückenverfahren; rechts vor links und
   Gehwegüberfahrt: pauschale Verlustzeit), Annahmen für fehlende Daten (Umlaufzeit je Ist-LSA nach Armzahl, gleiche
   Aufteilung auf die Arme, Abbiegeanteile). Jeder Wert mit Quelle oder als assumption mit Eintrag in docs/open_questions.md.
2. **Kfz:** mittlere Wartezeit in der Spitzenstunde und Auslastungsgrad je Knotenpunkt für Ist- und Soll-Typ; Stufe der
   Verkehrsqualität nach HBS, wo das Verfahren sie liefert.
3. **Rad und Fuß:** Wartezeit an LSA (mittlere Rotzeit), an Furten mit Vorrang, bei Wartepflicht; Anbindung an die
   Halte-Prüfung der Prinzipien (C-PRI-05, offene Frage „Soll für Halte nach Prompt 20“).
4. **Netzkennzahlen:** Fahrzeugstunden und Radfahrstunden je Werktag, gesamt und je Bezirk, Ist gegen Soll; Anzahl
   entfallender LSA; Knotenpunkte, deren Soll-Typ über der Kapazität liegt (Flag over_capacity, Rückmeldung an J-01/J-03).
5. **Zieljahr:** dieselbe Rechnung mit dtv_scenario und cyc_peak_h_scenario aus Prompt 22.
6. **Web:** Knoten-Steckbrief „Wartezeit heute ≈ … s, Soll ≈ … s“ (Kfz und Rad); Ebene „Zeitgewinn je Knotenpunkt“ mit
   farbenblind-sicherer Legende; Methodenseite: Verfahren, Annahmen, Grenzen (keine Signalpläne, keine Abbiegeströme).
7. **Schaufenster (optional, eigener Unterauftrag):** Mikrosimulation mit SUMO (Netz aus OSM) für 2–3 bekannte Korridore
   oder Knotenpunkte, Auswahl mit dem Team; Ist gegen Soll, Kennzahlen und kurze Animation für die Webseite.

Keine Schwellen im Code; Ergebnisse immer als Schätzung mit Spannweite aus der Sensitivität ausweisen.
