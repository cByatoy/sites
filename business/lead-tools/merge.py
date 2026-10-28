import json, re, collections, urllib.parse

SOC = re.compile(r'(vk\.com|vk\.ru|vk\.cc|vkontakte|instagram|t\.me|telegram|wa\.me|whatsapp|ok\.ru|facebook|youtube)', re.I)
BOOK = re.compile(r'(dikidi|yclients|taplink|sonline|easyweek|bookon|vk\.link|clck\.ru|hipolink|mst\.link|gnom\.guru|profsalon|2gis\.biz|pbxcard|linktr|sites\.google)', re.I)


def digits(p):
    d = re.sub(r'\D', '', p or '')
    return d[-10:] if len(d) >= 10 else ''


def domain(u):
    if not u:
        return ''
    if '://' not in u:
        u = 'http://' + u
    h = (urllib.parse.urlparse(u).hostname or '').lower().removeprefix('www.')
    parts = h.split('.')
    # Группируем по основному домену: moskovskaya.britvabarber.ru -> britvabarber.ru (кроме бесплатных конструкторов)
    if len(parts) > 2 and not re.search(r'(tilda\.ws|clients\.site|turbo\.site|taplink|business\.site|spb\.ru|msk\.ru|com\.ru)$', h):
        h = '.'.join(parts[-2:])
    return h


def norm_name(n):
    return re.sub(r'[^a-zа-я0-9]', '', (n or '').lower().replace('ё', 'е').replace('барбершоп', '').replace('barbershop', ''))


def is_barber(z):
    slug = z['zoon'].rstrip('/').split('/')[-1]
    if '/beauty/' not in z['zoon']:
        return False
    return slug.split('_')[0] in ('barbershop', 'muzhskaya', 'barber') or bool(
        re.search(r'(barb|барб|мужск|gentl|джентл|\bmen\b|men\'s|mens)', z['name'].lower()))


zoon = [z for z in json.load(open('zoon_barber.json')) if is_barber(z)]
zorg = json.load(open('zoon_org.json'))
spr = json.load(open('spravker.json'))
audit = json.load(open('audit.json'))

points = []
for z in zoon:
    o = zorg.get(z['zoon'], {})
    if o and not o.get('site'):
        cand = [l for l in o.get('links', []) if not SOC.search(l) and not BOOK.search(l) and 'zoon.ru' not in l and l.startswith('http')]
        if cand:
            o['site'] = cand[0]
    points.append({
        'name': z['name'], 'address': z['address'], 'metro': z['metro'], 'phone': z['phone'], 'rating': z['rating'],
        'reviews': int(z['reviews'] or 0), 'site': o.get('site', ''), 'links': o.get('links', []), 'emails': list(o.get('emails', [])),
        'closed': o.get('closed', False), 'src': ['Zoon'], 'zoon': z['zoon'],
    })

by_phone = {digits(p['phone']): p for p in points if digits(p['phone'])}
by_name = collections.defaultdict(list)
for p in points:
    by_name[norm_name(p['name'])].append(p)

for s in spr:
    addr = s['address'].replace(', Санкт-Петербург', '')
    match = None
    for ph in re.split(r',', s['phone']):
        if digits(ph) in by_phone:
            match = by_phone[digits(ph)]
            break
    if not match:
        for p in by_name.get(norm_name(s['name']), []):
            if addr.split(',')[0][:8].lower() in p['address'].lower():
                match = p
                break
    if match:
        if not match['site'] and s['site']:
            match['site'] = s['site']
        if 'Spravker' not in match['src']:
            match['src'].append('Spravker')
    else:
        points.append({'name': s['name'], 'address': addr, 'metro': '', 'phone': s['phone'], 'rating': '', 'reviews': 0,
                       'site': s['site'], 'links': [], 'emails': [], 'closed': False, 'src': ['Spravker'], 'zoon': ''})

# Сайты, найденные вручную через поиск (в карточках не указаны)
MANUAL = {'belousov': 'https://belousovbarbershop.com/', 'heisenberg': 'https://xn--80acggbjn8a3a6b.xn--90a1af.xn--p1ai/'}
for p in points:
    if not p['site'] and norm_name(p['name']) in MANUAL:
        p['site'] = MANUAL[norm_name(p['name'])]
        p['src'].append('поиск')

# Сайт-соцсеть или страница записи — это не сайт
for p in points:
    if p['site'] and (SOC.search(p['site']) or BOOK.search(p['site'])):
        p['links'].append(p['site'])
        p['site'] = ''

# Группировка в бизнесы: по домену сайта, иначе по названию
groups = collections.OrderedDict()
for p in points:
    key = domain(p['site']) or ('name:' + norm_name(p['name']) if len(norm_name(p['name'])) >= 3 else 'addr:' + p['address'])
    groups.setdefault(key, []).append(p)

# Склеиваем группы «по названию» с группами «по домену», если название совпадает
name_to_domain = {}
for key, ps in groups.items():
    if not key.startswith('name:'):
        for p in ps:
            name_to_domain.setdefault(norm_name(p['name']), key)
for key in [k for k in groups if k.startswith('name:')]:
    target = name_to_domain.get(key[5:])
    if target and len(key) > 7:
        groups[target].extend(groups.pop(key))

json.dump({'points': len(points), 'groups': len(groups)}, open('merge_stats.json', 'w'))
businesses = []
for key, ps in groups.items():
    ps.sort(key=lambda p: -p['reviews'])
    main = ps[0]
    site = next((p['site'] for p in ps if p['site']), '')
    businesses.append({
        'name': main['name'], 'points': len(ps), 'addresses': [p['address'] for p in ps], 'metro': [p['metro'] for p in ps if p['metro']],
        'phone': next((p['phone'] for p in ps if p['phone']), ''), 'rating': main['rating'], 'reviews': sum(p['reviews'] for p in ps),
        'site': site, 'links': sorted({l for p in ps for l in p['links']}), 'emails': sorted({e for p in ps for e in p['emails']}),
        'closed': all(p['closed'] for p in ps), 'src': sorted({s for p in ps for s in p['src']}), 'zoon': next((p['zoon'] for p in ps if p['zoon']), ''),
    })

json.dump(businesses, open('businesses.json', 'w'), ensure_ascii=False, indent=1)
need = sorted({b['site'] for b in businesses if b['site'] and b['site'] not in audit})
json.dump(need, open('sites_todo.json', 'w'), indent=0)
print('points', len(points), 'businesses', len(businesses), 'with site', sum(1 for b in businesses if b['site']), 'to audit', len(need))
