#!/usr/bin/env python3
"""Vygeneruje statický výpis sortimentu do sortiment.html.

Zdroj dat: assets/sortiment-data.js (window.SORTIMENT = [...]).
Výpis se vkládá mezi značky <!-- SORTIMENT:START --> a <!-- SORTIMENT:END -->
(a stejně tak filtry mezi <!-- CHIPS:START/END -->), takže je stránka hotová
hned po načtení: nic neposkakuje a vyhledávače vidí všechny názvy výrobků.

Použití (z kořene repozitáře):  python3 tools/build_sortiment.py
"""
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "assets" / "sortiment-data.js"
PAGE = ROOT / "sortiment.html"

# musí odpovídat JK.CATS v assets/products.js
CATS = [
    ("koreni", "Koření jednodruhové"),
    ("smesi", "Kořenicí směsi"),
    ("zelenina", "Sušená zelenina"),
    ("maso", "Směsi pro masný průmysl"),
    ("houby", "Sušené houby a plody"),
    ("polevky", "Bujóny, polévky, omáčky"),
    ("brambory", "Bramborové výrobky"),
    ("testoviny", "Škroby, těstoviny a další"),
]

ALPHA = "aábcčdďeéěfghchiíjklmnňoópqrřsštťuúůvwxyýzž"


def cs_key(text):
    """České abecední řazení (včetně „ch“ za „h“)."""
    t = text.lower().replace("ch", "\x01")
    out = []
    for ch in t:
        if ch == "\x01":
            out.append(ALPHA.index("h") + 0.5)
        elif ch in ALPHA:
            out.append(ALPHA.index(ch))
        else:
            out.append(100 + ord(ch))
    return out


def plural(n):
    return "výrobek" if n == 1 else "výrobky" if 2 <= n <= 4 else "výrobků"


def esc(s):
    return html.escape(s, quote=True)


def main():
    raw = DATA.read_text(encoding="utf-8")
    items = json.loads(raw[raw.index("["): raw.rindex("]") + 1])
    items.sort(key=lambda p: (p["g"], cs_key(p["s"]), cs_key(p["n"])))

    chips = ['<button type="button" class="chip all" data-id="" aria-pressed="true">Vše</button>']
    for i, (cid, name) in enumerate(CATS):
        chips.append(
            f'<button type="button" class="chip" data-id="{cid}" aria-pressed="false">'
            f'<canvas data-ic="{i}" width="26" height="26" aria-hidden="true"></canvas>{esc(name)}</button>'
        )

    out = []
    for gi, (cid, name) in enumerate(CATS):
        g_items = [p for p in items if p["g"] == gi]
        if not g_items:
            continue
        out.append(f'<section class="grp" id="sk-{cid}" data-id="{cid}" aria-labelledby="h-{cid}">')
        out.append(
            f'<div class="grp-head"><span class="grp-ic"><canvas data-ic="{gi}" width="52" height="52" aria-hidden="true"></canvas></span>'
            f'<h2 id="h-{cid}">{esc(name)}</h2><span class="n">{len(g_items)} {plural(len(g_items))}</span></div>'
        )
        subs = list(dict.fromkeys(p["s"] for p in g_items))
        for s in subs:
            out.append(f'<div class="sub" data-s="{esc(s)}">')
            if len(subs) > 1 or s != name:
                out.append(f"<h3>{esc(s)}</h3>")
            out.append('<ul class="items">')
            for p in g_items:
                if p["s"] != s:
                    continue
                href = "index.html?produkt=" + quote(p["n"], safe="") + "#kontakt"
                out.append(f'<li><a class="item" href="{href}">{esc(p["n"])}</a></li>')
            out.append("</ul></div>")
        out.append("</section>")

    page = PAGE.read_text(encoding="utf-8")
    page = re.sub(r"(<!-- CHIPS:START -->).*?(<!-- CHIPS:END -->)",
                  lambda m: m.group(1) + "\n" + "\n".join(chips) + "\n" + m.group(2), page, flags=re.S)
    page = re.sub(r"(<!-- SORTIMENT:START -->).*?(<!-- SORTIMENT:END -->)",
                  lambda m: m.group(1) + "\n" + "\n".join(out) + "\n" + m.group(2), page, flags=re.S)
    page = re.sub(r'(<p class="cat-count" id="count">)[^<]*(</p>)',
                  lambda m: f"{m.group(1)}Celkem {len(items)} {plural(len(items))}{m.group(2)}", page)
    PAGE.write_text(page, encoding="utf-8")
    print(f"sortiment.html: {len(items)} výrobků ve {len(CATS)} skupinách")


if __name__ == "__main__":
    main()
