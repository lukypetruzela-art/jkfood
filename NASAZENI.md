# Nasazení webu na hosting (kostera.cz nebo zkušební test.kostera.cz)

## Co musí hosting umět

| Požadavek | Proč |
|---|---|
| **PHP 8.0 nebo novější** | poptávkový formulář a administrace kariéry |
| **Webový server Apache** se zapnutým `.htaccess` (`AllowOverride All`), moduly `mod_rewrite` a `mod_headers` | přesměrování 542 adres starého webu, HTTPS, zabezpečení složky `api/`, ukládání do mezipaměti |
| **HTTPS certifikát** (např. Let's Encrypt) pro `www.kostera.cz`, `kostera.cz`, případně `test.kostera.cz` | zabezpečené připojení, přihlášení do administrace |
| **Odesílání e-mailů přes SMTP**: schránka `web@kostera.cz` (nebo jiná na doméně) + server, port, heslo | poptávky z formuláře chodí e-mailem |
| **SPF a DKIM** záznamy v DNS pro odesílající schránku | aby poptávky nepadaly do spamu |
| **Zápis PHP do složky `api/data/`** | administrace kariéry tam ukládá data a zálohy |
| Přístup přes **FTP/SFTP** (nebo Git) | nahrání souborů |
| Databáze **není potřeba** | |

Pokud hosting běží na **nginx** místo Apache, je potřeba převést pravidla z `.htaccess` do konfigurace serveru (správce hostingu).

## Rychlá kontrola hostingu

Soubor `tools/kontrola-hostingu.php` nahrajte spolu s webem do kořenové složky a otevřete
`https://…/kontrola-hostingu.php`. Ukáže, co hosting splňuje (✅), co je potřeba opravit (❌ s návodem)
a co ověřit ručně (⚠️): verzi PHP, rozšíření, .htaccess, HTTPS, zápis do `api/data/`, spojení se SMTP.
**Po kontrole soubor smažte.**

## Postup

1. **Nahrát soubory** do kořenové složky webu (u zkušební verze do složky subdomény). Nenahrávat:
   `tools/`, `podklady/`, `.git/`, `vercel.json`, soubory `*.md` (návody).
2. **Nastavení:** zkopírovat `api/config.example.php` jako `api/config.php` a vyplnit:
   - údaje SMTP (`smtp_host`, `smtp_port`, `smtp_secure`, `smtp_user`, `smtp_pass`, `from_email`, `to`),
   - `allowed_origins` – adresy, ze kterých smí formulář odesílat (u zkušební verze přidat `https://test.kostera.cz`),
   - `admin_heslo_hash` – otisk hesla do administrace. Nejjednodušeji: otevřít `/admin/`, dokud heslo není nastavené,
     stránka nabídne **Vytvořit otisk hesla**; výsledek vložit do `config.php`. (Nebo příkazem
     `php -r "echo password_hash('heslo', PASSWORD_DEFAULT), PHP_EOL;"`.)
3. **Práva:** složka `api/data/` zapisovatelná pro PHP (vytvoří se sama; jinak ručně s právy 750/770).
4. **Test** (viz níže).
5. **Ostrý provoz:** nasměrovat doménu, ověřit HTTPS, pak postup v `SEO.md` (Search Console, Seznam, Bing…).

Při každém dalším nahrání nové verze webu **nepřepisovat** `api/config.php` a `api/data/` (heslo, SMTP a úpravy kariéry).

## Zkušební verze (test.kostera.cz)

- `.htaccess` je připravený: zkušební subdoména zůstane bez „www“, jen se přesměruje na HTTPS.
- Aby ji nenašly vyhledávače a neviděl ji kdokoli, doporučujeme ji zaheslovat – přidat na začátek `.htaccess`
  **jen na zkušební verzi** (soubor `.htpasswd` vytvoří správce hostingu, obvykle v administraci hostingu):
  ```apache
  AuthType Basic
  AuthName "Náhled webu J.K.FOOD"
  AuthUserFile /cesta/mimo/web/.htpasswd
  Require valid-user
  Header set X-Robots-Tag "noindex, nofollow"
  ```

## Kontrola po nahrání

- [ ] `https://…/` – úvod se načte, fotky, písma, video
- [ ] `http://kostera.cz/sortiment.html` → přesměruje na `https://www.kostera.cz/sortiment.html`
- [ ] stará adresa, např. `/nabidka/korenici-smesi_c3` → `/sortiment-korenici-smesi.html`
- [ ] `https://…/api/config.php` → **403 Forbidden** (nastavení s heslem nesmí jít otevřít)
- [ ] formulář: odeslat zkušební poptávku → dorazí e-mail (a potvrzení odesílateli)
- [ ] `https://…/admin/` – přihlášení, úprava pozice, Uložit → změna je vidět na `/kariera.html`
- [ ] `https://…/api/data/kariera.json` → **403 Forbidden**
- [ ] anglická verze `/en/`, stránka 404 (libovolná neexistující adresa)
