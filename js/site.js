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

  function initSiteSearch() {
    var params = new URLSearchParams(window.location.search);
    var q = (params.get("q") || "").trim();
    document.querySelectorAll('form.site-search input[name="q"]').forEach(function (input) {
      if (!input.value) input.value = q;
    });
    if (!document.querySelector("[data-search-group]")) return;
    var needle = q.toLowerCase();
    var status = document.getElementById("search-status");
    var shown = 0;
    document.querySelectorAll("[data-search-group]").forEach(function (group) {
      var any = 0;
      group.querySelectorAll("li[data-q]").forEach(function (li) {
        var hay = ((li.getAttribute("data-q") || "") + " " + (li.textContent || "")).toLowerCase();
        var ok = !needle || hay.indexOf(needle) >= 0;
        li.hidden = !ok;
        if (ok) {
          any += 1;
          shown += 1;
        }
      });
      group.hidden = !any;
    });
    var extraWrap = document.querySelector("[data-search-extra]");
    var extraList = document.querySelector("[data-extra-results]");
    var extraCount = document.querySelector("[data-extra-count]");
    var extraShown = 0;
    if (extraWrap && extraList && needle) {
      extraList.innerHTML = "";
      var blob = document.getElementById("search-lists");
      var rows = [];
      try { rows = blob ? JSON.parse(blob.textContent || "[]") : []; } catch (e) { rows = []; }
      var seen = {};
      document.querySelectorAll("[data-search-group] a.item").forEach(function (a) {
        seen[a.getAttribute("href")] = 1;
      });
      rows.forEach(function (row) {
        if (extraShown >= 40) return;
        var hay = ((row.q || "") + " " + (row.t || "") + " " + (row.n || "")).toLowerCase();
        if (hay.indexOf(needle) < 0) return;
        if (seen[row.h]) return;
        seen[row.h] = 1;
        extraShown += 1;
        var li = document.createElement("li");
        var a = document.createElement("a");
        a.className = "item";
        a.href = row.h;
        var copy = document.createElement("div");
        var title = document.createElement("div");
        title.style.fontWeight = "700";
        title.textContent = row.t || "List";
        var note = document.createElement("div");
        note.className = "muted";
        note.style.fontSize = "13px";
        note.textContent = row.n || "";
        copy.appendChild(title);
        copy.appendChild(note);
        var link = document.createElement("div");
        link.className = "link";
        link.textContent = "Open →";
        a.appendChild(copy);
        a.appendChild(link);
        li.appendChild(a);
        extraList.appendChild(li);
      });
      extraWrap.hidden = extraShown === 0;
      if (extraCount) extraCount.textContent = extraShown ? extraShown + " lists" : "";
    } else if (extraWrap) {
      extraWrap.hidden = true;
    }
    if (status) {
      if (!needle) {
        status.hidden = true;
      } else {
        status.hidden = false;
        status.textContent = "Showing " + (shown + extraShown) + " matches for “" + q + "”.";
      }
    }
  }

  var THEME_KEY = "opdb-theme";
  var MOON_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 14.5A8.5 8.5 0 1 1 9.5 3 7 7 0 0 0 21 14.5z"/></svg>';
  var SUN_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';

  function themeStored() {
    try { return localStorage.getItem(THEME_KEY); } catch (e) { return null; }
  }

  function themeCurrent() {
    var t = document.documentElement.getAttribute("data-theme");
    if (t === "dark" || t === "light") return t;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function applyTheme(theme, persist) {
    document.documentElement.setAttribute("data-theme", theme);
    if (persist) {
      try { localStorage.setItem(THEME_KEY, theme); } catch (e) {}
    }
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", theme === "dark" ? "#121416" : "#b71c1c");
    var btn = document.querySelector("[data-theme-toggle]");
    if (!btn) return;
    var dark = theme === "dark";
    btn.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
    btn.setAttribute("title", dark ? "Light mode" : "Dark mode");
    btn.innerHTML = dark ? SUN_SVG : MOON_SVG;
  }

  function initTheme() {
    var header = document.querySelector("header");
    if (header && !document.querySelector("[data-theme-toggle]")) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "theme-toggle";
      btn.setAttribute("data-theme-toggle", "");
      btn.addEventListener("click", function () {
        applyTheme(themeCurrent() === "dark" ? "light" : "dark", true);
      });
      header.appendChild(btn);
    }
    var saved = themeStored();
    applyTheme(saved === "dark" || saved === "light" ? saved : themeCurrent(), false);
  }

  var NEW_SITE = "https://onepiecedecklists.com";

  function movedUrl() {
    return NEW_SITE + location.pathname + location.search + location.hash;
  }

  function initMoveNotice() {
    if (document.querySelector("[data-move-banner]")) return;
    var wrap = document.querySelector(".wrap");
    if (!wrap) return;
    var a = document.createElement("a");
    a.className = "move-banner";
    a.setAttribute("data-move-banner", "");
    a.href = movedUrl();
    a.textContent = "This site is dormant. Open this page on OnePieceDeckLists.com →";
    wrap.insertBefore(a, wrap.firstChild);
  }

  function redirectMoved() {
    location.replace(movedUrl());
  }

  function ready() {
    initMoveNotice();
    redirectMoved();
    initTheme();
    ensureCopyButtons();
    initCopy();
    initFilters();
    initSiteSearch();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", ready);
  else ready();
})();
