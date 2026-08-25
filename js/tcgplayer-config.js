/* TCGplayer affiliate config
 *
 * Preferred: paste the Impact API link into /data/tcgplayer.json
 *   { "partnerLink": "https://partner.tcgplayer.com/c/..../..../...." }
 * Find it in Impact: My Brands → TCGplayer → Assets → "api link".
 *
 * This file is a fallback if the JSON fetch fails. Leave partnerLink blank
 * until then. Buy buttons still open TCGplayer; they just will not credit
 * the affiliate program yet.
 */
window.OPDB_TCGPLAYER = {
  partnerLink: ""
};
