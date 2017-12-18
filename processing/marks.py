# -*- coding: utf-8 -*-

from processing.doc_iters import *

_MARKS = {
    '.': "dot",
    ',': "comma",
    '!': "excl",
    '?': "ques",
    ':': "colon",
    ';': "semicolon",
    '/': "slash",
    '-': "dash",
    '"': "quot",
    "'": "apos",
    '(': "lparenth",
    ')': "rparenth",
    '[': "lbracket",
    ']': "rbracket",
    '<': "langle",
    '>': "rangle",
    '{': "lbrace",
    '}': "rbrace",
    '\\': "backslash",
    u'\u2015': "dash",
    u'\u2026': "dots",
}


def set_marks(doc):
    for sent in all_sents(doc):
        words = sent["Words"]
        for i in xrange(len(words)):
            values = _inspect_marks(words[i]["Punct"])
            if values:
                append_flags(words[i], "a", values)
                if i > 0:
                    append_flags(words[i-1], "b", values)
        values = _inspect_marks(sent["Punct"])
        if values and words:
            append_flags(words[-1], "b", values)


def _inspect_marks(punct):
    # too obvious for a docstring
    values = set()
    for c in punct:
        if c in _MARKS:
            values.add(_MARKS[c])
    if "..." in punct:
        values.add("dots")
    if values:
        values.add("mark")
    return values


def normalize_punct(doc):
    # too obvious for a docstring
    for word in all_words(doc):
        word["Punct"] = _normalize_punct_str(word["Punct"])
    for sent in all_sents(doc):
        sent["Punct"] = _normalize_punct_str(sent["Punct"])


def _normalize_punct_str(punct):
    # too obvious for a docstring
    punct = punct.replace("---", u"\u2015")
    punct = punct.replace("--", u"\u2015")
    punct = punct.replace(" - ", u"\u2015")
    punct = punct.replace("...", u"\u2026")
    return punct


