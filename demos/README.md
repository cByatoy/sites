# Демо-сайты для портфолио

Три отдельных сайта, у каждого своя ссылка на Netlify. Все закрыты от индексации (robots.txt + заголовок X-Robots-Tag).

| Папка | Сайт | Стиль |
|---|---|---|
| `barbershop/` | Барбершоп «Гранит» | тёмный, латунь, строгая типографика |
| `dental/` | Стоматология «Ясна» | светлый, бирюзовый, доверие и цены |
| `coffee/` | Кофейня «Разводной» | тёплый, игривый, меню с вкладками |

Компании, люди, отзывы и реквизиты вымышлены — это указано в подвале каждого сайта.

## Ссылки

| Сайт | Адрес | Netlify site ID |
|---|---|---|
| Гранит | https://granit-barbershop-demo.netlify.app | cfe4c81b-efd3-4884-8f6d-5cd543c366a9 |
| Ясна | https://yasna-dental-demo.netlify.app | 7543d21a-139b-43c8-8d3f-330fdb13a6ee |
| Разводной | https://razvodnoy-coffee-demo.netlify.app | 43c3b7d0-879d-43a3-a7a2-1fbaa07514e4 |

Публикация — через коннектор Netlify из сессии Claude (деплой из папки сайта). Защита «только для команды» отключена.

## Как опубликовать вручную через интерфейс Netlify (для каждой папки)
1. Netlify → Add new project → Import an existing project → GitHub → репозиторий `sites`.
2. Base directory: `demos/barbershop` (или `demos/dental`, `demos/coffee`).
3. Build command — пусто, Publish directory — пусто (или та же папка).
4. Deploy. Потом Site configuration → Change site name, например `granit-demo`.

## Что поменять под реального клиента
- Название, тексты, цены, контакты, реквизиты, координаты карты (`ll=` и `pt=` в iframe).
- Фото вместо SVG-иллюстраций.
- Отправку формы в `script.js` (сейчас демо-заглушка) — Telegram-бот или Web3Forms.
- Убрать `robots.txt`, `netlify.toml` noindex и `meta robots` при запуске на боевом домене.
