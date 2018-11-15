#!/usr/bin/python

# -*- encoding: utf-8 -*-

import os
import logging
import argparse
import urlparse
import StringIO

import requests

from flask import Flask, current_app, redirect, request, Response
from flask_classful import FlaskView, route
from cgi import parse_header, parse_multipart

from search import search
from render import xslt
from integration.bug_report import ruscopora_bug_reporter


logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S',
                    level=logging.DEBUG)



class ServerHandler(FlaskView):
    engine = search.SearchEngine()

    @route('/favicon.ico', methods=['GET'])
    def static_favicon(self):
        return application.send_static_file('favicon.ico');

    @route('/www/js/graphic.js', methods=['GET'])
    def static_graphic(self):
        return application.send_static_file('js/graphic/graphic.js');

    @route('/video.xml', methods=['GET'])
    def get_video(self):
        redirect_url = "http://streaming.video.yandex.ru/get/ruscorpora-video/%s/sq.mp4" % request.args.get("id", "none")
        return redirect(redirect_url, 301);

    @route('/<path:path>', methods=['GET'])
    def search(self,path):
            args = ServerHandler.args
            output = StringIO.StringIO()

            #raw query string (non utf-8)
            query = request.query_string
            params = urlparse.parse_qs(query)

            if params.get('mode', None) == 'syntax':
                params = urlparse.parse_qs(query, keep_blank_values=True)

            if args.rendering == 'xml':
                content_type = 'text/xml; charset=utf-8'
                output.write('<?xml version=\'1.0\' encoding=\'utf-8\'?>\n')
            elif args.rendering == 'xslt':
                content_type = 'text/html; charset=utf-8'

            self.engine.search(params, output, args)
            result = output.getvalue()

            if args.rendering == 'xslt':
                result = xslt.transform(result, params)

            result = xslt.tostring(result, encoding='utf-8')
            return Response(result, content_type=content_type);

    @route('/bug-report.xml', methods=['POST'])
    def bugreport(self):

        params = request.form
        msg = params.get('msg', '<Message not found>');
        url = params.get('url', '<Url not found>');

        ruscopora_bug_reporter.process_bug_report(msg, url);
        return Response("Ok\n", content_type="text/plain; charset=UTF-8")


############################################
#
# Init application for WSGI
#

parser = argparse.ArgumentParser(description='Starts python web server.')
parser.add_argument('--subcorpus', default='main')
parser.add_argument('--kps', type=int, default=1, nargs='?')
parser.add_argument('--rendering', default='xslt',
                        choices=['xml', 'xslt'], nargs='?')
parser.add_argument('-p', '--port', type=int, default=8001, nargs='?')
args = parser.parse_args()

application = Flask(__name__, static_folder='www', static_url_path='/www')

ServerHandler.args = args
ServerHandler.register(application, route_base="/")

if __name__ == '__main__':
    application.run(host="0.0.0.0", port=args.port)
