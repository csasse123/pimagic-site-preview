# Craig's Elephant Trunk pieces (23 Oct 2026, Downloads/"Elephant Trunk Pieces": Red-Sulfur, Green-Hydrogen, Blue-Oxygen, Stars,
# Annotations - JPEGs meant to be combined in Screen mode) -> web layers for the home page's simplified Photoshop.
import os
from PIL import Image
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SRC = os.path.join(HERE, "sources/craig_elephant_pieces_2026-10-23")
for n, out in (("Red-Sulfur", "ly_sii"), ("Green-Hydrogen", "ly_ha"), ("Blue-Oxygen", "ly_oiii"), ("Stars", "ly_stars"), ("Annotations", "ly_annot")):
    im = Image.open(os.path.join(SRC, n + ".jpg")).convert("RGB").resize((1152, 1440), Image.LANCZOS)
    im.save(os.path.join(HERE, "site/assets/img", out + ".webp"), quality=86, method=6)
    im.resize((72, 90), Image.LANCZOS).save(os.path.join(HERE, "site/assets/img", out + "_t.webp"), quality=80)
print("layers ok")
