# -*- coding: utf-8 -*-

import json
import logging
import operator
from collections import defaultdict, OrderedDict

from params import ParamsProcessor, SearchParams
from processor import ResponseProcessor
from render import render_legacy, writers
from render.document import OutputDocumentWeb
from search_result import SearchResult
from syntax.syntax_search import syntax_search_process

from graphic.walker import PagesWalker

writers.WriterFactory.register_writer('body', writers.BodyWriter)

# MULTIPARC
writers.WriterFactory.register_writer('para_item', writers.GenericWriter)
writers.WriterFactory.register_writer('speach', writers.SpeechWriter)

# MULTILANG
writers.WriterFactory.register_writer('multilang:top', writers.GenericWriter)
writers.WriterFactory.register_writer('para', writers.ParaWriter)
writers.WriterFactory.register_writer('multilang:se', writers.SnippetWriter)

# OLD_RUS
writers.WriterFactory.register_writer('old_rus:top', writers.GenericWriter)
writers.WriterFactory.register_writer('old_rus:snippet', writers.SnippetWriter)
writers.WriterFactory.register_writer('old_rus:se', writers.SimpleTextWriter)

# MID_RUS
writers.WriterFactory.register_writer('mid_rus:top', writers.GenericWriter)
writers.WriterFactory.register_writer('mid_rus:snippet', writers.SnippetWriter)
writers.WriterFactory.register_writer('mid_rus:se', writers.SimpleTextWriter)

# BIRCHBARK
writers.WriterFactory.register_writer('birchbark:top', writers.GenericWriter)
writers.WriterFactory.register_writer('birchbark:snippet', writers.SnippetWriter)
writers.WriterFactory.register_writer('birchbark:se', writers.SimpleTextWriter)

# ORTHLIB
writers.WriterFactory.register_writer('orthlib:top', writers.GenericWriter)
writers.WriterFactory.register_writer('orthlib:snippet', writers.SnippetWriter)
writers.WriterFactory.register_writer('orthlib:se', writers.SimpleTextWriter)

# PAPER
writers.WriterFactory.register_writer('paper:top', writers.GenericWriter)
writers.WriterFactory.register_writer('paper:snippet', writers.SnippetWriter)
writers.WriterFactory.register_writer('paper:se', writers.SimpleTextWriter)

# STANDARD
writers.WriterFactory.register_writer('standard:top', writers.GenericWriter)
writers.WriterFactory.register_writer('standard:snippet', writers.SnippetWriter)
writers.WriterFactory.register_writer('standard:se', writers.SimpleTextWriter)

# MAIN
writers.WriterFactory.register_writer('main:top', writers.GenericWriter)
writers.WriterFactory.register_writer('main:snippet', writers.SnippetWriter)
writers.WriterFactory.register_writer('main:se', writers.SimpleTextWriter)

# PARA
writers.WriterFactory.register_writer('para:top', writers.GenericWriter)
writers.WriterFactory.register_writer('para:para', writers.ParaWriter)
writers.WriterFactory.register_writer('para:se', writers.SnippetWriter)

# DIALECT
writers.WriterFactory.register_writer('dialect:top', writers.GenericWriter)
writers.WriterFactory.register_writer('dialect:snippet', writers.SnippetWriter)
writers.WriterFactory.register_writer('dialect:se', writers.SimpleTextWriter)

# POETIC
writers.WriterFactory.register_writer('poetic:top', writers.GenericWriter)
writers.WriterFactory.register_writer('poetic:snippet', writers.SnippetWriter)
writers.WriterFactory.register_writer('poetic:se', writers.SimpleTextWriter)

# ACCENT
writers.WriterFactory.register_writer('accent:top', writers.GenericWriter)
writers.WriterFactory.register_writer('speach', writers.SpeechWriter)
writers.WriterFactory.register_writer('snippet', writers.SnippetWriter)
writers.WriterFactory.register_writer('accent_stihi:top', writers.GenericWriter)
writers.WriterFactory.register_writer('accent_stihi:snippet', writers.SnippetWriter)
writers.WriterFactory.register_writer('accent_stihi:se', writers.SimpleTextWriter)
writers.WriterFactory.register_writer('accent_poetic:top', writers.GenericWriter)
writers.WriterFactory.register_writer('accent_poetic:snippet', writers.SnippetWriter)
writers.WriterFactory.register_writer('accent_poetic:se', writers.SimpleTextWriter)

# SPOKEN
writers.WriterFactory.register_writer('spoken_spoken:top', writers.GenericWriter)
writers.WriterFactory.register_writer('spoken_accent:top', writers.GenericWriter)
writers.WriterFactory.register_writer('speach', writers.SpeechWriter)

