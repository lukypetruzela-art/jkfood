#!/usr/bin/env python3
"""Sestaví statické části webu J.K.FOOD.

Vytvoří / aktualizuje:
  - sortiment.html a 8 stránek skupin (sortiment-<skupina>.html) ze šablony tools/sortiment.template.html
  - v index.html: titulek, popis, metadata pro vyhledávače a sociální sítě, strukturovaná data,
    odkazy na skupiny v legendě a patičce
  - sitemap.xml
  - verze stylů a skriptů (?v=…), aby prohlížeče po změně načetly nové soubory

Zdroj výrobků: assets/sortiment-data.js. Po každé úpravě dat nebo šablony spusťte:
    python3 tools/build.py
"""
import datetime
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.kostera.cz"          # ostrá adresa webu (kanonické URL, sitemap, sociální sítě)
TODAY = datetime.date.today().isoformat()

ORG = {
    "name": "J.K.FOOD",
    "legal": "Jaroslav Kostera, J.K.FOOD s.r.o.",
    "ico": "27780384",
    "dic": "CZ27780384",
    "street": "Větřkovice 243",
    "city": "Větřkovice",
    "zip": "747 43",
    "phone": "+420556310205",
    "email": "kostera@kostera.cz",
    "founded": "1996",
    "founder": "Jaroslav Kostera",
    "same_as": ["https://www.facebook.com/Jaroslav-Kostera-JK-FOOD-355532857955037/"],
}

# osm skupin – pořadí musí odpovídat JK.CATS v assets/products.js
CATS = [
    dict(id="koreni", slug="koreni-jednodruhove", name="Koření jednodruhové",
         title="Jednodruhové koření celé, drcené i mleté",
         desc="Jednodruhové koření celé, drcené i mleté: pepř, paprika, kmín, koriandr, majoránka, badyán a další. Výroba J.K.FOOD ve Větřkovicích."),
    dict(id="smesi", slug="korenici-smesi", name="Kořenicí směsi",
         title="Kořenicí směsi podle vlastních receptur",
         desc="Kořenicí směsi J.K.FOOD podle vlastních receptur – na kuře, ryby, steak, gyros, guláš, grilování i svíčkovou. Pro jídelny, restaurace i výrobce."),
    dict(id="zelenina", slug="susena-zelenina", name="Sušená zelenina",
         title="Sušená zelenina – plátky, kostky, granule i pudr",
         desc="Sušená zelenina J.K.FOOD: cibule, česnek, karotka, celer, petržel, řepa, křen, špenát a zeleninové směsi v plátcích, kostkách, granulích i jako pudr."),
    dict(id="maso", slug="smesi-pro-masny-prumysl", name="Směsi pro masný průmysl",
         title="Kořenicí a kombi směsi pro masný průmysl",
         desc="Kořenicí a kombi směsi pro výrobu párků, salámů, klobás a šunek, lakovací nástřiky a technologické přísady. Směsi ladíme podle vaší technologie."),
    dict(id="houby", slug="susene-houby-a-plody", name="Sušené houby a plody",
         title="Sušené houby a suché plody",
         desc="Sušené houby – hřib pravý, liška, shiitake, hlíva – a suché plody: mandle, lískové a vlašské ořechy, rozinky, sušená jablka a švestky."),
    dict(id="polevky", slug="bujony-polevky-omacky", name="Bujóny, polévky, omáčky",
         title="Bujóny, polévky, omáčky a marinády",
         desc="Bujóny, polévky, omáčky, šťávy z pečeně a marinády J.K.FOOD pro školní a nemocniční jídelny, restaurace i domácí kuchyni."),
    dict(id="brambory", slug="bramborove-vyrobky", name="Bramborové výrobky",
         title="Bramborové kaše, knedlíky a halušky",
         desc="Bramborové kaše, bramborové a slezské knedlíky, halušky, bramborák a bramborové těsto J.K.FOOD pro velké i domácí kuchyně."),
    dict(id="testoviny", slug="skroby-testoviny", name="Škroby, těstoviny a další",
         title="Škroby, těstoviny a česnekové pasty",
         desc="Škroby (bramborový, kukuřičný, pšeničný, rýžový, tapiokový), těstoviny, česnekové pasty, paprikové výtažky, sladký program a další suroviny."),
]
for c in CATS:
    c["file"] = f"sortiment-{c['slug']}.html"

