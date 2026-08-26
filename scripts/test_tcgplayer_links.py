#!/usr/bin/env python3
import sys
import unittest
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tcgplayer_links import affiliate_url, card_url, mass_entry_url, parse_sim_text


class TcgplayerLinksTest(unittest.TestCase):
    def test_card_product_url(self):
        self.assertEqual(card_url("OP17-079", 707123), "https://www.tcgplayer.com/product/707123")

    def test_card_search_fallback(self):
        url = card_url("OP17-079")
        self.assertIn("OP17-079", url)
        self.assertIn("one-piece-card-game", url)

    def test_mass_entry_uses_ids_and_qty(self):
        url = mass_entry_url([(4, "OP17-079"), (1, "OP08-058")])
        parsed = urllib.parse.urlparse(url)
        self.assertEqual(parsed.path, "/massentry")
        q = urllib.parse.parse_qs(parsed.query)
        self.assertEqual(q["productline"], ["One Piece Card Game"])
        self.assertEqual(q["c"], ["4 OP17-079||1 OP08-058"])

    def test_affiliate_wraps_when_partner_blank(self):
        dest = "https://www.tcgplayer.com/product/1"
        wrapped = affiliate_url(dest, "")
        self.assertTrue(wrapped.startswith("https://partner.tcgplayer.com/"))
        q = urllib.parse.parse_qs(urllib.parse.urlparse(wrapped).query)
        self.assertEqual(q["u"], [dest])

    def test_affiliate_wraps_impact_link(self):
        dest = "https://www.tcgplayer.com/product/707123"
        wrapped = affiliate_url(dest, "https://partner.tcgplayer.com/c/1/2/3")
        self.assertTrue(wrapped.startswith("https://partner.tcgplayer.com/c/1/2/3?"))
        q = urllib.parse.parse_qs(urllib.parse.urlparse(wrapped).query)
        self.assertEqual(q["u"], [dest])

    def test_live_partner_link_wraps_every_destination(self):
        from tcgplayer_links import load_config

        partner = load_config()["partnerLink"]
        self.assertEqual(partner, "https://partner.tcgplayer.com/c/7670706/1780961/21018")
        dest = "https://www.tcgplayer.com/massentry?productline=One%20Piece%20Card%20Game&c=1%20OP17-079"
        wrapped = affiliate_url(dest)
        self.assertTrue(wrapped.startswith(partner + "?"))
        q = urllib.parse.parse_qs(urllib.parse.urlparse(wrapped).query)
        self.assertEqual(q["u"], [dest])

    def test_parse_sim_text(self):
        cards = parse_sim_text("1xOP08-058 4xOP11-070 4×ST34-003")
        self.assertEqual(cards, [(1, "OP08-058"), (4, "OP11-070"), (4, "ST34-003")])


class TcgplayerPlacementTest(unittest.TestCase):
    def setUp(self):
        spec = __import__("importlib.util").util.spec_from_file_location(
            "upgrade", Path("/workspace/scripts/upgrade-public-pages.py")
        )
        self.up = __import__("importlib.util").util.module_from_spec(spec)
        spec.loader.exec_module(self.up)

    def test_skips_homepage_without_lists(self):
        html = '<main class="single home" role="main"><section id="recent"></section></main></body>'
        out = self.up.ensure_tcgplayer_scripts(html)
        self.assertNotIn("tcgplayer.js", out)

    def test_adds_to_leader_hub(self):
        html = '<li class="list-row"></li></body>'
        out = self.up.ensure_tcgplayer_scripts(html)
        self.assertIn("/js/tcgplayer.js?v=tcg-pills", out)

    def test_adds_to_individual_decklist(self):
        html = (
            '<section class="text-deck"></section>'
            '<section class="picture-summary"></section>'
            "</body>"
        )
        out = self.up.ensure_tcgplayer_scripts(html)
        self.assertIn("/js/tcgplayer.js?v=tcg-pills", out)
        self.assertEqual(out.count("tcgplayer.js"), 1)

    def test_refreshes_stale_script_version(self):
        html = (
            '<li class="list-row"></li>\n'
            '  <script src="/js/tcgplayer-config.js?v=tcg-buy"></script>\n'
            '  <script src="/js/tcgplayer-ids.js?v=tcg-buy"></script>\n'
            '  <script src="/js/tcgplayer.js?v=tcg-buy"></script>\n'
            "</body>"
        )
        out = self.up.ensure_tcgplayer_scripts(html)
        self.assertIn("v=tcg-pills", out)
        self.assertNotIn("v=tcg-buy", out)

    def test_js_restores_pills_and_always_affiliates(self):
        src = Path("/workspace/js/tcgplayer.js").read_text()
        self.assertIn("addHubButtons", src)
        self.assertIn("Buy list on TCGplayer", src)
        self.assertIn("Buy on TCGplayer", src)
        self.assertIn("FALLBACK_PARTNER", src)
        self.assertIn("partner.tcgplayer.com/c/7670706/1780961/21018", src)

    def test_hover_preview_uses_larger_fallback(self):
        chrome = Path("/workspace/scripts/generate-tournament-lists.py").read_text()
        self.assertIn("offsetWidth || 220", chrome)
        self.assertIn("offsetHeight || 308", chrome)


if __name__ == "__main__":
    unittest.main()
