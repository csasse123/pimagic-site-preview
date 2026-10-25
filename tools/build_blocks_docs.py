# Instructions + extras for the block kit (run after build_blocks.py).
import os, html as H, shutil, subprocess
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(HERE, "exports", "pimagic-block-kit")
rep = [l.split("\t") for l in open(os.path.join(OUT, "_build", "report.txt")).read().splitlines()]
# plain-text copies (double-click opens them as text everywhere)
for fn, *_ in rep:
    src = os.path.join(OUT, "blocks", fn); dst = os.path.join(OUT, "blocks-as-text", fn[:-5] + ".txt")
    os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy(src, dst)
FONTCSS = """/* PiMagic Studio fonts for the native WordPress blocks, so they match the pasted PiMagic blocks.
   Paste into: Appearance > Editor > Styles > (pencil) > Additional CSS   (classic themes: Appearance > Customize > Additional CSS) */
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap");
body { font-family: Inter, system-ui, sans-serif; }
h1, h2, h3, h4, h5, h6, .wp-block-button__link { font-family: "Space Grotesk", system-ui, sans-serif; letter-spacing: -0.02em; }
/* optional helpers for native blocks (Block > Advanced > Additional CSS class) */
.pms-dark { background: #04060c; color: #e7edf7; }                       /* a Group/Cover block in the PiMagic dark */
.pms-grad { background: linear-gradient(92deg,#6fd3ff 0%,#a98bff 52%,#ff8fb1 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
.pms-mute { color: #93a1b8; }
.pms-btn .wp-block-button__link { background: linear-gradient(92deg,#6fd3ff 0%,#a98bff 52%,#ff8fb1 100%); color: #061018; border-radius: 999px; font-weight: 600; }
"""
open(os.path.join(OUT, "fonts-and-colours-for-native-blocks.css"), "w").write(FONTCSS)
rows = "".join(f"<tr><td class='n'>{i + 1}</td><td><code>{H.escape(fn)}</code></td><td>{H.escape(t)}{f'<br><span class=small>{H.escape(n)}</span>' if n else ''}</td></tr>"
               for i, (fn, t, n, size) in enumerate(rep))
