// Interactive export demo on the Orlo page: the quality slider and presets change the file size estimate,
// formatted like the app does it (decimal units, "≈", one decimal from 1 to 10 MB).
(function () {
  var meter = document.querySelector("[data-meter]");
  if (!meter) return;

  var range = meter.querySelector(".meter-range");
  var number = meter.querySelector(".mv-num");
  var unit = meter.querySelector(".mv-unit");
  var level = meter.querySelector(".mv-level");
  var chips = Array.prototype.slice.call(meter.querySelectorAll(".chips button"));
  var dots = Array.prototype.slice.call(meter.querySelectorAll(".meter-dots i"));
  var sizes = meter.getAttribute("data-sizes").split("|").map(Number);
  var levels = meter.getAttribute("data-levels").split("|");
  var units = meter.getAttribute("data-units").split("|");
  var comma = meter.getAttribute("data-decimal");

  function format(bytes) {
    if (bytes < 1000) return [String(Math.round(bytes)), units[0]];
    if (bytes < 1000000) return [String(Math.round(bytes / 1000)), units[1]];
    var mb = bytes / 1000000;
    var text = mb < 10 ? (Math.round(mb * 10) / 10).toString() : String(Math.round(mb));
    return [text.replace(".", comma), units[2]];
  }

  var shown = sizes[Number(range.value)];
  var frame = 0;

  function show(bytes) {
    var parts = format(bytes);
    number.textContent = parts[0];
    unit.textContent = parts[1];
  }

  function animateTo(target) {
    cancelAnimationFrame(frame);
    var from = shown;
    var start = performance.now();
    var calm = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var duration = calm ? 0 : 420;
    function step(now) {
      var t = duration ? Math.min(1, (now - start) / duration) : 1;
      var eased = 1 - Math.pow(1 - t, 3);
      shown = from + (target - from) * eased;
      show(shown);
      if (t < 1) frame = requestAnimationFrame(step);
    }
    frame = requestAnimationFrame(step);
  }

  function update(fromChip) {
    var i = Number(range.value);
    range.style.setProperty("--p", (i / (sizes.length - 1)) * 100 + "%");
    range.setAttribute("aria-valuetext", levels[i] + ", ≈ " + format(sizes[i]).join(" "));
    level.textContent = levels[i];
    dots.forEach(function (dot, d) { dot.classList.toggle("on", d <= i); });
    if (!fromChip) {
      chips.forEach(function (chip) {
        if (chip.classList.contains("on") && Number(chip.getAttribute("data-level")) !== i) {
          chip.classList.remove("on");
          chip.setAttribute("aria-pressed", "false");
        }
      });
    }
    animateTo(sizes[i]);
  }

  range.addEventListener("input", function () {
    meter.classList.add("is-touched");
    update(false);
  });

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      chips.forEach(function (other) {
        other.classList.toggle("on", other === chip);
        other.setAttribute("aria-pressed", other === chip ? "true" : "false");
      });
      range.value = chip.getAttribute("data-level");
      meter.classList.add("is-touched");
      update(true);
    });
  });

  meter.classList.add("is-live");
  update(true);
})();
