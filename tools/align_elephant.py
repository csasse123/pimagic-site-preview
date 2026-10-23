# Craig's finished Elephant Trunk (portrait, chat image 22 Oct 2026) -> PiMagic's Final SHO of the same data (landscape 9510x6299):
# try both 90-degree rotations, sweep the scale, FFT cross-correlation of high-passed luminance; refine at Craig's resolution.
import numpy as np, sys
from PIL import Image
from scipy.ndimage import gaussian_filter
from scipy.signal import fftconvolve
Image.MAX_IMAGE_PIXELS = None
P = "/Volumes/Masterclass/2026 Masterclass/Masterclass/Masterclass Targets from Workshop/Elephant Trunk-SHORGB/PiMagic-Elephant_Trunk-2026-09-27-14-02-08/PiMagic/Previews/Final_Preview_Elephant_Trunk_SHO.jpg"
C = sys.argv[1]
pim = Image.open(P).convert("L"); cim0 = Image.open(C).convert("L")
def hp(a, s1=1.0, s2=6): a = gaussian_filter(a, s1) - gaussian_filter(a, s2); return (a - a.mean()) / (a.std() + 1e-6)
best = None
for rot in (90, 270):
    cim = cim0.rotate(rot, expand=True)                       # Craig's frame turned back to landscape
    c = np.asarray(cim).astype(np.float32); ch, cw = c.shape
    t = hp(c)[int(ch * .15):int(ch * .85), int(cw * .15):int(cw * .85)]   # central part: no metadata text / logo
    for ppc in np.linspace(3.0, 9.0, 61):                     # PiMagic px per Craig px
        pw, ph = round(pim.width / ppc), round(pim.height / ppc)
        if pw < t.shape[1] or ph < t.shape[0]: continue
        p = hp(np.asarray(pim.resize((pw, ph), Image.BILINEAR)).astype(np.float32))
        r = fftconvolve(p, t[::-1, ::-1], mode="valid") / t.size
        i = np.unravel_index(np.argmax(r), r.shape)
        if best is None or r[i] > best[0]: best = (r[i], rot, ppc, i, (int(cw * .15), int(ch * .15)))
sc, rot, ppc, (yy, xx), (tx, ty) = best
print(f"coarse corr {sc:.3f} rot {rot} ppc {ppc:.3f}")
# refine scale finely around the coarse one
cim = cim0.rotate(rot, expand=True); c = np.asarray(cim).astype(np.float32); ch, cw = c.shape
t = hp(c)[int(ch * .15):int(ch * .85), int(cw * .15):int(cw * .85)]
best2 = None
for q in np.linspace(ppc - 0.12, ppc + 0.12, 25):
    pw, ph = round(pim.width / q), round(pim.height / q)
    p = hp(np.asarray(pim.resize((pw, ph), Image.LANCZOS)).astype(np.float32))
    r = fftconvolve(p, t[::-1, ::-1], mode="valid") / t.size
    i = np.unravel_index(np.argmax(r), r.shape)
    if best2 is None or r[i] > best2[0]: best2 = (r[i], q, i)
sc, q, (yy, xx) = best2
ox, oy = (xx - tx) * q, (yy - ty) * q                           # Craig (rotated) pixel (0,0) in PiMagic px
print(f"fine corr {sc:.3f} rot {rot} ppc {q:.4f} origin ({ox:.1f},{oy:.1f}) Craig-rotated size {cw}x{ch} covers {cw*q:.0f}x{ch*q:.0f}")
open("/Volumes/4TB Astro2/PiMagic/Marketing/website-2026/tools/elephant_fit.txt", "w").write(f"{rot} {q} {ox} {oy}\n")