ALPHA = "aábcčdďeéěfghchiíjklmnňoópqrřsštťuúůvwxyýzž"


def cs_key(text):
    """České abecední řazení (včetně „ch“ za „h“)."""
    out = []
    for ch in text.lower().replace("ch", "\x01"):
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


def nbsp(s):
    """Nezalomitelná mezera za jednopísmennými předložkami (typografie)."""
    return re.sub(r"(?<=\s)([ksvzouaiKSVZOUAI]) ", r"\1&nbsp;", " " + s)[1:]


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>"


def head_common(title, desc, path, image=f"{SITE}/assets/icons/og-image.jpg"):
    url = f"{SITE}/{path}" if path else f"{SITE}/"
    return "\n".join([
        f'<link rel="canonical" href="{url}">',
        '<link rel="icon" href="favicon.ico" sizes="48x48">',
        '<link rel="icon" href="assets/icons/favicon.svg" type="image/svg+xml">',
        '<link rel="apple-touch-icon" href="assets/icons/apple-touch-icon.png">',
        '<link rel="manifest" href="site.webmanifest">',
        '<meta property="og:type" content="website">',
        '<meta property="og:locale" content="cs_CZ">',
        f'<meta property="og:site_name" content="{ORG["name"]}">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(desc)}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{image}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta property="og:image:alt" content="J.K.FOOD – Dáváme jídlu chuť. Od roku 1996.">',
        '<meta name="twitter:card" content="summary_large_image">',
    ])


def org_ld():
    return {
        "@type": "Organization", "@id": f"{SITE}/#firma",
        "name": ORG["name"], "legalName": ORG["legal"], "alternateName": "Jaroslav Kostera",
        "url": f"{SITE}/", "logo": f"{SITE}/assets/icons/logo-512.png", "image": f"{SITE}/assets/icons/og-image.jpg",
        "description": "Rodinná firma z Větřkovic na Opavsku. Od roku 1996 vyrábí koření, kořenicí směsi, "
                       "sušenou zeleninu a dehydratované potraviny pro průmysl, jídelny, gastro i domácnosti.",
        "foundingDate": ORG["founded"], "founder": {"@type": "Person", "name": ORG["founder"]},
        "vatID": ORG["dic"], "taxID": ORG["ico"], "telephone": ORG["phone"], "email": ORG["email"],
        "address": {"@type": "PostalAddress", "streetAddress": ORG["street"], "addressLocality": ORG["city"],
                    "postalCode": ORG["zip"], "addressRegion": "Moravskoslezský kraj", "addressCountry": "CZ"},
        "areaServed": "CZ", "sameAs": ORG["same_as"],
        "contactPoint": {"@type": "ContactPoint", "contactType": "sales", "telephone": ORG["phone"],
                         "email": ORG["email"], "availableLanguage": "cs"},
    }


def breadcrumbs_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": f"{SITE}/{u}" if u else f"{SITE}/"}
        for i, (n, u) in enumerate(items)]}


def asset_version():
    h = hashlib.sha1()
    for f in ["assets/styles.css", "assets/products.js"]:
        h.update((ROOT / f).read_bytes())
    return h.hexdigest()[:8]


def load_items():
    raw = (ROOT / "assets" / "sortiment-data.js").read_text(encoding="utf-8")
    items = json.loads(raw[raw.index("["): raw.rindex("]") + 1])
    items.sort(key=lambda p: (p["g"], cs_key(p["s"]), cs_key(p["n"])))
    return items


