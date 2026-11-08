<?php
/*
 * Příjem poptávek z formuláře na webu J.K.FOOD a jejich odeslání e-mailem přes SMTP.
 *
 * - Odpovídá JSONem (pro JavaScript na webu); bez JavaScriptu přesměruje zpět na web.
 * - Kontroluje pole, chrání proti spamu (skryté pole, čas vyplnění, limit na IP, povolené domény).
 * - Nastavení je v api/config.php (vzor: api/config.example.php).
 *
 * Požadavky: PHP 7.4+ (s rozšířením openssl), SMTP účet na doméně kostera.cz.
 */
declare(strict_types=1);

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception as MailException;

require __DIR__ . '/lib/PHPMailer/Exception.php';
require __DIR__ . '/lib/PHPMailer/PHPMailer.php';
require __DIR__ . '/lib/PHPMailer/SMTP.php';

const TYPES = ['Nabídku sortimentu', 'Vzorky', 'Vývoj směsi na míru', 'Něco jiného'];
const MIN_FILL_SECONDS = 3;      // rychlejší vyplnění = robot
const RATE_WINDOW = 600;         // 10 minut

$wantsJson = stripos($_SERVER['HTTP_ACCEPT'] ?? '', 'application/json') !== false;

/** Ukončí požadavek: JSON pro JavaScript, přesměrování pro formulář bez JavaScriptu. */
function respond(int $status, array $body, bool $json): void
{
    if ($json) {
        http_response_code($status);
        header('Content-Type: application/json; charset=utf-8');
        header('Cache-Control: no-store');
        echo json_encode($body, JSON_UNESCAPED_UNICODE);
    } else {
        $state = $body['ok'] ? 'odeslano' : 'chyba';
        header('Location: ../index.html?formular=' . $state . '#kontakt', true, 303);
    }
    exit;
}

/** Jednořádkový text bez řídicích znaků (ochrana hlaviček e-mailu). */
function line(string $s, int $max): string
{
    $s = trim(preg_replace('/[\x00-\x1F\x7F]+/u', ' ', $s) ?? '');
    return mb_substr($s, 0, $max);
}

/** Víceřádkový text (zpráva) – zachová odřádkování, odstraní ostatní řídicí znaky. */
function text(string $s, int $max): string
{
    $s = str_replace(["\r\n", "\r"], "\n", $s);
    $s = trim(preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]+/u', '', $s) ?? '');
    return mb_substr($s, 0, $max);
}

// ---------- základní kontroly ----------
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Allow: POST');
    respond(405, ['ok' => false, 'message' => 'Použijte formulář na webu.'], true);
}

$configFile = __DIR__ . '/config.php';
if (!is_file($configFile)) {
    error_log('[poptavka] chybí api/config.php');
    respond(500, ['ok' => false, 'message' => 'Formulář zatím není nastavený.'], $wantsJson);
}
$cfg = require $configFile;

// odesílat smí jen web firmy (prohlížeč posílá Origin u každého POST požadavku)
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if ($origin !== '' && !in_array(rtrim($origin, '/'), $cfg['allowed_origins'], true)) {
    respond(403, ['ok' => false, 'message' => 'Nepovolený původ požadavku.'], $wantsJson);
}

// ---------- data ----------
$in = $_POST;
if (stripos($_SERVER['CONTENT_TYPE'] ?? '', 'application/json') !== false) {
    $in = json_decode((string) file_get_contents('php://input'), true) ?: [];
}
$get = static fn(string $k): string => is_string($in[$k] ?? null) ? $in[$k] : '';

