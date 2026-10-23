# Sub-pages of the PiMagic Studio sandbox: details/, gallery/, tutorials/, testimonials/, shop/, contact/. Shared header + footer, same css/js as the home page.
# Content comes from the live WordPress site (REST API, 21 Oct 2026): 26 tutorial posts with their YouTube videos, the six
# testimonials verbatim, the EDD products (PiMagic Studio Version 3 = download 611, $119, PiSolver included).
#   python3 tools/build_pages.py
import html, os, re
SITE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "site")
LIVE = "https://pimagicstudio.com"
E = html.escape

def head(title, desc):
    return f"""<!doctype html>
<html lang="en" data-base="../">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<meta name="robots" content="noindex, nofollow"><!-- sandbox: remove at launch -->
<meta name="theme-color" content="#04060c">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../css/site.css?v=202610231400">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Ccircle cx='32' cy='32' r='30' fill='%2304060c'/%3E%3Cellipse cx='32' cy='32' rx='24' ry='9' fill='none' stroke='%236fd3ff' stroke-width='3' transform='rotate(-25 32 32)'/%3E%3Ccircle cx='32' cy='32' r='7' fill='%23a98bff'/%3E%3C/svg%3E">
</head>
<body class="sub">
<canvas id="stars" aria-hidden="true"></canvas><div class="nebula" aria-hidden="true"></div>
"""

LOGO = """<svg viewBox="0 0 64 64" aria-hidden="true"><ellipse cx="32" cy="32" rx="27" ry="10" fill="none" stroke="url(#lg)" stroke-width="3" transform="rotate(-25 32 32)"/><circle cx="32" cy="32" r="8" fill="url(#lg)"/><circle cx="54" cy="21" r="2.6" fill="#e7edf7"/><defs><linearGradient id="lg" x1="0" x2="1"><stop offset="0" stop-color="#6fd3ff"/><stop offset="1" stop-color="#a98bff"/></linearGradient></defs></svg>"""
def nav(active):
    items = [("../#start", "How it works", ""), ("../details/", "Details", "details"), ("../gallery/", "Gallery", "gallery"), ("../tutorials/", "Tutorials", "tutorials"),
             ("../testimonials/", "Testimonials", "testimonials"), ("../shop/", "Shop", "shop"), ("../contact/", "Contact", "contact")]
    links = "".join(f'<a href="{h}"{" aria-current=\"page\"" if k == active else ""}>{t}</a>' for h, t, k in items)
    return f"""<header class="pm-nav scrolled" id="top">
  <a class="pm-logo" href="../" aria-label="PiMagic Studio home">{LOGO}<span>PiMagic <b>Studio</b></span></a>
  <nav class="pm-menu" aria-label="Main">{links}</nav>
  <div class="pm-nav-cta"><a class="pm-login" href="{LIVE}/checkout/order-history/">Customer</a><a class="btn btn-sm btn-glow" href="../shop/">Get PiMagic 3.2</a>
  <button class="pm-burger" aria-label="Open menu" aria-expanded="false"><span></span><span></span></button></div>
</header>
"""
FOOT = f"""<footer class="pm-foot">
  <div class="wrap foot-grid">
    <div><a class="pm-logo" href="../"><svg viewBox="0 0 64 64" aria-hidden="true"><ellipse cx="32" cy="32" rx="27" ry="10" fill="none" stroke="#6fd3ff" stroke-width="3" transform="rotate(-25 32 32)"/><circle cx="32" cy="32" r="8" fill="#a98bff"/></svg><span>PiMagic <b>Studio</b></span></a>
      <p class="small">Astrophotography, made simple. The creativity is yours.<br>By Dr. Christian Sasse and Craig Stocks.</p></div>
    <nav class="small"><a href="../shop/">Shop</a><a href="../details/">Details</a><a href="../gallery/">Gallery</a><a href="../tutorials/">Tutorials</a><a href="../testimonials/">Testimonials</a><a href="../contact/">Contact</a><a href="https://www.facebook.com/profile.php?id=61585927683743">Facebook</a></nav>
    <p class="small">Images: Craig Stocks · Utah Desert Remote Observatories (<a href="https://utahdesertremote.com">utahdesertremote.com</a>) and real PiMagic results from our users' data.<br>© 2026 Dr. Christian Sasse and Craig Stocks · <a href="{LIVE}/privacy-policy/">Privacy</a> · <a href="{LIVE}/terms/">Terms</a></p>
  </div>
</footer>
<div class="modal" id="filmModal" hidden><div class="modal-in"><button class="modal-x" aria-label="Close">✕</button><video controls playsinline preload="none"></video></div></div>
<div class="modal" id="lightbox" hidden><div class="modal-in lb"><button class="modal-x" aria-label="Close">✕</button><img alt=""><p class="mono"></p></div></div>
<script src="../js/site.js?v=202610231400" defer></script>
</body>
</html>
"""
def page_hero(eyebrow, h1, lede, extra=""):
    return f"""<section class="page-hero"><div class="wrap reveal">
  <p class="eyebrow mono">{eyebrow}</p><h1>{h1}</h1><p class="lede">{lede}</p>{extra}
</div></section>
"""

