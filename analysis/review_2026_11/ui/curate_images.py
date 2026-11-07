"""Keep only the screenshots referenced in docs/review/2026-11/*.md in git, recompressed (max. 1100 px wide).

All other screenshots move to data/scenarios/review_ui/img_all (not in git), so the full sequence stays available.
Run after the report is written; it can run again after new screenshots.
"""

import re
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
DOCS = ROOT / "docs/review/2026-11"
IMG = DOCS / "img"
KEEP_ALL = ROOT / "data/scenarios/review_ui/img_all"
MAX_W = 1100
QUALITY = 70


def main() -> None:
    KEEP_ALL.mkdir(parents=True, exist_ok=True)
    refs = set()
    for md in DOCS.glob("*.md"):
        refs |= set(re.findall(r"\(img/([^)\s]+)\)", md.read_text()))
    missing = [r for r in refs if not (IMG / r).exists() and not (KEEP_ALL / r).exists()]
    if missing:
        raise SystemExit(f"referenced but missing: {missing}")
    moved = kept = 0
    for f in sorted(IMG.glob("*.jpg")):
        shutil.copy2(f, KEEP_ALL / f.name)  # full-size copy outside git
        if f.name not in refs:
            f.unlink()
            moved += 1
    for r in refs:
        src = KEEP_ALL / r
        im = Image.open(src).convert("RGB")
        if im.width > MAX_W:
            im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
        im.save(IMG / r, "JPEG", quality=QUALITY, optimize=True, progressive=True)
        kept += 1
    size = sum(f.stat().st_size for f in IMG.glob("*.jpg")) / 1e6
    print(f"kept {kept} referenced images ({size:.1f} MB), moved {moved} to {KEEP_ALL.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
