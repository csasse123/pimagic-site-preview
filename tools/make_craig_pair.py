# Aligned pair for the "PiMagic -> your creativity" slider: PiMagic's Rosette_2 SHO (as it comes out of the run) and Craig Stocks'
# Photoshop finish of that same file (Downloads/Rosette Final from CraIg, 21 Oct 2026). Fit from align_craig_refine.py.
import numpy as np, os
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
P = "/Volumes/LaCie4TB-1/M5-Archive-2026-09-21/PiMagic-Archive/runs-2026-09-06/PiMagic-Rosette_2-2026-09-05-10-32-43/PiMagic/Previews/Final_Preview_Rosette_2_SHO.jpg"
C = "/Users/christiansasse/Downloads/Rosette Final from CraIg/Starless_Rosette_2_SHO-Clean.jpg"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ppc, ox, oy = map(float, open(os.path.join(HERE, "tools/craig_fit.txt")).read().split())
pim = Image.open(P).convert("RGB"); cim = Image.open(C).convert("RGB")
m = 0.02                                                     # inset: stay clear of Craig's thin edge border
X0, Y0, X1, Y1 = pim.width * m, pim.height * m, pim.width * (1 - m), pim.height * (1 - m)
W = 1500; H = round(W * (Y1 - Y0) / (X1 - X0))
a = pim.resize((W, H), Image.LANCZOS, box=(X0, Y0, X1, Y1))
b = cim.resize((W, H), Image.LANCZOS, box=((X0 - ox) / ppc, (Y0 - oy) / ppc, (X1 - ox) / ppc, (Y1 - oy) / ppc))
out = os.path.join(HERE, "site/assets/img")
a.save(os.path.join(out, "ba2_rosette_pimagic.webp"), quality=84, method=6)
b.save(os.path.join(out, "ba2_rosette_craig.webp"), quality=84, method=6)
print(W, H)
# check: 1:1 Craig-resolution crops, left half PiMagic | right half Craig, around the centre
cx, cy = pim.width / 2, pim.height / 2; s = 300 * ppc
box = (cx - s, cy - s, cx + s, cy + s)
pa = pim.resize((600, 600), Image.LANCZOS, box=box)
pb = cim.resize((600, 600), Image.LANCZOS, box=((box[0] - ox) / ppc, (box[1] - oy) / ppc, (box[2] - ox) / ppc, (box[3] - oy) / ppc))
chk = pa.copy(); chk.paste(pb.crop((300, 0, 600, 600)), (300, 0))
chk.save("/private/tmp/claude-501/-Users-christiansasse/640917e7-8054-485c-b83f-d84516254406/scratchpad/craig_seam_check.jpg", quality=92)
