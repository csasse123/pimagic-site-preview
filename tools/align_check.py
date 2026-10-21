# Find where PiMagic's cropped Final preview sits inside the linear stacked master (same run, same registration).
import numpy as np, sys
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
RUN = "/Volumes/4TB Astro2/PiMagic/Runs/PiMagic-Rosette_NGC2244-2026-10-19-21-41-46"
def xisf(path):
    import re, struct
    f = open(path, "rb"); h = f.read(16); n = struct.unpack("<I", h[8:12])[0]; x = f.read(n).decode()
    m = re.search(r'geometry="(\d+):(\d+):(\d+)".*?location="attachment:(\d+):(\d+)"', x)
    w, hgt, c, off, size = map(int, m.groups())
    return np.memmap(path, np.float32, "r", off, (c, hgt, w))[0]
M = xisf(RUN + "/masters/Rosette_NGC2244_stacked_Ha.xisf")
k = 8
def down(a): h, w = a.shape[0] // k * k, a.shape[1] // k * k; return a[:h, :w].reshape(h // k, k, w // k, k).mean((1, 3))
m = down(np.asarray(M)); m = np.arcsinh((m - np.median(m)) / (np.std(m) * 0.5))
F = np.asarray(Image.open(RUN + "/Previews/Final_Preview_Rosette_NGC2244_Ha.jpg").convert("L")).astype(np.float32)
f = down(F); f = (f - f.mean()) / f.std()
from scipy.signal import fftconvolve
def hp(a): from scipy.ndimage import gaussian_filter; return a - gaussian_filter(a, 6)
mm, ff = hp(m), hp(f)
c = fftconvolve(mm, ff[::-1, ::-1], mode="valid")
y, x = np.unravel_index(np.argmax(c), c.shape)
print("master", M.shape, "final", F.shape, "offset(px)", x * k, y * k, "peak/std", c.max() / c.std())
