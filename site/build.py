# -*- coding: utf-8 -*-
"""Собирает сайт из template.html:
- index.html — публичный лендинг (код админки вырезается целиком);
- admin.html — тот же лендинг + редактор (вход по паролю, API на Beget);
- privacy.html и 404.html.
Потом компилирует JSX в обоих файлах и вставляет разметку для поисковиков (seo.py)."""
import json, io, os, re, subprocess, sys

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = r"C:\Users\greag\AppData\Local\Temp\claude\c--Users-greag-Desktop------------1111\eab9426b-0f24-4fe6-b5fe-b82a3320af88\scratchpad\assets\assets.json"

a = json.load(open(ASSETS, encoding='utf-8'))
tpl = io.open(os.path.join(BASE, 'template.html'), encoding='utf-8').read()

# @font-face вставляем прямо в страницу: браузер узнаёт о шрифтах сразу,
# без отдельного запроса за fonts.css
FONTS_CSS = io.open(os.path.join(BASE, 'fonts.css'), encoding='utf-8').read().strip()


def inline_fonts(html):
    return html.replace('<link rel="stylesheet" href="fonts.css">',
                        '<style>' + FONTS_CSS + '</style>')


# картинки лежат отдельными файлами: страница перестаёт весить почти мегабайт
# и рисуется, не дожидаясь их загрузки
img = json.load(io.open(os.path.join(BASE, 'img', 'paths.json'), encoding='utf-8'))

out = (tpl
       .replace('__LOGO__', img['logo'])
       .replace('__SHOT_HERO_A__', img['heroA'])
       .replace('__SHOT_HERO_B__', img['heroB'])
       .replace('__SHOT_WHAT_A__', img['whatA'])
       .replace('__SHOT_WHAT_B__', img['whatB'])
       .replace('__SHOT_CASE_A__', img['caseA'])
       .replace('__SHOT_CASE_B__', img['caseB'])
       .replace('__SHOT_PRICE_A__', img['priceA'])
       .replace('__SHOT_PRICE_B__', img['priceB'])
       .replace('__TORN_A__', a['tornA'])
       .replace('__TORN_B__', a['tornB'])
       .replace('__TORN_C__', a['tornC'])
       .replace('__TORN_D__', a['tornD']))

# ── публичный сайт: без кода и стилей админки ─────────────────────────
ADMIN_JS = re.compile(r'/\*ADMIN:START\*/.*?/\*ADMIN:END\*/\n?', re.S)
ADMIN_HTML = re.compile(r'<!--ADMIN:START-->.*?<!--ADMIN:END-->\n?', re.S)
public = ADMIN_HTML.sub('', ADMIN_JS.sub('', out))
assert 'AdminApp' not in public and 'adm-top' not in public, 'код админки попал на сайт'
io.open(os.path.join(BASE, 'index.html'), 'w', encoding='utf-8').write(inline_fonts(public))
print('index.html собран:', len(public) // 1024, 'KB')

# ── админка: тот же сайт + редактор, поисковикам закрыта ───────────────
admin = (out.replace('const IS_ADMIN = false;', 'const IS_ADMIN = true;')
            .replace('<script type="application/ld+json">__JSONLD__</script>\n', ''))
admin = re.sub(r'<title>.*?</title>', u'<title>Админка — AppForse</title>', admin, count=1, flags=re.S)
admin = admin.replace('<meta charset="utf-8">',
                      '<meta charset="utf-8">\n<meta name="robots" content="noindex, nofollow">', 1)
io.open(os.path.join(BASE, 'admin.html'), 'w', encoding='utf-8').write(inline_fonts(admin))
print('admin.html собран:', len(admin) // 1024, 'KB')

# страница политики: подставляем только логотип
priv = io.open(os.path.join(BASE, 'privacy_template.html'), encoding='utf-8').read()
priv = priv.replace('__LOGO__', a['logo'])
io.open(os.path.join(BASE, 'privacy.html'), 'w', encoding='utf-8').write(inline_fonts(priv))
print('privacy.html собран:', len(priv) // 1024, 'KB')

# страница 404: две сборки — рядом с сайтом и в корне репозитория,
# чтобы Pages подхватывал её на любом несуществующем адресе
e404 = io.open(os.path.join(BASE, '404_template.html'), encoding='utf-8').read()
e404 = inline_fonts(e404.replace('__LOGO__', a['logo']).replace('__TORN__', a['tornB']))
io.open(os.path.join(BASE, '404.html'), 'w', encoding='utf-8').write(
    e404.replace('__HOME__', 'index.html'))
io.open(os.path.join(BASE, '..', '404.html'), 'w', encoding='utf-8').write(
    e404.replace('__HOME__', '/appforse-landing/site/'))
print('404.html собран:', len(e404) // 1024, 'KB')

env = dict(os.environ, PYTHONIOENCODING='utf-8')


def run(*args):
    r = subprocess.run([sys.executable] + [os.path.join(BASE, args[0])] + list(args[1:]),
                       capture_output=True, text=True, encoding='utf-8', env=env)
    text = (r.stdout or '') + (r.stderr or '')
    last = text.strip().splitlines()[-1] if text.strip() else args[0]
    print(last)
    if r.returncode:
        raise SystemExit(args[0] + ' упал:\n' + text[-1500:])


# JSX компилируем сразу: браузеру не нужно тащить Babel и разбирать разметку
run('compile.py', 'index.html')
run('compile.py', 'admin.html')
# JSON-LD для поисковиков: раньше сборка его не вставляла, и на сайте висела заглушка
run('seo.py')
