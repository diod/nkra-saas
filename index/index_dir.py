# -*- coding: utf-8 -*-

import os
import gc
import sys
import time
import json
import zlib
import pickle
import base64
import logging
import StringIO
import traceback
import multiprocessing
from operator import itemgetter as get
from xml.sax.saxutils import quoteattr
from itertools import product, combinations

import cjson

import upload
import prepare
import attrs as attrs_utils
from processing import doc_iters
from common import xml2json
from common.utils import replace_last_in_path

SAAS_INDEX_URL = 'http://saas-indexerproxy-outgone.yandex.net:80/service/' \
                 '2b6087d5f79ee63acbbb64c2ebea3223?timeout=2000000'

SORTING_ATTRS = [
    "gr_author",
    "gr_tagging",
    "gr_created",
    "gr_created_inv",
    "gr_birthday",
    "gr_birthday_inv",
]

ATTRS_WITH_COMBINATORIAL_EXPLOSION = (
    'gr',
    'sem'
)

CROPPED_URLS = [
    "old_rus",
]

NODISK_CHUNK_MAX_DOCS = 128
NODISK_CHUNK_MAX_PARTS = 256


def load_initial(inpaths,
                 kps=0,
                 paired='',
                 subcorpus="",
                 corpus_type=None,
                 nodisk=False,
                 only_meta=False):
    sortings_file = './%s.sortings' % corpus_type
    if os.path.isfile(sortings_file):
        logging.info("Found serialized sortings at %s, loading",
                     sortings_file)
        with open('./%s.sortings' % corpus_type) as f:
            sortings = pickle.load(f)
        logging.info("Loaded sortings")
    else:
        sortings = {x: set() for x in SORTING_ATTRS}
        logging.info("Loading attrs...")
        for inpath in inpaths:
            logging.info("Preloading %s", inpath)
            if paired:
                for inpath_elem in inpath:
                    _preload_attrs(sortings,
                                   inpath_elem,
                                   corpus_type=corpus_type,
                                   only_meta=only_meta)
            else:
                _preload_attrs(sortings,
                               inpath,
                               corpus_type=corpus_type,
                               only_meta=only_meta)
        _normalize_sortings(sortings)
        with open('./%s.sortings' % corpus_type, 'w') as w:
            pickle.dump(sortings, w)
    return sortings


def index(sortings,
          inpaths,
          kps=0,
          paired='',
          subcorpus="",
          corpus_type=None,
          nodisk=False):
    if nodisk:
        logging.info("WARNING: nodisk is True, watch your memory")
        chunk = []
        num_processed = 0
        pool = multiprocessing.Pool(processes=8)
        try:
            with open("./%s.upload" % corpus_type) as f:
                last_uploaded = f.read().strip()
        except IOError:
            last_uploaded = inpaths[0]
        continue_from = inpaths.index(last_uploaded)
        inpaths = inpaths[continue_from:]
        logging.info("Total %s files, continuing from %s",
                     len(inpaths), continue_from)
        time.sleep(1)
    failed_inpaths = set()
    for inpath in inpaths:
        if paired:
            if "rus-zho" in inpath[0]:
                continue
        else:
            if "rus-zho" in inpath:
                continue
        if nodisk:
            doc_parts_gen = _process_doc_nodisk(
                sortings, inpath, kps, paired, subcorpus, corpus_type)
            for doc_part in doc_parts_gen:
                if not doc_part:
                    with open("./%s.upload.err" % corpus_type, "a") as w:
                        if paired:
                            w.write(inpath[0] + "\n")
                        else:
                            w.write(inpath)
                    continue
                chunk.append(doc_part)
                docs_exceeded = num_processed >= NODISK_CHUNK_MAX_DOCS
                parts_exceeded = len(chunk) >= NODISK_CHUNK_MAX_PARTS
                if docs_exceeded or parts_exceeded:
                    reports = pool.map(upload.upload_part, chunk)
                    if any(r.get("error") for r in reports):
                        if inpath not in failed_inpaths:
                            with open("./%s.upload.err" % corpus_type, "a") as w:
                                w.write(inpath + "\n")
                            failed_inpaths.add(inpath)
                    chunk, num_processed = [], 0
                    logging.info("(nodisk) Uploaded chunk")
                    gc.collect()
            num_processed += 1
            with open("./%s.upload" % corpus_type, "w") as w:
                if paired:
                    w.write(inpath[0])
                else:
                    w.write(inpath)
        else:
            _process_doc(
                sortings, inpath, kps, paired, subcorpus, corpus_type)
    if nodisk and chunk:
        pool.map(upload.upload_part, chunk)
        logging.info("(nodisk) Uploaded final chunk")


