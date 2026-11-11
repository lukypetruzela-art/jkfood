#!/usr/bin/env python3
"""Sestaví statické části webu J.K.FOOD.

Vytvoří / aktualizuje:
  - sortiment.html a 8 stránek skupin (sortiment-<skupina>.html) ze šablony tools/sortiment.template.html
  - v index.html: titulek, popis, metadata pro vyhledávače a sociální sítě, strukturovaná data,
    odkazy na skupiny v legendě a patičce
  - nas-tym.html (Náš tým) z assets/tym.json, kariera.html (Kariéra) z assets/kariera.json
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

# devět skupin – pořadí musí odpovídat JK.CATS v assets/products.js
CATS = [
    dict(id="testoviny", slug="testoviny", name="Těstoviny",
         title="Těstoviny – vřetena, kolínka, široké i řezané",
         desc="Těstoviny J.K.FOOD: vřetena, kolínka, široké, řezané, větrníky, těstovinová rýže i tagliatelle s medvědím česnekem. Pro jídelny, gastro i domácnosti."),
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
    dict(id="skroby", slug="skroby-a-dalsi", name="Škroby a další",
         title="Škroby, česnekové pasty a další suroviny",
         desc="Škroby (bramborový, kukuřičný, pšeničný, rýžový, tapiokový), česnekové pasty, paprikové výtažky, sladký program a další suroviny pro výrobu i kuchyně."),
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


def head_common(title, desc, path, image=f"{SITE}/assets/icons/og-image.jpg", lang="cs", alternates=None):
    url = f"{SITE}/{path}" if path else f"{SITE}/"
    alt = []
    if alternates:   # {"cs": cesta, "en": cesta}
        for hl, ap in alternates.items():
            alt.append(f'<link rel="alternate" hreflang="{hl}" href="{SITE}/{ap}">')
        alt.append(f'<link rel="alternate" hreflang="x-default" href="{SITE}/{alternates["cs"]}">')
    return "\n".join(alt + [
        f'<link rel="canonical" href="{url}">',
        '<link rel="icon" href="favicon.ico" sizes="48x48">',
        '<link rel="icon" href="assets/icons/favicon.svg" type="image/svg+xml">',
        '<link rel="apple-touch-icon" href="assets/icons/apple-touch-icon.png">',
        '<link rel="manifest" href="site.webmanifest">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:locale" content="{"en_GB" if lang == "en" else "cs_CZ"}">',
        f'<meta property="og:site_name" content="{ORG["name"]}">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(desc)}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{image}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta property="og:image:alt" content="J.K.FOOD – Dáváme jídlu chuť. Od roku 1996.">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">',
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
        "areaServed": {"@type": "Country", "name": "Česká republika"}, "sameAs": ORG["same_as"],
        "foundingLocation": {"@type": "Place", "name": "Větřkovice, okres Opava"},
        "numberOfEmployees": {"@type": "QuantitativeValue", "minValue": 100},
        "slogan": "Dáváme jídlu chuť. Od roku 1996.",
        "knowsAbout": ["koření", "kořenicí směsi", "sušená zelenina", "dehydratované potraviny",
                       "směsi pro masný průmysl", "kombi směsi", "bujóny a polévky", "vývoj kořenicích směsí na míru",
                       "velkoobchod koření", "dodávky pro školní a nemocniční jídelny"],
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Sortiment J.K.FOOD", "url": f"{SITE}/sortiment.html",
                            "itemListElement": [{"@type": "OfferCatalog", "name": c["name"], "url": f"{SITE}/{c['file']}"} for c in CATS]},
        "contactPoint": [
            {"@type": "ContactPoint", "contactType": "sales", "telephone": ORG["phone"], "email": ORG["email"],
             "availableLanguage": ["cs", "en"], "areaServed": "CZ"},
            {"@type": "ContactPoint", "contactType": "sales", "name": "Jana Galčanová, obchodní ředitel",
             "telephone": "+420777340321", "email": "jana.galcanova@kostera.cz"}],
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
    hd, ft = site_chrome("sortiment.html", "products.html")   # menu a patička z úvodní stránky
    legacy = ", ".join(f"'{c['id']}': '{c['file']}'" for c in CATS)
    pages = [None] + list(range(len(CATS)))
    for active in pages:
        if active is None:
            file, h1 = "sortiment.html", "Sortiment"
            title = "Sortiment koření, směsí a sušených potravin | J.K.FOOD"
            desc = ("Přes 490 výrobků J.K.FOOD: koření, kořenicí směsi, sušená zelenina, směsi pro masný průmysl, "
                    "houby, bujóny, polévky, bramborové výrobky a těstoviny.")
            intro = ("Přes 490 výrobků v devíti skupinách. U každého výrobku můžete rovnou poslat poptávku, "
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
        alts = {"cs": file, "en": "en/products.html"} if active is None else None
        head = head_common(title, desc, file, alternates=alts) + "\n" + ld({"@context": "https://schema.org", "@graph": graph})
        page = (tpl.replace("{{TITLE}}", esc(title)).replace("{{DESCRIPTION}}", esc(desc)).replace("{{HEAD}}", head)
                .replace("{{V}}", v).replace("{{CRUMBS}}", crumbs_html).replace("{{H1}}", esc(h1))
                .replace("{{INTRO}}", nbsp(esc(intro))).replace("{{PLACEHOLDER}}", esc(placeholder))
                .replace("{{CHIPS}}", render_chips(active)).replace("{{LIST}}", render_list(items, cats_idx))
                .replace("{{COUNT}}", f"Celkem {len(shown)} {plural(len(shown))}")
                .replace("{{HEADER}}", hd).replace("{{FOOTER}}", ft).replace("{{LEGACY}}", legacy if active is None else ""))
        assert "{{" not in page, re.findall(r"\{\{\w+\}\}", page)
        (ROOT / file).write_text(page, encoding="utf-8")
    return [("sortiment.html", "0.9")] + [(c["file"], "0.8") for c in CATS]


def render_refs():
    """Slider referencí na úvodní stránce z assets/reference.json."""
    data = json.loads((ROOT / "assets" / "reference.json").read_text(encoding="utf-8"))
    cards = []
    for r in data["polozky"]:
        ph = r["nazev"].strip().startswith("[")
        if r.get("logo"):
            logo = f'<img src="img/reference/{esc(r["logo"])}" alt="{esc(r["nazev"])}" width="400" height="200" loading="lazy" decoding="async">'
        else:
            logo = '<svg class="ref-mk" viewBox="0 0 97.6 97.6" fill="currentColor" aria-hidden="true"><use href="#mark"/></svg>'
        quote_html = ""
        if r.get("citace"):
            quote_html = f'<blockquote class="ref-quote">„{esc(r["citace"])}“</blockquote>' + (f'<p class="ref-who">{esc(r["osoba"])}</p>' if r.get("osoba") else "")
        cards.append(f'<li class="ref{" is-empty" if ph else ""}"><div class="ref-logo">{logo}</div>'
                     f'<p class="ref-type">{esc(r["typ"])}</p><h3>{esc(r["nazev"])}</h3>{quote_html}</li>')
    return f"""      <div class="refs-head">
        <div>
          <h2 class="h2" id="ref-title">{esc(data["nadpis"])}</h2>
          <p class="intro">{nbsp(esc(data["intro"]))}</p>
        </div>
      </div>
      <div class="ref-slider" id="refSlider">
        <ul class="ref-track" tabindex="0" aria-label="Reference – posouvejte šipkami vlevo a vpravo">
          {"".join(cards)}
        </ul>
        <div class="ref-ctrl">
          <div class="ref-bar" aria-hidden="true"><i></i></div>
          <button type="button" class="ref-play g-play" aria-pressed="false" aria-label="Pozastavit posouvání referencí"><svg viewBox="0 0 16 16" aria-hidden="true"><path class="i-pause" d="M4.5 3h2.2v10H4.5zM9.3 3h2.2v10H9.3z"/><path class="i-play" d="M5 3l8 5-8 5z"/></svg></button>
          <button type="button" class="ref-prev ref-arrow" aria-label="Předchozí reference"><span class="i-prev" aria-hidden="true"></span></button>
          <button type="button" class="ref-next ref-arrow" aria-label="Další reference"><span class="i-next" aria-hidden="true"></span></button>
        </div>
      </div>"""

def faq_data(lang):
    return json.loads((ROOT / "assets" / "faq.json").read_text(encoding="utf-8"))[lang]


def render_faq(lang="cs"):
    """Časté dotazy (rozbalovací) z assets/faq.json."""
    d = faq_data(lang)
    intro = esc(d["intro"])
    intro = re.sub(r"\+420 556 310 205", '<a href="tel:+420556310205">+420 556 310 205</a>', intro)
    items = "".join(f'<details><summary>{esc(q)}<span class="job-toggle" aria-hidden="true"></span></summary>'
                    f'<p class="faq-a">{nbsp(esc(a)) if lang == "cs" else esc(a)}</p></details>' for q, a in d["polozky"])
    return f"""      <div class="faq-grid">
        <div class="faq-side">
          <h2 class="h2" id="faq-title">{esc(d["nadpis"])}</h2>
          <p class="intro">{intro}</p>
        </div>
        <div class="faq">{items}</div>
      </div>"""


def faq_ld(lang="cs"):
    d = faq_data(lang)
    return {"@type": "FAQPage", "inLanguage": lang, "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in d["polozky"]]}


def build_index(v):
    p = ROOT / "index.html"
    s = p.read_text(encoding="utf-8")
    title = "J.K.FOOD – koření a ingredience pro potravinářský průmysl"
    desc = ("Vyvíjíme, vyrábíme, dodáváme: koření, kořenicí směsi a dehydratované potraviny od receptury "
            "po sériovou výrobu pro průmysl, gastro i retail. Od roku 1996.")
    graph = [org_ld(), {
        "@type": "WebSite", "@id": f"{SITE}/#web", "url": f"{SITE}/", "name": ORG["name"],
        "inLanguage": "cs", "publisher": {"@id": f"{SITE}/#firma"},
        }, faq_ld("cs")]
    meta = "\n".join([
        f"<title>{esc(title)}</title>",
        f'<meta name="description" content="{esc(desc)}">',
        head_common(title, desc, "", alternates={"cs": "", "en": "en/"}),
        ld({"@context": "https://schema.org", "@graph": graph}),
    ])
    s = re.sub(r"<!-- META:START -->.*?<!-- META:END -->", lambda m: f"<!-- META:START -->\n{meta}\n<!-- META:END -->", s, flags=re.S)
    foot = "".join(f'<li><a href="{c["file"]}">{esc(c["name"])}</a></li>' for c in CATS)
    s = re.sub(r"<!-- FOOTCATS:START -->.*?<!-- FOOTCATS:END -->", lambda m: f"<!-- FOOTCATS:START -->{foot}<!-- FOOTCATS:END -->", s, flags=re.S)
    s = re.sub(r"<!-- FAQ:START -->.*?<!-- FAQ:END -->", lambda m: f"<!-- FAQ:START -->\n{render_faq('cs')}\n<!-- FAQ:END -->", s, flags=re.S)
    s = re.sub(r"<!-- REFERENCE:START -->.*?<!-- REFERENCE:END -->", lambda m: f"<!-- REFERENCE:START -->\n{render_refs()}\n<!-- REFERENCE:END -->", s, flags=re.S)
    s = re.sub(r'(assets/(?:styles\.css|products\.js))\?v=\w+', rf"\1?v={v}", s)
    # rychlost: úvodní fotka se začne stahovat hned a styly jsou přímo ve stránce (odpadá blokující požadavek)
    css = (ROOT / "assets" / "styles.css").read_text(encoding="utf-8").replace("url(fonts/", "url(assets/fonts/")
    home = ('<link rel="preload" as="image" href="img/uvod-m-600.avif" media="(max-width:760px)" type="image/avif" fetchpriority="high">\n'
            '<link rel="preload" as="image" href="img/uvod-1536.avif" imagesrcset="img/uvod-900.avif 900w, img/uvod-1536.avif 1536w" '
            'imagesizes="100vw" media="(min-width:761px)" type="image/avif" fetchpriority="high">\n'
            f"<style>{css}</style>")
    s = re.sub(r"<!-- HOME:START -->.*?<!-- HOME:END -->", lambda m: f"<!-- HOME:START -->\n{home}\n<!-- HOME:END -->", s, flags=re.S)
    rows = cat_rows(load_items(), [c["id"] for c in CATS]) + [cat_row(
        "hotova-jidla.html", "Vlastní značky", "Hotová jídla v kelímku CHUŤ a HOT&GO", "stačí zalít horkou vodou – kompletní jídlo za pár minut")]
    s = re.sub(r"<!-- SORTLIST:START -->.*?<!-- SORTLIST:END -->",
               lambda m: "<!-- SORTLIST:START -->\n" + "\n".join("          " + r for r in rows) + "\n<!-- SORTLIST:END -->", s, flags=re.S)
    p.write_text(s, encoding="utf-8")

    # stránka 404 (zobrazuje se na libovolné adrese, proto absolutní cesty)
    p404 = ROOT / "404.html"
    if p404.exists():
        t = p404.read_text(encoding="utf-8")
        t = re.sub(r'(assets/styles\.css)\?v=\w+', rf"\1?v={v}", t)
        hd, ft = site_chrome(absolute=True)
        t = re.sub(r'<header class="top".*?</header>', lambda m: hd, t, count=1, flags=re.S)
        t = re.sub(r'<footer class="foot">.*?</footer>', lambda m: ft, t, count=1, flags=re.S)
        p404.write_text(t, encoding="utf-8")


def site_chrome(nav_current=None, en_file=None, absolute=False):
    """Hlavička a patička z úvodní stránky pro podstránky (jedno místo pravdy pro menu a patičku)."""
    idx = (ROOT / "index.html").read_text(encoding="utf-8")
    header = idx[idx.index('<header class="top"'): idx.index("</header>") + 9]
    footer = idx[idx.index('<footer class="foot">'): idx.index("</footer>") + 9]

    def relink(x):
        x = re.sub(r'href="#(?!logo|mark|obsah")([\w-]+)"', r'href="index.html#\1"', x)
        x = x.replace('<a class="brand" href="#"', '<a class="brand" href="index.html"').replace('<a href="index.html#">', '<a href="#">')
        if absolute:    # stránka 404 se zobrazuje na libovolné adrese
            x = re.sub(r'href="(?!https?:|#|mailto:|tel:|/)([^"]*)"', r'href="/\1"', x)
        return x
    header, footer = relink(header), relink(footer)
    lang = ("/" if absolute else "") + f'en/{en_file or "index.html"}'
    header = re.sub(r'<a class="link lang" href="[^"]*"', f'<a class="link lang" href="{lang}"', header, count=1)
    if nav_current:
        cur = ("/" if absolute else "") + nav_current
        header = header.replace(f'<a class="link" href="{cur}">', f'<a class="link" href="{cur}" aria-current="page">')
    return header, footer


def simple_page(file, title, desc, crumbs, h1, intro, body, cta, graph, nav_current=None, en_file=None, write=True):
    """Podstránka se stejnou hlavičkou a patičkou jako index.html (Náš tým, Kariéra)."""
    idx = (ROOT / "index.html").read_text(encoding="utf-8")
    head_start = idx[: idx.index("<!-- META:START -->")]
    head_rest = idx[idx.index("<!-- META:END -->") + len("<!-- META:END -->"): idx.index("</head>")]
    head_rest = re.sub(r"<!-- HOME:START -->.*?<!-- HOME:END -->",
                       lambda m: f'<link rel="stylesheet" href="assets/styles.css?v={asset_version()}">', head_rest, flags=re.S)
    symbols = idx[idx.index('<svg width="0"'): idx.index("</svg>", idx.index('<svg width="0"')) + 6]
    header, footer = site_chrome(nav_current, en_file)

    meta = "\n".join([f"<title>{esc(title)}</title>", f'<meta name="description" content="{esc(desc)}">',
                      head_common(title, desc, file, alternates={"cs": file, "en": f"en/{en_file}"} if en_file else None),
                      ld({"@context": "https://schema.org", "@graph": [org_ld(), breadcrumbs_ld(crumbs)] + graph})])
    crumbs_html = '<nav class="crumbs" aria-label="Drobečková navigace">' + '<span aria-hidden="true">/</span>'.join(
        (f'<a href="{u or "index.html"}">{esc(n)}</a>' if i < len(crumbs) - 1 else f'<span aria-current="page">{esc(n)}</span>')
        for i, (n, u) in enumerate(crumbs)) + "</nav>"
    page = f"""{head_start}{meta}{head_rest}</head>
