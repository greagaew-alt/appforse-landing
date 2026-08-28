<?php
// Хранилище комментариев к прототипу. Совместимо с PHP 5.6+
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

$file = __DIR__ . '/comments.json';

function read_all($file) {
    if (!file_exists($file)) return array();
    $data = json_decode(file_get_contents($file), true);
    return is_array($data) ? $data : array();
}

function save_all($file, $items) {
    $flags = 0;
    if (defined('JSON_UNESCAPED_UNICODE')) $flags |= JSON_UNESCAPED_UNICODE;
    if (defined('JSON_PRETTY_PRINT')) $flags |= JSON_PRETTY_PRINT;
    file_put_contents($file, json_encode($items, $flags), LOCK_EX);
}

$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET') {
    $flags = defined('JSON_UNESCAPED_UNICODE') ? JSON_UNESCAPED_UNICODE : 0;
    echo json_encode(read_all($file), $flags);
    exit;
}

if ($method === 'POST') {
    $raw = file_get_contents('php://input');
    $d = json_decode($raw, true);
    if (!is_array($d)) $d = array();

    // удаление комментария
    if (!empty($d['delete'])) {
        $del = $d['delete'];
        $items = array();
        foreach (read_all($file) as $c) {
            if (!isset($c['id']) || $c['id'] !== $del) $items[] = $c;
        }
        save_all($file, array_values($items));
        echo '{"ok":true}';
        exit;
    }

    $text = isset($d['text']) ? trim($d['text']) : '';
    if ($text === '') {
        http_response_code(400);
        echo '{"ok":false,"error":"empty"}';
        exit;
    }

    $name = isset($d['name']) ? trim($d['name']) : '';
    $name = mb_substr($name, 0, 80);
    if ($name === '') $name = 'Клиент';

    $items = read_all($file);
    $items[] = array(
        'id'    => uniqid('c', true),
        'ts'    => time(),
        'block' => mb_substr(isset($d['block']) ? (string)$d['block'] : '', 0, 50),
        'x'     => round(isset($d['x']) ? (float)$d['x'] : 0, 4),
        'y'     => round(isset($d['y']) ? (float)$d['y'] : 0, 4),
        'name'  => $name,
        'text'  => mb_substr($text, 0, 2000),
    );
    save_all($file, $items);
    echo '{"ok":true}';
    exit;
}

http_response_code(405);
echo '{"ok":false}';
