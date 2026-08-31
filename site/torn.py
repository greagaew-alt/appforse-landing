# -*- coding: utf-8 -*-
"""Генерирует линии обрыва бумаги: у каждой границы своя, не отражение соседней."""
import io, os, json, math, random

ASSETS = (r"C:\Users\greag\AppData\Local\Temp\claude\c--Users-greag-Desktop"
          r"------------1111\eab9426b-0f24-4fe6-b5fe-b82a3320af88\scratchpad\assets")
W, H = 1600.0, 60.0


def edge(seed, base, spread):
    """Кромка разрыва: крупная волна + мелкие сколы + редкие резкие срывы."""
    rnd = random.Random(seed)
    ph1, ph2 = rnd.uniform(0, 6.3), rnd.uniform(0, 6.3)
    pts, x = [], 0.0
    while x < W:
        wave = (math.sin(x / 240.0 + ph1) * spread * .5 +
                math.sin(x / 61.0 + ph2) * spread * .34)
        y = base + wave + rnd.uniform(-spread * .55, spread * .55)
        if rnd.random() < .3:                       # резкий скол
            y += rnd.choice((-1, 1)) * spread * rnd.uniform(.8, 1.5)
        y = max(3.0, min(H - 3.0, y))
        pts.append((round(x, 1), round(y, 1)))
        x += rnd.uniform(9, 30)
    pts.append((W, round(base, 1)))
    return pts


def path_top(seed):
    """Вход в красную секцию: красная фигура снизу, рваный верх.
    Фон SVG прозрачный — сверху просто виден тёмный фон страницы,
    поэтому полоска на стыке физически невозможна."""
    pts = edge(seed, H * .42, H * .42)
    d = ['M0,%g' % (H + 10), 'L%g,%g' % (W, H + 10)]
    for x, y in reversed(pts):
        d.append('L%g,%g' % (x, y))
    d.append('Z')
    return ' '.join(d)


def path_bottom(seed):
    """Выход из красной секции: красная фигура сверху, рваный низ."""
    pts = edge(seed, H * .58, H * .42)
    d = ['M0,-10', 'L%g,-10' % W]
    for x, y in reversed(pts):
        d.append('L%g,%g' % (x, y))
    d.append('Z')
    return ' '.join(d)


p = os.path.join(ASSETS, 'assets.json')
a = json.load(io.open(p, encoding='utf-8'))
a['tornA'] = path_top(1704)      # вход в первую красную секцию
a['tornB'] = path_bottom(5312)   # выход из неё
a['tornC'] = path_top(8829)      # вход во вторую
a['tornD'] = path_bottom(2461)   # выход из второй
json.dump(a, io.open(p, 'w', encoding='utf-8'))
for k in ('tornA', 'tornB', 'tornC', 'tornD'):
    print('%s: %d точек' % (k, a[k].count('L')))
