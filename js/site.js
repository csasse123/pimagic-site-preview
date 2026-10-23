/* PiMagic Studio 2026 — interactions. No framework; each block is independent so it can live in a WordPress footer script. */
(() => {
const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x)), ease = x => (x = clamp(x), x * x * (3 - 2 * x)), seg = (p, a, b) => ease((p - a) / (b - a));

/* ---------- starfield ---------- */
(() => {
  const c = $("#stars"), g = c.getContext("2d"); let S = [], w, h, dpr;
  const size = () => { dpr = Math.min(2, devicePixelRatio || 1); w = c.width = innerWidth * dpr; h = c.height = innerHeight * dpr;
    S = Array.from({ length: Math.round(innerWidth * innerHeight / 2600) }, () => ({ x: Math.random() * w, y: Math.random() * h, r: Math.random() ** 3 * 1.6 * dpr + .3 * dpr,
      t: Math.random() * 6.28, s: .4 + Math.random() * 1.6, d: .15 + Math.random() * .85, c: Math.random() < .12 ? [180, 210, 255] : Math.random() < .08 ? [255, 214, 180] : [235, 240, 250] })); };
  size(); addEventListener("resize", size);
  let last = 0;
  const draw = now => {
    if (now - last > 33) { last = now; g.clearRect(0, 0, w, h); const sy = scrollY * dpr;
      for (const s of S) { const a = reduce ? .7 : .45 + .55 * Math.sin(s.t + now / 1000 * s.s); let y = (s.y - sy * s.d * .15) % h; if (y < 0) y += h;
        g.fillStyle = `rgba(${s.c},${a * (.4 + s.d * .6)})`; g.beginPath(); g.arc(s.x, y, s.r, 0, 6.28); g.fill(); } }
    if (!reduce) requestAnimationFrame(draw); };
  requestAnimationFrame(draw);
})();

/* ---------- header ---------- */
const nav = $(".pm-nav");
addEventListener("scroll", () => nav.classList.toggle("scrolled", scrollY > 40), { passive: true });
$(".pm-burger")?.addEventListener("click", e => { const o = nav.classList.toggle("open"); e.currentTarget.setAttribute("aria-expanded", o); });
$$(".pm-menu a").forEach(a => a.addEventListener("click", () => nav.classList.remove("open")));

/* ---------- reveal on scroll + lazy videos ---------- */
const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }), { threshold: .12 });
$$(".reveal").forEach(el => io.observe(el));
const vio = new IntersectionObserver(es => es.forEach(e => { const v = e.target;
  if (e.isIntersecting) { if (!v.src) v.src = v.dataset.src; if (!reduce) v.play().catch(() => {}); } else v.pause(); }), { threshold: .3 });
$$("video.lazyvid").forEach(v => vio.observe(v));

/* ---------- hero console: a run, step by step ---------- */
(() => {
  const L = $$(".console-steps li"), bar = $(".console-bar i"); if (!L.length) return; let i = 0;
  const tick = () => { L.forEach((li, k) => { li.classList.toggle("on", k < i); li.classList.toggle("now", k === i); });
    bar.style.width = (100 * i / L.length) + "%"; i = (i + 1) % (L.length + 3); };
  tick(); if (!reduce) setInterval(tick, 750);
})();

