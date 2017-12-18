# -*- coding: utf-8 -*-

import re
import os
import sys
import string
import unicodedata
from glob import glob
from pprint import PrettyPrinter as PP


def remove_accents(data):
    return ''.join(x for x in unicodedata.normalize('NFKD', data)
                   if x in string.ascii_letters).lower()


def replace_last_in_path(pattern, replacement, path):
    parts = re.split("(/)", path)
    if parts[-1] == "/":
        parts = parts[:-1]
    parts[-1] = re.sub(pattern, "", parts[-1])
    return "".join(parts)


def print_with_return(msg, *fmt_args):
    if fmt_args:
        msg = msg % fmt_args
    sys.stdout.write('{0}\r'.format(msg))
    sys.stdout.flush()


def get_all_paths_recursive(path, filter_by=""):
    output = [y for x in os.walk(path)
              for y in glob(os.path.join(x[0], '*.*'))]
    if filter_by:
        output = [x for x in output if filter_by in x]
    return output


class MyPrettyPrinter(PP):

    def format(self, *args, **kwargs):
        representation, readable, recursive = PP.format(self, *args, **kwargs)
        if representation:
            if representation[0] in ('"', "'"):
                representation = representation.decode('string_escape')
            elif representation[0:2] in ("u'", 'u"'):
                representation = representation.decode('unicode_escape')
                representation = representation.encode(sys.stdout.encoding)
        return representation, readable, recursive


def pprint(obj, stream=None, indent=1, width=80, depth=None):
    printer = MyPrettyPrinter(stream=stream, indent=indent,
                              width=width, depth=depth)
    printer.pprint(obj)
