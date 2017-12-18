# -*- coding: utf-8 -*-

import os
import csv
import shutil
import logging
import argparse

from common.utils import get_all_paths_recursive

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

parser = argparse.ArgumentParser()
parser.add_argument("corpus_dir", type=str,
                    help="Path to directory with corpus files")
parser.add_argument("csv_file", type=str,
                    help="Path to .csv file with files to filter")
parser.add_argument("output_dir", type=str,
                    help="Path to the output directory")
parser.add_argument("--delimiter", type=str, default=";",
                    help="Delimiter used in .csv file")
parser.add_argument("--extension", type=str, default=".xml",
                    help="Extension of corpus files")


def filter_corpus(corpus_dir,
                  csv_file,
                  output_dir,
                  delimiter=";",
                  extension=".xml"):
    """Copies files listed in `csv_file` from `corpus_dir` to `output_dir`.

    File names to be copied are expected to be under "path" key. All files in
    `output_dir` are destroyed before copying. All files in `output_dir` are
    expected to have the same extension, `extension`. Directory structure of
    `corpus_dir` is not preserved.

    Args:
        corpus_dir: Path to directory with corpus files.
        csv_file: Path to .csv file with files to filter.
        delimiter: Delimiter used in .csv file.
        extension: Extension of corpus files in `corpus_dir`.
    """
    logging.info("Cleaning output directory %s", output_dir)
    shutil.rmtree(output_dir)
    os.mkdir(output_dir)
    logging.info("Reading files from %s", corpus_dir)
    # All file names that really exist in `corpus_dir`.
    found_corpus_files = get_all_paths_recursive(corpus_dir)
    # File names in `csv_file` may have incorrect register. From now on we
    # lowercase all file names for uniformity, but we need the real file names
    # to be stored somewhere.
    lowercase_2_real = {fn.lower(): fn for fn in found_corpus_files}
    logging.info("Read %s files", len(lowercase_2_real))
    logging.info("Reading CSV file list from %s", csv_file)
    # Some of the files listed in `csv_file` may not exist.  Existent files go
    # to `required_files`, non-existent files go to `not_found`.
    files_to_copy, not_found = [], []
    with open(csv_file, "rb") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for csv_line in reader:
            # File names in `csv_file` should be relative to `corpus_dir`.
            relative_path = csv_line.get("path", "").lower()
            if not relative_path:
                continue
            absolute_path = "%s%s%s" % (corpus_dir, relative_path, extension)
            if absolute_path not in lowercase_2_real:
                not_found.append(absolute_path)
            else:
                # N.B.: adding the real path, not the lowercased one.
                files_to_copy.append(lowercase_2_real[absolute_path])
    num_found, num_not_found = len(files_to_copy), len(not_found)
    logging.info("%s files found, %s not found", num_found, num_not_found)
    for file_path in files_to_copy:
        shutil.copy2(file_path, output_dir)
    logging.info("Done.")
    if not_found:
        logging.info("Writing missing corpus files to error.log")
        with open("error.log", "w") as w:
            for file_path in not_found:
                w.write("%s\n" % file_path)


if __name__ == "__main__":
    args = parser.parse_args()
    filter_corpus(args.corpus_dir, args.csv_file, args.output_dir,
                  args.delimiter, args.extension)
