"""Override layer (guide 3.2 Stufe 7, prompts/09): validation, application, template helper."""

import io

import pandas as pd
import pytest

from pipeline.lib import overrides as ov

CATS = ["SW", "GOW50", "GOW30", "ETW30", "ETW_ERF", "GOW80", "ETW60"]


def segments() -> pd.DataFrame:
    return pd.DataFrame({"segment_id": ["seg_a", "seg_b", "seg_c", "seg_out"],
                         "cat_proposed": ["GOW50", "ETW30", "GOW30", None]})


def row(**kw) -> dict:
    base = {"segment_id": "seg_a", "cat_final": "GOW30", "reason": "Schulweg, Ortsbegehung", "author": "M. Muster",
            "date": "2026-10-28", "source": "Ortsbegehung 2026-10-20", "review_status": "approved"}
    return {**base, **kw}


def frame(*rows) -> pd.DataFrame:
    return pd.DataFrame(list(rows), columns=ov.COLUMNS)


def check(df):
    s = segments()
    ov.validate(df, s.loc[s["cat_proposed"].notna(), "segment_id"], s["segment_id"], CATS)


def test_valid_file_passes():
    check(frame(row(), row(segment_id="seg_b", cat_final="ETW_ERF", review_status="draft")))


def test_empty_file_passes():
    check(frame())


@pytest.mark.parametrize(
    ("bad", "message"),
    [
        (row(segment_id="seg_gone"), "verwaist"),
        (row(segment_id="seg_out"), "außerhalb des Arbeitsgebiets"),
        (row(cat_final="GOW40"), "ungültige Kategorie"),
        (row(reason=""), "Begründung fehlt"),
        (row(reason="   "), "Begründung fehlt"),
        (row(reason=None), "Begründung fehlt"),
        (row(author=""), "author fehlt"),
        (row(date="28.10.2026"), "Datum"),
        (row(review_status="ok"), "review_status"),
    ],
)
def test_invalid_rows_raise_clear_error(bad, message):
    with pytest.raises(ov.OverrideError, match=message) as exc:
        check(frame(bad))
    assert "Zeile 2" in str(exc.value)  # line number in the CSV (header = line 1)
    assert bad["segment_id"] in str(exc.value)


def test_duplicate_segment_id_raises():
    with pytest.raises(ov.OverrideError, match="doppelt"):
        check(frame(row(), row(review_status="draft")))


def test_wrong_columns_raise():
    with pytest.raises(ov.OverrideError, match="Spalten"):
        check(pd.DataFrame([{"segment_id": "seg_a", "cat_final": "GOW30"}]))


def test_all_errors_reported_together():
    with pytest.raises(ov.OverrideError) as exc:
        check(frame(row(segment_id="seg_gone"), row(segment_id="seg_b", cat_final="X")))
    assert "verwaist" in str(exc.value) and "ungültige Kategorie" in str(exc.value)


def test_apply_only_approved_and_keeps_cat_proposed():
    segs = segments()
    df = frame(row(), row(segment_id="seg_b", cat_final="ETW_ERF", review_status="draft"),
               row(segment_id="seg_c", cat_final="GOW50", review_status="rejected"))
    out = ov.apply(segs, df)
    assert list(out["cat_proposed"]) == list(segs["cat_proposed"])
    assert list(out["cat_final"].fillna("–")) == ["GOW30", "ETW30", "GOW30", "–"]
    assert list(out["cat_final_source"].fillna("–")) == ["override", "proposed", "proposed", "–"]
    assert out.loc[0, "override_reason"] == "Schulweg, Ortsbegehung"
    assert out.loc[0, "override_author"] == "M. Muster"
    assert pd.isna(out.loc[1, "override_reason"])


def test_read_csv_keeps_text(tmp_path):
    path = tmp_path / "overrides.csv"
    frame(row(date="2026-10-28")).to_csv(path, index=False)
    df = ov.read_overrides(path)
    assert df.loc[0, "date"] == "2026-10-28" and list(df.columns) == ov.COLUMNS


def test_repo_overrides_file_has_the_columns():
    df = ov.read_overrides(ov.OVERRIDES_PATH)
    assert list(df.columns) == ov.COLUMNS


def test_template_rows_round_trip():
    text = ov.template_csv(["seg_b", "seg_a"], segments(), author="M. Muster", today="2026-10-28")
    df = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    assert list(df.columns) == ov.COLUMNS
    assert list(df["segment_id"]) == ["seg_b", "seg_a"]
    assert list(df["cat_final"]) == ["ETW30", "GOW50"]  # prefilled with cat_proposed
    assert set(df["review_status"]) == {"draft"}
    with pytest.raises(ov.OverrideError, match="Begründung fehlt"):  # reason must be filled in by a person
        check(df)
    df["reason"] = "geprüft"
    check(df)


def test_template_rejects_unknown_ids():
    with pytest.raises(ov.OverrideError, match="seg_gone"):
        ov.template_csv(["seg_gone"], segments(), author="", today="2026-10-28")


# --- correction layers of the cycle network extension (prompts/14) ---------------------------


@pytest.mark.parametrize("path, columns", [
    (ov.CYCLE_NETWORK_OVERRIDES_PATH, ov.CYCLE_NETWORK_COLUMNS),
    (ov.JUNCTION_OVERRIDES_PATH, ov.JUNCTION_COLUMNS),
])
def test_cycling_override_files_have_expected_header(path, columns):
    df = ov.read_overrides(path)
    assert list(df.columns) == columns
    assert set(df["review_status"]) <= set(ov.REVIEW_STATUS)