# ------------------------------------------------------------------ tutorials (all 26 live posts are PiMagic 2 era: v=2)
TOPICS = [
  ("start", "Getting started", "Install PiMagic Studio and meet the workflow."),
  ("modes", "Smart & Expert mode", "Let PiMagic decide, or take control."),
  ("mosaic", "Mosaics & nightscapes", "Multi-pane mosaics and wide-field landscapes."),
  ("colour", "Colour", "Colour calibration and narrowband palettes."),
  ("layers", "AstroMagic: the layer structure", "Every group and layer AstroMagic builds in Photoshop, explained."),
  ("walk", "Walkthroughs by camera & filter", "Follow along from raw data to a finished image."),
  ("ps101", "Photoshop 101", "The Photoshop basics behind a non-destructive astro workflow."),
]
T = [  # (topic, title, youtube id, date, post slug, description)
  ("start", "Introduction to PiMagic Studio V2", "oV9ObVXRDPY", "2026-04-06", "introduction-to-pimagic-studio-v2", "The whole idea: PiMagic does the PixInsight work, AstroMagic sets up Photoshop for your creative finish."),
  ("start", "Installation (V2.2 for PixInsight 1.9.4)", "5Yk_vRFzyd4", "2026-06-07", "installation-3", "Installing V2.2: a streamlined interface and a much better deep-sky mosaic workflow."),
  ("start", "Installation (V2)", "PJfhtt3QLlo", "2026-04-06", "installation", "Installing through the PixInsight repository, step by step."),
  ("modes", "Smart Mode", "FV1ZQ3JVFYs", "2026-04-06", "smart-mode", "Smart mode knows the best settings for your kind of data. Load your files and start."),
  ("modes", "Expert Mode", "bxBqzyOlXw4", "2026-04-06", "expert-mode", "Open up every control and set the process and parameters yourself."),
  ("mosaic", "Mosaics", "dwVPENorFSY", "2026-04-07", "installation-2", "Mosaic processing with PiMagic and AstroMagic, from panes to a finished mosaic."),
  ("mosaic", "Nightscapes", "mmb9T0s3TUc", "2026-04-06", "nightscapes", "Processing a nightscape with PiMagic Studio and AstroMagic."),
  ("colour", "How Important are SPCC Settings?", "G12Ny35ZLKc", "2026-01-28", "how-important-are-spcc-settings", "Generic versus exact filter and sensor settings for colour calibration — tested."),
  ("colour", "Monochrome Narrowband Color Mapping", "tOVkoOCI0HM", "2026-04-06", "monochrome-narrowband-color-mapping", "Choosing a narrowband palette — SHO (Hubble) is AstroMagic's default."),
  ("layers", "AstroMagic Panel Overview", "TM3jfj0psJY", "2026-01-02", "astromagic-panel-overview", "The tools built into the AstroMagic panel for Photoshop."),
  ("layers", "AstroMagic Standard Layer Structure", "8r36oWO_5nY", "2026-01-02", "astromagic-standard-layer-structure", "The Photoshop layer structure AstroMagic creates for you."),
  ("layers", "Layer Groups", "YCUfd7zgOTw", "2026-04-06", "layer-groups", "The same layer structure in every image, so you always find your way around."),
  ("layers", "Global Adjustments", "PJK_hBoeXrY", "2026-04-06", "global-adjustments", "Brightness, contrast and colour for the whole image — without touching the stars."),
  ("layers", "Color Adjustments", "2xv7tY2Chys", "2026-04-06", "color-adjustments", "Every colour layer group shares one structure, so adjustments feel familiar."),
  ("layers", "Stars", "3QpG8jKmpBI", "2026-04-06", "stars", "Stars live in their own group: balance them against everything else."),
  ("layers", "Annotation Layers", "GL7a9DlGBA4", "2026-04-06", "annotation-layers", "The three annotation layers and how to fine-tune them."),
  ("layers", "Metadata Text Panel", "ylpB4B8FvHc", "2026-04-06", "metadata-text-panel", "Filters, integration time and more, in an editable metadata group."),
  ("walk", "One-Shot Color", "rTkf21V_ETI", "2026-01-02", "astromagic-one-shot-color", "A simple image from a one-shot colour camera, start to finish."),
  ("walk", "Dual-Narrowband", "65hFFslXmDI", "2026-01-02", "astromagic-dual-narrowband", "One-shot colour with a clear filter plus a dual-narrowband filter."),
  ("walk", "LRGB", "BTbZtp0AwME", "2026-01-02", "astromagic-lrgb", "A monochrome camera with a typical LRGB filter set."),
  ("walk", "SHO", "HaRSE1Gi7IU", "2026-01-02", "astromagic-sho", "SHO filters on a monochrome camera: a Hubble-palette image."),
  ("walk", "LRGB + Hα with Continuum Subtraction", "2CNh6D64DPk", "2026-01-02", "astromagic-lrgbha-continuum-subtraction", "LRGB plus Hα, with red continuum subtraction to clean up the Hα."),
  ("ps101", "The Photoshop Advantage", "DWEC38h3e0E", "2025-12-31", "the-photoshop-advantage", "Why Photoshop's tools are so useful for astro images."),
  ("ps101", "Workspace", "yAf7ZRzzXyE", "2026-01-01", "photoshop-101-workspace", "Organising the Photoshop workspace to fit your workflow."),
  ("ps101", "Layers and Groups", "-BXdf0hwBtc", "2026-01-01", "photoshop-101-layers-and-groups", "The two most fundamental features in Photoshop."),
  ("ps101", "Advanced Tools", "PR5OajddzKg", "2026-01-01", "photoshop-101-advanced-tools", "Blending modes, smart objects and more."),
]
def month(d): import datetime; return datetime.date.fromisoformat(d).strftime("%b %Y")
def tut_card(t, title, yt, d, slug, desc, v="2"):
    return f"""<article class="tut glass" data-topic="{t}" data-v="{v}">
  <button class="tut-thumb" data-yt="{yt}" aria-label="Play: {E(title)}"><img src="https://i.ytimg.com/vi/{yt}/hqdefault.jpg" alt="" loading="lazy"><span class="tut-play"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></span></button>
  <div class="tut-body"><p class="tut-meta mono"><span class="badge">PiMagic {v}</span>{month(d)}</p><h3>{E(title)}</h3><p>{E(desc)}</p>
  <a class="tut-link" href="{LIVE}/{slug}/">Read the post →</a></div>
</article>"""

