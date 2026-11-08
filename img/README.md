# Fotky pro web

## Galerie v úvodu (nahoře na stránce)

| Soubor | Co na fotce |
|---|---|
| `hero-1.jpg` | Výroba ve Větřkovicích |
| `hero-2.jpg` | Koření a kořenicí směsi |
| `hero-3.jpg` | Sušená zelenina a houby |
| `hero-4.jpg` | Hotová jídla z našich surovin |

- **Formát:** JPG, ideálně čtverec cca 1600 × 1600 px, do 400 kB na fotku
  (web fotku ořízne do tvaru bubliny z loga, střed zůstane vidět).
- Dokud fotka chybí, zobrazí se zástupný rámeček s názvem souboru.

### Jak fotku zapojit

1. Nahrajte fotku do této složky pod názvem z tabulky.
2. V `index.html` najděte příslušný snímek (`<figure class="g-slide" … data-cap="…">`)
   a hned za řádek `<figure …>` vložte:

   ```html
   <img src="img/hero-1.jpg" alt="Výroba ve Větřkovicích" width="1600" height="1600" decoding="async">
   ```

   U prvního snímku přidejte navíc `fetchpriority="high"`, u ostatních `loading="lazy"`.

Web fotky nenačítá „naslepo“, aby prohlížeč nehlásil chyby pro neexistující soubory.
Popisky pod fotkami se upravují v atributu `data-cap`.
