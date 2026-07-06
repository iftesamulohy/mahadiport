/* Theme toggle: light/dark with localStorage + cookie persistence.
 * The cookie lets Django render the correct data-theme server-side,
 * and the inline <head> script sets it before paint (no flash). */
(function () {
  "use strict";

  var root = document.documentElement;

  function current() {
    return root.getAttribute("data-theme") === "dark" ? "dark" : "light";
  }

  function persist(theme) {
    try { localStorage.setItem("theme", theme); } catch (e) {}
    // 1 year cookie so the server can pre-render the right theme.
    document.cookie =
      "theme=" + theme + ";path=/;max-age=31536000;samesite=lax";
  }

  function syncLabels() {
    var t = current();
    document.querySelectorAll("[data-theme-label]").forEach(function (el) {
      // Label shows the theme you'll switch TO.
      el.textContent = t === "dark" ? "LIGHT" : "DARK";
    });
    document.querySelectorAll("[data-theme-toggle]").forEach(function (el) {
      el.setAttribute("aria-checked", t === "dark" ? "true" : "false");
    });
  }

  function apply(theme) {
    root.setAttribute("data-theme", theme);
    persist(theme);
    syncLabels();
    // Let other modules (e.g. the hero curve) react to a theme change.
    window.dispatchEvent(new CustomEvent("themechange", { detail: { theme: theme } }));
  }

  function toggle() {
    apply(current() === "dark" ? "light" : "dark");
  }

  function init() {
    syncLabels();
    document.querySelectorAll("[data-theme-toggle]").forEach(function (el) {
      el.addEventListener("click", toggle);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
