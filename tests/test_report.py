import pandas as pd

from pipeline.lib.report import district_breakdown


def test_district_breakdown_shares_and_total():
    df = pd.DataFrame({"bezirk": ["A", "A", "B", None], "cat": ["X", "Y", "X", None],
                       "length_m": [3000.0, 1000.0, 2000.0, 500.0]})
    lines = district_breakdown(df, "cat", ["X", "Y"])
    assert lines[0] == "| Bezirk | Abschnitte | km | X | Y | – |"
    assert lines[2] == "| A | 2 | 4.0 | 75 % | 25 % | 0 % |"
    assert lines[3] == "| B | 1 | 2.0 | 100 % | 0 % | 0 % |"
    assert lines[4].startswith("| ohne Bezirk | 1 | 0.5 |")
    assert lines[5] == "| **gesamt** | 4 | 6.5 | 77 % | 15 % | 8 % |"