def tutorials():
    chips = '<button class="on" data-t="all">All topics</button>' + "".join(f'<button data-t="{k}">{E(n)}</button>' for k, n, _ in TOPICS)
    sections = ""
    for k, n, sub in TOPICS:
        cards = "".join(tut_card(*x) for x in T if x[0] == k)
        sections += f'<section class="topic" id="t-{k}"><div class="topic-head"><h2>{E(n)}</h2><p>{E(sub)}</p></div><div class="tut-grid">{cards}</div></section>\n'
    body = page_hero("// learn", "Tutorials", "Short videos, organised by topic. Every one plays right here.")
    body += f"""<section class="sec sec-tight"><div class="wrap">
  <div class="new32 glass reveal">
    <div><p class="eyebrow mono">// new · PiMagic 3.2</p><h2>Start here</h2>
      <p>The 3.2 tutorial series is being recorded. Until then: the two films show 3.2 at work, and the steps on the right get you installed.</p>
      <div class="hero-cta"><button class="btn btn-glow" data-film="short"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>PiMagic in 30 s</button>
      <button class="btn btn-ghost" data-film="long"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>The 75-second tour</button></div></div>
    <ol class="install mono">
      <li><b>Add two repositories</b> in PixInsight (Resources › Manage Repositories):<code>https://pixinsight.pimagicstudio.com/pm3/</code><code>https://pixinsight.pimagicstudio.com/pisolver/</code></li>
      <li><b>Check for updates</b> and restart PixInsight.</li>
      <li><b>Enter your licence key</b> — switch to Expert mode for the Tools tab. The same key activates PiSolver.</li>
      <li><b>Install AstroMagic</b> from the Tools tab: Install Plugin, then Install Actions.</li>
    </ol>
  </div>
</div></section>
<section class="sec sec-tight"><div class="wrap" id="tutorials">
  <div class="tut-tools">
    <div class="chips" role="toolbar" aria-label="Topics"><!--PMS:CHIPS-->{chips}<!--/PMS:CHIPS--></div>
    <div class="tut-row"><label class="search"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></svg><input id="tq" type="search" placeholder="Search tutorials"></label>
      <label class="toggle mono"><input id="archive" type="checkbox" checked><span></span>Show PiMagic 2 archive</label>
      <span class="count mono"><b id="tcount">26</b> videos</span></div>
    <p class="archive-note small">These videos were recorded with PiMagic Studio 2 and are kept as an archive. The PixInsight window looks different in 3.2.</p>
  </div>
  <!--PMS:TUT-->{sections}<!--/PMS:TUT-->
  <div class="tut-empty glass" id="tempty" hidden><h3>PiMagic 3.2 tutorials are on their way</h3><p>They are being recorded now. Meanwhile, switch the PiMagic 2 archive back on to browse the earlier videos.</p></div>
</div></section>
"""
    return head("Tutorials — PiMagic Studio", "PiMagic Studio tutorials by topic: installation, Smart and Expert mode, mosaics, colour, AstroMagic for Photoshop, walkthroughs and Photoshop 101.") + nav("tutorials") + "<main>" + body + "</main>" + FOOT

