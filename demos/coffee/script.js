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

// Маска телефона
document.querySelectorAll('input[type="tel"]').forEach((input) => {
  input.addEventListener('input', () => {
    let d = input.value.replace(/\D/g, '');
    if (d.startsWith('8')) d = '7' + d.slice(1);
    if (!d.startsWith('7')) d = '7' + d;
    d = d.slice(0, 11);
    const parts = ['+7'];
    if (d.length > 1) parts.push(' (' + d.slice(1, 4));
    if (d.length >= 4) parts.push(') ' + d.slice(4, 7));
    if (d.length >= 7) parts.push('-' + d.slice(7, 9));
    if (d.length >= 9) parts.push('-' + d.slice(9, 11));
    input.value = parts.join('');
  });
});

// Форма заявки. В демо заявка никуда не отправляется;
// на реальном сайте здесь отправка в Telegram-бот или через Web3Forms.
document.querySelectorAll('form.form').forEach((form) => {
  const status = form.querySelector('.form__status');
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const phone = form.querySelector('input[type="tel"]');
    const consent = form.querySelector('input[name="consent"]');
    const name = form.querySelector('input[name="name"]');
    form.querySelectorAll('.is-invalid').forEach((el) => el.classList.remove('is-invalid'));
    let error = '';
    if (name && !name.value.trim()) { name.classList.add('is-invalid'); error = 'Укажите имя.'; }
    if (phone && phone.value.replace(/\D/g, '').length < 11) { phone.classList.add('is-invalid'); error = error || 'Проверьте номер телефона.'; }
    if (consent && !consent.checked) { consent.closest('label').classList.add('is-invalid'); error = error || 'Нужно согласие на обработку данных.'; }
    if (error) {
      status.textContent = error;
      status.dataset.state = 'error';
      return;
    }
    status.textContent = 'Спасибо! Мы перезвоним в течение 15 минут. (Демо: заявка не отправляется.)';
    status.dataset.state = 'ok';
    form.reset();
  });
});
