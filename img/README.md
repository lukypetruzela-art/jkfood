# Fotky pro web

## Úvodní stránka

| Soubory | Kde je na webu |
|---|---|
| `uvod-900/1536.(avif/webp)`, `uvod.jpg` | velká úvodní fotka (rozmazání vlevo pod textem je přímo ve fotce) |
| `uvod-m-600.(avif/webp)` | úvodní fotka na mobilu (výřez na výšku, rozmazaný spodek) |
| `pilir-prumysl-*`, `pilir-vyvoj-*`, `pilir-produkty-*` | karty Průmysl / Vývoj na míru / Vlastní produkty (600, 800, 1000 px) |
| `hero-2-700/900.*`, `hero-2.jpg` | fotka u sortimentu |

Fotky jsou zatím **generované** – až budou skutečné fotky z výroby, nahraďte je (stejné názvy a rozměry).
Uložte WebP (kvalita ~70) a spusťte `python3 tools/build.py` – verze AVIF se vytvoří samy (seznam `AVIF_SRC` v `tools/build.py`).

Web fotky nenačítá „naslepo“, aby prohlížeč nehlásil chyby pro neexistující soubory.
Popisky pod fotkami se upravují v atributu `data-cap`.
