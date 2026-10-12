# Pokročilý uživatel

> **Pozor:** Tato část předpokládá, že jste si nastudovali předchozí kapitolu `Začátečník`.

Pokročilé možnosti Bindery umožňují upravit vzhled výsledné knihy. Tato část je určena uživatelům, kteří chtějí mít větší kontrolu nad typografií, písmem a vzhledem jednotlivých prvků.

## Písmo

Bindery umožňuje používat vlastní písma. Fonty mohou být součástí projektu knihy a následně použity při generování výsledného dokumentu.

Použití vlastního písma umožňuje například:

- změnit vzhled běžného textu
- použít jiné písmo pro nadpisy
- používat vlastní typografii
- vytvořit jednotný vzhled celé knihy

Otevřete složku s knhou a vytvořte v ní novou složku pojmenovanou `Fonts`. Do složky uložte vlastní fonty ve tvaru `ttf` nebo `otf`.

Fonty pojmenujte následovně:

- header.ttf
- header_Italic.ttf
- italic.ttf
- italic_Bold.ttf
- paragraph.ttf
- paragraph_Bold.ttf

Výsledná struktura bude vypadat takto:

    Moje kniha/
    ├── Fonts/
    │   ├── header.ttf
    │   ├── header_Italic.ttf
    │   ├── italic.ttf
    │   ├── italic_Bold.ttf
    │   ├── paragraph.ttf
    │   └── paragraph_Bold.ttf (dle počtu vlastních fontů)
    ├── Images/
    ├── Pages/
    ├── description.md
    └── settings.md

> **Pozor - Fonty jsou pojmenované dle použití:**  
> `header.ttf` pro nadpisy.  
> `paragraph.ttf` pro texty.  
> `italic` pro kurzívu.  
> `bold` pro tučné písmo.

> **Tip:** Nemusíte stahovat všechny fonty, stačí pouze ty, které potřebujete.

> **Varování:** Pokud budete stahovat dostupné fonty z internetu a knihu publikovat za peníze, vždy si přečtěte licenci.

## CSS

Vzhled knihy lze upravovat také pomocí `CSS`.

`CSS` určuje například:

- velikost textu
- typ písma
- řádkování
- zarovnání
- mezery
- vzhled nadpisů
- vzhled odstavců
- vzhled obrázků
- další vizuální vlastnosti dokumentu

Vytváření vlastních `CSS` souborů není v této uživatelské úrovni dovoleno. Pokud ale přesto chcete upravit vzhled knihy, je to možné.

Nejprve vygenerujte knihu. Poté se ve složce s knihou zobrazí složka `Styles`.

Struktura bude vypadat takto:

    Moje kniha/
    ├── Fonts/
    ├── Images/
    ├── Pages/
    ├── Styles/
    │   ├── style_body.css
    │   ├── style_cover.css
    │   ├── style_font.css
    │   └── style_chapter.css
    ├── description.md
    └── settings.md

Následně můžete tyto soubory otevřít a upravit tak jak potřebujete. Veškeré informace o úpravě `CSS` souborů se dozvíte na internetu. Úprava stylů přesahuje rozsah této příručky a není možné pokrýt veškeré možnosti, které `CSS` nabízí.

> **Info - Níže je seznam stránek, které vám s úpravou `CSS` pomůžou:**  
> [CSS: Cascading Style Sheets - MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/CSS)  
> [A Complete CSS Flexbox Layout Guide](https://css-tricks.com/snippets/css/a-guide-to-flexbox/)  
