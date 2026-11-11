# Formulář poptávky – zprovoznění

Formulář na webu odesílá poptávky skriptem `api/poptavka.php`, který je pošle e-mailem
přes SMTP schránku firmy. Nic se neposílá žádné třetí straně.

## 1. Co potřebujeme od správce hostingu / IT

| Údaj | Příklad |
|---|---|
| SMTP server | `smtp.wedos.net`, `smtp.forpsi.com`, `smtp.active24.com` … |
| Port a šifrování | `587` + STARTTLS (doporučeno), nebo `465` + SSL |
| Schránka pro odesílání | ideálně nová `web@kostera.cz` (nebo existující) |
| Heslo k této schránce | — |

Hosting musí mít **PHP 7.4 nebo novější** (s rozšířeními `openssl` a `mbstring` – bývají standardně)
a web musí běžet na **HTTPS**.

## 2. Nastavení

1. Zkopírujte `api/config.example.php` jako `api/config.php`.
2. Doplňte do něj údaje z tabulky výše (`smtp_host`, `smtp_port`, `smtp_secure`, `smtp_user`, `smtp_pass`).
3. Zkontrolujte `allowed_origins` – musí obsahovat adresu webu (např. `https://www.kostera.cz`).
4. Nahrajte celý web na hosting **včetně** `api/config.php`.

`api/config.php` obsahuje heslo, proto se **neukládá do Gitu** (je v `.gitignore`)
a soubor `api/.htaccess` zakazuje jeho stažení z prohlížeče.

## 3. Doručitelnost (aby poptávky nepadaly do spamu)

Správce domény by měl mít pro `kostera.cz` nastavené **SPF**, **DKIM** a ideálně **DMARC**
pro server, přes který se odesílá. U běžných hostingů je to nastavené automaticky,
pokud odesíláte přes jejich SMTP a odesílatel (`from_email`) je na doméně kostera.cz.

## 4. Test po spuštění

1. Odešlete z webu zkušební poptávku na svůj e-mail.
2. Ověřte, že dorazila na `kostera@kostera.cz` a že „Odpovědět“ míří na zákazníka.
3. Ověřte, že zákazník dostal potvrzení.

Pokud něco nefunguje, zapněte v `api/config.php` `'debug' => true` – průběh komunikace se SMTP
serverem se zapíše do chybového logu PHP na hostingu. Po vyřešení debug zase vypněte.

## Co skript dělá

- kontroluje povinná pole (jméno, e-mail, zpráva) a formát e-mailu a telefonu,
- chrání proti spamu: skryté pole pro roboty, minimální doba vyplnění 3 s,
  max. 5 poptávek z jedné IP adresy za 10 minut, odesílat smí jen web firmy,
- poptávku pošle firmě s předmětem „Poptávka: výrobek – firma“ a „Odpovědět“ míří na zákazníka,
- zákazníkovi pošle krátké potvrzení (bez kopie jeho zprávy, aby formulář nešel zneužít k rozesílání spamu),
- funguje i bez JavaScriptu (po odeslání přesměruje zpět na web s potvrzením),
- když server není dostupný, web zákazníkovi nabídne odeslat poptávku e-mailem
  s předvyplněným obsahem, takže se žádná poptávka neztratí.

Knihovna PHPMailer 6.9.3 (`api/lib/PHPMailer`, licence LGPL 2.1).

---

# Administrace kariéry – kostera.cz/admin/

Zákazník si sám upravuje stránku Kariéra: volné pozice (přidat, upravit, skrýt, smazat, seřadit),
úvodní text, kontaktní e-mail, body „Proč pracovat u nás“ a text v červeném pruhu.
Změny se na webu projeví ihned po kliknutí na **Uložit**.

## Zprovoznění (jednorázově, správce webu)

1. Hosting musí mít **PHP 8.0 nebo novější** (stejně jako formulář poptávky).
2. Zvolte heslo (aspoň 12 znaků) a vytvořte jeho otisk:
   ```bash
   php -r "echo password_hash('zvolene-heslo', PASSWORD_DEFAULT), PHP_EOL;"
   ```
   Výsledek (začíná `$2y$`) vložte do `api/config.php` jako `'admin_heslo_hash' => '...'`.
   Samotné heslo předejte zákazníkovi bezpečně (ne e-mailem spolu s adresou).
3. Složka `api/data/` musí být **zapisovatelná** pro PHP (vytvoří se sama při prvním uložení;
   když to hosting nedovolí, vytvořte ji ručně s právy 750 nebo 770).
4. Otevřete `https://www.kostera.cz/admin/`, přihlaste se a jednou uložte.

## Jak to funguje

- Data se ukládají do `api/data/kariera.json`. Stránka `kariera.html` si je při načtení vezme přes
  `api/kariera.php`. Skryté pozice se na web vůbec neposílají.
- Dokud v administraci nikdo nic neuložil, platí výchozí data z `assets/kariera.json`
  (ta jsou zároveň přímo v HTML stránky – zobrazí se i bez PHP, např. na náhledu na Vercelu).
- Každé uložení si pamatuje předchozí stav: posledních 20 verzí je v `api/data/zalohy/`
  a v administraci je lze obnovit (sekce „Předchozí verze“).
- **Pozor při nahrávání nové verze webu:** složku `api/data/` nepřepisujte ani nemažte –
  jsou v ní úpravy zákazníka (v Gitu není, je v `.gitignore`).

## Google Jobs

Pozice se zobrazují i ve vyhledávání práce na Googlu (strukturovaná data JobPosting na stránce Kariéra).
U pozice stačí vybrat **typ úvazku**; datum zveřejnění se doplní samo při prvním uložení
(inzerát platí 90 dní od zveřejnění – pak ho stačí znovu uložit s novým datem).
Vzorové pozice s názvem v hranatých závorkách […] se Googlu neposílají.
Kontrola: https://search.google.com/test/rich-results (adresa stránky Kariéra).

## Zabezpečení

- Přihlášení heslem (uložený je jen otisk), po 5 chybných pokusech z jedné IP blokace na 15 minut.
- Ochrana formulářů proti podvržení (CSRF token), odhlášení po 2 hodinách nečinnosti.
- Administrace je skrytá před vyhledávači (`noindex`, `robots.txt`).
- Doporučení: provozovat jen přes HTTPS (přesměrování je v kořenovém `.htaccess`).
