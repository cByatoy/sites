import json, os, re, subprocess, time, urllib.parse

UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36'
SOCIAL = re.compile(r'(vk\.com|vkontakte|t\.me|telegram|wa\.me|whatsapp|instagram|ok\.ru|youtube|dikidi|yclients|taplink|tilda|wix)', re.I)
EMAIL = re.compile(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[a-z]{2,}', re.I)


def get(url):
    for _ in range(3):
        r = subprocess.run(['curl', '-s', '-m', '30', '-A', UA, url], capture_output=True)
        if r.returncode == 0 and len(r.stdout) > 5000:
            return r.stdout.decode('utf-8', 'ignore')
        time.sleep(4)
    return ''


rows = json.load(open('zoon_barber.json'))
cache = json.load(open('zoon_org.json')) if os.path.exists('zoon_org.json') else {}
for i, r in enumerate(rows):
    if r['zoon'] in cache:
        continue
    s = get(r['zoon'])
    site = ''
    m = re.search(r'org-service-website".*?href="([^"]+)"', s, re.S)
    if m:
        q = urllib.parse.parse_qs(urllib.parse.urlparse(m.group(1).replace('&amp;', '&')).query)
        site = q.get('to', [''])[0]
    links = set()
    for u in re.findall(r'redirect/\?to=([^&"]+)', s):
        links.add(urllib.parse.unquote(u))
    links |= set(re.findall(r'https?://(?:vk\.com|t\.me|wa\.me|instagram\.com|taplink\.cc)/[^\s"\'<>&]+', s))
    emails = {e for e in EMAIL.findall(s) if 'zoon' not in e.lower() and not e.lower().endswith(('.png', '.jpg', '.svg', '.webp'))}
    closed = bool(re.search(r'(Закрыто навсегда|больше не работает|Организация закрыта)', s))
    cache[r['zoon']] = {'site': site, 'links': sorted(l for l in links if l != site), 'emails': sorted(emails), 'closed': closed, 'ok': bool(s)}
    if i % 25 == 0:
        json.dump(cache, open('zoon_org.json', 'w'), ensure_ascii=False)
        print(i, flush=True)
    time.sleep(1.2)
json.dump(cache, open('zoon_org.json', 'w'), ensure_ascii=False, indent=1)
print('done', len(cache), 'with site', sum(1 for v in cache.values() if v['site']), 'emails', sum(1 for v in cache.values() if v['emails']))
