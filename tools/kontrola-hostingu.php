<?php
/*
 * Kontrola hostingu pro web J.K.FOOD
 * ----------------------------------
 * 1) Nahrajte tento soubor do kořenové složky webu (vedle index.html) spolu s celým webem.
 * 2) Otevřete https://vase-domena/kontrola-hostingu.php
 * 3) Po kontrole soubor SMAŽTE (zobrazuje technické údaje o serveru).
 * Nic neukládá a nezobrazuje hesla.
 */
declare(strict_types=1);
header('Content-Type: text/html; charset=utf-8');
header('X-Robots-Tag: noindex, nofollow');
header('Cache-Control: no-store');

$root = __DIR__;
$checks = [];
function check(string $group, string $name, ?bool $ok, string $detail, string $fix = ''): void
{
    $GLOBALS['checks'][] = compact('group', 'name', 'ok', 'detail', 'fix');
}

// --- PHP
check('PHP', 'Verze PHP 8.0 nebo novější', version_compare(PHP_VERSION, '8.0.0', '>='), 'PHP ' . PHP_VERSION,
      'V administraci hostingu přepněte verzi PHP na 8.1 nebo novější.');
foreach (['mbstring' => 'práce s češtinou', 'openssl' => 'šifrované odesílání e-mailů (TLS)', 'json' => 'data kariéry',
          'filter' => 'kontrola e-mailů', 'session' => 'přihlášení do administrace', 'ctype' => 'knihovna PHPMailer'] as $ext => $why) {
    check('PHP', "Rozšíření $ext", extension_loaded($ext), $why, "Požádejte hosting o zapnutí rozšíření PHP „$ext“.");
}
check('PHP', 'Hesla (password_hash)', function_exists('password_hash'), 'administrace kariéry');
$disabled = array_map('trim', explode(',', (string) ini_get('disable_functions')));
check('PHP', 'Síťové připojení (fsockopen)', function_exists('fsockopen') && !in_array('fsockopen', $disabled, true),
      'odesílání e-mailů přes SMTP', 'Hosting má zakázanou funkci fsockopen/stream_socket_client – bez ní nejde SMTP.');

// --- server
$soft = (string) ($_SERVER['SERVER_SOFTWARE'] ?? 'neznámý');
$htaccessServer = (bool) preg_match('/apache|litespeed/i', $soft);
check('Server', 'Server podporuje .htaccess (Apache/LiteSpeed)', $htaccessServer ?: null, $soft,
      'Na nginx je potřeba převést pravidla z .htaccess do konfigurace serveru (správce hostingu).');
$https = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') || (($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https');
check('Server', 'HTTPS', $https, $https ? 'stránka je načtená přes HTTPS' : 'stránka je načtená přes HTTP',
      'Zapněte SSL certifikát (např. Let\'s Encrypt) pro doménu.');
if (function_exists('apache_get_modules')) {
    $mods = apache_get_modules();
    check('Server', 'mod_rewrite (přesměrování starých adres)', in_array('mod_rewrite', $mods, true), '', 'Požádejte hosting o zapnutí mod_rewrite.');
    check('Server', 'mod_headers (zabezpečení, mezipaměť)', in_array('mod_headers', $mods, true), '', 'Požádejte hosting o zapnutí mod_headers.');
}

// .htaccess opravdu platí? api/config.example.php musí vrátit 403
$base = ($https ? 'https' : 'http') . '://' . ($_SERVER['HTTP_HOST'] ?? 'localhost') . rtrim(dirname($_SERVER['SCRIPT_NAME'] ?? '/'), '/');
function http_status(string $url): ?int
{
    $ctx = stream_context_create(['http' => ['method' => 'HEAD', 'ignore_errors' => true, 'timeout' => 6, 'follow_location' => 0],
                                  'ssl' => ['verify_peer' => false, 'verify_peer_name' => false]]);
    $h = @get_headers($url, false, $ctx);
    return $h && preg_match('/\s(\d{3})\s/', $h[0], $m) ? (int) $m[1] : null;
}
if (is_file("$root/api/config.example.php")) {
    $st = ini_get('allow_url_fopen') ? http_status("$base/api/config.example.php") : null;
    check('Server', 'Složka api/ je zvenku zamčená (.htaccess platí)', $st === null ? null : $st === 403,
          $st === null ? 'nelze ověřit automaticky – otevřete ručně /api/config.example.php, musí být 403 Forbidden' : "odpověď $st",
          'Hosting ignoruje .htaccess (AllowOverride). Bez něj by šlo stáhnout nastavení s heslem!');
    $st2 = ini_get('allow_url_fopen') ? http_status("$base/nabidka/korenici-smesi_c3") : null;
    check('Server', 'Přesměrování starých adres', $st2 === null ? null : $st2 === 301,
          $st2 === null ? 'nelze ověřit automaticky – otevřete /nabidka/korenici-smesi_c3, musí přesměrovat na katalog' : "odpověď $st2",
          'Nefunguje mod_rewrite nebo .htaccess.');
} else {
    check('Server', 'Soubory webu', false, 'nenalezena složka api/ vedle tohoto souboru', 'Nahrajte kontrolu do kořenové složky webu.');
}

