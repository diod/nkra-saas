#!/usr/bin/python

# -*- encoding: utf-8 -*-

import os
import logging
import argparse
import urlparse
import BaseHTTPServer
import StringIO

import requests

from search import search
from render import xslt

logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S',
                    level=logging.DEBUG)


def write_pid_file():
    pid = str(os.getpid())
    f = open('/var/run/saas.pid', 'w')
    f.write(pid)
    f.close()


class ServerHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    engine = search.SearchEngine()

    def do_GET(self):
        if self.path.startswith('/favicon'):
            with open('www/favicon.ico', 'rb') as infile:
                self.wfile.write(infile.read())

        else:
            args = ServerHandler.args
            output = StringIO.StringIO()
            query = urlparse.urlparse(self.path).query
            params = urlparse.parse_qs(query)

            if params.get('mode', [None])[0] == 'syntax':
                params = urlparse.parse_qs(query, keep_blank_values=True)

            if "video.xml" in self.path:
                redirect_url = "http://streaming.video.yandex.ru/get/ruscorpora-video/%s/sq.mp4" % params.get("id", ["None"])[0]
                self.send_response(301)
                self.send_header("Location", redirect_url)
                self.send_header("Content-Type", "application/octet-stream")
                self.end_headers()
                return

            self.send_response(200, 'OK')
            if args.rendering == 'xml':
                self.send_header('Content-Type', 'text/xml; charset=utf-8')
                self.end_headers()
                output.write('<?xml version=\'1.0\' encoding=\'utf-8\'?>\n')
            elif args.rendering == 'xslt':
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()

            self.engine.search(params, output, args)
            result = output.getvalue()
            if args.rendering == 'xslt':
                result = xslt.transform(result, params)
            self.wfile.write(result)


def main():
    write_pid_file()
    parser = argparse.ArgumentParser(description='Starts python web server.')
    parser.add_argument('--subcorpus', default='main')
    parser.add_argument('--kps', type=int, default=1, nargs='?')
    parser.add_argument('--rendering', default='xslt',
                        choices=['xml', 'xslt'], nargs='?')
    parser.add_argument('-p', '--port', type=int, default=8001, nargs='?')
    args = parser.parse_args()
    ServerHandler.args = args
    serv = BaseHTTPServer.HTTPServer(('', args.port), ServerHandler)
    while True:
        serv.handle_request()
    serv.server_close()


if __name__ == '__main__':
    main()