# MURCO
writers.WriterFactory.register_writer('murco:top', writers.GenericWriter)
writers.WriterFactory.register_writer('speach', writers.SpeechWriter)

# REGIONAL_RUS
writers.WriterFactory.register_writer('regional_rus:top', writers.GenericWriter)
writers.WriterFactory.register_writer('regional_rus:snippet', writers.SnippetWriter)
writers.WriterFactory.register_writer('regional_rus:se', writers.SimpleTextWriter)

# MISC
writers.WriterFactory.register_writer('context:top', writers.GenericWriter)
writers.WriterFactory.register_writer('context:entry', writers.SnippetWriter)
writers.WriterFactory.register_writer('subcorpus:top', writers.GenericWriter)

# GRAPHIC
writers.WriterFactory.register_writer('graphic', writers.GraphicWriter)


MODE_TO_KPS = {
    "test": 10010,
    "old_rus": 10000,
    "mid_rus": 10010,
    "birchbark": 10020,
    "orthlib": 10030,
    "multiparc": 10040,
    "multiparc_rus": 10050,
    "multi": 10060,
    "paper": 10070,
    "main": 10092,
    "para": 10100,
    "dialect": 10111,
    "poetic": 10120,
    "accent": 10134,
    "spoken": 10145,
    "murco": 10152,
    "regional_rus": 10160,
    "syntax": 10910,
    'graphic_main': 10092,
}

MAX_DOCS_CONTEXT = 100


