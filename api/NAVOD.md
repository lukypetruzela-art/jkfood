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
