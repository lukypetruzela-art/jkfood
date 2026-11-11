<?php
/*
 * Data stránky Kariéra – společné pro api/kariera.php (web) a admin/ (administrace).
 *
 *  - api/data/kariera.json      aktuální data (vytvoří je administrace při prvním uložení)
 *  - api/data/zalohy/*.json     posledních 20 verzí (pro obnovení)
 *  - assets/kariera.json        výchozí data z webu, používají se, dokud nikdo nic neuložil
 */
declare(strict_types=1);

const KARIERA_DIR = __DIR__ . '/../data';
const KARIERA_FILE = KARIERA_DIR . '/kariera.json';
const KARIERA_BACKUPS = KARIERA_DIR . '/zalohy';
const KARIERA_DEFAULT = __DIR__ . '/../../assets/kariera.json';
const KARIERA_KEEP = 20;
// typy úvazku pro Google Jobs (schema.org employmentType)
const KARIERA_UVAZKY = ['FULL_TIME', 'PART_TIME', 'TEMPORARY', 'CONTRACTOR', 'INTERN', 'OTHER'];

function kariera_load(): array
{
    foreach ([KARIERA_FILE, KARIERA_DEFAULT] as $f) {
        if (is_file($f)) {
            $d = json_decode((string) file_get_contents($f), true);
            if (is_array($d)) {
                return kariera_normalize($d)[0];
            }
        }
    }
    return kariera_normalize([])[0];
}

/** Jen to, co potřebuje web (bez skrytých pozic a interních poznámek). */
function kariera_public(array $d): array
{
    $d['pozice'] = array_values(array_filter($d['pozice'], fn($p) => $p['aktivni']));
    return $d;
}

function k_line($v, int $max): string
{
    $s = is_string($v) ? $v : '';
    $s = trim(preg_replace('/[\x00-\x1F\x7F]+/u', ' ', $s) ?? '');
    return mb_substr($s, 0, $max);
}

/** Seznam (pole nebo text po řádcích) → pole neprázdných řádků. */
function k_list($v, int $maxItems = 30, int $max = 300): array
{
    if (is_string($v)) {
        $v = preg_split('/\R/u', $v) ?: [];
    }
    if (!is_array($v)) {
        return [];
    }
    $out = [];
    foreach ($v as $x) {
        $x = k_line($x, $max);
        if ($x !== '') {
            $out[] = $x;
        }
    }
    return array_slice($out, 0, $maxItems);
}

/**
 * Ověří a uklidí data. Vrací [data, chyby]. Chyby jsou srozumitelné české věty pro administraci.
 */
