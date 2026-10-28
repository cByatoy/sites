import json, re, urllib.parse, datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

biz = json.load(open('businesses.json'))
audit = json.load(open('audit.json'))
YEAR = 2026


def mb(b):
    return round(b / 1024 / 1024, 1)


def problems(b):
    """Возвращает (оценка, [проблемы], [аргументы для письма], статус сайта)."""
    site = b['site']
    dead_args = lambda why: [f'Сайт, указанный в картах ({site}), не работает: {why}. Клиенты, которые на него кликают, уходят к конкурентам']
    if not site:
        LP = r'(vk\.com|vk\.ru|vk\.link|instagram|t\.me|wa\.me|taplink|dikidi|yclients|hipolink|mst\.link|profsalon|2gis\.biz|pbxcard|gnom\.guru|clck\.ru|sites\.google)'
        social = [l for l in b['links'] if re.search(LP, l)]
        what = 'только ' + ', '.join(sorted({re.search(LP, l).group(1) for l in social})) if social else 'только карточки на картах'
        return 100, ['Сайт не указан в карточках'], [f'В карточках на картах и в справочниках не указан сайт ({what}) — по запросу «барбершоп + район» вас находят только через агрегаторы, а записаться напрямую негде'], 'Нет сайта'
    host0 = (urllib.parse.urlparse(site if '://' in site else 'http://' + site).hostname or '').lower()
    if re.search(r'(vk\.link|vk\.cc|taplink|clck\.ru|hipolink|mst\.link|gnom\.guru|profsalon|2gis\.biz|pbxcard|linktr|dikidi|yclients|sites\.google)', host0 + site):
        return 100, ['Нет сайта (только ссылка-визитка)'], [f'Своего сайта нет — в картах указана ссылка-визитка {host0}. По запросу «барбершоп + район» в Яндексе вас находят только через агрегаторы'], 'Нет сайта'
    a = audit.get(site)
    if not a:
        return 0, ['Не проверен'], [], 'Не проверен'
    title = (a.get('title') or '')
    if a.get('ok') and re.search(r'(Domain has been assigned|Не опубликован|Please renew your subscription|больше не работает|продается|продаётся|for sale)', title + ' ' + (a.get('parked') or ''), re.I):
        why = 'не оплачен хостинг/конструктор' if 'renew' in title.lower() else 'сайт снят с публикации' if 'опубликован' in title else 'домен не привязан к сайту' if 'assigned' in title else 'домен выставлен на продажу' if re.search('прода|sale', title, re.I) else 'страница филиала закрыта'
        return 95, [f'Сайт отключён ({why})'], dead_args(why), 'Не работает'
    if a.get('ok') and re.search(r'(казино|casino|ставк|букмекер|\bbet\b|slots|слоты)', title, re.I):
        return 100, ['Домен перехвачен — открывается онлайн-казино'], [f'По ссылке на сайт из ваших карточек ({site}) сейчас открывается онлайн-казино — домен, видимо, не продлили и его перекупили. Клиенты это видят, а поисковики могут пометить вашу карточку'], 'Не работает'
    if a.get('ok') and re.search(r'^(404|.*Page Not Found|.*не найдена)', title, re.I):
        return 90, ['Ошибка 404 (страница не найдена)'], dead_args('показывает «страница не найдена»'), 'Не работает'
    if a.get('ok') and 'Just a moment' in title:
        return 0, ['Защита Cloudflare, не проверен'], [], 'Не проверен'
    if a.get('dns') == 'NXDOMAIN':
        return 95, ['Домен не существует'], dead_args('домен не продлён или удалён'), 'Не работает'
    if a.get('dns') == 'SERVFAIL':
        return 95, ['Домен не работает (ошибка DNS)'], dead_args('у домена сломаны настройки DNS'), 'Не работает'
    if not a.get('ok') or a.get('status', 200) >= 500:
        rc = a.get('ru_check', '')
        if rc.startswith('OK'):
            return 0, ['Работает (проверено из РФ), подробный разбор не сделан'], [], 'Не проверен'
        if rc.startswith('ERR'):
            return 90, [f'Не открывается и из России ({rc[4:]})'], dead_args('сервер не отвечает или отдаёт ошибку'), 'Не работает'
        return 0, ['Не удалось проверить'], [], 'Не проверен'
    p, args, score = [], [], 0
    if a.get('parked'):
        p.append('Домен припаркован / сайт отключён'); args.append(f'Вместо сайта открывается заглушка «{a["parked"]}»'); score += 90
    st = a.get('status', 200)
    if st >= 400:
        why = {402: 'не оплачен хостинг/конструктор', 404: 'страница не найдена', 401: 'закрыт паролем', 403: 'доступ запрещён'}.get(st, f'ошибка {st}')
        return 90, [f'Ошибка {st} ({why})'], dead_args(f'показывает ошибку {st} — {why}'), 'Не работает'
    if a.get('template'):
        p.append('Остатки шаблона'); args.append(f'На сайте остался текст шаблона «{a["template"]}»'); score += 60
    if not a.get('viewport') or a.get('viewport', '').startswith('width=1'):
        p.append('Не адаптирован под телефон'); args.append('На телефоне открывается уменьшенная версия для компьютера или страница не помещается в экран — приходится масштабировать и листать вбок'); score += 55
    elif (a.get('overflow') or 0) > 60:
        p.append('Страница шире экрана телефона'); args.append('На телефоне страница «гуляет» вбок — какой-то блок шире экрана'); score += 15
    host = urllib.parse.urlparse(a.get('finalUrl') or site).hostname or ''
    if re.search(r'(tilda\.ws|clients\.site|wixsite|taplink|business\.site|ucoz|narod|nethouse\.ru|mya5\.ru|ukit\.me|turbo\.site)', host):
        p.append('Нет своего домена'); args.append(f'Сайт на бесплатном адресе {host} — выглядит несолидно и хуже находится в поиске'); score += 40
    if not a.get('https'):
        p.append('Нет HTTPS'); args.append('Сайт открывается без HTTPS — браузер пишет «Не защищено» рядом с формой записи'); score += 40
    size = a.get('bytes') or 0
    if size > 8 * 1024 * 1024:
        p.append(f'Очень тяжёлый ({mb(size)} МБ)'); args.append(f'Главная страница весит {mb(size)} МБ — на мобильном интернете грузится 10+ секунд'); score += 40
    elif size > 4 * 1024 * 1024:
        p.append(f'Тяжёлый ({mb(size)} МБ)'); args.append(f'Главная весит {mb(size)} МБ — это в 3–5 раз больше нормы, на телефоне грузится медленно'); score += 20
    years = [y for y in (a.get('years') or []) if 2000 < y <= YEAR]
    if years and max(years) <= YEAR - 3:
        p.append(f'Не обновлялся (© {max(years)})'); args.append(f'В подвале сайта © {max(years)} — посетитель думает, что сайт заброшен'); score += 20
    if not a.get('tel'):
        p.append('Нет кнопки звонка'); args.append('Телефон на сайте не кликается — с телефона нельзя позвонить в одно касание'); score += 15
    if not a.get('booking') and not a.get('form'):
        p.append('Нет онлайн-записи'); args.append('На сайте нельзя записаться онлайн — только звонить'); score += 25
    if (a.get('smallText') or 0) > 15:
        p.append('Мелкий текст'); score += 10
    if (a.get('textLen') or 0) < 300:
        p.append('Почти нет текста'); args.append('На главной почти нет текста (всё на картинках) — поисковики не видят ваши услуги и цены'); score += 35
    return score, p, args, 'Есть проблемы' if p else 'В порядке'