def _preload_attrs(sortings,
                   inpath,
                   corpus_type="",
                   only_meta=False):
    try:
        doc = xml2json.process(
            inpath, corpus_type=corpus_type, only_meta=only_meta)
        doc_attrs = _get_doc_sorting_attrs(doc)
        for attr_name, attr_val in doc_attrs.items():
            sortings[attr_name].add(attr_val)
    except Exception as ex:
        logging.error('Failed to index %s: %s', inpath, ex)
        traceback.print_exc(ex)


def _murco_split_attrs(attr_name, attr_val):
    subattrs = [x.strip().split("=") for x in attr_val.split(" ")]
    subattrs = [(attr_name + u"_" + x[0], x[1].replace(u"\"", u"")) for x in subattrs]
    subattrs = [x for x in subattrs if x[1]]

    return subattrs


def _normalize_sortings(sortings):
    for sorting_name, seen_values in sortings.items():
        sortings[sorting_name] = list(seen_values)
    sortings["gr_tagging"].sort(key=get(0, 2, 3))
    sortings["gr_tagging"].sort(reverse=True, key=get(1))
    sortings["gr_tagging"] = {v: k for k, v in dict(
        enumerate(sortings["gr_tagging"])).items()}
    sortings["gr_author"].sort(key=get(0, 1, 2))
    sortings["gr_author"] = {v: k for k, v in dict(
        enumerate(sortings["gr_author"])).items()}
    sortings["gr_created"].sort(key=get(0, 1, 2))
    sortings["gr_created"] = {v: k for k, v in dict(
        enumerate(sortings["gr_created"])).items()}
    sortings["gr_created_inv"].sort(key=get(1, 2))
    sortings["gr_created_inv"].sort(reverse=True, key=get(0))
    sortings["gr_created_inv"] = {v: k for k, v in dict(
        enumerate(sortings["gr_created_inv"])).items()}
    sortings["gr_birthday"].sort(key=get(0, 1, 2, 3))
    sortings["gr_birthday"] = {v: k for k, v in dict(
        enumerate(sortings["gr_birthday"])).items()}
    sortings["gr_birthday_inv"].sort(key=get(1, 2, 3))
    sortings["gr_birthday_inv"].sort(reverse=True, key=get(0))
    sortings["gr_birthday_inv"] = {v: k for k, v in dict(
        enumerate(sortings["gr_birthday_inv"])).items()}


def _process_doc(sortings,
                 inpath,
                 kps,
                 paired,
                 subcorpus,
                 corpus_type):
    if paired:
        sample_inpath = inpath[0]
    else:
        sample_inpath = inpath
    try:
        prepare_cb = prepare.prepare_multifile if paired else prepare.prepare
        doc = prepare_cb(inpath, subcorpus=subcorpus, corpus_type=corpus_type)
        if corpus_type in [u"murco"]:
            new_attrs = []
            for attr_name, attr_val in doc["Attrs"]:
                if attr_name in [u"act", u"gesture"]:
                    split_attrs = _murco_split_attrs(attr_name, attr_val)
                    new_attrs.extend(split_attrs)
                else:
                    new_attrs.append((attr_name, attr_val))
            doc["Attrs"] = new_attrs
        for i, doc_part in enumerate(doc['Parts']):
            try:
                body_xml = _produce_xml(attrs_utils.split_attrs(
                    doc_part, attrs_utils.C_INDEX))
                json_message = _produce_json(doc, sortings, inpath, i, kps, corpus_type=corpus_type)
                logging.info('Processing %s, %s', inpath, i)
                with open(inpath + ".%04d.json" % i, "w") as f:
                    f.write(json_message)
                with open(inpath + ".%04d.saas" % i, "w") as f:
                    f.write(body_xml)
            except Exception as ex:
                logging.error('Failed to index %s: %s', sample_inpath, ex)
                traceback.print_exc(ex)
        logging.info('DONE: %s, %s', inpath, len(doc['Parts']))
        sys.stdout.flush()
    except Exception as ex:
        logging.error('Failed to index %s: %s', inpath, ex)
        traceback.print_exc(ex)