class SearchEngine(object):
    """Implements search logic for all requests received by the server.

    The only shared thing in this class is the `response mapping`, which maps
    types of queries to response callbacks.
    """
    max_snippets = 100
    stats = {
        MODE_TO_KPS["old_rus"]: (16, 0, 500292),
        MODE_TO_KPS["mid_rus"]: (5876, 0, 8074107),
        MODE_TO_KPS["birchbark"]: (879, 0, 19002),
        MODE_TO_KPS["orthlib"]: (1160 , 0, 4476006),
        MODE_TO_KPS["multiparc"]: (3652, 0, 421226),
        MODE_TO_KPS["multiparc_rus"]: (1315, 0, 960738),
        MODE_TO_KPS["multi"]: (12, 0, 5022425),
        MODE_TO_KPS["paper"]: (0, 0, 0),
        MODE_TO_KPS["main"]: (0, 0, 0),
        MODE_TO_KPS["para"]: (2013, 0, 71033352),
        MODE_TO_KPS["dialect"]: (627, 0, 285281),
        MODE_TO_KPS["poetic"]: (78852, 0, 10923513),
        MODE_TO_KPS["spoken"]: (3821, 0, 11318245),
        MODE_TO_KPS["accent"]: (238318, 0, 25254284),
        MODE_TO_KPS["murco"]: (187230, 0, 4497729),
        MODE_TO_KPS["regional_rus"]: (0, 0, 0),
    }

    def __init__(self):
        # this is a mapping from possible values of the 'text' parameter to
        # their respective response callbacks (i.e., 'text' tells us what kind
        # of search we are going to run)
        self.response_mapping = defaultdict(lambda: self._serve_lex)
        self.response_mapping['word-info'] = self._serve_word_info
        self.response_mapping['document-info'] = self._serve_doc_info

    def search(self, raw_query, wfile, args):
        """Main search method, guaranties that something gets written to
        @wfile.

        Args:
            raw_query: Output of urlparse.parse_qs() applied to current request.
            wfile: ServerHandler's @wfile (writable response for client).
            args: ServerHandler's parsed arguments (as received from stdin).
        """
        if raw_query.get('mode', [None])[0] == 'syntax':
            syntax_search_process(raw_query, wfile)
        else:
            params = SearchParams(raw_query)
            response_callback = self.response_mapping[params.text]
            response_callback(params, wfile, args)

    def _serve_lex(self, params, wfile, args):
        """Used for queries by some grammatical marker or by some wordform.

        Args:
            params: An instance of SearchParams.
            wfile: ServerHandler's @wfile (writable response for client).
            args: ServerHandler's parsed arguments (as received from stdin).
        """
        saas_query, query_len = self._get_saas_query_details(params)
        kps = MODE_TO_KPS.get(params.mode, 150)
        if params.doc_id:
            params.snippets_per_doc = self.max_snippets
        if params.sort_by in ["cont1", "cont2"]:
            max_docs = MAX_DOCS_CONTEXT
        else:
            max_docs = (params.page + 1) * params.docs_per_page

        if params.mode.startswith('graphic'):
            results = {}
            params.queries_in_order = [None] * len(saas_query)
            for i, parted_saas_query in enumerate(saas_query):
                response = SearchResult(
                    query=parted_saas_query,
                    kps=kps,
                    max_docs=max_docs,
                    docs_per_group=params.snippets_per_doc,
                    group_attr=params.group_by,
                    sort=params.sort_by,
                    hits_info=False,
                    hits_count=False,
                    docid=params.doc_id,
                    subcorpus=params.subcorpus,
                    mode=params.mode
                )
                pos = parted_saas_query.find(':"')
                parted_query = parted_saas_query[pos + 2:][:-1]
                params.queries_in_order[i] = parted_query

                walker = PagesWalker(params, response, parted_query)
                walker.walk()
                results[parted_query] = walker.parsed

            query_len = query_len[0]
            hchy = {"type": "graphic",
                    "items": [{"type": "graphic", 'results': results, 'params': params}]}

        else:
            response = SearchResult(
                query=saas_query,
                kps=kps,
                max_docs=max_docs,
                docs_per_group=params.snippets_per_doc,
                group_attr=params.group_by,
                sort=params.sort_by,
                hits_info=True,
                hits_count=True,
                docid=params.doc_id,
                subcorpus=params.subcorpus,
                mode=params.mode
            )
            results = ResponseProcessor(snippets=params.snippets_per_doc).process(
                params, response, extend_id=params.sent_id, sort_by=params.sort_by, subcorpus=params.mode)

            hchy = {"type": "body", "items": results}

        query_info = QueryInfo.get_query_info(params)
        stat = self._get_stat(kps, response, query_len)
        out = OutputDocumentWeb(
            wfile, page=params.page, stat=stat,
            info=query_info, search_type=params.search_type, subcorpus=params.subcorpus)
        writers.BodyWriter.write(
            out, hchy, nodia=params.diacritic, text=params.text)
        out.finalize()

    def _serve_doc_info(self, params, wfile, args):
        """Gets information about some document.

        Args:
            params: An instance of SearchParams.
            wfile: ServerHandler's @wfile (writable response for client).
            args: ServerHandler's parsed arguments (as received from stdin).
        """
        kps = MODE_TO_KPS.get(params.mode, 150)
        response = SearchResult(
            query='s_url:"%s"' % params.doc_id,
            kps=kps,
            grouping=False,
            max_docs=1,
        )
        if response.is_empty():
            return
        attrs = response.get_first_group().get_attributes()
        results = [{
            'Attrs': attrs,
            'Snippets': list(),
            'Url': params.doc_id
        }]
        stat = {'Docs': 1, 'Hits': 0}
        render_legacy.render_doc_info(results, wfile, stat)

    def _serve_word_info(self, params, wfile, args):
        """Gets information about some word.

        Args:
            params: An instance of SearchParams.
            wfile: `ServerHandler`'s `wfile` (writable response for client).
            args: `ServerHandler`'s parsed arguments (as received from stdin).
        """
        url, sent, word = params.source.rsplit('\t', 2)
        sent = int(sent)
        word = int(word)
        kps = MODE_TO_KPS.get(params.mode, 150)
        response = SearchResult(
            query="url:'%s'" % url,
            kps=kps,
            grouping=False,
            max_docs=1,
            add_props='info',
            sentence_num=sent
        )
        if response.is_empty():
            logging.error("SearchEngine._serve_word_info(): no response, failed")
            return
        group = response.get_first_group()
        if not group:
            logging.error("SearchEngine._serve_word_info(): no group, failed")
            return
        document = group.get_first_document()
        if not document:
            logging.error("SearchEngine._serve_word_info(): no document, failed")
            return
        directIndex = document.get_info(sent)
        result = directIndex['Words'][word]
        render_legacy.render_word_info(result, wfile)

    def _get_saas_query_details(self, params):
        """Modifies params.text for a certain type of "lex" search.

        Args:
            params: An instance of SearchParams.

        Returns:
            Query string (possibly modified) and integer query length.
        """
        if params.text in ["lexgramm"]:
            return ParamsProcessor.parse_lexgramm_cgi(params)
        if params.text in ["lexform", "meta"]:
            return ParamsProcessor.parse_lexform_cgi(params)
        return params.text, 1

    def _get_stat(self, kps, response, query_len):
        """
        Used for getting statistics about the current search result.

        """
        if query_len < 1:
            query_len = 1
        total_docs, total_sents, total_words = self._total_stat(kps)
        return {'Docs': response.get_docs_count(),
                'Hits': response.get_hits_count() / query_len,
                'TotalDocs': total_docs,
                'TotalSents': total_sents,
                'TotalWords': total_words}

    def _total_stat(self, kps):
        """Gets total statistics about a certain corpus.

        WARNING: the statistics may be incorrect (for unknown reason).

        Args:
            kps: An integer which defines the "address" of a corpus at the
            search server.
        Returns:
            total_docs: Total number of documents in a corpus.
            total_sents: Total number of sentences in a corpus.
            total_words: Total number of words in a corpus.
        """
        if True:
            return self.stats.get(kps, (0, 0, 0))
        response = SearchResult(
            query="sz_form:'*'",
            kps=kps,
            hits_count=True,
            max_docs=1,
            docs_per_group=0,
        )
        total_docs = response.get_docs_count()
        total_sents = 0
        total_words = response.get_hits_count()
        self.stats[kps] = (total_docs, total_sents, total_words)
        return total_docs, total_sents, total_words


