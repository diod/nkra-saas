# -*- coding: utf-8 -*-

import json
import cjson
import urllib
import logging
import urllib2
from base64 import b64decode
from zlib import decompress as dcmprss

import defaults


class SearchResult(object):
    """
    This class represents a SaaS query result.

    """

    def __init__(self,
                 query,
                 kps,
                 grouping=True,
                 group_attr='s_url',
                 max_docs=10,
                 docs_per_group=5,
                 hits_count=False,
                 hits_info=False,
                 sort=None,
                 asc=True,
                 docid=None,
                 add_props=None,
                 subcorpus="",
                 sentence_num=None):
        """
        :param query:
        :param kps:
        :param grouping:
        :param group_attr:
        :param max_docs:
        :param docs_per_group:
        :param hits_count:
        :param hits_info:
        :param sort:
        :param asc:
        :param docid:
        :param add_props:
        :param subcorpus:

        """
        if not (subcorpus is None):
            query += subcorpus
        query = self._process_query(query, docid)
        params = self._get_params(query, kps, grouping, group_attr, max_docs,
                                  docs_per_group, hits_count, hits_info, sort,
                                  asc, add_props, subcorpus, sentence_num)
        url = self._get_url(params)
        logging.info(url)
        self.mapping = self._get_mapping(url)

    def is_empty(self):
        return 'results' not in self.mapping.get('response', [])

    def get_docs_count(self):
        try:
            return int(self.mapping['response']['results'][0]
                                   ['found']['all'])
        except Exception:
            return 0

    def get_hits_count(self):
        try:
            return int(self.mapping['response']['searcher_properties']
                                   ['rty_hits_count_full'])
        except Exception:
            return 0

    def get_groups(self):
        try:
            for group in self.mapping['response']['results'][0]['groups']:
                yield Group(group)
        except Exception:
            return

    def get_first_group(self):
        try:
            return Group(self.mapping['response']['results'][0]['groups'][0])
        except Exception:
            return None

    def _process_query(self, query, docid=None):
        if docid:
            return defaults.EXTENDED_QUERY % (query, docid)
        else:
            return query

    def _get_url(self, params):
        return defaults.SAAS_HOST + urllib.urlencode(params)

    def _get_params(self,
                    query,
                    kps,
                    grouping=True,
                    group_attr='s_url',
                    max_docs=10,
                    docs_per_group=5,
                    hits_count=False,
                    hits_info=False,
                    sort=None,
                    asc=True,
                    add_props=None,
                    subcorpus=None,
                    sentence_num=None):
        """
        Form a list of parameters for the request to SaaS host.

        """
        params = defaults.BASE_PARAMS(query, kps)
        if add_props:
            params += defaults.PROPS_PARAMS[add_props](sentence_num)
        if hits_count:
            params += defaults.HITS_COUNT_PARAMS
        if hits_info:
            params += defaults.HITS_INFO_PARAMS
        if sort:
            params += defaults.SORT_PARAMS(sort, asc)
        if grouping:
            params += defaults.GRP_PARAMS(group_attr, max_docs, docs_per_group)
        else:
            params += defaults.DEFAULT_GRP_PARAMS(max_docs)
        return params

    def _get_mapping(self, url):
        try:
            return self._read_json_from_url(url)
        except Exception as ex:
            logging.error("read_json_from_url(): failed, %s", ex)
            return dict()

    def _read_json_from_url(self, url):
        try:
            # cjson fails to load Unicode fields
            return json.loads(urllib2.urlopen(url).read())
        except Exception as ex:
            logging.error("read_json_from_url(): failed with %s", ex)


class Group(object):
    """
    This class represents a group of found documents. Its functionality boils
    down to providing a convenient interface for querying any "group" part of
    the JSON structure returned by the search server.

    """

    def __init__(self, obj):
        """
        :param obj: a dictionary representing one of the objects in a typical
                    server_response['results'][0]['groups'] list.
        """
        self.obj = obj

    def get_documents(self):
        try:
            for doc in self.obj['documents']:
                yield Document(doc)
        except Exception:
            return

    def get_first_document(self):
        try:
            return Document(self.obj['documents'][0])
        except Exception:
            logging.error("Group.get_first_document(): failed")
            return None

    def get_hits_count(self):
        count = 0
        for doc in self.get_documents():
            for hit in doc.get_hits().values():
                count += len(hit)
        return count

    def get_attributes(self):
        """
        This method returns the attributes of the first document in the
        group.

        """
        for doc in self.get_documents():
            return doc.get_attributes()
        return {}

    def get_property(self, propName):
        for doc in self.get_documents():
            return doc.get_property(propName)
        return ''


class Document(object):
    """
    This class represents a found document; its functionality is similar to
    that of the Group class.

    """

    def __init__(self, obj):
        self.obj = obj
        self.directIndex = None
        self.info = None
        self.hits = None
        self.attrs = None

    def get_properties(self):
        try:
            return self.obj['properties']
        except Exception:
            return {}

    def get_property(self, propName):
        return self.get_properties().get(propName, '')

    def get_direct_index(self):
        if not self.directIndex:
            try:
                blob = self.obj['properties']['p_serp_part']
                self.directIndex = self._read_json(dcmprss(b64decode(blob)))
            except Exception:
                self.directIndex = {}
        return self.directIndex

    def get_info(self, sentence_id):
        if not self.info:
            try:
                blob = self.obj['properties']['p_info_part_%s' % sentence_id]
                self.info = self._read_json(dcmprss(b64decode(blob)))
            except Exception:
                self.info = {}
        return self.info

    def get_hits(self):
        if not self.hits:
            try:
                blob = self.obj['properties']['__HitsInfo'][0]
                hits_info = self._read_json(blob)
                self.hits = {}
                for item in hits_info:
                    s = int(item['sent']) - 1
                    w = int(item['word']) - 1
                    if s not in self.hits:
                        self.hits[s] = set()
                    self.hits[s].add(w)
            except Exception:
                self.hits = {}
        return self.hits

    def get_attributes(self):
        if not self.attrs:
            try:
                self.attrs = {}
                for key, value in self.get_properties().items():
                    key = key.replace("p_", "")
                    key = key.replace("s_", "")
                    if type(value) is list:
                        value = value[0]
                    self.attrs[key] = self.attrs.get(key, []) + [value]
                self.attrs['url'] = [self.get_url()]
            except Exception:
                self.attrs = {}
        return self.attrs

    def get_url(self):
        return self.obj.get('url', '')

    def _read_json(self, blob):
        return cjson.decode(blob)