BARBER = re.compile(r"(barb|барб|мужск|gentl|джентл|\bmen\b|men's|mens|муж)", re.I)


def is_barber(b):
    return bool(BARBER.search(b['name']) or BARBER.search(b['site'] or '') or '/barbershop_' in b['zoon'] or '/muzhskaya_' in b['zoon'])


rows_bad, rows_ok, rows_salon = [], [], []
for b in biz:
    if b['closed']:
        continue
    score, p, args, status = problems(b)
    a = audit.get(b['site'], {}) if b['site'] else {}
    emails = sorted(set(b['emails']) | (set() if status == 'Не работает' else set(a.get('emails') or [])))
    emails = [e for e in emails if not re.search(r'(noreply|no-reply|support@tilda|@tilda|@sentry|@yclients|@dikidi|@zoon|@example|vk-portal|wixpress|@2x|\.(js|css|png)$)', e, re.I)
              and not re.match(r'^[0-9a-f]{16,}@', e, re.I)]
    vk = next((l for l in b['links'] if re.search(r'vk\.(com|ru)', l)), '')
    tg = next((l for l in b['links'] if 't.me' in l), '')
    wa = next((l for l in b['links'] if 'wa.me' in l), '')
    inst = next((l for l in b['links'] if 'instagram' in l), '')
    prio = 'A' if score >= 55 else 'B' if score >= 25 else 'C'
    if b['points'] >= 4:
        prio = {'A': 'B', 'B': 'C', 'C': 'C'}[prio]  # крупная сеть — решения дольше
    row = {
        'prio': prio, 'score': score, 'name': b['name'], 'type': 'сеть' if b['points'] >= 4 else f'{b["points"]} точки' if b['points'] > 1 else 'одна точка',
        'address': b['addresses'][0] + (f' (+ ещё {b["points"] - 1})' if b['points'] > 1 else ''), 'metro': (b['metro'] or [''])[0],
        'phone': b['phone'], 'email': ', '.join(emails), 'site': b['site'], 'status': status, 'problems': '; '.join(p),
        'args': ' '.join(args[:3]), 'size': f'{mb(a["bytes"])} МБ' if a.get('bytes') else '', 'builder': a.get('builder', ''),
        'rating': b['rating'], 'reviews': b['reviews'], 'vk': vk, 'tg': tg, 'wa': wa, 'inst': inst, 'zoon': b['zoon'],
        'shot': a.get('shot', ''), 'src': ', '.join(b['src']),
        'check': ('Перед письмом поискать сайт по названию' if status == 'Нет сайта' and not p[0].startswith('Нет сайта (') else
                  'Убедиться, что барбершоп работает (свежие отзывы, звонок)' if status == 'Не работает' else '')
                 + ('; мало отзывов — возможно, закрыт' if (b['reviews'] or 0) == 0 else ''),
    }
    if not is_barber(b):
        rows_salon.append(row)
    else:
        (rows_bad if status not in ('В порядке', 'Не проверен') else rows_ok).append(row)

