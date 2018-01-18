# -*- coding: utf-8 -*-

import json

from common.doc_iters import all_sents
from common import xml2json
from processing import partition, normalization, marks, positions, repetition
from processing import reversion, groupattrs, bastardness, sorts, rhyme
from processing import orthography
from index import attrs


def need_simplified_orthography(subcorpus):
    return subcorpus in ('birchbark', 'mid_rus', 'old_rus', 'orthlib')


def should_keep_accents(subcorpus):
    return subcorpus in ('poetic', 'accent', 'accent_stihi', 'spoken', 'murco')


def has_media(subcorpus):
    return subcorpus in ('murco', 'multiparc')


def is_multilangual(subcorpus):
    return subcorpus in ('para', 'multi')


def prepare(inpath, subcorpus='', split=True, corpus_type=None):
    """Prepares a corpus document for uploading.

    Args:
        inpath: Path to the .xml file with a corpus document.
        subcorpus: (str) An identifier of a corpus type (triggers special
            processing routines, e.g. generating simplified orthography).
            WARNING: this parameter, coupled with `corpus_type`, might be
            redundant; we should consider getting rid of it.
        corpus_type: (str) Used as a key to look up "environmental"
            variables in `xml2json.KNOWN_CORPUS_TYPES`.
    Returns:
        The mutated doc in JSON format.
    """
    doc = xml2json.process(inpath, corpus_type=corpus_type)
    if split:
        partition.split_long_sentences(doc)
        partition.make_aligned_parts(doc)
    if not should_keep_accents(subcorpus):
        normalization.normalize_accents(doc)
    marks.normalize_punct(doc)
    marks.set_marks(doc)
    positions.set_first_last(doc)
    positions.set_capital(doc)
    repetition.set_repetitions(doc)
    reversion.set_reversed(doc)
    groupattrs.set_groupattrs(doc)
    bastardness.move_bastardness_to_flags(doc)
    sorts.set_sorts(doc)
    if should_keep_accents(subcorpus):
        rhyme.set_rhyme(doc)
    if need_simplified_orthography(subcorpus):
        orthography.simplify_orthography(doc, subcorpus)
    return doc


def prepare_multifile(inpaths, subcorpus="", corpus_type=None):
    """
    Обрабатываем каждый файл из пары по отдельности, а затем склеиваем их
    вместе и описываем зоны.

    :param inpaths: list of paths to the .xml files
    :param subcorpus: a subcorpus name

    :return: the united doc in JSON format

    """
    docs = [
        prepare(
            inpath, subcorpus=subcorpus, split=False, corpus_type=corpus_type
        ) for inpath in inpaths
    ]
    sents = list()
    hchy = {
        "type": "multi",
        "items": list(),
        "_id": "multi:0",
        "path": [{
            "type": "top",
            "_id": "top:0",
            "items": list()
        }],
        "Attrs": docs[0]["Attrs"],
        "snippet_type": docs[0]["snippet_type"],
        "context": docs[0]["context"],
        "prefix": docs[0]["prefix"]
    }
    for doc_idx in xrange(len(docs)):
        doc = docs[doc_idx]
        prev_len = len(sents)
        sents += list(all_sents(doc))
        item = {
            "type": "para_item",
            "_id": "para_item:%s" % doc_idx,
            "index": {
                "start": {"sent": prev_len, "word": -1},
                "end": {"sent": len(sents), "word": -1}
            },
            # document attributes -> item attributes
            "Attrs": doc["Attrs"],
            "prefix": docs[0]["prefix"],

        }
        if "items" in doc:
            item["items"] = doc["items"]
            update_ranges(item["items"], prev_len)
        hchy["items"].append(item)

    united_doc = {"Parts": []}
    for doc in docs:
        united_doc["Parts"].append({
            "Sents": sents,
            "Hierarchy": hchy,
            "Attrs": doc["Attrs"],
        })

    return united_doc


def update_ranges(items, delta):
    """
    When embedding items in a higher-level item, we need to update start/end
    references to direct index.

    :param delta: Offset from the doc's start.

    """
    for item in items:
        item["index"]["start"]["sent"] += delta
        item["index"]["end"]["sent"] += delta
        if "items" in item:
            update_ranges(item["items"], delta)


def dumps(doc):
    doc = attrs.split_attrs(doc, attrs.C_INFO)
    return json.dumps(doc, indent=1, ensure_ascii=False).encode('utf-8')


if __name__ == '__main__':
    pass
