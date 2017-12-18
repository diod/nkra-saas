# -*- coding: utf-8 -*-

from processing.doc_iters import *


def set_first_last(doc):
    # too obvious for a docstring
    for sent in all_sents(doc):
        if not sent["Words"]:
            continue
        append_flag(sent["Words"][0], "first")
        append_flag(sent["Words"][-1], "last")


def set_capital(doc):
    # too obvious for a docstring
    for word in all_words(doc):
        if word["Text"] and word["Text"][0].isupper():
            append_flag(word, "capital")
