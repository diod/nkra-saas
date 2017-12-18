# -*- coding: utf-8 -*-

import sys
import json
import requests

from search import search

SAAS_HOST = "http://saas-indexerproxy-outgone.yandex.net:80/service/2b6087d5" \
            "f79ee63acbbb64c2ebea3223?timeout=20000"


def delete_kps(kps, common_url):
    if common_url == "ALL":
        for url in search.all_urls(kps):
            print("Deleting url: %s" % url)
            json_message = produceJSON(kps, url)
            index_requests(json_message)
    else:
        print("Deleting all urls starting with: %s" % common_url)
        json_message = produceJSON(kps, common_url)
        index_requests(json_message)


def produceJSON(kps, url):
    obj = {
        "prefix": int(kps),
        "action": "delete",
        "docs": [{
            "options": {
                "mime_type": "text/xml",
                "charset": "utf8",
                "language": "ru"
            },
            "url": {"value": url},
        }],
    }
    return json.dumps(obj, ensure_ascii=False)


def index_requests(json_message):
    files = [("json_message", json_message)]
    requests.post(SAAS_HOST, files=files, timeout=5.)


if __name__ == "__main__":
    del_kps = sys.argv[1]
    del_common_url = sys.argv[2]
    delete_kps(del_kps, del_common_url)