<body>
{symbols}

<a class="skip" href="#obsah">Přeskočit na obsah</a>

{header}

<main id="obsah">
  <section class="cat-head" aria-labelledby="page-title">
    <div class="wrap">
      {crumbs_html}
      <h1 class="h2 cat-title" id="page-title">{esc(h1)}</h1>
      <p class="intro">{nbsp(esc(intro))}</p>
    </div>
  </section>
  <div class="wrap page-body">
    {body}
  </div>
  {cta}
</main>

{footer}

<script>
(() => {{
  const top = document.getElementById('top'), burger = top.querySelector('.burger'), nav = document.getElementById('nav');
  const setMenu = open => {{
    nav.classList.toggle('open', open); burger.setAttribute('aria-expanded', open);
    burger.setAttribute('aria-label', open ? 'Zavřít menu' : 'Otevřít menu'); document.body.style.overflow = open ? 'hidden' : '';
  }};
  burger.addEventListener('click', () => setMenu(!nav.classList.contains('open')));
  matchMedia('(min-width: 1181px)').addEventListener('change', e => {{ if (e.matches) setMenu(false); }});
  nav.addEventListener('click', e => {{ if (e.target.closest('a')) setMenu(false); }});
  addEventListener('keydown', e => {{ if (e.key === 'Escape' && nav.classList.contains('open')) {{ setMenu(false); burger.focus(); }} }});
  const onScroll = () => top.classList.toggle('scrolled', scrollY > 8);
  addEventListener('scroll', onScroll, {{ passive: true }}); onScroll();
}})();
</script>
</body>
</html>
"""
    if write:
        (ROOT / file).write_text(page, encoding="utf-8")
    return page


def cta_band(cid, title, text, buttons):
    btns = "".join(f'<a class="btn {cls}" href="{href}">{label}</a>' for cls, href, label in buttons)
    return f"""<section class="shop cat-cta" aria-labelledby="{cid}">
    <div class="wrap">
      <div>
        <h2 class="h2" id="{cid}">{title}</h2>
        <p>{text}</p>
        <div class="cat-cta-btns">{btns}</div>
      </div>
      <svg class="shop-mark" viewBox="0 0 97.6 97.6" fill="currentColor" aria-hidden="true" style="--s:1;--o:.35"><use href="#mark"/></svg>
    </div>
  </section>"""


def tel_href(t):
    return "tel:" + re.sub(r"[^+0-9]", "", t)


def build_team(v):
    """Stránka Náš tým (nas-tym.html) z assets/tym.json."""
    data = json.loads((ROOT / "assets" / "tym.json").read_text(encoding="utf-8"))
    placeholder = lambda t: t.strip().startswith("[")
    people_ld = []

    def card(p):
        name, role = p.get("jmeno", ""), p.get("pozice", "")
        ph = placeholder(name)
        if p.get("foto"):
            img = f'<img src="img/tym/{esc(p["foto"])}" alt="{esc(name)}" width="800" height="1000" loading="lazy" decoding="async">'
        else:
            words = [w for w in name.split() if not w.endswith(".")]   # bez titulů (Bc., Ing. …)
            ini = "".join(w[0] for w in words[:2]).upper() if not ph else ""
            img = f'<span class="person-ini" aria-hidden="true">{esc(ini)}</span>'
        bits = [f'<li class="person{" is-empty" if ph else ""}">', f'<div class="person-ph">{img}</div>',
                f"<h3>{esc(name)}</h3>", f'<p class="person-role">{esc(role)}</p>']
        if p.get("oblast"):
            bits.append(f'<p class="person-area">{esc(p["oblast"])}</p>')
        links = []
        if p.get("telefon"):
            links.append(f'<a href="{tel_href(p["telefon"])}">{esc(p["telefon"])}</a>')
        if p.get("email"):
            links.append(f'<a href="mailto:{esc(p["email"])}">{esc(p["email"])}</a>')
        if links:
            bits.append('<p class="person-contact">' + "".join(links) + "</p>")
        bits.append("</li>")
        if not ph:
            person = {"@type": "Person", "name": name, "jobTitle": role, "worksFor": {"@id": f"{SITE}/#firma"}}
            if p.get("telefon"): person["telephone"] = p["telefon"]
            if p.get("email"): person["email"] = p["email"]
            people_ld.append(person)
        return "".join(bits)

    groups = []
    for i, g in enumerate(data["skupiny"]):
        gid = f"tym-{i + 1}"
        groups.append(f'<section class="team-grp" aria-labelledby="{gid}"><div class="team-grp-head"><h2 id="{gid}">{esc(g["nazev"])}</h2>'
                      + (f'<p>{nbsp(esc(g["popis"]))}</p>' if g.get("popis") else "") + "</div>"
                      + '<ul class="team">' + "".join(card(p) for p in g["lide"]) + "</ul></section>")

    desc = "Seznamte se s lidmi z J.K.FOOD – vedení, obchodní zástupci, výroba a vývoj kořenicích směsí ve Větřkovicích."
    graph = [{"@type": "AboutPage", "@id": f"{SITE}/nas-tym.html#stranka", "url": f"{SITE}/nas-tym.html", "name": "Náš tým",
              "description": desc, "inLanguage": "cs", "about": {"@id": f"{SITE}/#firma"},
              **({"mainEntity": people_ld} if people_ld else {})}]
    cta = cta_band("team-cta", "Ozvěte se nám",
                   "Rádi s&nbsp;vámi probereme nabídku, vzorky i&nbsp;směs připravenou přesně pro vaši výrobu.",
                   [("btn-white", "index.html#kontakt", "Napsat poptávku"), ("btn-ghost", "kariera.html", "Chcete k&nbsp;nám? Kariéra")])
    simple_page("nas-tym.html", "Náš tým | J.K.FOOD Větřkovice", desc,
                [("Úvod", ""), ("O nás", "index.html#pribeh"), ("Náš tým", "nas-tym.html")],
                "Náš tým", data["intro"], "".join(groups), cta, graph, nav_current="nas-tym.html", en_file="team.html")
    return [("nas-tym.html", "0.6")]


JOBS_EMPTY = '<li class="job-empty">Momentálně nemáme vypsanou žádnou pozici. Pošlete nám ale životopis – rádi se vám ozveme.</li>'


def jobs_count(n):
    if n == 0:
        return "Žádná volná pozice"
    return f'{n} {"pozice" if n <= 4 else "pozic"} · klikněte pro podrobnosti'


# stejné vykreslení jako v build_career, ale v prohlížeči z aktuálních dat administrace
CAREER_JS = r"""(()=>{const E=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const nb=s=>E(s).replace(/ ([aikosuvzAIKOSUVZ]) /g,' $1&nbsp;');
fetch('api/kariera.php',{cache:'no-store'}).then(r=>r.ok&&/json/.test(r.headers.get('content-type')||'')?r.json():null).then(d=>{if(!d||!Array.isArray(d.pozice))return;
const mail=d.kontakt_email,act=d.pozice.filter(j=>j.aktivni!==false),n=act.length;
const intro=document.querySelector('.cat-head .intro');if(intro&&d.intro)intro.innerHTML=nb(d.intro);
const why=document.querySelector('.career-why .why');if(why&&Array.isArray(d.proc))why.innerHTML=d.proc.map(w=>'<li><h3>'+E(w.nadpis)+'</h3><p>'+nb(w.text)+'</p></li>').join('');
document.getElementById('jobsCount').textContent=n?n+' '+(n<=4?'pozice':'pozic')+' · klikněte pro podrobnosti':'Žádná volná pozice';
const L=[['nabizime','Nabízíme'],['pozadujeme','Požadujeme'],['naplne','Náplň práce']];
document.getElementById('jobs').innerHTML=n?act.map((j,i)=>{const cols=L.filter(([k])=>(j[k]||[]).length).map(([k,l])=>'<div><h4>'+l+'</h4><ul>'+j[k].map(x=>'<li>'+E(x)+'</li>').join('')+'</ul></div>').join('');
const m=j.kontakt_email||mail,tel=j.kontakt_tel;
return '<li class="job"><details'+(i?'':' open')+'><summary><h3>'+E(j.nazev)+'</h3><span class="job-tags">'+(j.stitky||[]).map(t=>'<span>'+E(t)+'</span>').join('')+'</span><span class="job-toggle" aria-hidden="true"></span></summary>'
+'<div class="job-body"><div class="job-cols">'+cols+'</div><div class="job-actions"><a class="btn btn-red" href="mailto:'+E(m)+'?subject='+encodeURIComponent('Zájem o pozici: '+j.nazev)+'">Mám zájem – poslat životopis</a>'
+(tel?'<a class="btn btn-line" href="tel:'+E(tel.replace(/[^+0-9]/g,''))+'">Zavolat '+E(tel)+'</a>':'')+'</div></div></details></li>';}).join(''):"""
CAREER_JS += repr(JOBS_EMPTY) + r""";
const ld=document.getElementById('jobsLd');if(ld){const L2=[['nabizime','Nabízíme'],['pozadujeme','Požadujeme'],['naplne','Náplň práce']];
ld.textContent=JSON.stringify(act.filter(j=>j.zverejneno&&j.nazev.indexOf('[')<0).map(j=>{const d=new Date(j.zverejneno);d.setDate(d.getDate()+90);
return {'@context':'https://schema.org','@type':'JobPosting',title:j.nazev,description:'<p>'+E(j.nazev)+' – J.K.FOOD, Větřkovice.</p>'+L2.filter(([k])=>(j[k]||[]).length).map(([k,l])=>'<h3>'+l+'</h3><ul>'+j[k].map(x=>'<li>'+E(x)+'</li>').join('')+'</ul>').join(''),
datePosted:j.zverejneno,validThrough:d.toISOString().slice(0,10),employmentType:j.uvazek||'FULL_TIME',
hiringOrganization:{'@type':'Organization',name:'Jaroslav Kostera, J.K.FOOD s.r.o.',sameAs:location.origin+'/',logo:location.origin+'/assets/icons/logo-512.png'},
jobLocation:{'@type':'Place',address:{'@type':'PostalAddress',streetAddress:'Větřkovice 243',addressLocality:'Větřkovice',postalCode:'747 43',addressRegion:'Moravskoslezský kraj',addressCountry:'CZ'}},directApply:false};}));}
const cta=document.getElementById('career-cta');if(cta){const box=cta.closest('section');const p=box.querySelector('p');if(p&&d.dalsi)p.innerHTML=nb(d.dalsi);
const a=box.querySelector('a[href^="mailto:"]');if(a&&mail){a.href='mailto:'+mail+'?subject='+encodeURIComponent('Životopis – J.K.FOOD');a.textContent='Napsat na '+mail;}}
}).catch(()=>{});})();"""


def job_ld(j):
    """JobPosting pro vyhledávání práce na Googlu (Google Jobs). Vzorové pozice ([…]) se nepublikují."""
    if "[" in j["nazev"] or not j.get("zverejneno"):
        return None
    desc = "".join(f"<h3>{l}</h3><ul>" + "".join(f"<li>{esc(x)}</li>" for x in j.get(k, [])) + "</ul>"
                   for k, l in [("nabizime", "Nabízíme"), ("pozadujeme", "Požadujeme"), ("naplne", "Náplň práce")] if j.get(k))
    posted = datetime.date.fromisoformat(j["zverejneno"])
    return {"@context": "https://schema.org", "@type": "JobPosting", "title": j["nazev"],
            "description": f"<p>{esc(j['nazev'])} – J.K.FOOD, Větřkovice.</p>{desc}",
            "datePosted": j["zverejneno"], "validThrough": (posted + datetime.timedelta(days=90)).isoformat(),
            "employmentType": j.get("uvazek", "FULL_TIME"),
            "hiringOrganization": {"@type": "Organization", "name": ORG["legal"], "sameAs": f"{SITE}/", "logo": f"{SITE}/assets/icons/logo-512.png"},
            "jobLocation": {"@type": "Place", "address": {"@type": "PostalAddress", "streetAddress": "Větřkovice 243", "addressLocality": "Větřkovice",
                                                          "postalCode": "747 43", "addressRegion": "Moravskoslezský kraj", "addressCountry": "CZ"}},
            "directApply": False}


def build_career(v):
    """Stránka Kariéra (kariera.html) z assets/kariera.json."""
    data = json.loads((ROOT / "assets" / "kariera.json").read_text(encoding="utf-8"))
    mail = data["kontakt_email"]
    why = "".join(f'<li><h3>{esc(w["nadpis"])}</h3><p>{nbsp(esc(w["text"]))}</p></li>' for w in data["proc"])
    jobs = []
    active = [j for j in data["pozice"] if j.get("aktivni", True)]   # skryté pozice se nezobrazují
    for i, j in enumerate(active):
        tags = "".join(f"<span>{esc(t)}</span>" for t in j.get("stitky", []))
        cols = []
        for key, label in [("nabizime", "Nabízíme"), ("pozadujeme", "Požadujeme"), ("naplne", "Náplň práce")]:
            if j.get(key):
                cols.append(f'<div><h4>{label}</h4><ul>' + "".join(f"<li>{esc(x)}</li>" for x in j[key]) + "</ul></div>")
        subj = quote(f"Zájem o pozici: {j['nazev']}")
        actions = [f'<a class="btn btn-red" href="mailto:{esc(j.get("kontakt_email", mail))}?subject={subj}">Mám zájem – poslat životopis</a>']
        if j.get("kontakt_tel"):
            actions.append(f'<a class="btn btn-line" href="{tel_href(j["kontakt_tel"])}">Zavolat {esc(j["kontakt_tel"])}</a>')
        jobs.append(f'<li class="job"><details{" open" if i == 0 else ""}><summary><h3>{esc(j["nazev"])}</h3>'
                    f'<span class="job-tags">{tags}</span><span class="job-toggle" aria-hidden="true"></span></summary>'
                    f'<div class="job-body"><div class="job-cols">{"".join(cols)}</div><div class="job-actions">{"".join(actions)}</div></div></details></li>')
    body = (f'<section class="career-why" aria-labelledby="why-title"><h2 id="why-title" class="sr">Proč pracovat u nás</h2><ul class="why">{why}</ul></section>'
            f'<section class="career-jobs" aria-labelledby="jobs-title"><div class="team-grp-head"><h2 id="jobs-title">Volné pozice</h2>'
            f'<p id="jobsCount">{jobs_count(len(active))}</p></div>'
            f'<ul class="jobs" id="jobs">{"".join(jobs) or JOBS_EMPTY}</ul></section>'
            # inzeráty pro Google Jobs (aktualizuje je i skript níže podle administrace)
            + '<script type="application/ld+json" id="jobsLd">' + json.dumps([x for x in map(job_ld, active) if x], ensure_ascii=False).replace("</", "<\\/") + "</script>"
            # aktuální inzeráty z administrace (api/kariera.php); bez PHP zůstanou ty z HTML
            + f'<script>{CAREER_JS}</script>')
    cta = cta_band("career-cta", "Nenašli jste svou pozici?", nbsp(esc(data["dalsi"])),
                   [("btn-white", f"mailto:{mail}?subject={quote('Životopis – J.K.FOOD')}", f"Napsat na {mail}"),
                    ("btn-ghost", "nas-tym.html", "Poznejte náš tým")])
    desc = "Kariéra v J.K.FOOD ve Větřkovicích: volné pozice ve výrobě, kvalitě a obchodě, praxe a stáže. Rodinná firma s benefity a přátelským kolektivem."
    graph = [{"@type": "WebPage", "@id": f"{SITE}/kariera.html#stranka", "url": f"{SITE}/kariera.html", "name": "Kariéra",
              "description": desc, "inLanguage": "cs", "about": {"@id": f"{SITE}/#firma"}}]
    simple_page("kariera.html", "Kariéra – volné pozice | J.K.FOOD Větřkovice", desc,
                [("Úvod", ""), ("Kariéra", "kariera.html")], "Kariéra", data["intro"], body, cta, graph, nav_current="kariera.html")
    return [("kariera.html", "0.6")]


# ---------------------------------------------------------------- anglická verze (en/)
def html_unescape(s):
    return html.unescape(s)


def build_en():
    """Anglická verze vzniká z hotových českých stránek: překlad (tools/i18n_en.py),
    úprava cest pro složku en/ a nová metadata. Nepřeložené dvojice ohlásí."""
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    import i18n_en as T
    (ROOT / "en").mkdir(exist_ok=True)
    cat_by_slug = {c["file"]: c for c in CATS}
    missing = []

    def tr(html, pairs, label):
        # Kariéra je jen česky: v anglickém menu ji neukazujeme (zůstává v patičce)
        html = re.sub(r'\s*<a class="link" href="kariera\.html"[^>]*>Kariéra</a>', "", html)
        for cz, en in pairs:
            if cz not in html:
                missing.append(f"{label}: {cz[:70]}")
            html = html.replace(cz, en)
        return html

    def names(html):
        for (en, _), c in zip(T.CATS_EN, CATS):
            html = html.replace(f">{esc(c['name'])}<", f">{esc(en)}<")
        for cz, en in T.SUBS_EN.items():
            html = html.replace(f"<h3>{esc(cz)}</h3>", f"<h3>{esc(en)}</h3>").replace(f'data-s="{esc(cz)}"', f'data-s="{esc(en)}"')
        return html

    def paths(html):
        def fix(m):
            attr, u = m.group(1), m.group(2)
            if attr in ("srcset", "imagesrcset"):
                return f'{attr}="' + ", ".join("../" + c.strip() for c in u.split(",")) + '"'
            if re.match(r"(https?:|//|#|mailto:|tel:|data:|/|\.\./|\$\{)", u):
                return m.group(0)
            base, _, frag = u.partition("#")
            if base == "index.html" or base.startswith("index.html?"):
                new = u
            elif base in T.B2B_FILES:
                new = T.B2B_FILES[base] + (f"#{frag}" if frag else "")
            elif base == "nas-tym.html":
                new = "team.html" + (f"#{frag}" if frag else "")
            elif base == "sortiment.html":
                new = "products.html"
            elif base in cat_by_slug:
                new = f"products.html#sk-{cat_by_slug[base]['id']}"
            elif base.startswith("en/"):
                new = base[3:]
            else:
                new = "../" + u
            return f'{attr}="{new}"'
        html = html.replace("url(assets/", "url(../assets/")
        return re.sub(r'\b(href|src|srcset|imagesrcset|action)="([^"]*)"', fix, html)

    def meta(html, title, desc, path_en, path_cs, graph):
        html = re.sub(r"<title>.*?</title>\n?", "", html, flags=re.S)
        html = re.sub(r'<meta name="description"[^>]*>\n?', "", html)
        html = re.sub(r'<link rel="(?:canonical|alternate|icon|apple-touch-icon|manifest)"[^>]*>\n?', "", html)
        html = re.sub(r'<meta (?:property="og:[^"]*"|name="twitter:[^"]*")[^>]*>\n?', "", html)
        html = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', "", html, flags=re.S)
        html = re.sub(r"<!-- META:START -->\s*<!-- META:END -->\n?", "", html)
        head = "\n".join([f"<title>{esc(title)}</title>", f'<meta name="description" content="{esc(desc)}">',
                          head_common(title, desc, f"en/{path_en}", lang="en", alternates={"cs": path_cs, "en": f"en/{path_en}"}),
                          ld({"@context": "https://schema.org", "@graph": graph})])
        return html.replace("</head>", head + "\n</head>", 1)

    def lang_link(html, cz_target):
        return re.sub(r'<a class="link lang" href="[^"]*"[^>]*>EN</a>',
                      f'<a class="link lang" href="../{cz_target}" hreflang="cs" lang="cs" aria-label="CZ – česká verze">CZ</a>', html)

    org = dict(org_ld(), description="A Czech family company from Větřkovice. Since 1996 we have produced spices, seasoning blends, "
               "dried vegetables and dehydrated foods for food manufacturers, canteens and catering.")

    # --- úvodní stránka
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    html = re.sub(r"<!-- FAQ:START -->.*?<!-- FAQ:END -->", lambda m: f"<!-- FAQ:START -->\n{render_faq('en')}\n<!-- FAQ:END -->", html, flags=re.S)
    html = names(tr(html, T.COMMON + T.INDEX, "index"))
    html = re.sub(r"(\d+)&nbsp;výrob(?:ek|ky|ků)", r"\1&nbsp;products", html)
    html = re.sub(r"page: '([\w-]+\.html)'", lambda m: f"page: '{T.B2B_FILES.get(m.group(1), '../' + m.group(1))}'", html)
    html = meta(html, "J.K.FOOD – Czech producer of spices and seasoning blends",
                "Family company from Větřkovice, Czech Republic. Since 1996 we have produced spices, seasoning blends, dried vegetables "
                "and dehydrated foods for food manufacturers and catering.", "", "",
                [org, {"@type": "WebSite", "@id": f"{SITE}/en/#web", "url": f"{SITE}/en/", "name": "J.K.FOOD", "inLanguage": "en",
                       "publisher": {"@id": f"{SITE}/#firma"}}, faq_ld("en")])
    (ROOT / "en" / "index.html").write_text(lang_link(paths(html), ""), encoding="utf-8")

    # --- katalog (jedna stránka se všemi skupinami)
    html = (ROOT / "sortiment.html").read_text(encoding="utf-8")
    html = tr(html, T.COMMON + T.CATALOG, "products")
    html = names(html)
    html = html.replace('<h1 class="h2 cat-title" id="cat-title">Sortiment</h1>', '<h1 class="h2 cat-title" id="cat-title">Products</h1>')
    html = re.sub(r'<p class="intro">Přes 490 výrobků.*?</p>',
                  '<p class="intro">Over 490 products in nine groups. Product names are given in Czech – just send us an enquiry '
                  'and we will reply in English.</p>', html, flags=re.S)
    html = re.sub(r'(<nav class="crumbs"[^>]*>)<a href="index.html">Úvod</a>(.*?)<span aria-current="page">Sortiment</span>',
                  r'\1<a href="index.html">Home</a>\2<span aria-current="page">Products</span>', html)
    html = re.sub(r"(\d+) výrob(?:ek|ky|ků)", lambda m: f"{m.group(1)} product{'s' if m.group(1) != '1' else ''}", html)
    html = html.replace("Celkem ", "").replace('<p class="cat-count" id="count">', '<p class="cat-count" id="count">Total: ')
    html = re.sub(r"const legacy = \{.*?\};", "const legacy = {};", html)
    html = re.sub(r'<a class="chip(?: all)?" href="sortiment.html" aria-current="page">All</a>', '<a class="chip all" href="#obsah" aria-current="page">All</a>', html)
    graph = [org, breadcrumbs_ld([("Home", "en/"), ("Products", "en/products.html")]),
             {"@type": "CollectionPage", "url": f"{SITE}/en/products.html", "name": "Products", "inLanguage": "en",
              "description": "J.K.FOOD product range – spices, seasoning blends, dried vegetables, meat industry blends, stocks, soups and more."}]
    html = meta(html, "Products – spices, seasoning blends and dehydrated foods | J.K.FOOD",
                "Over 490 products from J.K.FOOD, Czech Republic: single spices, seasoning blends, dried vegetables, blends for the "
                "meat industry, dried mushrooms, stocks, soups and potato products.", "products.html", "sortiment.html", graph)
    (ROOT / "en" / "products.html").write_text(lang_link(paths(html), "sortiment.html"), encoding="utf-8")

    # --- tým
    html = (ROOT / "nas-tym.html").read_text(encoding="utf-8")
    html = tr(html, T.COMMON + [
        ('<h1 class="h2 cat-title" id="page-title">Náš tým</h1>', '<h1 class="h2 cat-title" id="page-title">Our team</h1>'),
        ('<a href="index.html">Úvod</a>', '<a href="index.html">Home</a>'),
        ('<span aria-current="page">Náš tým</span>', '<span aria-current="page">Our team</span>'),
        ('aria-label="Drobečková navigace"', 'aria-label="Breadcrumbs"'),
        (">Ozvěte se nám</h2>", ">Get in touch</h2>"),
        ("<p>Rádi s&nbsp;vámi probereme nabídku, vzorky i&nbsp;směs připravenou přesně pro vaši výrobu.</p>",
         "<p>We are happy to discuss an offer, samples or a blend made precisely for your production – in English, too.</p>"),
        (">Napsat poptávku</a>", ">Send an enquiry</a>"),
        (">Chcete k&nbsp;nám? Kariéra</a>", ">Careers (in Czech)</a>"),
    ], "team")
    html = names(html)
    html = re.sub(r'<p class="intro">.*?</p>', f'<p class="intro">{esc(T.TEAM["intro"])}</p>', html, count=1, flags=re.S)
    for cz, en in T.TEAM["groups"].items():
        html = html.replace(f">{esc(cz)}</h2>", f">{esc(en)}</h2>")
    for cz, en in T.TEAM["popis"].items():
        html = html.replace(f"<p>{nbsp(esc(cz))}</p>", f"<p>{esc(en)}</p>")
    for cz, en in sorted(T.TEAM["roles"].items(), key=lambda kv: -len(kv[0])):
        html = html.replace(f'<p class="person-role">{esc(cz)}</p>', f'<p class="person-role">{esc(en)}</p>')
        html = html.replace(f'<p class="person-area">{esc(cz)}</p>', f'<p class="person-area">{esc(en)}</p>')
        html = html.replace(f"<h3>{esc(cz)}</h3>", f"<h3>{esc(en)}</h3>")
    html = meta(html, "Our team | J.K.FOOD, Czech Republic",
                "Meet the people of J.K.FOOD – management, sales representatives, production and development of seasoning blends in Větřkovice.",
                "team.html", "nas-tym.html", [org, breadcrumbs_ld([("Home", "en/"), ("Our team", "en/team.html")])])
    (ROOT / "en" / "team.html").write_text(lang_link(paths(html), "nas-tym.html"), encoding="utf-8")

    # --- stránky pro firmy (Průmysl, obory, Výzkum a vývoj, Hotová jídla): obsah z anglických dat, menu a patička překladem
    items = load_items()
    b2b = [("prumysl.html", lambda: page_prumysl("en")), ("vyzkum-a-vyvoj.html", lambda: page_vyvoj("en")),
           ("hotova-jidla.html", lambda: page_jidla("en"))] + [(o["file"], lambda o=o: page_obor(o, items, "en")) for o in OBORY] \
        + [(f, lambda k=k: page_legal(k, "en")) for k, f in LEGAL_FILES.items()]
    b2b_pages = []
    for cz, render in b2b:
        en = T.B2B_FILES[cz]
        html = render()
        html = tr(html, T.COMMON + [('aria-label="Drobečková navigace"', 'aria-label="Breadcrumbs"')], en)
        html = names(html)
        title = re.search(r"<title>(.*?)</title>", html).group(1)
        desc = re.search(r'<meta name="description" content="([^"]*)"', html).group(1)
        h1 = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S).group(1)
        crumbs = [("Home", "en/")] + ([("Industry", "en/industry.html")] if cz in {o["file"] for o in OBORY} else []) \
            + [(html_unescape(h1), f"en/{en}")]
        graph = [org, breadcrumbs_ld(crumbs), {"@type": "WebPage", "url": f"{SITE}/en/{en}", "name": html_unescape(h1), "inLanguage": "en",
                                               "description": html_unescape(desc), "about": {"@id": f"{SITE}/#firma"}}]
        html = meta(html, html_unescape(title), html_unescape(desc), en, cz, graph)
        (ROOT / "en" / en).write_text(lang_link(paths(html), cz), encoding="utf-8")
        b2b_pages.append((f"en/{en}", "0.6"))

    # --- kontrola: nepřeložené dvojice a zbytky češtiny
    if missing:
        raise SystemExit("Nepřeložené texty (upravte tools/i18n_en.py):\n  " + "\n  ".join(missing))
    allowed = {"CHUŤ", "halušky", "Větřkovice", "Galčanová", "Kostera", "Větřkovic", "Česká verze", "CZ – česká verze", "Má chuť", "pepř, guláš"}
    leftovers = []
    for f in ["index.html", "products.html", "team.html"] + list(T.B2B_FILES.values()):
        h = (ROOT / "en" / f).read_text(encoding="utf-8")
        h = re.sub(r"<script>.*?</script>|<style.*?</style>", " ", h, flags=re.S)
        h = re.sub(r'<ul class="items">.*?</ul>', " ", h, flags=re.S)     # názvy výrobků zůstávají česky
        h = re.sub(r'<script type="application/ld\+json">.*?</script>', " ", h, flags=re.S)
        for t in re.findall(r">([^<>]*[ěščřžůťďňĚŠČŘŽŮŤĎŇ][^<>]*)<|(?:aria-label|placeholder|alt|title)=\"([^\"]*[ěščřžůťďňĚŠČŘŽŮŤĎŇ][^\"]*)\"", h):
            t = (t[0] or t[1]).strip()
            if t and not any(a in t for a in allowed) and not re.fullmatch(r"[\w.@+ -]*kostera\.cz", t):
                leftovers.append(f"{f}: {t[:80]}")
    if leftovers:
        print("⚠ zbytky češtiny v anglické verzi:\n  " + "\n  ".join(sorted(set(leftovers))))
    return [("en/", "0.8"), ("en/products.html", "0.7"), ("en/team.html", "0.5")] + b2b_pages

# ---------------------------------------------------------------- AI vyhledávače
AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User",
           "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended", "Bingbot",
           "DuckAssistBot", "Meta-ExternalAgent", "MistralAI-User", "CCBot"]


def build_ai(items):
    """robots.txt (výslovně povolené AI roboty), llms.txt a llms-full.txt – stručný strojově čitelný
    přehled firmy pro ChatGPT, Claude, Gemini, Perplexity a další (konvence llmstxt.org)."""
    robots = ["# Vyhledávače i AI asistenti mají k veřejnému obsahu webu přístup povolený.", "User-agent: *",
              "Allow: /", "Disallow: /api/", "Disallow: /admin/", "Disallow: /tools/", ""]
    for bot in AI_BOTS:
        robots += [f"User-agent: {bot}", "Allow: /", "Disallow: /api/", "Disallow: /admin/", "Disallow: /tools/", ""]
    robots += [f"Sitemap: {SITE}/sitemap.xml", ""]
    (ROOT / "robots.txt").write_text("\n".join(robots), encoding="utf-8")

    faq = faq_data("cs")["polozky"]
    team = json.loads((ROOT / "assets" / "tym.json").read_text(encoding="utf-8"))
    people = [p for g in team["skupiny"] for p in g["lide"] if not p["jmeno"].startswith("[")]
    groups = "\n".join(f"- [{c['name']}]({SITE}/{c['file']}): {c['desc']} ({sum(1 for x in items if x['g'] == i)} výrobků)"
                       for i, c in enumerate(CATS))
    head = f"""# J.K.FOOD – Jaroslav Kostera, J.K.FOOD s.r.o.