def render_list(items, cats_idx):
    out = []
    for gi in cats_idx:
        c = CATS[gi]
        g_items = [p for p in items if p["g"] == gi]
        if not g_items:
            continue
        head_tag = "h2"
        out.append(f'<section class="grp" id="sk-{c["id"]}" aria-labelledby="h-{c["id"]}">')
        title = (f'<a href="{c["file"]}">{esc(c["name"])}</a>' if len(cats_idx) > 1 else esc(c["name"]))
        out.append(
            f'<div class="grp-head"><span class="grp-ic"><canvas data-ic="{gi}" width="52" height="52" aria-hidden="true"></canvas></span>'
            f'<{head_tag} id="h-{c["id"]}">{title}</{head_tag}><span class="n">{len(g_items)} {plural(len(g_items))}</span></div>')
        subs = list(dict.fromkeys(p["s"] for p in g_items))
        for s in subs:
            out.append(f'<div class="sub" data-s="{esc(s)}">')
            if len(subs) > 1 or s != c["name"]:
                out.append(f"<h3>{esc(s)}</h3>")
            out.append('<ul class="items">')
            for p in g_items:
                if p["s"] == s:
                    href = "index.html?produkt=" + quote(p["n"], safe="") + "#kontakt"
                    out.append(f'<li><a class="item" href="{href}">{esc(p["n"])}</a></li>')
            out.append("</ul></div>")
        out.append("</section>")
    return "\n".join(out)


def render_chips(active):
    cur_all = ' aria-current="page"' if active is None else ""
    chips = [f'<a class="chip all" href="sortiment.html"{cur_all}>Vše</a>']
    for i, c in enumerate(CATS):
        cur = ' aria-current="page"' if active == i else ""
        chips.append(f'<a class="chip" href="{c["file"]}"{cur}><canvas data-ic="{i}" width="26" height="26" aria-hidden="true"></canvas>{esc(c["name"])}</a>')
    return "\n".join(chips)


def build_catalog(items, v):
    tpl = (ROOT / "tools" / "sortiment.template.html").read_text(encoding="utf-8")
    footcats = "".join(f'<li><a href="{c["file"]}">{esc(c["name"])}</a></li>' for c in CATS)
    legacy = ", ".join(f"'{c['id']}': '{c['file']}'" for c in CATS)
    pages = [None] + list(range(len(CATS)))
    for active in pages:
        if active is None:
            file, h1 = "sortiment.html", "Sortiment"
            title = "Sortiment koření, směsí a sušených potravin | J.K.FOOD"
            desc = ("Přes 490 výrobků J.K.FOOD: koření, kořenicí směsi, sušená zelenina, směsi pro masný průmysl, "
                    "houby, bujóny, polévky, bramborové výrobky a těstoviny.")
            intro = ("Přes 490 výrobků v osmi skupinách. U každého výrobku můžete rovnou poslat poptávku, "
                     "balení pro domácnost najdete v e-shopu.")
            crumbs = [("Úvod", ""), ("Sortiment", "sortiment.html")]
            shown = items
            cats_idx = list(range(len(CATS)))
            placeholder = "Hledat, např. pepř, guláš, šunka…"
        else:
            c = CATS[active]
            file, h1 = c["file"], c["name"]
            title = f"{c['title']} | J.K.FOOD"
            desc = c["desc"]
            intro = c["desc"]
            crumbs = [("Úvod", ""), ("Sortiment", "sortiment.html"), (c["name"], c["file"])]
            shown = [p for p in items if p["g"] == active]
            cats_idx = [active]
            placeholder = "Hledat v této skupině…"

        crumbs_html = '<nav class="crumbs" aria-label="Drobečková navigace">' + '<span aria-hidden="true">/</span>'.join(
            (f'<a href="{u or "index.html"}">{esc(n)}</a>' if i < len(crumbs) - 1 else f'<span aria-current="page">{esc(n)}</span>')
            for i, (n, u) in enumerate(crumbs)) + "</nav>"
        graph = [org_ld(), breadcrumbs_ld(crumbs), {
            "@type": "CollectionPage", "@id": f"{SITE}/{file}#stranka", "url": f"{SITE}/{file}", "name": h1,
            "description": desc, "inLanguage": "cs", "isPartOf": {"@id": f"{SITE}/#web"},
            "publisher": {"@id": f"{SITE}/#firma"},
            "mainEntity": {"@type": "ItemList", "numberOfItems": len(shown),
                           "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": p["n"]}
                                               for i, p in enumerate(shown)]},
        }]
        head = head_common(title, desc, file) + "\n" + ld({"@context": "https://schema.org", "@graph": graph})
        page = (tpl.replace("{{TITLE}}", esc(title)).replace("{{DESCRIPTION}}", esc(desc)).replace("{{HEAD}}", head)
                .replace("{{V}}", v).replace("{{CRUMBS}}", crumbs_html).replace("{{H1}}", esc(h1))
                .replace("{{INTRO}}", nbsp(esc(intro))).replace("{{PLACEHOLDER}}", esc(placeholder))
                .replace("{{CHIPS}}", render_chips(active)).replace("{{LIST}}", render_list(items, cats_idx))
                .replace("{{COUNT}}", f"Celkem {len(shown)} {plural(len(shown))}")
                .replace("{{FOOTCATS}}", footcats).replace("{{LEGACY}}", legacy if active is None else ""))
        assert "{{" not in page, re.findall(r"\{\{\w+\}\}", page)
        (ROOT / file).write_text(page, encoding="utf-8")
    return [("sortiment.html", "0.9")] + [(c["file"], "0.8") for c in CATS]