def _process_doc_nodisk(sortings,
                        inpath,
                        kps,
                        paired,
                        subcorpus,
                        corpus_type):
    if paired:
        sample_inpath = inpath[0]
    else:
        sample_inpath = inpath
    try:
        prepare_cb = prepare.prepare_multifile if paired else prepare.prepare
        doc = prepare_cb(inpath, subcorpus=subcorpus, corpus_type=corpus_type)
        if corpus_type in [u"murco"]:
            new_attrs = []
            for attr_name, attr_val in doc["Attrs"]:
                if attr_name in [u"act", u"gesture"]:
                    split_attrs = _murco_split_attrs(attr_name, attr_val)
                    new_attrs.extend(split_attrs)
                else:
                    new_attrs.append((attr_name, attr_val))
            doc["Attrs"] = new_attrs

        for i, doc_part in enumerate(doc['Parts']):
            try:
                body_xml = _produce_xml(attrs_utils.split_attrs(
                    doc_part, attrs_utils.C_INDEX))
                json_message = _produce_json(
                    doc, sortings, sample_inpath, i, kps, corpus_type=corpus_type)
                logging.info('Processing %s, %s', inpath, i)
                yield (inpath, StringIO.StringIO(
                    json_message), StringIO.StringIO(body_xml),)
            except Exception as ex:
                logging.error('Failed to index %s: %s', sample_inpath, ex)
                traceback.print_exc(ex)
                yield None
        logging.info('DONE: %s, %s', inpath, len(doc['Parts']))
    except Exception as ex:
        logging.error('Failed to index %s: %s', inpath, ex)
        traceback.print_exc(ex)
        yield None


def _get_doc_sortings(control_attrs, doc):
    dst_attrs = _get_doc_sorting_attrs(doc)
    for name, val in dst_attrs.items():
        dst_attrs[name] = control_attrs[name][val]
    return dst_attrs


def _get_doc_sorting_attrs(doc):
    dst_attrs, doc_attrs = {}, dict(doc["Attrs"])
    dst_attrs["gr_tagging"] = (
        doc_attrs.get("tagging"), doc_attrs.get("created"),
        doc_attrs.get("author"), doc_attrs.get("header")
    )
    dst_attrs["gr_author"] = (
        doc_attrs.get("author"), doc_attrs.get("created"),
        dst_attrs.get("header")
    )
    dst_attrs["gr_created"] = (
        doc_attrs.get("created"), doc_attrs.get("author"),
        doc_attrs.get("header")
    )
    dst_attrs["gr_created_inv"] = (
        doc_attrs.get("created"), doc_attrs.get("author"),
        doc_attrs.get("header")
    )
    dst_attrs["gr_birthday"] = (
        doc_attrs.get("birthday"), doc_attrs.get("author"),
        doc_attrs.get("created"), doc_attrs.get("header")
    )
    dst_attrs["gr_birthday_inv"] = (
        doc_attrs.get("birthday"), doc_attrs.get("author"),
        doc_attrs.get("created"), doc_attrs.get("header")
    )
    return dst_attrs


def _get_resulting_filename(inpaths, pair_pattern):
    if pair_pattern:
        return replace_last_in_path(pair_pattern, "", inpaths[0])
    else:
        return inpaths


