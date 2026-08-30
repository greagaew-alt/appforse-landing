# -*- coding: utf-8 -*-
"""Забирает шрифты с Google Fonts и кладёт рядом с сайтом: в России CDN нестабилен,
а без своего шрифта метрики уезжают и строки налезают друг на друга."""
import io, os, re, sys, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, 'fonts')
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0 Safari/537.36')
API = ('https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700'
       '&family=Manrope:wght@400;500;600;800&display=swap')


def get(url):
    r = urllib.request.Request(url, headers={'User-Agent': UA})
    return urllib.request.urlopen(r, timeout=40).read()


css = get(API).decode('utf-8')
faces = re.findall(r'/\* ([\w-]+) \*/\s*@font-face \{(.*?)\}', css, re.S)
keep = {'cyrillic', 'cyrillic-ext', 'latin', 'latin-ext'}
rules = []
n = 0
for subset, body in faces:
    if subset not in keep:
        continue
    fam = re.search(r"font-family: '([^']+)'", body).group(1)
    wt = re.search(r'font-weight: (\d+)', body).group(1)
    url = re.search(r'url\((https://[^)]+\.woff2)\)', body).group(1)
    rng = re.search(r'unicode-range: ([^;]+);', body).group(1)
    name = '%s-%s-%s.woff2' % (fam.lower(), wt, subset)
    path = os.path.join(OUT, name)
    if not os.path.exists(path):
        io.open(path, 'wb').write(get(url))
        n += 1
    rules.append("@font-face{font-family:'%s';font-style:normal;font-weight:%s;font-display:swap;"
                 "src:url(fonts/%s) format('woff2');unicode-range:%s}" % (fam, wt, name, rng))

io.open(os.path.join(BASE, 'fonts.css'), 'w', encoding='utf-8').write('\n'.join(rules))
size = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT)) // 1024
print('скачано файлов: %d, всего в папке: %d файлов, %d KB, правил @font-face: %d'
      % (n, len(os.listdir(OUT)), size, len(rules)))