def build_index(v):
    p = ROOT / "index.html"
    s = p.read_text(encoding="utf-8")
    title = "J.K.FOOD – výrobce koření a kořenicích směsí z Větřkovic"
    desc = ("Rodinná firma z Větřkovic na Opavsku. Od roku 1996 vyrábíme koření, kořenicí směsi, sušenou "
            "zeleninu a dehydratované potraviny pro průmysl, jídelny a gastro.")
    graph = [org_ld(), {
        "@type": "WebSite", "@id": f"{SITE}/#web", "url": f"{SITE}/", "name": ORG["name"],
        "inLanguage": "cs", "publisher": {"@id": f"{SITE}/#firma"},
        }]
    meta = "\n".join([
        f"<title>{esc(title)}</title>",
        f'<meta name="description" content="{esc(desc)}">',
        head_common(title, desc, ""),
        ld({"@context": "https://schema.org", "@graph": graph}),
    ])
    s = re.sub(r"<!-- META:START -->.*?<!-- META:END -->", lambda m: f"<!-- META:START -->\n{meta}\n<!-- META:END -->", s, flags=re.S)
    legend = "\n".join(
        f'<li><a href="{c["file"]}" data-cat="{i}"><canvas class="sw-ic" data-ic="{i}" width="28" height="28" aria-hidden="true"></canvas><span class="nm">{esc(c["name"])}</span></a></li>'
        for i, c in enumerate(CATS))
    s = re.sub(r"<!-- LEGEND:START -->.*?<!-- LEGEND:END -->", lambda m: f"<!-- LEGEND:START -->\n{legend}\n<!-- LEGEND:END -->", s, flags=re.S)
    foot = "".join(f'<li><a href="{c["file"]}">{esc(c["name"])}</a></li>' for c in CATS)
    s = re.sub(r"<!-- FOOTCATS:START -->.*?<!-- FOOTCATS:END -->", lambda m: f"<!-- FOOTCATS:START -->{foot}<!-- FOOTCATS:END -->", s, flags=re.S)
    s = re.sub(r'(assets/(?:styles\.css|products\.js))\?v=\w+', rf"\1?v={v}", s)
    p.write_text(s, encoding="utf-8")

    # stránka 404 (zobrazuje se na libovolné adrese, proto absolutní cesty)
    p404 = ROOT / "404.html"
    if p404.exists():
        t = p404.read_text(encoding="utf-8")
        foot404 = "".join(f'<li><a href="/{c["file"]}">{esc(c["name"])}</a></li>' for c in CATS)
        t = re.sub(r"<!-- FOOTCATS:START -->.*?<!-- FOOTCATS:END -->", lambda m: f"<!-- FOOTCATS:START -->{foot404}<!-- FOOTCATS:END -->", t, flags=re.S)
        t = re.sub(r'(assets/styles\.css)\?v=\w+', rf"\1?v={v}", t)
        p404.write_text(t, encoding="utf-8")


def build_sitemap(pages):
    urls = [("", "1.0")] + pages
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, prio in urls:
        xml.append(f"  <url><loc>{SITE}/{path}</loc><lastmod>{TODAY}</lastmod><priority>{prio}</priority></url>")
    xml.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(xml) + "\n", encoding="utf-8")


def main():
    v = asset_version()
    items = load_items()
    pages = build_catalog(items, v)
    build_index(v)
    build_sitemap(pages)
    print(f"hotovo: {len(items)} výrobků, {len(pages)} stránek sortimentu, verze stylů {v}")


if __name__ == "__main__":
    main()
