# -*- coding: utf-8 -*-

import marisa_trie
import sys
import BaseHTTPServer
import json
import heapq
import urlparse

SUGGEST_TRIE = marisa_trie.BytesTrie()
HOST = ''
PORT = 8989
RESULT_SIZE = 10
RUN = True

CONFIG_PARAMETERS = {}


class SuggestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def __write_json_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json; charset=UTF-8")
        self.end_headers()

    def do_HEAD(self):
        self.__write_json_headers()

    def WriteSuggest(self, in_query_dict):
        result = ''
        if 'q' in in_query_dict:
            suggest_result = self.GetSuggest(
                in_query_dict['q'][0].decode('utf-8'))
            result += json.dumps(suggest_result, ensure_ascii=False)
        if 'callback' in in_query_dict:
            result = '%s(%s)' % (in_query_dict['callback'][
                0].decode('utf-8'), result)
        self.wfile.write(result.encode('utf-8'))

    def GetSuggest(self, in_prefix):
        keys = SUGGEST_TRIE.keys(in_prefix.lower())
        results = set([])
        for key in keys:
            results.update([value.decode('utf-8')
                            for value in SUGGEST_TRIE[key]])

        sort_key = CONFIG_PARAMETERS[
            'sort_key'] if 'sort_key' in CONFIG_PARAMETERS else None
        first_n = heapq.nsmallest(RESULT_SIZE, results, key=sort_key)
        result_dict = {'q': in_prefix, 'data': first_n}
        return result_dict

    def do_GET(self):
        self.__write_json_headers()

        # reading the query
        query_string = self.path.split('?')
        if len(query_string) < 2:
            return
        prefix_to_find = None
        callback = None
        query = urlparse.parse_qs(query_string[1])
        if 'action' in query and query['action'][0] == 'shutdown':
            global RUN
            RUN = False
            print >>sys.stderr, 'Recieved shutdown request. Exiting'
            return
        self.WriteSuggest(query)


def run_service(in_host,
                in_port,
                server_class=BaseHTTPServer.HTTPServer,
                handler_class=SuggestHandler):
    server_address = (in_host, in_port)
    httpd = server_class(server_address, handler_class)
    while RUN:
        httpd.handle_request()


def parse_config(in_file_name):
    config_map = json.load(open(in_file_name))
    if 'sort_key' in config_map:
        global CONFIG_PARAMETERS
        module_name = config_map['sort_key']
        module = __import__(module_name)
        CONFIG_PARAMETERS['sort_key'] = getattr(module, 'sort_key')

if __name__ == '__main__':
    if len(sys.argv) < 4:
        exit('Usage: suggestd.py <host> <port> <trie dump> [config file]')
    SUGGEST_TRIE.load(sys.argv[3])
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    if len(sys.argv) == 5:
        parse_config(sys.argv[4])
    run_service(HOST, PORT)
