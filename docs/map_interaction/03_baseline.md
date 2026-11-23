# Leistung und Barrierefreiheit (vorher)

Stand: 22.11.2026, Prompt 28. Gemessen vom Agenten `a11y-perf-check` (haiku) gegen `vite preview` mit dem Build von
main (Dateien `index-t9iKy390.js`, `map-jkw02JXi.js`). Skript für die Wiederholung nach dem Umbau:
`measure.mjs` (Scratchpad der Sitzung; wird in Phase 2 nach `web/scripts/perf.mjs` übernommen).

## Bundle (gzip Stufe 9, KB = 1000 Byte)

| Datei | roh | gzip |
| --- | ---: | ---: |
| index.js (Seite) | 162,7 | 54,6 |
| map.js (MapLibre, Protomaps, eigener Kartencode) | 1096,9 | 292,9 |
| maplibre-gl-worker.mjs | 508,3 | 144,5 |
| index.css | 15,7 | 4,1 |
| map.css | 82,9 | 10,4 |

JS beim Laden von `#karte`: 492,0 KB gzip (347,5 KB ohne Worker). Daten beim ersten Laden: meta.json 17,5 KB,
search.json 574 KB, search_junctions.json 328 KB (zusammen ≈ 919 KB JSON, vom Vorschauserver unkomprimiert),
PMTiles-Bereichsabfragen ≈ 1 MB.

## Zeit bis bedienbar (`#karte?map=13/53.5560/9.9700`, 5 Läufe, kalter Cache)

Gemessen bis zur letzten WebGL-Zeichnung bzw. letzten Antwort (Karte ruht 500 ms), da die Karteninstanz nicht
global erreichbar ist.

| Profil | Median | Min–Max |
| --- | ---: | ---: |
| Desktop | 1578 ms | 1547–1727 ms |
| Mobil 390 × 844, CPU ×4 | 2691 ms | 2430–2997 ms |

## Bildrate (Mobil, CPU ×4, Verschieben und Neigen je 3 × 3 s)

| Geste | Median | p10 |
| --- | ---: | ---: |
| Verschieben | 10,5 fps | 8,0 fps |
| Neigen | 10,2 fps | 6,4 fps |

Schon heute niedrig auf dem gedrosselten Profil (ganze Stadt als Vektorkacheln, dicke Linien mit Rand). Der Umbau
darf das nicht verschlechtern; Verbesserungen an den Kartenebenen sind nicht Teil dieses Auftrags.

## Barrierefreiheit

`npm run a11y`: 72 Playwright-Tests bestanden; axe-core 4.13.0 auf 34 Seitenprüfungen (17 Desktop, 17 Mobil):
0 Verstöße. Manuell zu prüfen: 14 bzw. 16 Hinweise. Konsole: keine Fehler auf `#karte`, `#karte?theme=rad`,
`#karte?place=…` (zwei abgebrochene Basemap-Anfragen beim Zoomen auf den Ort – vermutlich durch das Einpassen
abgebrochene Bereichsabfragen, nicht untersucht).

## Vorschlag Budget für Phase 2

- JS: höchstens **+15 KB gzip** auf `#karte` (Registry, Panel, Sheet, URL-Schema).
- Zeit bis bedienbar: höchstens **+5 %** (Desktop ≤ 1660 ms, Mobil ≤ 2830 ms).
- Bildrate: nicht schlechter als vorher (Median ≥ 10 fps, p10 ≥ 6 fps auf dem gedrosselten Profil); die
  Prüfung „im Ausschnitt“ läuft erst 150 ms nach `idle`, nie während einer Bewegung.
- axe: weiterhin 0 Verstöße.
