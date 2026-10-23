# Block kit for Craig (23 Oct 2026): he builds the new home page in WordPress himself and pastes our interactive parts in as
# self-contained "Custom HTML" blocks (CSS + JavaScript inline). This cuts every section out of the finished sandbox pages, scopes
# its CSS under .pms (the theme can neither break it nor be broken by it), keeps only the script parts it needs, and points
# every image and film at a small asset-only plugin (pimagic-block-assets). Output: exports/pimagic-block-kit/ and a zip.
#   python3 tools/build_blocks.py
import os, re, shutil, subprocess, html as H
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SITE = os.path.join(HERE, "site")
OUT = os.path.join(HERE, "exports", "pimagic-block-kit"); KITVER = "1.0"
ASSETS = "/wp-content/plugins/pimagic-block-assets/"                         # root-relative: works on the live site and on staging
LINKS = {"buy": "/downloads/pimagic-studio-version-3/", "details": "/details/", "gallery": "/gallery/", "tutorials": "/about/",
         "testimonials": "/testimonials/", "contact": "/contact/"}
FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@300;400;500;600;700&display=swap">'

# ------------------------------------------------------------------ CSS: parse into rules, keep what a block uses, scope under .pms
css_src = re.sub(r"/\*.*?\*/", "", open(os.path.join(SITE, "css/site.css")).read(), flags=re.S)
def parse(s):
    out, i = [], 0
    while i < len(s):
        j = s.find("{", i)
        if j < 0: break
        head = s[i:j].strip(); depth, k = 1, j + 1
        while depth:
            depth += {"{": 1, "}": -1}.get(s[k], 0); k += 1
        body = s[j + 1:k - 1]
        if head.startswith("@media") or head.startswith("@supports"): out.append(("media", head, parse(body)))
        elif head.startswith("@keyframes"): out.append(("kf", head, body))
        elif head: out.append(("rule", head, body))
        i = k
    return out
RULES = parse(css_src)
KF = [h.split()[1] for t, h, _ in RULES if t == "kf"]
JS_CLASSES = {"on", "in", "done", "now", "exploded", "expert", "go", "yours", "demo", "off", "open", "long", "lall", "tile", "reveal",
              "ov-tile", "dtab-panel", "badge"}
def scope_sel(sel):
    sel = sel.strip()
    if sel.startswith("html"): return None
    if sel.startswith(":root"): return ".pms" + sel[5:]
    if sel == "body" or sel.startswith("body."): return ".pms"
    if sel == "*": return ".pms,.pms *"
    return ".pms " + sel
def keep(sel, cls, ids):
    c = set(re.findall(r"\.([\w-]+)", re.sub(r"\[[^\]]*\]", "", sel))); d = set(re.findall(r"#([\w-]+)", sel))
    if sel.strip().startswith((":root", "body", "*")) or sel.strip() == "[hidden]": return True
    return c <= cls and d <= ids
def emit(rules, cls, ids):
    out = []
    for t, h, b in rules:
        if t == "media":
            inner = emit(b, cls, ids)
            if inner: out.append(f"{h}{{{inner}}}")
        elif t == "kf":
            if re.search(r"\b" + h.split()[1] + r"\b", css_used_anim[0]): out.append(f"@keyframes pms-{h.split()[1]}{{{b.strip()}}}")
        else:
            sels = [scope_sel(x) for x in h.split(",") if keep(x, cls, ids)]
            sels = [x for x in sels if x]
            if sels:
                b = re.sub(r"\s+", " ", b.strip())
                for k in KF: b = re.sub(r"(animation[^;]*?)\b" + k + r"\b", r"\1pms-" + k, b)
                b = b.replace("url(../assets/", f"url({ASSETS}assets/")
                if h.strip() == "body": b = re.sub(r"margin:0;?", "", b)
                out.append(",".join(sels) + "{" + b + "}")
    return "".join(out)
