(function () {
  var COPY_LABEL = "Copy to OP TCG SIM";

  function textList(root) {
    return Array.prototype.map.call(root.querySelectorAll(".text-line"), function (line) {
      var qty = (line.querySelector(".qty") || {}).textContent || "";
      var id = (line.querySelector(".card-id") || {}).textContent || "";
      qty = qty.replace(/\s+/g, "");
      id = id.trim();
      if (!qty || !id) return "";
      if (qty.slice(-1) !== "x") qty += "x";
      return qty + id;
    }).filter(Boolean).join("\n");
  }

  function simText(btn) {
    var raw = btn.getAttribute("data-sim");
    if (raw && raw.trim()) return raw.trim().split(/\s+/).join("\n");
    var root = btn.closest(".text-deck") || document;
    return textList(root);
  }

  function initCopy() {
    document.querySelectorAll("[data-copy-sim]").forEach(function (btn) {
      if (btn.dataset.bound) return;
      btn.dataset.bound = "1";
      if (btn.textContent.replace(/\s+/g, " ").trim() === "Copy for sim") {
        btn.textContent = COPY_LABEL;
      }
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        var text = simText(btn);
        if (!text) return;
        var done = function () {
          var prev = btn.textContent;
          btn.textContent = "Copied";
          setTimeout(function () { btn.textContent = prev; }, 1400);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(done).catch(function () {
            window.prompt("Copy this list for OP TCG SIM", text);
          });
        } else {
          window.prompt("Copy this list for OP TCG SIM", text);
        }
      });
    });
  }

  function ensureCopyButtons() {
    document.querySelectorAll(".text-deck .section-title").forEach(function (title) {
      var existing = title.querySelector("[data-copy-sim]");
      if (existing) {
        if (existing.textContent.replace(/\s+/g, " ").trim() === "Copy for sim") {
          existing.textContent = COPY_LABEL;
        }
        return;
      }
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "copy-sim";
      btn.setAttribute("data-copy-sim", "");
      btn.textContent = COPY_LABEL;
      title.appendChild(btn);
    });
  }

  function initFilters() {
    document.querySelectorAll("[data-hub-filters]").forEach(function (bar) {
      if (bar.dataset.bound) return;
      bar.dataset.bound = "1";
      var section = bar.closest(".deck-index");
      if (!section) return;
      var items = section.querySelectorAll("ul.list > li");
      var countEl = section.querySelector(".section-title .muted");
      var total = items.length;
      function apply() {
        var q = ((bar.querySelector("[data-filter=q]") || {}).value || "").toLowerCase();
        var when = (bar.querySelector("[data-filter=when]") || {}).value || "";
        var place = (bar.querySelector("[data-filter=place]") || {}).value || "";
        var event = (bar.querySelector("[data-filter=event]") || {}).value || "";
        var shown = 0;
        items.forEach(function (li) {
          var hay = (li.textContent || "").toLowerCase();
          var date = li.getAttribute("data-date") || "";
          var placing = parseInt(li.getAttribute("data-placing") || "9999", 10);
          var bucket = li.getAttribute("data-event") || "other";
          var ok = true;
          if (q && hay.indexOf(q) < 0) ok = false;
          if (when === "jul" && date < "2026-07-01") ok = false;
          if (when === "aug" && date < "2026-08-01") ok = false;
          if (place === "top8" && placing > 8) ok = false;
          if (place === "win" && placing !== 1) ok = false;
          if (event && bucket !== event) ok = false;
          li.hidden = !ok;
          if (ok) shown += 1;
        });
        if (countEl) countEl.textContent = shown === total ? total + " lists" : shown + " of " + total;
      }
      bar.addEventListener("input", apply);
      bar.addEventListener("change", apply);
    });
  }

  function ready() {
    ensureCopyButtons();
    initCopy();
    initFilters();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", ready);
  else ready();
})();
