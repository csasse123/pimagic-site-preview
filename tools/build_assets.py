# Web assets for the PiMagic Studio site (2026 redesign). Everything shown is real: PiMagic outputs, the real run, Craig Stocks'
# UDRO time-lapse and data. Sources: ../hook-film (film masters, captures, assets) and the Rosette run in PiMagic/Runs.
#   python3 tools/build_assets.py [images] [video]
import glob, json, os, re, struct, subprocess, sys
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILM = os.path.join(os.path.dirname(HERE), "hook-film")
sys.path.insert(0, os.path.join(FILM, "tools"))
OUT_I = os.path.join(HERE, "site", "assets", "img"); OUT_V = os.path.join(HERE, "site", "assets", "video")
os.makedirs(OUT_I, exist_ok=True); os.makedirs(OUT_V, exist_ok=True)
RUN = "/Volumes/4TB Astro2/PiMagic/Runs/PiMagic-Rosette_NGC2244-2026-10-19-21-41-46"
what = sys.argv[1:] or ["images", "video"]

def save(im, name, maxside=None, q=82):
    if maxside: im = im.copy(); im.thumbnail((maxside, maxside), Image.LANCZOS)
    im.save(os.path.join(OUT_I, name + ".webp"), quality=q, method=6); return im.size

def present(im, lo=1.0, hi=99.97, s=0.10):                 # the film's presentation contrast for PiMagic outputs (render4.present)
    a = np.asarray(im).astype(np.float32); l = a.mean(-1)
    p0, p1 = np.percentile(l, lo), np.percentile(l, hi)
    x = np.clip((a - p0) / max(1.0, p1 - p0), 0, 1); x = np.clip(x + s * (x - 0.5) * (1 - np.abs(2 * x - 1)), 0, 1)
    return Image.fromarray((x * 255).astype(np.uint8))

