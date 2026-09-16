# -*- coding: utf-8 -*-
"""Компилирует JSX заранее, чтобы браузеру не пришлось тащить и запускать Babel.
Экономит около 500 КБ загрузки и заметную паузу на телефоне.
Запуск: py compile.py index.html   (или admin.html)"""
import io, os, re, json, subprocess, sys, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
BABEL = os.path.join(BASE, '_babel.js')
SRC = 'https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.26.4/babel.min.js'

if not os.path.exists(BABEL):
    req = urllib.request.Request(SRC, headers={'User-Agent': 'Mozilla/5.0'})
    io.open(BABEL, 'wb').write(urllib.request.urlopen(req, timeout=60).read())
    print('babel скачан:', os.path.getsize(BABEL) // 1024, 'KB')

name = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
p = os.path.join(BASE, name)
html = io.open(p, encoding='utf-8').read()

m = re.search(r'<script type="text/babel">(.*?)</script>', html, re.S)
if not m:
    raise SystemExit(name + ': JSX не найден — уже скомпилирован')
jsx = m.group(1)

tag = re.sub(r'\W', '_', name)
runner = os.path.join(BASE, '_run_' + tag + '.js')
src_txt = os.path.join(BASE, '_jsx_' + tag + '.txt')
out_js = os.path.join(BASE, '_out_' + tag + '.js')
io.open(runner, 'w', encoding='utf-8').write(
    "const Babel = require(%s);\n"
    "const fs = require('fs');\n"
    "const src = fs.readFileSync(%s, 'utf8');\n"
    "const out = Babel.transform(src, { presets: [['react', { runtime: 'classic' }]] }).code;\n"
    "fs.writeFileSync(%s, out, 'utf8');\n"
    % (json.dumps(BABEL), json.dumps(src_txt), json.dumps(out_js)))
io.open(src_txt, 'w', encoding='utf-8').write(jsx)

r = subprocess.run(['node', runner], capture_output=True, text=True, encoding='utf-8')
try:
    if r.returncode:
        raise SystemExit(name + ': babel не отработал: ' + (r.stderr or '')[:1500])
    js = io.open(out_js, encoding='utf-8').read()
finally:
    for f in (runner, src_txt, out_js):
        if os.path.exists(f):
            os.remove(f)

html = html[:m.start()] + '<script>\n' + js + '\n</script>' + html[m.end():]
html = re.sub(r'\s*<script src="[^"]*babel[^"]*"></script>', '', html)
io.open(p, 'w', encoding='utf-8').write(html)
print('%s: JSX скомпилирован, Babel убран; %d KB' % (name, os.path.getsize(p) // 1024))
