# The recorded Elephant Trunk run as a fast time-lapse for the home page (Christian, 23 Oct 2026: "record the whole workflow ...
# do it in fast mode"). Frames: tools/capture/capture_run.py (PixInsight's main window by window id, 1 s). Steps and the clock
# come from the run's own log timestamps, under our names, in a strip under the window.
#   python3 tools/build_run_video.py FRAMES_DIR RUN_DIR  ->  site/assets/video/run_elephant.mp4 (+ poster, + run_elephant.json)
import os, re, sys, json, glob, subprocess, datetime as dt
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FR, RUN = sys.argv[1], sys.argv[2]
OUTV = os.path.join(HERE, "site/assets/video/run_elephant.mp4"); POSTER = os.path.join(HERE, "site/assets/img/run_elephant_poster.webp")
W, H, STRIP, FPS, SECS = 1920, 1080, 150, 30, 22

# ---- steps from the log (UTC stamps) -> seconds since the run started
log = open(sorted(glob.glob(os.path.join(RUN, "Logs", "Log_*.txt")))[-1], encoding="utf-8", errors="replace").read().splitlines()
ts = lambda l: dt.datetime.strptime(l[1:20], "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc).timestamp()
stamped = [(ts(l), l[22:]) for l in log if re.match(r"^\[\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\]", l)]
T0 = next(t for t, s in stamped if s.startswith("Step 1: Categorizing"))
FIL = {"R": "R", "G": "G", "B": "B", "Ha": "Hα", "OIII": "OIII", "SII": "SII", "Hydrogen": "Hα", "Oxygen": "OIII", "Sulfur": "SII",
       "Red": "R", "Green": "G", "Blue": "B"}
# every log event that names what is happening now (the per-channel steps repeat: the latest event wins)
EV = [(r"^Step 1: Categorizing", "Reading and sorting 49 files", 0), (r"^Step 1b", "Checking frame quality", 0),
      (r"^Step 2a", "Calibration masters matched", 0), (r"^Step 3: Calibrating", "Calibrating 37 light frames", 0),
      (r"^Step 5: Registration (\w+)", "Aligning {}", 1), (r"^Step 6: Stacking (\w+)", "Stacking {}", 1),
      (r"^PiSolver: Processing", "PiSolver · plate solve", 2), (r"Processing view: MasterLight_(\w+)", None, 2),
      (r"^=== Running GradientCorrection", "Gradient removal · {ch}", 2), (r"^=== Running Deblur", "Deblur · {ch}", 2),
      (r"^=== Applying Nuclear Stretch", "Stretch · {ch}", 2), (r"rc-astro --no-banner nxt", "Denoise · {ch}", 2),
      (r"^=== Applying Embedded Annotation", "Annotation · names and grid", 2), (r"^=== Running StarXTerminator", "Star separation · {ch}", 2),
      (r"^=== RGB Channel Combination", "RGB colour image", 3), (r"^=== SPCC", "Star Color Tuning · RGB", 3),
      (r"^=== HOO Channel Combination", "HOO colour image", 3), (r"^=== SHO Channel Combination", "SHO colour image", 3),
      (r"tag=starx_enter .*baseTag=Elephant_Trunk_(SHO|HOO|RGB)\b", "Star separation · {}", 3)]
PHASES = ["Calibrate", "Align & stack", "Process", "Colour", "Layers"]
events, ch = [], ""
for t, s in stamped:
    for rx, lab, ph in EV:
        m = re.search(rx, s)
        if not m: continue
        if lab is None: ch = FIL.get(m.group(1), m.group(1)); break
        if "{ch}" in lab and not ch: break
        if lab.startswith("RGB") or lab.startswith("Star Color"): ch = "RGB"
        if lab[:3] in ("HOO", "SHO"): ch = lab[:3]
        events.append((t - T0, lab.replace("{ch}", ch).replace("{}", FIL.get(m.group(1), m.group(1)) if m.groups() else ""), ph)); break
END = max(t for t, s in stamped) - T0
events.append((END - 5, "Layers saved for Photoshop", 4))
ph_start = [min(t for t, l, p in events if p == i) for i in range(5)]
def step_at(x):
    e = [v for v in events if v[0] <= x]; return e[-1] if e else events[0]

# ---- frames with their run time (capture times are wall-clock offsets from the first frame's file time)
rows = [l.split("\t") for l in open(os.path.join(FR, "frames.txt")).read().splitlines()]
f0 = os.path.getmtime(os.path.join(FR, "f00000.jpg")) - float(rows[0][1])
caps = [(os.path.join(FR, f"f{int(r[0]):05d}.jpg"), f0 + float(r[1]) - T0) for r in rows]
caps = [c for c in caps if -3 <= c[1] <= END + 6]
print("frames", len(caps), "run", round(END), "s", "events", len(events), "phases", [round(v) for v in ph_start])

F = "/System/Library/Fonts/SFNS.ttf" if os.path.exists("/System/Library/Fonts/SFNS.ttf") else "/System/Library/Fonts/Helvetica.ttc"
MONO = "/System/Library/Fonts/SFNSMono.ttf" if os.path.exists("/System/Library/Fonts/SFNSMono.ttf") else "/System/Library/Fonts/Menlo.ttc"
fBig, fMid, fSm = ImageFont.truetype(F, 46), ImageFont.truetype(MONO, 30), ImageFont.truetype(MONO, 19)
CY, VI, MI = (111, 211, 255), (169, 139, 255), (142, 240, 196)
ease_ = lambda v: (lambda c: c * c * (3 - 2 * c))(min(1, max(0, v)))
def window(path):
    im = Image.open(path).convert("RGB"); im = im.crop((0, round(im.height * 0.03), im.width, im.height))   # drop the title bar
    s = min(W / im.width, (H - STRIP) / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    c = Image.new("RGB", (W, H - STRIP), (30, 32, 38)); c.paste(im, ((W - im.width) // 2, (H - STRIP - im.height) // 2)); return c
def strip(x):
    t, label, ph = step_at(max(0, x)); s = Image.new("RGB", (W, STRIP), (6, 9, 16)); d = ImageDraw.Draw(s)
    if x > END: label = "Finished: SHO, HOO, RGB, Hα, OIII, SII + layers"
    m, sec = divmod(int(max(0, min(x, END))), 60)
    d.text((48, 24), label, font=fBig, fill=(240, 244, 250))
    d.text((48, 94), f"real time {m}:{sec:02d}  ·  unattended  ·  PiMagic · Elephant Trunk · SHO + RGB", font=fSm, fill=(150, 162, 184))
    x0, x1, gap = 1000, W - 48, 10; sw = (x1 - x0 - gap * 4) / 5          # five phases, each fills at its own pace
    for i, name in enumerate(PHASES):
        a, b = ph_start[i], (ph_start[i + 1] if i < 4 else END)
        f = 1 if x >= b else max(0, min(1, (x - a) / max(1, b - a))) if x >= a else 0
        X = x0 + i * (sw + gap); d.rounded_rectangle((X, 52, X + sw, 64), 6, fill=(34, 42, 60))
        if f > 0:
            col = tuple(int(CY[j] + (VI[j] - CY[j]) * i / 4) for j in range(3)); d.rounded_rectangle((X, 52, X + max(12, sw * f), 64), 6, fill=col)
        cur = a <= x < b or (i == 4 and x >= a)
        d.text((X, 86), name, font=fSm, fill=(240, 244, 250) if cur else (150, 162, 184) if x >= a else (70, 80, 100))
    if x >= END: d.text((x0, 8), "✓ finished — ready for Photoshop", font=fSm, fill=MI)
    return s

# ---- pacing: time on screen follows what there is to see. The linear RGB before colour calibration (green) and an empty
# desktop go by 4x faster; everything else at the same pace. Then the run's own finished SHO opens over the window.
def dull(path):
    a = np.asarray(Image.open(path).convert("RGB").resize((96, 48)), dtype=np.float32)[8:44, 8:80]
    r, g, b = a[..., 0].mean(), a[..., 1].mean(), a[..., 2].mean()
    return (g > 1.35 * r and g > 1.35 * b) or a.std() < 9
T = np.array([c[1] for c in caps]); wgt = np.array([0.25 if dull(c[0]) else 1.0 for c in caps])
print("dull frames", int((wgt < 1).sum()))
cum = np.concatenate([[0], np.cumsum(wgt[:-1] * np.diff(T))])            # "screen time" at each capture
N_RUN, N_END, lead = FPS * (SECS - 3), FPS * 3, int(FPS * 0.8)
fin = Image.open(next(p for p in (os.path.join(RUN, "Previews/Final_Preview_Elephant_Trunk_SHO.jpg"), os.path.join(RUN, "PiMagic/Previews/Final_Preview_Elephant_Trunk_SHO.jpg")) if os.path.exists(p))).convert("RGB")
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-c:v", "libx264", "-preset", "slow", "-crf", "23", "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUTV], stdin=subprocess.PIPE)
cache = {}
def win(i):
    if i not in cache:
        if len(cache) > 4: cache.pop(min(cache))
        cache[i] = np.asarray(window(caps[i][0]), dtype=np.float32)
    return cache[i]
last_good = max(i for i in range(len(caps)) if wgt[i] == 1 and caps[i][1] < END)   # the last frame with something on screen
for n in range(N_RUN + N_END):
    if n < N_RUN:
        u = 0 if n < lead else (n - lead) / (N_RUN - lead - 1) * cum[-1]
        j = int(np.searchsorted(cum, u)); j = min(max(j, 1), len(cum) - 1); a = (u - cum[j - 1]) / max(1e-6, cum[j] - cum[j - 1]); a = min(max(a, 0), 1)
        x = T[j - 1] + (T[j] - T[j - 1]) * a
        if x > caps[last_good][1]: j, a = last_good, 0                    # keep the last image up instead of the empty desktop
        top = win(j - 1) * (1 - a) + win(j) * a
    else:
        x = END + 1; k = ease_((n - N_RUN) / (N_END * 0.55))
        base = win(last_good); sz = (H - STRIP) * 0.86; im = fin.resize((round(sz * fin.width / fin.height), round(sz)), Image.LANCZOS)
        canvas = Image.fromarray(base.astype(np.uint8)); ov = Image.new("RGB", canvas.size, (12, 14, 20)); ov.paste(im, ((W - im.width) // 2, (H - STRIP - im.height) // 2))
        top = base * (1 - k) + np.asarray(ov, dtype=np.float32) * k
    frame = np.vstack([top, np.asarray(strip(x), dtype=np.float32)]).astype(np.uint8)
    ff.stdin.write(frame.tobytes())
    if n == N_RUN + N_END - 1: Image.fromarray(frame).save(POSTER, quality=82)
ff.stdin.close(); ff.wait()
json.dump({"real_seconds": round(END), "video_seconds": SECS, "phases": dict(zip(PHASES, [round(v) for v in ph_start]))},
          open(os.path.join(HERE, "site/assets/video/run_elephant.json"), "w"), indent=1)
print("video", OUTV, os.path.getsize(OUTV) // 1024, "KB")