// ---------- ochrana proti spamu ----------
// 1) skryté pole – člověk ho nevidí a nevyplní
if ($get('web') !== '') {
    respond(200, ['ok' => true], $wantsJson);          // robotovi tváříme úspěch
}
// 2) čas vyplnění (čas načtení formuláře v ms posílá JavaScript)
$started = (int) $get('t');
if ($started > 0) {
    $elapsed = time() - intdiv($started, 1000);
    if ($elapsed < MIN_FILL_SECONDS) {
        respond(200, ['ok' => true], $wantsJson);
    }
}
// 3) limit odeslání z jedné IP adresy
$ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
$rateFile = sys_get_temp_dir() . '/jkfood-poptavka-' . hash('sha256', $ip . __DIR__);
$hits = array_filter(
    is_file($rateFile) ? (array) json_decode((string) file_get_contents($rateFile), true) : [],
    static fn($ts) => is_int($ts) && $ts > time() - RATE_WINDOW
);
if (count($hits) >= (int) $cfg['rate_limit']) {
    respond(429, ['ok' => false, 'message' => 'Odeslali jste několik poptávek za sebou. Zkuste to prosím za pár minut, nebo nám zavolejte.'], $wantsJson);
}

// ---------- kontrola polí ----------
$name    = line($get('name'), 120);
$company = line($get('company'), 160);
$email   = line($get('email'), 200);
$tel     = line($get('tel'), 40);
$type    = line($get('type'), 60);
$product = line($get('produkt'), 160);
$message = text($get('message'), 5000);

$errors = [];
if ($name === '') {
    $errors['name'] = 'Vyplňte prosím jméno.';
}
if ($email === '' || !PHPMailer::validateAddress($email)) {
    $errors['email'] = 'Zadejte prosím platný e-mail.';
}
if ($tel !== '' && !preg_match('/^[+0-9 ()\/-]{6,40}$/', $tel)) {
    $errors['tel'] = 'Telefon může obsahovat jen čísla, mezery a znak +.';
}
if ($message === '') {
    $errors['message'] = 'Napište nám prosím, o co máte zájem.';
}
if (!in_array($type, TYPES, true)) {
    $type = 'Něco jiného';
}
if ($errors) {
    respond(422, ['ok' => false, 'message' => 'Zkontrolujte prosím označená pole.', 'errors' => $errors], $wantsJson);
}

// ---------- e-mail ----------
function mailer(array $cfg): PHPMailer
{
    $m = new PHPMailer(true);
    $m->isSMTP();
    $m->Host       = $cfg['smtp_host'];
    $m->Port       = (int) $cfg['smtp_port'];
    if ($cfg['smtp_secure'] === 'ssl') {
        $m->SMTPSecure = PHPMailer::ENCRYPTION_SMTPS;       // port 465
    } elseif ($cfg['smtp_secure'] === 'tls') {
        $m->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;    // port 587
    } else {
        $m->SMTPAutoTLS = false;                            // bez šifrování (jen interní relay hostingu)
    }
    $m->SMTPAuth   = $cfg['smtp_user'] !== '';
    $m->Username   = $cfg['smtp_user'];
    $m->Password   = $cfg['smtp_pass'];
    $m->Timeout    = 15;
    $m->CharSet    = PHPMailer::CHARSET_UTF8;
    $m->Encoding   = PHPMailer::ENCODING_BASE64;
    $m->setFrom($cfg['from_email'], $cfg['from_name']);
    if (!empty($cfg['debug'])) {
        $m->SMTPDebug   = 2;
        $m->Debugoutput = static function ($str) { error_log('[poptavka smtp] ' . trim($str)); };
    }
    return $m;
}

$h = static fn(string $s): string => htmlspecialchars($s, ENT_QUOTES, 'UTF-8');
$subject = 'Poptávka: ' . ($product !== '' ? $product : $type) . ' – ' . ($company !== '' ? $company : $name);

$rows = [
    'Jméno'      => $name,
    'Firma'      => $company,
    'E-mail'     => $email,
    'Telefon'    => $tel,
    'Zájem o'    => $type,
    'Výrobek'    => $product,
];
$plain = "Nová poptávka z webu kostera.cz\n\n";
$html  = '<div style="font-family:Arial,sans-serif;font-size:15px;color:#1F1A19">'
       . '<h2 style="color:#A7110C;margin:0 0 16px">Nová poptávka z webu</h2><table cellpadding="6" style="border-collapse:collapse">';
