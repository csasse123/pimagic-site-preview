# Where Craig's Photoshop finish (2519x3000) sits in PiMagic's Rosette_2 Final SHO (9527x11380): scale + offset by FFT
# cross-correlation of high-passed luminance over a scale sweep.
import numpy as np, sys
from PIL import Image
from scipy.signal import fftconvolve
from scipy.ndimage import gaussian_filter
Image.MAX_IMAGE_PIXELS = None
P = "/Volumes/LaCie4TB-1/M5-Archive-2026-09-21/PiMagic-Archive/runs-2026-09-06/PiMagic-Rosette_2-2026-09-05-10-32-43/PiMagic/Previews/Final_Preview_Rosette_2_SHO.jpg"
C = "/Users/christiansasse/Downloads/Rosette Final from CraIg/Starless_Rosette_2_SHO-Clean.jpg"
def lum(im): return np.asarray(im.convert("L")).astype(np.float32)
def hp(a): a = a - gaussian_filter(a, 8); return (a - a.mean()) / (a.std() + 1e-6)
pim = Image.open(P); cim = Image.open(C)
k = 0.1                                   # work at 10 % of PiMagic's size
pw, ph = int(pim.width * k), int(pim.height * k)
p = hp(lum(pim.resize((pw, ph), Image.LANCZOS)))
best = None
for s in np.linspace(0.85, 1.15, 31):     # Craig's pixels per PiMagic pixel, relative to the plain size ratio
    cs = k * (11380 / 3000) / s           # Craig -> work scale
    cw, ch = int(cim.width * cs * 0.8), int(cim.height * cs * 0.8)   # central 80 % as the template
    c = lum(cim.resize((int(cim.width * cs), int(cim.height * cs)), Image.LANCZOS))
    y0, x0 = (c.shape[0] - ch) // 2, (c.shape[1] - cw) // 2
    t = hp(c[y0:y0 + ch, x0:x0 + cw])
    if t.shape[0] >= p.shape[0] or t.shape[1] >= p.shape[1]: continue
    r = fftconvolve(p, t[::-1, ::-1], mode="valid") / t.size
    i = np.unravel_index(np.argmax(r), r.shape)
    if best is None or r[i] > best[0]: best = (r[i], s, cs, i, x0, y0)
sc, s, cs, (yy, xx), x0, y0 = best
# Craig pixel (0,0) in PiMagic full-res pixels; PiMagic px per Craig px
ppc = 1 / cs * k
ox = (xx - x0) / k; oy = (yy - y0) / k
print(f"corr {sc:.3f}  scale(PiMagic px per Craig px) {ppc:.4f}  Craig(0,0) at PiMagic ({ox:.0f},{oy:.0f})  covers {cim.width*ppc:.0f}x{cim.height*ppc:.0f}")
