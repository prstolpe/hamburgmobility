"""Proposal (prompt 25, item 7): "HMR" rebuilt as SVG paths from the house font Inter (weight 800), for comparison with
the raster logo. Not used on the site without approval. Run: uv run --with fonttools --with brotli python web/scripts/brand_svg.py"""
from io import BytesIO
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "web" / "src" / "fonts" / "InterVariable.woff2"
OUT = ROOT / "web" / "src" / "brand" / "hmr-logo-inter.svg"
TEXT, WEIGHT, TRACKING = "HMR", 800, 0.04  # tracking as share of the em (the source logo is set slightly open)


def main() -> None:
    font = TTFont(SRC)
    font.flavor = None
    buf = BytesIO()
    font.save(buf)
    font = instantiateVariableFont(TTFont(BytesIO(buf.getvalue())), {"wght": WEIGHT, **({"opsz": 32} if any(
        a.axisTag == "opsz" for a in TTFont(BytesIO(buf.getvalue()))["fvar"].axes) else {})})
    glyphs, cmap, upm = font.getGlyphSet(), font.getBestCmap(), font["head"].unitsPerEm
    cap = font["OS/2"].sCapHeight
    pen, x = SVGPathPen(glyphs), 0
    for ch in TEXT:
        name = cmap[ord(ch)]
        glyphs[name].draw(TransformPen(pen, (1, 0, 0, -1, x, cap)))  # flip y, baseline at cap height
        x += glyphs[name].width + (TRACKING * upm if ch != TEXT[-1] else 0)
    # tight box: left side bearing of H and right bearing of R are small; keep the advance width
    OUT.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {round(x)} {cap}" role="img" aria-label="HMR">'
                   f'<path fill="#111111" d="{pen.getCommands()}"/></svg>\n')
    print(f"wrote {OUT} viewBox 0 0 {round(x)} {cap}, {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
