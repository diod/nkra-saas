# -*- coding: utf-8 -*-

from processing.doc_iters import *


def _reverse(doc, attr, rev_attr, is_should_keep_accents):
    for word in all_words(doc):
        if attr == "lex":
            for ana in word["Anas"]:
                val = ana["lex"]
                if val:
                    append_attr(word, rev_attr, val[::-1])
        elif attr == "form":
            val = word["Text"]
            if is_should_keep_accents:
                val = val.replace(u'\u0300', '').replace(u'\u0301', '').replace('`', '')
            if val:
                append_attr(word, rev_attr, val[::-1])


def set_reversed(doc, is_should_keep_accents):
    _reverse(doc, "lex", "rlex", is_should_keep_accents)
    _reverse(doc, "form", "rform", is_should_keep_accents)

