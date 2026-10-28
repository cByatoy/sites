import html, json, re, subprocess, time

UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36'
BASE = 'https://zoon.ru/spb/beauty/type/barbershop/'


def get(url):
    for _ in range(4):
        r = subprocess.run(['curl', '-s', '-m', '30', '-A', UA, url], capture_output=True)
        if r.returncode == 0 and len(r.stdout) > 5000:
            return r.stdout.decode('utf-8', 'ignore')
        time.sleep(4)
    return ''


def text(x):
    return html.unescape(re.sub(r'<[^>]+>', ' ', x or '')).replace('\xa0', ' ').strip()


def parse(s):
    out = []
    for block in s.split('<li class="minicard-item js-results-item')[1:]:
        a = re.search(r'<a href="([^"]+)" class="title-link[^>]*>(.*?)</a>', block, re.S)
        if not a:
            continue
        feats = re.search(r'minicard-item__features">(.*?)</div>', block, re.S)
        rating = re.search(r'z-text--bold">([\d,]+)</div>', block)
        reviews = re.search(r'class="comments">\s*(\d+)', block)
        metro = re.findall(r'class="metro"[^>]*>(.*?)</a>', block)
        addr = re.search(r'class="address">(.*?)</span>', block, re.S)
        phone = re.search(r'data-number="([^"]+)"', block)
        out.append({
            'name': text(a.group(2)), 'zoon': a.group(1), 'features': re.sub(r'\s*•\s*', ', ', text(feats.group(1) if feats else '')).strip(', '),
            'rating': rating.group(1).replace(',', '.') if rating else '', 'reviews': reviews.group(1) if reviews else '0',
            'metro': ', '.join(text(m) for m in metro), 'address': text(addr.group(1) if addr else ''),
            'phone': phone.group(1).replace('\xa0', ' ') if phone else '',
        })
    return out


rows, page = [], 1
while True:
    s = get(BASE if page == 1 else f'{BASE}page-{page}/')
    items = parse(s)
    print(page, len(items), flush=True)
    if not items:
        break
    rows += items
    if f'page-{page + 1}/' not in s:
        break
    page += 1
    time.sleep(1.5)

seen, uniq = set(), []
for r in rows:
    if r['zoon'] not in seen:
        seen.add(r['zoon'])
        uniq.append(r)
json.dump(uniq, open('zoon.json', 'w'), ensure_ascii=False, indent=1)
print('total', len(uniq))
