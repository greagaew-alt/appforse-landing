# -*- coding: utf-8 -*-
"""Компилирует JSX заранее, чтобы браузеру не пришлось тащить и запускать Babel.
Экономит около 500 КБ загрузки и заметную паузу на телефоне."""
import io, os, re, json, subprocess, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
BABEL = os.path.join(BASE, '_babel.js')
SRC = 'https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.26.4/babel.min.js'

if not os.path.exists(BABEL):
    req = urllib.request.Request(SRC, headers={'User-Agent': 'Mozilla/5.0'})
    io.open(BABEL, 'wb').write(urllib.request.urlopen(req, timeout=60).read())
    print('babel скачан:', os.path.getsize(BABEL) // 1024, 'KB')

p = os.path.join(BASE, 'index.html')
html = io.open(p, encoding='utf-8').read()

m = re.search(r'<script type="text/babel">(.*?)</script>', html, re.S)
if not m:
    raise SystemExit('в index.html нет JSX — уже скомпилирован')
jsx = m.group(1)

runner = os.path.join(BASE, '_run.js')
io.open(runner, 'w', encoding='utf-8').write(
    "const Babel = require(%s);\n"
    "const fs = require('fs');\n"
    "const src = fs.readFileSync(%s, 'utf8');\n"
    "const out = Babel.transform(src, { presets: [['react', { runtime: 'classic' }]] }).code;\n"
    "fs.writeFileSync(%s, out, 'utf8');\n"
    % (json.dumps(BABEL), json.dumps(os.path.join(BASE, '_jsx.txt')),
       json.dumps(os.path.join(BASE, '_out.js'))))
io.open(os.path.join(BASE, '_jsx.txt'), 'w', encoding='utf-8').write(jsx)

r = subprocess.run(['node', runner], capture_output=True, text=True)
if r.returncode:
    raise SystemExit('babel не отработал: ' + (r.stderr or '')[:400])
js = io.open(os.path.join(BASE, '_out.js'), encoding='utf-8').read()

html = html[:m.start()] + '<script>\n' + js + '\n</script>' + html[m.end():]
html = re.sub(r'\s*<script src="[^"]*babel[^"]*"></script>', '', html)
io.open(p, 'w', encoding='utf-8').write(html)

for f in ('_run.js', '_jsx.txt', '_out.js'):
    q = os.path.join(BASE, f)
    if os.path.exists(q):
        os.remove(q)
print('JSX скомпилирован, Babel из страницы убран; index.html %d KB'
      % (os.path.getsize(p) // 1024))
