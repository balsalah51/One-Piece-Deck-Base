#!/usr/bin/env python3
"""Write unpublished shop pages (kept on disk, not linked from the public site)."""

from pathlib import Path

ROOT = Path("/workspace")
DISCORD = "https://discord.gg/adZ2WUQ3D"


def chrome(title: str, desc: str, current: str, body: str) -> str:
    def nav(href: str, label: str, key: str) -> str:
        cur = ' aria-current="page"' if key == current else ""
        return f'        <a href="{href}"{cur}>{label}</a>'

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <meta name="robots" content="noindex, nofollow" />
  <link rel="stylesheet" href="/css/site.css" />
</head>
<body>
  <div class="wrap">
    <header>
      <a class="brand" href="/">
        <div class="logo">OP</div>
        <div>
          <h1>One Piece Deck Base</h1>
          <div class="subtitle">Decklists, community, and custom gear</div>
        </div>
      </a>
      <nav aria-label="Primary">
{nav("/#decklists", "Decklists", "decklists")}
{nav("/decklists/op17.html", "OP17", "op17")}
{nav("/shop/", "Shop", "shop")}
{nav("/#community", "Community", "community")}
      </nav>
    </header>
    <main class="single">
      <div class="card hero">
{body}
      </div>
    </main>
    <footer>
      © <span id="year"></span> One Piece Deck Base — Fan merch, not affiliated with Bandai or Shueisha.
      <a href="/shop/">Shop</a> · <a href="{DISCORD}" target="_blank" rel="noopener">Discord</a>
    </footer>
  </div>
  <script>document.getElementById('year').textContent = new Date().getFullYear();</script>
