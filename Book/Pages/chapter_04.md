# Syntaxe Markdownu

Markdown je jednoduchý způsob, jak psát formátovaný text pomocí běžných znaků. Stačí text napsat a doplnit pár symbolů, například `#` pro nadpis nebo `**` pro tučné písmo.

Tento návod ukazuje přesný zápis v `Markdownu` a na konci, jak bude text vypadat v dokumentu.

---

### 1. Nadpisy

Počet znaků `#` na začátku řádku určuje úroveň nadpisu. Za `#` vždy napište mezeru.

    # Nadpis první úrovně (největší)
    ## Nadpis druhé úrovně
    ### Nadpis třetí úrovně
    #### Nadpis čtvrté úrovně
    ##### Nadpis páté úrovně
    ###### Nadpis šesté úrovně (nejmenší)

> **Tip:** Používejte jeden nadpis první úrovně na dokument a dál se držte logické hierarchie.  

### 2. Odstavce a zalomení řádku

**Text** se píše bez speciální syntaxe. Odstavce se oddělují **prázdným řádkem**.

    První odstavec.
    
    Druhý odstavec.


Chcete-li zalomit řádek **bez** založení nového odstavce, ukončete předchozí řádek **dvěma mezerami**.

    První řádek··
    Druhý řádek

> **Pozor:** Znak `·` zde znázorňuje mezeru. Do dokumentu napište skutečné mezery.

### 3. Formátování textu

Markdown umožňuje jednoduché formátování textu. Můžete zapsat tučný text, kurzívu, tučnou kurzívu nebo přeškrtnutý text.

    **tučné**
    *kurzíva*
    ***tučná kurzíva***
    ~~přeškrtnuto~~

### 4. Citace

Řádek uvozený znakem `>` se zobrazí jako citace.

    > Citace textu.
    > Může mít i více řádků.

### 5. Kód

Kód můžete vložit přímo do věty nebo jako samostatný blok.

##### Kód uvnitř věty

Text ohraničte jedním zpětným apostrofem (`` ` ``).

    Příkaz `git status` zobrazí stav repozitáře.

##### Blok kódu

Blok ohraničte třemi zpětnými apostrofy na samostatných řádcích nebo **čtyřmi mezerami** a nebo tabulátorem.

    ```
    console.log("Ahoj, světe!")
    ```

    ....console.log("Ahoj, světe!")

> **Pozor:** Znak `·` zde znázorňuje mezeru. Do dokumentu napište skutečné mezery nebo tabulátor.  

> **Pozor:** Uvozovky `"takto"` v běžném textu nepotřebují žádnou speciální syntaxi. Kód (zpětné apostrofy) používejte jen pro skutečný kód nebo přesné texty.

### 6. Seznamy

##### Odrážkový seznam

Použijte pomlčku, hvězdičku nebo plus, vždy s mezerou za znakem.

    - První položka seznamu
    - Druhá položka seznamu
    - ...

    * První položka seznamu
    * Druhá položka seznamu
    * ...

    + První položka seznamu
    + Druhá položka seznamu
    + ...

##### Číslovaný seznam

    1. První číslovaná položka seznamu
    2. Druhá číslovaná položka seznamu
    3. ...

##### Vnořený seznam

Podpoložku odsaďte o **4 mezery** nebo jeden tabulátor.

```
- První položka seznamu
....- První vnořená položka seznamu
....- Druhá vnořená položka seznamu
```

> **Pozor:** Znak `·` zde znázorňuje mezeru. Do dokumentu napište skutečné mezery.

### 7. Odkazy

Text odkazu dejte do hranatých závorek a adresu do kulatých závorek. Kliknutím na `Text odkazu` se otevře uvedená internetová adresa.

    [Text odkazu](https://www.example.com)

### 8. Obrázky

Zápis je podobný odkazu, jen začíná vykřičníkem. Text v hranatých závorkách je **alternativní popis** obrázku. Zobrazí se, když se obrázek nenačte, a čtou ho odečítače obrazovky.

##### Obrázek bez určení velikosti

    ![Název obrázku](../Images/image.png)

##### Obrázek s určenou šířkou

Bindery rozšiřuje standardní Markdown o možnost nastavit šířku obrázku v procentech. Za alternativní popis přidejte svislítko `|` a požadovanou šířku v procentech.

    ![Název obrázku|25%](../Images/image.png)
    ![Název obrázku|50%](../Images/image.png)
    ![Název obrázku|75%](../Images/image.png)
    ![Název obrázku|99%](../Images/image.png)

> **Pozor:** Pro obrázek v dokumentu nepoužívejte název `cover`. Tento název je vyhrazený pro obálku knihy.  

> **Tip:** Pokud budete chtít stejný obrázek použít také uvnitř dokumentu, vložte do složky `Images` druhý obrázek s jiným názvem.

> **Tip:** Cestu k obrázku zadávejte relativně k umístění vašeho dokumentu. `../` znamená "o složku výš".

### 9. Tabulky

Sloupce oddělte svislítkem `|`. Druhý řádek (z pomlček) odděluje záhlaví od obsahu.

    | Sloupec 1 | Sloupec 2 |
    |-----------|-----------|
    | Text      | Text      |
    | Text      | Text      |

**Zarovnání sloupců** určíte dvojtečkou v oddělovacím řádku.

    | Vlevo |  Střed  | Vpravo |
    |:------|:-------:|-------:|
    | text  | text    | text   |

> **Tip:** Svislítka nemusí být pod sebou. Zarovnání je jen pro vaše pohodlí při psaní.

### 10. Oddělovač

Tři pomlčky na samostatném řádku vytvoří vodorovnou čáru.

    ---

### 11. Speciální znaky

Pokud chcete, aby se znak, který má v Markdownu zvláštní význam, zobrazil doslova, napište před něj zpětné lomítko `\`.

    \# Tohle není nadpis první úrovně
    \**Tohle není tučné\**
    \*Tohle není kurzíva\*

Takto lze vypsat například: `\`, `*`, `_`, `#`, `[`, `]`, `` ` ``, `>`

### 12. Tip

Pro studijní účely můžete také využít tohoto průvodce, který najdete na stránce projektu [Github](https://github.com/PepikVaio/iPad_Test)

---

## Rychlý přehled

| Chci...                   | Napíšu...              | Výsledek              |
|---------------------------|------------------------|-----------------------|
| Nadpis                    | `# Nadpis`             | Nadpis                |
| Tučně                     | `**text**`             | **text**              |
| Kurzívu                   | `*text*`               | *text*                |
| Přeškrtnout               | `~~text~~`             | ~~text~~              |
| Citaci                    | `> citace`             | > citace              |
| Kód ve větě               | `` `kód` ``            | `kód`                 |
| Blok kódu                 | tři zpětné apostrofy   | blok kódu             |
| Odrážku                   | `- položka`            | - položka             |
| Číslovaný seznam          | `1. položka`           | 1. položka            |
| Odkaz                     | `[text](adresa)`       | [Text odkazu](adresa) |
| Obrázek                   | `![popis](cesta)`      | obrázek               |
| Obrázek na 50 % (Bindery) | `![popis\|50%](cesta)` | obrázek na 50 %       |
| Vodorovnou čáru           | `---`                  | vodorovná čára        |
| Doslovný znak             | `\*`                   | \*                    |