/* ---------- before / after sliders ---------- */
$$(".ba").forEach(ba => {
  const before = $(".ba-before", ba), h = $(".ba-handle", ba);
  const tl = $(".ba-tag-l", ba), tr = $(".ba-tag-r", ba);
  const set = f => { f = clamp(f, 0, 1); before.style.clipPath = `inset(0 ${(1 - f) * 100}% 0 0)`; h.style.left = f * 100 + "%"; h.setAttribute("aria-valuenow", Math.round(f * 100)); ba._f = f;
    if (tl) tl.style.opacity = clamp((f - .04) / .14); if (tr) tr.style.opacity = clamp((.96 - f) / .14); };   // a label leaves with its side
  set(+ba.dataset.start || .5);
  ba._glide = to => { ba._user = true; const from = ba._f, t0 = performance.now(); const st = t => { const u = clamp((t - t0) / 600); set(from + (to - from) * ease(u)); if (u < 1) requestAnimationFrame(st); }; requestAnimationFrame(st); };
  const at = e => { const r = ba.getBoundingClientRect(); set((e.clientX - r.left) / r.width); };
  let drag = false;
  ba.addEventListener("pointerdown", e => { drag = true; ba.setPointerCapture(e.pointerId); at(e); });
  ba.addEventListener("pointermove", e => drag && at(e));
  ba.addEventListener("pointerup", () => drag = false);
  h.addEventListener("keydown", e => { if (e.key === "ArrowLeft") set(ba._f - .05); if (e.key === "ArrowRight") set(ba._f + .05); });
  // a gentle hint the first time it is seen
  const hint = new IntersectionObserver(es => { if (es[0].isIntersecting && !reduce) { hint.disconnect(); let t0 = null;
    const an = t => { t0 ??= t; const u = (t - t0) / 1600; if (u > 1 || drag || ba._user) return; set(.5 + .22 * Math.sin(u * 6.28)); requestAnimationFrame(an); }; requestAnimationFrame(an); } }, { threshold: .6 });
  hint.observe(ba);
});

