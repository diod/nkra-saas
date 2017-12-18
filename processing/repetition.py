# -*- coding: utf-8 -*-

from grammemes import *
from processing.doc_iters import *


def set_repetitions(doc):
    for sent in all_sents(doc):
        words = sent["Words"]
        if not words:
            continue
        _check_grammeme_repetition(words, 1, "posred", PARTS_OF_SPEECH)
        _check_grammeme_repetition(words, 1, "genderred", GENDERS)
        _check_grammeme_repetition(words, 1, "numred", NUMBERS)
        _check_grammeme_repetition(words, 1, "casered", CASES)
        _check_grammeme_repetition(words, 1, "timered", TENSES)
        _check_grammeme_repetition(words, 1, "persred", PERSONS)
        _check_grammeme_repetition(words, 1, "animred", ANIMATES)
        _check_attr_repetition(words, 1, "lexred", "lex")


def _check_grammeme_repetition(words, shift, flag, category):
    # this is done to pass the @category value to _has_common_grammeme
    predicate = lambda w1, w2: _has_common_grammeme(w1, w2, category)
    return _check_predicate(words, shift, flag, predicate)


def _check_predicate(words, shift, flag, predicate):
    for i in xrange(len(words) - shift):
        if predicate(words[i], words[i + shift]):
            append_flag(words[i + shift], flag)


def _has_common_grammeme(word1, word2, category):
    grammemes1 = _extract_grammemes(word1, category)
    grammemes2 = _extract_grammemes(word2, category)
    return not grammemes1.isdisjoint(grammemes2)


def _extract_grammemes(word, category):
    result = set()
    for ana in word["Anas"]:
        grammemes = set(ana.get("gr", "").split(","))
        result |= grammemes.intersection(category)
    return result


def _has_common_attr(word1, word2, attr):
    val1 = word1.get(attr)
    val2 = word2.get(attr)
    return val1 is not None and val1 == val2


def _check_attr_repetition(words, shift, flag, attr):
    predicate = lambda w1, w2: _has_common_attr(w1, w2, attr)
    return _check_predicate(words, shift, flag, predicate)


