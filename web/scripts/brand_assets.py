"""Create HMR logo brand assets for the web frontend (web/src/brand/).

Run from the repository root:
    uv run --with pillow --with fonttools --with brotli python web/scripts/brand_assets.py
"""
from __future__ import annotations

from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "assets/brand/hmr-logo-source.jpg"  # never modified
OUT = REPO / "web/src/brand"
WOFF2 = REPO / "web/src/fonts/InterVariable.woff2"
FONT_TMP = Path("/private/tmp/claude-501/-Users-raphael-Code-web-projects-SFP/"
                "07c4233a-74d1-45e3-9ee4-5b6fae121b87/scratchpad")
INK = (0x11, 0x11, 0x11)
WHITE = (255, 255, 255)
LANCZOS = Image.Resampling.LANCZOS


def load_letters() -> tuple[Image.Image, tuple[int, int, int, int]]:
    """Crop the grayscale source to the letters and map it to #111111 with alpha = darkness."""
    src = Image.open(SOURCE).convert("L")
    box = src.point(lambda v: 255 if v < 128 else 0).getbbox()
    gray = src.crop(box)
    # smooth threshold: 0-80 -> black, 200-255 -> white, linear in between
    lut = [round(min(255, max(0, (v - 80) * 255 / 120))) for v in range(256)]
    gray = gray.point(lut)
    rgba = Image.new("RGBA", gray.size, INK + (255,))
    rgba.putalpha(gray.point(lambda v: 255 - v))
    return rgba, box


def border_max_alpha(img: Image.Image, width: int = 2) -> int:
    alpha = img.getchannel("A")
    w, h = alpha.size
    return max(
        alpha.getpixel((x, y))
        for x in range(w) for y in range(h)
        if x < width or y < width or x >= w - width or y >= h - width
    )


def pad(img: Image.Image, p: int) -> Image.Image:
    out = Image.new("RGBA", (img.width + 2 * p, img.height + 2 * p), (0, 0, 0, 0))
    out.paste(img, (p, p))
    return out


def scale_to_letter_height(img: Image.Image, letter_h: int, target: int) -> Image.Image:
    s = target / letter_h
    return img.resize((round(img.width * s), round(img.height * s)), LANCZOS)


def square_icon(letters: Image.Image, size: int, width_ratio: float) -> Image.Image:
    w = round(size * width_ratio)
    h = round(letters.height * w / letters.width)
    canvas = Image.new("RGBA", (size, size), WHITE + (255,))
    canvas.alpha_composite(letters.resize((w, h), LANCZOS), ((size - w) // 2, (size - h) // 2))
    return canvas.convert("RGB")


def inter(size: int, weight: int, ttf: Path) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(ttf), size)
    axes = font.get_variation_axes()
    values = [weight if a["name"] in (b"Weight", "Weight") else a["default"] for a in axes]
    font.set_variation_by_axes(values)
    return font


def load_fonts() -> tuple[dict[str, ImageFont.FreeTypeFont], str]:
    """Return bold/regular fonts; fall back to Helvetica if the variable Inter cannot be set."""
    try:
        FONT_TMP.mkdir(parents=True, exist_ok=True)
        ttf = FONT_TMP / "InterVariable.ttf"
        font = TTFont(str(WOFF2))
        font.flavor = None
        font.save(ttf)
        return {
            "bold64": inter(64, 700, ttf), "reg36": inter(36, 400, ttf), "reg28": inter(28, 400, ttf),
        }, "Inter Variable"
    except Exception as exc:  # noqa: BLE001 - any failure triggers the documented fallback
        print(f"FALLBACK: Inter variable font not usable ({exc}); using Helvetica.ttc")
        hel = "/System/Library/Fonts/Helvetica.ttc"
        return {
            "bold64": ImageFont.truetype(hel, 64, index=1),
            "reg36": ImageFont.truetype(hel, 36, index=0),
            "reg28": ImageFont.truetype(hel, 28, index=0),
        }, "Helvetica"


def og_image(letters: Image.Image, fonts: dict[str, ImageFont.FreeTypeFont]) -> Image.Image:
    canvas = Image.new("RGBA", (1200, 630), WHITE + (255,))
    logo = scale_to_letter_height(letters, letters.height, 120)
    canvas.alpha_composite(logo, (80, 80))
    draw = ImageDraw.Draw(canvas)
    draw.text((80, 300), "Straßenfunktionsplan Hamburg", font=fonts["bold64"], fill=INK)
    draw.text((80, 392), "Entwurf · nicht amtlich", font=fonts["reg36"], fill=(0x4A, 0x4A, 0x4A))
    draw.text((80, 530), "Hamburg Mobility Revolution · hamburgmobility.de",
              font=fonts["reg28"], fill=(0x6B, 0x6B, 0x6B))
    return canvas.convert("RGB")


def save(img: Image.Image, name: str) -> None:
    img.save(OUT / name, optimize=True)
    print(f"wrote {OUT / name}  {img.width}x{img.height}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    letters, box = load_letters()
    h = letters.height
    p = round(0.25 * h)
    print(f"crop box (left, top, right, bottom): {box}  letters {letters.width}x{h}  pad {p}")
    print(f"max alpha, 2px border of letter crop: {border_max_alpha(letters)} (letters touch the crop edge)")
    padded = pad(letters, p)
    print(f"max alpha, 2px border of padded logo: {border_max_alpha(padded)} (must be 0)")

    logo1 = scale_to_letter_height(padded, h, 20)
    logo2 = scale_to_letter_height(padded, h, 40)
    for img, name in ((logo1, "hmr-logo.png"), (logo2, "hmr-logo@2x.png")):
        measured = img.getchannel("A").point(lambda v: 255 if v >= 128 else 0).getbbox()
        print(f"{name}: letter height {measured[3] - measured[1]} px")
        save(img, name)
    # header: letters only (spacing comes from the grid), letter height = title line height 28 px (1x and 2x)
    save(scale_to_letter_height(letters, h, 28), "hmr-header.png")
    save(scale_to_letter_height(letters, h, 56), "hmr-header@2x.png")

    save(square_icon(letters, 16, 0.8), "favicon-16.png")
    save(square_icon(letters, 32, 0.8), "favicon-32.png")
    save(square_icon(letters, 180, 0.7), "apple-touch-icon.png")

    fonts, font_name = load_fonts()
    print(f"og font: {font_name}")
    save(og_image(letters, fonts), "og-image.png")


if __name__ == "__main__":
    main()
