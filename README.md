# Web J.K.FOOD (kostera.cz)

Statický web (HTML, CSS, JS) generovaný skriptem v Pythonu, s PHP jen pro poptávkový formulář a administraci kariéry.

## Kde co je

| Cesta | Co to je |
|---|---|
| `index.html` | **úvodní stránka – zdroj** (ručně upravovaná). Menu a patička odsud platí pro celý web. Části mezi značkami `<!-- …:START -->` a `<!-- …:END -->` doplňuje generátor. |
| `assets/styles.css` | **styly – zdroj**. Web používá z nich vygenerovaný zmenšený `assets/site.min.css`. |
| `assets/*.json`, `assets/sortiment-data.js` | data: výrobky, tým, reference, časté dotazy, kariéra (výchozí) |
| `tools/build.py` | generátor: katalog, Průmysl a obory, Výzkum a vývoj, Hotová jídla, tým, kariéra, anglická verze, SEO soubory |
| `tools/i18n_en.py` | anglické texty |
| `tools/sortiment.template.html` | šablona stránek katalogu |
| `tools/cssmin.py` | zmenšení stylů (jen použitá pravidla) |
| `api/` | PHP: poptávkový formulář (`poptavka.php`), data kariéry pro web (`kariera.php`) |
| `admin/` | PHP: administrace kariéry |
| `img/` | fotky (WebP/AVIF/JPG), popis v `img/README.md` |
| `en/`, `sortiment*.html`, `prumysl.html`, obory, `nas-tym.html`, `kariera.html`… | **vygenerované** – neupravovat ručně |

## Úpravy

1. Upravte zdroj (`index.html`, `assets/styles.css`, data v `assets/` nebo texty v `tools/`).
2. Spusťte generátor:
   ```bash
   python3 tools/build.py
   ```
   Vygeneruje všechny stránky, anglickou verzi, `sitemap.xml`, `llms.txt`, zmenšené styly a AVIF fotky.
   Ohlásí, pokud chybí anglický překlad.
3. Náhled: `python3 -m http.server` a otevřít `http://localhost:8000` (formulář a administrace potřebují PHP: `php -S localhost:8000`).

Potřeba: Python 3.10+ s knihovnami `Pillow` (fotky AVIF) a `fontTools` (jen při úpravě písem).

## Návody

- [NASAZENI.md](NASAZENI.md) – nasazení na hosting, co potřebuje server, kontrolní seznam
- [api/NAVOD.md](api/NAVOD.md) – poptávkový formulář (SMTP) a administrace kariéry
- [SEO.md](SEO.md) – vyhledávače a AI vyhledávání, co udělat při spuštění
- [img/README.md](img/README.md) – fotky: názvy, rozměry, výměna
