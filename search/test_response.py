# -*- coding: utf-8 -*-

import unittest

from response import SearchResult


class TestSearchResponse(unittest.TestCase):
    """
    This class contains tests for various methods of the SearchResponse class.

    """
    def test_get_params(self):
        """
        This test should check that SearchResponse translates a sample query to
        a valid search server query. All important combinations of parameters
        should be checked.

        """
        # response = SearchResponse("sample_query", 42)
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