// --- zápis
$dataDir = "$root/api/data";
$created = false;
if (!is_dir($dataDir)) { $created = @mkdir($dataDir, 0750, true); }
$probe = "$dataDir/.zapis-test";
$writable = is_dir($dataDir) && @file_put_contents($probe, 'ok') !== false;
if ($writable) { @unlink($probe); }
if ($created) { @rmdir($dataDir); }
check('Zápis', 'PHP může zapisovat do api/data/', $writable, 'administrace kariéry ukládá data a zálohy',
      'Nastavte složce api/ (nebo api/data/) práva zápisu pro PHP, např. 750/770.');
check('Zápis', 'Ukládání přihlášení (session)', is_writable((string) (session_save_path() ?: sys_get_temp_dir())), 'přihlášení do administrace',
      'Hosting má nezapisovatelnou složku pro session.');

// --- nastavení a e-mail
$cfgFile = "$root/api/config.php";
if (is_file($cfgFile)) {
    $cfg = include $cfgFile;
    check('Nastavení', 'api/config.php existuje', true, '');
    check('Nastavení', 'Heslo do administrace nastavené', !empty($cfg['admin_heslo_hash']), '', 'Doplňte admin_heslo_hash (viz NASAZENI.md).');
    $host = (string) ($cfg['smtp_host'] ?? ''); $port = (int) ($cfg['smtp_port'] ?? 587);
    if ($host !== '' && $host !== 'smtp.example.cz') {
        $t = microtime(true);
        $fp = @fsockopen(($cfg['smtp_secure'] ?? '') === 'ssl' ? "ssl://$host" : $host, $port, $errno, $errstr, 8);
        check('Nastavení', "Spojení se SMTP serverem $host:$port", (bool) $fp,
              $fp ? sprintf('spojení navázáno (%d ms)', (microtime(true) - $t) * 1000) : "nelze se připojit: $errstr",
              'Ověřte server a port SMTP; některé hostingy blokují odchozí porty – zeptejte se na správný SMTP server.');
        if ($fp) { fclose($fp); }
    } else {
        check('Nastavení', 'Údaje SMTP vyplněné', false, 'smtp_host je prázdný nebo vzorový', 'Doplňte údaje k odesílání e-mailů.');
    }
    $origins = (array) ($cfg['allowed_origins'] ?? []);
    $here = ($https ? 'https' : 'http') . '://' . ($_SERVER['HTTP_HOST'] ?? '');
    check('Nastavení', 'Formulář smí odesílat z této adresy', in_array($here, $origins, true), $here,
          "Přidejte '$here' do allowed_origins v api/config.php.");
} else {
    check('Nastavení', 'api/config.php existuje', null, 'zatím není – vytvoří se zkopírováním api/config.example.php', 'Viz NASAZENI.md, krok 2.');
}

$bad = count(array_filter($checks, fn($c) => $c['ok'] === false));
$unk = count(array_filter($checks, fn($c) => $c['ok'] === null));
?>
<!DOCTYPE html>
<html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>Kontrola hostingu · J.K.FOOD</title>
<style>
body{font:16px/1.5 system-ui,sans-serif;max-width:860px;margin:32px auto;padding:0 16px;color:#1F1A19}
h1{margin:0 0 4px}h2{margin:28px 0 8px;font-size:18px}
.sum{padding:14px 18px;border-radius:12px;font-weight:600;margin:16px 0}
.ok{background:#E9F3EC;color:#1E6B3A}.bad{background:#FBE9E8;color:#A7110C}.unk{background:#FFF6DD;color:#7A5A00}
table{width:100%;border-collapse:collapse}td{padding:8px 6px;border-bottom:1px solid #EEE;vertical-align:top}
td:first-child{width:28px;font-size:18px}.d{color:#675D5B;font-size:14px}.f{color:#A7110C;font-size:14px}
.warn{margin-top:28px;padding:12px 16px;border:2px solid #A7110C;border-radius:12px}
</style></head><body>
<h1>Kontrola hostingu</h1>
<p class="d">Web J.K.FOOD · <?= htmlspecialchars(date('j. n. Y H:i')) ?></p>
<div class="sum <?= $bad ? 'bad' : ($unk ? 'unk' : 'ok') ?>">
<?= $bad ? "Hosting zatím nesplňuje $bad " . ($bad === 1 ? 'požadavek' : ($bad < 5 ? 'požadavky' : 'požadavků')) . ' – opravy jsou uvedené níže.'
        : ($unk ? 'Vše podstatné je v pořádku, ' . $unk . ' ' . ($unk === 1 ? 'bod je' : 'body jsou') . ' potřeba ověřit ručně.' : 'Hosting splňuje všechno, co web potřebuje.') ?>
</div>
<?php foreach (array_unique(array_column($checks, 'group')) as $g): ?>
<h2><?= htmlspecialchars($g) ?></h2><table>
<?php foreach ($checks as $c): if ($c['group'] !== $g) continue; ?>
<tr><td><?= $c['ok'] === true ? '✅' : ($c['ok'] === false ? '❌' : '⚠️') ?></td>
<td><b><?= htmlspecialchars($c['name']) ?></b><?php if ($c['detail']): ?><div class="d"><?= htmlspecialchars($c['detail']) ?></div><?php endif; ?>
<?php if ($c['ok'] !== true && $c['fix']): ?><div class="f">→ <?= htmlspecialchars($c['fix']) ?></div><?php endif; ?></td></tr>
<?php endforeach; ?></table>
<?php endforeach; ?>
<p class="warn"><b>Po kontrole tento soubor smažte</b> (kontrola-hostingu.php) – zobrazuje technické údaje o serveru.</p>
</body></html>