</body>
</html>
"""


def write(rel: str, title: str, desc: str, current: str, body: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(chrome(title, desc, current, body))
    print("wrote", rel)


index_body = f"""        <div class="crumb"><a href="/">Home</a> / Shop</div>
        <h2>Shop</h2>
        <p>Playmats, dice, sleeves, and custom leaders. Order on Discord. Fan merch — not official Bandai product.</p>
        <div class="shop-grid">
          <a class="shop-card" href="/shop/playmats.html">
            <div class="shop-mock">Playmat</div>
            <div style="font-weight:800">Playmats</div>
            <div class="muted">24&quot; × 14&quot; cloth mats. Crew, emperor, and custom-leader art.</div>
            <div class="price">from $35</div>
          </a>
          <a class="shop-card" href="/shop/dice.html">
            <div class="shop-mock dice">D6</div>
            <div style="font-weight:800">DON!! / life dice</div>
            <div class="muted">Life counters and DON!! trackers in red, black, or gold.</div>
            <div class="price">from $12</div>
          </a>
          <a class="shop-card" href="/shop/sleeves.html">
            <div class="shop-mock sleeves">63×88</div>
            <div style="font-weight:800">Sleeves</div>
            <div class="muted">Standard OPTCG size. Solid colors plus art backs.</div>
            <div class="price">from $8</div>
          </a>
          <a class="shop-card" href="/shop/custom-leaders.html">
            <div class="shop-mock leader">Leader</div>
            <div style="font-weight:800">Custom leaders</div>
            <div class="muted">Design a fan leader, preview it, then order a print or playmat.</div>
            <div class="price">from $18</div>
          </a>
        </div>
        <p class="muted" style="margin-top:18px">To order: open Discord, paste the product name, color, quantity, and shipping city. <a href="{DISCORD}">discord.gg/adZ2WUQ3D</a></p>"""

playmats_body = f"""        <div class="crumb"><a href="/">Home</a> / <a href="/shop/">Shop</a> / Playmats</div>
        <h2>Playmats</h2>
        <p>Stitched-edge cloth mats sized for a One Piece TCG board. Art is fan-made. Say which leader or crew you want on Discord.</p>
        <div class="shop-grid">
          <div class="shop-card">
            <div class="shop-mock">Straw Hat</div>
            <div style="font-weight:800">Straw Hat crew mat</div>
            <div class="muted">Black / red. Life track on the left, DON!! row on the right.</div>
            <div class="price">$35</div>
          </div>
          <div class="shop-card">
            <div class="shop-mock" style="background:linear-gradient(135deg,#1565c0,#90caf9);color:#fff">Rocks</div>
            <div style="font-weight:800">Rocks Pirates mat</div>
            <div class="muted">Blue God Valley layout. Room for a 50-card deck and trash.</div>
            <div class="price">$38</div>
          </div>
          <div class="shop-card">
            <div class="shop-mock" style="background:linear-gradient(135deg,#6a1b9a,#ce93d8);color:#fff">Beasts</div>
            <div style="font-weight:800">Animal Kingdom mat</div>
            <div class="muted">Purple Kaido field. Optional custom-leader portrait upgrade.</div>
            <div class="price">$38</div>
          </div>
          <div class="shop-card">
            <div class="shop-mock leader">Yours</div>
            <div style="font-weight:800">Custom leader mat</div>
            <div class="muted">Print the leader you design on the custom-leader page as the mat art.</div>
            <div class="price">$45</div>
          </div>
        </div>
        <a class="discord" href="{DISCORD}" style="margin-top:18px">Order playmats on Discord</a>"""

dice_body = f"""        <div class="crumb"><a href="/">Home</a> / <a href="/shop/">Shop</a> / Dice</div>
        <h2>DON!! and life dice</h2>
        <p>Opaque D6 sets for life and DON!!. Not official Bandai DON!! cards — use them as counters at kitchen-table games, or check your locals if custom dice are allowed.</p>
        <div class="shop-grid">
          <div class="shop-card">
            <div class="shop-mock dice">Life</div>
            <div style="font-weight:800">Life counter pair</div>
            <div class="muted">Two D6, pips 1–5 plus a blank. Red or black.</div>
            <div class="price">$12</div>
          </div>
          <div class="shop-card">
            <div class="shop-mock dice">DON</div>
            <div style="font-weight:800">DON!! tracker set</div>
            <div class="muted">Ten small cubes to mark attached DON!! without extra cards.</div>
            <div class="price">$14</div>
          </div>
          <div class="shop-card">
            <div class="shop-mock" style="background:#c9a227;color:#222">Gold</div>
            <div style="font-weight:800">Emperor gold set</div>
            <div class="muted">Life pair plus DON!! cubes in gold resin.</div>
            <div class="price">$22</div>
          </div>
        </div>
        <a class="discord" href="{DISCORD}" style="margin-top:18px">Order dice on Discord</a>"""

sleeves_body = f"""        <div class="crumb"><a href="/">Home</a> / <a href="/shop/">Shop</a> / Sleeves</div>
        <h2>Sleeves</h2>
        <p>Standard 63×88 mm. Solid colors ship first. Art backs are printed in small batches — ask on Discord before you assume a character is in stock.</p>
        <div class="shop-grid">
          <div class="shop-card">
            <div class="shop-mock sleeves">Red</div>
            <div style="font-weight:800">Solid pack (60)</div>
            <div class="muted">Red, green, blue, purple, black, or yellow. Enough for a 50-card deck plus leader.</div>
            <div class="price">$8</div>
          </div>
          <div class="shop-card">
            <div class="shop-mock" style="background:#222;color:#fff">Matte</div>
            <div style="font-weight:800">Matte inner + outer</div>
            <div class="muted">Double sleeve kit. Inners clear, outers your color.</div>
            <div class="price">$14</div>
          </div>
          <div class="shop-card">
            <div class="shop-mock leader">Art</div>
            <div style="font-weight:800">Art back (60)</div>
            <div class="muted">Fan art of a leader you pick, or the custom leader you design.</div>
            <div class="price">$16</div>
          </div>
        </div>
        <a class="discord" href="{DISCORD}" style="margin-top:18px">Order sleeves on Discord</a>"""

custom_body = f"""        <div class="crumb"><a href="/">Home</a> / <a href="/shop/">Shop</a> / Custom leaders</div>
        <h2>Custom leaders</h2>
        <p>Fan-made leader cards for kitchen-table games, display, playmats, and sleeve backs. They are <strong>not</strong> official Bandai cards and are <strong>not</strong> legal in official constructed events. Design one here, then send the spec on Discord to order a print ($18), art sleeves ($16), or a playmat with this portrait ($45).</p>
        <div class="custom-wrap">
          <div>
            <article class="custom-card" id="preview" style="background:linear-gradient(180deg,#b71c1c,#7a1212)">
              <div class="life"><span id="p-life">5</span> Life · <span id="p-attr">Strike</span></div>
              <div class="cname" id="p-name">Custom Leader</div>
              <div class="types" id="p-types">Straw Hat Crew</div>
              <div class="effect" id="p-effect">[Activate: Main] [Once Per Turn] Design your own effect. Keep it readable — this is the text that prints.</div>
              <div class="power"><span id="p-power">5000</span></div>
            </article>
          </div>
          <form class="custom-form" id="designer">
            <label for="name">Leader name</label>
            <input id="name" name="name" maxlength="42" value="Custom Leader" />
            <label for="color">Color</label>
            <select id="color" name="color">
              <option value="#b71c1c">Red</option>
              <option value="#2e7d32">Green</option>
              <option value="#1565c0">Blue</option>
              <option value="#6a1b9a">Purple</option>
              <option value="#212121">Black</option>
              <option value="#c9a227">Yellow</option>
            </select>
            <label for="life">Life</label>
            <select id="life" name="life">
              <option>4</option>
              <option selected>5</option>
            </select>
            <label for="power">Power</label>
            <input id="power" name="power" value="5000" />
            <label for="attr">Attribute</label>
            <select id="attr" name="attr">
              <option>Strike</option>
              <option>Slash</option>
              <option>Ranged</option>
              <option>Special</option>
              <option>Wisdom</option>
            </select>
            <label for="types">Types</label>
            <input id="types" name="types" value="Straw Hat Crew" />
            <label for="effect">Effect text</label>
            <textarea id="effect" name="effect">[Activate: Main] [Once Per Turn] Design your own effect. Keep it readable — this is the text that prints.</textarea>
            <label for="product">What to print</label>
            <select id="product" name="product">
              <option value="leader-print">Leader print — $18</option>
              <option value="sleeves">Art sleeves (60) — $16</option>
              <option value="playmat">Playmat with this leader — $45</option>
              <option value="bundle">Print + sleeves + mat — $70</option>
            </select>
            <button class="discord" type="button" id="copy" style="margin-top:14px;border:0;width:100%;cursor:pointer">Copy order text for Discord</button>
            <p class="muted" id="copied" style="display:none;margin-top:8px">Copied. Paste it in Discord to place the order.</p>
            <pre class="order-box" id="order"></pre>
          </form>
        </div>
        <p class="muted" style="margin-top:18px">Not affiliated with Bandai or Shueisha. Custom leaders are original fan designs for personal use and display.</p>
        <script>
          const colors = {{
            '#b71c1c': 'linear-gradient(180deg,#b71c1c,#7a1212)',
            '#2e7d32': 'linear-gradient(180deg,#2e7d32,#1b5e20)',
            '#1565c0': 'linear-gradient(180deg,#1565c0,#0d47a1)',
            '#6a1b9a': 'linear-gradient(180deg,#6a1b9a,#4a148c)',
            '#212121': 'linear-gradient(180deg,#424242,#212121)',
            '#c9a227': 'linear-gradient(180deg,#c9a227,#8d6e12)'
          }};
          function val(id) {{ return document.getElementById(id).value.trim(); }}
          function sync() {{
            document.getElementById('p-name').textContent = val('name') || 'Custom Leader';
            document.getElementById('p-life').textContent = val('life');
            document.getElementById('p-attr').textContent = val('attr');
            document.getElementById('p-types').textContent = val('types') || '—';
            document.getElementById('p-effect').textContent = val('effect') || ' ';
            document.getElementById('p-power').textContent = val('power') || '5000';
            document.getElementById('preview').style.background = colors[val('color')] || colors['#b71c1c'];
            const lines = [
              'CUSTOM LEADER ORDER — One Piece Deck Base',
              'Name: ' + (val('name') || 'Custom Leader'),
              'Color: ' + document.getElementById('color').selectedOptions[0].text,
              'Life: ' + val('life'),
              'Power: ' + (val('power') || '5000'),
              'Attribute: ' + val('attr'),
              'Types: ' + (val('types') || '—'),
              'Effect: ' + (val('effect') || '—'),
              'Product: ' + document.getElementById('product').selectedOptions[0].text,
              'Ship to: (add city / country)'
            ];
            document.getElementById('order').textContent = lines.join('\\n');
          }}
          document.getElementById('designer').addEventListener('input', sync);
          document.getElementById('copy').addEventListener('click', function() {{
            sync();
            navigator.clipboard.writeText(document.getElementById('order').textContent).then(function() {{
              document.getElementById('copied').style.display = 'block';
            }});
          }});
          sync();
        </script>"""

write("shop/index.html", "Shop | One Piece Deck Base", "Playmats, dice, sleeves, and custom OPTCG leaders.", "shop", index_body)
write("shop/playmats.html", "Playmats | One Piece Deck Base shop", "Fan-made One Piece TCG playmats.", "shop", playmats_body)
write("shop/dice.html", "Dice | One Piece Deck Base shop", "DON!! and life dice for One Piece TCG.", "shop", dice_body)
write("shop/sleeves.html", "Sleeves | One Piece Deck Base shop", "OPTCG-size sleeves and art backs.", "shop", sleeves_body)
write("shop/custom-leaders.html", "Custom leaders | One Piece Deck Base shop", "Design a fan-made One Piece TCG leader and order a print, sleeves, or playmat.", "shop", custom_body)
print("shop pages ready")
