# -*- coding: utf-8 -*-

import copy

from common.hierarchy import slice_by_type
from common.doc_iters import all_sents

# A list of fields that should be inherited by each align part from the full
# document
INHERITED_FIELDS = [
    "snippet_type",
    "context",
    "prefix"
]


def make_aligned_parts(doc):
    """
    Splits the doc into parts aligned by doc["align_by"]. Each part has its
    own hierarchy (because each part will be treated as a separate document).
    See common.utils.tree_slice_by_type for splitting details.

    Indices in each part's hierarchy are shifted.

    """
    align_by = doc["align_by"]
    item_type = "%s:top" % doc["prefix"]
    item_top = {
        "type": item_type, "_id": "%s:0" % item_type, "items": doc["items"],
        "Attrs": doc["Attrs"]
    }
    parts = list()
    align_items = slice_by_type(item_top, align_by)
    doc_sents = list(all_sents(doc))
    if not align_items:
        raise Exception(
            "No aligned items: perhaps wrong align type: %s?" % align_by)
    for item in align_items:
        start = item["index"]["start"]["sent"]
        end = item["index"]["end"]["sent"]
        sents = doc_sents[start:end]
        shift_sent_indices_neg(item, start)
        for field in INHERITED_FIELDS:
            item[field] = doc[field]
        parts.append({
            "Sents": sents,
            "Hierarchy": item,
        })
    doc["Parts"] = parts


def shift_sent_indices_neg(item_top, shift):
    item_top["index"]["start"]["sent"] -= shift
    item_top["index"]["end"]["sent"] -= shift
    if "items" in item_top:
        for item in item_top["items"]:
            shift_sent_indices_neg(item, shift)


def shift_sent_indices_split(item_top, split_item_idx):
    if "index" in item_top:
        start = item_top["index"]["start"]["sent"]
        end = item_top["index"]["end"]["sent"]
        if start <= split_item_idx < end:
            item_top["index"]["end"]["sent"] += 1
        if start > split_item_idx:
            item_top["index"]["start"]["sent"] += 1
            item_top["index"]["end"]["sent"] += 1
    if "items" in item_top:
        for item in item_top["items"]:
            shift_sent_indices_split(item, split_item_idx)


def split_long_sentences(doc):
    """
    Actually does what it says. Long sentences are those sentences that are
    longer that 64 words.

    :returns: None, just modifies the document.

    """
    total_seen = 0
    for part in doc["Parts"]:
        sents = part["Sents"]
        i = 0
        while i < len(sents):
            sent = sents[i]
            if len(sent["Words"]) >= 64:
                rest_sent = copy.deepcopy(sent)
                rest_sent["Words"] = rest_sent["Words"][63:]
                sent["Words"] = sent["Words"][:63]
                sent["Punct"] = ""
                sents.insert(i + 1, rest_sent)
                shift_sent_indices_split(doc, i + total_seen)
                i = 0
                continue
            i += 1
        total_seen += len(sents)
