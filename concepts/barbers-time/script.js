// Меню на телефоне
const burger = document.querySelector('.burger');
const nav = document.getElementById('nav');
if (burger && nav) {
  burger.addEventListener('click', () => {
    const open = nav.classList.toggle('is-open');
    burger.setAttribute('aria-expanded', String(open));
  });
  nav.addEventListener('click', (e) => {
    if (e.target.closest('a')) {
      nav.classList.remove('is-open');
      burger.setAttribute('aria-expanded', 'false');
    }
  });
}

// Текущий год в подвале
document.querySelectorAll('[data-year]').forEach((el) => { el.textContent = new Date().getFullYear(); });

// Плавное появление блоков
const revealed = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window) {
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  revealed.forEach((el) => io.observe(el));
} else {
  revealed.forEach((el) => el.classList.add('is-visible'));
}

// Вкладки (меню кофейни)
document.querySelectorAll('[data-tabs]').forEach((tabs) => {
  const buttons = tabs.querySelectorAll('[role="tab"]');
  buttons.forEach((btn) => btn.addEventListener('click', () => {
    buttons.forEach((b) => {
      const active = b === btn;
      b.setAttribute('aria-selected', String(active));
      document.getElementById(b.getAttribute('aria-controls')).hidden = !active;
    });
  }));
});

// Согласие на cookie, Яндекс Метрика и виджеты Яндекса (логика из templates/production-starter)
(function () {
  var CONFIG = window.SITE_CONFIG || {};
  var CONSENT_KEY = 'cookie-consent'; // 'all' | 'necessary'
  var banner = document.getElementById('cookie');
  function readConsent() { try { return localStorage.getItem(CONSENT_KEY); } catch (e) { return null; } }
  function saveConsent(v) { try { localStorage.setItem(CONSENT_KEY, v); } catch (e) {} }
  function showBanner(show) { if (banner) banner.hidden = !show; }

  // Яндекс Метрика: только после согласия и только если вписан числовой ID
  var metrikaLoaded = false;
  var metrikaId = Number(CONFIG.metrikaId);
  function loadMetrika() {
    if (metrikaLoaded || !metrikaId) return;
    metrikaLoaded = true;
    (function (m, e, t, r, i, k, a) {
      m[i] = m[i] || function () { (m[i].a = m[i].a || []).push(arguments); };
      m[i].l = 1 * new Date();
      k = e.createElement(t); a = e.getElementsByTagName(t)[0];
      k.async = 1; k.src = r; a.parentNode.insertBefore(k, a);
    })(window, document, 'script', 'https://mc.yandex.ru/metrika/tag.js', 'ym');
    window.ym(metrikaId, 'init', { clickmap: true, trackLinks: true, accurateTrackBounce: true, webvisor: false });
  }
  // Цели: элементы с data-goal. В Метрике заводятся как «JavaScript-событие» с тем же именем.
  document.addEventListener('click', function (e) {
    var el = e.target.closest('[data-goal]');
    if (el && metrikaLoaded && window.ym) window.ym(metrikaId, 'reachGoal', el.getAttribute('data-goal'));
  });

  // Карта и отзывы Яндекса: после согласия или по кнопке
  function embedReady(box) { var src = box && box.getAttribute('data-src'); return src && src.indexOf('{{') === -1; }
  function loadEmbed(box) {
    if (!embedReady(box) || box.dataset.loaded) return;
    box.dataset.loaded = '1';
    var f = document.createElement('iframe');
    f.src = box.getAttribute('data-src');
    f.title = box.getAttribute('data-title') || '';
    f.loading = 'lazy';
    f.setAttribute('allowfullscreen', '');
    box.innerHTML = '';
    box.appendChild(f);
    box.classList.add('is-loaded');
  }
  function loadAllEmbeds() { document.querySelectorAll('[data-consent-embed]').forEach(loadEmbed); }
  document.querySelectorAll('[data-embed-load]').forEach(function (b) {
    var box = b.closest('[data-consent-embed]');
    if (!embedReady(box)) { b.hidden = true; return; } // ID ещё не вписан — кнопку не показываем
    b.addEventListener('click', function () { loadEmbed(box); });
  });

  function applyConsent(v) { if (v === 'all') { loadMetrika(); loadAllEmbeds(); } }
  document.querySelectorAll('[data-cookie-accept]').forEach(function (b) {
    b.addEventListener('click', function () { saveConsent('all'); showBanner(false); applyConsent('all'); });
  });
  document.querySelectorAll('[data-cookie-reject]').forEach(function (b) {
    b.addEventListener('click', function () {
      var was = readConsent();
      saveConsent('necessary');
      showBanner(false);
      // Метрика и виджеты уже загружены: перезагружаем страницу, чтобы они отключились
      if (was === 'all' || metrikaLoaded) location.reload();
    });
  });
  document.querySelectorAll('[data-cookie-settings]').forEach(function (b) {
    b.addEventListener('click', function () { showBanner(true); });
  });

  var consent = readConsent();
  if (consent) applyConsent(consent); else showBanner(true);
})();

// Прайс: переключатель точки. Цены, которые отличаются, заданы в data-price-shotmana / data-price-dybenko.
document.querySelectorAll('[data-price-point]').forEach((group) => {
  const buttons = group.querySelectorAll('[data-point]');
  const apply = (point) => {
    buttons.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.point === point)));
    document.querySelectorAll('[data-price-' + point + ']').forEach((el) => {
      el.textContent = el.getAttribute('data-price-' + point) + ' ₽';
    });
  };
  buttons.forEach((b) => b.addEventListener('click', () => apply(b.dataset.point)));
  apply('shotmana');
});

// Нижняя панель на телефоне: показываем, когда первый экран ушёл из вида
(function () {
  var bar = document.querySelector('.mobile-bar');
  var hero = document.querySelector('.hero');
  if (!bar) return;
  if (!hero || !('IntersectionObserver' in window)) { bar.classList.add('is-shown'); return; }
  new IntersectionObserver(function (entries) {
    bar.classList.toggle('is-shown', !entries[0].isIntersecting);
  }).observe(hero);
})();
