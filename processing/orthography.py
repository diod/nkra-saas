# -*- coding: utf-8 -*-

from processing.doc_iters import all_words, append_attr
from simplifier_all import simplify_inner, simplify_modern
from simplifier_orth import orth_simplify_inner, orth_simplify_modern


def simplify_orthography(doc, subcorpus):
    for word in all_words(doc):
        _simplify_attr(subcorpus, word, "form", word["Text"])
        for ana in word["Anas"]:
            _simplify_attr(subcorpus, word, "lex", ana["lex"])


def _simplify_attr(subcorpus, node, attr, value):
    if subcorpus in ["orthlib"]:
        append_attr(node, attr + "i", orth_simplify_inner(value))
        append_attr(node, attr + "m", orth_simplify_modern(value))
    else:
        append_attr(node, attr + "i", simplify_inner(value))
        append_attr(node, attr + "m", simplify_modern(value))
