# Expert: Vnitřní fungování Bindery

Tato kapitola je určena uživatelům, kteří chtějí upravovat nejen vzhled knihy, ale také způsob, jakým Bindery jednotlivé dokumenty vytváří.

Předpokládá základní znalost `HTML`, `CSS` a `Pythonu`. Není nutné znát celý program nazpaměť. Důležité je vědět, kde hledat příslušnou část a jak její změna ovlivní výsledek.

## 1. Jak Bindery vytváří knihu

Bindery zpracovává zdrojové soubory, připravuje obsah, vkládá jej do šablon a vytváří výsledný dokument.

Zjednodušeně lze proces popsat takto:

1. Program načte informace o knize a její obsah.
2. Zpracuje jednotlivé kapitoly a připraví jejich HTML podobu.
3. Načte odpovídající šablony a vloží do nich připravený obsah.
4. Připojí potřebné styly a další zdroje.
5. Připraví výstup pro zvolený formát.
6. Dokončí generování a uklidí pracovní soubory.

Jednotlivé kroky se mohou podle typu výstupu lišit. `PDF` a `EPUB` například nemusí zpracovávat výsledné `HTML` stejným způsobem.

### Úloha jednotlivých částí

| Část          | Úloha                                                     |
|---------------|-----------------------------------------------------------|
| `Fonts`       | Fonty použité v knize                                     |
| `Images`      | Obrázky použité v knize                                   |
| `Misc`        | Licenční informace k jednotlivým souborům (např. fontům)  |
| `Pages`       | Zdrojový text knihy a její metadata                       |
| `Styles`      | CSS pravidla určující vzhled dokumentu                    |
| `TEMP`        | Pracovní soubory vznikající během generování              |
| `Templates`   | HTML šablony určující strukturu dokumentu                 |
| `bindery.py`  | Programová logika celého procesu                          |

Ne všechny části jsou určeny k běžnému používání. Uživatel připravující knihu obvykle pracuje především se zdrojovým obsahem. Expert může zasahovat také do šablon, stylů a samotného programu.

## 2. Složka Templates

Složka `Templates` obsahuje `HTML` předlohy, ze kterých Bindery sestavuje jednotlivé části knihy.

Šablona může určovat například strukturu obálky, rozložení nadpisů, umístění textu nebo způsob, jakým se zobrazí údaje o autorovi.

Šablona není hotová kniha. Je to předloha, do které program během generování doplní konkrétní obsah.

### 2.1 Zástupné značky

Šablony mohou obsahovat značky, které program při generování nahrazuje skutečnými hodnotami.

V Bindery se používají například:

    {{TITLE}}
    {{SUBTITLE}}
    {{AUTHOR}}
    {{CONTENT}}
    {{STYLES}}

Konkrétní použití závisí na dané šabloně a na tom, které hodnoty do ní program předává.

Pokud šablona obsahuje zástupnou značku, kterou program nenahradí, může se tato značka objevit ve výsledném dokumentu jako obyčejný text. Pokud naopak odstraníte značku, kterou program očekává, příslušný obsah se nemusí zobrazit.

Při úpravách proto zachovávejte všechny značky, které jsou pro danou šablonu potřebné.

### 2.2 Úprava existující šablony

Nejjednodušší způsob přizpůsobení Bindery je upravit již používanou šablonu.

Doporučený postup:

1. Zjistěte, který soubor se pro danou část knihy skutečně načítá.
2. Vytvořte jeho záložní kopii.
3. Upravte požadovanou část HTML.
4. Pokud změna vyžaduje nové styly, upravte také odpovídající CSS.
5. Znovu vygenerujte knihu a zkontrolujte výsledek.

Pokud chcete změnit například strukturu obálky, zasahujte do šablony obálky. Pokud chcete změnit strukturu běžné kapitoly, upravujte šablonu kapitoly.

Samotná změna šablony se projeví až při novém generování. Již vytvořený `PDF` nebo `EPUB` soubor se automaticky nezmění.

### 2.3 HTML versus CSS

`HTML` určuje strukturu. Rozhoduje například o tom, které prvky dokument obsahuje a v jakém pořadí jsou uspořádány. `CSS` určuje vzhled. Nastavuje například písmo, barvy, velikosti, okraje, zarovnání a rozvržení prvků.

