# -*- encoding: utf-8 -*-

import itertools
import json
import logging
import urllib2


COMBINED_YEARS = tuple()

with open('./search/graphic/combined_create_years.txt', 'r') as infile:
    data = [x.strip() for x in infile.readlines()]
    dummy = []
    for line in data:
        start, x, end = line.split('-')
        dummy.append((line, int(start), int(end),))
    dummy.sort()
    COMBINED_YEARS = tuple(dummy)


class PagesWalker(object):

    _URL = 'https://saas-searchproxy-outgone.yandex.net/yandsearch?service=ruscorpora&format=json&timeout=2147483647&text=sz_form%3A%22{}%22+s_year_created%3A%22{}%22&kps=10092&relev=attr_limit%3D1000000&g=1.s_url.1.1.....s_subindex.1&qi=rty_hits_count_full&rty_hits_detail=da'

    def __init__(self, params, parted_query):
        self.params = params
        self.parted_query = parted_query

        self.start_year = int(params.raw['startyear'][0])
        self.end_year = int(params.raw['endyear'][0])

        self.parsed = {}
        self.parsed['table'] = [[str(i) + '-2-' + str(i), i, 0]
                                for i in range(self.start_year, self.end_year + 1)]

        self.parsed['graphic'] = dict(
            itertools.izip(range(self.start_year, self.end_year + 1),
                           itertools.cycle([0])))

        self.parsed['multiply_years'] = {}

    def walk(self):
        for index, year in enumerate(self.parsed['table']):

            url = PagesWalker._URL.format(self.parted_query, year[0])
            result = self._read_json_from_url(url)

            self._parse(result, index, year, True)

        for years in COMBINED_YEARS:
            if (self.start_year >= years[1] and self.start_year <= years[2]) or \
               (self.end_year >= years[1] and self.end_year <= years[2]):

                url = PagesWalker._URL.format(self.parted_query, years[0])
                result = self._read_json_from_url(url)

                self._parse(result, -1, years, False)

    def _read_json_from_url(self, url):
        try:
            # cjson fails to load Unicode fields
            return json.loads(urllib2.urlopen(url).read())
        except Exception as ex:
            logging.error("read_json_from_url(): failed with %s - '%s'", ex, url)

    def _parse(self, result, index, year, is_one_year_mode=True):
        if not 'searcher_properties' in result['response']:
            return False

        frequency = result['response']['searcher_properties']['rty_hits_count_full']
        frequency = int(frequency)

        if is_one_year_mode:
            self.parsed['table'][index][2] = frequency
            self.parsed['graphic'][year[1]] = frequency

        else:
            if frequency != 0:
                self.parsed['multiply_years'][year[0]] = (year[1], year[2], frequency)

        return True