DOC = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PiMagic Studio Block Kit — Instructions</title>
<style>
:root{{--bg:#0b0f19;--panel:#121a2b;--line:#24304a;--fg:#e7edf7;--mute:#9aa7bf;--a:#7fe3b8;--b:#b49bff}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 -apple-system,"Segoe UI",Inter,system-ui,sans-serif}}
.w{{max-width:900px;margin:0 auto;padding:40px 20px 80px}} h1{{font-size:34px;margin:0 0 6px}} h2{{font-size:22px;margin:42px 0 10px;color:var(--a)}}
p,li{{color:#cfd8e6}} .small{{color:var(--mute);font-size:13.5px}} code{{background:#0a0f1a;border:1px solid var(--line);border-radius:5px;padding:1px 6px;font-size:13.5px}}
table{{width:100%;border-collapse:collapse;margin-top:8px}} td{{border-top:1px solid var(--line);padding:8px 6px;vertical-align:top}} td.n{{color:var(--mute);width:28px}}
.box{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:14px 0}} .box.warn{{border-left:3px solid #ffc27a}}
ol li,ul li{{margin:6px 0}} pre{{background:#0a0f1a;border:1px solid var(--line);border-radius:8px;padding:12px;overflow:auto;font-size:13px}}
</style></head><body><div class="w">
<h1>PiMagic Studio Block Kit</h1>
<p class="small">For Craig · version 1.0.2 · 25 Oct 2026 · builds the new home page, Details and Gallery in WordPress so they look exactly like the preview (csasse123.github.io/pimagic-site-preview)</p>

<div class="box"><b>What's in the kit</b><ul>
<li><code>pimagic-block-assets.zip</code> — a tiny plugin that only holds the images and films (it changes no page and adds no settings).</li>
<li><code>blocks/home/</code> — the 11 home-page blocks, in order (00–10). <code>blocks/pages/</code> — Details and Gallery, one block each.</li>
<li><code>blocks-as-text/</code> — the same blocks as .txt files: double-click, Select All, Copy. Use these if your computer opens .html as a web page.</li>
<li><code>fonts-and-colours-for-native-blocks.css</code> — makes your own WordPress blocks use the same fonts and colours.</li></ul>
Every block is complete in itself: design and behaviour are inside it, and the theme can't change it.</div>

<h2>1 · Install the assets plugin (once)</h2>
<ol><li>WordPress admin › Plugins › Add New Plugin › Upload Plugin › choose <code>pimagic-block-assets.zip</code> › Install Now › Activate.</li>
<li>If WordPress says the file is too large (it is about 80 MB because the films are inside): unzip it and copy the folder <code>pimagic-block-assets</code> into <code>wp-content/plugins/</code> with the Bluehost File Manager, then activate it under Plugins.</li></ol>

<h2>2 · The home page</h2>
<ol><li>Open your draft page (Home V3.2). In the page settings choose a template without the page title and without sidebars (often called "No Title", "Blank" or "Full width").</li>
<li>For each file below, in order: add a <b>Custom HTML</b> block (type <code>/html</code> and press Enter), open the file from <code>blocks-as-text/home/</code>, Select All, Copy, and paste into the block.</li>
<li>Block 00 is optional but recommended: it paints the whole page in the PiMagic dark with the moving starfield, like the preview.</li>
<li>Preview the page (the editor shows only code; the real look appears in Preview and on the live page).</li></ol>
<table>{rows}</table>
<p class="small">Blocks 05, 08, 09 and 10 are simple — you can rebuild them as native WordPress blocks any time (use the font file in step 5 so they match).</p>

<h2>3 · Details and Gallery pages</h2>
<ol><li>Create a page <b>Details</b> with the slug <code>details</code>: add block 00 (background) and then <code>pages/details-page</code>.</li>
<li>Create a page <b>Gallery</b> with the slug <code>gallery</code>: add block 00 and then <code>pages/gallery-page</code>.</li>
<li>Same template as the home page (no title, no sidebar). Each Details tab has its own link, for example <code>/details/#pisolver</code>.</li></ol>

<h2>4 · Links inside the blocks</h2>
<p>The buttons and links point to these addresses. If one of your pages has a different address, open the block, use Find (Ctrl/Cmd + F) and replace it:</p>
<table><tr><td>Buy / Get PiMagic 3.2</td><td><code>/downloads/pimagic-studio-version-3/</code> (the current V3 product page)</td></tr>
<tr><td>Details</td><td><code>/details/</code></td></tr><tr><td>Gallery</td><td><code>/gallery/</code></td></tr>
<tr><td>Tutorials</td><td><code>/about/</code></td></tr><tr><td>Testimonials · Contact</td><td><code>/testimonials/</code> · <code>/contact/</code></td></tr></table>

<h2>5 · Fonts (Roboto Flex vs Inter)</h2>
<p>The pasted blocks bring their own fonts (Inter for text, Space Grotesk for headings, JetBrains Mono for small labels), so they look like the preview whatever the theme uses. Your own native WordPress blocks use the theme's Roboto Flex. To make them match, paste the contents of <code>fonts-and-colours-for-native-blocks.css</code> into <b>Appearance › Editor › Styles › Additional CSS</b>. It also adds three optional classes for native blocks: <code>pms-dark</code> (PiMagic dark background), <code>pms-grad</code> (the gradient heading text) and <code>pms-btn</code> (the gradient button) — add them under Block › Advanced › Additional CSS class.</p>

<h2>6 · Changing words</h2>
<p>All text in a block is readable in the Custom HTML code — change a sentence directly there. Leave the <code>&lt;style&gt;</code> part and the long <code>&lt;script data-pms=…&gt;</code> line untouched: that line is the block's behaviour, stored encoded on purpose because WordPress alters some characters in pasted scripts.</p>

<h2>7 · If something doesn't look right</h2>
<div class="box warn"><ul>
<li><b>Images or films missing</b> — the assets plugin is not installed or not in <code>wp-content/plugins/pimagic-block-assets</code>.</li>
<li><b>Blocks show but nothing moves</b> — the person pasting must be an Administrator (WordPress strips scripts for other roles). Speed/optimisation features that delay or combine scripts (Jetpack Boost "Defer non-essential JavaScript", Cloudflare Rocket Loader) can stop them: exclude these pages there.</li>
<li><b>White strips between sections</b> — an empty paragraph block or the theme's block spacing; delete empty blocks, and use block 00.</li>
<li><b>Old content after a change</b> — clear the site cache (Bluehost › Caching) and reload.</li></ul></div>

<h2>8 · Still to fix in the draft page (from our review)</h2>
<ul><li>The film cover still says "PixInsight. Made simple." — the right message is "Astrophotography. Made simple." (block 02 brings the correct film and cover).</li>
<li>"Three Clicks" → two clicks: select a folder, press Start.</li><li>"For Windows and Mac" — the blocks say Mac, Windows and Linux; please confirm which is right.</li>
<li>"Photohsop" → Photoshop.</li></ul>
<p class="small">Tested in WordPress 6.x (latest) with the default block theme: all blocks pasted as Custom HTML, visitor view, desktop and phone, Details tabs, Gallery lightbox, the Elephant player, the layers simulator.</p>
</div></body></html>"""
open(os.path.join(OUT, "INSTRUCTIONS.html"), "w").write(DOC)
txt = subprocess.run(["textutil", "-convert", "txt", "-stdout", os.path.join(OUT, "INSTRUCTIONS.html")], capture_output=True, text=True).stdout
open(os.path.join(OUT, "INSTRUCTIONS.txt"), "w").write(txt)
z = os.path.join(HERE, "exports", "pimagic-block-kit-1.0.2.zip")
if os.path.exists(z): os.remove(z)
subprocess.run(["zip", "-qr", "-X", z, "pimagic-block-kit", "-x", "pimagic-block-kit/_build/*", "pimagic-block-kit/pimagic-block-assets.zip", "*.DS_Store"], cwd=os.path.join(HERE, "exports"), check=True)
print("kit zip", os.path.getsize(z) // 1024, "KB")
