/* Заготовка боевого сайта: меню, согласие на cookie, Яндекс Метрика и виджеты после согласия, форма заявки. */
(function () {
  'use strict';
  var CONFIG = window.SITE_CONFIG || {};
  var CONSENT_KEY = 'cookie-consent'; // 'all' | 'necessary'

  /* ---------- Меню на телефоне ---------- */
  var burger = document.querySelector('.burger');
  var nav = document.getElementById('nav');
  if (burger && nav) {
    burger.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      burger.setAttribute('aria-expanded', String(open));
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) { nav.classList.remove('is-open'); burger.setAttribute('aria-expanded', 'false'); }
    });
  }
  document.querySelectorAll('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });

  /* ---------- Согласие на cookie ---------- */
  function readConsent() { try { return localStorage.getItem(CONSENT_KEY); } catch (e) { return null; } }
  function saveConsent(v) { try { localStorage.setItem(CONSENT_KEY, v); } catch (e) {} }

  var banner = document.getElementById('cookie');
  function showBanner(show) { if (banner) banner.hidden = !show; }

  function applyConsent(value) {
    if (value === 'all') { loadMetrika(); loadAllEmbeds(); }
  }

  document.querySelectorAll('[data-cookie-accept]').forEach(function (b) {
    b.addEventListener('click', function () { saveConsent('all'); showBanner(false); applyConsent('all'); });
  });
  document.querySelectorAll('[data-cookie-reject]').forEach(function (b) {
    b.addEventListener('click', function () { saveConsent('necessary'); showBanner(false); });
  });
  document.querySelectorAll('[data-cookie-settings]').forEach(function (b) {
    b.addEventListener('click', function () { showBanner(true); });
  });

  /* ---------- Яндекс Метрика (только после согласия) ---------- */
  var metrikaLoaded = false;
  function loadMetrika() {
    var id = Number(CONFIG.metrikaId);
    if (metrikaLoaded || !id) return;
    metrikaLoaded = true;
    /* Официальный код счётчика Яндекс Метрики, вынесенный в функцию */
    (function (m, e, t, r, i, k, a) {
      m[i] = m[i] || function () { (m[i].a = m[i].a || []).push(arguments); };
      m[i].l = 1 * new Date();
      k = e.createElement(t); a = e.getElementsByTagName(t)[0];
      k.async = 1; k.src = r; a.parentNode.insertBefore(k, a);
    })(window, document, 'script', 'https://mc.yandex.ru/metrika/tag.js', 'ym');
    window.ym(id, 'init', { clickmap: true, trackLinks: true, accurateTrackBounce: true, webvisor: false });
  }
  /* Цели: любой элемент с data-goal="имя_цели". Цели заводятся в Метрике как «JavaScript-событие» с тем же именем. */
  document.addEventListener('click', function (e) {
    var el = e.target.closest('[data-goal]');
    if (el && metrikaLoaded && window.ym) window.ym(Number(CONFIG.metrikaId), 'reachGoal', el.getAttribute('data-goal'));
  });

  /* ---------- Виджеты Яндекса: карта и отзывы (после согласия или по клику) ---------- */
  function loadEmbed(box) {
    if (!box || box.dataset.loaded) return;
    box.dataset.loaded = '1';
    var f = document.createElement('iframe');
    f.src = box.getAttribute('data-src');
    f.title = box.getAttribute('data-title') || '';
    f.loading = 'lazy';
    f.setAttribute('allowfullscreen', '');
    box.innerHTML = '';
    box.appendChild(f);
  }
  function loadAllEmbeds() { document.querySelectorAll('[data-consent-embed]').forEach(loadEmbed); }
  /* Кнопка «Показать карту/отзывы» — разовое согласие на конкретный виджет */
  document.querySelectorAll('[data-embed-load]').forEach(function (b) {
    b.addEventListener('click', function () { loadEmbed(b.closest('[data-consent-embed]')); });
  });

  var consent = readConsent();
  if (consent) applyConsent(consent); else showBanner(true);

  /* ---------- Форма заявки ---------- */
  document.querySelectorAll('input[type="tel"]').forEach(function (input) {
    input.addEventListener('input', function () {
      var d = input.value.replace(/\D/g, '');
      if (!d) { input.value = ''; return; }
      if (d[0] === '8') d = '7' + d.slice(1);
      if (d[0] !== '7') d = '7' + d;
      d = d.slice(0, 11);
      var out = '+7';
      if (d.length > 1) out += ' (' + d.slice(1, 4);
      if (d.length >= 4) out += ') ' + d.slice(4, 7);
      if (d.length >= 7) out += '-' + d.slice(7, 9);
      if (d.length >= 9) out += '-' + d.slice(9, 11);
      input.value = out;
    });
  });

  document.querySelectorAll('[data-form]').forEach(function (form) {
    var status = form.querySelector('.form__status');
    function setStatus(text, state) { status.textContent = text; status.dataset.state = state || ''; }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      form.querySelectorAll('.is-invalid').forEach(function (el) { el.classList.remove('is-invalid'); });
      var name = form.elements.name, phone = form.elements.phone, consentBox = form.elements.consent;
      var error = '';
      if (!name.value.trim()) { name.classList.add('is-invalid'); error = 'Укажите имя.'; }
      if (phone.value.replace(/\D/g, '').length < 11) { phone.classList.add('is-invalid'); error = error || 'Проверьте номер телефона.'; }
      if (!consentBox.checked) { consentBox.closest('label').classList.add('is-invalid'); error = error || 'Нужно согласие на обработку персональных данных.'; }
      if (error) { setStatus(error, 'error'); return; }

      var btn = form.querySelector('[type="submit"]');
      btn.disabled = true;
      setStatus('Отправляем…');
      fetch(CONFIG.formEndpoint || form.action, { method: 'POST', body: new FormData(form), headers: { 'Accept': 'application/json' } })
        .then(function (r) { return r.json().catch(function () { return { ok: r.ok }; }); })
        .then(function (res) {
          if (res && res.ok) {
            setStatus('Спасибо! Заявка отправлена, скоро перезвоним.', 'ok');
            form.reset();
            if (metrikaLoaded && window.ym) window.ym(Number(CONFIG.metrikaId), 'reachGoal', 'form_sent');
          } else {
            setStatus((res && res.error) || 'Не удалось отправить. Позвоните нам, пожалуйста.', 'error');
          }
        })
        .catch(function () { setStatus('Не удалось отправить. Позвоните нам, пожалуйста.', 'error'); })
        .then(function () { btn.disabled = false; });
    });
  });
})();