# ------------------------------------------------------------------ testimonials (verbatim from the live page)
Q = [
  ("Julian Segal", "A Game Changer in Image Processing", "in mere minutes, I produced stunning results that would have otherwise demanded years of trial and error.",
   "PiMagic and AstroMagic are the closest you’ll get to experiencing true time travel. I’ve always dreamed of diving into astrophotography, but life got in the way—I had to wait until retirement in my late 60s to finally dedicate the time to a craft that typically takes years to master. It felt like scaling an insurmountable mountain, and I hesitated at the base. That all changed when I had the fortunate chance to be among the first to try PiMagic and AstroMagic. For the first time, I felt like I’d bent time itself: in mere minutes, I produced stunning results that would have otherwise demanded years of trial and error. There’s genuine magic in these tools—they’ve turned my distant dream into an immediate reality."),
  ("Mark Killion", "Improved my Final Images Immeasurably", "It has sped up my post processing by magnitudes and improved my final images immeasurably.",
   "I am so glad Dr. Christian Sasse and Craig Stocks developed PiMagic and AstroMagic. It has sped up my post processing by magnitudes and improved my final images immeasurably. I can now run PiMagic using various parameters to see which ones work the best without having to go through each of these steps individually with PixInsight. The final stretched starless image is exceptional without destroying faint details. The star field produced is wonderful too. AstroMagic is great in the way it creates Grouped Layers automatically in Photoshop and has helped me since I would tend to skip a process to get to the final result. I am sure we all are guilty of some destructive editing at some point in our post processing and AstroMagic is the governor against that. I am just delighted with this new software and will use it from now on in my post processing workflow."),
  ("Matt Shetzer", "Highly Recommended for Astrophotographers", "PiMagic replaces years of training and experimentation with PixInsight and creates a structured workflow with just a few clicks.",
   "PiMagic replaces years of training and experimentation with PixInsight and creates a structured workflow with just a few clicks. Whether you are an astrophotography beginner, or an old pro, this tool simplifies the process and creates outstanding results. With the addition of the Photoshop Plugin, you now have the option to fine tune with PixInsight or move to Photoshop for final adjustments. Create the perfect image and print it BIG!"),
  ("Paul Brandenburg", "Brings the Fun Back to Astrophotography", "For me, this has truly brought back the fun of astro imaging and processing.",
   "I had the privilege of attending the first Utah Masterclass, where Dr. Christian Sasse and Craig Stocks presented their integrated astro-imaging workflow using PixInsight and Photoshop. I was amazed by the image quality achievable through their standardized, step-by-step manual approach.\n\nThe automation introduced by PiMagic and AstroMagic elevates this process even further by making it easy to quickly select input images and define the PixInsight processing steps and parameters to apply. Once this simple and intuitive setup is complete, the workflow runs unattended, producing fully processed images. This has been a tremendous time-saver and lets me devote my energy to refining the final results in Photoshop with AstroMagic. The plugin works seamlessly with output from PixInsight, creating a complete image-processing environment that makes it fast and efficient to produce a finished image.\n\nFor me, this has truly brought back the fun of astro imaging and processing."),
  ("Hawk Wolinski (astrohawk)", "Transformative Tools for Astrophotography", "Pixinsight can be a giant pain. I’m sure you all agree. Well PI magic changes all of that.",
   "I’ve known Christian Sasse for many years now. His partnership with ITelescope and Star Pix are changing the Astro photography landscape. Just when you think there’s nothing left for him to come up with he proves you wrong. PI magic for Pixinsight and Astro Magic for Photoshop are his two latest breakthroughs. And they are breakthroughs. I’ve been using Pixinsight and Photoshop for way over a decade and although I can get around Photoshop, Pixinsight can be a giant pain. I’m sure you all agree. Well PI magic changes all of that. After you do your stacking in weighted batch pre-processing you just run your master frames through PI magic and you’re ready to dump everything perfectly into Photoshop. And then when you go to Photoshop, you don’t have to spend 20 minutes grouping everything (a new trend in processing) Astro magic for Photoshop does it for you. It allows you to be creative right out of the gate. In Pixinsight, it does everything you need to prepare your masters, including changing them all into the TIFF files. I’m sure you’re going to enjoy this as much as I do. But the real question is what are you going to do with all the time you save?"),
  ("Josep Drudis", "Exceptional Software for All Levels", "Probably one of the greatest contributions to processing since RC-Astro’s AI tools!!",
   "Processing astrophotos is both tedious and creative. Christian’s script followed by his PS plug-in prepares everything after the pre-processing and allows the astrophotographer to focus only in the creative phases of the processing (usually only a few touch-ups are left…). Probably one of the greatest contributions to processing since RC-Astro’s AI tools!!"),
]
BG = ["g_veil_nebula", "g_wizard_nebula", "g_elephant_s_trunk", "g_tarantula_nebula", "g_andromeda_galaxy", "g_soul_nebula"]
def testimonials():
    feat = Q[0]
    cards = ""
    for i, (who, title, pull, full) in enumerate(Q):
        ini = "".join(w[0] for w in who.replace("(astrohawk)", "").split()[:2])
        paras = "".join(f"<p>{E(p)}</p>" for p in full.split("\n\n"))
        long = len(full) > 420
        cards += f"""<article class="tq glass reveal{' long' if long else ''}">
  <div class="tq-img" style="background-image:url(../assets/img/{BG[i]}_t.webp)"></div>
  <p class="stars-5" aria-label="5 out of 5 stars">★★★★★</p><h3>{E(title)}</h3>{f'<blockquote class="tq-pull">“{E(pull)}”</blockquote>' if long else ''}
  <div class="tq-full{'' if long else ' tq-short'}">{paras}</div>{'<button class="more link-arrow">Read the full story</button>' if long else ''}
  <p class="tq-who"><span class="ava">{E(ini)}</span><b>{E(who)}</b></p>
</article>"""
    body = page_hero("// astrophotographers on PiMagic", "Real users,<br><span class=\"grad\">real results</span>",
                     "Beginners and decades-long PixInsight users, in their own words.")
    body += f"""<section class="sec sec-tight"><div class="wrap">
  <figure class="feature-quote glass reveal">
    <img src="../assets/img/g_veil_nebula.webp" alt="" loading="lazy">
    <blockquote>“{E(feat[2][0].upper() + feat[2][1:])}”<cite class="mono">{E(feat[0])}</cite></blockquote>
  </figure>
  <div class="tq-grid">{cards}</div>
  <div class="cta-band glass reveal"><div><h2>Your turn</h2><p>We take away the hard work. The creativity is yours.</p></div>
    <div class="hero-cta"><a class="btn btn-glow" href="../shop/">Get PiMagic 3.2</a><a class="btn btn-ghost" href="../contact/">Share your story</a></div></div>
</div></section>
"""
    return head("Testimonials — PiMagic Studio", "What astrophotographers say about PiMagic Studio and AstroMagic.") + nav("testimonials") + "<main>" + body + "</main>" + FOOT

