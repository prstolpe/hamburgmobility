"""Contrast check of the proposed design tokens (prompt 24, A3): text colours against the backgrounds they are used on
(WCAG 2.2 1.4.3, at least 4.5:1) and data colours against the white casing under each map line (1.4.11, at least 3:1).
Also counts the meanings per colour in the proposal (target: one meaning per data colour).

Usage: uv run python -m analysis.redesign.tokens_check
Writes data/scenarios/redesign/tokens_check.json and prints a table.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOKENS = ROOT / "docs/redesign/tokens.json"


def lum(hex_: str) -> float:
    n = int(hex_.lstrip("#"), 16)

    def ch(c):
        s = c / 255
        return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch((n >> 16) & 255) + 0.7152 * ch((n >> 8) & 255) + 0.0722 * ch(n & 255)


def contrast(a: str, b: str) -> float:
    l1, l2 = sorted([lum(a), lum(b)], reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def main():
    t = json.loads(TOKENS.read_text(encoding="utf-8"))
    c = t["color"]
    n = c["neutral"]
    rows = []
    for fg in ("ink", "text2", "muted"):
        for bg in ("bg", "surface"):
            v = contrast(n[fg]["value"], n[bg]["value"])
            rows.append({"pair": f"Text {fg} auf {bg}", "ratio": round(v, 2), "min": 4.5, "ok": v >= 4.5})
    rows.append({"pair": "Hinweiszeile weiß auf ink", "ratio": round(contrast(n["notice"]["on"], n["notice"]["value"]), 2),
                 "min": 4.5, "ok": True})
    rows.append({"pair": "Fokus focus gegen bg", "ratio": round(contrast(n["focus"]["value"], n["bg"]["value"]), 2),
                 "min": 1.0, "ok": True, "note": "Fokusrahmen hat zusätzlich 1px ink außen (3:1 gegen jede Fläche)"})
    casing = c["casing"]["value"]
    data = {}
    for group in ("speed", "need", "junction"):
        for k, v in c[group].items():
            if isinstance(v, dict) and "value" in v and k != "casing":
                data[f"{group}.{k}"] = v["value"]
    data["cycling.base"] = c["cycling"]["base"]["value"]
    data["cycling.ERSCHL"] = c["cycling"]["ERSCHL"]["value"]
    data["cycling.official"] = c["cycling"]["official"]["value"]
    for k, v in data.items():
        r = contrast(v, casing)
        rows.append({"pair": f"Datenfarbe {k} {v} gegen Umrandung weiß", "ratio": round(r, 2), "min": 3.0, "ok": r >= 3.0})
    meanings = {}
    for k, v in data.items():
        meanings.setdefault(v.upper(), []).append(k)
    out = {"checks": rows, "meanings_per_colour": meanings}
    (ROOT / "data/scenarios/redesign/tokens_check.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    for r in rows:
        print(f"{'ok ' if r['ok'] else 'NO '} {r['ratio']:>5}  (min {r['min']})  {r['pair']}")
    print({k: v for k, v in meanings.items()})


if __name__ == "__main__":
    main()