rows_bad.sort(key=lambda r: ({'A': 0, 'B': 1, 'C': 2}[r['prio']], -r['score'], -(r['reviews'] or 0)))
rows_ok.sort(key=lambda r: r['name'].lower())

COLS = [('№', 5), ('Приоритет', 9), ('Название', 24), ('Тип', 11), ('Адрес', 32), ('Метро', 16), ('Телефон', 18), ('E-mail', 28),
        ('Сайт', 28), ('Статус сайта', 14), ('Проблемы', 36), ('Аргументы для письма', 60), ('Вес главной', 10), ('Конструктор', 12),
        ('Рейтинг Zoon', 9), ('Отзывов', 8), ('VK', 22), ('Telegram', 22), ('WhatsApp', 22), ('Instagram', 22), ('Карточка Zoon', 22),
        ('Статус контакта', 14), ('Дата письма', 12), ('Напомнить', 12), ('Заметки', 30)]
KEYS = ['prio', 'name', 'type', 'address', 'metro', 'phone', 'email', 'site', 'status', 'problems', 'args', 'size', 'builder',
        'rating', 'reviews', 'vk', 'tg', 'wa', 'inst', 'zoon']


def sheet(ws, rows, with_tracking=True):
    ws.append([c for c, _ in COLS])
    for i, r in enumerate(rows, 1):
        ws.append([i] + [r[k] for k in KEYS] + ['Не писал', '', '', r.get('check', '').strip('; ')])
    for c in ws[1]:
        c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='1F2937')
        c.alignment = Alignment(wrap_text=True, vertical='center')
    fills = {'A': 'DCFCE7', 'B': 'FEF9C3', 'C': 'F3F4F6'}
    for row in ws.iter_rows(min_row=2):
        row[1].fill = PatternFill('solid', fgColor=fills.get(row[1].value, 'FFFFFF'))
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical='top')
    for i, (_, w) in enumerate(COLS):
        ws.column_dimensions[ws.cell(1, i + 1).column_letter].width = w
    ws.freeze_panes = 'D2'
    ws.auto_filter.ref = ws.dimensions
    dv = DataValidation(type='list', formula1='"Не писал,Написал,Напомнил,Ответил,Созвон,Отказ,Клиент"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f'V2:V{len(rows) + 1}')


wb = Workbook()
ws = wb.active; ws.title = 'Проблемы с сайтом'
sheet(ws, rows_bad)
ws2 = wb.create_sheet('Сайт в порядке или не проверен'); sheet(ws2, rows_ok)
rows_salon.sort(key=lambda r: ({'A': 0, 'B': 1, 'C': 2}[r['prio']], -r['score']))
ws3 = wb.create_sheet('Салоны с барбер-услугами'); sheet(ws3, rows_salon)
info = wb.create_sheet('Как читать')
stats = json.load(open('merge_stats.json'))
cnt = {k: sum(1 for r in rows_bad if r['prio'] == k) for k in 'ABC'}
lines = [
    ('Дата сбора', datetime.date.today().strftime('%d.%m.%Y')),
    ('Источники', f'Zoon (все страницы рубрики «Барбершопы», СПб) + Spravker. Точек: {stats["points"]}, после объединения филиалов: {stats["groups"]} бизнесов'),
    ('Как проверялось', 'Каждый сайт открыт в браузере с экраном iPhone 13: https, адаптивность, вес страницы, кнопка звонка, онлайн-запись, остатки шаблона, год в копирайте, почта на сайте'),
    ('Приоритет A', f'{cnt["A"]} шт. — нет сайта, сайт не работает, не адаптирован под телефон или остался шаблон. Начинать с них'),
    ('Приоритет B', f'{cnt["B"]} шт. — сайт есть, но тяжёлый / без https / без онлайн-записи / на бесплатном домене; или крупная сеть с проблемами'),
    ('Приоритет C', f'{cnt["C"]} шт. — мелкие недочёты'),
    ('E-mail', 'Только найденные на сайте или карточке. У большинства барбершопов почты нет — писать в VK / Telegram / WhatsApp из таблицы'),
    ('Вес главной', 'Норма — до 2–3 МБ. Скорость в секундах не указана: она измерялась через медленную сеть и была бы завышена'),
    ('Исключено', 'Закрытые точки; филиалы одной сети сведены в одну строку (пишем владельцу один раз)'),
    ('Салоны', 'Салоны красоты, которые справочники относят к барбершопам, вынесены на отдельный лист'),
    ('Не проверен', 'Сайт работает (проверено с серверов в России через check-host.net), но из моей среды не открывается — разобрать вручную'),
    ('Закон', 'Пишите каждому лично и с разбором его сайта. Массовые рекламные рассылки без согласия запрещены (ст. 18 закона «О рекламе»)'),
]
for l in lines:
    info.append(l)
info.column_dimensions['A'].width = 18; info.column_dimensions['B'].width = 120
for c in info['A']:
    c.font = Font(bold=True)
wb.save('/home/user/sites/private/barbershops-spb-full.xlsx')
print('bad', len(rows_bad), cnt, 'ok', len(rows_ok), 'salons', len(rows_salon), 'emails', sum(1 for r in rows_bad if r['email']))
json.dump(rows_bad, open('rows_bad.json', 'w'), ensure_ascii=False, indent=1)
