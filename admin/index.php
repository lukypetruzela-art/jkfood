<?php
/*
 * Administrace stránky Kariéra – kostera.cz/admin/
 * Přihlášení heslem (hash v api/config.php → 'admin_heslo_hash'), úpravy se na webu projeví ihned.
 * Návod: NASAZENI.md a api/NAVOD.md, část „Administrace kariéry“.
 */
declare(strict_types=1);

require __DIR__ . '/../api/lib/kariera-data.php';

header('Content-Type: text/html; charset=utf-8');
header('X-Frame-Options: DENY');
header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: same-origin');
header('X-Robots-Tag: noindex, nofollow');
header('Cache-Control: no-store');
header("Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none'; form-action 'self'");

$cfgFile = __DIR__ . '/../api/config.php';
$cfg = is_file($cfgFile) ? (require $cfgFile) : [];
$hash = is_array($cfg) ? (string) ($cfg['admin_heslo_hash'] ?? '') : '';
$newHash = '';

$https = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') || (($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https');
session_name('jkadmin');
session_set_cookie_params(['lifetime' => 0, 'path' => '/admin/', 'secure' => $https, 'httponly' => true, 'samesite' => 'Strict']);
session_start();

const IDLE = 7200;                       // odhlášení po 2 hodinách nečinnosti
const MAX_FAILS = 5;                     // max. chybných pokusů o přihlášení za 15 minut z jedné IP

function h(string $s): string { return htmlspecialchars($s, ENT_QUOTES, 'UTF-8'); }
function csrf(): string { return $_SESSION['csrf'] ??= bin2hex(random_bytes(32)); }
function csrf_ok(): bool { return is_string($_POST['csrf'] ?? null) && hash_equals(csrf(), $_POST['csrf']); }

$failFile = sys_get_temp_dir() . '/jkfood-admin-' . hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '') . __DIR__);
$fails = array_filter(is_file($failFile) ? (array) json_decode((string) file_get_contents($failFile), true) : [], fn($t) => $t > time() - 900);

$logged = !empty($_SESSION['ok']) && ($_SESSION['seen'] ?? 0) > time() - IDLE;
if (!$logged) {
    unset($_SESSION['ok']);
}
$msg = $_SESSION['flash'] ?? null;
unset($_SESSION['flash']);
$errors = [];
$action = $_POST['action'] ?? '';

