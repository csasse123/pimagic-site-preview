# Zoomed 16:10 crops of Craig's workflow GIF frames (1920x1080, written by build_assets2.py) for the two-click stepper.
# The Photoshop frames are cropped right of the census panel (its Gal. Lat line shows a known bug).
import os
from PIL import Image
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); IMG = os.path.join(HERE, "site/assets/img")
CROPS = {"wf_window": (287, 65, 1587, 877), "wf_mapped": (264, 104, 1630, 958), "wf_running": (544, 310, 1344, 810),
         "wf_astromagic": (1000, 380, 1900, 943), "wf_layers": (580, 60, 1920, 898), "wf_finished": (580, 60, 1920, 898)}
for n, b in CROPS.items():
    Image.open(os.path.join(HERE, "sources/craig_gif_frames", n + ".webp")).convert("RGB").crop(b).resize((1280, 800), Image.LANCZOS) \
        .save(os.path.join(IMG, n + "_z.webp"), quality=84, method=6)
print("ok")

# Stars layer with its own alpha (alpha = brightest channel, colour un-premultiplied) so it stacks over the nebula without blend modes
import numpy as np
s = np.asarray(Image.open(os.path.join(HERE, "sources/craig_gif_frames/el_stars_rgb.webp")).convert("RGB")).astype(np.float32) / 255
a = s.max(2, keepdims=True); rgb = np.where(a > 1e-3, s / np.maximum(a, 1e-3), 0)
Image.fromarray((np.concatenate([rgb, np.clip(a * 1.15, 0, 1)], 2) * 255).astype(np.uint8), "RGBA").save(os.path.join(IMG, "el_stars_a.webp"), quality=86, method=6)
# Craig's speed-run graphic and Pleiades layer graphic; the census block in the 2026 half is softened (its Gal. Lat line shows a known bug)
SRC = os.path.join(HERE, "sources/craig_elephant_2026-10-22")
sr = np.asarray(Image.open(os.path.join(SRC, "speedrun_2023_vs_2026.webp")).convert("RGB")).astype(np.float32)
from scipy.ndimage import median_filter, binary_dilation, gaussian_filter
y0, y1, x0, x1 = 1008, 1180, 826, 1000                                   # the census text block
blk = sr[y0:y1, x0:x1]; L = blk.mean(2); bg = median_filter(L, 9)
m = binary_dilation((L - bg > 9) & (L > 55), iterations=3)               # text strokes only; the dark frame lines stay
w = (~m).astype(np.float32); fill = np.stack([gaussian_filter(blk[..., c] * w, 6) / np.maximum(gaussian_filter(w, 6), 1e-3) for c in range(3)], 2)
blk[m] = fill[m]; sr[y0:y1, x0:x1] = blk
sr[y0:1088, 900:904] = 3; sr[1084:1088, 900:x1] = 3                      # Craig's frame lines, redrawn where the text crossed them
Image.fromarray(np.clip(sr, 0, 255).astype(np.uint8)).save(os.path.join(IMG, "speedrun.webp"), quality=84, method=6)
Image.open(os.path.join(SRC, "pleiades_layers_craig.webp")).convert("RGB").save(os.path.join(IMG, "pleiades_layers.webp"), quality=84, method=6)
print("stars alpha, speed run, pleiades layers ok")
