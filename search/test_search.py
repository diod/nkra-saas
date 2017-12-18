# -*- coding: utf-8 -*-

import hashlib
import unittest

from StringIO import StringIO
from argparse import Namespace

from search import SearchEngine, SearchParams
from test_data import DATA_SEARCH_ENGINE, DATA_SEARCH_PARAMS


class TestSearchEngine(unittest.TestCase):
    """
    This class contains tests that create search params for various types of
    queries and make a SearchEngine get search server's response; then they
    check that the response is what we expect. Requires connection to search
    server.

    """
    def setUp(self):
        self.engine = SearchEngine()
        self.args = Namespace(
            kps=1, port=8888,
            rendering='xml', subcorpus='main'
        )

    def test_serve_lexform(self):
        data = DATA_SEARCH_ENGINE['test_serve_lexform']
        checksum = self._get_test_checksum(data)
        self.assertEqual(checksum, data['expected_checksum'])

    def test_serve_lexgramm(self):
        data = DATA_SEARCH_ENGINE['test_serve_lexgramm']
        checksum = self._get_test_checksum(data)
        self.assertEqual(checksum, data['expected_checksum'])

    def test_serve_word_info(self):
        data = DATA_SEARCH_ENGINE['test_serve_word_info']
        checksum = self._get_test_checksum(data)
        self.assertEqual(checksum, data['expected_checksum'])

    def _get_test_checksum(self, data):
        wfile = StringIO()
        self.engine.search(data['params'], wfile, self.args)
        return hashlib.sha256(wfile.getvalue()).hexdigest()


class TestSearchParams(unittest.TestCase):
    """
    This class contains tests that feed certain params (as received by
    ServerHandler) to SearchParams and checks whether everything's parsed
    and stored properly.

    """
    def test_lexform_query(self):
        data = DATA_SEARCH_PARAMS['test_lexform_query']
        out_params = SearchParams(data['input']).__dict__
        self.assertEqual(out_params, data['expected'])

    def test_lexgram_query(self):
        data = DATA_SEARCH_PARAMS['test_lexgram_query']
        out_params = SearchParams(data['input']).__dict__
        self.assertEqual(out_params, data['expected'])

    def test_word_info_query(self):
        # N.B.: not implemented until new index is uploaded to search server!
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
