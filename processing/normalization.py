# -*- coding: utf-8 -*-

from processing.doc_iters import all_words


def normalize_accents(doc):
    """
    For each word in a document, removes U+0300 code points from word strings
    and stores info about those points in word["Attrs"]["Accents"].

    """
    for word in all_words(doc):
        t, a = normalize_accents_str(word["Text"])
        word["Text"] = t
        if a:
            if "Attrs" not in word:
                word["Attrs"] = {}
            word["Attrs"] = ["Accents", ",".join(map(str, a))]


def normalize_accents_str(s):
    """
    Deals exclusively with Unicode Character 'COMBINING GRAVE ACCENT' (U+0300).

    :returns: the string without any U+0300 code points and a list of indixes
              of the removed points.

    """
    a = list()
    pos = s.find(u'`')
    while 0 <= pos < len(s):
        s = s[:pos] + s[pos + 1:]
        a.append(pos)
        pos = s.find(u'`', pos)
    pos = s.find(u"\u0301")
    while 0 <= pos < len(s):
        s = s[:pos] + s[pos + 1:]
        a.append(pos)
        pos = s.find(u"\u0301", pos)
    return s, a
