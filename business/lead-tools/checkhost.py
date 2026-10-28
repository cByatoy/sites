"""Перепроверка недоступных сайтов с российских узлов check-host.net.
Результат пишется в audit[url]['ru_check'] = 'OK 200' | 'ERR ...'."""
import json, subprocess, time, urllib.parse

audit = json.load(open('audit.json'))


def call(url):
    r = subprocess.run(['curl', '-s', '-m', '25', '-H', 'Accept: application/json', url], capture_output=True, text=True)
    return json.loads(r.stdout)


todo = [u for u, a in audit.items()
        if 'ru_check' not in a and a.get('dns') not in ('NXDOMAIN', 'SERVFAIL')
        and (not a.get('ok') or a.get('status', 200) >= 500)]
print('to check', len(todo), flush=True)
for n, u in enumerate(todo):
    target = u.replace('http://', 'https://')
    try:
        q = urllib.parse.quote(target, safe=':/')
        rid = call(f'https://check-host.net/check-http?host={q}&node=ru1.node.check-host.net&node=ru2.node.check-host.net')['request_id']
        res = None
        for _ in range(8):
            time.sleep(3)
            res = call(f'https://check-host.net/check-result/{rid}')
            if res and all(v is not None for v in res.values()):
                break
        verdicts = []
        for node, v in (res or {}).items():
            if v and v[0]:
                ok, _, msg, code = (v[0] + [None, None, None, None])[:4]
                verdicts.append(f'{"OK" if ok == 1 else "ERR"} {code or msg}')
        good = [x for x in verdicts if x.startswith('OK') and not x.endswith(('5', '502', '503', '504'))]
        audit[u]['ru_check'] = good[0] if good else (verdicts[0] if verdicts else 'ERR no answer')
    except Exception as e:
        audit[u]['ru_check'] = 'UNKNOWN ' + str(e)[:60]
    print(n, u, audit[u]['ru_check'], flush=True)
    json.dump(audit, open('audit.json', 'w'), ensure_ascii=False)
    time.sleep(2)
json.dump(audit, open('audit.json', 'w'), ensure_ascii=False, indent=1)
