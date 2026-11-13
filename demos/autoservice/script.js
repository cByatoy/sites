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

// Вкладки прайса
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

// Нижняя панель на телефоне: показываем, когда первый экран (с его кнопками) ушёл из вида
(() => {
  const bar = document.getElementById('mobile-bar');
  const actions = document.querySelector('.hero');
  if (!bar || !actions) return;
  if (!('IntersectionObserver' in window)) { bar.classList.add('is-shown'); return; }
  new IntersectionObserver((entries) => {
    bar.classList.toggle('is-shown', !entries[0].isIntersecting);
  }).observe(actions);
})();