/* ---------- films ---------- */
const BASE = document.documentElement.dataset.base || "";          // sub-pages set data-base="../"
const FILMS = { long: BASE + "assets/video/film_long.mp4", short: BASE + "assets/video/film_short.mp4" };
const modal = $("#filmModal"), mv = $("video", modal);
const closeModal = m => { m.hidden = true; const v = $("video", m); if (v) { v.pause(); v.removeAttribute("src"); v.load(); v.hidden = false; } const f = $("iframe", m); if (f) { f.src = "about:blank"; f.hidden = true; } document.body.style.overflow = ""; };
const playIn = src => { mv.src = src; modal.hidden = false; document.body.style.overflow = "hidden"; mv.play().catch(() => {}); };
$$("[data-film]").forEach(b => b.addEventListener("click", () => playIn(FILMS[b.dataset.film])));
// YouTube tutorials: a privacy-friendly embed, only loaded on click
$$("[data-yt]").forEach(b => b.addEventListener("click", () => {
  const box = $(".modal-in", modal); mv.hidden = true; let f = $("iframe", box);
  if (!f) { f = document.createElement("iframe"); f.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen"; f.allowFullscreen = true; box.append(f); }
  f.hidden = false; f.src = `https://www.youtube-nocookie.com/embed/${b.dataset.yt}?autoplay=1&rel=0`; modal.hidden = false; document.body.style.overflow = "hidden"; }));
$$(".modal").forEach(m => { m.addEventListener("click", e => { if (e.target === m || e.target.classList.contains("modal-x")) closeModal(m); }); });
addEventListener("keydown", e => { if (e.key === "Escape") $$(".modal").forEach(m => !m.hidden && closeModal(m)); });
$$(".player[data-src]").forEach(p => $(".play", p).addEventListener("click", () => {
  const v = document.createElement("video"); v.src = p.dataset.src; v.controls = true; v.playsInline = true; v.autoplay = true;
  p.replaceChildren(v); v.play().catch(() => {}); }));

/* ---------- Smart | Expert ---------- */
(() => {
  const sw = $(".mode-switch"); if (!sw) return;
  $$("button", sw).forEach(b => b.addEventListener("click", () => {
    const m = b.dataset.mode; sw.classList.toggle("expert", m === "expert");
    $$("button", sw).forEach(x => x.setAttribute("aria-selected", x === b));
    $$(".mode-body").forEach(d => d.hidden = d.dataset.mode !== m); }));
})();

/* ---------- the engine: PiMagic's tools as a living network ---------- */
(() => {
  const c = $("#engineCanvas"); if (!c) return; const g = c.getContext("2d");
  const N = ["Calibration", "Stacking", "PiSolver", "Image Analyzer", "Gradient", "Star Color Tuning", "Deblur", "Denoise", "Star Separation", "Mosaic Blend", "Annotation"];
  let w, h, dpr, vis = false, mx = .5, my = .5, t0 = performance.now();
  const size = () => { dpr = Math.min(2, devicePixelRatio || 1); const r = c.getBoundingClientRect(); w = c.width = r.width * dpr; h = c.height = r.height * dpr; };
  size(); addEventListener("resize", size);
  new IntersectionObserver(es => { vis = es[0].isIntersecting; if (vis) { t0 = performance.now(); requestAnimationFrame(draw); } }, { threshold: .05 }).observe(c);
  c.parentElement.addEventListener("pointermove", e => { const r = c.getBoundingClientRect(); mx = (e.clientX - r.left) / r.width; my = (e.clientY - r.top) / r.height; });
  function draw(now) {
    if (!vis) return; const wide = innerWidth > 900, t = (now - t0) / 1000, cx = w * (wide ? .73 : .5), cy = h * (wide ? .4 : .3), R = Math.min(w * (wide ? .14 : .24), h * (wide ? .36 : .2));
    g.clearRect(0, 0, w, h);
    const P = N.map((n, i) => { const a = i / N.length * 6.283 + t * .05 + (mx - .5) * .4, rr = R * (1 + .16 * Math.sin(i * 1.7));
      return [cx + Math.cos(a) * rr * 1.25, cy + Math.sin(a) * rr * .72 + (my - .5) * 20 * dpr]; });
    const grow = reduce ? 1 : clamp(t / 2.2);
    N.forEach((_, i) => [1, 3].forEach(k => { const j = (i + k) % N.length, [x1, y1] = P[i], [x2, y2] = P[j], kk = clamp(grow * 1.6 - i * .06);
      if (kk <= 0) return; g.strokeStyle = `rgba(130,190,255,${.16 * kk})`; g.lineWidth = dpr; g.beginPath(); g.moveTo(x1, y1); g.lineTo(x1 + (x2 - x1) * kk, y1 + (y2 - y1) * kk); g.stroke();
      const ph = (t * .35 + i * .13 + k * .3) % 1; g.fillStyle = `rgba(200,230,255,${.85 * kk})`; g.beginPath(); g.arc(x1 + (x2 - x1) * ph, y1 + (y2 - y1) * ph, 2.2 * dpr, 0, 6.28); g.fill(); }));
    const core = g.createRadialGradient(cx, cy, 0, cx, cy, R * .55); core.addColorStop(0, "rgba(169,139,255,.28)"); core.addColorStop(1, "rgba(169,139,255,0)");
    g.fillStyle = core; g.beginPath(); g.arc(cx, cy, R * .55, 0, 6.28); g.fill();
    g.font = `500 ${(wide ? 12 : 9.5) * dpr}px "JetBrains Mono", monospace`; g.textAlign = "center";
    P.forEach(([x, y], i) => { const k = clamp(grow * 1.8 - i * .07); if (k <= 0) return;
      g.fillStyle = `rgba(160,210,255,${k})`; g.shadowColor = "rgba(111,211,255,.9)"; g.shadowBlur = 14 * dpr; g.beginPath(); g.arc(x, y, 5 * dpr, 0, 6.28); g.fill(); g.shadowBlur = 0;
      const lab = N[i].toUpperCase(), tw = g.measureText(lab).width / 2 + 6 * dpr;   // labels stay on screen
      g.fillStyle = `rgba(231,237,247,${.9 * k})`; g.fillText(lab, clamp(x, tw, w - tw), y + 22 * dpr); });
    g.font = `600 ${15 * dpr}px "Space Grotesk", sans-serif`; g.fillStyle = "rgba(231,237,247,.95)"; g.fillText("START", cx, cy + 5 * dpr);
    g.strokeStyle = `rgba(142,240,196,${.5 + .3 * Math.sin(t * 3)})`; g.lineWidth = 1.5 * dpr; g.beginPath(); g.ellipse(cx, cy, 46 * dpr, 26 * dpr, 0, 0, 6.28); g.stroke();
    if (!reduce) requestAnimationFrame(draw);
  }
})();

/* ---------- mosaic story: plays by itself like a GIF (Craig, 23 Oct 2026: no scroll-driving, never stalls the page) ---------- */
(() => {
  const sec = $(".mosaic-story"); if (!sec) return;
  const panes = $$(".pane", sec), fin = $(".mosaic-final", sec), steps = $$(".mstep li", sec);
  const PW = 47, PH = 47 * 314 / 470;
  const GRID = [[0, 0], [1, 0], [0, 1], [1, 1], [0, 2], [1, 2]].map(([c, r]) => [50 + (c - .5) * PW * .94, 50 + (r - 1) * PH * .94]);
  const SCAT = [[17, 15, -9], [83, 13, 7], [13, 55, 5], [86, 50, -6], [33, 88, 8], [69, 90, -4]];
  const GAIN = [1.45, .62, 1.2, .78, 1.32, .7];
  fin.style.cssText += `left:${50 - .97 * PW}%;top:${50 - 1.44 * PH}%;width:${.97 * PW * 2}%;height:${1.44 * PH * 2}%;object-fit:cover`;
  const render = p => {
    const kp = seg(p, .24, .5), km = seg(p, .5, .66), kb = seg(p, .68, .84);
    panes.forEach((el, i) => { const k = seg(p, .02 + i * .03, .12 + i * .03), [sx, sy, a] = SCAT[i], [gx, gy] = GRID[i];
      const x = sx + (gx - sx) * kp, y = sy + (gy - sy) * kp, z = .58 + .42 * kp, gn = GAIN[i] + (1 - GAIN[i]) * km;
      el.style.opacity = k * (1 - kb * .999);
      el.style.transform = `translate(-50%,-50%) rotate(${a * (1 - kp)}deg) scale(${z * (.9 + .1 * k)})`;
      el.style.left = x + "%"; el.style.top = y + "%"; el.style.filter = `brightness(${gn})`; el.style.outlineColor = `rgba(150,210,255,${.4 * (1 - kp) + .12})`; });
    fin.style.opacity = kb; fin.style.transform = `scale(${1 + .03 * seg(p, .84, 1)})`;
    const on = [p > .06, p > .3, p > .53, p > .72]; steps.forEach((s, i) => s.classList.toggle("on", on[i]));
  };
  const RUN = 9000, HOLD = 3200; let vis = false, t0 = 0;              // 9 s found -> placed -> matched -> blended, 3 s on the mosaic, loop
  const tick = now => { if (!vis) return; const u = (now - t0) % (RUN + HOLD); render(Math.min(1, u / RUN)); requestAnimationFrame(tick); };
  new IntersectionObserver(es => { const v = es[0].isIntersecting; if (v && !vis) { vis = true; t0 = performance.now(); requestAnimationFrame(tick); } else if (!v) vis = false; },
    { threshold: .3 }).observe(sec);
  render(reduce ? 1 : 0);
})();

/* ---------- gallery (gallery page: one masonry per section) + lightbox ---------- */
(() => {
  const G = [  // k: g_<k>.webp + g_<k>_t.webp ; src: one file for both
    { c: "mosaics", src: "mosaic_rho", t: "Rho Ophiuchi", s: "six-pane deep-sky mosaic" }, { c: "mosaics", k: "soul_nebula", t: "Soul Nebula", s: "deep-sky mosaic" },
    { c: "mosaics", k: "gunlock_panorama", t: "Gunlock", s: "landscape panorama" }, { c: "mosaics", src: "solve_orion", t: "Orion", s: "deep-sky mosaic" },
    { c: "narrowband", k: "veil_nebula", t: "Veil Nebula", s: "SHO narrowband" }, { c: "narrowband", k: "wizard_nebula", t: "Wizard Nebula", s: "SHO narrowband · mono" },
    { c: "narrowband", k: "elephant_s_trunk", t: "Elephant's Trunk", s: "SHO narrowband" }, { c: "narrowband", k: "tarantula_nebula", t: "Tarantula Nebula", s: "SHO narrowband" },
    { c: "narrowband", k: "heart_nebula", t: "Heart Nebula", s: "narrowband" }, { c: "narrowband", k: "horsehead_nebula", t: "Horsehead Nebula", s: "one-shot colour + dual-band" },
    { c: "broadband", k: "andromeda_galaxy", t: "Andromeda Galaxy", s: "RGB" }, { c: "broadband", k: "bode_s_galaxy", t: "Bode's Galaxy", s: "LRGB · mono" },
    { c: "broadband", k: "pleiades", t: "Pleiades", s: "one-shot colour" }, { c: "broadband", k: "m78", t: "M78", s: "mono" },
    { c: "broadband", k: "dumbbell_nebula", t: "Dumbbell Nebula", s: "large telescope" }, { c: "broadband", k: "comet_12p_pons_brooks", t: "Comet 12P/Pons-Brooks", s: "RGB" },
    { c: "nightscapes", k: "m8", t: "M8 · Lagoon & Trifid", s: "Milky Way core" }, { c: "nightscapes", k: "lambs_knoll", t: "Lambs Knoll", s: "Milky Way nightscape" },
    { c: "nightscapes", k: "milky_way_nightscape", t: "Milky Way", s: "nightscape · mirrorless" }, { c: "nightscapes", k: "all_sky", t: "All-sky", s: "fisheye" },
    { c: "solved", src: "solve_orion_annot", t: "Orion", s: "solved & annotated by PiSolver" }, { c: "solved", src: "ba2_rosette_craig_annot", t: "Rosette Nebula", s: "PiMagic's annotation on Craig Stocks' finish" }];
  const lb = $("#lightbox"), thumb = g => `${BASE}assets/img/${g.k ? `g_${g.k}_t` : g.src}.webp`, full = g => `${BASE}assets/img/${g.k ? `g_${g.k}` : g.src}.webp`;
  $$(".masonry[data-cat]").forEach(m => {
    const L = G.filter(g => g.c === m.dataset.cat);
    m.innerHTML = L.map((g, i) => `<figure class="tile reveal" tabindex="0" data-i="${i}"><img src="${thumb(g)}" alt="${g.t} — ${g.s}, processed by PiMagic" loading="lazy"><figcaption><b>${g.t}</b><span>${g.s}</span></figcaption></figure>`).join("");
    $$(".tile", m).forEach(el => { io.observe(el); const g = L[+el.dataset.i];
      const open = () => { $("img", lb).src = full(g); $("img", lb).alt = g.t; $("p", lb).textContent = `${g.t} · ${g.s} · PiMagic`; lb.hidden = false; document.body.style.overflow = "hidden"; };
      el.addEventListener("click", open); el.addEventListener("keydown", e => e.key === "Enter" && open()); }); });
})();

/* ---------- two clicks: Craig's recorded run, frame by frame ---------- */
(() => {
  const wf = $(".wf"); if (!wf) return;
  const F = $$(".wf-screen img", wf), rip = $(".wf-ripple", wf), cap = $(".wf-text", wf), dots = $(".wf-dots", wf), C = $$(".click");
  const DUR = [2800, 3200, 2600, 2400, 2400, 3600];
  dots.innerHTML = F.map(() => "<i></i>").join(""); const D = $$("i", dots);
  let i = 0, tm = [], vis = false;
  const show = k => { i = k; F.forEach((f, j) => f.classList.toggle("on", j === k)); D.forEach((d, j) => d.classList.toggle("on", j === k));
    cap.textContent = F[k].dataset.cap; C.forEach(c => c.classList.toggle("on", +c.dataset.c === +F[k].dataset.c)); };
  const clear = () => { tm.forEach(clearTimeout); tm = []; };
  const run = () => { clear(); show(i); const f = F[i], d = DUR[i];
    if (f.dataset.click) { const [x, y] = f.dataset.click.split(","); rip.style.left = x + "%"; rip.style.top = y + "%";
      tm.push(setTimeout(() => { rip.classList.remove("go"); void rip.offsetWidth; rip.classList.add("go"); }, d - 1000)); }
    if (vis && !reduce) tm.push(setTimeout(() => { i = (i + 1) % F.length; run(); }, d)); };
  D.forEach((d, j) => d.addEventListener("click", () => { i = j; run(); }));
  new IntersectionObserver(es => { vis = es[0].isIntersecting; if (vis) run(); else clear(); }, { threshold: .35 }).observe(wf);
  show(0);
})();

/* ---------- it configures itself: what PiMagic found, line by line ---------- */
(() => {
  const d = $(".detect"); if (!d) return;
  const L = $$(".det li", d), go = $(".det-go", d), st = $(".det-state", d); let tm = [];
  const play = () => { tm.forEach(clearTimeout); tm = []; L.forEach(l => l.classList.remove("on", "now")); go.classList.remove("on"); st.textContent = "READING…";
    if (reduce) { L.forEach(l => l.classList.add("on")); go.classList.add("on"); st.textContent = "● READY"; return; }
    L.forEach((l, k) => tm.push(setTimeout(() => { L.forEach(x => x.classList.remove("now")); l.classList.add("on", "now"); }, 400 + k * 520)));
    tm.push(setTimeout(() => { L.forEach(x => x.classList.remove("now")); go.classList.add("on"); st.textContent = "● READY"; }, 400 + L.length * 520 + 300)); };
  new IntersectionObserver(es => { if (es[0].isIntersecting) play(); }, { threshold: .5 }).observe(d);
})();

/* ---------- the Elephant Trunk player: real run (sped up) -> layers fly into Photoshop in 3D -> Craig's finish ---------- */
(() => {
  const jr = $("#jr"); if (!jr) return;
  const scenes = $$(".jr-scene", jr), steps = $$(".jr-steps button", jr), cap = $(".jr-cap", jr), playB = $(".jr-play", jr);
  const vid = $(".jr-run video", jr), xEl = $(".jr-x", jr);
  const stack = $(".ps-stack", jr), L = ["neb", "stars", "annot", "meta"].map(n => $(".pl-" + n, jr)), labs = $$(".pl-lab", jr), rows = $$(".ps-layers li", jr);
  const CAP = ["A real PiMagic run on Craig's Elephant Trunk folder, recorded on our Mac: 49 files in, calibrated, stacked, processed and finished — unattended.",
               "AstroMagic brings PiMagic's results into Photoshop as layers: the nebula without stars, the stars, the annotation and the metadata.",
               "Craig Stocks' finish of the same data. The routine was automatic; the creativity is his."];
  const DUR = [0, 8200, 7000];                                // scene 0 lasts as long as the film
  let k = -1, t0 = 0, playing = true, vis = false;
  // 3D: layers arrive one by one into an exploded stack, then settle into the canvas
  const stack3d = u => {
    const ex = seg(u, .02, .2) * (1 - seg(u, .74, .96)), H = stack.offsetHeight, nar = innerWidth < 900, sp = nar ? .2 : .3;   // phones: a tighter stack
    stack.style.transform = `translateY(${(nar ? 16 : 4) * ex}%) scale(${1 - (nar ? .38 : .3) * ex}) rotateX(${58 * ex}deg) rotateZ(${-30 * ex}deg)`;
    L.forEach((el, i) => { const a = seg(u, .06 + i * .13, .26 + i * .13);
      el.style.opacity = a; el.style.transform = `translateZ(${(i * sp * H) * ex + (1 - a) * H * 1.1 + i * .5}px)`; el.style.setProperty("--edge", (.7 * ex).toFixed(3)); });
    labs.forEach((l, i) => { l.style.opacity = ex * seg(u, .14 + i * .13, .26 + i * .13); l.style.transform = `translateY(-50%) rotateZ(${30 * ex}deg) rotateX(${-58 * ex}deg)`; });
    rows.forEach(r => { const i = ["neb", "stars", "annot", "meta"].indexOf(r.dataset.l); r.classList.toggle("in", u > .2 + i * .13); }); };
  const flat = () => { stack.style.transform = ""; L.forEach(el => { el.style.opacity = 1; el.style.transform = ""; el.style.setProperty("--edge", 0); }); labs.forEach(l => l.style.opacity = 0); rows.forEach(r => r.classList.add("in")); };
  const show = n => { k = n; t0 = performance.now(); scenes.forEach((sc, i) => sc.classList.toggle("on", i === n));
    steps.forEach((b, i) => { b.classList.toggle("on", i === n); b.classList.toggle("done", i < n); b.style.setProperty("--p", i < n ? 1 : 0); });
    cap.textContent = CAP[n];
    if (n === 0) { if (!vid.src) vid.src = vid.dataset.src; vid.currentTime = 0; if (playing) vid.play().catch(() => {}); } else vid.pause();
    if (n === 1) playing ? stack3d(0) : flat(); };
  const tick = now => { requestAnimationFrame(tick); if (!playing || !vis || k < 0) return;
    let u; if (k === 0) { u = vid.currentTime / (vid.duration || 22); if (vid.ended) return next(); }
    else { u = (now - t0) / DUR[k]; if (u >= 1) return next(); }
    steps[k].style.setProperty("--p", clamp(u).toFixed(3)); if (k === 1) stack3d(clamp(u)); };
  const next = () => show((k + 1) % 3);
  const stop = () => { playing = false; vid.pause(); playB.textContent = "▶ Play"; playB.setAttribute("aria-label", "Play"); if (k === 1) flat(); };
  const go = () => { playing = true; playB.textContent = "❚❚ Pause"; playB.setAttribute("aria-label", "Pause"); t0 = performance.now(); if (k === 0) vid.play().catch(() => {}); };
  playB.addEventListener("click", () => playing ? stop() : (go(), k === 1 && show(1)));
  $(".jr-replay", jr).addEventListener("click", () => { go(); show(0); });
  $$("[data-s]", jr).forEach(b => b.addEventListener("click", () => { go(); show(+b.dataset.s); }));
  vid.addEventListener("loadedmetadata", () => { xEl.textContent = `${Math.round(+vid.dataset.real / 60)} real minutes in ${Math.round(vid.duration)} s`; });
  new IntersectionObserver(es => { vis = es[0].isIntersecting; if (vis && k < 0) show(0); if (!vis) vid.pause(); else if (playing && k === 0) vid.play().catch(() => {}); }, { threshold: .35 }).observe(jr);
  if (reduce) { playing = false; show(2); } requestAnimationFrame(tick);
})();

/* ---------- why layers: Craig's Elephant Trunk pieces in Screen mode - a show box and an intensity slider per layer ---------- */
(() => {
  const box = $(".lyps"); if (!box) return;
  const rows = $$(".ly-list li", box);
  const set = li => { const on = $("input[type=checkbox]", li).checked, r = $("input[type=range]", li), img = $(".ly-" + li.dataset.ly, box);
    img.style.display = on ? "" : "none"; img.style.filter = `brightness(${r.value / 100})`; $("output", li).textContent = r.value + "%";
    li.classList.toggle("off", !on); };
  rows.forEach(li => { $$("input", li).forEach(i => i.addEventListener("input", () => set(li))); set(li); });
  $(".ly-reset", box).addEventListener("click", () => rows.forEach(li => { $("input[type=checkbox]", li).checked = true; $("input[type=range]", li).value = 100; set(li); }));
})();

/* ---------- details page: one section at a time, the menu stays (hash = section) ---------- */
(() => {
  const nav = $(".dtab-nav"); if (!nav) return;
  const B = $$("[data-tab]", nav), P = $$(".dtab-panel");
  const open = (k, scroll) => { const i = Math.max(0, B.findIndex(b => b.dataset.tab === k));
    B.forEach((b, j) => b.setAttribute("aria-selected", j === i)); P.forEach((p, j) => p.hidden = j !== i);
    $$(".reveal", P[i]).forEach(el => el.classList.add("in"));
    dispatchEvent(new Event("resize"));                                            // canvases and sliders measure themselves again
    if (scroll) scrollTo({ top: $("#dtabs").getBoundingClientRect().top + scrollY - nav.offsetHeight - parseFloat(getComputedStyle(nav).top), behavior: "instant" });   // the section starts right under the menu
    const w = $(".wrap", nav); w.scrollLeft = B[i].offsetLeft - w.offsetLeft - 16; };   // phones: the chosen tab stays in sight
  B.forEach(b => b.addEventListener("click", () => { history.replaceState(null, "", "#" + b.dataset.tab); open(b.dataset.tab, true); }));
  addEventListener("hashchange", () => open(location.hash.slice(1), true));
  open(location.hash.slice(1), !!location.hash);
})();

/* ---------- tutorials: topic chips, version toggle, search ---------- */
(() => {
  const list = $("#tutorials"); if (!list) return;
  const chips = $$(".chips button"), q = $("#tq"), arch = $("#archive");
  let topic = "all";
  const apply = () => { const s = (q.value || "").toLowerCase().trim();
    $$(".tut", list).forEach(c => { const ok = (topic === "all" || c.dataset.topic === topic) && (!s || c.textContent.toLowerCase().includes(s)) && (arch.checked || c.dataset.v !== "2");
      c.hidden = !ok; });
    $$(".topic", list).forEach(t => t.hidden = !$$(".tut", t).some(c => !c.hidden));
    const n = $$(".tut", list).filter(c => !c.hidden).length; $("#tcount").textContent = n; $("#tempty").hidden = n > 0; };
  chips.forEach(b => b.addEventListener("click", () => { topic = b.dataset.t; chips.forEach(x => x.classList.toggle("on", x === b)); apply(); }));
  q.addEventListener("input", apply); arch.addEventListener("change", apply); apply();
})();
$$(".more").forEach(b => b.addEventListener("click", () => { const c = b.closest(".tq"); c.classList.toggle("open"); b.textContent = c.classList.contains("open") ? "Show less" : "Read the full story"; }));

/* ---------- PiMagic layers (step 1) and Craig's versions (step 2) ---------- */
const showLayers = L => { const ba = L.closest(".ba"); if (ba && ba._f > .02) ba._glide(0); };   // the layers live on PiMagic's side: open it up
$$(".lchip[data-layer]").forEach(b => b.addEventListener("click", () => { const L = $("#" + b.dataset.layer), on = !L.classList.contains("on");
  L.classList.toggle("on", on); b.classList.toggle("on", on); b.setAttribute("aria-pressed", on); if (on) showLayers(L); }));
$$(".lchip[data-all]").forEach(b => b.addEventListener("click", () => { const chips = $$(`.lchip[data-layer^="${b.dataset.all}-"]`), on = !b.classList.contains("on");
  chips.forEach(c => { $("#" + c.dataset.layer).classList.toggle("on", on); c.classList.toggle("on", on); c.setAttribute("aria-pressed", on); });
  b.classList.toggle("on", on); b.setAttribute("aria-pressed", on); if (on && chips[0]) showLayers($("#" + chips[0].dataset.layer)); }));
(() => { const img = $("#craigImg"); if (!img) return;
  ["ba2_rosette_craig_meta", "ba2_rosette_craig_annot"].forEach(n => { const i = new Image(); i.src = BASE + `assets/img/${n}.webp`; });   // no flash on switch
  $$(".lchip[data-craig]").forEach(b => b.addEventListener("click", () => { img.src = BASE + `assets/img/${b.dataset.craig}.webp`;
    const ba = img.closest(".ba"); if (b.dataset.craig !== "ba2_rosette_craig" && ba._f > .02) ba._glide(0);
    $$(".lchip[data-craig]").forEach(x => { x.classList.toggle("on", x === b); x.setAttribute("aria-pressed", x === b); }); })); })();

/* ---------- contact form: compose an email (WordPress: WPForms takes over) ---------- */
(() => { const f = $("#cform"); if (!f) return;
  f.addEventListener("submit", e => { e.preventDefault(); const v = n => f.elements[n].value.trim();
    const body = `${v("message")}\n\n— ${v("first")} ${v("last")} <${v("email")}>`;
    location.href = `mailto:info@pimagicstudio.com?subject=${encodeURIComponent("PiMagic Studio: " + v("topic"))}&body=${encodeURIComponent(body)}`; }); })();

/* ---------- counters ---------- */
$$("[data-count]").forEach(el => new IntersectionObserver((es, o) => { if (!es[0].isIntersecting || reduce) return; o.disconnect();
  const n = +el.dataset.count, t0 = performance.now(); const f = t => { const u = clamp((t - t0) / 1200); el.textContent = Math.round(n * ease(u)); if (u < 1) requestAnimationFrame(f); }; requestAnimationFrame(f); }, { threshold: .6 }).observe(el));
})();
