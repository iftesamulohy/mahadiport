/* curve.js — the signature live ad-performance chart.
 * Pure SVG path manipulation, no libraries. Two lines (ROAS up, CPL down),
 * a sliding window, ticking chips, a pulsing tip dot, a hover crosshair,
 * and a CTA-hover "boost". Degrades to a static drawing under reduced motion. */
(function () {
  "use strict";

  var root = document.querySelector("[data-curve]");
  if (!root) return;

  var svg = root.querySelector("[data-curve-svg]");
  var gridG = root.querySelector("[data-curve-grid]");
  var areaP = root.querySelector("[data-curve-area]");
  var roasP = root.querySelector("[data-curve-roas]");
  var cplP = root.querySelector("[data-curve-cpl]");
  var tip = root.querySelector("[data-curve-tip]");
  var cross = root.querySelector("[data-curve-cross]");
  var crossLine = root.querySelector("[data-cross-line]");
  var crossDot = root.querySelector("[data-cross-dot]");
  var tooltip = root.querySelector("[data-curve-tooltip]");
  var roasChip = root.querySelector("[data-chip-roas]");
  var cplChip = root.querySelector("[data-chip-cpl]");

  // Plot geometry (in the 600x320 viewBox).
  var L = 44, R = 584, T = 28, B = 286;
  var VISIBLE = 22;                 // points visible across the width
  var N = VISIBLE + 2;              // + off-screen point each side
  var DX = (R - L) / (VISIBLE - 1);
  var STEP = 900;                   // ms between new data points

  var roasMin = 1.4, roasMax = 5.2;
  // CPL in USD — Meta ad budgets are managed in dollars (local + foreign clients).
  var cplMin = 2.4, cplMax = 12.5;

  function clamp(v, lo, hi) { return v < lo ? lo : v > hi ? hi : v; }
  function yR(v) { return B - (clamp(v, roasMin, roasMax) - roasMin) / (roasMax - roasMin) * (B - T); }
  // CPL: high value sits high on the chart so a falling value draws a descending line.
  function yC(v) { return T + (clamp(v, cplMin, cplMax) - cplMin) / (cplMax - cplMin) * (B - T); }

  // ---- data: rolling arrays of values -------------------------------------
  var roas = [], cpl = [];
  (function seed() {
    var rv = 1.9, cv = 9.6;
    for (var i = 0; i < N; i++) {
      rv = clamp(rv + 0.11 + (Math.random() - 0.45) * 0.22, roasMin, roasMax);
      cv = clamp(cv - 0.18 + (Math.random() - 0.5) * 0.5, cplMin, cplMax);
      roas.push(rv); cpl.push(cv);
    }
  })();

  var driftBoost = 0;   // temporary extra upward drift on CTA hover

  function pushPoint() {
    var lastR = roas[roas.length - 1];
    var lastC = cpl[cpl.length - 1];
    // ROAS: random walk with gentle positive drift (+ optional boost).
    var nr = lastR + 0.05 + driftBoost + (Math.random() - 0.5) * 0.5;
    // Mean-revert so it wanders around the upper band instead of pinning.
    if (nr > roasMax - 0.3) nr -= 0.6;
    // CPL: random walk with negative drift (USD scale).
    var nc = lastC - 0.08 + (Math.random() - 0.5) * 1.3;
    if (nc < cplMin + 0.5) nc += 1.8;
    roas.push(clamp(nr, roasMin, roasMax));
    cpl.push(clamp(nc, cplMin, cplMax));
    roas.shift(); cpl.shift();
  }

  // ---- smoothing: Catmull-Rom -> cubic bezier path ------------------------
  function smoothPath(pts) {
    if (pts.length < 2) return "";
    var d = "M" + pts[0][0].toFixed(1) + "," + pts[0][1].toFixed(1);
    for (var i = 0; i < pts.length - 1; i++) {
      var p0 = pts[i - 1] || pts[i];
      var p1 = pts[i];
      var p2 = pts[i + 1];
      var p3 = pts[i + 2] || p2;
      var c1x = p1[0] + (p2[0] - p0[0]) / 6;
      var c1y = p1[1] + (p2[1] - p0[1]) / 6;
      var c2x = p2[0] - (p3[0] - p1[0]) / 6;
      var c2y = p2[1] - (p3[1] - p1[1]) / 6;
      d += "C" + c1x.toFixed(1) + "," + c1y.toFixed(1) + " " +
           c2x.toFixed(1) + "," + c2y.toFixed(1) + " " +
           p2[0].toFixed(1) + "," + p2[1].toFixed(1);
    }
    return d;
  }

  function points(vals, yFn, shift) {
    var pts = [];
    for (var i = 0; i < vals.length; i++) {
      pts.push([L + (i - 1 - shift) * DX, yFn(vals[i])]);
    }
    return pts;
  }

  function drawGrid() {
    var frag = "";
    for (var r = 0; r <= 4; r++) {
      var y = T + (B - T) * r / 4;
      frag += '<line x1="' + L + '" y1="' + y.toFixed(1) + '" x2="' + R +
              '" y2="' + y.toFixed(1) + '"/>';
    }
    for (var c = 0; c <= 4; c++) {
      var x = L + (R - L) * c / 4;
      frag += '<line x1="' + x.toFixed(1) + '" y1="' + T + '" x2="' + x.toFixed(1) +
              '" y2="' + B + '"/>';
    }
    gridG.innerHTML = frag;
  }

  // Latest on-screen values track the tip (second-to-last real point).
  function tipIndex() { return N - 2; }

  function render(shift) {
    var rp = points(roas, yR, shift);
    var cp = points(cpl, yC, shift);
    roasP.setAttribute("d", smoothPath(rp));
    cplP.setAttribute("d", smoothPath(cp));
    // Area under ROAS.
    var area = smoothPath(rp) + "L" + rp[rp.length - 1][0].toFixed(1) + "," + B +
               "L" + rp[0][0].toFixed(1) + "," + B + "Z";
    areaP.setAttribute("d", area);
    // Tip dot rides the ROAS line at the last fully-visible point.
    var ti = tipIndex();
    tip.setAttribute("transform", "translate(" + rp[ti][0].toFixed(1) + "," + rp[ti][1].toFixed(1) + ")");
  }

  function updateChips() {
    var ti = tipIndex();
    if (roasChip) roasChip.textContent = roas[ti].toFixed(1) + "x";
    if (cplChip) cplChip.textContent = "$" + cpl[ti].toFixed(2);
  }

  // ---- reduced motion: draw once, static ----------------------------------
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduced) {
    drawGrid();
    render(0);
    updateChips();
    return;
  }

  // ---- animation loop -----------------------------------------------------
  drawGrid();
  var shift = 0, last = null, acc = 0;

  function frame(ts) {
    if (last === null) last = ts;
    var dt = ts - last; last = ts;
    acc += dt;
    shift += dt / STEP;
    while (shift >= 1) {
      shift -= 1;
      pushPoint();
    }
    if (driftBoost > 0) driftBoost = Math.max(0, driftBoost - dt / 2000 * 0.18);
    render(shift);
    if (acc > 120) { updateChips(); acc = 0; }
    raf = requestAnimationFrame(frame);
  }
  var raf = requestAnimationFrame(frame);

  // Pause when off-screen to save cycles.
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (e.isIntersecting && raf === null) { last = null; raf = requestAnimationFrame(frame); }
      else if (!e.isIntersecting && raf !== null) { cancelAnimationFrame(raf); raf = null; }
    });
  }, { threshold: 0 });
  io.observe(root);

  // ---- theme change: area gradient uses currentColor vars, redraw grid ----
  window.addEventListener("themechange", function () { drawGrid(); });

  // ---- CTA hover boost ----------------------------------------------------
  document.querySelectorAll("[data-boost-curve]").forEach(function (el) {
    var trigger = function () { driftBoost = 0.18; };
    el.addEventListener("mouseenter", trigger);
    el.addEventListener("focus", trigger);
  });

  // ---- hover crosshair + tooltip ------------------------------------------
  function svgX(clientX) {
    var rect = svg.getBoundingClientRect();
    return (clientX - rect.left) / rect.width * 600;
  }
  function onMove(clientX) {
    var x = clamp(svgX(clientX), L, R);
    var idx = Math.round((x - L) / DX) + 1;   // map to a data slot
    idx = clamp(idx, 1, N - 2);
    var day = clamp(Math.round((x - L) / (R - L) * 29) + 1, 1, 30);
    var px = L + (idx - 1) * DX;
    cross.classList.add("is-on");
    crossLine.setAttribute("x1", px); crossLine.setAttribute("x2", px);
    crossDot.setAttribute("cx", px); crossDot.setAttribute("cy", yR(roas[idx]));
    tooltip.hidden = false;
    tooltip.textContent = "Day " + day + " · ROAS " + roas[idx].toFixed(1) +
                          "x · CPL $" + cpl[idx].toFixed(2);
    var rect = svg.getBoundingClientRect();
    tooltip.style.left = (px / 600 * rect.width) + "px";
  }
  function hideCross() { cross.classList.remove("is-on"); tooltip.hidden = true; }

  svg.addEventListener("mousemove", function (e) { onMove(e.clientX); });
  svg.addEventListener("mouseleave", hideCross);
  svg.addEventListener("touchmove", function (e) {
    if (e.touches[0]) onMove(e.touches[0].clientX);
  }, { passive: true });
  svg.addEventListener("touchend", hideCross);
})();
