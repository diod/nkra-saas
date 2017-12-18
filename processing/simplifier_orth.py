# -*- coding: utf-8 -*-


def orth_simplify_exact(s):
    # lowercase all
    s = s.lower()
    # remove accents
    s = s.replace(u'\u0300', u'').replace(
        u'\u0301', u'').replace(u'\u0302', u'')
    s = s.replace(u'\u030f', u'')  # ѷ
    return s


# Внутреннее (упрощенное) представление
def orth_simplify_inner(s):
    s = orth_simplify_exact(s)
    s = s.replace(u'\u0311', u'')  # letter-titlo = с̑ р̑ о̑
    t = {
        u'є': u'е', u'ѻ': u'о', u'ѽ': u'ѡ', u'ѿ': u'ѡт'
    }
    res = u""
    for c in s:
        res += t.get(c, c)
    return res


# Модернизированное представление
def orth_simplify_modern(s):
    s = orth_simplify_inner(s)
    s = s.replace(u'\u0483', u'')  # titlo = ҃
    s = s.replace(u'аѵ', u'ав').replace(u'еѵ', u'ев')
    t = {
        u'ѣ': u'е', u'ѡ': u'о',
        u'і': u'и', u'ѵ': u'и',
        u'ѕ': u'з', u'ѳ': u'ф',
        u'ѯ': u'кс', u'ѱ': u'пс'
    }
    res = u""
    for c in s:
        res += t.get(c, c)
    if (res.endswith(u"ъ") or res.endswith(u"Ъ")):
        res = res[:-1]
    return res


if __name__ == "__main__":
    pass
