# Refine Craig's finish -> PiMagic Rosette_2 SHO: search scale and offset at 1/3.83 (Craig's own resolution) around the coarse fit.
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from scipy.signal import fftconvolve
Image.MAX_IMAGE_PIXELS = None
P = "/Volumes/LaCie4TB-1/M5-Archive-2026-09-21/PiMagic-Archive/runs-2026-09-06/PiMagic-Rosette_2-2026-09-05-10-32-43/PiMagic/Previews/Final_Preview_Rosette_2_SHO.jpg"
C = "/Users/christiansasse/Downloads/Rosette Final from CraIg/Starless_Rosette_2_SHO-Clean.jpg"
pim = Image.open(P).convert("L"); c = np.asarray(Image.open(C).convert("L")).astype(np.float32)
def hp(a): a = gaussian_filter(a, 1.0) - gaussian_filter(a, 6); return (a - a.mean()) / (a.std() + 1e-6)
ct = hp(c)[300:2700, 300:2200]            # central template in Craig pixels
best = None
for ppc in np.linspace(3.80, 3.86, 25):   # PiMagic px per Craig px
    pw, ph = round(pim.width / ppc), round(pim.height / ppc)
    p = hp(np.asarray(pim.resize((pw, ph), Image.LANCZOS)).astype(np.float32))
    r = fftconvolve(p, ct[::-1, ::-1], mode="valid") / ct.size
    i = np.unravel_index(np.argmax(r), r.shape)
    if best is None or r[i] > best[0]: best = (r[i], ppc, i)
sc, ppc, (yy, xx) = best
# template top-left (300,300) in Craig px sits at (xx,yy) in PiMagic/ppc px -> Craig origin in PiMagic px:
ox, oy = (xx - 300) * ppc, (yy - 300) * ppc
print(f"corr {sc:.3f} ppc {ppc:.4f} origin ({ox:.1f},{oy:.1f})")
open("/Volumes/4TB Astro2/PiMagic/Marketing/website-2026/tools/craig_fit.txt", "w").write(f"{ppc} {ox} {oy}\n")