css_used_anim = [""]
BASECSS = (".pms{background:var(--bg);width:100vw!important;max-width:100vw!important;margin:0 calc(50% - 50vw)!important;padding:0!important;"
           "position:relative;text-align:left}html,body{overflow-x:clip}"
           ".pms h1,.pms h2,.pms h3{color:var(--text);text-transform:none;padding:0;background:none;border:0}"
           ".pms p{font-family:var(--body)}.pms ul,.pms ol{margin-top:0}.pms li{list-style:inherit}.pms img{height:auto;border:0;box-shadow:none}"
           ".pms a:focus,.pms button:focus{outline-offset:2px}.pms figure{margin:0}.pms input[type=range]{background:transparent;border:0;box-shadow:none}"
           ".pms button{box-shadow:none;text-transform:none;letter-spacing:inherit;min-height:0;border-radius:inherit}")

# ------------------------------------------------------------------ JS: split site.js at its section markers
js_src = open(os.path.join(SITE, "js/site.js")).read()
parts = re.split(r"\n(?=/\* ---------- )", js_src)
pre = parts[0]; JSB = {}
for p in parts[1:]:
    name = re.match(r"/\* ---------- (.+?) ---------- \*/", p).group(1)
    JSB[name.split(":")[0].split(" (")[0].strip()] = p
JSB[list(JSB)[-1]] = JSB[list(JSB)[-1]].rsplit("})();", 1)[0]          # the file's own closing wrapper
def jsblocks(*names):
    body = []
    for n in names:
        k = next(k for k in JSB if k.startswith(n))
        b = JSB[k]
        if k.startswith("films"):
            b = b.replace('const BASE = document.documentElement.dataset.base || "";          // sub-pages set data-base="../"\n', "")
        if k.startswith("reveal"): b = b  # observers for this block only (helpers default to the block's root)
        body.append(b)
    return ("(() => {\n"                                               # ROOT (this block) comes from the loader
            "const $ = (s, r = ROOT) => r.querySelector(s), $$ = (s, r = ROOT) => [...r.querySelectorAll(s)];\n"
            "const reduce = matchMedia(\"(prefers-reduced-motion: reduce)\").matches;\n"
            + re.search(r"^const clamp.*$", pre, re.M).group(0) + "\n"       # clamp / ease / seg
            + f'const BASE = "{ASSETS}";\n' + "\n".join(body) + "\n})();")

# WordPress rewrites some characters inside pasted scripts (an "&&" after a "<" became "&#038;&#038;" in testing), so each block's
# script travels base64-encoded in a data attribute; the tiny loader contains no "&" and no "<" for WordPress to touch.
import base64
def loader(js):
    b = base64.b64encode(js.encode()).decode()
    # runs once the page has loaded (observers set up while WordPress is still parsing the page never fired in testing)
    return ('<script data-pms="' + b + '">(function(){var s=document.currentScript,r=s.parentElement,b=atob(s.getAttribute("data-pms")),u=new Uint8Array(b.length);'
            'for(var i=0;i!==b.length;i++)u[i]=b.charCodeAt(i);var f=new Function("ROOT",new TextDecoder().decode(u)),go=function(){f(r)};'
            'document.readyState==="loading"?document.addEventListener("DOMContentLoaded",go):go();})();</script>')
assert "&" not in loader("x") and "<" not in loader("x")[8:-9]

# ------------------------------------------------------------------ sections out of the finished pages
def sections(path, ids):
    s = open(os.path.join(SITE, path)).read(); out = {}
    for key, rx in ids:
        m = re.search(rx, s)
        a = s.rfind("<!--", 0, m.start()) if s.rfind("<!--", 0, m.start()) > s.rfind("</section>", 0, m.start()) else m.start()
        depth, i = 0, m.start()
        for t in re.finditer(r"<(/?)section\b", s[m.start():]):
            depth += -1 if t.group(1) else 1
            if depth == 0: i = m.start() + t.end(); break
        out[key] = s[m.start():s.index(">", i) + 1]
    return out, s
