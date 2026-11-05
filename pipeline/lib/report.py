"""Report helpers shared by the stages: tables per Bezirk."""

import pandas as pd

from pipeline.lib.area import NO_DISTRICT


def _de(v: float, digits: int) -> str:
    return f"{v:,.{digits}f}".replace(",", " ")  # same format as the stage reports


def district_breakdown(df: pd.DataFrame, col: str, categories: list, title_col: str = "Bezirk") -> list[str]:
    """Markdown table: per Bezirk (alphabetical) and in total the segments, km and km share per category of `col`.

    Missing values count as "–". Bezirke without any segment are not listed.
    """
    cats = [*categories, None] if df[col].isna().any() else list(categories)
    head = f"| {title_col} | Abschnitte | km | " + " | ".join("–" if c is None else str(c) for c in cats) + " |"
    sep = "| --- | ---: | ---: | " + " | ".join("---:" for _ in cats) + " |"
    lines = [head, sep]
    bez = df["bezirk"].fillna(NO_DISTRICT)

    def row(name: str, g: pd.DataFrame, bold: bool = False) -> str:
        km = g["length_m"].sum() / 1000
        shares = []
        for c in cats:
            part = g.loc[g[col].isna() if c is None else g[col] == c, "length_m"].sum() / 1000
            shares.append(f"{_de(100 * part / km, 0)} %" if km else "–")
        b = "**" if bold else ""
        return f"| {b}{name}{b} | {_de(len(g), 0)} | {_de(km, 1)} | " + " | ".join(shares) + " |"

    for name in sorted(bez.unique(), key=lambda n: (n == NO_DISTRICT, n)):
        lines.append(row(name, df[bez == name]))
    lines.append(row("gesamt", df, bold=True))
    return lines
