(function () {
  var CFG = window.OPDB_TCGPLAYER || {};
  var IDS = window.OPDB_TCGPLAYER_IDS || {};
  var PRODUCT_LINE = "One Piece Card Game";
  var SEARCH_LINE = "one-piece-card-game";
  var REL = "noopener nofollow sponsored";
  var ID_RE = /((?:OP|ST|EB|PRB)\d{2}-\d{3}|P-\d{3})/i;
  var SIM_RE = /(\d+)\s*[x×]\s*((?:OP|ST|EB|PRB)\d{2}-\d{3}|P-\d{3})/gi;

  function partnerLink() {
    return (CFG.partnerLink || "").trim();
  }

  function affiliate(dest) {
    var base = partnerLink();
    if (!base) return dest;
    return base + (base.indexOf("?") >= 0 ? "&" : "?") + "u=" + encodeURIComponent(dest);
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
      parts.push(qty + " " + cid);
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

  function textList(root) {
    return Array.prototype.map.call((root || document).querySelectorAll(".text-line"), function (line) {
      var qty = ((line.querySelector(".qty") || {}).textContent || "").replace(/\s+/g, "");
      var id = ((line.querySelector(".card-id") || {}).textContent || "").trim();
      if (!qty || !id) return "";
      if (qty.slice(-1) !== "x") qty += "x";
      return qty + id;
    }).filter(Boolean).join(" ");
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

  function isHome() {
    return !!(document.querySelector("main.home") || document.getElementById("recent"));
  }

  function isIndividualDecklist() {
    return !!document.querySelector(".picture-summary") && !!document.querySelector(".text-deck");
  }

  function addListButton() {
    var deck = document.querySelector(".text-deck");
    if (!deck) return;
    var title = deck.querySelector(".section-title");
    if (!title || title.querySelector(".buy-tcg")) return;
    var cards = parseSim(textList(deck));
    var href = massUrl(cards);
    if (!href) return;
    title.appendChild(buyLink(href, "Buy this list on TCGplayer", "buy-tcg"));
    if (deck.querySelector(".tcg-note")) return;
    var note = document.createElement("p");
    note.className = "muted tcg-note";
    note.textContent = "Opens the full 50-card list in TCGplayer Mass Entry. Affiliate link.";
    if (title.nextSibling) deck.insertBefore(note, title.nextSibling);
    else deck.appendChild(note);
  }

  function addCardButtons() {
    document.querySelectorAll(".picture-summary .card-entry").forEach(function (entry) {
      if (entry.querySelector(".buy-tcg-inline")) return;
      var cid = cidFrom(entry.querySelector(".id")) || cidFrom(entry);
      if (!cid) return;
      var wrap = entry.querySelector("div") || entry;
      var after = wrap.querySelector(".text") || wrap.querySelector("h4") || wrap;
      var link = buyLink(cardUrl(cid), "TCGplayer", "buy-tcg-inline");
      link.title = "This printing on TCGplayer";
      if (after && after.parentNode === wrap) after.insertAdjacentElement("afterend", link);
      else wrap.appendChild(link);
    });
  }

  function ready() {
    if (isHome() || !isIndividualDecklist()) return;
    addListButton();
    addCardButtons();
  }

  function boot() {
    fetch("/data/tcgplayer.json", { cache: "no-store" })
      .then(function (r) { return r.ok ? r.json() : {}; })
      .then(function (cfg) {
        if (cfg && cfg.partnerLink) CFG.partnerLink = String(cfg.partnerLink);
      })
      .catch(function () {})
      .then(ready);
  }

  window.OPDB_TCGPLAYER_UI = {
    isHome: isHome,
    isIndividualDecklist: isIndividualDecklist
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
