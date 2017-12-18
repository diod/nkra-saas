# -*- coding: utf-8 -*-

import re
import sys
import json
import zlib
import cjson
import base64
import logging
import requests
import StringIO
import itertools
from xml.sax.saxutils import quoteattr

# from index import prepare, attrs
from index import prepare, attrs
from processing import doc_iters
from common.utils import replace_last_in_path


SAAS_INDEX_URL = 'http://saas-indexerproxy-outgone.yandex.net:80/service/' \
                 '2b6087d5f79ee63acbbb64c2ebea3223?timeout=2000000'

ATTRS_WITH_COMBINATORIAL_EXPLOSION = (
    'gr',
)


def process(inpath, paired='', kps="42", subcorpus="", corpus_type=None):
    """Performs all stages of processing a single (or a paired) document.

    Translates the document from XML to JSON, prepares it (e.g., splits into
    parts, normalizes punctuation, etc.) and wites the results to disk. 
    Args:
        inpath: Path to the .xml file with a corpus document.
        subcorpus: (str) An identifier of a corpus type (triggers special
            processing routines, e.g. generating simplified orthography).
            WARNING: this parameter, coupled with `corpus_type`, might be
            redundant; we should consider getting rid of it.
        corpus_type: (str) Used as a key to look up "environmental"
            variables in `xml2json.KNOWN_CORPUS_TYPES`.
    """
    if paired:
        doc = prepare.prepare_multifile(
            inpath, subcorpus=subcorpus, corpus_type=corpus_type
        )
    else:
        doc = prepare.prepare(
            inpath, subcorpus=subcorpus, corpus_type=corpus_type
        )
    inpath = get_resulting_filename(inpath, paired)
    for i, doc_part in enumerate(doc['Parts']):
        body_xml = produceXML(attrs.split_attrs(doc_part, attrs.C_INDEX))
        json_message = produceJSON(doc, inpath, i, kps)
        logging.info('Processing %s, %s', inpath, i)
        with open(inpath + '.%04d.json' % i, 'w') as f:
            f.write(json_message)
        with open(inpath + '.%04d.saas' % i, 'w') as f:
            f.write(body_xml)
    logging.info('DONE: %s, %s', inpath, len(doc['Parts']))
    sys.stdout.flush()


def get_resulting_filename(inpaths, pair_pattern):
    if pair_pattern:
        return replace_last_in_path(pair_pattern, "", inpaths[0])
    else:
        return inpaths


def produceXML(doc_part):
    out = StringIO.StringIO()
    out.write('<doc_part>\n')
    for sent in doc_part['Sents']:
        out.write('<sent>\n')
        append_attrs(sent, out)
        for word in sent['Words']:
            out.write('<w sz_%s=%s>' % ('form', quoteattr(word['Text'])))
            for attr in ATTRS_WITH_COMBINATORIAL_EXPLOSION:
                for item in combinatorial_explosion(word['Anas'], attr):
                    out.write(' <e sz_%s=\'%s\'/>\n' % (attr, item))
            for ana in word['Anas']:
                for key, val in ana.items():
                    if key not in ATTRS_WITH_COMBINATORIAL_EXPLOSION:
                        out.write(' <e sz_%s=%s/>\n' % (key, quoteattr(val)))
                append_attrs(ana, out)
            append_attrs(word, out)
            out.write('a</w>\n')
        out.write('</sent>\n')
    out.write('</doc_part>')
    return out.getvalue().encode('utf-8')


def produceJSON(doc, url, i, kps="42"):
    part = doc['Parts'][i]
    p_serp_part = pack(attrs.split_attrs(part, attrs.C_SERP))  # direct index
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
            'p_url': {'value': url, 'type': '#p'},
            's_subindex': {'value': i, 'type': '#g'},
            'p_serp_part': {'value': p_serp_part, 'type': '#p'},
            'body': {'value': 'body_xml'},
        }],
    }
    # here we save direct index for each sentence. so, for each sentence in
    # this part
    for sent_id in xrange(len(part['Sents'])):
        sent = part['Sents'][sent_id]
        # do the packing magic
        info_value = pack(attrs.split_attrs(sent, attrs.C_INFO))
        # and add a field with this sentence's id
        obj['docs'][0]['p_info_part_%s' % sent_id] = {
            'value': info_value, 'type': '#p'
        }
    parent = obj["docs"][0]
    p_keys = []
    for name, value in doc.get("Attrs", []):
        key = "s_" + name.encode("utf-8")
        parent[key] = parent.get(key, []) + [{
            "value": value.encode("utf-8"), "type": "#p"
        }]
        p_keys.append(key)
    logging.debug(
        "The following fields were indexed as properties:\n%s", p_keys)
    return json.dumps(obj, ensure_ascii=False)


def append_attrs(node, out):
    for key in node:
        for val in doc_iters.attr_values(node[key]):
            out.write('<e sz_%s=%s/>' % (key, quoteattr(val)))


def combinatorial_explosion(anas, attr):
    subsets = set()
    for ana in anas:
        for key, val in ana.items():
            if key == attr:
                vals = val.replace(',', ' ').replace('=', ' ').split(' ')
                for i in xrange(1, len(vals) + 1):
                    for comb in itertools.combinations(vals, i):
                        subsets.add(','.join(sorted(comb)))
    return subsets


def pack(obj):
    return base64.b64encode(zlib.compress(cjson.encode(obj)))


def index_requests(inpath, json_message, body_xml, retries=3):
    if retries == 0:
        logging.info('%s, FAILED', inpath)
        return
    files = [('json_message', json_message), ('body_xml', body_xml)]
    try:
        r = requests.post(SAAS_INDEX_URL, files=files, timeout=(20, 60))
        response = r.text.strip()
        if response:
            logging.info('%s, retrying...', response)
            index_requests(inpath, json_message, body_xml, retries - 1)
    except Exception as ex:
        logging.info('%s, retrying...', ex)
        index_requests(inpath, json_message, body_xml, retries - 1)


if __name__ == '__main__':
    pass