# ------------------------------------------------------------------ shop (EDD products on the live site)
def shop():
    body = page_hero("// shop", "Get<br><span class=\"grad\">PiMagic Studio 3</span>", "Astrophotography, made simple: the routine processing done for you, from a folder of raw frames to finished images — so your time goes into the creative part. One licence.")
    body += f"""<section class="sec sec-tight"><div class="wrap">
  <div class="plans">
    <article class="plan plan-main glass reveal">
      <p class="mono price-k">PiMagic Studio 3 · current version 3.2</p>
      <p class="price-v"><span>$</span>119</p><p class="price-s">One licence · Mac, Windows, Linux · plus applicable tax</p>
      <ul class="ticks">
        <li><b>PiMagic for PixInsight</b> — the complete workflow, from calibration to finished images. Smart and Expert mode.</li>
        <li><b>PiSolver</b> — our blind solver and annotator, also as a stand-alone PixInsight process</li>
        <li><b>AstroMagic for Photoshop</b> — your results loaded and organised into layer groups</li>
        <li>Deep sky, nightscapes and mosaics · DSLR, mirrorless, one-shot colour, mono, smart telescopes</li>
        <li>Calibration library · every filter and palette · 16-bit TIFF and JPEG output</li>
      </ul>
      <a class="btn btn-glow btn-block" href="{LIVE}/downloads/pimagic-studio-version-3/">Buy PiMagic Studio 3</a>
      <p class="price-f">Secure checkout on pimagicstudio.com · instant download · licence key by email</p>
    </article>
    <div class="plan-side">
      <article class="plan glass reveal">
        <p class="mono price-k">Already a customer?</p>
        <ul class="links">
          <li><a href="{LIVE}/checkout/order-history/">Order history &amp; licence keys →</a></li>
          <li><a href="{LIVE}/downloads/pimagic-studio-download-only/">Download only (update with an existing licence) →</a></li>
          <li><a href="{LIVE}/downloads/pimagic-studio-documentation/">Installation guide &amp; manuals →</a></li>
        </ul>
      </article>
    </div>
  </div>
</div></section>

<section class="sec sec-tight"><div class="wrap">
  <div class="sec-head reveal"><p class="eyebrow mono">// what you get</p><h2>Three tools, one workflow</h2></div>
  <div class="trio">
    <article class="card glass reveal"><i class="ic">◎</i><h3>PiMagic for PixInsight</h3><p>Select a folder: it sorts every file, calibrates, stacks, solves, removes gradients, tunes star colour, deblurs, denoises and separates stars — then writes finished images and layered TIFFs.</p></article>
    <article class="card glass reveal"><i class="ic">✶</i><h3>PiSolver</h3><p>A blind solver that needs no target, scope or camera information. Works on any file type, linear or not. Generates annotated images or transparent overlays.</p></article>
    <article class="card glass reveal"><i class="ic">▣</i><h3>AstroMagic for Photoshop</h3><p>Loads every result and builds the same familiar layer groups for each image, with non-destructive adjustment layers ready for your creative finish.</p></article>
  </div>
</div></section>

<section class="sec sec-tight"><div class="wrap install-grid">
  <div class="reveal"><p class="eyebrow mono">// after you order</p><h2>Up and running in minutes</h2>
    <p>You receive an email from info@pimagicstudio.com with your licence key, receipt and download information. Nothing arrived? Check your spam folder.</p>
    <a class="link-arrow" href="../tutorials/">Watch the tutorials →</a></div>
  <ol class="install mono glass reveal">
    <li><b>Add two repositories</b> in PixInsight (Resources › Manage Repositories):<code>https://pixinsight.pimagicstudio.com/pm3/</code><code>https://pixinsight.pimagicstudio.com/pisolver/</code></li>
    <li><b>Check for updates</b> and restart PixInsight.</li>
    <li><b>Enter your licence key</b> — Expert mode opens the Tools tab. The same key activates PiSolver.</li>
    <li><b>Install AstroMagic</b> from the Tools tab: Install Plugin, then Install Actions.</li>
    <li><b>Mac:</b> also install the free RC-Astro command-line tool (it does not use a licence seat).</li>
  </ol>
</div></section>

<section class="sec sec-tight" id="faq"><div class="wrap"><div class="faq">
  <div class="sec-head reveal"><p class="eyebrow mono">// questions</p><h2>Before you buy</h2></div>
  <details class="glass"><summary>What do I need?</summary><p>PixInsight 1.9.5 on Mac, Windows or Linux. RC-Astro's BlurXTerminator, NoiseXTerminator and StarXTerminator are used when installed. Photoshop only for AstroMagic — PiMagic's TIFF and JPEG results open in just about any image editor.</p></details>
  <details class="glass"><summary>The download or licence activation is blocked.</summary><p>By far the most common cause is a firewall or antivirus program. Pause both briefly to complete the installation.</p></details>
  <details class="glass"><summary>Do I need my own stacking software?</summary><p>No. Select the folder with your lights, flats, darks and bias — it calibrates and stacks for you. You can also keep a calibration library and let PiMagic pick the matching masters.</p></details>
  <details class="glass"><summary>Which cameras work?</summary><p>Mono and one-shot-colour astro cameras, DSLRs and mirrorless cameras, smart telescopes and fisheye lenses — deep sky, nightscapes and mosaics.</p></details>
</div></div></section>
"""
    return head("Shop — PiMagic Studio", "Buy PiMagic Studio 3: PiMagic for PixInsight, PiSolver and AstroMagic for Photoshop.") + nav("shop") + "<main>" + body + "</main>" + FOOT


