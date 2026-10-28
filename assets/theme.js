// Theme switch: follows the system until the visitor picks light or dark; the choice stays in this browser only.
(function () {
  var root = document.documentElement;
  var button = document.querySelector(".theme-toggle");
  if (!button) return;

  var system = window.matchMedia("(prefers-color-scheme: dark)");
  var metas = Array.prototype.slice.call(document.querySelectorAll('meta[name="theme-color"]'));
  var colors = {};
  metas.forEach(function (meta) {
    colors[(meta.getAttribute("media") || "").indexOf("dark") >= 0 ? "dark" : "light"] = meta.getAttribute("content");
  });

  function current() {
    return root.getAttribute("data-theme") || (system.matches ? "dark" : "light");
  }

  function syncBrowserChrome() {
    var theme = root.getAttribute("data-theme");
    metas.forEach(function (meta) {
      var own = (meta.getAttribute("media") || "").indexOf("dark") >= 0 ? "dark" : "light";
      meta.setAttribute("content", colors[theme || own]);
    });
    button.setAttribute("aria-pressed", current() === "dark" ? "true" : "false");
  }

  function apply(theme) {
    root.setAttribute("data-theme", theme);
    try {
      localStorage.setItem("theme", theme);
    } catch (e) {}
    syncBrowserChrome();
  }

  // The new theme opens as a circle growing from the button (View Transitions); otherwise it just switches.
  button.addEventListener("click", function () {
    var next = current() === "dark" ? "light" : "dark";
    var calm = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!document.startViewTransition || calm) {
      apply(next);
      return;
    }
    var box = button.getBoundingClientRect();
    var x = box.left + box.width / 2;
    var y = box.top + box.height / 2;
    var radius = Math.hypot(Math.max(x, window.innerWidth - x), Math.max(y, window.innerHeight - y));
    root.classList.add("theme-switching");
    var transition = document.startViewTransition(function () { apply(next); });
    transition.ready.then(function () {
      root.animate(
        { clipPath: ["circle(0 at " + x + "px " + y + "px)", "circle(" + radius + "px at " + x + "px " + y + "px)"] },
        { duration: 620, easing: "cubic-bezier(0.2, 0.7, 0.2, 1)", pseudoElement: "::view-transition-new(root)" }
      );
    });
    transition.finished.then(function () { root.classList.remove("theme-switching"); });
  });

  syncBrowserChrome();
})();