MODALS = '''<div class="modal" id="filmModal" hidden><div class="modal-in"><button class="modal-x" aria-label="Close">✕</button><video controls playsinline preload="none"></video></div></div>
<div class="modal" id="lightbox" hidden><div class="modal-in lb"><button class="modal-x" aria-label="Close">✕</button><img alt=""><p class="mono"></p></div></div>'''
def fix(h, sub=False):
    pre_ = "../" if sub else ""
    h = re.sub(r'(src|data-src|poster|href)="' + re.escape(pre_) + r'assets/', lambda m: f'{m.group(1)}="{ASSETS}assets/', h)
    h = h.replace(f"url({pre_}assets/", f"url({ASSETS}assets/")
    for k, v in (("shop", LINKS["buy"]), ("details", LINKS["details"]), ("gallery", LINKS["gallery"]), ("tutorials", LINKS["tutorials"]),
                 ("testimonials", LINKS["testimonials"]), ("contact", LINKS["contact"])):
        h = re.sub(r'href="' + re.escape(pre_) + k + r'/', f'href="{v}', h)
    h = h.replace('href="../#', 'href="/#').replace('href="../"', 'href="/"')
    return h

home, _ = sections("index.html", [("hero", r'<section class="hero"'), ("start", r'<section class="sec" id="start"'), ("smart", r'<section class="sec" id="smart"'),
    ("layers", r'<section class="sec" id="layers"'), ("variety", r'<section class="sec sec-tight" id="variety"'), ("standout", r'<section class="sec sec-tight" id="standout"'),
    ("journey", r'<section class="sec" id="journey"'), ("speedrun", r'<section class="sec sec-tight" id="speedrun"'), ("voices", r'<section class="sec" id="voices"'),
    ("pricing", r'<section class="sec" id="pricing"')])
def main_of(path):
    s = open(os.path.join(SITE, path)).read(); return s[s.index("<main>") + 6:s.index("</main>")]

