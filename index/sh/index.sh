#!/usr/bin/env bash
set -e

FILENAME=$1

curl -X POST -F "json_message=@$FILENAME.json" -F "body_xml=@$FILENAME.saas" http://saas-indexerproxy-outgone.yandex.net:80/service/2b6087d5f79ee63acbbb64c2ebea3223?timeout=20000
