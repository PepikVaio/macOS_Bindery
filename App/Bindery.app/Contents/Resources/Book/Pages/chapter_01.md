# Co je Bindery

Bindery je nástroj pro vytváření knih z textových souborů, obrázků a dalších podkladů.

Je určený jak pro uživatele, kteří chtějí jednoduše napsat a vytvořit vlastní knihu, tak pro pokročilé uživatele, kteří chtějí ovlivnit její vzhled a způsob generování.

Kniha je v Bindery tvořena především pomocí souborů `Markdown`. Text knihy je rozdělen do jednotlivých stránek nebo kapitol a obrázky jsou uloženy samostatně.

Bindery z těchto souborů vytvoří výslednou knihu.

## Pro koho je Bindery určen

Bindery může používat například:

- autor knihy
- člověk vytvářející dokumentaci
- technický dokumentátor
- uživatel vytvářející elektronickou knihu
- pokročilý uživatel, který chce mít kontrolu nad vzhledem knihy
- vývojář, který chce Bindery dále upravovat

Základní používání nevyžaduje znalost programování. Stačí vytvořit obsah knihy, uložit jej do správné struktury a nechat Bindery knihu vygenerovat.

## Jak Bindery pracuje

Základem je složka s knihou. V ní jsou uloženy informace o knize, text jednotlivých částí a obrázky.

**Například:**

    Moje kniha/
    ├── Images/
    ├── Pages/
    ├── description.md
    └── settings.md

Bindery tuto strukturu načte a použije ji jako zdroj pro vytvoření výsledné knihy. Čím pokročilejší uživatel je, tím více částí procesu může ovlivnit.
