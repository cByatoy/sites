# Демо-сайты для портфолио

Три отдельных сайта, у каждого своя ссылка на Netlify. Все закрыты от индексации (robots.txt + заголовок X-Robots-Tag).

| Папка | Сайт | Стиль |
|---|---|---|
| `barbershop/` | Барбершоп «Гранит» | тёмный, латунь, строгая типографика |
| `dental/` | Стоматология «Ясна» | светлый, бирюзовый, доверие и цены |
| `coffee/` | Кофейня «Разводной» | тёплый, игривый, меню с вкладками |

Компании, люди, отзывы и реквизиты вымышлены — это указано в подвале каждого сайта.

## Как опубликовать на Netlify (для каждой папки)
1. Netlify → Add new project → Import an existing project → GitHub → репозиторий `sites`.
2. Base directory: `demos/barbershop` (или `demos/dental`, `demos/coffee`).
3. Build command — пусто, Publish directory — пусто (или та же папка).
4. Deploy. Потом Site configuration → Change site name, например `granit-demo`.

## Что поменять под реального клиента
- Название, тексты, цены, контакты, реквизиты, координаты карты (`ll=` и `pt=` в iframe).
- Фото вместо SVG-иллюстраций.
- Отправку формы в `script.js` (сейчас демо-заглушка) — Telegram-бот или Web3Forms.
- Убрать `robots.txt`, `netlify.toml` noindex и `meta robots` при запуске на боевом домене.
