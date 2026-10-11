# Začátečník

Tato kapitola vás provede vytvořením první knihy od úplného začátku až po její vygenerování.  

## 1. Vytvoření složky knihy

Nejdříve vytvořte novou složku knihy, například:

    Moje kniha/

## 2. Vytvoření základní struktury

Ve složce vytvořte 2 další složky:

    Pages/
    Images/

A dále 2 soubory:

    description.md
    settings.md

Výsledná struktura bude vypadat takto:

    Moje kniha/
    ├── Images/ (doporučené)
    ├── Pages/
    ├── description.md (doporučené)
    └── settings.md (doporučené)

## 3. Přidání obálky knihy

Otevřete složku `Images`. Do ní vložte obrázek knihy a pojmenujte jej `cover` (obrázek může být ve formátu `png`, `jpg`, `jpeg`).

Výsledná struktura bude vypadat takto:

    Moje kniha/
    ├── Images/
    │   ├── background.png (volitelné)
    │   └── cover.png (doporučené)
    ├── Pages/
    ├── description.md
    └── settings.md

> **Info:** Obrázek vyberte bez popisků, Bindery jej doplní ze souboru `description.md` (viz dále).  
> Pokud nevyberete žádný obrázek, Bindery vytvoří bílou přední stránku s popisky knihy (viz dále).

> **Info:** Pokud budete chtít na každou stránku obrázek pozadí, uložte do složky `Images` soubor `background.png`, Bindery si jej načte a použije (funguje pouze v `PDF`).

## 4. Vytvoření první stránky

Otevřete složku `Pages`. V ní vytvořte první markdown soubor, který pojmenujte `chapter_01.md`

**Do souboru napište:**

    # Moje první kapitola
    
    Toto je moje první kniha vytvořená pomocí Bindery.
    
    Toto je druhý odstavec knihy.

Výsledná struktura bude vypadat takto:

    Moje kniha/
    ├── Images/
    │   ├── background.png
    │   └── cover.png
    ├── Pages/
    │   └── chapter_01.md
    ├── description.md
    └── settings.md

> **Tip:** Každý soubor představuje jednu kapitolu knihy.

> **Tip - Jak psát text:**  
> Bindery používá `Markdown`, který umožňuje jednoduchým způsobem zapsat například nadpisy, tučné písmo, kurzívu nebo seznamy (více v části `Syntaxe Markdownu`).

## 5. Soubor description.md

Soubor `description.md` obsahuje základní informace o knize. Otevřete jej v textovém editoru a zapište informace podle struktury, kterou Bindery používá.

**Do souboru napište:**

    # Title
    název knihy
    
    # Subtitle
    podtitul knihy
    
    # Author
    autor knihy
    
    # Series
    série knihy (pokud je)
    
    # Number
    číslo série knihy (pokud je)
    
    # Rating
    hodnocení knihy, pomocí hvězdiček (maximálně 5)
    
    # Tags
    štítky knihy (román, detektivní, ...)
    
    # Identifier
    isbn: 
    
    # Published
    datum vydání knihy
    
    # Publisher
    vydavatel / nakladatel knihy
    
    # Language
    jazyk knihy (cs, en, ...)
    
    # Description
    #### Popis knihy:
    stručný popis knihy.

> **Info:** Pokud některé informace nechcete zapisovat, jednoduše je nechte prázdné.  
> Tyto informace budou uložené v metadatech knihy (některé čtečky knih je dokáží zobrazit).

> **Pozor:** Pokud nevytvoříte soubor `description.md`, nebude kniha obsahovat metadata ani popisky obálky knihy.

## 6. Soubor settings.md

Soubor `settings.md` obsahuje základní nastavení knihy. Otevřete jej v textovém editoru a zapište informace podle struktury, kterou Bindery používá.

**Do souboru napište:**

    # Format
    A4 (nebo A5, A6, ... nebo velikost v px např.: 1404x1872px)
    
    # Base font size
    15 (základní velikost písma)
    
    # Type
    book (nebo document, který má více možností formátování textu)
    
    # Image size
    contain (nebo cover)

> **Info:** Pokud některé informace nechcete zapisovat, jednoduše je nechte prázdné, nebo pokud soubor vůbec nevytvoříte, Bindery samo nastaví výchozí hodnoty (`A4`, `15`, `book`, `cover`).

> **Info:** Pokud vytváříte knihu, zvolte `#Type book`, dostanete vzhled knihy, tedy odsazení odstavců, jako v klasické knize. Pokud chcete vytvořit návod nebo jiný dokument, zvlote `document`, jednotlivé odstavce nejsou odsazené od kraje stránky.

> **Info:** Pokud budete chtít, obrázek knihy cely viditelný, zvolte `#Image size contain`. Pokud chcete obrázek roztáhnout, aby vyplnil celý prostor stránky, zvolte `contain`.

## 7. Generování knihy

Po dokončení bude struktura vypadat například takto:

    Moje kniha/
    ├── Images/
    │   ├── background.png
    │   └── cover.png
    ├── Pages/
    │   ├── chapter_01.md
    │   └── chapter_02.md (dle počtu kapitol)
    ├── description.md
    └── settings.md

Nyní máte připravené všechny základní části knihy.

Spusťte Bindery a vyberte složku s knihou. Bindery načte její obsah a připraví knihu k vytvoření.  

Pokud pracujete ve webové aplikaci, vyberte jaký formát knihy chcete stáhnout. Pokud pracujete v desktopové verzi, Bindery sama vytvoří knihu na základě nastavení a uloží ji do složky s knihhou, například `Moje kniha`.

## 8. Dodatečná úprava knihy

Pokud chcete v knize něco změnit, upravte příslušný soubor.

Po provedení změn knihu znovu vygenerujte. Tímto způsobem můžete knihu postupně vytvářet a upravovat, aniž byste museli celý projekt vytvářet znovu.
