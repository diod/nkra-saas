# -*- coding: utf-8 -*-

from processing.doc_iters import *


def set_rhyme(doc):
    for word in all_words(doc):
        if "Rhyme" in word:
            append_flag(word, "rhyme")
