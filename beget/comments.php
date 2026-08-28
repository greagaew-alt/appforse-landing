<?php
// Хранилище комментариев к прототипу. Кладётся рядом с index.html на хостинг.
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

$file = __DIR__ . '/comments.json';

function read_all($file) {
    if (!file_exists($file)) return [];
    $data = json_decode(file_get_contents($file), true);
    return is_array($data) ? $data : [];
}

$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET') {
    echo json_encode(read_all($file), JSON_UNESCAPED_UNICODE);
    exit;
}

if ($method === 'POST') {
    $d = json_decode(file_get_contents('php://input'), true);

    // удаление комментария
    if (!empty($d['delete'])) {
        $items = array_values(array_filter(read_all($file), function ($c) use ($d) {
            return $c['id'] !== $d['delete'];
        }));
        file_put_contents($file, json_encode($items, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT), LOCK_EX);
        echo '{"ok":true}';
        exit;
    }

    $text = isset($d['text']) ? trim($d['text']) : '';
    if ($text === '') {
        http_response_code(400);
        echo '{"ok":false,"error":"empty"}';
        exit;
    }

    $items = read_all($file);
    $items[] = [
        'id'    => uniqid('c', true),
        'ts'    => time(),
        'block' => mb_substr((string)($d['block'] ?? ''), 0, 50),
        'x'     => round((float)($d['x'] ?? 0), 4),
        'y'     => round((float)($d['y'] ?? 0), 4),
        'name'  => mb_substr(trim((string)($d['name'] ?? 'Клиент')), 0, 80) ?: 'Клиент',
        'text'  => mb_substr($text, 0, 2000),
    ];
    file_put_contents($file, json_encode($items, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT), LOCK_EX);
    echo '{"ok":true}';
    exit;
}

http_response_code(405);
echo '{"ok":false}';