> Česká rodinná firma z Větřkovic (okres Opava, Moravskoslezský kraj). Od roku 1996 vyrábí koření,
> kořenicí směsi, sušenou zeleninu a dehydratované potraviny podle vlastních receptur – pro potravinářský
> průmysl (zejména masnou výrobu), školní a nemocniční jídelny, restaurace a domácnosti.

## Fakta o firmě
- Obchodní název: Jaroslav Kostera, J.K.FOOD s.r.o.; značka J.K.FOOD
- Sídlo a výroba: Větřkovice 243, 747 43 Větřkovice, Česká republika
- IČ 27780384, DIČ CZ27780384; zapsaná v obchodním rejstříku u Krajského soudu v Ostravě, sp. zn. C 51605
- Založení: 1996 (Jaroslav Kostera), společnost s.r.o. od roku 2001
- Zaměstnanci: více než 100
- Výrobní kapacita: přes 30 000 t ročně
- Certifikace: ISO, IFS
- Sortiment: přes {len(items)} výrobků v {len(CATS)} skupinách
- Služby: vývoj kořenicích směsí na míru, navážení směsí na výrobní dávku, technologické postupy ke kombi směsím,
  dodávky vlastní dopravou (obvykle do 5 pracovních dnů), osobní odběr, obchodní zástupci ve všech krajích ČR
