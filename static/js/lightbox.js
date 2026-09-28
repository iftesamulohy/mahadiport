/* lightbox.js — full-screen viewer for case-study proof screenshots.
 * Any element with [data-lightbox="<group>"] + data-src opens it; siblings in the
 * same group become prev/next. Delegated on document, so HTMX-loaded drawer
 * content works without re-binding.
 * Keys: ← → navigate, Esc closes (without also closing the case drawer).
 * Touch: swipe left/right to navigate. Click the image to toggle 100% zoom. */
(function () {
  "use strict";

  var box = document.getElementById("lightbox");
  if (!box) return;

  var img = box.querySelector(".lightbox__img");
  var stage = box.querySelector(".lightbox__stage");
  var kindEl = box.querySelector(".lightbox__kind");
  var textEl = box.querySelector(".lightbox__text");
  var countEl = box.querySelector(".lightbox__count");
  var openLink = box.querySelector(".lightbox__open");
  var closeBtn = box.querySelector(".lightbox__close");

  var items = [];
  var index = 0;
  var opener = null;

  function show(i) {
    index = (i + items.length) % items.length;
    var el = items[index];
    var caption = el.getAttribute("data-caption") || "";
    box.classList.remove("is-zoomed", "is-loaded");
    img.onload = function () { box.classList.add("is-loaded"); };
    img.src = el.getAttribute("data-src");
    img.alt = caption || el.getAttribute("data-kind") || "";
    kindEl.textContent = el.getAttribute("data-kind") || "";
    textEl.textContent = caption;
    countEl.textContent = items.length > 1 ? (index + 1) + " / " + items.length : "";
    openLink.href = img.src;
    box.classList.toggle("is-single", items.length < 2);
    stage.scrollTop = stage.scrollLeft = 0;
  }

  function open(trigger) {
    var group = trigger.getAttribute("data-lightbox");
    items = Array.prototype.filter.call(
      document.querySelectorAll("[data-lightbox]"),
      function (el) { return el.getAttribute("data-lightbox") === group; }
    );
    opener = trigger;
    box.hidden = false;
    document.documentElement.classList.add("lightbox-open");
    show(items.indexOf(trigger));
    requestAnimationFrame(function () { box.classList.add("is-open"); });
    closeBtn.focus({ preventScroll: true });
  }

  function close() {
    box.classList.remove("is-open", "is-zoomed");
    document.documentElement.classList.remove("lightbox-open");
    box.hidden = true;
    img.removeAttribute("src");
    if (opener && document.contains(opener)) opener.focus({ preventScroll: true });
    opener = null;
  }

  document.addEventListener("click", function (e) {
    var trigger = e.target.closest("[data-lightbox]");
    if (trigger) { e.preventDefault(); open(trigger); return; }
    if (box.hidden) return;
    if (e.target.closest("[data-lb-close]")) close();
    else if (e.target.closest("[data-lb-prev]")) show(index - 1);
    else if (e.target.closest("[data-lb-next]")) show(index + 1);
    else if (e.target === img) box.classList.toggle("is-zoomed");
    else if (e.target === stage) close();
  });

  // Registered on document so stopPropagation keeps Esc from reaching the
  // drawer's window-level Alpine listener.
  document.addEventListener("keydown", function (e) {
    if (box.hidden) return;
    if (e.key === "Escape") { e.stopPropagation(); close(); }
    else if (e.key === "ArrowLeft") show(index - 1);
    else if (e.key === "ArrowRight") show(index + 1);
    else if (e.key === "Tab") {
      // Keep focus inside the dialog.
      var f = box.querySelectorAll("button:not([hidden]), a[href]");
      var visible = Array.prototype.filter.call(f, function (el) { return el.offsetParent; });
      var first = visible[0], last = visible[visible.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });

  var touchX = null;
  box.addEventListener("touchstart", function (e) {
    touchX = e.touches.length === 1 ? e.touches[0].clientX : null;
  }, { passive: true });
  box.addEventListener("touchend", function (e) {
    if (touchX === null || box.classList.contains("is-zoomed") || items.length < 2) return;
    var dx = e.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) > 50) show(index + (dx < 0 ? 1 : -1));
    touchX = null;
  });
})();
