(function () {
  var FALLBACK_PARTNER = "https://partner.tcgplayer.com/c/7670706/1780961/21018";
  var CFG = window.OPDB_TCGPLAYER || {};
  var IDS = window.OPDB_TCGPLAYER_IDS || {};
  // Mass Entry line format from TCGPlayer's own parser:
  //   qty name [SetCode] CardNumber   or   qty-productId
  // https://help.tcgplayer.com/hc/en-us/articles/360055768913
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

  function prefixOf(cid) {
    return cid.indexOf("-") >= 0 ? cid.split("-")[0] : cid;
  }

  function collectorOf(cid) {
    return cid.indexOf("-") >= 0 ? cid.split("-").slice(1).join("-") : cid;
  }

  // TCGPlayer set abbreviations, from /v2/massentry/sets/68.
  // OP boosters stay OP17; starters/extras hyphenate (ST-32, EB-01).
  function tcgSetCode(cid) {
    var set = prefixOf(cid);
    if (set === "P") return "OP-PR";
    if (set === "OP15" || set === "EB04") return "OP15-EB04";
    if (set === "EB03") return "EB-03-04";
    if (/^OP\d+$/.test(set)) return set;
    var m = /^([A-Z]+)(\d+)$/.exec(set);
    return m ? m[1] + "-" + m[2] : set;
  }

  function isLeader(cid, flagged) {
    if (flagged) return true;
    var meta = CARD_CACHE && CARD_CACHE[cid] ? CARD_CACHE[cid] : null;
    return !!(meta && String(meta.category || "").toLowerCase() === "leader");
  }

  function catalogName(cid, given, flagged) {
    var meta = CARD_CACHE && CARD_CACHE[cid] ? CARD_CACHE[cid] : null;
    var name = meta && meta.name
      ? String(meta.name).trim()
      : String(given || "").replace(/\s+/g, " ").trim();
    if (!name) return "";
    // Leaders use the same qty name [SET] ID line as other cards.
    // A collector suffix on the leader (Nico Robin (062)) made Mass Entry
    // reject the whole paste. Only reused dotted character names get it.
    if (isLeader(cid, flagged)) return name;
    if (name.indexOf(".") >= 0 && name.indexOf("(") < 0) {
      name += " (" + collectorOf(cid) + ")";
    }
    return name;
  }

  function cardUrl(cid) {
    cid = (cid || "").toUpperCase();
    var pid = IDS[cid];
    if (pid) return "https://www.tcgplayer.com/product/" + pid;
    return "https://www.tcgplayer.com/search/" + SEARCH_LINE + "/product?q=" +
      encodeURIComponent(cid) + "&productLineName=" + encodeURIComponent(SEARCH_LINE);
  }

  function massLine(qty, cid, given, flagged) {
    var name = catalogName(cid, given, flagged);
    var setCode = tcgSetCode(cid);
    if (name && setCode) return qty + " " + name + " [" + setCode + "] " + cid;
    if (name) return qty + " " + name;
    return qty + " " + cid;
  }

  function uniqueCards(cards) {
    var out = [];
    var seen = {};
    (cards || []).forEach(function (row) {
      var qty = row[0];
      var cid = (row[1] || "").toUpperCase();
      if (!qty || !cid || seen[cid]) return;
      seen[cid] = 1;
      out.push([qty, cid, row[2], row[3]]);
    });
    return out;
  }

  // Newline list for the Mass Entry textarea. Their URL `c=` + affiliate
  // wrap has not been filling the box, so we copy this and open a short page.
  function massText(cards) {
    return uniqueCards(cards).map(function (row) {
      return massLine(row[0], row[1], row[2], row[3]);
    }).join("\n");
  }

  function simText(cards) {
    return uniqueCards(cards).map(function (row) {
      return row[0] + "x" + row[1];
    }).join(" ");
  }

  function massBoxUrl() {
    return affiliate(
      "https://www.tcgplayer.com/massentry?productline=" +
      encodeURIComponent(PRODUCT_LINE)
    );
  }

  function helperUrl(cards) {
    var sim = simText(cards);
    return sim ? "/shop/buy-list.html#" + encodeURIComponent(sim) : "/shop/buy-list.html";
  }

  function copyText(text) {
    if (!text) return false;
    try {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.cssText = "position:fixed;left:-9999px;top:0";
      document.body.appendChild(ta);
      ta.select();
      ta.setSelectionRange(0, text.length);
      var ok = document.execCommand("copy");
      document.body.removeChild(ta);
      if (ok) return true;
    } catch (e) {}
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).catch(function () {});
    }
    return false;
  }

  function openMassEntry(cards, ev) {
    var text = massText(cards);
    // Copy on this page first (user gesture), then open the short Mass Entry
    // URL. Prefilling `c=` through the affiliate redirect has been dropping
    // the list, so the user pastes (Ctrl+V) into the box.
    copyText(text);
    var win = window.open(massBoxUrl(), "_blank", "noopener");
    if (win && ev) {
      ev.preventDefault();
      ev.stopPropagation();
    }
    return text;
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
      cards.push([qty, cid, name, !!(line.closest && line.closest(".text-deck-leader"))]);
    });
    return cards;
  }

  function buyLink(href, label, className) {
    var a = document.createElement("a");
    a.className = className;
    a.href = href;
    a.target = "_blank";
    a.rel = REL;
    a.textContent = label;
    a.addEventListener("click", function (e) { e.stopPropagation(); });
    return a;
  }

  function listBuyLink(cards, label, className) {
    var a = buyLink(helperUrl(cards), label, className);
    a.addEventListener("click", function (e) { openMassEntry(cards, e); });
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
      var cards = cardsFromTextDeck(root);
      if (!cards.length) return;
      title.appendChild(listBuyLink(cards, "Buy list on TCGplayer", "buy-tcg"));
    });
    document.querySelectorAll(".text-deck > p.muted").forEach(function (p) {
      if (p.dataset.tcgNote) return;
      p.dataset.tcgNote = "1";
      p.appendChild(document.createTextNode(" Buy list copies a Mass Entry list and opens TCGplayer. Paste it into the box (Ctrl+V). Individual Buy links open that printing when TCGplayer has it. TCGplayer links are affiliate links."));
    });
  }

  function addHubButtons() {
    document.querySelectorAll(".list-row").forEach(function (row) {
      if (row.querySelector(".buy-tcg")) return;
      var btn = row.querySelector("[data-copy-sim]");
      var sim = btn ? btn.getAttribute("data-sim") : "";
      var cards = parseSim(sim || "");
      if (!cards.length) return;
      row.appendChild(listBuyLink(cards, "Buy on TCGplayer", "buy-tcg"));
    });
  }

  function addCardButtons() {
    document.querySelectorAll(".text-line").forEach(function (line) {
      if (line.querySelector(".buy-tcg-inline")) return;
      var cid = cidFrom(line.querySelector(".card-id")) || cidFrom(line);
      if (!cid) return;
      line.appendChild(buyLink(affiliate(cardUrl(cid)), "Buy", "buy-tcg-inline"));
    });
    document.querySelectorAll(".card-entry").forEach(function (entry) {
      if (entry.querySelector(".buy-tcg-inline")) return;
      var cid = cidFrom(entry.querySelector(".id")) || cidFrom(entry);
      if (!cid) return;
      var wrap = entry.querySelector("div") || entry;
      wrap.appendChild(buyLink(affiliate(cardUrl(cid)), "Buy on TCGplayer", "buy-tcg-inline"));
    });
  }

  window.OPDB_TCG = {
    parseSim: parseSim,
    massText: massText,
    massBoxUrl: massBoxUrl,
    openMassEntry: openMassEntry,
    catalogName: catalogName,
    tcgSetCode: tcgSetCode
  };

  function ready() {
    addListButtons();
    addHubButtons();
    addCardButtons();
    if (typeof window.OPDB_onTcgReady === "function") window.OPDB_onTcgReady();
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