- Kontakt: +420 556 310 205, kostera@kostera.cz
""" + "".join(f"- {p['jmeno']} ({p['pozice']}): {p.get('telefon', '')}, {p.get('email', '')}\n" for p in people) + f"""- E-shop pro domácnosti: https://eshop.kostera.cz/
- Jazyky: čeština, angličtina

## Hlavní stránky
- [Úvod]({SITE}/): vyvíjíme, vyrábíme, dodáváme – průmysl, vývoj na míru, vlastní produkty, kontakt
- [Sortiment]({SITE}/sortiment.html): kompletní seznam výrobků s možností poptávky
- [Náš tým]({SITE}/nas-tym.html): vedení firmy, obchod, výroba
- [Kariéra]({SITE}/kariera.html): volné pozice
- [Průmysl]({SITE}/prumysl.html): suroviny a směsi pro potravinářské výrobce, obory, postup spolupráce
""" + "".join(f"- [{o['nav']}]({SITE}/{o['file']}): {o['tag']}\n" for o in OBORY) + f"""- [Výzkum a vývoj]({SITE}/vyzkum-a-vyvoj.html): vývoj receptur na míru, vzorky k testování
- [Hotová jídla CHUŤ a HOT&GO]({SITE}/hotova-jidla.html): hotová jídla v kelímku vlastních značek
- [English version]({SITE}/en/): company overview and product range in English

