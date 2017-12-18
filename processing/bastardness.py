# -*- coding: utf-8 -*-

from processing.doc_iters import *


def move_bastardness_to_flags(doc):
    for word in all_words(doc):
        bastardness = None
        for ana in word["Anas"]:
            if "gr" not in ana:
                continue
            grammems = ana["gr"].split(",")
            for tag in ("norm", "bastard"):
                if tag in grammems:
                    grammems.remove(tag)
                    bastardness = tag
            ana["gr"] = ",".join(grammems)
        if bastardness:
            append_flag(word, bastardness)
