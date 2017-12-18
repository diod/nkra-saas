# -*- coding: utf-8 -*-

import collections

from processing.doc_iters import *

INDEX_ATTRS = frozenset((
    "flags",
    "formi",
    "formm",
    "gr",
    "lex",
    "lex_el",
    "lexi",
    "lexm",
    "rform",
    "rformi",
    "rformm",
    "rlex",
    "rlexi",
    "rlexm",
    "sem",
    "source_el",
    "Text",
    "type",
    "Attrs",
))

SERP_ATTRS = frozenset((
    "lang",
    "Punct",
    "Text",
    "Attrs",
    # Hierarchy-oriented arrts
    "_id",
    "type",
    "path",
    "prefix",
    "snippet_type",
))

INFO_ATTRS = frozenset((
    "flags",
    "gr",
    "lex",
    "lex_el",
    "sem",
    "source_el",
    "Text",
    "type",
))

C_INDEX = 0x01
C_SERP = 0x02
C_INFO = 0x04

C_ALL = C_INDEX | C_SERP | C_INFO

AttrCategory = collections.defaultdict(int)

for attr in INDEX_ATTRS:
    AttrCategory[attr] = AttrCategory.get(attr, 0) | C_INDEX

for attr in SERP_ATTRS:
    AttrCategory[attr] = AttrCategory.get(attr, 0) | C_SERP

for attr in INFO_ATTRS:
    AttrCategory[attr] = AttrCategory.get(attr, 0) | C_INFO


def split_attrs(obj, category):
    if type(obj) is list:
        return [split_attrs(item, category) for item in obj]
    elif type(obj) is dict:
        res = dict()
        for key, val in obj.items():
            if is_attr_value(val):
                if AttrCategory[key] & category:
                    res[key] = val
            else:
                res[key] = split_attrs(val, category)
        return res
    else:
        return obj
