# -*- coding: utf-8 -*-
"""Готовит картинку для соцсетей и фавиконы из логотипа."""
import io, os, json, base64
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = (r"C:\Users\greag\AppData\Local\Temp\claude\c--Users-greag-Desktop"
          r"------------1111\eab9426b-0f24-4fe6-b5fe-b82a3320af88\scratchpad\assets")
FONTS = r"C:\Windows\Fonts"
INK = (14, 12, 16)
RED = (232, 36, 60)


def load_logo():
    a = json.load(io.open(os.path.join(ASSETS, 'assets.json'), encoding='utf-8'))
    raw = base64.b64decode(a['logo'].split(',', 1)[1])
    return Image.open(io.BytesIO(raw)).convert('RGB')


def font(name, size):
    for n in (name, 'arialbd.ttf', 'arial.ttf'):
        p = os.path.join(FONTS, n)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


# ── картинка для соцсетей 1200×630 ──
og = Image.new('RGB', (1200, 630), INK)
d = ImageDraw.Draw(og)
d.rectangle([0, 0, 1200, 8], fill=RED)          # фирменная полоса сверху
d.rectangle([0, 622, 1200, 630], fill=RED)

logo = load_logo()
lw = 190
logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
og.paste(logo, (80, 74))

big = font('impact.ttf', 92)
mid = font('arial.ttf', 30)
lines = ['ГОТОВОЕ ПРИЛОЖЕНИЕ', 'ДЛЯ ВАШЕГО МАГАЗИНА']
y = 214
for ln in lines:
    d.text((80, y), ln, font=big, fill=(255, 255, 255))
    y += 104
d.text((80, y + 6), 'ЗА 7 ДНЕЙ', font=big, fill=RED)
d.text((80, 556), '150 000 ₽  ·  публикация в App Store и Google Play',
       font=mid, fill=(169, 169, 186))
og.save(os.path.join(BASE, 'og.jpg'), quality=88, optimize=True)

# ── фавиконы: логотип на фирменном красном ──
src = load_logo()
for size, name in ((180, 'apple-touch-icon.png'), (32, 'favicon-32.png'), (192, 'icon-192.png')):
    ico = Image.new('RGB', (size, size), RED)
    pad = int(size * 0.14)
    w = size - pad * 2
    lg = src.resize((w, max(1, int(src.height * w / src.width))), Image.LANCZOS)
    ico.paste(lg, (pad, (size - lg.height) // 2))
    ico.save(os.path.join(BASE, name), optimize=True)

print('og.jpg %d KB, фавиконы готовы' % (os.path.getsize(os.path.join(BASE, 'og.jpg')) // 1024))
