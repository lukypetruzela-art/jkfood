<?php
/*
 * Aktuální inzeráty pro stránku kariera.html (JSON).
 * Data upravuje zákazník v administraci (admin/), ukládají se do api/data/kariera.json.
 * Dokud v administraci nikdo nic neuložil, vrací výchozí data z assets/kariera.json.
 */
declare(strict_types=1);

require __DIR__ . '/lib/kariera-data.php';

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-cache');
header('X-Content-Type-Options: nosniff');

if (($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'GET') {
    http_response_code(405);
    header('Allow: GET');
    echo '{"error":"method"}';
    exit;
}

echo json_encode(kariera_public(kariera_load()), JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
