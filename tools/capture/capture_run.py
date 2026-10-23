# Time-lapse of a PiMagic run: every INTERVAL s, capture PixInsight's main window and the pipeline dialog by window id (other
# apps in front never show, and it works while PixInsight sits on another Space) and composite them, back to front, onto the main window's frame.  python3 capture_run.py OUT [INTERVAL]
import os, sys, time, subprocess, tempfile
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); out = sys.argv[1]; iv = float(sys.argv[2]) if len(sys.argv) > 2 else 3
os.makedirs(out, exist_ok=True); tmp = tempfile.mkdtemp(); n = 0; seen = False; t0 = time.time()
def wins():
    r = subprocess.run([os.path.join(HERE, "piwins"), "PixInsight", "all"], capture_output=True, text=True).stdout.strip().splitlines()
    return [(int(a), float(x), float(y), float(w), float(h), int(l), t) for a, x, y, w, h, l, t, *_ in (s.split("\t") + [""] for s in r) if int(l) == 0 and float(w) > 80 and float(h) > 80 and (t == "PixInsight" or "Integration Pipeline" in t)]   # main window + the pipeline dialog, wherever they are
while True:
  try:
      W = wins()
      if not W:
          if seen and time.time() - last > 120: break                       # PixInsight gone for 2 min: done
          if not seen and time.time() - t0 > 3600: break
          time.sleep(iv); continue
      seen = True; last = time.time()
      if os.path.exists(os.path.join(out, "STOP")): break
      main = next((v for v in W if v[6] == "PixInsight"), max(W, key=lambda v: v[3] * v[4])); X0, Y0, MW, MH = main[1], main[2], main[3], main[4]
      canvas = None; sc = 1
      for (i, x, y, w, h, l, t) in W:
          p = os.path.join(tmp, f"{i}.png")
          if subprocess.run(["screencapture", "-x", "-o", "-l", str(i), p]).returncode or not os.path.exists(p): continue
          im = Image.open(p).convert("RGB")
          if t != "PixInsight":                                              # a web-drawn dialog off-screen paints white: leave it out
              g = im.convert("L").crop((im.width // 8, im.height // 4, im.width * 7 // 8, im.height * 7 // 8)).resize((64, 64))
              px = list(g.get_flattened_data()) if hasattr(g, 'get_flattened_data') else list(g.getdata()); m = sum(px) / len(px)
              if m > 240 and max(px) - min(px) < 25: continue
          if canvas is None: sc = im.width / w; canvas = Image.new("RGB", (round(MW * sc), round(MH * sc)), (30, 32, 38))
          canvas.paste(im, (round((x - X0) * sc), round((y - Y0) * sc)))
      if canvas:
          canvas.save(os.path.join(out, f"f{n:05d}.jpg"), quality=88); n += 1
          open(os.path.join(out, "frames.txt"), "a").write(f"{n - 1}\t{time.time() - t0:.1f}\t{len(W)}\t{'|'.join(v[6][:40] for v in W)}\n")
      time.sleep(iv)
  except Exception as e:
    open(os.path.join(out, 'errors.txt'), 'a').write(repr(e) + '\n'); time.sleep(iv)
print("frames", n)