Pokud chcete změnit barvu nadpisu, začněte v `CSS`. Pokud chcete přidat do dokumentu nový blok, který dosud neexistuje, bude zpravidla nutná úprava `HTML` a případně také `CSS`.

Ne každá vlastnost se navíc projeví stejně v `PDF` a `EPUB`. Výsledný vzhled ovlivňuje také způsob zpracování `HTML` a `CSS` daným výstupním formátem.

### 2.4 Přidání vlastní šablony

Novou šablonu lze vytvořit jako samostatný `HTML` soubor. Aby ji však Bindery používalo, musí být součástí jeho logiky.

Při přidávání vlastní šablony je nutné:

1. Vytvořit HTML soubor s požadovanou strukturou.
2. Připravit potřebné zástupné značky.
3. Zajistit, aby program novou šablonu načítal ve správné situaci.
4. Připojit odpovídající CSS a případné další zdroje.
5. Ověřit výsledek v požadovaných výstupních formátech.

Samotné vložení nového souboru do `Templates` nestačí, pokud program jeho existenci nikde nezohledňuje.

Chcete-li přidat například alternativní obálku, musíte v `bindery.py` najít místo, kde se vybírá šablona obálky, a upravit výběr tak, aby program dokázal použít i novou variantu.

Konkrétní způsob výběru závisí na současné implementaci. Než začnete program měnit, zjistěte, jak vybírá a načítá šablony ve své aktuální verzi.

## 3. Složka TEMP a pracovní soubory

`TEMP` je pracovní složka používaná během generování knihy.

Program do ní může ukládat připravené `HTML` dokumenty a další mezivýsledky, které potřebuje při sestavování výstupu.

Tyto soubory nejsou určeny k běžné editaci. Jsou však velmi užitečné při ladění a při zjišťování, kde vzniká chyba.

### 3.1 Proč se TEMP maže

Po dokončení generování Bindery uklízí nepotřebné pracovní soubory. Díky tomu se složka nezaplňuje daty z předchozích generování.

Pokud chcete sledovat vnitřní proces, můžete toto automatické mazání dočasně vypnout.

### 3.2 Jak zachovat pracovní soubory

Otevřete `bindery.py` a zakomentujete část, `remove_Temp(DIR_TEMP)`.

Po změně spusťte generování znovu. Pokud program složku `TEMP` automaticky nemaže, zůstanou pracovní soubory zachované pro kontrolu.

Po dokončení ladění vraťte původní chování.

## 4. Soubor bindery.py

`bindery.py` je hlavní soubor programu. Obsahuje logiku, která propojuje zdrojové soubory, šablony, styly a generování výsledných dokumentů.

Znalost tohoto souboru umožňuje upravovat chování programu, nejen výsledný vzhled.

### 4.1 Kdy je nutné znát Python

Pro běžné změny vzhledu není znalost Pythonu nutná. Pro přidání nové varianty šablony, změnu výběru souborů nebo úpravu průběhu generování už je zpravidla potřeba rozumět programové logice.

Nemusíte však celý program přepisovat. Ve většině případů je lepší najít existující funkci, pochopit její vstupy a výstupy a změnit jen nezbytnou část.

## 5. Vlastní úpravy a aktualizace

Při přizpůsobování Bindery je důležité rozlišovat mezi soubory, které obsahují vlastní úpravy, a soubory, které program doplňuje ze své výchozí šablony.

Pokud Bindery při prvním spuštění nebo synchronizaci doplňuje chybějící soubory, neznamená to automaticky, že bezpečně zachová všechny vlastní úpravy. Záleží na konkrétním způsobu synchronizace.

### Závěrečné doporučení

Bindery lze přizpůsobovat na několika úrovních. Pro vzhled používejte `CSS`, pro strukturu `HTML` šablony a pro změny samotného procesu generování upravujte `bindery.py`.

Složka `TEMP` vám pomůže pochopit, co program vytváří během jednotlivých kroků. Zachování těchto souborů je užitečné při ladění, ale pro běžný provoz není nutné.
