"""Scenario B (status quo of rules 0.14.0): port the DTV cap on C-G30-01 and rule C-G50-02 onto the current rules.

Writes a patch for the scenario worktree only (config/ of the main checkout stays unchanged). Rule text, threshold
and plain-language sentences are copied verbatim from tag variante-gow50-kompromiss (rules.yaml 0.14.0).

Usage: python -m analysis.review_2026_11.make_patch_B <scratch_dir> <patch_out>
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TAG = "variante-gow50-kompromiss"

OLD_IF = 'if: "schools_or_kitas_within_m <= thresholds.sensitive_radius or shop_frontage_share >= thresholds.frontage or crossing_demand == high"'
NEW_IF = 'if: "(schools_or_kitas_within_m <= thresholds.sensitive_radius or shop_frontage_share >= thresholds.frontage or crossing_demand == high) and (not in_hvs or dtv_official <= thresholds.gow30_max_dtv)"'
CAP = '      gow30_max_dtv:    {value: 10000, unit: "Kfz/24h", source: CROW_GOW30_2023, source_type: swov_crow, check: "gleich requirements.GOW30.profiles.wide.max_dtv (Schema prüft)"}\n'
G50_02 = '''  - id: C-G50-02
    description: "Umfeld spräche für 30, aber die Hauptverkehrsstraße trägt mehr Verkehr als das CROW-GOW30-Profil: GOW50, Tempo-30-Abschnitt vor Ort prüfen"
    applies_to: GOW
    if: "(schools_or_kitas_within_m <= thresholds.sensitive_radius or shop_frontage_share >= thresholds.frontage or crossing_demand == high) and in_hvs and dtv_official > thresholds.gow30_max_dtv"
    then: GOW50
    source: CROW_GOW30_2023
    source_type: swov_crow
    status: draft
    note: "Szenario B (Review 2026-11): aus rules.yaml 0.14.0 übernommen."

'''
PL_FAILED = '      - {when: "in_hvs and dtv_official > thresholds.gow30_max_dtv", text: "zu viel Verkehr für eine Stadtstraße 30: {dtv_official|.0f} Kfz/Tag (CROW-Profil bis {thresholds.gow30_max_dtv|.0f})"}\n'
PL_G50_02 = '''  C-G50-02:
    passed:
      - {text: "Schule, Kita oder Läden in der Nähe, aber {dtv_official|.0f} Kfz/Tag – mehr als eine Stadtstraße 30 nach CROW trägt (bis {thresholds.gow30_max_dtv|.0f}); darum Stadtmagistrale mit baulichem Radweg. Abschnitt mit Tempo 30 vor Ort prüfen"}
'''


def replace_once(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, f"expected exactly one match for: {old[:60]}"
    return text.replace(old, new)


def main(scratch: str, patch_out: str) -> None:
    s = Path(scratch)
    for side in ("a", "b"):
        (s / side / "config").mkdir(parents=True, exist_ok=True)
    rules = (ROOT / "config/rules.yaml").read_text(encoding="utf-8")
    pl = (ROOT / "config/plain_language.yaml").read_text(encoding="utf-8")
    (s / "a/config/rules.yaml").write_text(rules, encoding="utf-8")
    (s / "a/config/plain_language.yaml").write_text(pl, encoding="utf-8")

    rules = replace_once(rules, OLD_IF, NEW_IF)
    rules = replace_once(rules, '      frontage:         {value: 0.4, unit: "Anteil Erdgeschoss mit Publikumsnutzung", source_type: assumption}\n',
                         '      frontage:         {value: 0.4, unit: "Anteil Erdgeschoss mit Publikumsnutzung", source_type: assumption}\n' + CAP)
    rules = replace_once(rules, "  - id: C-G50-01\n", G50_02 + "  - id: C-G50-01\n")
    pl = replace_once(pl, '      - {text: "keine Schule oder Kita in der Nähe und wenig Publikumsverkehr"}\n',
                      PL_FAILED + '      - {text: "keine Schule oder Kita in der Nähe und wenig Publikumsverkehr"}\n')
    pl = replace_once(pl, "  C-G50-01:\n", PL_G50_02 + "  C-G50-01:\n")
    (s / "b/config/rules.yaml").write_text(rules, encoding="utf-8")
    (s / "b/config/plain_language.yaml").write_text(pl, encoding="utf-8")

    # check against the tag: the C-G50-02 condition must be identical to 0.14.0
    tag_rules = subprocess.run(["git", "-C", str(ROOT), "show", f"{TAG}:config/rules.yaml"], capture_output=True,
                               text=True, check=True).stdout
    assert NEW_IF in tag_rules and G50_02.splitlines()[3].strip() in tag_rules, "rule text differs from 0.14.0"

    # golden cases of 0.14.0: case 28 expects GOW50 there, case 30 tests the cap at exactly 10 000
    for side in ("a", "b"):
        (s / side / "tests/golden").mkdir(parents=True, exist_ok=True)
    cur28 = "tests/golden/28_gow30_hvs_school_high_dtv.geojson"
    (s / "a" / cur28).write_bytes((ROOT / cur28).read_bytes())
    for f in ("tests/golden/28_gow50_hvs_school_dtv_above_gow30.geojson", "tests/golden/30_dtv_at_gow30_max.geojson"):
        (s / "b" / f).write_bytes(subprocess.run(["git", "-C", str(ROOT), "show", f"{TAG}:{f}"], capture_output=True,
                                                 check=True).stdout)
    diff = ""
    for sub in ("config", "tests"):
        diff += subprocess.run(["git", "diff", "--no-index", "--no-renames", f"a/{sub}", f"b/{sub}"], cwd=s,
                               capture_output=True, text=True).stdout
    # paths in the patch relative to the repo root
    for sub in ("config", "tests"):
        for x in ("a", "b"):
            for y in ("a", "b"):
                diff = diff.replace(f"{x}/{y}/{sub}/", f"{x}/{sub}/")
    Path(patch_out).write_text(diff, encoding="utf-8")
    print(f"patch -> {patch_out} ({len(diff.splitlines())} lines)")


if __name__ == "__main__":
    main(*sys.argv[1:3])
