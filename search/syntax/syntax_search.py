#!/usr/local/bin/python
# -*- Encoding: windows-1251 -*-

import codecs
import urllib

import MySQLdb
import MySQLdb.cursors

import sql


_from_utf8 = codecs.getdecoder("utf8")


def syntax_search_process(query, output):
    converted_query = _query_param_to_ustr(_from_utf8, query)

    db = MySQLdb.connect(user="syntax_search", db="search_syntax", passwd="ahH8sei7thoo5Oo", use_unicode=True, charset="utf8")
    request = sql.Search(converted_query, db, output)
    request.execute()

def _query_param_to_ustr(from_codec, query, is_replace=False):
    converted_query = {}
    for (key, val) in query.items():
        l = []
        for el in val:
            l.append(from_codec(urllib.unquote(el))[0])
        converted_query[key] = l

    if is_replace:
        for (key, val) in query.items():
            l = []
            for el in val:
                l.append(from_codec(urllib.unquote(el))[0].encode('utf8'))
            query[key] = l

    return converted_query
