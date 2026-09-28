/* Sidebar active-state fix for django-bangla-admin 0.3.1:
 *  - its {% ba_is_active %} tag emits "active" without a leading space, so the
 *    server-rendered class becomes "ba-nav-itemactive" (item loses its styles);
 *  - both the tag and its JS use prefix matching, so the Dashboard link
 *    ("/admin/") is marked active on every admin page.
 * Runs after the package's own sync (load + every HTMX navigation). */
(function () {
  "use strict";

  function fix() {
    var path = window.location.pathname;
    var items = document.querySelectorAll(".ba-nav a");
    var best = null;
    items.forEach(function (a) {
      if (a.classList.contains("ba-nav-itemactive")) {
        a.classList.remove("ba-nav-itemactive");
        a.classList.add("ba-nav-item");
      }
      var href = a.getAttribute("href");
      if (href && href !== "#" && path.indexOf(href) === 0 &&
          (!best || href.length > best.getAttribute("href").length)) {
        best = a;
      }
    });
    // Only the longest matching link is active (Dashboard only on /admin/).
    items.forEach(function (a) { a.classList.toggle("active", a === best); });
  }

  function later() { setTimeout(fix, 0); }
  document.addEventListener("DOMContentLoaded", later);
  document.addEventListener("htmx:afterSettle", later);
  window.addEventListener("popstate", later);
})();
