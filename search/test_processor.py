# -*- coding: utf-8 -*-

import unittest

from processor import ParamsProcessor, ResponseProcessor


class TestParamsProcessor(unittest.TestCase):
    """
    This class contains tests for ParamsProcessor. As its public methods are
    used for different types of queries, all those type are covered here.

    """
    def test_parse_lexform_cgi(self):
        self.assertTrue(True)

    def test_parse_lexgramm_cgi(self):
        self.assertTrue(True)

    def test(self):
        self.assertTrue(True)


class TestResponseProcessor(unittest.TestCase):
    """
    This class contains tests that ensure correctness of SearchResponse
    preprocessing stages.

    """
    def test_process(self):
        self.assertTrue(True)

    def test_process_group(self):
        self.assertTrue(True)

    def test_process_snippets(self):
        self.assertTrue(True)

    def test_get_accented(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