function kariera_normalize(array $in): array
{
    $err = [];
    $mail = k_line($in['kontakt_email'] ?? '', 200);
    if ($mail === '' || !filter_var($mail, FILTER_VALIDATE_EMAIL)) {
        $err[] = 'Výchozí kontaktní e-mail není platný.';
    }
    $proc = [];
    foreach (is_array($in['proc'] ?? null) ? $in['proc'] : [] as $w) {
        $n = k_line($w['nadpis'] ?? '', 80);
        $t = k_line($w['text'] ?? '', 400);
        if ($n !== '' || $t !== '') {
            $proc[] = ['nadpis' => $n, 'text' => $t];
        }
    }
    $pozice = [];
    foreach (is_array($in['pozice'] ?? null) ? array_slice($in['pozice'], 0, 30) : [] as $i => $p) {
        if (!is_array($p)) {
            continue;
        }
        $nazev = k_line($p['nazev'] ?? '', 120);
        $label = $nazev !== '' ? "„{$nazev}“" : 'č. ' . ($i + 1);
        if ($nazev === '') {
            $err[] = "Pozice {$label} nemá název.";
        }
        $item = [
            'nazev' => $nazev,
            'aktivni' => !isset($p['aktivni']) || filter_var($p['aktivni'], FILTER_VALIDATE_BOOLEAN),
            'stitky' => k_list($p['stitky'] ?? [], 6, 60),
            'nabizime' => k_list($p['nabizime'] ?? []),
            'pozadujeme' => k_list($p['pozadujeme'] ?? []),
            'naplne' => k_list($p['naplne'] ?? []),
        ];
        $uv = k_line($p['uvazek'] ?? '', 20);
        $item['uvazek'] = in_array($uv, KARIERA_UVAZKY, true) ? $uv : 'FULL_TIME';
        $dt = k_line($p['zverejneno'] ?? '', 10);
        if ($dt !== '' && preg_match('/^\d{4}-\d{2}-\d{2}$/', $dt) && strtotime($dt)) {
            $item['zverejneno'] = $dt;
        }
        $pm = k_line($p['kontakt_email'] ?? '', 200);
        if ($pm !== '') {
            if (!filter_var($pm, FILTER_VALIDATE_EMAIL)) {
                $err[] = "Pozice {$label}: kontaktní e-mail není platný.";
            }
            $item['kontakt_email'] = $pm;
        }
        $tel = k_line($p['kontakt_tel'] ?? '', 30);
        if ($tel !== '') {
            if (!preg_match('/^\+?[0-9 ()\-]{6,30}$/', $tel)) {
                $err[] = "Pozice {$label}: telefon může obsahovat jen číslice, mezery a +.";
            }
            $item['kontakt_tel'] = $tel;
        }
        $pozice[] = $item;
    }
    return [[
        'intro' => k_line($in['intro'] ?? '', 600),
        'kontakt_email' => $mail,
        'proc' => array_slice($proc, 0, 6),
        'pozice' => $pozice,
        'dalsi' => k_line($in['dalsi'] ?? '', 600),
    ], $err];
}

/** Uloží data (atomicky) a předchozí verzi odloží do záloh. */
function kariera_save(array $d): void
{
    foreach ($d['pozice'] as &$p) {          // datum zveřejnění se doplní při prvním uložení pozice
        $p['zverejneno'] ??= date('Y-m-d');
    }
    unset($p);
    foreach ([KARIERA_DIR, KARIERA_BACKUPS] as $dir) {
        if (!is_dir($dir) && !mkdir($dir, 0750, true) && !is_dir($dir)) {
            throw new RuntimeException('Nelze vytvořit složku pro data: ' . $dir);
        }
    }
    if (is_file(KARIERA_FILE)) {
        $name = KARIERA_BACKUPS . '/kariera-' . date('Y-m-d-His');
        for ($n = 2; is_file($name . '.json'); $n++) {
            $name = KARIERA_BACKUPS . '/kariera-' . date('Y-m-d-His') . '-' . $n;
        }
        copy(KARIERA_FILE, $name . '.json');
        $all = kariera_backups();
        foreach (array_slice($all, KARIERA_KEEP) as $old) {
            @unlink(KARIERA_BACKUPS . '/' . $old['file']);
        }
    }
    $tmp = KARIERA_FILE . '.tmp';
    $json = json_encode($d, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
    if ($json === false || file_put_contents($tmp, $json, LOCK_EX) === false || !rename($tmp, KARIERA_FILE)) {
        throw new RuntimeException('Data se nepodařilo uložit (zkontrolujte práva zápisu do api/data/).');
    }
}

/** Zálohy od nejnovější: [['file' => ..., 'time' => ...], ...] */
function kariera_backups(): array
{
    $out = [];
    foreach (glob(KARIERA_BACKUPS . '/kariera-*.json') ?: [] as $f) {
        $out[] = ['file' => basename($f), 'time' => filemtime($f) ?: 0];
    }
    usort($out, fn($a, $b) => strcmp($b['file'], $a['file']));
    return $out;
}

function kariera_restore(string $file): bool
{
    if (!preg_match('/^kariera-\d{4}-\d{2}-\d{2}-\d{6}(-\d+)?\.json$/', $file) || !is_file(KARIERA_BACKUPS . '/' . $file)) {
        return false;
    }
    $d = json_decode((string) file_get_contents(KARIERA_BACKUPS . '/' . $file), true);
    if (!is_array($d)) {
        return false;
    }
    kariera_save(kariera_normalize($d)[0]);
    return true;
}