# ------------------------------------------------------------------ contact (WP: the WPForms form #63 replaces the mailto form)
def contact():
    body = page_hero("// contact", "<span class=\"grad\">Let's talk</span>", "Questions before you buy, help with an installation, an idea for PiMagic — Christian and Craig read every message.")
    body += f"""<section class="sec sec-tight"><div class="wrap contact-grid">
  <form class="cform glass reveal" id="cform" action="mailto:info@pimagicstudio.com" method="post" enctype="text/plain">
    <div class="row2"><label>First name<input name="first" required autocomplete="given-name"></label><label>Last name<input name="last" autocomplete="family-name"></label></div>
    <label>Email<input type="email" name="email" required autocomplete="email"></label>
    <label>Topic<select name="topic"><option>A question before buying</option><option>Installation or licence</option><option>Help with my data or a result</option><option>An idea or feature request</option><option>Something else</option></select></label>
    <label>Message<textarea name="message" rows="6" required></textarea></label>
    <button class="btn btn-glow btn-block" type="submit">Send message</button>
    <p class="small">Opens your email app, addressed to info@pimagicstudio.com.</p>
  </form>
  <div class="contact-side">
    <article class="card glass reveal"><i class="ic">✉</i><h3>Email us directly</h3><p><a class="link-arrow" href="mailto:info@pimagicstudio.com">info@pimagicstudio.com</a></p></article>
    <article class="card glass reveal"><i class="ic">▶</i><h3>Quick answers</h3><ul class="links">
      <li><a href="../tutorials/">Tutorials, by topic →</a></li><li><a href="../shop/#faq">Installation &amp; licence FAQ →</a></li>
      <li><a href="{LIVE}/checkout/order-history/">Order history &amp; licence keys →</a></li></ul></article>
    <article class="card glass reveal"><i class="ic">✦</i><h3>Your order</h3><p>Download, installation information and your receipt arrive by email right after checkout, from info@pimagicstudio.com. Nothing there? Please check your spam folder.</p></article>
  </div>
</div></section>
"""
    return head("Contact — PiMagic Studio", "Contact PiMagic Studio: questions, installation help, ideas.") + nav("contact") + "<main>" + body + "</main>" + FOOT

