# Assets for the focused home page (Christian + Craig meeting, 22 Oct 2026):
#  - workflow steps from Craig's GIF (PIMagic---AstroMagic-Animation-copy.gif, real Windows screenshots, IC 405)
#  - Elephant Trunk journey, same pixels throughout, upright as Craig framed it: raw stacked Ha master (linear) -> PiMagic Final SHO
#    -> PiMagic's layers (Starless SHO = nebula, Stars RGB = true-colour stars, Annotation overlay, metadata) -> Craig Stocks' Photoshop finish
#  - Pleiades: Craig's PSD "Edit Sequence - Global Adjustments Only" (as opened with AstroMagic / after Levels, Color, Hue/Saturation)
import os, re, struct, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageSequence
from scipy.ndimage import gaussian_filter
from scipy.signal import fftconvolve
Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(HERE, "site/assets/img")
def save(im, name, q=82): im.save(os.path.join(OUT, name + ".webp"), quality=q, method=6); return im.size

# ---------------- 1 Craig's workflow frames
g = Image.open("/Users/christiansasse/Downloads/PIMagic---AstroMagic-Animation-copy.gif")
fr = [f.convert("RGB").copy() for f in ImageSequence.Iterator(g)]
for n, i in (("wf_window", 0), ("wf_mapped", 2), ("wf_running", 5), ("wf_astromagic", 7), ("wf_layers", 9), ("wf_finished", 12)):
    fr[i].save(os.path.join(HERE, "sources/craig_gif_frames", n + ".webp"), quality=80, method=6)   # full frames; build_wf_zoom.py crops them for the site

# ---------------- 2 Elephant Trunk
RUN = "/Volumes/Masterclass/2026 Masterclass/Masterclass/Masterclass Targets from Workshop/Elephant Trunk-SHORGB/PiMagic-Elephant_Trunk-2026-09-27-14-02-08"
rot, ppc, ox, oy = map(float, open(os.path.join(HERE, "tools/elephant_fit.txt")).read().split())
craig = Image.open(os.path.join(HERE, "sources/craig_elephant_2026-10-22/elephant_finish_craig.webp")).convert("RGB")
cw, ch = craig.rotate(rot, expand=True).size                              # Craig's frame in PiMagic orientation
box = (ox, oy, ox + cw * ppc, oy + ch * ppc)                               # ... in PiMagic pixels
fin = Image.open(RUN + "/PiMagic/Previews/Final_Preview_Elephant_Trunk_SHO.jpg").convert("RGB")
W0, H0 = fin.size
box = (max(0, box[0]), max(0, box[1]), min(W0, box[2]), min(H0, box[3]))
OW = 1100; OH = round(OW * (box[2] - box[0]) / (box[3] - box[1]))       # output: upright, OW wide
def upright(im, mode="RGB"):
    a = im.crop(tuple(round(v) for v in box)).rotate(-rot, expand=True)    # back to Craig's upright frame
    return a.resize((OW, round(OW * a.height / a.width)), Image.LANCZOS)
e_fin = upright(fin); print("elephant", e_fin.size)
save(e_fin, "el_pimagic")
for src, name in (("Starless_Elephant_Trunk_SHO.tif", "el_starless"), ("Stars_Elephant_Trunk_RGB.tif", "../../../sources/craig_gif_frames/el_stars_rgb"), ("Annotation_Overlay_Elephant_Trunk_Ha.tif", "el_annot")):
    im = Image.open(RUN + "/PiMagic/Images/" + src)
    im = im.convert("RGBA") if im.mode in ("RGBA", "LA") else im.convert("RGB")
    save(upright(im), name, 86)
