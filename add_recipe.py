#!/usr/bin/env python3
"""
add_recipe.py — Add a new recipe to Bean Cooking.

Usage:
    python add_recipe.py recipe_data.json          # add new recipe
    python add_recipe.py recipe_data.json --force  # regenerate existing page (index unchanged)

The JSON file should have this structure (see recipe_template.json for a full example):
{
  "title": "Recipe Title",
  "slug": "recipe-title",           // used as filename: recipes/<slug>.html
  "image_url": "https://...",
  "image_alt": "Description of image",
  "source_url": "https://...",
  "source_label": "Site Name",
  "prep_min": 15,
  "cook_min": 30,
  "servings": 4,
  "tags": "Vegan · GF",             // dietary/label string shown in meta row
  "card_tag": "Modified",           // optional badge on index card (e.g. "Modified", "Original")
  "modifications": [                // optional; omit section if empty list
    "Used garlic powder instead of fresh garlic"
  ],
  "ingredient_groups": [
    {
      "label": "Vegetables",        // optional group label; omit for flat list
      "items": [
        {"amount": "1 cup", "name": "onion, chopped", "modified": false},
        {"amount": "similar qty", "name": "broccoli florets ✱ added", "modified": true}
      ]
    }
  ],
  "steps": [
    "Preheat oven to 400°F ...",
    "Mix spices ..."
  ],
  "nutrition": {                    // optional; omit entire key to hide section
    "Calories": "284",
    "Carbs": "44g",
    "Protein": "12g",
    "Fat": "7g",
    "Fiber": "11g"
  }
}
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).parent
INDEX = REPO / "index.html"
RECIPES_DIR = REPO / "recipes"


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text


def render_recipe_page(d: dict) -> str:
    title = d["title"]
    slug = d.get("slug") or slugify(title)
    image_url = d["image_url"]
    image_alt = d.get("image_alt", title)
    source_url = d.get("source_url", "")
    source_label = d.get("source_label", "Original recipe")
    prep = d.get("prep_min", 0)
    cook = d.get("cook_min", 0)
    servings = d.get("servings", "")
    tags = d.get("tags", "")
    modifications = d.get("modifications", [])

    # Build meta row
    meta_parts = []
    if prep:
        meta_parts.append(f"Prep: {prep} min")
    if cook:
        meta_parts.append(f"Cook: {cook} min")
    if servings:
        meta_parts.append(f"Serves: {servings}")
    if tags:
        meta_parts.append(tags)
    meta_row = "".join(f"      <span>{p}</span>\n" for p in meta_parts)

    # Source link
    source_html = ""
    if source_url:
        source_html = f'\n    <a class="source-link" href="{source_url}" target="_blank" rel="noopener">{source_label} ↗</a>\n'

    # Modifications box
    mods_html = ""
    if modifications:
        items = "".join(f"        <li>{m}</li>\n" for m in modifications)
        mods_html = f"""
    <h2>My Changes</h2>
    <div class="mods-box">
      <h3>Aaron's Modifications</h3>
      <ul>
{items}      </ul>
    </div>
