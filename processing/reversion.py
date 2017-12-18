# -*- coding: utf-8 -*-

from processing.doc_iters import *


def _reverse(doc, attr, rev_attr):
    for word in all_words(doc):
        if attr == "lex":
            for ana in word["Anas"]:
                val = ana["lex"]
                if val:
                    append_attr(word, rev_attr, val[::-1])
        elif attr == "form":
            val = word["Text"]
            if val:
                append_attr(word, rev_attr, val[::-1])


def set_reversed(doc):
    _reverse(doc, "lex", "rlex")
    _reverse(doc, "form", "rform")

