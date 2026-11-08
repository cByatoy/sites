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

// Онлайн-запись: в демо — заглушка. На реальном сайте здесь виджет YCLIENTS / DIKIDI
// (их скрипт открывает окно записи по клику на кнопку).
const modal = document.getElementById('booking-modal');
document.querySelectorAll('[data-booking]').forEach((btn) => {
  btn.addEventListener('click', () => {
    if (modal && typeof modal.showModal === 'function') modal.showModal();
    else alert('Здесь откроется онлайн-запись YCLIENTS или DIKIDI. Демо: запись не работает.');
  });
});