# Craig's finish on the same box (his own crop, rotated back = identity on his image apart from the inset)
cb = ((box[0] - ox) / ppc, (box[1] - oy) / ppc, (box[2] - ox) / ppc, (box[3] - oy) / ppc)
cr = craig.rotate(rot, expand=True).crop(tuple(round(v) for v in cb)).rotate(-rot, expand=True).resize(e_fin.size, Image.LANCZOS)
save(cr, "el_craig", 86)
# raw: the stacked Ha master, linear; the Final is a crop of it - find the offset
def xisf(path):
    f = open(path, "rb"); h = f.read(16); n = struct.unpack("<I", h[8:12])[0]; x = f.read(n).decode()
    m = re.search(r'geometry="(\d+):(\d+):(\d+)".*?location="attachment:(\d+):(\d+)"', x)
    w, hgt, c, off, _ = map(int, m.groups()); return np.memmap(path, np.float32, "r", off, (c, hgt, w))[0]
M = xisf(RUN + "/masters/Elephant_Trunk_stacked_Ha.xisf")
k = 8
def down(a): h, w = a.shape[0] // k * k, a.shape[1] // k * k; return a[:h, :w].reshape(h // k, k, w // k, k).mean((1, 3))
def hp(a): a = a - gaussian_filter(a, 6); return (a - a.mean()) / (a.std() + 1e-6)
m8 = down(np.asarray(M)); m8 = np.arcsinh((m8 - np.median(m8)) / (np.std(m8) * 0.5))
f8 = down(np.asarray(Image.open(RUN + "/PiMagic/Previews/Final_Preview_Elephant_Trunk_Ha.jpg").convert("L")).astype(np.float32))
r = fftconvolve(hp(m8), hp(f8)[::-1, ::-1], mode="valid"); yy, xx = np.unravel_index(np.argmax(r), r.shape)
mx, my = xx * k, yy * k; print("Ha master", M.shape, "final at", mx, my, "peak", float(r.max() / r.std()))
lin = np.asarray(M[my:my + H0, mx:mx + W0], dtype=np.float32)
lo, hi = np.percentile(lin[::8, ::8], 1), np.percentile(lin[::8, ::8], 99.7)
raw = Image.fromarray((np.clip((lin - lo) / (hi - lo), 0, 1) ** 0.75 * 0.62 * 255).astype(np.uint8)).convert("RGB")
save(upright(raw), "el_raw")
# metadata panel (the run's ImageInfo text, as AstroMagic sets it, top left of the upright frame)
lines = open(RUN + "/PiMagic/Images/ImageInfo_Overlay_Elephant_Trunk.txt").read().strip().splitlines()
md = Image.new("RGBA", e_fin.size, (0, 0, 0, 0)); d = ImageDraw.Draw(md)
F = "/System/Library/Fonts/Helvetica.ttc"; ft = ImageFont.truetype(F, 26); fl = ImageFont.truetype(F, 14)
x, y = 26, 22
for i, s in enumerate(lines):
    f = ft if i == 0 else fl
    if i == 1: s = s.replace("  •  Ha", "\n Ha")                         # the long filter line wraps in a portrait frame
    for part in s.split("\n"):
        for dx, dy in ((1, 2), (2, 2)): d.text((x + dx, y + dy), part.strip(), font=f, fill=(0, 0, 0, 150))
        d.text((x, y), part.strip(), font=f, fill=(240, 242, 248, 235)); y += 34 if i == 0 else 19
save(md, "el_meta", 90)

# ---------------- 3 Pleiades (Craig's PSD) - before/after of his global adjustments, Photoshop window crops
try:
    from psd_tools import PSDImage
    psd = PSDImage.open("/Users/christiansasse/Downloads/Pleiades Edit Sequence - Global Adjustments Only.psd")
    L = [l.topil().convert("RGB") for l in psd]
    save(L[1], "pl_ps_opened", 84); save(L[2], "pl_ps_adjusted", 84)
except ImportError:
    print("psd-tools not here - run with the scratch venv for the Pleiades step")
json.dump({"elephant": list(e_fin.size), "box": box}, open(os.path.join(HERE, "site/assets/meta2.json"), "w"))
print("ok")
