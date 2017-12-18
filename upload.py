# -*- coding: utf-8 -*-

import sys
import requests
import multiprocessing

from index.index_multipart import SAAS_INDEX_URL
from common.utils import get_all_paths_recursive, print_with_return

CHUNK_SIZE = 128
ERROR_LOG = "./upload_errors.log"
PROGRESS_LOG = "./upload_progress.log"


def upload_directory(inpath, history=False):
    """Uploads corpus files found in `inpath` to the search server.

    Info about any errors is stored in `ERROR_LOG`.
    Info about the successfully uploaded files is stored in `PROGRESS_LOG`.

    Args:
        inpath: Path to the directory containing corpus files.
        history: If `True`, `PROGRESS_LOG` file is used to avoid
        re-uploading files.
    """
    chunks, num_chunks = _get_files_in_chunks(inpath, history=history)
    pool = multiprocessing.Pool(processes=16)
    for num, chunk in enumerate(chunks):
        print_with_return("Sending chunk %s out of %s", num, num_chunks)
        resps = pool.map(upload_part, chunk)
        _process_resps(resps)


def upload_part(inpath):
    """Uploads .json and .saas files for a given part to the search server.

    Args:
        inpath: Path to the part file without any extension. It will be used to
            collect both .json and .saas files.
    Returns:
        An empty dict if there was no error while uploading OR a dict with
        two keys: `error` and `inpath`.
    """
    try:
        with open("%s.json" % inpath, "rb") as f_json:
            with open("%s.saas" % inpath, "rb") as f_saas:
                return _upload_part(inpath, f_json, f_saas)
    except Exception as ex:
        return {"error": ex, "inpath": inpath}


def _get_files_in_chunks(inpath, history=False):
    """Gets .saas files in `inpath` and splits them into CHUNK_SIZE'd parts.

    Args:
        inpath: Path to the directory containing corpus files.
        history: If `True`, `PROGRESS_LOG` file is used to avoid
        re-uploading files.

    Returns:
        A list of tuples with file paths.
    """
    files = get_all_paths_recursive(inpath, filter_by="saas")
    files = [x.replace(".saas", "") for x in files]
    if history:
        with open(PROGRESS_LOG) as f:
            progress = f.read().splitlines()
            files = [x for x in files if x not in progress]
    # Note that if the data is not aligned properly, the trailing chunk will
    # be omitted. This has to be fixed in future.
    if len(files) > CHUNK_SIZE:
        out = zip(*[iter(files)] * CHUNK_SIZE)
    else:
        out = [files]
    return out, len(out)


def _process_resps(resps):
    with open(PROGRESS_LOG, "a") as w_prog:
        with open(ERROR_LOG, "a") as w_err:
            for resp in resps:
                try:
                    if resp["error"]:
                        # An error occured.
                        w_err.write("%s:\t%s\n" %
                                    (resp["inpath"], resp["error"]))
                    else:
                        # No error, save progress.
                        w_prog.write("%s\n" % resp["inpath"])
                except Exception as ex:
                    print ex


def _upload_part(inpath, f_json, f_saas):
    """Does the networking part of uploading a given part to the search server.

    Args:
        inpath: Path to the part file without any extension. It will be used to
            collect both .json and .saas files.
        f_json: An open file object (not read!) for the .json service file.
        f_saas: An open file object (not read!) for the .saas XML file.
    Returns:
        An empty dict if there was no error while uploading OR a dict with
        two keys: `error` and `inpath`.
    """
    try:
        payload = [('json_message', f_json), ('body_xml', f_saas)]
        resp = requests.post(SAAS_INDEX_URL, files=payload, timeout=250)
        if resp.status_code == 200:
            return {"error": None, "inpath": inpath}
        else:
            return {"error": resp.text, "inpath": inpath}
    except Exception as ex:
        return {"error": ex, "inpath": inpath}


if __name__ == '__main__':
    upload_directory(sys.argv[1])