# ------------------------------------------------------------------ details (everything the focused home page leaves out; body in tools/pages/details_body.html)
CTA = """<section class="sec sec-tight"><div class="wrap"><div class="cta-band glass reveal"><div><h2>Two clicks, then it's yours</h2><p>Select a folder, press Start. The creativity is yours.</p></div>
  <div class="hero-cta"><a class="btn btn-glow" href="../shop/">Get PiMagic 3.2 <small>$119</small></a><a class="btn btn-ghost" href="../gallery/">See the gallery</a></div></div></div></section>
"""
DTABS = (("overview", "Overview"), ("features", "Features"), ("result", "Layers"), ("engine", "Engine"), ("pisolver", "PiSolver"),
         ("cameras", "Cameras"), ("astromagic", "AstroMagic"), ("faq", "FAQ"))
OVERVIEW = (("features", "Features", "Calibration, every filter and palette, gradients, deblur, denoise, star separation"),
            ("result", "Layers", "PiMagic's layers on the Rosette, and Craig's Photoshop finish of it"),
            ("engine", "Engine", "Every routine step, one button"),
            ("pisolver", "PiSolver", "Our blind solver: any image, linear or stretched, named and annotated"),
            ("cameras", "Cameras", "From a fisheye lens to a deep-sky telescope"),
            ("astromagic", "AstroMagic", "The auto-loader for Photoshop: layers and groups built for you"),
            ("faq", "FAQ", "Requirements, installation, your order"))