"""

    # Ingredients
    ingredients_html = ""
    for group in d.get("ingredient_groups", []):
        label = group.get("label")
        if label:
            ingredients_html += f'      <li class="ingredient-group-label"><span>{label}</span></li>\n'
        for item in group.get("items", []):
            amount = item.get("amount", "")
            name = item.get("name", "")
            mod = item.get("modified", False)
            cls = ' class="modified"' if mod else ""
            ingredients_html += f'      <li{cls}><span class="amount" data-amount="{amount}">{amount}</span><span>{name}</span></li>\n'

    # Steps
    steps_html = "".join(
        f"      <li>{step}</li>\n" for step in d.get("steps", [])
    )

    # Nutrition
    nutrition_html = ""
    nutrition = d.get("nutrition")
    if nutrition:
        items = "".join(
            f'      <div class="nutrition-item"><span class="value">{v}</span><span class="label">{k}</span></div>\n'
            for k, v in nutrition.items()
        )
        nutrition_html = f"""
    <h2>Nutrition <span style="font-family:'DM Sans';font-size:0.75rem;color:var(--muted);font-weight:300;">(per serving, original recipe)</span></h2>
    <div class="nutrition-grid">
{items}    </div>
"""

    footer_source = ""
    if source_url:
        footer_source = f' · <a class="source-link" href="{source_url}" target="_blank">Source</a>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} — Bean Cooking</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --bg: #faf9f7;
      --ink: #1c1a18;
      --muted: #6b6560;
      --accent: #c07a3a;
      --border: #e8e4de;
      --card-bg: #ffffff;
    }}

    body {{
      font-family: 'DM Sans', sans-serif;
      background: var(--bg);
      color: var(--ink);
      min-height: 100vh;
    }}

    nav {{
      max-width: 900px;
      margin: 0 auto;
      padding: 1.5rem 2rem;
    }}

    nav a {{
      color: var(--muted);
      text-decoration: none;
      font-size: 0.85rem;
      letter-spacing: 0.02em;
    }}

    nav a:hover {{ color: var(--ink); }}

    .hero {{
      width: 100%;
      max-height: 480px;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .hero img {{
      width: 100%;
      max-height: 480px;
      object-fit: cover;
      display: block;
    }}

    .content {{
      max-width: 720px;
      margin: 0 auto;
      padding: 2.5rem 2rem 4rem;
    }}

    .controls {{
      display: flex;
      align-items: center;
      gap: 0.35rem;
      margin-bottom: 2rem;
      padding-bottom: 1.25rem;
      border-bottom: 1px solid var(--border);
      flex-wrap: wrap;
    }}

    .ctrl-label {{
      font-size: 0.7rem;
      font-weight: 500;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--muted);
      margin-right: 0.1rem;
    }}

    .ctrl-sep {{
      color: var(--border);
      margin: 0 0.5rem;
      user-select: none;
    }}

    .ctrl-btn {{
      font-family: 'DM Sans', sans-serif;
      font-size: 0.75rem;
      font-weight: 500;
      background: none;
      border: 1px solid var(--border);
      border-radius: 2px;
      padding: 0.2em 0.6em;
      color: var(--muted);
      cursor: pointer;
      transition: border-color 0.15s, color 0.15s;
      line-height: 1.4;
    }}

    .ctrl-btn:hover {{
      border-color: var(--accent);
      color: var(--accent);
    }}

    .ctrl-btn.active {{
      border-color: var(--accent);
      color: var(--accent);
    }}

    h1 {{
      font-family: 'Playfair Display', serif;
      font-size: clamp(1.6rem, 4vw, 2.4rem);
      font-weight: 400;
      line-height: 1.25;
      margin-bottom: 0.75rem;
    }}

    .meta-row {{
      display: flex;
      gap: 1.5rem;
      color: var(--muted);
      font-size: 0.85rem;
      margin-bottom: 1.5rem;
      flex-wrap: wrap;
    }}

    .source-link {{
      color: var(--accent);
      text-decoration: none;
      font-size: 0.8rem;
    }}

    .source-link:hover {{ text-decoration: underline; }}

    .mods-box {{
      background: #fffbf5;
      border-left: 3px solid var(--accent);
      padding: 1rem 1.2rem;
      margin-bottom: 2rem;
      border-radius: 0 4px 4px 0;
    }}

    .mods-box h3 {{
      font-size: 0.75rem;
      font-weight: 500;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 0.5rem;
    }}

    .mods-box ul {{
      list-style: none;
      padding: 0;
    }}

    .mods-box ul li {{
      font-size: 0.9rem;
      color: var(--ink);
      padding: 0.2rem 0;
      padding-left: 1rem;
      position: relative;
    }}

    .mods-box ul li::before {{
      content: '–';
      position: absolute;
      left: 0;
      color: var(--accent);
    }}

    h2 {{
      font-family: 'Playfair Display', serif;
      font-size: 1.2rem;
      font-weight: 400;
      margin: 2rem 0 1rem;
    }}

    .ingredients {{
      list-style: none;
      padding: 0;
    }}

    .ingredients li {{
      padding: 0.55rem 0;
      border-bottom: 1px solid var(--border);
      font-size: 0.92rem;
      display: flex;
      gap: 0.5rem;
    }}

    .ingredients li:last-child {{ border-bottom: none; }}

    .ingredients .amount {{
      min-width: 120px;
      color: var(--muted);
      font-weight: 300;
    }}

    .ingredients li.modified {{
      color: var(--accent);
    }}

    .ingredients li.modified .amount {{
      color: var(--accent);
      opacity: 0.8;
    }}

    .steps {{
      list-style: none;
      counter-reset: steps;
      padding: 0;
    }}

    .steps li {{
      counter-increment: steps;
      padding: 1rem 0 1rem 2.5rem;
      border-bottom: 1px solid var(--border);
      position: relative;
      font-size: 0.92rem;
      line-height: 1.65;
    }}

    .steps li:last-child {{ border-bottom: none; }}

    .steps li::before {{
      content: counter(steps);
      position: absolute;
      left: 0;
      top: 1rem;
      font-family: 'Playfair Display', serif;
      font-size: 1.1rem;
      color: var(--accent);
      font-weight: 400;
    }}

    .nutrition-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
      gap: 1rem;
      margin-top: 0.5rem;
    }}

    .nutrition-item {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 4px;
      padding: 0.75rem;
      text-align: center;
    }}

    .nutrition-item .value {{
      font-family: 'Playfair Display', serif;
      font-size: 1.3rem;
      display: block;
    }}

    .nutrition-item .label {{
      font-size: 0.72rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    footer {{
      text-align: center;
      padding: 2rem;
      color: var(--muted);
      font-size: 0.8rem;
      border-top: 1px solid var(--border);
    }}

    .ingredient-group-label {{
      font-size: 0.72rem;
      font-weight: 500;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
      padding: 0.75rem 0 0.3rem;
      border-bottom: none !important;
    }}
  </style>
</head>
<body>

  <nav>
    <a href="../index.html">← Bean Cooking</a>
  </nav>

  <div class="hero">
    <img src="{image_url}" alt="{image_alt}" />
  </div>

  <div class="content">

    <div class="controls">
      <span class="ctrl-label">Text</span>
      <button class="ctrl-btn" id="font-down">A−</button>
      <button class="ctrl-btn" id="font-up">A+</button>
      <span class="ctrl-sep">·</span>
      <span class="ctrl-label">Serves</span>
      <button class="ctrl-btn scale-btn" data-scale="0.5">½×</button>
      <button class="ctrl-btn scale-btn active" data-scale="1">1×</button>
      <button class="ctrl-btn scale-btn" data-scale="2">2×</button>
    </div>

    <h1>{title}</h1>

    <div class="meta-row">
{meta_row}    </div>
{source_html}{mods_html}
    <h2>Ingredients</h2>
    <ul class="ingredients">
{ingredients_html}    </ul>

    <h2>Instructions</h2>
    <ol class="steps">
{steps_html}    </ol>
{nutrition_html}
  </div>

  <footer>Bean Cooking{footer_source}</footer>

  <script>
    (function () {{
      // Font size
      var content = document.querySelector('.content');
      var fs = parseFloat(localStorage.getItem('recipeFont') || '1');
      content.style.fontSize = fs + 'em';

      document.getElementById('font-down').addEventListener('click', function () {{
        fs = Math.max(0.5, parseFloat((fs - 5.0).toFixed(1)));
        content.style.fontSize = fs + 'em';
        localStorage.setItem('recipeFont', fs);
      }});

      document.getElementById('font-up').addEventListener('click', function () {{
        fs = Math.min(20.0, parseFloat((fs + 5.0).toFixed(1)));
        content.style.fontSize = fs + 'em';
        localStorage.setItem('recipeFont', fs);
      }});

      // Portion scaling
      var FRACS = {{'½':0.5,'¼':0.25,'¾':0.75,'⅓':1/3,'⅔':2/3,'⅛':0.125,'⅜':0.375,'⅝':0.625,'⅞':0.875}};

      function parse(s) {{
        s = s.trim();
        var m = s.match(/^(\d+)\s*([½¼¾⅓⅔⅛⅜⅝⅞])/);
        if (m) return parseInt(m[1]) + FRACS[m[2]];
        if (FRACS[s]) return FRACS[s];
        m = s.match(/^(\d+\.?\d*)/);
        if (m) return parseFloat(m[1]);
        return null;
      }}

      function fmt(n) {{
        if (n <= 0) return '0';
        var nice = [[1/8,'⅛'],[1/4,'¼'],[1/3,'⅓'],[3/8,'⅜'],[1/2,'½'],[5/8,'⅝'],[2/3,'⅔'],[3/4,'¾'],[7/8,'⅞']];
        var whole = Math.floor(n), frac = n - whole;
        if (frac < 0.04) return String(whole);
        for (var i = 0; i < nice.length; i++) {{
          if (Math.abs(frac - nice[i][0]) < 0.05) return (whole > 0 ? whole : '') + nice[i][1];
        }}
        return n.toFixed(1);
      }}

      function scaleAmt(orig, factor) {{
        if (!orig.trim()) return orig;
        // Handle ranges like "½–1" or "1-2"
        var rm = orig.match(/^(.+?)\s*[–\-]\s*(\S+)(.*)/);
        if (rm) {{
          var a = parse(rm[1]), b = parse(rm[2]);
          if (a !== null && b !== null) return fmt(a * factor) + '–' + fmt(b * factor) + rm[3];
        }}
        var m = orig.match(/^(\d+\s*[½¼¾⅓⅔⅛⅜⅝⅞]|[½¼¾⅓⅔⅛⅜⅝⅞]|\d+\.?\d*)/);
        if (!m) return orig;
        var num = parse(m[1]);
        if (num === null) return orig;
        return fmt(num * factor) + orig.slice(m[1].length);
      }}

      document.querySelectorAll('.scale-btn').forEach(function (btn) {{
        btn.addEventListener('click', function () {{
          document.querySelectorAll('.scale-btn').forEach(function (b) {{ b.classList.remove('active'); }});
          btn.classList.add('active');
          var factor = parseFloat(btn.dataset.scale);
          document.querySelectorAll('.amount[data-amount]').forEach(function (el) {{
            el.textContent = scaleAmt(el.dataset.amount, factor);
          }});
        }});
      }});
    }})();
  </script>

</body>
</html>"""