foreach ($rows as $label => $value) {
    if ($value === '') {
        continue;
    }
    $plain .= $label . ':' . str_repeat(' ', max(1, 11 - mb_strlen($label))) . "$value\n";
    $cell = $label === 'E-mail' ? '<a href="mailto:' . $h($value) . '">' . $h($value) . '</a>'
          : ($label === 'Telefon' ? '<a href="tel:' . $h(preg_replace('/[^+0-9]/', '', $value)) . '">' . $h($value) . '</a>' : $h($value));
    $html .= '<tr><td style="color:#675D5B;padding-right:16px">' . $h($label) . '</td><td><b>' . $cell . '</b></td></tr>';
}
$plain .= "\nZpráva:\n$message\n\n—\nOdpovědět můžete přímo na tento e-mail.";
$html  .= '</table><p style="color:#675D5B;margin:20px 0 6px">Zpráva:</p>'
        . '<div style="white-space:pre-wrap;border-left:3px solid #A7110C;padding:8px 14px;background:#FBF4F3">' . $h($message) . '</div>'
        . '<p style="color:#675D5B;font-size:13px;margin-top:20px">Odpovědět můžete přímo na tento e-mail.</p></div>';

try {
    $m = mailer($cfg);
    foreach ($cfg['to'] as $to) {
        $m->addAddress($to);
    }
    $m->addReplyTo($email, $name);
    $m->Subject = $subject;
    $m->isHTML(true);
    $m->Body    = $html;
    $m->AltBody = $plain;
    $m->send();
} catch (MailException $e) {
    error_log('[poptavka] odeslání selhalo: ' . $e->getMessage());
    respond(502, ['ok' => false, 'message' => 'Poptávku se nepodařilo odeslat. Zkuste to prosím znovu, nebo nám napište na kostera@kostera.cz.'], $wantsJson);
}

// započítat do limitu až úspěšné odeslání
$hits[] = time();
@file_put_contents($rateFile, json_encode(array_values($hits)), LOCK_EX);

// potvrzení zákazníkovi – záměrně bez kopie jeho zprávy, aby formulář nešel zneužít k rozesílání spamu
if (!empty($cfg['send_confirmation'])) {
    try {
        $c = mailer($cfg);
        $c->addAddress($email, $name);
        $c->addReplyTo($cfg['to'][0], 'J.K.FOOD');
        $c->Subject = 'Vaše poptávka dorazila – J.K.FOOD';
        $c->isHTML(true);
        $c->Body = '<div style="font-family:Arial,sans-serif;font-size:15px;color:#1F1A19">'
                 . '<p>Dobrý den,</p><p>děkujeme za Vaši poptávku. Dorazila v pořádku a ozveme se Vám co nejdříve, obvykle do jednoho pracovního dne.</p>'
                 . '<p>Pokud spěcháte, volejte <a href="tel:+420556310205">+420 556 310 205</a>.</p>'
                 . '<p>S pozdravem<br><b>Jaroslav Kostera, J.K.FOOD s.r.o.</b><br>Větřkovice 243, 747 43 Větřkovice</p></div>';
        $c->AltBody = "Dobrý den,\n\nděkujeme za Vaši poptávku. Dorazila v pořádku a ozveme se Vám co nejdříve, obvykle do jednoho pracovního dne.\n"
                    . "Pokud spěcháte, volejte +420 556 310 205.\n\nS pozdravem\nJaroslav Kostera, J.K.FOOD s.r.o.\nVětřkovice 243, 747 43 Větřkovice";
        $c->send();
    } catch (MailException $e) {
        error_log('[poptavka] potvrzení zákazníkovi selhalo: ' . $e->getMessage());   // poptávka už odešla, zákazníka tím nestrašíme
    }
}

respond(200, ['ok' => true], $wantsJson);
