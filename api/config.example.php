<?php
/*
 * Nastavení odesílání poptávek.
 *
 * 1) Zkopírujte tento soubor jako  api/config.php  (ten se NEUKLÁDÁ do Gitu – obsahuje heslo).
 * 2) Doplňte údaje k SMTP (dodá správce hostingu / IT).
 * 3) Hotovo – formulář na webu začne posílat poptávky.
 */
return [
    // --- SMTP server pro odesílání ---
    'smtp_host'     => 'smtp.example.cz',      // např. smtp.wedos.net, smtp.forpsi.com, smtp.active24.com
    'smtp_port'     => 587,                    // 587 = STARTTLS (doporučeno), 465 = SSL
    'smtp_secure'   => 'tls',                  // 'tls' pro port 587, 'ssl' pro port 465, '' bez šifrování
    'smtp_user'     => 'web@kostera.cz',       // přihlašovací jméno (obvykle celá e-mailová adresa)
    'smtp_pass'     => '',                     // heslo k této schránce

    // --- odesílatel a příjemci ---
    'from_email'    => 'web@kostera.cz',       // musí být schránka na doméně kostera.cz (kvůli SPF/DKIM)
    'from_name'     => 'Web J.K.FOOD',
    'to'            => ['kostera@kostera.cz'], // kam chodí poptávky (může být víc adres)

    // --- potvrzení zákazníkovi ---
    'send_confirmation' => true,               // zákazník dostane krátké potvrzení, že poptávka dorazila

    // --- zabezpečení ---
    // Domény, ze kterých smí formulář odesílat (ochrana proti zneužití skriptu z cizích webů).
    'allowed_origins' => ['https://www.kostera.cz', 'https://kostera.cz'],
    // Max. počet odeslání z jedné IP adresy za 10 minut.
    'rate_limit'    => 5,

    // Při ladění zapněte – do logu se zapíše podrobný průběh SMTP komunikace.
    'debug'         => false,
];
