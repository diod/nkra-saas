# -*- coding: utf-8 -*-

import sys
import logging

from search.search import MODE_TO_KPS

"""This script is for Jenkins only. It lets Jenkins get a KPS number by the
name of a specific subcorpus.
"""


if __name__ == '__main__':
    if len(sys.argv) < 2:
        logging.error("Usage: <subcorpus_name>")
        exit(1)
    subcorpus = sys.argv[1]
    if subcorpus not in MODE_TO_KPS:
        logging.error('Subcorpus "%s" not found', subcorpus)
        exit(1)
    sys.stdout.write(str(MODE_TO_KPS[subcorpus]))
