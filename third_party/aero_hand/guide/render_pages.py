"""Render aero_guide_original.pdf to p1.png..pN.png (200 dpi). Pages are gitignored."""
import pathlib, fitz
here = pathlib.Path(__file__).parent
doc = fitz.open(here / "aero_guide_original.pdf")
for i, page in enumerate(doc, 1):
    page.get_pixmap(dpi=200).save(here / f"p{i}.png")
