import base64, html, json, re, subprocess, time

UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36'


def get(url):
    for _ in range(4):
        r = subprocess.run(['curl', '-s', '-m', '30', '-A', UA, url], capture_output=True)
        if r.returncode == 0 and len(r.stdout) > 5000:
            return r.stdout.decode('utf-8', 'ignore')
        time.sleep(3)
    return ''


def parse(s):
    out = []
    for block in s.split('<div class="org-widget ')[1:]:
        name = re.search(r'class="org-widget-header__title-link">(.*?)</a>', block, re.S)
        if not name:
            continue
        href = re.search(r'<a href="([^"]+)"', block)
        metas = re.findall(r'org-widget-header__meta[^"]*">\s*(.*?)\s*</span>', block, re.S)
        specs = dict()
        for k, v in re.findall(r'spec__index-inner">(.*?)</span></dt>\s*<dd class="spec__value">(.*?)</dd>', block, re.S):
            specs[k.strip()] = v
        site = ''
        m = re.search(r'data-url="([^"]+)"', specs.get('Сайт', ''))
        if m:
            site = base64.b64decode(m.group(1)).decode('utf-8', 'ignore')
        out.append({
            'name': html.unescape(name.group(1).strip()),
            'url': 'https://spb.spravker.ru' + href.group(1) if href else '',
            'categories': html.unescape(metas[0].strip()) if metas else '',
            'address': html.unescape(metas[1].strip()) if len(metas) > 1 else '',
            'phone': html.unescape(re.sub('<[^>]+>', ' ', specs.get('Телефон', '')).strip()),
            'hours': html.unescape(re.sub('<[^>]+>', ' ', specs.get('Часы работы', '')).strip()),
            'site': site,
        })
    return out


rows, page = [], 1
while True:
    s = get(f'https://spb.spravker.ru/barbershop/?page={page}' if page > 1 else 'https://spb.spravker.ru/barbershop/')
    items = parse(s)
    print(page, len(items), flush=True)
    if not items:
        break
    rows += items
    if f'page={page + 1}' not in s:
        break
    page += 1
    time.sleep(1)

json.dump(rows, open('spravker.json', 'w'), ensure_ascii=False, indent=1)
print('total', len(rows), 'with site', sum(1 for r in rows if r['site']))
