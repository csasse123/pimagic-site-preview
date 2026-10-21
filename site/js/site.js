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
$(".pm-burger").addEventListener("click", e => { const o = nav.classList.toggle("open"); e.currentTarget.setAttribute("aria-expanded", o); });
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
  const set = f => { f = clamp(f, 0, 1); before.style.clipPath = `inset(0 ${(1 - f) * 100}% 0 0)`; h.style.left = f * 100 + "%"; h.setAttribute("aria-valuenow", Math.round(f * 100)); ba._f = f; };
  set(+ba.dataset.start || .5);
  const at = e => { const r = ba.getBoundingClientRect(); set((e.clientX - r.left) / r.width); };
  let drag = false;
  ba.addEventListener("pointerdown", e => { drag = true; ba.setPointerCapture(e.pointerId); at(e); });
  ba.addEventListener("pointermove", e => drag && at(e));
  ba.addEventListener("pointerup", () => drag = false);
  h.addEventListener("keydown", e => { if (e.key === "ArrowLeft") set(ba._f - .05); if (e.key === "ArrowRight") set(ba._f + .05); });
  // a gentle hint the first time it is seen
  const hint = new IntersectionObserver(es => { if (es[0].isIntersecting && !reduce) { hint.disconnect(); let t0 = null;
    const an = t => { t0 ??= t; const u = (t - t0) / 1600; if (u > 1 || drag) return; set(.5 + .22 * Math.sin(u * 6.28)); requestAnimationFrame(an); }; requestAnimationFrame(an); } }, { threshold: .6 });
  hint.observe(ba);
});

/* ---------- films ---------- */
const FILMS = { long: "assets/video/film_long.mp4", short: "assets/video/film_short.mp4" };
const modal = $("#filmModal"), mv = $("video", modal);
const closeModal = m => { m.hidden = true; const v = $("video", m); if (v) { v.pause(); v.removeAttribute("src"); v.load(); } document.body.style.overflow = ""; };
$$("[data-film]").forEach(b => b.addEventListener("click", () => { mv.src = FILMS[b.dataset.film]; modal.hidden = false; document.body.style.overflow = "hidden"; mv.play().catch(() => {}); }));
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

/* ---------- mosaic story: scroll drives found -> placed -> matched -> blended ---------- */
(() => {
  const sec = $(".mosaic-story"); if (!sec) return;
  const panes = $$(".pane", sec), fin = $(".mosaic-final", sec), steps = $$(".mstep li", sec);
  const PW = 47, PH = 47 * 314 / 470;
  const GRID = [[0, 0], [1, 0], [0, 1], [1, 1], [0, 2], [1, 2]].map(([c, r]) => [50 + (c - .5) * PW * .94, 50 + (r - 1) * PH * .94]);
  const SCAT = [[17, 15, -9], [83, 13, 7], [13, 55, 5], [86, 50, -6], [33, 88, 8], [69, 90, -4]];
  const GAIN = [1.45, .62, 1.2, .78, 1.32, .7];
  fin.style.cssText += `left:${50 - .97 * PW}%;top:${50 - 1.44 * PH}%;width:${.97 * PW * 2}%;height:${1.44 * PH * 2}%;object-fit:cover`;
  const render = () => {
    const r = sec.getBoundingClientRect(), p = reduce ? 1 : clamp(-r.top / (r.height - innerHeight));
    const kp = seg(p, .24, .5), km = seg(p, .5, .66), kb = seg(p, .68, .84);
    panes.forEach((el, i) => { const k = seg(p, .02 + i * .03, .12 + i * .03), [sx, sy, a] = SCAT[i], [gx, gy] = GRID[i];
      const x = sx + (gx - sx) * kp, y = sy + (gy - sy) * kp, z = .58 + .42 * kp, gn = GAIN[i] + (1 - GAIN[i]) * km;
      el.style.opacity = k * (1 - kb * .999);
      el.style.transform = `translate(-50%,-50%) rotate(${a * (1 - kp)}deg) scale(${z * (.9 + .1 * k)})`;
      el.style.left = x + "%"; el.style.top = y + "%"; el.style.filter = `brightness(${gn})`; el.style.outlineColor = `rgba(150,210,255,${.4 * (1 - kp) + .12})`; });
    fin.style.opacity = kb; fin.style.transform = `scale(${1 + .03 * seg(p, .84, 1)})`;
    const on = [p > .06, p > .3, p > .53, p > .72]; steps.forEach((s, i) => s.classList.toggle("on", on[i]));
  };
  addEventListener("scroll", () => requestAnimationFrame(render), { passive: true }); addEventListener("resize", render); render();
})();

/* ---------- gallery + lightbox ---------- */
(() => {
  const G = [["veil_nebula", "Veil Nebula", "SHO narrowband"], ["wizard_nebula", "Wizard Nebula", "SHO narrowband · mono"], ["m8", "M8 · Lagoon & Trifid", "Milky Way core"],
    ["elephant_s_trunk", "Elephant's Trunk", "SHO narrowband"], ["soul_nebula", "Soul Nebula", "mosaic"], ["andromeda_galaxy", "Andromeda Galaxy", "RGB"],
    ["tarantula_nebula", "Tarantula Nebula", "SHO narrowband"], ["bode_s_galaxy", "Bode's Galaxy", "LRGB · mono"],
    ["comet_12p_pons_brooks", "Comet 12P/Pons-Brooks", "RGB"], ["lambs_knoll", "Lambs Knoll", "Milky Way nightscape"]];
  const m = $("#masonry"), lb = $("#lightbox"); if (!m) return;
  m.innerHTML = G.map(([k, t, s]) => `<figure class="tile reveal" tabindex="0" data-k="${k}"><img src="assets/img/g_${k}_t.webp" alt="${t} — ${s}, processed by PiMagic" loading="lazy"><figcaption><b>${t}</b><span>${s}</span></figcaption></figure>`).join("");
  $$(".tile", m).forEach(el => { io.observe(el);
    const open = () => { const [k, t, s] = G.find(g => g[0] === el.dataset.k); $("img", lb).src = `assets/img/g_${k}.webp`; $("img", lb).alt = t; $("p", lb).textContent = `${t} · ${s} · PiMagic`; lb.hidden = false; document.body.style.overflow = "hidden"; };
    el.addEventListener("click", open); el.addEventListener("keydown", e => e.key === "Enter" && open()); });
})();

/* ---------- counters ---------- */
$$("[data-count]").forEach(el => new IntersectionObserver((es, o) => { if (!es[0].isIntersecting || reduce) return; o.disconnect();
  const n = +el.dataset.count, t0 = performance.now(); const f = t => { const u = clamp((t - t0) / 1200); el.textContent = Math.round(n * ease(u)); if (u < 1) requestAnimationFrame(f); }; requestAnimationFrame(f); }, { threshold: .6 }).observe(el));
})();
