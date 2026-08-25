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

    def test_affiliate_passthrough_when_blank(self):
        dest = "https://www.tcgplayer.com/product/1"
        self.assertEqual(affiliate_url(dest, ""), dest)

    def test_affiliate_wraps_impact_link(self):
        dest = "https://www.tcgplayer.com/product/707123"
        wrapped = affiliate_url(dest, "https://partner.tcgplayer.com/c/1/2/3")
        self.assertTrue(wrapped.startswith("https://partner.tcgplayer.com/c/1/2/3?"))
        q = urllib.parse.parse_qs(urllib.parse.urlparse(wrapped).query)
        self.assertEqual(q["u"], [dest])

    def test_parse_sim_text(self):
        cards = parse_sim_text("1xOP08-058 4xOP11-070 4×ST34-003")
        self.assertEqual(cards, [(1, "OP08-058"), (4, "OP11-070"), (4, "ST34-003")])


if __name__ == "__main__":
    unittest.main()
