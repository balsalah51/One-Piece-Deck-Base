(function () {
  var FALLBACK_PARTNER = "https://partner.tcgplayer.com/c/7670706/1780961/21018";
  var CFG = window.OPDB_TCGPLAYER || {};
  var IDS = window.OPDB_TCGPLAYER_IDS || {};
  // Used to translate each list card into TCGplayer Mass Entry's
  // expected line: "<qty> <name> [<SET>] <FULL-ID>".
  var CARD_CACHE = null;
  var PRODUCT_LINE = "One Piece Card Game";
  var SEARCH_LINE = "one-piece-card-game";
  var REL = "noopener nofollow sponsored";
  var ID_RE = /((?:OP|ST|EB|PRB)\d{2}-\d{3}|P-\d{3})/i;
  var SIM_RE = /(\d+)\s*[x×]\s*((?:OP|ST|EB|PRB)\d{2}-\d{3}|P-\d{3})/gi;

  function partnerLink() {
    return (CFG.partnerLink || FALLBACK_PARTNER).trim() || FALLBACK_PARTNER;
  }

  function affiliate(dest) {
    if (!dest) return dest;
    if (dest.indexOf("partner.tcgplayer.com") >= 0) return dest;
    var base = partnerLink();
    return base + (base.indexOf("?") >= 0 ? "&" : "?") + "u=" + encodeURIComponent(dest);
  }

  function normalizeCacheName(name) {
    // card-cache.json uses dots for multi-part names (Monkey.D.Luffy).
    // Mass Entry wants the printed name (Monkey D. Luffy).
    name = String(name || "");
    if (!name) return "";
    var s = name.replace(/\./g, " ");
    s = s.replace(/\bD\b/g, "D.");
    return s.replace(/\s+/g, " ").trim();
  }

  function displayName(given, cid) {
    var pageName = String(given || "").replace(/\s+/g, " ").trim();
    if (pageName) return pageName;
    var meta = CARD_CACHE && CARD_CACHE[cid] ? CARD_CACHE[cid] : null;
    return meta && meta.name ? normalizeCacheName(meta.name) : "";
  }

  function cardUrl(cid) {
    cid = (cid || "").toUpperCase();
    var pid = IDS[cid];
    if (pid) return "https://www.tcgplayer.com/product/" + pid;
    return "https://www.tcgplayer.com/search/" + SEARCH_LINE + "/product?q=" +
      encodeURIComponent(cid) + "&productLineName=" + encodeURIComponent(SEARCH_LINE);
  }

  function massUrl(cards) {
    var parts = [];
    var seen = {};
    cards.forEach(function (row) {
      var qty = row[0];
      var cid = (row[1] || "").toUpperCase();
      if (!qty || !cid || seen[cid]) return;
      seen[cid] = 1;
      // TCGplayer Mass Entry format for whatever card is on the list:
      //   <qty> <name> [<SET>] <FULL-ID>
      var setCode = cid.indexOf("-") >= 0 ? cid.split("-")[0] : cid;
      var name = displayName(row[2], cid);
      if (name) {
        parts.push(qty + " " + name + " [" + setCode + "] " + cid);
      } else {
        parts.push(qty + " " + cid);
      }
    });
    if (!parts.length) return "";
    return "https://www.tcgplayer.com/massentry?productline=" +
      encodeURIComponent(PRODUCT_LINE) + "&c=" + encodeURIComponent(parts.join("||"));
  }

  function parseSim(text) {
    var cards = [];
    var seen = {};
    var m;
    SIM_RE.lastIndex = 0;
    while ((m = SIM_RE.exec(text || ""))) {
      var cid = m[2].toUpperCase();
      if (seen[cid]) continue;
      seen[cid] = 1;
      cards.push([parseInt(m[1], 10), cid]);
    }
    return cards;
  }

  function cardsFromTextDeck(root) {
    var cards = [];
    var seen = {};
    Array.prototype.forEach.call((root || document).querySelectorAll(".text-line"), function (line) {
      var qty = parseInt(((line.querySelector(".qty") || {}).textContent || "").replace(/\D/g, ""), 10);
      var cid = cidFrom(line.querySelector(".card-id")) || cidFrom(line);
      var name = ((line.querySelector(".card-title") || {}).textContent || "").trim();
      if (!qty || !cid || seen[cid]) return;
      seen[cid] = 1;
      cards.push([qty, cid, name]);
    });
    return cards;
  }

  function buyLink(href, label, className) {
    var a = document.createElement("a");
    a.className = className;
    a.href = affiliate(href);
    a.target = "_blank";
    a.rel = REL;
    a.textContent = label;
    a.addEventListener("click", function (e) { e.stopPropagation(); });
    return a;
  }

  function cidFrom(el) {
    var text = (el && el.textContent) || "";
    var m = text.match(ID_RE);
    return m ? m[1].toUpperCase() : "";
  }

  function addListButtons() {
    document.querySelectorAll(".text-deck .section-title").forEach(function (title) {
      if (title.querySelector(".buy-tcg")) return;
      var root = title.closest(".text-deck");
      var href = massUrl(cardsFromTextDeck(root));
      if (!href) return;
      title.appendChild(buyLink(href, "Buy list on TCGplayer", "buy-tcg"));
    });
    document.querySelectorAll(".text-deck > p.muted").forEach(function (p) {
      if (p.dataset.tcgNote) return;
      p.dataset.tcgNote = "1";
      p.appendChild(document.createTextNode(" Buy list opens TCGplayer Mass Entry. Individual Buy links open that printing when TCGplayer has it. TCGplayer links are affiliate links."));
    });
  }

  function addHubButtons() {
    document.querySelectorAll(".list-row").forEach(function (row) {
      if (row.querySelector(".buy-tcg")) return;
      var btn = row.querySelector("[data-copy-sim]");
      var sim = btn ? btn.getAttribute("data-sim") : "";
      var href = massUrl(parseSim(sim || ""));
      if (!href) return;
      row.appendChild(buyLink(href, "Buy on TCGplayer", "buy-tcg"));
    });
  }

  function addCardButtons() {
    document.querySelectorAll(".text-line").forEach(function (line) {
      if (line.querySelector(".buy-tcg-inline")) return;
      var cid = cidFrom(line.querySelector(".card-id")) || cidFrom(line);
      if (!cid) return;
      line.appendChild(buyLink(cardUrl(cid), "Buy", "buy-tcg-inline"));
    });
    document.querySelectorAll(".card-entry").forEach(function (entry) {
      if (entry.querySelector(".buy-tcg-inline")) return;
      var cid = cidFrom(entry.querySelector(".id")) || cidFrom(entry);
      if (!cid) return;
      var wrap = entry.querySelector("div") || entry;
      wrap.appendChild(buyLink(cardUrl(cid), "Buy on TCGplayer", "buy-tcg-inline"));
    });
  }

  function ready() {
    addListButtons();
    addHubButtons();
    addCardButtons();
  }

  function boot() {
    Promise.all([
      fetch("/data/tcgplayer.json", { cache: "no-store" })
        .then(function (r) { return r.ok ? r.json() : {}; })
        .catch(function () { return {}; }),
      fetch("/data/card-cache.json", { cache: "no-store" })
        .then(function (r) { return r.ok ? r.json() : null; })
        .catch(function () { return null; }),
    ]).then(function (results) {
      var cfg = results[0] || {};
      var cc = results[1];
      if (cfg && cfg.partnerLink) CFG.partnerLink = String(cfg.partnerLink);
      if (cc) CARD_CACHE = cc;
      ready();
    }).catch(function () { ready(); });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