def details():
    # a menu that stays put: it starts the page, "Overview" first; each section opens as a block under it
    # (Craig, 23 Oct 2026: "each section just opens as a block ... keep the menu available"; then: Overview button, eight in all)
    body_src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pages/details_body.html")).read()
    panels = {}
    for chunk in re.split(r"(?=<!-- ============)", body_src):
        m = re.search(r'<section[^>]*\bid="(\w+)"', chunk)
        if m: panels[m.group(1)] = chunk
    tiles = "".join(f'<button class="ov-tile glass" data-goto="{k}"><b>{t}</b><span>{E(d)}</span><i>→</i></button>' for k, t, d in OVERVIEW)
    panels["overview"] = f'''<section class="sec sec-tight" id="overview"><div class="wrap">
  <p class="eyebrow mono">// more details</p><h1 class="ov-h1"><span class="grad">Everything inside</span></h1>
  <p class="lede">Workflow automation for PixInsight, with an auto-loader for Photoshop. The home page is two clicks — this is what happens inside them, and what you get to play with afterwards.</p>
  <div class="hero-cta"><a class="btn btn-glow" href="../shop/">Get PiMagic 3.2 <small>$119</small></a></div>
  <div class="ov-grid">{tiles}</div>
</div></section>
'''
    assert set(panels) == {k for k, _ in DTABS}, sorted(panels)
    tabs = "".join(f'<button role="tab" id="tb-{k}" aria-controls="{k}" aria-selected="{str(i == 0).lower()}" data-tab="{k}">{t}</button>' for i, (k, t) in enumerate(DTABS))
    body = f'<nav class="dtab-nav dtab-top" aria-label="Details sections"><div class="wrap" role="tablist">{tabs}</div></nav>\n<div class="dtabs" id="dtabs">'
    body += "".join(f'<div class="dtab-panel" role="tabpanel" aria-labelledby="tb-{k}"{"" if i == 0 else " hidden"}>{panels[k]}</div>' for i, (k, _) in enumerate(DTABS))
    body += "</div>" + CTA
    return head("Details — PiMagic Studio", "Everything inside PiMagic Studio: automatic calibration, any filter and palette, mosaics, PiSolver, Star Color Tuning, layers, AstroMagic for Photoshop.") + nav("details") + "<main>" + body + "</main>" + FOOT

# ------------------------------------------------------------------ gallery (tiles come from site.js, one masonry per section)
GSECS = [("mosaics", "Mosaics & panoramas", "Deep-sky mosaics and landscape panoramas, every pane found, placed, matched and blended."),
         ("narrowband", "Narrowband", "SHO, HOO and dual-band — mono or one-shot colour."),
         ("broadband", "Galaxies & broadband", "RGB, LRGB and one-shot colour, from comets to galaxies."),
         ("nightscapes", "Nightscapes & wide field", "Milky Way, nightscapes and all-sky fisheye."),
         ("solved", "Solved & annotated", "PiSolver knows where you were pointing and names what it sees.")]
def gallery():
    jump = "".join(f'<a href="#{k}">{n}</a>' for k, n, _ in GSECS)
    body = page_hero("// gallery", "Made by<br><span class=\"grad\">PiMagic Studio</span>", "Real PiMagic results, straight out of a run — by kind of night. Click any image to enlarge.",
                     f'<nav class="jump" aria-label="Sections">{jump}</nav>')
    body += '<section class="sec sec-tight"><div class="wrap">' + "".join(
        f'<section class="gsec" id="{k}"><div class="topic-head"><h2>{E(n)}</h2><p>{E(sub)}</p></div><div class="masonry" data-cat="{k}"></div></section>' for k, n, sub in GSECS) + "</div></section>" + CTA
    return head("Gallery — PiMagic Studio", "Images made with PiMagic Studio: mosaics, narrowband, galaxies, nightscapes, solved and annotated.") + nav("gallery") + "<main>" + body + "</main>" + FOOT


if __name__ == "__main__":
    for d, f in (("details", details), ("gallery", gallery), ("contact", contact), ("tutorials", tutorials), ("testimonials", testimonials), ("shop", shop)):
        os.makedirs(os.path.join(SITE, d), exist_ok=True)
        open(os.path.join(SITE, d, "index.html"), "w").write(f())
    print("pages ok", len(T), "tutorials")