def add_card_to_index(d: dict) -> None:
    title = d["title"]
    slug = d.get("slug") or slugify(title)
    image_url = d["image_url"]
    image_alt = d.get("image_alt", title)
    card_tag = d.get("card_tag", "")
    prep = d.get("prep_min", 0)
    cook = d.get("cook_min", 0)
    servings = d.get("servings", "")

    total_min = (prep or 0) + (cook or 0)
    time_str = f"{total_min} min" if total_min else ""
    servings_str = str(servings)
    if servings_str and not any(w in servings_str.lower() for w in ["serving", "cookie", "piece", "portion"]):
        servings_str = f"{servings_str} servings"
    meta_parts = [p for p in [time_str, servings_str] if p]
    meta_str = " · ".join(meta_parts)

    tag_html = f'\n          <span class="tag">{card_tag}</span>' if card_tag else ""

    # Local images live in recipes/images/. Recipe pages (in recipes/) use
    # "images/filename.jpg"; index.html (at root) needs "recipes/images/filename.jpg"
    card_image_url = image_url.replace("images/", "recipes/images/") if not image_url.startswith("http") else image_url

    card = f"""
      <a class="recipe-card" href="recipes/{slug}.html">
        <img src="{card_image_url}" alt="{image_alt}" />
        <div class="recipe-card-body">
          <h2>{title}</h2>
          <p class="meta">{meta_str}</p>{tag_html}
        </div>
      </a>"""

    content = INDEX.read_text()
    marker = "</div>\n  </main>"
    if marker not in content:
        raise ValueError("Could not find insertion point in index.html")
    updated = content.replace(marker, card + "\n    " + marker)
    INDEX.write_text(updated)


def main():
    force = "--force" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if len(args) != 1:
        print("Usage: python add_recipe.py <recipe_data.json> [--force]")
        sys.exit(1)

    data_file = Path(args[0])
    if not data_file.exists():
        print(f"File not found: {data_file}")
        sys.exit(1)

    d = json.loads(data_file.read_text())
    slug = d.get("slug") or slugify(d["title"])
    d["slug"] = slug

    out_path = RECIPES_DIR / f"{slug}.html"
    if out_path.exists() and not force:
        print(f"Recipe file already exists: {out_path}")
        print("Use --force to regenerate it (index will not be updated).")
        sys.exit(1)

    html = render_recipe_page(d)
    out_path.write_text(html)
    print(f"{'Regenerated' if force else 'Created'}: {out_path}")

    if not force:
        add_card_to_index(d)
        print(f"Updated: {INDEX}")
    else:
        print("(index unchanged — use without --force to add a new card)")


if __name__ == "__main__":
    main()
