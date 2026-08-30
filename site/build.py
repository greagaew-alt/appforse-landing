# -*- coding: utf-8 -*-
"""Собирает design/index.html: шаблон + ассеты (логотип, скриншоты, рваный край)."""
import json, io, os

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = r"C:\Users\greag\AppData\Local\Temp\claude\c--Users-greag-Desktop------------1111\eab9426b-0f24-4fe6-b5fe-b82a3320af88\scratchpad\assets\assets.json"

a = json.load(open(ASSETS, encoding='utf-8'))
tpl = io.open(os.path.join(BASE, 'template.html'), encoding='utf-8').read()

out = (tpl
       .replace('__LOGO__', a['logo'])
       .replace('__SHOT1__', a['shot1'])
       .replace('__SHOT2__', a['shot2'])
       .replace('__TAPE__', a['tape'])
       .replace('__TORN_A__', a['tornA'])
       .replace('__TORN_B__', a['tornB']))

io.open(os.path.join(BASE, 'index.html'), 'w', encoding='utf-8').write(out)
print('index.html собран:', len(out) // 1024, 'KB')
