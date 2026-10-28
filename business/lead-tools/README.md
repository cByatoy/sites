# Сбор и проверка потенциальных клиентов

Скрипты, которыми собран список барбершопов СПб с проблемами сайта. Данные (json, xlsx) в репозиторий не кладём — они в `private/`.

Порядок запуска (в рабочей папке, нужен полный доступ к сети):
1. `python3 zoon_list.py` — все карточки рубрики на Zoon (поменять BASE для другой ниши/города)
2. `python3 spravker.py` — карточки Spravker (поменять URL рубрики)
3. `python3 zoon_org.py` — сайт, соцсети, мессенджеры из карточек Zoon (~1,5 ч, медленно специально)
4. `python3 merge.py` — объединение источников, филиалы → один бизнес; пишет sites_todo.json
5. `mkdir -p shots && node audit.js sites_todo.json audit.json` — проверка сайтов в браузере (экран iPhone 13)
6. `python3 dnscheck.py --drop-retry && node audit.js sites_todo.json audit.json && python3 dnscheck.py` — мёртвые домены через dns.google
7. `python3 checkhost.py` — перепроверка недоступных сайтов с российских серверов check-host.net
8. `python3 merge.py && python3 report.py` — итоговая таблица в private/

Ограничения: среда Claude не ходит по http:// (только https) и не достаёт часть российских хостингов — поэтому шаги 6–7.
