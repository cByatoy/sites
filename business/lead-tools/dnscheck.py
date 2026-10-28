"""Для сайтов с ошибкой: проверяем DNS через dns.google. Мёртвые помечаем, живые — на повторную проверку."""
import json, subprocess, urllib.parse, sys

audit = json.load(open('audit.json'))
retry = []
for url, a in audit.items():
    if a.get('ok') or 'dns' in a and a['dns'] in ('NXDOMAIN', 'SERVFAIL'):
        continue
    host = urllib.parse.urlparse(url).hostname
    r = subprocess.run(['curl', '-s', '-m', '15', f'https://dns.google/resolve?name={host}&type=A'], capture_output=True, text=True)
    try:
        st = json.loads(r.stdout).get('Status')
    except Exception:
        st = None
    a['dns'] = {0: 'OK', 2: 'SERVFAIL', 3: 'NXDOMAIN'}.get(st, 'UNKNOWN')
    if a['dns'] == 'OK':
        retry.append(url)
json.dump(audit, open('audit.json', 'w'), ensure_ascii=False, indent=1)
json.dump(retry, open('sites_retry.json', 'w'), indent=0)
print('dead', sum(1 for a in audit.values() if a.get('dns') in ('NXDOMAIN', 'SERVFAIL')), 'retry', len(retry))
if '--drop-retry' in sys.argv:
    for u in retry:
        audit.pop(u)
    json.dump(audit, open('audit.json', 'w'), ensure_ascii=False, indent=1)
