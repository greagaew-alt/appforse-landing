# -*- coding: utf-8 -*-
"""Собирает design/index.html: шаблон + ассеты (логотип, скриншоты, рваный край)."""
import json, io, os

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = r"C:\Users\greag\AppData\Local\Temp\claude\c--Users-greag-Desktop------------1111\eab9426b-0f24-4fe6-b5fe-b82a3320af88\scratchpad\assets\assets.json"

a = json.load(open(ASSETS, encoding='utf-8'))
tpl = io.open(os.path.join(BASE, 'template.html'), encoding='utf-8').read()

# картинки лежат отдельными файлами: страница перестаёт весить почти мегабайт
# и рисуется, не дожидаясь их загрузки
img = json.load(io.open(os.path.join(BASE, 'img', 'paths.json'), encoding='utf-8'))

out = (tpl
       .replace('__LOGO__', img['logo'])
       .replace('__SHOT1__', img['shot1'])
       .replace('__SHOT2__', img['shot2'])
       .replace('__TAPE__', img['tape'])
       .replace('__TORN_A__', a['tornA'])
       .replace('__TORN_B__', a['tornB'])
       .replace('__TORN_C__', a['tornC'])
       .replace('__TORN_D__', a['tornD']))

io.open(os.path.join(BASE, 'index.html'), 'w', encoding='utf-8').write(out)
print('index.html собран:', len(out) // 1024, 'KB')

# страница политики: подставляем только логотип
priv = io.open(os.path.join(BASE, 'privacy_template.html'), encoding='utf-8').read()
priv = priv.replace('__LOGO__', a['logo'])
io.open(os.path.join(BASE, 'privacy.html'), 'w', encoding='utf-8').write(priv)
print('privacy.html собран:', len(priv) // 1024, 'KB')

# страница 404: две сборки — рядом с сайтом и в корне репозитория,
# чтобы Pages подхватывал её на любом несуществующем адресе
e404 = io.open(os.path.join(BASE, '404_template.html'), encoding='utf-8').read()
e404 = e404.replace('__LOGO__', a['logo']).replace('__TORN__', a['tornB'])
io.open(os.path.join(BASE, '404.html'), 'w', encoding='utf-8').write(
    e404.replace('__HOME__', 'index.html'))
io.open(os.path.join(BASE, '..', '404.html'), 'w', encoding='utf-8').write(
    e404.replace('__HOME__', '/appforse-landing/site/'))
print('404.html собран:', len(e404) // 1024, 'KB')

# JSX компилируем сразу: браузеру не нужно тащить Babel и разбирать разметку
import subprocess as _sp
_r = _sp.run(['python', os.path.join(BASE, 'compile.py')], capture_output=True, text=True)
print((_r.stdout or _r.stderr).strip().splitlines()[-1] if (_r.stdout or _r.stderr) else 'compile.py')
