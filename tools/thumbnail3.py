# Thumbnail v3 (Christian, 21 Oct: never "PixInsight made simple" - astrophotography made simple, the creativity is yours). From v2: bold and readable at phone size - grey raw stack | glowing seam | vivid
# finished Rosette, "PiMagic Studio" + "PIXINSIGHT. MADE SIMPLE." in heavy type with a soft shadow.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import render as R
W, H = 1920, 1080
fin = R.cover(R.FINAL["rosette"], 0, 1.0, 1.0, (0.58, 0.5))
f = np.asarray(fin).astype(np.float32)
lum = f.mean(-1, keepdims=True); f = np.clip(lum + (f - lum) * 1.35, 0, 255); f = np.clip((f - 8) * 1.28, 0, 255)   # vivid for a small screen
raw = np.asarray(R.MEAN_IMG[24].resize((W, H), Image.LANCZOS)).astype(np.float32) * 1.1
x = np.linspace(0, 1, W)[None, :] * np.ones((H, 1)) + np.linspace(0.06, -0.06, H)[:, None]   # a slight diagonal seam
seam = 0.53
m = np.clip((x - seam) / 0.035 + 0.5, 0, 1)[..., None]
glow = (np.exp(-((x - seam) / 0.009) ** 2) * 0.75 + np.exp(-((x - seam) / 0.045) ** 2) * 0.35)[..., None] * np.array([150, 200, 255])
img = np.clip(raw * (1 - m) + f * m + glow, 0, 255)
shade = np.clip(1 - 0.35 * np.clip((0.5 - x) / 0.5, 0, 1), 0, 1)[..., None]
img = Image.fromarray((img * shade).astype(np.uint8))
img = R.vignette(img, 0.25)
def shadowed(s, x0, y0, size, face, color, spacing):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); R.text(sh, s, x0 + 4, y0 + 5, size=size, face=face, color=(0, 0, 0), anchor="lm", spacing=spacing)
    sh = sh.filter(ImageFilter.GaussianBlur(8)); img.paste(sh, (0, 0), sh)
    R.text(img, s, x0, y0, size=size, face=face, color=color, anchor="lm", spacing=spacing)
shadowed("PiMagic", 90, 330, 170, 2, (255, 255, 255), 2)
shadowed("Studio", 94, 490, 170, 2, (255, 255, 255), 2)
shadowed("ASTROPHOTOGRAPHY.", 98, 680, 64, 0, (130, 195, 255), 3)
shadowed("MADE SIMPLE.", 98, 762, 64, 0, (130, 195, 255), 3)
R.text(img, "THE CREATIVITY IS YOURS.", 100, 848, size=34, face=5, anchor="lm", spacing=6, color=(235, 240, 255))
R.text(img, "RAW", 98, 960, size=30, face=5, anchor="lm", spacing=8, color=(200, 200, 200))
R.text(img, "FINISHED", W - 90, 960, size=30, face=5, anchor="rm", spacing=8, color=(235, 240, 255))
img.save(os.path.join(R.ROOT, "exports/thumbnail3_1920.jpg"), quality=93)
img.resize((1280, 720), Image.LANCZOS).save(os.path.join(R.ROOT, "exports/thumbnail3_1280.jpg"), quality=92)
img.resize((320, 180), Image.LANCZOS).save("/tmp/claude-501/thumb3_small.jpg", quality=90)
print("ok")
