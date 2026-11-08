<?php
/**
 * Отправка заявки с сайта на e-mail. Работает на российском хостинге с PHP (Beget, Timeweb).
 * Данные никуда, кроме почты клиента, не передаются и на сервере не хранятся.
 *
 * Настройка (README → «Форма»):
 *   1. TO_EMAIL   — почта, куда приходят заявки (почта клиента).
 *   2. FROM_EMAIL — ящик на домене сайта (создаётся в панели хостинга), иначе письма попадут в спам.
 *   3. SITE_NAME  — название для темы письма.
 */
const TO_EMAIL   = '{{ПОЧТА_ДЛЯ_ЗАЯВОК}}';
const FROM_EMAIL = 'no-reply@{{ДОМЕН}}';
const SITE_NAME  = '{{НАЗВАНИЕ}}';

header('Content-Type: application/json; charset=utf-8');

function reply(bool $ok, string $error = '', int $code = 200): void {
    http_response_code($code);
    echo json_encode($ok ? ['ok' => true] : ['ok' => false, 'error' => $error], JSON_UNESCAPED_UNICODE);
    exit;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    reply(false, 'Метод не поддерживается.', 405);
}

// Скрытое поле-ловушка: люди его не видят, боты заполняют
if (!empty($_POST['website'])) {
    reply(true);
}

$name    = trim(strip_tags((string)($_POST['name'] ?? '')));
$phone   = preg_replace('/[^\d+]/', '', (string)($_POST['phone'] ?? ''));
$consent = ($_POST['consent'] ?? '') === '1';

if ($name === '' || mb_strlen($name) > 80) {
    reply(false, 'Укажите имя.', 422);
}
if (strlen(preg_replace('/\D/', '', $phone)) < 11) {
    reply(false, 'Проверьте номер телефона.', 422);
}
if (!$consent) {
    reply(false, 'Нужно согласие на обработку персональных данных.', 422);
}

// Простая защита от повторной отправки: не чаще раза в 30 секунд с одного IP
$ipKey = sys_get_temp_dir() . '/form_' . md5($_SERVER['REMOTE_ADDR'] ?? '');
if (is_file($ipKey) && time() - filemtime($ipKey) < 30) {
    reply(false, 'Заявка уже отправлена, подождите немного.', 429);
}
@touch($ipKey);

$subject = 'Заявка с сайта ' . SITE_NAME;
$body = "Новая заявка с сайта\n\n"
      . "Имя: {$name}\n"
      . "Телефон: {$phone}\n"
      . "Согласие на обработку ПД: да, " . date('d.m.Y H:i') . "\n"
      . "Страница: " . ($_SERVER['HTTP_REFERER'] ?? '—') . "\n";

$headers = [
    'From: ' . '=?UTF-8?B?' . base64_encode(SITE_NAME) . '?= <' . FROM_EMAIL . '>',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
];

$sent = mail(TO_EMAIL, '=?UTF-8?B?' . base64_encode($subject) . '?=', $body, implode("\r\n", $headers), '-f' . FROM_EMAIL);

$sent ? reply(true) : reply(false, 'Не удалось отправить. Позвоните нам, пожалуйста.', 500);