def _produce_xml(doc_part):
    out = StringIO.StringIO()
    out.write('<doc_part>\n')
    for sent in doc_part['Sents']:
        out.write('<sent>\n')
        _append_attrs(sent, out)
        for word in sent['Words']:
            out.write('<w sz_%s=%s>' % ('form', quoteattr(word['Text'])))
            for attr in ATTRS_WITH_COMBINATORIAL_EXPLOSION:
                for item in _combinatorial_explosion(word['Anas'], attr):
                    out.write(' <e sz_%s=\'%s\'/>\n' % (attr, item))
            for ana in word['Anas']:
                for key, val in ana.items():
                    if key not in ATTRS_WITH_COMBINATORIAL_EXPLOSION:
                        out.write(' <e sz_%s=%s/>\n' % (key, quoteattr(val)))
                _append_attrs(ana, out)
            _append_attrs(word, out)
            out.write('a</w>\n')
        out.write('</sent>\n')
    out.write('</doc_part>')
    return out.getvalue().encode('utf-8')


def _maybe_crop_url(url, corpus_type):
    if corpus_type in CROPPED_URLS:
        return url.split("/")[-1]
    return url


def _produce_json(doc, sortings, url, i, kps, corpus_type=None):
    url = _maybe_crop_url(url, corpus_type)
    part = doc['Parts'][i]
    # Multipart docs don't have attributes, but their parts do.
    attrs_holder = doc if doc.get("Attrs") else part
    # This is direct index.
    p_serp_part = _pack(attrs_utils.split_attrs(part, attrs_utils.C_SERP))
    obj = {
        'prefix': kps,
        'action': 'modify',
        'docs': [{
            'options': {
                'mime_type': 'text/xml',
                'charset': 'utf8',
                'language': 'ru',
                'realtime': 'false'
            },
            'url': {'value': url + '#%04d' % i},
            # For some corpora (paper) this value is intended to be used as a
            # list of dicts. Everything crashes if it's just a dict. Don't know
            # why it happens only sometimes.
            's_url': [{'value': url, 'type': '#hl'}],
            'p_url': [{'value': url, 'type': '#p'}],
            's_subindex': {'value': i, 'type': '#g'},
            'p_serp_part': {'value': p_serp_part, 'type': '#p'},
            'body': {'value': 'body_xml'},
        }],
    }
    doc_sortings = _get_doc_sortings(sortings, attrs_holder)
    for sorting_name, value in doc_sortings.items():
        obj["docs"][0][sorting_name] = {"value": value, "type": "#g"}
    # Here we save direct index for each sentence. so, for each sentence in
    # this part.
    for sent_id in xrange(len(part['Sents'])):
        sent = part['Sents'][sent_id]
        # do the packing magic
        info_value = _pack(attrs_utils.split_attrs(sent, attrs_utils.C_INFO))
        # and add a field with this sentence's id
        obj['docs'][0]['p_info_part_%s' % sent_id] = {
            'value': info_value, 'type': '#p'
        }
    parent = obj["docs"][0]
    for name, value in attrs_holder.get("Attrs", []):
        s_key = "s_" + name.encode("utf-8")
        p_key = "p_" + name.encode("utf-8")

        if len(value) > 120:
            value = value[:120]
        value = value.encode("utf-8")

        # I don't what kind of bullshit this `"date" in p_key` is, but it breaks subcorpus search
        # for `para` corpus. I'm a little bit afraid to simply remove this check (maybe it was necessary
        # for some other corpus), so I'll just make this work for `para`.
        if corpus_type not in ["para"] and "date" in p_key:
            continue
        parent[p_key] = parent.get(p_key, []) + [{
            "value": value, "type": "#pl"
        }]
        parent[s_key] = parent.get(s_key, []) + [{
            "value": value, "type": "#l"
        }]
    return json.dumps(obj, ensure_ascii=False)


def _append_attrs(node, out):
    for key in node:
        for val in doc_iters.attr_values(node[key]):
            out.write('<e sz_%s=%s/>' % (key, quoteattr(val)))


def _combinatorial_explosion(anas, attr):
    subsets = set()
    for ana in anas:
        for key, val in ana.items():
            if key == attr:
                vals = val.replace(',', ' ').replace('=', ' ').split(' ')
                for i in xrange(1, len(vals) + 1):
                    for comb in combinations(vals, i):
                        subsets.add(','.join(sorted(comb)))
    return subsets


def _pack(obj):
    return base64.b64encode(zlib.compress(cjson.encode(obj)))