class QueryInfo(object):
    """QueryInfo extracts query info data from SearchParams.

    This operation is required for translating Web-GUI queries into queries to
    the search server.
    """

    @classmethod
    def get_query_info(cls, params):
        """Builds a list of dicts with info about the words in the query.

        Args:
            params: a SearchParams object

        Returns:
            A list of dicts where each dict contains certain info about a
            single query entity (left/right context, etc.) OR None.
        """
        if params.text == "lexgramm":
            return cls._get_query_info_lexgramm(params)
        if params.text == "lexform":
            return cls._get_query_info_form(params)
        return None

    @classmethod
    def _get_query_info_form(cls, params):
        out = OrderedDict()
        req = cls._try_decode(params.req)
        count = 1
        if req:
            tokens = [x.strip() for x in req.split() if x.strip()]
            for token in tokens:
                out[count] = {
                    "lex": token, "gramm": u"", "sem1": u"", "form": u"",
                }
                if count > 1:
                    out[count]["min"] = u"1"
                count += 1
        return out.values()

    @classmethod
    def _get_query_info_lexgramm(cls, params):
        out = OrderedDict()
        all_lex = cls._get_all_by_key(params, "lex")
        all_gramm = cls._get_all_by_key(params, "gramm")
        all_form = cls._get_all_by_key(params, "form")
        all_sem1 = cls._get_all_by_key(params, "sem1")
        all_min = cls._get_all_by_key(params, "min")
        all_max = cls._get_all_by_key(params, "max")
        cls._aggregate_items(out, all_lex, "lex")
        cls._aggregate_items(out, all_gramm, "gramm")
        cls._aggregate_items(out, all_form, "form")
        cls._aggregate_items(out, all_sem1, "sem")
        cls._aggregate_items(out, all_min, "min")
        cls._aggregate_items(out, all_max, "max")
        out.items().sort(key=operator.itemgetter(0))
        return out.values()

    @classmethod
    def _aggregate_items(cls, out, items, item_type):
        try:
            query_keys = ["lex", "gramm", "sem1", "form"]
            for item in items:
                type_key, val = item
                level = type_key.split(item_type).pop()
                level = int(level)
                if level not in out:
                    out[level] = {
                        "lex": u"", "gramm": u"", "sem1": u"", "form": u"",
                    }
                # If there's nothing after current word, do nothing
                if item_type in ["max", "min"]:
                    if not any(out[level].get(t) for t in query_keys):
                        continue
                    level += 1
                out[level][item_type] = val
        except Exception:
            pass

    @classmethod
    def _get_all_by_key(cls, params, start_key):
        out = list()
        for k, v in params.raw.items():
            if k.startswith(start_key):
                out.append((k, cls._try_decode(v[0])))
        out.sort(key=operator.itemgetter(0))
        return out

    @classmethod
    def _try_decode(cls, item):
        try:
            return item.decode("utf-8")
        except UnicodeDecodeError:
            return item.decode("utf-8")


def all_urls(kps):
    response = SearchResult(
        query='url:"*"',
        kps=kps,
        grouping=False,
        max_docs=2 ** 10,
    )
    result = []
    for group in response.get_groups():
        for doc in group.get_documents():
            result.append(doc.get_url())
    return result


def all_docs(kps):
    response = SearchResult(
        query='url:"*"',
        kps=kps,
        max_docs=2 ** 10,
    )
    result = []
    for group in response.get_groups():
        for doc in group.Docs():
            result.append(doc.Url())
            break
    return result


if __name__ == '__main__':
    pass
