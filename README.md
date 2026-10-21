# PiMagic Studio website - 2026 redesign (sandbox)

Static prototype of pimagicstudio.com (WordPress 7.1 on Bluehost, theme bluehost-blueprint, Easy Digital Downloads shop).
`site/` = the page (index.html, css/site.css, js/site.js, assets/). Preview: `python3 -m http.server 8762 -d site`.
`tools/build_assets.py` rebuilds every image/video from the real sources (../hook-film, PiMagic/Runs Rosette run).

Everything shown is real: the before/after is the Rosette run's own linear stacked Ha master (XISF, crop at 72,128 px) vs its
Final SHO; PiSolver = Orion mosaic plain/annotated (same crop) + the live Witch Head JPEG solve; mosaic = Sikander's six linear
Rho Oph panes + PiMagic's mosaic; gallery = PiMagic outputs (film presentation contrast); hero = Craig's UDRO time-lapse.
Links to Shop / Tutorials / Contact / order history point at the live WordPress pages.

To WordPress later: header/footer = template parts (pm-nav, pm-foot), each <section> = a block pattern (Custom HTML),
css/js = child-theme enqueue; the pricing card's button becomes the EDD buy button. The sandbox has <meta robots noindex>.