function redirect(string $flash): void
{
    $_SESSION['flash'] = $flash;
    header('Location: ./', true, 303);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!csrf_ok()) {
        $errors[] = 'Platnost formuláře vypršela. Obnovte stránku a zkuste to znovu.';
    } elseif ($action === 'hash' && $hash === '') {
        // jen dokud není heslo nastavené: vytvoří otisk k vložení do api/config.php (nic neukládá)
        $pw = (string) ($_POST['nove_heslo'] ?? '');
        if (mb_strlen($pw) < 12) {
            $errors[] = 'Heslo musí mít aspoň 12 znaků.';
        } else {
            $newHash = password_hash($pw, PASSWORD_DEFAULT);
        }
    } elseif ($action === 'login') {
        if ($hash === '') {
            $errors[] = 'Administrace zatím nemá nastavené heslo (viz návod).';
        } elseif (count($fails) >= MAX_FAILS) {
            $errors[] = 'Příliš mnoho pokusů. Zkuste to prosím za 15 minut.';
        } elseif (password_verify((string) ($_POST['heslo'] ?? ''), $hash)) {
            session_regenerate_id(true);
            $_SESSION['ok'] = true;
            $_SESSION['seen'] = time();
            @unlink($failFile);
            redirect('Přihlášení proběhlo úspěšně.');
        } else {
            $fails[] = time();
            @file_put_contents($failFile, json_encode(array_values($fails)), LOCK_EX);
            usleep(400000);
            $errors[] = 'Nesprávné heslo.';
        }
    } elseif ($action === 'logout') {
        $_SESSION = [];
        session_destroy();
        session_start();
        redirect('Byli jste odhlášeni.');
    } elseif (!$logged) {
        $errors[] = 'Přihlášení vypršelo. Přihlaste se prosím znovu – neuložené změny je potřeba zadat znovu.';
    } elseif ($action === 'save') {
        $in = json_decode((string) ($_POST['data'] ?? ''), true);
        [$data, $errors] = kariera_normalize(is_array($in) ? $in : []);
        if (!$errors) {
            try {
                kariera_save($data);
                redirect('Uloženo. Změny jsou na webu ihned.');
            } catch (Throwable $e) {
                $errors[] = $e->getMessage();
            }
        }
        $draft = $data;   // při chybě zůstanou zadané údaje ve formuláři
    } elseif ($action === 'restore') {
        try {
            redirect(kariera_restore((string) ($_POST['file'] ?? '')) ? 'Předchozí verze byla obnovena.' : 'Zálohu se nepodařilo obnovit.');
        } catch (Throwable $e) {
            $errors[] = $e->getMessage();
        }
    }
}
if ($logged) {
    $_SESSION['seen'] = time();
}
$data = $draft ?? kariera_load();
$backups = $logged ? array_slice(kariera_backups(), 0, 8) : [];
?>
<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Administrace kariéry · J.K.FOOD</title>
<link rel="icon" href="../favicon.ico">
<style>
:root{--red:#A7110C;--ink:#1F1A19;--muted:#675D5B;--line:#E6DCDB;--blush:#FBF4F3;--ok:#1E6B3A}
*{box-sizing:border-box}
body{margin:0;font:16px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:var(--ink);background:#F6F2F1}
a{color:var(--red)}
.top{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
.top .in{max-width:980px;margin:0 auto;padding:12px 20px;display:flex;align-items:center;gap:16px;justify-content:space-between;flex-wrap:wrap}
.top b{font-size:18px}.top b span{color:var(--red)}
.wrap{max-width:980px;margin:0 auto;padding:24px 20px 120px}
h1{font-size:28px;margin:0 0 4px}h2{font-size:20px;margin:0 0 14px}
.lead{color:var(--muted);margin:0 0 24px}
.card{background:#fff;border:1px solid var(--line);border-radius:18px;padding:22px;margin-bottom:18px}
label{display:block;font-weight:600;font-size:14px;margin:14px 0 6px}
label small{font-weight:400;color:var(--muted)}
input[type=text],input[type=email],input[type=tel],input[type=password],input[type=date],select,textarea{width:100%;font:inherit;padding:10px 12px;border:1.5px solid var(--line);border-radius:10px;background:#fff}
input:focus,textarea:focus{outline:2px solid var(--red);outline-offset:1px;border-color:var(--red)}
textarea{min-height:96px;resize:vertical}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:0 16px}
@media (max-width:700px){.grid{grid-template-columns:1fr}}
.btn{display:inline-flex;align-items:center;gap:6px;font:inherit;font-weight:600;border:1.5px solid var(--ink);background:#fff;color:var(--ink);padding:9px 16px;border-radius:999px;cursor:pointer;text-decoration:none}
.btn:hover{background:var(--ink);color:#fff}
.btn.red{background:var(--red);border-color:var(--red);color:#fff}.btn.red:hover{background:#8E0E0A}
.btn.sm{padding:6px 12px;font-size:14px}
.btn.del{border-color:#C9B8B6;color:var(--red)}.btn.del:hover{background:var(--red);color:#fff;border-color:var(--red)}
.pos{border-left:4px solid var(--red)}
.pos.off{border-left-color:#BDB3B1;background:#FBFAFA}
.pos-head{display:flex;align-items:center;gap:10px;flex-wrap:wrap;justify-content:space-between}
.pos-head h3{margin:0;font-size:18px}
.tools{display:flex;gap:6px;flex-wrap:wrap}
.switch{display:inline-flex;align-items:center;gap:8px;font-weight:600;font-size:14px;margin:0;cursor:pointer}
.switch input{width:18px;height:18px;accent-color:var(--red)}
.badge{font-size:12px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;padding:3px 8px;border-radius:999px;background:#E9F3EC;color:var(--ok)}
.off .badge{background:#EEE;color:#777}
.msg{padding:12px 16px;border-radius:12px;margin-bottom:18px;font-weight:600}
.msg.ok{background:#E9F3EC;color:var(--ok)}.msg.err{background:#FBE9E8;color:var(--red)}
.msg ul{margin:6px 0 0;padding-left:20px;font-weight:400}
.bar{position:fixed;left:0;right:0;bottom:0;background:#fff;border-top:1px solid var(--line);z-index:5}
.bar .in{max-width:980px;margin:0 auto;padding:12px 20px;display:flex;gap:12px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.bar span{color:var(--muted);font-size:14px}
.dirty .bar span{color:var(--red);font-weight:600}
.why-item{display:grid;grid-template-columns:1fr 2fr auto;gap:10px;align-items:end;margin-top:8px}
@media (max-width:700px){.why-item{grid-template-columns:1fr}}
.login{max-width:380px;margin:12vh auto}
.backups li{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:6px 0;border-bottom:1px solid var(--line)}
.backups ul{list-style:none;margin:0;padding:0}
details summary{cursor:pointer;font-weight:600}
.help{font-size:14px;color:var(--muted)}
</style>
</head>
<body>
<?php if (!$logged): ?>
<div class="wrap">
  <form class="card login" method="post" action="./">
    <h1>Administrace kariéry</h1>
    <p class="lead">J.K.FOOD · úpravy volných pozic na webu</p>
    <?php if ($msg): ?><div class="msg ok"><?= h($msg) ?></div><?php endif; ?>
    <?php if ($errors): ?><div class="msg err"><?= h(implode(' ', $errors)) ?></div><?php endif; ?>
    <?php if ($hash === ''): ?>
      <div class="msg err">Heslo zatím není nastavené. Správce webu ho nastaví podle návodu v souboru NASAZENI.md.</div>
      <?php if (!empty($newHash)): ?>
        <p class="help">Otisk hesla – zkopírujte ho do <b>api/config.php</b> jako <code>'admin_heslo_hash' =&gt; '…'</code>:</p>
        <input type="text" readonly value="<?= h($newHash) ?>" onclick="this.select()">
      <?php else: ?>
        <label for="nove_heslo">Zvolte heslo pro administraci <small>(aspoň 12 znaků)</small></label>
        <input id="nove_heslo" type="password" name="nove_heslo" autocomplete="new-password" minlength="12">
        <p><button class="btn" type="submit" name="action" value="hash" formnovalidate>Vytvořit otisk hesla</button></p>
        <p class="help">Heslo se nikam neuloží – vznikne jen otisk, který správce vloží do nastavení.</p>
      <?php endif; ?>
    <?php endif; ?>
    <?php if ($hash !== ''): ?><label for="heslo">Heslo</label><?php endif; ?>
    <?php if ($hash !== ''): ?><input id="heslo" type="password" name="heslo" autocomplete="current-password" required autofocus><?php endif; ?>
    <input type="hidden" name="csrf" value="<?= h(csrf()) ?>">
    <?php if ($hash !== ''): ?><p><button class="btn red" type="submit" name="action" value="login">Přihlásit</button></p><?php endif; ?>
  </form>
</div>
<?php else: ?>
<header class="top"><div class="in">
  <b><span>J.K.FOOD</span> · Administrace kariéry</b>
  <div class="tools">
    <a class="btn sm" href="../kariera.html" target="_blank" rel="noopener">Zobrazit stránku Kariéra ↗</a>
    <form method="post" action="./"><input type="hidden" name="csrf" value="<?= h(csrf()) ?>"><button class="btn sm" name="action" value="logout">Odhlásit</button></form>
  </div>
</div></header>

<main class="wrap">
  <h1>Kariéra</h1>
  <p class="lead">Upravte texty a volné pozice a klikněte na <b>Uložit</b>. Změny se na webu projeví ihned. Pozici, kterou nechcete smazat, můžete jen skrýt.</p>
  <?php if ($msg): ?><div class="msg ok"><?= h($msg) ?></div><?php endif; ?>
  <?php if ($errors): ?><div class="msg err">Neuloženo – opravte prosím:<ul><?php foreach ($errors as $e): ?><li><?= h($e) ?></li><?php endforeach; ?></ul></div><?php endif; ?>

  <form id="f" method="post" action="./">
    <input type="hidden" name="csrf" value="<?= h(csrf()) ?>">
    <input type="hidden" name="action" value="save">
    <input type="hidden" name="data" id="data">

    <section class="card">
      <h2>Volné pozice</h2>
      <div id="positions"></div>
      <button type="button" class="btn" id="addPos">+ Přidat pozici</button>
    </section>

    <section class="card">
      <h2>Texty stránky</h2>
      <label for="intro">Úvodní text pod nadpisem</label>
      <textarea id="intro" data-k="intro" maxlength="600"></textarea>
      <label for="kontakt_email">Kontaktní e-mail pro životopisy <small>(použije se u pozic, které nemají vlastní)</small></label>
      <input id="kontakt_email" type="email" data-k="kontakt_email" maxlength="200" required>
      <label for="dalsi">Text v červeném pruhu „Nenašli jste svou pozici?“</label>
      <textarea id="dalsi" data-k="dalsi" maxlength="600"></textarea>
    </section>

    <section class="card">
      <h2>Proč pracovat u nás</h2>
      <div id="why"></div>
      <button type="button" class="btn sm" id="addWhy">+ Přidat bod</button>
    </section>
  </form>

  <?php if ($backups): ?>
  <section class="card backups">
    <details>
      <summary>Předchozí verze (obnovení)</summary>
      <p class="help">Každé uložení si pamatuje předchozí stav. Obnovením se vrátí celá stránka Kariéra do dané verze.</p>
      <ul>
      <?php foreach ($backups as $b): ?>
        <li><span><?= h(date('j. n. Y H:i', $b['time'])) ?></span>
          <form method="post" action="./" onsubmit="return confirm('Obnovit verzi z <?= h(date('j. n. Y H:i', $b['time'])) ?>? Současný stav se uloží do záloh.')">
            <input type="hidden" name="csrf" value="<?= h(csrf()) ?>"><input type="hidden" name="file" value="<?= h($b['file']) ?>">
            <button class="btn sm" name="action" value="restore">Obnovit</button>
          </form></li>
      <?php endforeach; ?>
      </ul>
    </details>
  </section>
  <?php endif; ?>
</main>

<div class="bar"><div class="in"><span id="state">Vše uloženo</span><button class="btn red" form="f" type="submit">Uložit</button></div></div>

<template id="tplPos">
  <div class="card pos">
    <div class="pos-head">
      <h3 data-title>Nová pozice</h3>
      <div class="tools">
        <label class="switch"><input type="checkbox" data-f="aktivni" checked> Zobrazit na webu</label>
        <span class="badge" data-badge>Na webu</span>
        <button type="button" class="btn sm" data-move="-1" title="Posunout výš">↑</button>
        <button type="button" class="btn sm" data-move="1" title="Posunout níž">↓</button>
        <button type="button" class="btn sm del" data-del>Smazat</button>
      </div>
    </div>
    <label>Název pozice</label>
    <input type="text" data-f="nazev" maxlength="120" required placeholder="např. Operátor/ka výroby">
    <div class="grid">
      <div><label>Typ úvazku <small>(pro vyhledávání práce na Googlu)</small></label>
        <select data-f="uvazek"><option value="FULL_TIME">Plný úvazek (HPP)</option><option value="PART_TIME">Zkrácený úvazek</option><option value="TEMPORARY">Brigáda / dočasně (DPP, DPČ)</option><option value="CONTRACTOR">Spolupráce na IČ</option><option value="INTERN">Praxe / stáž</option><option value="OTHER">Jiné</option></select></div>
      <div><label>Zveřejněno <small>(vyplní se samo při uložení)</small></label><input type="date" data-f="zverejneno"></div>
    </div>
    <label>Štítky <small>(každý na nový řádek – úvazek, místo, nástup…)</small></label>
    <textarea data-f="stitky" rows="3" placeholder="HPP&#10;Větřkovice&#10;nástup ihned"></textarea>
    <div class="grid">
      <div><label>Nabízíme <small>(každý bod na nový řádek)</small></label><textarea data-f="nabizime" rows="5"></textarea></div>
      <div><label>Požadujeme <small>(každý bod na nový řádek)</small></label><textarea data-f="pozadujeme" rows="5"></textarea></div>
    </div>
    <label>Náplň práce <small>(každý bod na nový řádek)</small></label>
    <textarea data-f="naplne" rows="4"></textarea>
    <div class="grid">
      <div><label>E-mail pro tuto pozici <small>(nepovinné)</small></label><input type="email" data-f="kontakt_email" maxlength="200"></div>
      <div><label>Telefon pro tuto pozici <small>(nepovinné)</small></label><input type="tel" data-f="kontakt_tel" maxlength="30"></div>
    </div>
  </div>
</template>
<template id="tplWhy">
  <div class="why-item">
    <div><label>Nadpis</label><input type="text" data-w="nadpis" maxlength="80"></div>
    <div><label>Text</label><input type="text" data-w="text" maxlength="400"></div>
    <button type="button" class="btn sm del" data-delwhy>Smazat</button>
  </div>
</template>

<script>
(() => {
  const DATA = <?= json_encode($data, JSON_UNESCAPED_UNICODE | JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT) ?>;
  const LISTS = ['stitky', 'nabizime', 'pozadujeme', 'naplne'];
  const $ = s => document.querySelector(s);
  const posBox = $('#positions'), whyBox = $('#why');
  let dirty = <?= $errors ? 'true' : 'false' ?>;
  const mark = () => { dirty = true; document.body.classList.add('dirty'); $('#state').textContent = 'Neuložené změny'; };
  if (dirty) mark();

  function refresh(card) {
    const name = card.querySelector('[data-f="nazev"]').value.trim();
    const on = card.querySelector('[data-f="aktivni"]').checked;
    card.querySelector('[data-title]').textContent = name || 'Nová pozice';
    card.querySelector('[data-badge]').textContent = on ? 'Na webu' : 'Skryto';
    card.classList.toggle('off', !on);
  }
  function addPos(p = {}, focus = false) {
    const card = $('#tplPos').content.firstElementChild.cloneNode(true);
    card.querySelectorAll('[data-f]').forEach(el => {
      const k = el.dataset.f, v = p[k];
      if (k === 'aktivni') el.checked = v !== false;
      else if (k === 'uvazek') el.value = v || 'FULL_TIME';
      else el.value = LISTS.includes(k) ? (v || []).join('\n') : (v || '');
    });
    card.addEventListener('input', () => refresh(card));
    card.addEventListener('change', () => refresh(card));
    card.querySelector('[data-del]').addEventListener('click', () => {
      const n = card.querySelector('[data-f="nazev"]').value.trim() || 'tuto pozici';
      if (confirm('Opravdu smazat „' + n + '“? (Pokud ji chcete jen dočasně schovat, odškrtněte „Zobrazit na webu“.)')) { card.remove(); mark(); }
    });
    card.querySelectorAll('[data-move]').forEach(b => b.addEventListener('click', () => {
      const sib = +b.dataset.move < 0 ? card.previousElementSibling : card.nextElementSibling;
      if (!sib) return;
      +b.dataset.move < 0 ? posBox.insertBefore(card, sib) : posBox.insertBefore(sib, card);
      mark(); b.focus();
    }));
    posBox.appendChild(card); refresh(card);
    if (focus) { card.scrollIntoView({ behavior: 'smooth', block: 'center' }); card.querySelector('[data-f="nazev"]').focus(); }
  }
  function addWhy(w = {}) {
    const row = $('#tplWhy').content.firstElementChild.cloneNode(true);
    row.querySelector('[data-w="nadpis"]').value = w.nadpis || '';
    row.querySelector('[data-w="text"]').value = w.text || '';
    row.querySelector('[data-delwhy]').addEventListener('click', () => { row.remove(); mark(); });
    whyBox.appendChild(row);
  }

  (DATA.pozice || []).forEach(p => addPos(p));
  (DATA.proc || []).forEach(w => addWhy(w));
  document.querySelectorAll('[data-k]').forEach(el => el.value = DATA[el.dataset.k] || '');
  $('#addPos').addEventListener('click', () => { addPos({}, true); mark(); });
  $('#addWhy').addEventListener('click', () => { addWhy(); mark(); });
  $('#f').addEventListener('input', mark);

  $('#f').addEventListener('submit', () => {
    const out = {};
    document.querySelectorAll('[data-k]').forEach(el => out[el.dataset.k] = el.value);
    out.pozice = [...posBox.children].map(card => {
      const p = {};
      card.querySelectorAll('[data-f]').forEach(el => {
        const k = el.dataset.f;
        p[k] = k === 'aktivni' ? el.checked : LISTS.includes(k) ? el.value.split('\n').map(s => s.trim()).filter(Boolean) : el.value.trim();
      });
      return p;
    });
    out.proc = [...whyBox.children].map(r => ({ nadpis: r.querySelector('[data-w="nadpis"]').value, text: r.querySelector('[data-w="text"]').value }));
    $('#data').value = JSON.stringify(out);
    dirty = false;
  });
  addEventListener('beforeunload', e => { if (dirty) { e.preventDefault(); e.returnValue = ''; } });
})();
</script>
<?php endif; ?>
</body>
</html>
