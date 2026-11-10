# Dohledatelnost webu kostera.cz – co je hotové a co udělat při spuštění

## Hotové v kódu

- **Přesměrování starého webu** (`.htaccess`): všech 542 adres starého webu (kategorie, výrobky,
  O nás, Kontakty …) trvale (301) vede na odpovídající stránku nového webu. Pozice ve vyhledávačích
  se tím přenesou a z odkazů z jiných webů nevznikne chyba 404.
- **Jedna adresa webu**: vše se přesměruje na `https://www.kostera.cz`.
- **Samostatné stránky skupin sortimentu** (`sortiment-*.html`) s vlastním titulkem, popisem,
  nadpisem a seznamem výrobků přímo v HTML – vyhledávače vidí všech 490 názvů výrobků.
- **Titulky a popisy** všech stránek v délce, kterou Google zobrazí celou.
- **Strukturovaná data (schema.org)**: firma (název, IČ, DIČ, adresa, telefon, e-mail, logo, rok založení),
  web, drobečková navigace, seznamy výrobků.
- **Sociální sítě**: náhledový obrázek a texty pro Facebook, WhatsApp, LinkedIn (`assets/icons/og-image.jpg`).
- **Ikony** pro prohlížeče, iPhone a Android, `site.webmanifest`.
- `robots.txt`, `sitemap.xml` (včetně propojení jazykových verzí), stránka `404.html`.
- **Anglická verze** (`en/`): úvod, katalog a tým s propojením jazyků pro Google (`hreflang`).
  Texty jsou v `tools/i18n_en.py` – když se změní český text, `python3 tools/build.py` ohlásí, co je potřeba přeložit.
- **Rychlost**: Lighthouse 97–100, komprese a dlouhé ukládání do mezipaměti.

## Při spuštění webu (jednorázově, cca 1 hodina)

1. **Google Search Console** (search.google.com/search-console): přidat doménu `kostera.cz`,
   ověřit ji (záznam v DNS) a odeslat `https://www.kostera.cz/sitemap.xml`.
   Starou verzi webu ani nic jiného není třeba mazat – přesměrování to vyřeší.
2. **Seznam Webmaster** (search.seznam.cz/webmaster): totéž pro Seznam – v Česku je pořád důležitý.
3. **Firmy.cz** (Seznam) a **Profil firmy na Googlu** (business.google.com): zkontrolovat, že název,
   adresa, telefon a web jsou **přesně stejné** jako na webu: Jaroslav Kostera, J.K.FOOD s.r.o.,
   Větřkovice 243, 747 43 Větřkovice, +420 556 310 205, https://www.kostera.cz.
   Přidat fotky výroby, otvírací dobu a krátký popis. Právě tyto profily rozhodují o zobrazení
   na mapách a u dotazů typu „výrobce koření Opava“.
4. **Bing Webmaster Tools**: lze jedním klikem naimportovat z Google Search Console.
5. Po týdnu v Search Console zkontrolovat **Stránky → Proč nejsou indexované** a
   **Vylepšení → Drobečková navigace**.

## Dlouhodobě (to, co posune web ve výsledcích nejvíc)

- **Odkazy z e-shopu chut.kostera.cz** na web kostera.cz (patička, „O nás“) a naopak.
- **Popisy výrobků**: zatím jsou v katalogu jen názvy. Krátký popis a použití u hlavních výrobků
  (např. „Gulášové koření – složení, dávkování, na co se hodí“) je nejsilnější obsah pro vyhledávání.
- **Fotky** výroby a výrobků s výstižnými názvy souborů a popisky.
- **Novinky / recepty**: pravidelný obsah (i jednou měsíčně) dává Googlu důvod web častěji procházet.
- **Profily na sociálních sítích**: až budou aktuální adresy (Facebook, Instagram, YouTube kanál),
  doplnit je do `ORG["same_as"]` v `tools/build.py` a spustit `python3 tools/build.py`.

## Údržba

Po každé změně výrobků (`assets/sortiment-data.js`), šablony katalogu nebo stylů spusťte:

```bash
python3 tools/build.py
```

Skript znovu vygeneruje stránky sortimentu, metadata, `sitemap.xml` a verze stylů pro prohlížeče.
Pokud by se změnila adresa webu, upravte `SITE` v `tools/build.py` a adresu v `robots.txt`.

## Vyhledávání přes AI (ChatGPT, Claude, Gemini, Perplexity, Copilot)

Hotové v kódu:
- `robots.txt` výslovně povoluje roboty AI vyhledávačů (GPTBot, OAI-SearchBot, ClaudeBot,
  Claude-SearchBot, PerplexityBot, Google-Extended, Applebot-Extended, Bingbot …).
- `llms.txt` a `llms-full.txt`: stručný strojově čitelný přehled firmy (fakta, kontakty, služby,
  skupiny sortimentu, časté dotazy) a úplný seznam výrobků – generuje `python3 tools/build.py`.
- Strukturovaná data: firma včetně oboru (`knowsAbout`), počtu zaměstnanců, sloganu, katalogu
  sortimentu, kontaktů; časté dotazy (`FAQPage`), drobečková navigace, seznamy výrobků.
- Obsah je přímo v HTML (bez načítání JavaScriptem), takže ho AI roboti přečtou celý.

Při spuštění:
1. **Bing Webmaster Tools** (bing.com/webmasters) – odeslat sitemap. ChatGPT Search a Copilot
   čerpají z indexu Bingu, je to pro AI vyhledávání stejně důležité jako Google.
2. **Google Search Console** – Gemini a AI přehledy v Googlu vycházejí z indexu Googlu.
3. **Konzistentní údaje všude**: název, adresa, telefon a web stejně na webu, Firmy.cz,
   Profilu firmy na Googlu, e-shopu i sociálních sítích – AI asistenti si fakta ověřují z více zdrojů.
4. Za pár týdnů vyzkoušet v ChatGPT / Claude / Perplexity dotazy typu „výrobce koření Opava“,
   „dodavatel kořenicích směsí pro masnou výrobu“ nebo „kdo vyrábí koření ve Větřkovicích“.

Co AI viditelnost posune nejvíc dlouhodobě: konkrétní popisy výrobků, zmínky o firmě na jiných
webech (oborové katalogy, Firmy.cz, články, reference odběratelů) a aktuální Časté dotazy.

## Verze 2 (návrh podle zákazníka) – složka `v2/`
- Generuje ji `python3 tools/build.py` z hotových stránek verze 1 + `tools/v2_home.html` a `assets/v2.css`.
- Má `noindex` (návrh k porovnání). Pokud se zvolí jako hlavní, přesune se do kořene a `noindex` se odstraní.
