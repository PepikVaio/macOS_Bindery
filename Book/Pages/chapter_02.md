# Začínáme

Bindery lze používat několika způsoby:

- jako aplikaci pro Windows
- jako aplikaci pro macOS
- prostřednictvím webové verze

Princip práce s knihou je stejný. Kniha je uložena ve vlastní složce a Bindery z této složky načítá její obsah.

## První spuštění

Po spuštění Bindery je potřeba vybrat nebo vytvořit složku, ve které bude kniha uložena. Tato složka bude představovat celý projekt knihy. Je vhodné vytvořit pro každou knihu vlastní složku.

Například:

    Moje kniha/

Do této složky budete postupně přidány jednotlivé soubory knihy.

## Základní princip

Práce s Bindery je jednoduchá:

1. vytvoříte složku knihy
2. vytvoříte informace o knize
3. vytvoříte text knihy
4. přidáte obrázky
5. spustíte generování
6. Bindery vytvoří výslednou knihu

Jednotlivé části knihy jsou uloženy jako běžné soubory. Díky tomu je možné knihu upravovat i bez Bindery, například pomocí běžného textového editoru.  

## Co je potřeba pro první knihu

Pro první jednoduchou knihu stačí čtyři základní části:

    Moje kniha/
    ├── Images/
    ├── Pages/
    ├── description.md
    └── settings.md

Další možnosti Bindery lze přidávat postupně podle toho, co od výsledné knihy potřebujete.

> **Info - Složky a soubory jsou pojmenované dle využití:**  
> `Images` obsahuje obrázky používané v knize.  
> `Pages` obsahuje texty knihy.  
> `description.md` obsahuje popisky ke knize.  
> `settings.md` obsahuje nastavení knihy.

> **Info:** Všechny ostatní potřebné části si také Bondery vytvořit sama.

---

# Obsah

Tato příručka je rozdělene do několika částí, dle zkušenosti uživatele.  

- Začátecník zapíše pouze 2 ladící soubory a poté se věnuje pouze psaní obsahu knihy. O zbytek se postará Bindery.
    - Syntaxe: Markdown je jednoduchý způsob, jak psát formátovaný text pomocí běžných znaků.  

- Pokročilý užívatel má možnost pomocí Bindery upravit vzhled výsledné knihy. Tato část je určena uživatelům, kteří chtějí mít větší kontrolu nad typografií, písmem a vzhledem jednotlivých prvků.

- Expert, může nahlédnout jak Bindery pracuje uvnitř, a případně upravit samotný proces generování knihy.