def filled_crop(im, aspect=None):
    """largest centred box free of empty (black) mosaic canvas"""
    a = np.asarray(im.convert("L").resize((im.width // 8, im.height // 8))) > 6
    h, w = a.shape; best = (0, 0, w, h)
    for f in np.linspace(1.0, 0.4, 61):
        cw, ch = int(w * f), int(h * f)
        if aspect: ch = min(ch, int(cw / aspect)); cw = int(ch * aspect)
        x0, y0 = (w - cw) // 2, (h - ch) // 2
        if a[y0:y0 + ch, x0:x0 + cw].mean() > 0.999: best = (x0, y0, x0 + cw, y0 + ch); break
    return im.crop(tuple(v * 8 for v in best))

def xisf(path):
    f = open(path, "rb"); h = f.read(16); n = struct.unpack("<I", h[8:12])[0]; x = f.read(n).decode()
    m = re.search(r'geometry="(\d+):(\d+):(\d+)".*?location="attachment:(\d+):(\d+)"', x)
    w, hgt, c, off, _ = map(int, m.groups())
    return np.memmap(path, np.float32, "r", off, (c, hgt, w))[0]

meta = {}
if "images" in what:
    # 1 before/after: the run's own linear stacked H-alpha master vs PiMagic's finished SHO (Final is a crop of the master at 72,128 px)
    M = xisf(RUN + "/masters/Rosette_NGC2244_stacked_Ha.xisf")
    fin = Image.open(RUN + "/Previews/Final_Preview_Rosette_NGC2244_SHO.jpg").convert("RGB")
    W0, H0 = fin.size; ox, oy = 72, 128
    lin = np.asarray(M[oy:oy + H0, ox:ox + W0], dtype=np.float32)
    lo, hi = np.percentile(lin[::8, ::8], 1), np.percentile(lin[::8, ::8], 99.7)
    raw = np.clip((lin - lo) / (hi - lo), 0, 1) ** 0.75 * 0.62          # straight from the stack: dim, flat, grey (no colour work)
    rawim = Image.fromarray((np.repeat(raw[..., None], 3, -1) * 255).astype(np.uint8))
    box = (int(W0 * 0.12), int(H0 * 0.05), int(W0 * 0.88), int(H0 * 0.05) + int(W0 * 0.76 / 1.6))   # 16:10 on the nebula
    meta["ba"] = save(rawim.crop(box), "ba_rosette_raw", 2000); save(fin.crop(box), "ba_rosette_final", 2000)
    # 2 PiSolver: Orion mosaic, plain and annotated (same frame)
    box = (72, 120, 2720, 2240)   # filled_crop(orion, 1.25): the mosaic's empty canvas cut away, same box for both
    for n in ("orion", "orion_annot"):
        save(Image.open(os.path.join(FILM, "assets/final", n + ".jpg")).convert("RGB").crop(box), "solve_" + n, 2000)
    # 3 mosaic: six raw linear panes (as they come) + PiMagic's mosaic
    import render as R
    for i, p in enumerate(R.RHO): save(p, f"pane{i + 1}", 940)
    save(filled_crop(Image.open(os.path.join(FILM, "assets/final/rho.jpg")).convert("RGB"), 1.0), "mosaic_rho", 1800)
    # 4 the real window (Smart | Expert, files sorted) and the switch close-up
    import render5 as R5, render6 as R6
    win = Image.open(R5.FOLD[-1]).convert("RGB")
    save(win.crop(tuple(int(v) for v in R5.C_WIN)), "ui_window", 1800, 88)
    save(win.crop(tuple(int(v) for v in R5.C_MAP)), "ui_mapping", 1600, 88)
    # 5 gallery: real PiMagic outputs (presentation contrast as in the film), empty mosaic canvas cropped away
    G = [("pm/Final_Veil_for_Class_SHO", "Veil Nebula", "SHO narrowband"), ("pm/Final_Wizard_NGC7380_SHO", "Wizard Nebula", "SHO narrowband · mono"),
         ("pm/Final_Elephant_Trunk_SHO", "Elephant's Trunk", "SHO narrowband"), ("pm/Final_tarantulan_SHO", "Tarantula Nebula", "SHO narrowband"),
         ("run/SHO", "Rosette Nebula", "SHO · 146 raw files, one press of Start"), ("final/soul", "Soul Nebula", "mosaic"),
         ("pm/Final_Andromeda_RGB", "Andromeda Galaxy", "RGB"), ("pm/Final_M81_Bodes_Galaxy_RGB", "Bode's Galaxy", "LRGB · mono"),
         ("pm/Final_Dumbbell_OSC_RGB", "Dumbbell Nebula", "one-shot colour · large telescope"), ("pm/Final_M78_6200_RGB", "M78", "RGB · mono"),
         ("pm/Final_Pleiades_for_Me_RGB", "Pleiades", "one-shot colour"), ("pm/Final_Horsehead_for_John_DNBHO", "Horsehead Nebula", "one-shot colour + dual-band"),
         ("pm/Final_Comet_Pons_Brooks_for_Me_4_3_RGB", "Comet 12P/Pons-Brooks", "RGB"), ("pm/Final_Jem_Trailhead", "Milky Way nightscape", "mirrorless camera"),
         ("final/gunlock", "Gunlock panorama", "fisheye nightscape · 4 frames blended"), ("pm/fisheye", "All-sky", "fisheye lens"),
         ("final/m8", "M8", "Milky Way core"), ("final/heart", "Heart Nebula", "mosaic"), ("pm/Final_Lambs_Knoll_RGB", "Lambs Knoll", "nightscape")]
    gal = []
    for src, title, sub in G:
        if src.startswith("run/"):
            im = Image.open(RUN + "/Previews/Final_Preview_Rosette_NGC2244_SHO.jpg").convert("RGB"); im.thumbnail((3000, 3000))
        else:
            im = Image.open(os.path.join(FILM, "assets", src + ".jpg")).convert("RGB")
            if src.startswith("pm/") and "fisheye" not in src: im = present(im)
        if src in ("final/soul", "final/m8", "final/heart"): im = filled_crop(im)
        key = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
        size = save(im, "g_" + key, 1800); save(im, "g_" + key + "_t", 720)
        gal.append({"key": key, "title": title, "sub": sub, "w": size[0], "h": size[1]})
    meta["gallery"] = gal
    # 6 posters / social
    save(Image.open(os.path.join(FILM, "exports/thumbnail2_1920.jpg")).convert("RGB"), "poster_film", 1920, 86)
    og = Image.open(os.path.join(FILM, "exports/thumbnail2_1920.jpg")).convert("RGB").resize((1200, 675), Image.LANCZOS)
    og.crop((0, 22, 1200, 652)).save(os.path.join(OUT_I, "og.jpg"), quality=88)
    im = Image.open(os.path.join(FILM, "assets/craig/gunlock_ps.jpg")).convert("RGB"); save(im, "am_gunlock", 1800)   # Craig's finish of PiMagic's blend
    json.dump(meta, open(os.path.join(HERE, "site", "assets", "meta.json"), "w"), indent=1)
    print("images ok", len(gal))

def ff(*a): subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
if "video" in what:
    # hero: Craig's time-lapse, the big scopes slewing, a seamless 12 s loop (the tail crossfades into the head)
    TL = sorted(glob.glob(os.path.join(FILM, "capture/udro_timelapse/t*.jpg")))[288:288 + 312]
    Mx = 24; N = len(TL)
    tmp = os.path.join(OUT_V, "_hero"); os.makedirs(tmp, exist_ok=True)
    for k in range(N - Mx):
        a = Image.open(TL[k]).convert("RGB")
        if k < Mx: a = Image.blend(Image.open(TL[N - Mx + k]).convert("RGB"), a, k / Mx)
        a.resize((1920, 1080), Image.LANCZOS).save(os.path.join(tmp, f"f{k:04d}.jpg"), quality=92)
    for name, size, crf in (("hero_loop", "1920:1080", 27), ("hero_loop_m", "1280:720", 28)):
        ff("-framerate", "24", "-i", os.path.join(tmp, "f%04d.jpg"), "-vf", f"scale={size}", "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
           "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", os.path.join(OUT_V, name + ".mp4"))
    Image.open(os.path.join(tmp, "f0000.jpg")).save(os.path.join(OUT_I, "hero_poster.webp"), quality=80)
    subprocess.run(["rm", "-rf", tmp])
    # the films (16:9 masters, web encodes)
    for src, name, crf in (("PiMagic_Studio_SHORT_30s_1080p.mp4", "film_short", 23), ("PiMagic_Studio_LONG_75s_1080p.mp4", "film_long", 24)):
        ff("-i", os.path.join(FILM, "exports", src), "-map", "0:v:0", "-map", "0:a", "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", os.path.join(OUT_V, name + ".mp4"))
    # the real run, 15 minutes in 14 s, ending on its SHO
    ff("-framerate", "36", "-pattern_type", "glob", "-i", os.path.join(FILM, "capture/rosette_run/f*.jpg"), "-vf", "scale=1280:720", "-c:v", "libx264",
       "-preset", "slow", "-crf", "26", "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", os.path.join(OUT_V, "run_timelapse.mp4"))
    # PiSolver live on Craig's Witch Head JPEG
    ff("-framerate", "30", "-i", os.path.join(FILM, "capture/solver/clip_frames/c%04d.jpg"), "-vf", "scale=1280:720", "-c:v", "libx264", "-preset", "slow",
       "-crf", "25", "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", os.path.join(OUT_V, "pisolver_live.mp4"))
    print("video ok")
