# PiMagic's layers on the website (Christian, 21 Oct 2026: "we should also show the overlay - the annotation, the metadata").
# Step 1 (Rosette NGC2244 run, 19 Oct): full frame raw stack / Final SHO + PiMagic's own overlays as transparent layers:
#   Annotation_Overlay (names + grid), SkyMap_Overlay (inset), metadata = ImageInfo_Overlay text set like AstroMagic's metadata panel.
#   The Census overlay is left out: this run's census reads Gal. Lat -60 / ~835 galaxies for the Rosette (should be about -2) - a bug.
# Step 2 (Rosette_2 mosaic): Craig Stocks' three versions (clean / metadata / metadata + annotations), aligned to PiMagic's Final SHO.
import os, re, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(HERE, "site/assets/img")
RUN = "/Volumes/4TB Astro2/PiMagic/Runs/PiMagic-Rosette_NGC2244-2026-10-19-21-41-46"
def xisf(path):
    f = open(path, "rb"); h = f.read(16); n = struct.unpack("<I", h[8:12])[0]; x = f.read(n).decode()
    m = re.search(r'geometry="(\d+):(\d+):(\d+)".*?location="attachment:(\d+):(\d+)"', x)
    w, hgt, c, off, _ = map(int, m.groups()); return np.memmap(path, np.float32, "r", off, (c, hgt, w))[0]
def save(im, name, q=84): im.save(os.path.join(OUT, name + ".webp"), quality=q, method=6)

# ---------------- step 1: full frame
fin = Image.open(RUN + "/Previews/Final_Preview_Rosette_NGC2244_SHO.jpg").convert("RGB"); W0, H0 = fin.size
W = 2000; H = round(W * H0 / W0)
M = xisf(RUN + "/masters/Rosette_NGC2244_stacked_Ha.xisf"); ox, oy = 72, 128           # Final = crop of the master at (72,128)
lin = np.asarray(M[oy:oy + H0, ox:ox + W0], dtype=np.float32)
lo, hi = np.percentile(lin[::8, ::8], 1), np.percentile(lin[::8, ::8], 99.7)
raw = (np.clip((lin - lo) / (hi - lo), 0, 1) ** 0.75 * 0.62 * 255).astype(np.uint8)
save(Image.fromarray(raw).convert("RGB").resize((W, H), Image.LANCZOS), "l1_raw")
save(fin.resize((W, H), Image.LANCZOS), "l1_final")
for src, name in (("Annotation_Overlay_Rosette_NGC2244_Ha.tif", "l1_annot"), ("SkyMap_Overlay_Rosette_NGC2244_Ha.tif", "l1_skymap")):
    o = Image.open(RUN + "/PiMagic/Images/" + src).convert("RGBA").resize((W, H), Image.LANCZOS)
    save(o, name, 88)
# metadata panel: the run's ImageInfo text, top left, as AstroMagic sets it
lines = open(RUN + "/PiMagic/Images/ImageInfo_Overlay_Rosette_NGC2244.txt").read().strip().splitlines()
md = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(md)
F = "/System/Library/Fonts/Helvetica.ttc"; ft = ImageFont.truetype(F, 34); fl = ImageFont.truetype(F, 19)
x, y = 34, 30
for i, s in enumerate(lines):
    f = ft if i == 0 else fl
    for dx, dy in ((1, 2), (2, 2)): d.text((x + dx, y + dy), s, font=f, fill=(0, 0, 0, 150))
    d.text((x, y), s, font=f, fill=(240, 242, 248, 235)); y += 46 if i == 0 else 26
save(md, "l1_meta", 90)

# ---------------- step 2: Craig's three versions on the same box as PiMagic's Rosette_2 Final
P = "/Volumes/LaCie4TB-1/M5-Archive-2026-09-21/PiMagic-Archive/runs-2026-09-06/PiMagic-Rosette_2-2026-09-05-10-32-43/PiMagic/Previews/Final_Preview_Rosette_2_SHO.jpg"
CD = os.path.join(HERE, "sources/craig_rosette_2026-10-21/")
ppc, cox, coy = map(float, open(os.path.join(HERE, "tools/craig_fit.txt")).read().split())
pim = Image.open(P).convert("RGB")
X0, Y0, X1, Y1 = 14 * ppc + cox, 14 * ppc + coy, min(pim.width, 2504 * ppc + cox), min(pim.height, 2986 * ppc + coy)   # inside Craig's thin border
W2 = 1500; H2 = round(W2 * (Y1 - Y0) / (X1 - X0))
save(pim.resize((W2, H2), Image.LANCZOS, box=(X0, Y0, X1, Y1)), "ba2_rosette_pimagic")
cbox = ((X0 - cox) / ppc, (Y0 - coy) / ppc, (X1 - cox) / ppc, (Y1 - coy) / ppc)
for f, name in (("Starless_Rosette_2_SHO-Clean.jpg", "ba2_rosette_craig"), ("Starless_Rosette_2_SHO-with Metadata.jpg", "ba2_rosette_craig_meta"),
                ("Starless_Rosette_2_SHO-with Metadata and Annotations.jpg", "ba2_rosette_craig_annot")):
    save(Image.open(CD + f).convert("RGB").resize((W2, H2), Image.LANCZOS, box=cbox), name)
print("step1", W, H, "step2", W2, H2, "box", [round(v) for v in (X0, Y0, X1, Y1)])
