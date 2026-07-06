/* reveal.js — one IntersectionObserver drives:
 *   - scroll reveals   ([data-reveal] / .reveal)
 *   - count-up numbers  ([data-count])
 *   - skill meter fills  ([data-meter])
 * Plus active-section highlighting in the navbar.
 * Everything degrades to its final state under reduced motion. */
(function () {
  "use strict";

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- count-up ---- */
  function easeOut(t) { return 1 - Math.pow(1 - t, 3); }

  function formatNumber(value, decimals) {
    return value.toFixed(decimals);
  }

  function countUp(el) {
    var to = parseFloat(el.getAttribute("data-count"));
    var from = parseFloat(el.getAttribute("data-count-from") || "0");
    var decimals = parseInt(el.getAttribute("data-decimals") || "0", 10);
    var prefix = el.getAttribute("data-prefix") || "";
    var suffix = el.getAttribute("data-suffix") || "";
    var duration = parseInt(el.getAttribute("data-duration") || "1200", 10);

    if (reduced) { el.textContent = prefix + formatNumber(to, decimals) + suffix; return; }

    var start = null;
    function frame(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / duration, 1);
      var val = from + (to - from) * easeOut(p);
      el.textContent = prefix + formatNumber(val, decimals) + suffix;
      if (p < 1) requestAnimationFrame(frame);
      else el.textContent = prefix + formatNumber(to, decimals) + suffix;
    }
    requestAnimationFrame(frame);
  }

  /* ---- meter fill ---- */
  function fillMeter(el) {
    var pct = parseFloat(el.getAttribute("data-meter")) || 0;
    var bar = el.querySelector("[data-meter-bar]");
    var num = el.querySelector("[data-meter-num]");
    if (reduced) {
      if (bar) bar.style.width = pct + "%";
      if (num) num.textContent = pct + "%";
      return;
    }
    if (bar) requestAnimationFrame(function () { bar.style.width = pct + "%"; });
    if (num) {
      num.setAttribute("data-count", pct);
      num.setAttribute("data-suffix", "%");
      countUp(num);
    }
  }

  /* ---- activate an element that scrolled into view ---- */
  function activate(el) {
    el.classList.add("is-visible");
    el.querySelectorAll("[data-count]:not([data-counted])").forEach(function (n) {
      n.setAttribute("data-counted", "1");
      countUp(n);
    });
    if (el.hasAttribute("data-count") && !el.hasAttribute("data-counted")) {
      el.setAttribute("data-counted", "1");
      countUp(el);
    }
    el.querySelectorAll("[data-meter]:not([data-filled])").forEach(function (m) {
      m.setAttribute("data-filled", "1");
      fillMeter(m);
    });
    if (el.hasAttribute("data-meter") && !el.hasAttribute("data-filled")) {
      el.setAttribute("data-filled", "1");
      fillMeter(el);
    }
  }

  var revealObserver = new IntersectionObserver(function (entries, obs) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        activate(entry.target);
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.18, rootMargin: "0px 0px -40px 0px" });

  /* ---- active nav section highlighting ---- */
  function initSectionSpy() {
    var sections = document.querySelectorAll("section[id]");
    var links = {};
    document.querySelectorAll(".nav__links a").forEach(function (a) {
      var id = a.getAttribute("href").replace("#", "");
      if (id) links[id] = a;
    });
    if (!sections.length) return;
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          Object.values(links).forEach(function (a) { a.classList.remove("is-active"); });
          var link = links[entry.target.id];
          if (link) link.classList.add("is-active");
        }
      });
    }, { threshold: 0.4 });
    sections.forEach(function (s) { spy.observe(s); });
  }

  /* ---- register everything (also for HTMX-swapped content) ---- */
  function register(root) {
    (root || document).querySelectorAll(
      ".reveal, [data-reveal], [data-count], [data-meter]"
    ).forEach(function (el) {
      if (el.hasAttribute("data-observed")) return;
      el.setAttribute("data-observed", "1");
      revealObserver.observe(el);
    });
  }

  function init() {
    register(document);
    initSectionSpy();
  }

  // Re-scan content that HTMX swaps in (skills tabs, case panel).
  document.body && document.body.addEventListener("htmx:afterSwap", function (e) {
    register(e.target);
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Fire Meta Pixel "Contact" on WhatsApp / phone / email clicks (if pixel loaded).
  document.addEventListener("click", function (e) {
    var link = e.target.closest("[data-track-contact]");
    if (link && window.fbq) { try { fbq("track", "Contact"); } catch (err) {} }
  });

  window.__reveal = { register: register };
})();
