# -*- Encoding: utf-8

CREATED_IN_ONE_YEAR_SUFFIX = 2 << 4
SEVERAL_YEARS_CREATED_SUFFIX = 1 << 4


def str_bits36(v):
    if ord(v[0]) < 128:
        V = list(v)
        for i in range(len(V)):
            if u'A' <= v[i] <= u'Z':
                V[i] = v[i].lower()
            elif v[i] < u'a' or v[i] > u'z':
                V[i] = u'a'
        res = 0
        shift = ord(u'a')  # a - latin
    else:
        V = list(v)
        for i in range(len(V)):
            if u'А' <= v[i] <= u'Я':
                V[i] = v[i].lower()
            elif v[i] < u'а' or v[i] > u'я':
                if v[i] in [u'Ё', u'ё', u'Ѣ', u'ѣ']:
                    V[i] = u'е'
                elif v[i] in [u'І', u'і', u'I', u'i', u'Ѵ', u'ѵ']:
                    V[i] = u'и'
                elif v[i] in [u'Ѳ', u'ѳ']:
                    V[i] = u'ф'
                else:
                    V[i] = u'а'
        res = 0b100000000000000000000000000000000000  # set 35th bit
        shift = ord(u'а')  # a - rus
    bit_shift = 30
    for l in V:
        res += (ord(l) - shift) << bit_shift
        bit_shift -= 5
    return res


def author_int(s):
    names = s.replace(".", " ").replace("  ", " ").split()
    surname = names[-1] if len(names) > 0 else ""
    name = names[0] if len(names) > 1 else " "
    second_name = names[1] if len(names) > 2 else " "
    if len(surname) < 5:
        surname += " " * (5 - len(surname))
    if len(name) < 1:
        name = " "
    if len(second_name) < 1:
        second_name = " "
    v = surname[:5] + name[:1] + second_name[:1]
    return str_bits36(v)


def header_int(s):
    v = ""
    for S in list(s):
        if (ord(
                S) > 128 or u'A' <= S <= u'Z' or u'a' <= S <= u'z'):
            v = v + S
            if len(v) > 6:
                break
    if len(v) < 7:
        v += " " * (7 - len(v))
    return str_bits36(v)


def date_int(year, month, day):
    return (year << 5) + int((((month - 1) * 30.36 + day) / 365) * 32)


def date_parse_int(s):
    left_bound = s.split("-")[0]
    d = left_bound.split(".")
    year = int(d[0])
    month = int(d[1]) if len(d) > 1 else 0
    day = int(d[2]) if len(d) > 2 else 0
    return date_int(year, month, day), year


def created_years_parse_int(s):
    created_parts = s.split('-')
    _, start_year = date_parse_int(created_parts[0])
    dummy = str(start_year)
    s_year_created = dummy + '-'
    year_created = start_year << 5
    if len(created_parts) == 1:
        year_created += CREATED_IN_ONE_YEAR_SUFFIX + start_year
        s_year_created += '2-' + dummy
    else:
        _, end_year = date_parse_int(created_parts[1])
        year_created += SEVERAL_YEARS_CREATED_SUFFIX + end_year
        s_year_created += '1-' + str(end_year)
    return year_created, s_year_created


def set_sorts(doc):
    author = 0
    header = 0
    tagging = 0
    created = 0
    year_created = 3000
    s_year_created = '3000-0-3000'
    for k, v in doc["Attrs"]:
        if k == "author" and author == 0:
            author = author_int(v)
        if k == "tagging" and v == "manual":
            tagging = 1
        if k == "grcreated" and created == 0:
            year_created, s_year_created = created_years_parse_int(v)
        if k == "header" and header == 0:
            header = header_int(v)
    created_desc = 65535 - created
    tagging = 1 - tagging

    # author 36 bit
    # tagging 1 bit
    # created 16 bit
    # birthday 16 bit // not suported in poetic
    # header 36 bit (always partially lost)

    doc["Sorts"] = {
        "tagging": (tagging << 62) + (created_desc << 46) + (author << 10) + (
            header >> 26),
        "author": (author << 27) + (created << 11) + (header >> 25),
        "created": (created << 47) + (author << 11) + (header >> 25),
        "created_inv": (created_desc << 47) + (author << 11) + (header >> 25),
        'year_created': year_created,
        's_year_created': s_year_created
    }
