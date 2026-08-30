# -*- coding: utf-8 -*-
"""Типографика: предлоги и союзы не остаются в конце строки, тире не начинает строку,
число не отрывается от единицы. Правит только текст, разметку и код не трогает."""
import io, os, re, sys

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template.html')
NB = u' '

# предлоги, союзы и частицы, после которых нельзя переносить
SHORT = set((u'в во на но и а с со к ко о об обо от ото до за из изо по при для без над под '
             u'про у не ни что как же бы ли то их его её или да чем уже там где чтобы если '
             u'все всё это так тех кто ещё был была было были есть').split())

# устойчивые пары, которые нельзя рвать
PAIRS = [(u'App Store', u'App' + NB + u'Store'),
         (u'Google Play', u'Google' + NB + u'Play'),
         (u'₽/мес', u'₽/мес')]


def typo(t):
    if NB in t and u' ' not in t:
        return t
    # предлог или союз склеивается со следующим словом
    t = re.sub(u'(?<![\\wЀ-ӿ])([\\wЀ-ӿ]{1,6})[ ]',
               lambda m: m.group(1) + NB if m.group(1).lower() in SHORT else m.group(0), t)
    t = re.sub(u'[ ]—', NB + u'—', t)          # тире остаётся на строке со своим словом
    # последнее слово не остаётся одно на строке: склеиваем его с предыдущим
    t = re.sub(u'[ ]([^ ]+)$', lambda m: NB + m.group(1), t)
    t = re.sub(u'(\\d)[ ](?=[\\dЀ-ӿ₽])', u'\\1' + NB, t)   # 7 дней, 150 000 ₽
    for a, b in PAIRS:
        t = t.replace(a, b)
    return t


s = io.open(P, encoding='utf-8').read()
head, sep, code = s.partition('<script type="text/babel">')
if not sep:
    sys.exit('не найден блок с разметкой')

n = [0]

# 1. строковые литералы в массивах с содержанием
def fix_data(m):
    inner = m.group(1)
    out = typo(inner)
    if out != inner:
        n[0] += 1
    return u"'" + out + u"'"

start = code.index('const NAV')
end = code.index('/* ─────────── мелкие детали')
data, rest = code[start:end], code[end:]
data = re.sub(u"'([^'\\\\\n]{4,})'", fix_data, data)

# 2. текстовые узлы разметки: между тегами, без выражений в фигурных скобках
def fix_jsx(m):
    inner = m.group(1)
    if not re.search(u'[Ѐ-ӿ]', inner):
        return m.group(0)
    out = typo(inner)
    if out != inner:
        n[0] += 1
    return u'>' + out + u'<'

rest = re.sub(u'>([^<>{}]{4,}?)<', fix_jsx, rest, flags=re.S)

io.open(P, 'w', encoding='utf-8').write(head + sep + code[:start] + data + rest)
print('обработано фрагментов текста: %d' % n[0])
