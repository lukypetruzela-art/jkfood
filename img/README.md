# Fotky pro web

## Galerie v úvodu (nahoře na stránce)

| Snímek | Fotka | Popisek |
|---|---|---|
| 1 | `hero-1` | Výroba kořenicích směsí |
| 2 | `hero-2` | Koření a kořenicí směsi |
| 3 | `hero-3` | Sušená zelenina a houby |
| 4 | `hero-4` | Balení pro průmysl a gastro |

Fotky jsou zatím **generované** – až budou skutečné fotky z výroby, nahraďte je.

Každá fotka je uložená ve čtyřech souborech: `hero-N-700.webp`, `hero-N-900.webp`,
`hero-N-1200.webp` (prohlížeč si vybere velikost podle displeje) a `hero-N.jpg` (pro staré prohlížeče).
Při výměně fotky vytvořte stejné čtyři soubory (čtverec, WebP kvalita ~70, JPG ~76)
a v `index.html` upravte popisek (`data-cap`) a popis obrázku (`alt`).

Web fotky nenačítá „naslepo“, aby prohlížeč nehlásil chyby pro neexistující soubory.
Popisky pod fotkami se upravují v atributu `data-cap`.