## Skupiny sortimentu
{groups}

## Časté dotazy
""" + "".join(f"- **{q}** {a}\n" for q, a in faq) + f"""
## Optional
- [Úplný seznam výrobků]({SITE}/llms-full.txt)
"""
    (ROOT / "llms.txt").write_text(head, encoding="utf-8")
    full = [head.replace("## Optional\n- [Úplný seznam výrobků](" + SITE + "/llms-full.txt)\n", ""), "## Úplný seznam výrobků\n"]
    for i, c in enumerate(CATS):
        full.append(f"\n### {c['name']}\n")
        for sub in dict.fromkeys(x["s"] for x in items if x["g"] == i):
            names = [x["n"] for x in items if x["g"] == i and x["s"] == sub]
            full.append((f"- {sub}: " if sub != c["name"] else "- ") + ", ".join(names) + "\n")
    full.append("\nNázvy výrobků jsou obchodní názvy v češtině. Poptávka: kostera@kostera.cz, +420 556 310 205.\n")
    (ROOT / "llms-full.txt").write_text("".join(full), encoding="utf-8")


def build_sitemap(pages):
    urls = [("", "1.0")] + pages
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    import i18n_en as T
    pairs = {"": "en/", "sortiment.html": "en/products.html", "nas-tym.html": "en/team.html", **{cz: f"en/{en}" for cz, en in T.B2B_FILES.items()}}
    pairs.update({v: k for k, v in list(pairs.items())})
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for path, prio in urls:
        alt = ""
        if path in pairs:
            cs, en = (path, pairs[path]) if not path.startswith("en/") else (pairs[path], path)
            alt = (f'<xhtml:link rel="alternate" hreflang="cs" href="{SITE}/{cs}"/>'
                   f'<xhtml:link rel="alternate" hreflang="en" href="{SITE}/{en}"/>')
        xml.append(f"  <url><loc>{SITE}/{path}</loc><lastmod>{TODAY}</lastmod><priority>{prio}</priority>{alt}</url>")
    xml.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(xml) + "\n", encoding="utf-8")



# ---------- VERZE 2 (B2B) ----------
# Texty vycházejí z podkladů zákazníka (Texty_na_WEB.docx) a dosavadního obsahu webu.

STEPS5 = [("Analýza potřeb", "Probereme váš výrobek, technologii, požadovanou chuť i&nbsp;cenu."),
          ("Návrh řešení", "Navrhneme suroviny nebo směs a&nbsp;připravíme vzorky."),
          ("Testování a ladění", "Vzorky vyzkoušíte ve své výrobě, podle výsledků je doladíme."),
          ("Výrobní standard", "Recepturu zafixujeme, aby každá šarže byla stejná."),
          ("Dodávky a podpora", "Pravidelné dodávky vlastní dopravou a&nbsp;technická podpora.")]

WHY = [("Zkušenosti napříč obory", "Od roku 1996 dodáváme masné výrobě, pekárnám, mlékárnám, výrobcům snacků i&nbsp;velkým kuchyním."),
       ("Rozumíme výrobě", "Víme, jak se suroviny chovají při dávkování, zpracování i&nbsp;skladování."),
       ("Kvalita a opakovatelnost", "Stejná chuť, barva a&nbsp;sypkost v&nbsp;každé šarži."),
       ("Flexibilní přístup", "Receptura, balení i&nbsp;dodávky podle vašich potřeb.")]

OBORY = [
    dict(file="masny-prumysl.html", name="Masný průmysl", nav="Řeznictví a masný průmysl",
         title="Kořenicí a kombi směsi pro masný průmysl | J.K.FOOD",
         desc="Kořenicí a technologické směsi pro řeznictví a masnou výrobu: uzeniny, salámy, párky, šunky. Stabilní chuť a barva, přesné dávkování, navážení na výrobní dávku.",
         h1="Řeznictví a masný průmysl", tag="Chuť, barva a konzistence pod kontrolou",
         intro="Pro řeznické a masné provozy dodáváme kořenicí a technologické směsi přizpůsobené specifickým požadavkům masné výroby.",
         focus=["stabilitu chuti a barvy", "kompatibilitu s výrobními technologiemi", "jednoduché a přesné dávkování"],
         offer=[("Směsi podle vaší receptury", "Vyvineme směs na míru, nebo převezmeme vaši recepturu a vyrábíme ji ve stálé kvalitě."),
                ("Navážení na výrobní dávku", "Koření, škroby i technologické přípravky namícháme přímo na vaši kutrovací dávku. Odpadá vážení a pracoviště se nepráší."),
                ("Technologické postupy", "Ke kombi směsím dodáváme technologické postupy a pomůžeme při zavádění nového výrobku."),
                ("Balení a značení šarží", "Balení podle vaší spotřeby, na každém balení šarže, na přání EAN kód.")],
         cats=["maso", "smesi", "koreni", "skroby"]),
    dict(file="pekarstvi.html", name="Pekařství", nav="Pekařství",
         title="Koření a směsi pro pekárny | J.K.FOOD",
         desc="Koření, semínka, kořenicí směsi a sušená zelenina pro pekařskou výrobu. Rovnoměrné rozložení chuti, stabilní receptury, jednoduchá aplikace.",
         h1="Pekařství", tag="Funkční suroviny pro pekařskou výrobu",
         intro="Pekařským provozům nabízíme suroviny a směsi, které podporují rovnoměrné rozložení chuti, stabilní strukturu a jednoduchou aplikaci ve výrobě.",
         focus=["zjednodušení práce s ochucujícími složkami", "stabilitu receptur", "opakovatelnost výsledků ve výrobě"],
         offer=[("Koření a semínka do pečiva", "Kmín, koriandr, fenykl a další koření celé i mleté."),
                ("Sušená zelenina", "Cibule, česnek, paprika a další zelenina v plátcích, kostkách i granulích."),
                ("Směsi na míru", "Připravíme směs pro váš výrobek – od slaného pečiva po plněné výrobky."),
                ("Balení podle objemu výroby", "Velikost balení přizpůsobíme vaší spotřebě.")],
         cats=["koreni", "zelenina", "smesi", "skroby"]),
    dict(file="mlekarny.html", name="Mlékárny", nav="Mlékárenský průmysl",
         title="Suroviny a směsi pro mlékárny | J.K.FOOD",
         desc="Koření, kořenicí směsi a sušená zelenina pro mléčné výrobky – pomazánky, sýry, dresinky. Jemná chuť, stabilita při zpracování, kontrola složení.",
         h1="Mlékárenský průmysl", tag="Stabilní chuť a funkčnost v mléčných výrobcích",
         intro="Pro mlékárenské provozy dodáváme suroviny a směsi pro aplikace, kde je důležitá jemnost chuti, stabilita při zpracování a kontrola složení.",
         focus=["respektují technologické požadavky mlékárenské výroby", "fungují při různých teplotních režimech", "podporují konzistentní senzorický výsledek"],
         focus_lead="Řešení jsou navržena tak, aby:",
         offer=[], cats=["zelenina", "koreni", "smesi"]),
    dict(file="snacky-a-pochutiny.html", name="Snacky a pochutiny", nav="Snacky a pochutiny",
         title="Ochucovací směsi pro snacky a pochutiny | J.K.FOOD",
         desc="Kořenicí a ochucovací směsi pro výrobce snacků a pochutin: rychlá aplikace, rovnoměrné ochucení, stabilní chuťový profil mezi šaržemi.",
         h1="Snacky a pochutiny", tag="Intenzivní chuť a efektivní aplikace",
         intro="Pro výrobce snacků a pochutin nabízíme směsi určené pro rychlou aplikaci a rovnoměrné ochucení.",
         focus=["efektivitu výroby", "stabilní chuťový profil", "minimální rozdíly mezi šaržemi"],
         focus_lead="Řešení navrhujeme s ohledem na:",
         offer=[], cats=["smesi", "koreni", "zelenina"]),
    dict(file="gastro-a-jidelny.html", name="Gastro a jídelny", nav="Gastro a jídelny",
         title="Koření, bujóny a polévky pro jídelny a gastro | J.K.FOOD",
         desc="Bujóny, polévky, omáčky, kořenicí směsi a sušená zelenina v gastro baleních pro školní a nemocniční jídelny, restaurace, hotely a catering.",
         h1="Gastro a jídelny", tag="Spolehlivý dodavatel pro velké kuchyně",
         intro="Bujóny, polévky, omáčky, koření a sušená zelenina v gastro baleních pro školní, nemocniční a sociální stravování, restaurace, hotely i catering.",
         focus=[],
         offer=[("Gastro balení", "Velká balení koření, směsí i polotovarů, se kterými se ve velké kuchyni dobře pracuje."),
                ("Pravidelné dodávky", "Zboží dovezeme vlastní dopravou obvykle do 5 pracovních dnů."),
                ("Obchodní zástupce ve vašem kraji", "Osobní kontakt, poradenství se sortimentem a pomoc s objednávkami."),
                ("Hotové směsi i suroviny", "Směsi na maso, ryby a zeleninu, bramborové výrobky, těstoviny i sušené houby.")],
         cats=["polevky", "smesi", "koreni", "zelenina", "brambory", "testoviny"]),
    dict(file="privatni-znacka.html", name="Private label a OEM", nav="Private label a OEM",
         title="Private label a OEM – koření a směsi pod vaší značkou | J.K.FOOD",
         desc="Private label a OEM spolupráce: vývoj receptur, optimalizace pro výrobu, standardizace a dlouhodobé dodávky koření a směsí pod značkou partnera.",
         h1="Private label a OEM", tag="Vývoj a výroba na míru",
         intro="Průmyslovým a obchodním partnerům nabízíme private label a OEM spolupráci. Zajišťujeme vývoj receptur, jejich optimalizaci pro výrobu a dlouhodobé dodávky.",
         focus=["technické konzultace", "vývoj a úpravy složení", "standardizaci výroby", "logistickou podporu"],
         focus_lead="Spolupráce zahrnuje:",
         offer=[], cats=["koreni", "smesi", "zelenina", "houby"]),
]

V2_EX = {
    "testoviny": "vřetena, kolínka, široké a řezané nudle",
    "koreni": "pepř, paprika, kmín, majoránka – celé, drcené, mleté",
    "smesi": "gulášové, grilovací, na kuře, gyros, svíčkovou",
    "zelenina": "cibule, česnek, mrkev, celer – plátky, kostky, pudr",
    "maso": "kombi směsi, lakovací nástřiky, technologické přísady",
    "houby": "hřib, liška, shiitake, ořechy a sušené ovoce",
    "polevky": "bujóny, polévky, omáčky a marinády pro velké kuchyně",
    "brambory": "kaše, knedlíky, halušky, bramborák",
    "skroby": "škroby, česnekové pasty, paprikové výtažky",
}


def count_word(n, lang="cs"):
    if lang == "en":
        return "product" if n == 1 else "products"
    return "výrobek" if n == 1 else "výrobky" if 2 <= n <= 4 else "výrobků"


def cat_row(href, count, name, ex):
    return (f'<li><a href="{href}"><span class="vs-n">{count}</span><span class="vs-nm">{esc(name)}</span>'
            f'<span class="vs-ex">{nbsp(esc(ex))}</span><span class="vs-go" aria-hidden="true"></span></a></li>')


def _en():
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    import i18n_en
    return i18n_en


def cat_rows(items, ids, lang="cs"):
    by_id = {c["id"]: (i, c) for i, c in enumerate(CATS)}
    ex = _en().V2_EX_EN if lang == "en" else V2_EX
    rows = []
    for cid in ids:
        i, c = by_id[cid]
        n = sum(1 for p in items if p["g"] == i)
        rows.append(cat_row(c["file"], f"{n}&nbsp;{count_word(n, lang)}", c["name"], ex[cid]))
    return rows


def cards(items, cls=""):
    return (f'<ol class="coop-list b2b-cards {cls}">' + "".join(
        f'<li><span class="coop-n" aria-hidden="true">{i + 1}</span><h3>{t}</h3><p>{x}</p></li>'
        for i, (t, x) in enumerate(items)) + "</ol>")


UI_CS = {
    "home": "Úvod", "industry": "Průmysl",
    "focus_sr": "Na co klademe důraz", "focus_lead": "Důraz klademe na:",
    "offer": "Co pro vás uděláme", "cats": "Typický sortiment", "all": "Celý sortiment",
    "steps": "Jak spolupráce probíhá", "others": "Další obory",
    "cta_title": "Pošleme vám vzorky", "cta_text": "Napište nám, co vyrábíte a co hledáte – připravíme vzorky i nabídku.",
    "cta_enquire": "Poptat spolupráci", "cta_samples": "Objednat vzorky",
    "why": "Proč spolupracovat s&nbsp;J.K.FOOD", "count": "výrobků",
}


def ui(lang):
    return _en().B2B_UI if lang == "en" else UI_CS


def steps5_html(lang="cs"):
    L = ui(lang)
    steps = _en().STEPS5_EN if lang == "en" else STEPS5
    return (f'<section class="obor-sec" aria-labelledby="ob-steps"><h2 class="obor-h" id="ob-steps">{L["steps"]}</h2>'
            + cards(steps, "five") + "</section>")


def why_html(lang="cs", hid="ob-why"):
    L = ui(lang)
    why = _en().WHY_EN if lang == "en" else WHY
    return (f'<section class="obor-sec" aria-labelledby="{hid}"><h2 class="obor-h" id="{hid}">{L["why"]}</h2>'
            + '<ul class="b2b-why">' + "".join(f"<li><h3>{t}</h3><p>{x}</p></li>" for t, x in why) + "</ul></section>")


def bullets(lead, pts):
    return (f'<div class="b2b-focus"><p>{lead}</p><ul>' + "".join(f"<li>{nbsp(esc(x))}</li>" for x in pts) + "</ul></div>")


def form_link(obor, typ=None):
    q = "index.html?obor=" + obor.replace(" ", "%20").replace("&", "%26")
    return q + (f"&amp;typ={typ.replace(' ', '%20')}" if typ else "") + "#kontakt"


def b2b_page(file, title, desc, crumbs, h1, intro, body, cta, lang="cs"):
    """Stránka pro firmy. Česky se rovnou zapíše, anglicky vrátí HTML (dokončí ho build_en)."""
    en_file = _en().B2B_FILES[file]
    url = f"{SITE}/{file}" if lang == "cs" else f"{SITE}/en/{en_file}"
    graph = [{"@type": "WebPage", "@id": f"{url}#stranka", "url": url, "name": h1,
              "description": desc, "inLanguage": lang, "about": {"@id": f"{SITE}/#firma"}}]
    nav = {"prumysl.html": "prumysl.html", "vyzkum-a-vyvoj.html": "vyzkum-a-vyvoj.html"}.get(file)
    if file in {o["file"] for o in OBORY}:
        nav = "prumysl.html"
    return simple_page(file, title, desc, crumbs, h1, intro, body, cta, graph, nav_current=nav, en_file=en_file, write=lang == "cs")


def photo(src, alt, cls="b2b-photo"):
    return (f'<figure class="{cls}"><picture><source srcset="img/{src}-600.webp 600w, img/{src}-800.webp 800w, img/{src}-1000.webp 1000w" sizes="(max-width:900px) 92vw, 560px" type="image/webp">'
            f'<img src="img/{src}.jpg" alt="{alt}" width="1000" height="800" fetchpriority="high" decoding="async"></picture></figure>')

SPECULATION = ('<script type="speculationrules">{"prerender":[{"where":{"and":[{"href_matches":"/*"},'
               '{"not":{"href_matches":"/api/*"}},{"not":{"selector_matches":"[target=_blank], [href^=\'tel:\'], [href^=\'mailto:\']"}}]},'
               '"eagerness":"moderate"}]}</script>')
AVIF_SRC = ["img/uvod-m-600", "img/uvod-900", "img/uvod-1536", "img/hero-2-700", "img/hero-2-900"] + [
    f"img/{n}-{w}" for n in ("pilir-prumysl", "pilir-vyvoj", "pilir-produkty") for w in (600, 800, 1000)]


def make_avif():
    """AVIF verze fotek (vytvoří se z WebP, jen když chybí nebo je WebP novější)."""
    from PIL import Image
    for f in AVIF_SRC:
        src, dst = ROOT / f"{f}.webp", ROOT / f"{f}.avif"
        if src.exists() and (not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime):
            Image.open(src).convert("RGB").save(dst, quality=45, speed=4)


def obor_text(o, lang):
    """Údaje oboru v daném jazyce (soubor, sortiment a štítek pro odkazy zůstávají společné)."""
    return o if lang == "cs" else {**o, **_en().OBORY_EN[o["file"]]}


def page_obor(o, items, lang="cs"):
    L, t = ui(lang), obor_text(o, lang)
    parts = []
    head = f'<p class="b2b-tag">{esc(t["tag"])}</p>'
    if t["focus"]:
        parts.append(f'<section class="obor-sec" aria-labelledby="ob-focus">{head}<h2 class="sr" id="ob-focus">{L["focus_sr"]}</h2>'
                     + bullets(t.get("focus_lead", L["focus_lead"]), t["focus"]) + "</section>")
    else:
        parts.append(f'<div class="obor-sec">{head}</div>')
    if t["offer"]:
        parts.append(f'<section class="obor-sec" aria-labelledby="ob-offer"><h2 class="obor-h" id="ob-offer">{L["offer"]}</h2>'
                     + cards([(esc(a), nbsp(esc(b))) for a, b in t["offer"]]) + "</section>")
    parts.append(f'<section class="obor-sec" aria-labelledby="ob-cats"><div class="obor-cats-head"><h2 class="obor-h" id="ob-cats">{L["cats"]}</h2>'
                 f'<a class="rail-mini" href="sortiment.html">{L["all"]} <span class="i-next" aria-hidden="true"></span></a></div>'
                 f'<ul class="vsort-list">{"".join(cat_rows(items, o["cats"], lang))}</ul></section>')
    parts.append(steps5_html(lang))
    others = "".join(f'<li><a href="{x["file"]}">{esc(obor_text(x, lang)["nav"])}</a></li>' for x in OBORY if x is not o)
    parts.append(f'<nav class="obor-sec b2b-others" aria-label="{L["others"]}"><h2 class="obor-h">{L["others"]}</h2><ul>{others}</ul></nav>')
    cta = cta_band("obor-cta", L["cta_title"], L["cta_text"],
                   [("btn-white", form_link(t["name"]), L["cta_enquire"]), ("btn-ghost", form_link(t["name"], "Vzorky"), L["cta_samples"])])
    return b2b_page(o["file"], t["title"], t["desc"], [(L["home"], ""), (L["industry"], "prumysl.html"), (t["nav"], o["file"])],
                   t["h1"], t["intro"], "".join(parts), cta, lang)


PRUMYSL_CS = dict(
    title="Průmysl – suroviny a směsi pro potravinářské výrobce | J.K.FOOD",
    desc="Dehydratované suroviny, kořenicí a technologické směsi pro potravinářský průmysl: masná výroba, pekařství, mlékárny, snacky, private label a OEM.",
    h1="Řešení pro potravinářské výrobce a zpracovatele",
    intro="Dodáváme suroviny a směsi pro potravinářský průmysl, kde je klíčová stálá kvalita, opakovatelnost chuti a funkčnost ve výrobním procesu. Spolupracujeme s výrobci napříč obory potravinářství.",
    tag="Spolehlivý partner pro průmyslové aplikace", h2="Dehydratované suroviny a&nbsp;technologické směsi",
    p="Pro průmyslové provozy dodáváme dehydratované suroviny, kořenicí a&nbsp;technologické směsi, které umožňují přesné dávkování, stabilní chuť a&nbsp;snadné zapojení do výrobních linek. Každé řešení přizpůsobujeme konkrétní technologii, výrobnímu procesu a&nbsp;požadovanému výsledku.",
    lead="Naše řešení pomáhají:", pts=["snížit závislost na sezónních surovinách", "zjednodušit výrobní procesy", "zajistit stejnou kvalitu napříč šaržemi"],
    alt="Pracovnice obsluhuje průmyslový míchací stroj s kořenicí směsí", sectors="Obory, kterým dodáváme",
    cta_title="Kontakt pro průmyslové partnery",
    cta_text="Máte konkrétní požadavky nebo hledáte spolehlivého dodavatele pro výrobu? Rádi s&nbsp;vámi projdeme možnosti spolupráce.",
    obor="Průmysl")


def page_prumysl(lang="cs"):
    L = ui(lang)
    T = _en().PRUMYSL_EN if lang == "en" else PRUMYSL_CS
    tiles = "".join(f'<li><a href="{o["file"]}"><span class="vs-nm">{esc(obor_text(o, lang)["nav"])}</span><span class="vs-ex">{esc(obor_text(o, lang)["tag"])}</span>'
                    '<span class="vs-go" aria-hidden="true"></span></a></li>' for o in OBORY)
    body = (f'<section class="obor-sec b2b-split" aria-labelledby="pr-dehy"><div><p class="b2b-tag">{T["tag"]}</p>'
            f'<h2 class="obor-h" id="pr-dehy">{T["h2"]}</h2><p class="b2b-p">{T["p"]}</p>'
            + bullets(T["lead"], T["pts"]) + "</div>" + photo("pilir-prumysl", T["alt"]) + "</section>"
            f'<section class="obor-sec" aria-labelledby="pr-obory"><h2 class="obor-h" id="pr-obory">{T["sectors"]}</h2>'
            f'<ul class="vsort-list b2b-obory">{tiles}</ul></section>'
            + why_html(lang) + steps5_html(lang))
    cta = cta_band("pr-cta", T["cta_title"], T["cta_text"],
                   [("btn-white", form_link(T["obor"]), L["cta_enquire"]), ("btn-ghost", "tel:+420556310205", "+420 556 310 205")])
    return b2b_page("prumysl.html", T["title"], T["desc"], [(L["home"], ""), (L["industry"], "prumysl.html")], T["h1"], T["intro"], body, cta, lang)


VYVOJ_CS = dict(
    title="Výzkum a vývoj kořenicích směsí na míru | J.K.FOOD",
    desc="Vlastní vývojové zázemí: receptury na míru, úpravy chuti a složení, stabilita šarží a zavedení do sériové výroby. Vzorky k testování.",
    h1="Výzkum a vývoj",
    intro="Vývoj je přirozenou součástí J.K.FOOD. Ve vlastním vývojovém zázemí vyvíjíme a testujeme receptury tak, aby splňovaly nároky na chuť, funkčnost i dlouhodobou stabilitu.",
    tag="Stálá kvalita začíná u vývoje", h2="Co ve vývoji řešíme",
    p="Každý výrobek vyvíjíme s&nbsp;ohledem na jeho skutečné použití – ve výrobě, gastronomii i&nbsp;retailu. Sledujeme technologické chování, senzoriku i&nbsp;opakovatelnost výsledku. Nevyvíjíme do šuplíku, ale pro výrobu.",
    lead="Zaměřujeme se zejména na:", pts=["chuť, vůni a stálost barvy", "homogenitu směsí a stabilitu šarží", "dávkování, sypkost a mísitelnost", "chování výrobku při zpracování a skladování"],
    alt="Laboratoř: vzorek kořenicí směsi na laboratorní váze, zkumavky se vzorky koření",
    h2b="Vývoj na míru a&nbsp;spolupráce",
    pb="Spolupracujeme s&nbsp;výrobci, gastronomií i&nbsp;partnery pro private label. Připravujeme nové výrobky a&nbsp;upravujeme stávající receptury podle konkrétního zadání, technologie a&nbsp;požadované ceny.",
    cards=[("Vývoj směsí na míru", "Nová chuť podle vašeho zadání a&nbsp;technologie."),
           ("Úpravy chuti a&nbsp;složení", "Doladíme stávající recepturu – chuť, složení i&nbsp;cenu."),
           ("Stálá kvalita při růstu", "Recepturu připravíme tak, aby fungovala i&nbsp;při vyšších objemech."),
           ("Zavedení do sériové výroby", "Pomůžeme s&nbsp;přechodem ze vzorku na pravidelnou výrobu.")],
    quote="Nejsme jen dodavatel surovin. Jsme partner, který rozumí surovinám, technologii i&nbsp;provozu.",
    cta_title="Máte konkrétní zadání?", cta_text="Rádi s&nbsp;vámi probereme váš projekt a&nbsp;připravíme vzorky k&nbsp;testování.",
    cta_btn="Poptat vývoj", obor="Vývoj na míru")


def page_vyvoj(lang="cs"):
    L = ui(lang)
    T = _en().VYVOJ_EN if lang == "en" else VYVOJ_CS
    body = (f'<section class="obor-sec b2b-split" aria-labelledby="rd-co"><div><p class="b2b-tag">{T["tag"]}</p>'
            f'<h2 class="obor-h" id="rd-co">{T["h2"]}</h2><p class="b2b-p">{T["p"]}</p>'
            + bullets(T["lead"], T["pts"]) + "</div>" + photo("pilir-vyvoj", T["alt"]) + "</section>"
            f'<section class="obor-sec" aria-labelledby="rd-help"><h2 class="obor-h" id="rd-help">{T["h2b"]}</h2><p class="b2b-p">{T["pb"]}</p>'
            + cards(T["cards"]) + f'<blockquote class="b2b-quote">{T["quote"]}</blockquote></section>'
            + steps5_html(lang))
    cta = cta_band("rd-cta", T["cta_title"], T["cta_text"],
                   [("btn-white", form_link(T["obor"], "Vývoj směsi na míru"), T["cta_btn"]), ("btn-ghost", "tel:+420556310205", "+420 556 310 205")])
    return b2b_page("vyzkum-a-vyvoj.html", T["title"], T["desc"], [(L["home"], ""), (T["h1"], "vyzkum-a-vyvoj.html")], T["h1"], T["intro"], body, cta, lang)


JIDLA_CS = dict(
    title="Hotová jídla v kelímku CHUŤ a HOT&GO | J.K.FOOD",
    desc="Hotová jídla v kelímku značek CHUŤ a HOT&GO: stačí zalít horkou vodou. Pro obchody, kanceláře, pracovní provozy i cestování.",
    h1="Hotová jídla v kelímku CHUŤ a HOT&GO",
    intro="Vlastní řada hotových jídel pro rychlou a jednoduchou přípravu. Jistota chuti, pohodlí a stejný výsledek bez ohledu na místo nebo situaci.",
    tag="Spolehlivé řešení, když je čas rozhodující", h2="Kompletní jídlo za pár minut",
    p="Řada hotových jídel v&nbsp;kelímku značek CHUŤ a&nbsp;HOT&amp;GO je určená pro rychlou a&nbsp;jednoduchou přípravu. Stačí zalít horkou vodou a&nbsp;za několik minut je jídlo připravené k&nbsp;podávání – doma, v&nbsp;práci i&nbsp;na cestách.",
    lead="Každý kelímek:", pts=["je kompletní hotové jídlo", "má jasný a jednoduchý způsob přípravy", "dává pokaždé stejný chuťový výsledek", "nepotřebuje další suroviny ani vybavení"],
    ph_hero="Fotka řady CHUŤ a HOT&amp;GO", ph_hero_label="Místo pro fotografii hotových jídel CHUŤ a HOT&amp;GO",
    ph_item="Foto kelímku", ph_item_sub="název · gramáž · příprava", h_types="Druhy a balení",
    h_b2b="Pro obchodní partnery",
    pb="Hotová jídla v&nbsp;kelímku se snadno skladují, přenášejí i&nbsp;prodávají. Hodí se tam, kde zákazníci potřebují rychlé a&nbsp;spolehlivé jídlo – v&nbsp;kancelářích a&nbsp;pracovních provozech, pro studenty i&nbsp;na cestách.",
    cards=[("Rychlá příprava", "Bez vaření – stačí horká voda."), ("Žádné nádobí navíc", "Jídlo se připraví i&nbsp;podává přímo v&nbsp;kelímku."),
           ("Snadné skladování", "Kelímky se dobře skladují, přenášejí i&nbsp;vystavují."), ("Porce jako hotové jídlo", "Každý kelímek je plnohodnotná porce.")],
    cta_title="Hotová jídla do vašeho sortimentu", cta_text="Máte zájem o&nbsp;hotová jídla CHUŤ a&nbsp;HOT&amp;GO pro svůj obchod nebo provoz? Napište nám.",
    cta_btn="Poptat hotová jídla", obor="Hotová jídla CHUŤ a HOT&GO")


def page_jidla(lang="cs"):
    L = ui(lang)
    T = _en().JIDLA_EN if lang == "en" else JIDLA_CS
    ph = "".join(f'<li class="b2b-ph"><span class="b2b-ph-ic" aria-hidden="true"></span><b>{T["ph_item"]}</b><span>{T["ph_item_sub"]}</span></li>' for _ in range(4))
    body = (f'<section class="obor-sec b2b-split" aria-labelledby="hj-co"><div><p class="b2b-tag">{T["tag"]}</p>'
            f'<h2 class="obor-h" id="hj-co">{T["h2"]}</h2><p class="b2b-p">{T["p"]}</p>'
            + bullets(T["lead"], T["pts"])
            + f'</div><div class="b2b-ph-hero" role="img" aria-label="{T["ph_hero_label"]}"><span class="b2b-ph-ic" aria-hidden="true"></span><b>{T["ph_hero"]}</b></div></section>'
            f'<section class="obor-sec" aria-labelledby="hj-druhy"><h2 class="obor-h" id="hj-druhy">{T["h_types"]}</h2>'
            f'<ul class="b2b-ph-grid">{ph}</ul></section>'
            f'<section class="obor-sec" aria-labelledby="hj-b2b"><h2 class="obor-h" id="hj-b2b">{T["h_b2b"]}</h2><p class="b2b-p">{T["pb"]}</p>'
            + cards(T["cards"]) + "</section>")
    cta = cta_band("hj-cta", T["cta_title"], T["cta_text"],
                   [("btn-white", form_link(T["obor"]), T["cta_btn"]), ("btn-ghost", form_link(T["obor"], "Vzorky"), L["cta_samples"])])
    return b2b_page("hotova-jidla.html", T["title"], T["desc"], [(L["home"], ""), (T["h1"], "hotova-jidla.html")], T["h1"], T["intro"], body, cta, lang)



# ---------------------------------------------------------------- ochrana osobních údajů a cookies
FILL = '<mark class="fill">[doplnit: {}]</mark>'


def legal_texts(lang):
    """Texty stránek Ochrana osobních údajů a Cookies. Místa [doplnit] musí firma doplnit/ověřit."""
    if lang == "en":
        return _en().LEGAL_EN
    f = FILL.format
    ctrl = ("Jaroslav Kostera, J.K.FOOD s.r.o., Větřkovice 243, 747 43 Větřkovice, IČ 27780384, "
            "zapsaná v obchodním rejstříku u Krajského soudu v Ostravě, sp. zn. C 51605")
    return {
        "privacy": dict(
            title="Ochrana osobních údajů | J.K.FOOD",
            desc="Jak J.K.FOOD zpracovává osobní údaje z poptávkového formuláře, e-mailu a životopisů a jaká máte práva.",
            h1="Ochrana osobních údajů",
            intro="Jak na webu kostera.cz zpracováváme vaše osobní údaje a jaká máte práva.",
            body=[
                ("Správce osobních údajů", f"<p>{ctrl}.</p><p>Kontakt ve věcech osobních údajů: "
                 '<a href="mailto:kostera@kostera.cz">kostera@kostera.cz</a>, <a href="tel:+420556310205">+420 556 310 205</a>.</p>'),
                ("Jaké údaje zpracováváme a proč",
                 "<h3>Poptávkový formulář a přímý kontakt</h3>"
                 "<p>Jméno a příjmení, název firmy, e-mail, telefon, text zprávy, případně výrobek nebo obor, o který máte zájem.</p>"
                 "<ul><li><b>Účel:</b> vyřízení poptávky, příprava nabídky a navazující komunikace.</li>"
                 "<li><b>Právní základ:</b> jednání o smlouvě na vaši žádost (čl. 6 odst. 1 písm. b) GDPR) a oprávněný zájem "
                 "odpovědět na váš dotaz (čl. 6 odst. 1 písm. f) GDPR).</li></ul>"
                 "<h3>Životopisy a zájem o práci</h3>"
                 "<p>Údaje, které nám pošlete v životopisu nebo e-mailu.</p>"
                 "<ul><li><b>Účel:</b> výběrové řízení na volnou pozici.</li>"
                 "<li><b>Právní základ:</b> jednání o pracovní smlouvě (čl. 6 odst. 1 písm. b) GDPR); delší uchování jen s vaším souhlasem.</li></ul>"
                 "<h3>Technické údaje</h3>"
                 "<p>Při návštěvě webu server zaznamenává technické údaje (IP adresa, čas, zobrazená stránka, typ prohlížeče). "
                 "Pro ochranu formuláře proti zneužití dočasně (10&nbsp;minut) uchováváme otisk IP adresy.</p>"
                 "<ul><li><b>Účel:</b> provoz a bezpečnost webu.</li><li><b>Právní základ:</b> oprávněný zájem (čl. 6 odst. 1 písm. f) GDPR).</li></ul>"),
                ("Jak dlouho údaje uchováváme",
                 f"<ul><li>Poptávky a komunikace: {f('např. 3 roky od poslední komunikace')}; pokud uzavřeme smlouvu, po dobu stanovenou zákonem (účetní a daňové předpisy).</li>"
                 f"<li>Životopisy: do konce výběrového řízení, se souhlasem {f('např. 1 rok')}.</li>"
                 f"<li>Záznamy serveru: {f('podle nastavení hostingu, obvykle 30–90 dní')}.</li></ul>"),
                ("Komu údaje předáváme",
                 f"<p>Údaje neprodáváme ani je nepředáváme k marketingu. Zpracovávají je jen naši zaměstnanci a dodavatelé, kteří pro nás zajišťují "
                 f"provoz webu a e-mailu ({f('název poskytovatele hostingu a e-mailu')}).</p>"
                 "<p>Video na úvodní stránce se načítá ze služby YouTube (Google Ireland Limited) – podrobnosti "
                 'najdete na stránce <a href="cookies.html">Cookies</a>. Google může údaje předávat do USA v rámci EU-US Data Privacy Framework.</p>'),
                ("Vaše práva",
                 "<p>Máte právo na přístup ke svým údajům, jejich opravu nebo výmaz, omezení zpracování, přenositelnost, "
                 "vznést námitku proti zpracování na základě oprávněného zájmu a odvolat souhlas, pokud byl udělen. "
                 'Stačí napsat na <a href="mailto:kostera@kostera.cz">kostera@kostera.cz</a>.</p>'
                 '<p>Pokud se domníváte, že údaje zpracováváme v rozporu s předpisy, můžete podat stížnost u Úřadu pro ochranu osobních údajů '
                 '(<a href="https://uoou.gov.cz" target="_blank" rel="noopener">uoou.gov.cz</a>).</p>'),
            ],
            note=f"Účinné od {f('datum')}. Tento text je vzor připravený pro web – před spuštěním ho firma ověří, případně s právníkem."),
        "cookies": dict(
            title="Cookies | J.K.FOOD",
            desc="Jaké cookies a úložiště v prohlížeči web kostera.cz používá. Bez reklamních a analytických cookies.",
            h1="Cookies",
            intro="Web kostera.cz nepoužívá reklamní ani analytické cookies a neměří vaši návštěvnost.",
            body=[
                ("Co web ukládá ve vašem prohlížeči",
                 '<div class="legal-table"><table><thead><tr><th>Název</th><th>K čemu slouží</th><th>Jak dlouho</th></tr></thead><tbody>'
                 "<tr><td><code>jkadmin</code></td><td>Přihlášení do administrace – jen pro správce webu.</td><td>do zavření prohlížeče</td></tr>"
                 "</tbody></table></div>"
                 "<p>Jinak web do vašeho prohlížeče nic neukládá.</p>"),
                ("Video z YouTube",
                 "<p>Na úvodní stránce je video ze služby YouTube (Google). Načte se, až stránku začnete procházet, a když k němu dojedete, "
                 "spustí se samo bez zvuku. Přehrává se z adresy youtube-nocookie.com (režim se zvýšenou ochranou soukromí), YouTube ale "
                 "může do vašeho prohlížeče ukládat cookies a obdobná data a zpracovávat vaši IP adresu – podle "
                 '<a href="https://policies.google.com/privacy" target="_blank" rel="noopener">zásad ochrany soukromí Google</a>.</p>'
                 "<p>Pokud si to nepřejete, můžete si v prohlížeči zablokovat obsah třetích stran nebo video sledovat přímo na YouTube.</p>"),
                ("Jak cookies smazat",
                 "<p>Cookies a data webu můžete kdykoli smazat v nastavení prohlížeče (obvykle Nastavení → Soukromí → Vymazat údaje o prohlížení).</p>"
                 '<p>Více o zpracování osobních údajů najdete na stránce <a href="ochrana-osobnich-udaju.html">Ochrana osobních údajů</a>.</p>'),
            ],
            note=""),
    }


LEGAL_FILES = {"privacy": "ochrana-osobnich-udaju.html", "cookies": "cookies.html"}

def page_legal(kind, lang="cs"):
    T = legal_texts(lang)[kind]
    file = LEGAL_FILES[kind]
    body = '<div class="legal">' + "".join(f'<section class="legal-sec"><h2>{h}</h2>{t}</section>' for h, t in T["body"]) \
        + (f'<p class="legal-note">{T["note"]}</p>' if T["note"] else "") + "</div>"
    graph = [{"@type": "WebPage", "url": f"{SITE}/{file}" if lang == "cs" else f"{SITE}/en/{_en().B2B_FILES[file]}",
              "name": T["h1"], "inLanguage": lang, "about": {"@id": f"{SITE}/#firma"}}]
    home = "Úvod" if lang == "cs" else "Home"
    return simple_page(file, T["title"], T["desc"], [(home, ""), (T["h1"], file)], T["h1"], T["intro"], body, "", graph,
                       en_file=_en().B2B_FILES[file], write=lang == "cs")


def build_legal():
    for k in LEGAL_FILES:
        page_legal(k)
    return [(f, "0.2") for f in LEGAL_FILES.values()]


def build_b2b(items):
    """Stránky pro firmy: Průmysl, šest oborů, Výzkum a vývoj, Hotová jídla."""
    for o in OBORY:
        page_obor(o, items)
    page_prumysl()
    page_vyvoj()
    page_jidla()
    return [("prumysl.html", "0.9"), ("vyzkum-a-vyvoj.html", "0.8"), ("hotova-jidla.html", "0.8")] + [(o["file"], "0.8") for o in OBORY]


AVIF_RE = re.compile(r'(img/[\w/-]+)\.webp')


def finalize_html():
    """Po vygenerování všech stránek: zmenšené styly (jen použitá pravidla), fotky AVIF (s WebP jako zálohou)
    a okamžité přechody mezi stránkami."""
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    import cssmin
    make_avif()
    allpages = list(ROOT.glob("*.html")) + list((ROOT / "en").glob("*.html"))
    src = (ROOT / "assets" / "styles.css").read_text(encoding="utf-8")
    js = set()
    # třídy, které se objeví až podle dat (reference s citátem, fotky týmu…) nebo je přidává skript
    for f in [*(ROOT / "assets").glob("*.js"), *(ROOT / "assets").glob("*.json"), *(ROOT / "tools").glob("*.py"), *(ROOT / "tools").glob("*.html")]:
        js |= set(re.findall(r"[A-Za-z_][\w-]*", f.read_text(encoding="utf-8")))
    tokens = set(js)
    for p in allpages:
        tokens |= cssmin.tokens_from_html(p.read_text(encoding="utf-8"))
    # písma mají v adrese otisk obsahu → mohou se v prohlížeči ukládat natrvalo, a přesto se po změně stáhnou znovu
    fver = {f.name: hashlib.sha1(f.read_bytes()).hexdigest()[:8] for f in (ROOT / "assets" / "fonts").glob("*.woff2")}
    fonts = lambda css: re.sub(r"url\((fonts/)([\w-]+\.woff2)\)", lambda m: f"url({m.group(1)}{m.group(2)}?v={fver.get(m.group(2), '')})", css)
    src = fonts(src)
    mincss = cssmin.minify(src, tokens)
    (ROOT / "assets" / "site.min.css").write_text(mincss, encoding="utf-8")
    cver = hashlib.sha1(mincss.encode()).hexdigest()[:8]
    for p in allpages:
        html = p.read_text(encoding="utf-8")
        orig = html
        html = re.sub(r'(/?(?:\.\./)?assets/)(?:styles|site\.min)\.css\?v=\w+', rf"\1site.min.css?v={cver}", html)
        html = re.sub(r'(assets/fonts/)([\w-]+\.woff2)(?:\?v=\w+)?"', lambda m: f'{m.group(1)}{m.group(2)}?v={fver.get(m.group(2), "")}"', html)
        if "<!-- HOME:START -->" in html:     # úvodní stránka: ve stránce jen styly, které sama používá
            pre = "../" if p.parent.name == "en" else ""
            css = cssmin.minify(src, cssmin.tokens_from_html(html)).replace("url(fonts/", f"url({pre}assets/fonts/")
            html = re.sub(r"(<!-- HOME:START -->.*?)<style>.*?</style>", lambda m: m.group(1) + "<style>" + css + "</style>", html, flags=re.S)
        if p.name == "404.html":
            if html != orig:
                p.write_text(html, encoding="utf-8")
            continue
        html = re.sub(r'<source [^>]*type="image/avif">', "", html)          # idempotentní: nejdřív staré AVIF pryč

        def avif(m):
            tag = m.group(0)
            files = AVIF_RE.findall(tag)
            if not files or not all((ROOT / f"{f}.avif").exists() for f in files):
                return tag
            return tag.replace(".webp", ".avif").replace('type="image/webp"', 'type="image/avif"') + tag
        html = re.sub(r'<source [^>]*type="image/webp">', avif, html)
        if 'type="speculationrules"' not in html:
            html = html.replace("</body>", SPECULATION + "\n</body>", 1)
        if html != orig:
            p.write_text(html, encoding="utf-8")


def main():
    v = asset_version()
    items = load_items()
    build_index(v)                      # nejdřív úvod: z něj ostatní stránky přebírají menu a patičku
    pages = build_catalog(items, v)
    pages += build_team(v)
    pages += build_career(v)
    pages += build_b2b(items)
    pages += build_legal()
    pages += build_en()
    finalize_html()
    build_ai(items)
    build_sitemap(pages)
    print(f"hotovo: {len(items)} výrobků, {len(pages)} stránek, verze stylů {v}")


if __name__ == "__main__":
    main()
