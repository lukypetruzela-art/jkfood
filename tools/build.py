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
    footcats = "".join(f'<li><a href="{c["file"]}">{esc(c["name"])}</a></li>' for c in CATS)
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
                .replace("{{FOOTCATS}}", footcats).replace("{{LEGACY}}", legacy if active is None else ""))
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
    legend = "\n".join(
        f'<li><a href="{c["file"]}" data-cat="{i}"><canvas class="sw-ic" data-ic="{i}" width="28" height="28" aria-hidden="true"></canvas><span class="nm">{esc(c["name"])}</span></a></li>'
        for i, c in enumerate(CATS))
    s = re.sub(r"<!-- LEGEND:START -->.*?<!-- LEGEND:END -->", lambda m: f"<!-- LEGEND:START -->\n{legend}\n<!-- LEGEND:END -->", s, flags=re.S)
    foot = "".join(f'<li><a href="{c["file"]}">{esc(c["name"])}</a></li>' for c in CATS)
    s = re.sub(r"<!-- FOOTCATS:START -->.*?<!-- FOOTCATS:END -->", lambda m: f"<!-- FOOTCATS:START -->{foot}<!-- FOOTCATS:END -->", s, flags=re.S)
    s = re.sub(r"<!-- FAQ:START -->.*?<!-- FAQ:END -->", lambda m: f"<!-- FAQ:START -->\n{render_faq('cs')}\n<!-- FAQ:END -->", s, flags=re.S)
    s = re.sub(r"<!-- REFERENCE:START -->.*?<!-- REFERENCE:END -->", lambda m: f"<!-- REFERENCE:START -->\n{render_refs()}\n<!-- REFERENCE:END -->", s, flags=re.S)
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


def simple_page(file, title, desc, crumbs, h1, intro, body, cta, graph, nav_current=None, en_file=None):
    """Podstránka se stejnou hlavičkou a patičkou jako index.html (Náš tým, Kariéra)."""
    idx = (ROOT / "index.html").read_text(encoding="utf-8")
    head_start = idx[: idx.index("<!-- META:START -->")]
    head_rest = idx[idx.index("<!-- META:END -->") + len("<!-- META:END -->"): idx.index("</head>")]
    symbols = idx[idx.index('<svg width="0"'): idx.index("</svg>", idx.index('<svg width="0"')) + 6]
    header = idx[idx.index('<header class="top"'): idx.index("</header>") + 9]
    footer = idx[idx.index('<footer class="foot">'): idx.index("</footer>") + 9]

    def relink(x):
        x = re.sub(r'href="#(?!logo|mark|obsah")([\w-]+)"', r'href="index.html#\1"', x)
        return x.replace('<a class="brand" href="#"', '<a class="brand" href="index.html"')
    header, footer = relink(header), relink(footer)
    header = header.replace('<a class="link lang" href="en/index.html"', f'<a class="link lang" href="en/{en_file or "index.html"}"')
    if nav_current:
        header = header.replace(f'<a class="link" href="{nav_current}">', f'<a class="link" href="{nav_current}" aria-current="page">')

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
    (ROOT / file).write_text(page, encoding="utf-8")


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


def build_career(v):
    """Stránka Kariéra (kariera.html) z assets/kariera.json."""
    data = json.loads((ROOT / "assets" / "kariera.json").read_text(encoding="utf-8"))
    mail = data["kontakt_email"]
    why = "".join(f'<li><h3>{esc(w["nadpis"])}</h3><p>{nbsp(esc(w["text"]))}</p></li>' for w in data["proc"])
    jobs = []
    for i, j in enumerate(data["pozice"]):
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
            f'<p>{len(data["pozice"])} {"pozice" if 2 <= len(data["pozice"]) <= 4 else "pozic" if len(data["pozice"]) != 1 else "pozice"} · klikněte pro podrobnosti</p></div>'
            f'<ul class="jobs">{"".join(jobs)}</ul></section>')
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
            if re.match(r"(https?:|//|#|mailto:|tel:|data:|/|\.\./)", u):
                return m.group(0)
            base, _, frag = u.partition("#")
            if base == "index.html" or base.startswith("index.html?"):
                new = u
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
        return re.sub(r'\b(href|src|action)="([^"]*)"', fix, html)

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
                      f'<a class="link lang" href="../{cz_target}" hreflang="cs" lang="cs" aria-label="Česká verze">CZ</a>', html)

    org = dict(org_ld(), description="A Czech family company from Větřkovice. Since 1996 we have produced spices, seasoning blends, "
               "dried vegetables and dehydrated foods for food manufacturers, canteens and catering.")

    # --- úvodní stránka
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    html = re.sub(r"<!-- FAQ:START -->.*?<!-- FAQ:END -->", lambda m: f"<!-- FAQ:START -->\n{render_faq('en')}\n<!-- FAQ:END -->", html, flags=re.S)
    html = names(tr(html, T.COMMON + T.INDEX, "index"))
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

    # --- kontrola: nepřeložené dvojice a zbytky češtiny
    if missing:
        raise SystemExit("Nepřeložené texty (upravte tools/i18n_en.py):\n  " + "\n  ".join(missing))
    allowed = {"Větřkovice", "Galčanová", "Kostera", "Větřkovic", "Česká verze", "Má chuť", "pepř, guláš"}
    leftovers = []
    for f in ["index.html", "products.html", "team.html"]:
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
    return [("en/", "0.8"), ("en/products.html", "0.7"), ("en/team.html", "0.5")]

# ---------------------------------------------------------------- AI vyhledávače
AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User",
           "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended", "Bingbot",
           "DuckAssistBot", "Meta-ExternalAgent", "MistralAI-User", "CCBot"]


def build_ai(items):
    """robots.txt (výslovně povolené AI roboty), llms.txt a llms-full.txt – stručný strojově čitelný
    přehled firmy pro ChatGPT, Claude, Gemini, Perplexity a další (konvence llmstxt.org)."""
    robots = ["# Vyhledávače i AI asistenti mají k veřejnému obsahu webu přístup povolený.", "User-agent: *",
              "Allow: /", "Disallow: /api/", "Disallow: /tools/", ""]
    for bot in AI_BOTS:
        robots += [f"User-agent: {bot}", "Allow: /", "Disallow: /api/", "Disallow: /tools/", ""]
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
- [Úvod]({SITE}/): kdo jsme, pro koho vyrábíme, výroba na míru, kontakt
- [Sortiment]({SITE}/sortiment.html): kompletní seznam výrobků s možností poptávky
- [Náš tým]({SITE}/nas-tym.html): vedení firmy, obchod, výroba
- [Kariéra]({SITE}/kariera.html): volné pozice
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
    pairs = {"": "en/", "sortiment.html": "en/products.html", "nas-tym.html": "en/team.html"}
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


def main():
    v = asset_version()
    items = load_items()
    pages = build_catalog(items, v)
    build_index(v)
    pages += build_team(v)
    pages += build_career(v)
    pages += build_en()
    build_ai(items)
    build_sitemap(pages)
    print(f"hotovo: {len(items)} výrobků, {len(pages)} stránek (sortiment, tým, kariéra), verze stylů {v}")


if __name__ == "__main__":
    main()
