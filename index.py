# -*- coding: utf-8 -*-

import argparse
import logging
import os.path
import re
import sys

import requests

from common.utils import get_all_paths_recursive
from index import index_dir
from index.index_dir import SAAS_INDEX_URL

logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S',
                    level=logging.INFO)

parser = argparse.ArgumentParser()

excl_group = parser.add_mutually_exclusive_group()
excl_group.add_argument('-idx', '--index', action='store_true')

index_group = parser.add_argument_group()
index_group.add_argument('--paired', type=str, default="")
index_group.add_argument('--dir', type=str)
index_group.add_argument('--kps', type=int, default=42)
index_group.add_argument('--single', action='store_true')
index_group.add_argument('--jobs', type=int, default=1)
index_group.add_argument('--only_listed', type=str, default="")

prepare_group = parser.add_argument_group()
prepare_group.add_argument('--inpath', default='/dev/stdin', nargs='?')
prepare_group.add_argument('--outpath', default="", nargs='?')
prepare_group.add_argument('--subcorpus', default='main')
prepare_group.add_argument('--corpus_type', type=str, default='')
prepare_group.add_argument('--nodisk', action='store_true')
prepare_group.add_argument('--meta', action='store_true')

delete_group = parser.add_argument_group()
delete_group.add_argument('--url', type=str, default='ALL')

FILE_LIST = list()
VALID_FILE_EXTENSIONS = ('.xml', '.xhtml')


def main():
    args = parser.parse_args()
    if os.path.isdir(args.dir):
        prepare_file_list(args.dir, in_handler=_append_path)
        if args.only_listed:
            targets = args.only_listed.split(",")
            filtered = []
            for filename in FILE_LIST:
                for target in targets:
                    if target in filename:
                        filtered.append(filename)
            del FILE_LIST[:]
            for filename in filtered:
                FILE_LIST.append(filename)
        if args.paired:
            tuple_files(args.paired)
        sortings = index_dir.load_initial(
            FILE_LIST, paired=args.paired, kps=args.kps,
            subcorpus=args.subcorpus,
            corpus_type=args.corpus_type,
            only_meta=args.meta)
        if not args.meta:
            index_dir.index(
                sortings, FILE_LIST, paired=args.paired, kps=args.kps,
                subcorpus=args.subcorpus,
                corpus_type=args.corpus_type, nodisk=args.nodisk)
    else:
        raise Exception("No such file or directory: %s" % args.dir)


def prepare_file_list(indir, in_handler):
    filelist = os.listdir(indir)
    subdirs = [f for f in filelist if os.path.isdir(os.path.join(indir, f))]
    files = [f for f in filelist if not os.path.isdir(os.path.join(indir, f))]
    for subdir in subdirs:
        inpath = os.path.join(indir, subdir)
        prepare_file_list(inpath, in_handler)
    for f in files:
        if os.path.splitext(f)[1] not in VALID_FILE_EXTENSIONS:
            continue
        inpath = os.path.join(indir, f)
        in_handler(inpath)


def tuple_files(pair_pattern):
    pairs = dict()
    for file_name in FILE_LIST:
        modified = re.sub(pair_pattern, "", file_name)
        if modified not in pairs:
            pairs[modified] = list()
        pairs[modified].append(file_name)
        pairs[modified].sort()
    del FILE_LIST[:]
    for pair in pairs.values():
        FILE_LIST.append(tuple(pair))


def _append_path(path):
    FILE_LIST.append(path)


def upload_directory(inpath):
    files = get_all_paths_recursive(inpath, filter_by="saas")
    files = [x.replace("saas", "") for x in files]
    for f in files:
        with open("%s.json" % f) as f_json:
            with open("%s.saas" % f) as f_saas:
                payload = [('json_message', f_json), ('body_xml', f_saas)]
                r = requests.post(SAAS_INDEX_URL, files=payload)
                print r.__dict__


if __name__ == '__main__':
    # find ./multiparc_deep/ -mindepth 2 -type f -exec cp -t ./multipark_flat -i '{}' +
    # clear && python index_dir.py --index --paired="eng|rus" --dir ../res/mp/ --kps 280 --corpus_type multiparc
    # clear && python server.py -p 8888 --rendering xml --kps 134
    # sh index_folder.sh ../../../res/mp/
    # scp ./* zavgorodny@ruscorpora.ru:/var/www/saas/
    # clear && python index_dir.py --index --paired=".*(?=[0-9]{4}.xml)" --dir
    # /place/ruscorpora/texts/finalized/multiparc_rus/ --kps 1488
    # --corpus_type multiparc_rus --meta
    main()