# ------------------------------------------------------------------ the blocks: file, title, html, script parts, extra css, note
BLOCKS = [
 ("home/00-page-background.html", "Page background (dark + starfield)", '<canvas id="stars" aria-hidden="true"></canvas><div class="nebula" aria-hidden="true"></div>', ("starfield",),
  "body{background:#04060c!important}body .pms{background:transparent}.pms.pms-bg{height:0!important;overflow:visible}"
  ".pms #stars{position:fixed;inset:0;width:100%;height:100%;z-index:-2;pointer-events:none}.pms .nebula{position:fixed;inset:-20%;z-index:-1}"
  ".wp-site-blocks,.wp-site-blocks main,.entry-content,.site-content,.site-main{background:transparent!important}",
  "Optional, first block on the page: makes the whole page dark with the moving starfield, exactly like the preview."),
 ("home/01-hero.html", "Hero", home["hero"], ("reveal", "hero console"), ".pms .hero{min-height:min(100svh,880px)}.pms .hero-inner{padding:70px 0 90px}", ""),
 ("home/02-two-clicks.html", "Two clicks — Then it's all yours", home["start"] + MODALS, ("reveal", "films", "two clicks"), "", ""),
 ("home/03-it-configures-itself.html", "It configures itself", home["smart"], ("reveal", "Smart", "it configures itself"), "", ""),
 ("home/04-hybrid-workflow-layers.html", "The hybrid workflow · try it (simulated layers)", home["layers"], ("reveal", "why layers"), "", ""),
 ("home/05-every-kind-of-night.html", "One workflow, every kind of night (gallery strip)", home["variety"], ("reveal",), "", "Easy to rebuild natively: a Gallery block with 7 images."),
 ("home/06-standout-features.html", "Two standout features: mosaics + PiSolver", home["standout"], ("reveal", "before / after", "mosaic story"), "", ""),
 ("home/07-elephant-player.html", "From Start to your finish (Elephant player)", home["journey"], ("reveal", "the Elephant Trunk player"), "", ""),
 ("home/08-speed-run.html", "Same fifteen minutes (speed run)", home["speedrun"], ("reveal",), "", "Easy to rebuild natively: image + heading + text + 2 buttons."),
 ("home/09-quotes.html", "Real users, real results", home["voices"], ("reveal",), "", "Easy to rebuild natively: 3 quote blocks, or your testimonials."),
 ("home/10-pricing.html", "More nights imaging · $119", home["pricing"], ("reveal",), "", "Easy to rebuild natively; the Buy button can be the shop's own button."),
 ("pages/details-page.html", "Details page (all eight tabs)", fix(main_of("details/index.html"), sub=True) + MODALS,
  ("reveal", "before / after", "films", "Smart", "the engine", "details page", "PiMagic layers", "counters"),
  ".pms .dtab-top{margin-top:0}.pms .dtab-nav{top:0}body.admin-bar .pms .dtab-nav{top:32px}@media (max-width:782px){body.admin-bar .pms .dtab-nav{top:46px}}", "Its own page with the slug  details ."),
 ("pages/gallery-page.html", "Gallery page", fix(main_of("gallery/index.html"), sub=True) + MODALS, ("reveal", "films", "gallery"),
  ".pms .page-hero{padding-top:70px}", "Its own page with the slug  gallery ."),
]
if os.path.exists(OUT): shutil.rmtree(OUT)
used_assets = set(); report = []
for fn, title, html_, jsn, extra, note in BLOCKS:
    body = html_ if fn.startswith("pages/") else fix(html_)
    cls = set(c for m in re.findall(r'class="([^"]+)"', body + jsblocks(*jsn)) for c in m.split()) | JS_CLASSES
    cls |= set(re.findall(r'class(?:Name|List\.(?:add|toggle))?\(?\s*["\']([\w-]+)', jsblocks(*jsn)))
    ids = set(re.findall(r'id="([^"]+)"', body))
    js = jsblocks(*jsn)
    css_used_anim[0] = ""
    css = emit(RULES, cls, ids)
    css_used_anim[0] = css
    css = emit(RULES, cls, ids)                                    # second pass keeps the keyframes the kept rules use
    css = BASECSS + css + extra
    key = os.path.basename(fn)[:-5]
    doc = (f"<!-- PiMagic Studio block kit {KITVER} · {title} · paste into ONE WordPress \"Custom HTML\" block. "
           f"Images and films come from the PiMagic Block Assets plugin ({ASSETS}). -->\n"
           f"{FONTS}\n<style>{css}</style>\n<div class=\"pms pms-{re.sub(r'^[0-9]+-', '', key)}{' pms-bg' if 'background' in key else ''}\">\n{body.strip()}\n"
           f"{loader(js)}\n</div>\n")
    p = os.path.join(OUT, "blocks", fn); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w").write(doc)
    used_assets |= set(re.findall(r"assets/(?:img|video)/[\w.-]+", doc))
    report.append((fn, title, note, len(doc)))
    print(f"{fn:42s} {len(doc) // 1024:4d} KB")

# ------------------------------------------------------------------ the asset plugin (only files; no settings, no page changes)
AP = os.path.join(OUT, "_build", "pimagic-block-assets"); os.makedirs(AP)
open(os.path.join(AP, "pimagic-block-assets.php"), "w").write("""<?php
/**
 * Plugin Name: PiMagic Block Assets
 * Description: Images and films for the PiMagic Studio page blocks (Custom HTML). Holds files only - changes no page, adds no settings.
 * Version: %s
 * Author: Dr. Christian Sasse and Craig Stocks
 */
if (!defined('ABSPATH')) exit;
""" % KITVER)
open(os.path.join(AP, "index.php"), "w").write("<?php // Silence is golden.\n")
shutil.copytree(os.path.join(SITE, "assets"), os.path.join(AP, "assets"), ignore=shutil.ignore_patterns("*.json", ".DS_Store", "._*"))
z = os.path.join(OUT, "pimagic-block-assets.zip")
subprocess.run(["zip", "-qr", "-X", z, "pimagic-block-assets", "-x", "*.DS_Store", "*/._*"], cwd=os.path.dirname(AP), check=True)
missing = [a for a in sorted(used_assets) if not os.path.exists(os.path.join(SITE, a))]
print("assets plugin", os.path.getsize(z) // 1024 // 1024, "MB · referenced", len(used_assets), "· missing", missing)
open(os.path.join(OUT, "_build", "report.txt"), "w").write("\n".join(f"{a}\t{b}\t{c}\t{d}" for a, b, c, d in report))
