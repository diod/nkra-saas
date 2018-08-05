
import itertools
import json
import logging
import urllib2


class PagesWalker(object):

    def __init__(self, params, response, parted_query):
        self.params = params
        self.parted_query = parted_query
        self.url = response.url + '&p='
        self.page = 0

        self.start_year = int(params.raw['startyear'][0])
        self.end_year = int(params.raw['endyear'][0])
        self.parsed = {}
        self.parsed['table'] = dict(
            itertools.izip([str(i) + '-2-' + str(i) for i in range(self.start_year, self.end_year + 1)],
                           itertools.cycle([0])))
        self.parsed['graphic'] = dict(
            itertools.izip(range(self.start_year, self.end_year + 1),
                           itertools.cycle([0])))
        self.parsed['multiply_years'] = {}

        self._parse(response.mapping)

    def walk(self):
        while True:
            self.page += 1
            url = self.url + str(self.page)
            logging.info('graphic walk for %s' % (url,))
            result = self._read_json_from_url(url)
            if not self._parse(result):
                break

    def _read_json_from_url(self, url):
        try:
            # cjson fails to load Unicode fields
            return json.loads(urllib2.urlopen(url).read())
        except Exception as ex:
            logging.error("read_json_from_url(): failed with %s", ex)

    def _parse(self, result):
        if 'results' in result['response']:
            if not 'groups' in result['response']['results'][0]:
                return False

            for doc_parts in result['response']['results'][0]['groups']:
                s_year_created = doc_parts['documents'][0]['properties']['s_year_created']
                start_year, years_mode, _ = s_year_created.split('-')

                i_start_year = int(start_year)
                if i_start_year < self.start_year or i_start_year > self.end_year:
                    continue

                cnt = int(doc_parts['found']['all'])

                if years_mode == '2':
                    self.parsed['table'][s_year_created] += cnt
                    self.parsed['graphic'][i_start_year] += cnt

                else:
                    self.parsed['multiply_years'][s_year_created] = \
                        cnt + self.parsed['multiply_years'].get(s_year_created, 0)
            return True

        return False
