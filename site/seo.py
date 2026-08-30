# -*- coding: utf-8 -*-
"""Структурированные данные, robots и карта сайта.
Разметка собирается из тех же текстов, что видит человек, — чтобы не разъезжались."""
import io, os, re, json

BASE = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://greagaew-alt.github.io/appforse-landing/site/'

tpl = io.open(os.path.join(BASE, 'template.html'), encoding='utf-8').read()


def block(name):
    m = re.search(r"const " + name + r" = \[(.*?)\n\];", tpl, re.S)
    if not m:
        raise SystemExit('не найден массив ' + name)
    return m.group(1)


def nb(t):
    """неразрывные пробелы нужны вёрстке, но не поисковику"""
    return t.replace(u' ', ' ').strip()


pairs = re.findall(r"\['([^']+)',\s*\n?\s*'([^']+)'\]", block('FAQ'))
included = re.findall(r"^\s*'([^']+)',", block('INCLUDED'), re.M)
audience = re.findall(r"t: '([^']+)'", block('AUDIENCE'))
if not pairs or not included:
    raise SystemExit('не удалось разобрать тексты для разметки')

graph = [
    {"@type": "Organization", "@id": SITE + "#org", "name": "AppForse",
     "url": SITE, "logo": SITE + "icon-192.png", "image": SITE + "og.jpg",
     "description": "Готовая платформа мобильных приложений для торговли "
                    "под брендом заказчика",
     "sameAs": ["https://vk.com/appforse", "https://t.me/shark154"],
     "contactPoint": [{"@type": "ContactPoint", "contactType": "sales",
                       "url": "https://t.me/shark154", "availableLanguage": "Russian"}]},
    {"@type": "WebSite", "@id": SITE + "#site", "url": SITE, "name": "AppForse",
     "inLanguage": "ru-RU", "publisher": {"@id": SITE + "#org"}},
    {"@type": "WebPage", "@id": SITE + "#page", "url": SITE,
     "name": "Мобильное приложение под вашим брендом за 7 дней — AppForse",
     "isPartOf": {"@id": SITE + "#site"}, "about": {"@id": SITE + "#org"},
     "inLanguage": "ru-RU", "primaryImageOfPage": SITE + "og.jpg"},
    {"@type": "Service", "@id": SITE + "#service",
     "name": "Запуск мобильного приложения под брендом заказчика",
     "serviceType": "Разработка мобильного приложения на готовой платформе",
     "provider": {"@id": SITE + "#org"},
     "areaServed": {"@type": "Country", "name": "Россия"},
     "audience": [{"@type": "BusinessAudience", "name": nb(a)} for a in audience],
     "description": "Клиентское приложение и админ-панель под брендом заказчика: "
                    "каталог, заказы, доставка, оплата, бонусы, push-уведомления и CRM. "
                    "Публикация в App Store и Google Play за 7 рабочих дней.",
     "offers": {"@type": "Offer", "price": "150000", "priceCurrency": "RUB",
                "availability": "https://schema.org/InStock", "url": SITE + "#price",
                "itemOffered": {"@type": "Service",
                                "name": "Запуск платформы под вашим брендом"}},
     "hasOfferCatalog": {"@type": "OfferCatalog", "name": "В стоимость входит",
                         "itemListElement": [
                             {"@type": "Offer",
                              "itemOffered": {"@type": "Service", "name": nb(t)}}
                             for t in included]}},
    {"@type": "FAQPage", "@id": SITE + "#faq",
     "mainEntity": [{"@type": "Question", "name": nb(q),
                     "acceptedAnswer": {"@type": "Answer", "text": nb(a)}}
                    for q, a in pairs]},
]
ld = json.dumps({"@context": "https://schema.org", "@graph": graph},
                ensure_ascii=False, separators=(',', ':'))

p = os.path.join(BASE, 'index.html')
html = io.open(p, encoding='utf-8').read()
if '__JSONLD__' not in html:
    raise SystemExit('в index.html нет места для разметки')
io.open(p, 'w', encoding='utf-8').write(html.replace('__JSONLD__', ld))

# ── robots и карта сайта ──
io.open(os.path.join(BASE, 'robots.txt'), 'w', encoding='utf-8').write(
    "User-agent: *\nAllow: /\nDisallow: /privacy.html\n\nSitemap: " + SITE + "sitemap.xml\n")

io.open(os.path.join(BASE, 'sitemap.xml'), 'w', encoding='utf-8').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    '  <url>\n'
    '    <loc>' + SITE + '</loc>\n'
    '    <lastmod>2026-08-31</lastmod>\n'
    '    <changefreq>monthly</changefreq>\n'
    '    <priority>1.0</priority>\n'
    '  </url>\n'
    '</urlset>\n')

print('разметка: вопросов %d, пунктов тарифа %d, аудиторий %d; robots и sitemap готовы'
      % (len(pairs), len(included), len(audience)))
