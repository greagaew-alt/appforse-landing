# -*- coding: utf-8 -*-
"""Прогон страницы по ширинам: ищет переполнение, вылезающие элементы,
мелкий текст и обрезанное содержимое."""
import io, os, sys
from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.abspath(__file__))
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
url = 'file:///' + os.path.join(BASE, PAGE).replace(os.sep, '/')

WIDTHS = [(1920, 1080), (1680, 1050), (1440, 900), (1280, 800), (1180, 820),
          (1024, 768), (900, 1200), (834, 1112), (768, 1024), (640, 960),
          (540, 960), (430, 932), (414, 896), (390, 844), (360, 800), (320, 568)]

CHECK = """() => {
  const out = { ovx: document.documentElement.scrollWidth - document.documentElement.clientWidth,
                wide: [], small: [], clipped: [], touch: [] };
  const vw = document.documentElement.clientWidth;
  const seen = new Set();
  document.querySelectorAll('body *').forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || !el.offsetParent && cs.position !== 'fixed') {
      if (cs.position !== 'sticky' && cs.position !== 'fixed' && !el.offsetHeight) return;
    }
    const b = el.getBoundingClientRect();
    if (b.width === 0 && b.height === 0) return;
    const tag = el.tagName.toLowerCase() + (el.className && typeof el.className === 'string'
      ? '.' + el.className.trim().split(/\\s+/).slice(0, 2).join('.') : '');
    // вылезает за экран
    if (b.right > vw + 1.5 || b.left < -1.5) {
      const key = 'w' + tag;
      if (!seen.has(key)) { seen.add(key);
        out.wide.push(tag + ' [' + Math.round(b.left) + '…' + Math.round(b.right) + ']'); }
    }
    // содержимое не помещается в свой блок
    if (el.scrollWidth > el.clientWidth + 2 && cs.overflowX === 'visible'
        && el.clientWidth > 0 && !el.closest('.circle') && !el.querySelector('.circle')
        && !el.closest('.fv-play') && !el.querySelector('.fv-play')) {
      const key = 'c' + tag;
      if (!seen.has(key)) { seen.add(key);
        out.clipped.push(tag + ' (' + el.scrollWidth + ' в ' + el.clientWidth + ')'); }
    }
    // мелкий текст
    const txt = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (txt) {
      const fs = parseFloat(cs.fontSize);
      if (fs < 12) { const key = 's' + tag;
        if (!seen.has(key)) { seen.add(key); out.small.push(tag + ' ' + fs.toFixed(1) + 'px'); } }
    }
    // мелкие цели нажатия
    const inline = el.tagName === 'A' && cs.display === 'inline';
    if (['a', 'button', 'input', 'label'].includes(el.tagName.toLowerCase()) && !inline
        && b.height > 0 && b.height < 32 && b.width < 200) {
      const key = 't' + tag;
      if (!seen.has(key)) { seen.add(key);
        out.touch.push(tag + ' ' + Math.round(b.width) + '×' + Math.round(b.height)); }
    }
  });
  return out;
}"""

rows = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in WIDTHS:
        pg = b.new_page(viewport={'width': w, 'height': h})
        pg.goto(url)
        pg.wait_for_timeout(2600 if w == WIDTHS[0][0] else 1400)
        pg.evaluate("document.querySelectorAll('.rise').forEach(e => e.classList.add('seen'))")
        pg.wait_for_timeout(400)
        d = pg.evaluate(CHECK)
        bad = []
        if d['ovx'] > 0:
            bad.append('скролл вбок %dpx' % d['ovx'])
        if d['wide']:
            bad.append('за экран: ' + '; '.join(d['wide'][:4]))
        if d['clipped']:
            bad.append('не влезает: ' + '; '.join(d['clipped'][:4]))
        if d['small']:
            bad.append('мелкий текст: ' + '; '.join(d['small'][:3]))
        if d['touch'] and w <= 768:
            bad.append('мелкие кнопки: ' + '; '.join(d['touch'][:3]))
        rows.append('%4d×%-4d %s' % (w, h, ' | '.join(bad) if bad else 'ок'))
        if w in (390, 768, 1024):
            pg.screenshot(path=os.path.join(BASE, '_shots', 'w%d.png' % w), full_page=True)
        pg.close()
    b.close()

txt = '\n'.join(rows)
io.open(os.path.join(BASE, '_adapt.txt'), 'w', encoding='utf-8').write(txt)
print(txt)
