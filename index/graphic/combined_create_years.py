# -*- Encoding: utf-8 -*-
# This script prints the average amount of documents for each year
# This distribution is needed for ngram viewer plots
# Usage: python years.py PATH >years.xml 2>log
# File years.xml should be copied to graymantle:ruscorpora/xml/
import sys
import getopt
import os
import os.path
import time
import xml.sax

N = 1
PUNCT = False
MONTHS = False

total_years = set([])


class TextHandler(xml.sax.ContentHandler):
  def __init__(self):
    self.years = set([])

  def startElement(self, tag, attrs):
    if tag == "meta" and attrs["name"] == "created":
        created = attrs["content"]
        start_year = int(attrs["content"][:4])
        if len(created) > 4 and created[4] == "-":
          finish_year = int(created[5:])
        else:
          finish_year = start_year

        for i in range(start_year, finish_year + 1):
          self.years.add(i)

def convert_directory(indir, indent = ""):
  curdirname = os.path.basename(indir)

  print >>sys.stderr, "%sEntering %s" % (indent, curdirname)
  starttime = time.time()
  nextindent  = indent + "    "

  filelist = os.listdir(indir)
  subdirs = [f for f in filelist if os.path.isdir(os.path.join(indir, f))]
  files = [f for f in filelist if not os.path.isdir(os.path.join(indir, f))]

  for subdir in subdirs:
    if subdir == ".svn": continue
    inpath = os.path.join(indir, subdir)
    convert_directory(inpath, nextindent)

  for f in files:
    inpath = os.path.join(indir, f)
    convert(inpath, nextindent)

  print >>sys.stderr, "%sTime: %.2f s" % (indent, time.time() - starttime)


def convert(inpath, indent=""):
  print >>sys.stderr, "%s%s" % (indent, os.path.basename(inpath)),
  global filename
  filename = inpath

  try:
    parser = TextHandler()
    xml.sax.parse(inpath, parser)
    dummy = list(parser.years)
    dummy.sort()
    start_year = dummy[0]
    finish_year = dummy[-1]
    if not (start_year == finish_year):
      global total_years
      years = str(start_year) + '-1-' + str(finish_year)
      total_years.add(years)
    print >>sys.stderr, " - OK"
  except Exception as e:
    print >>sys.stderr, " - FAILED: ", e


def usage():
  print "Usage: python ngramms.py PATH [N [PUNCT]]"


def main():
  global N
  global PUNCT
  global MONTHS
  if len(sys.argv) <= 1:
    usage()
    return
  inpath = sys.argv[1]
  if "--months" in sys.argv:
    MONTHS = True
  else:
    if len(sys.argv) > 2:
      N = int(sys.argv[2])
    if len(sys.argv) > 3:
      PUNCT = bool(sys.argv[3])

  convert_directory(inpath)

  global total_years
  ordered_years = list(total_years)
  ordered_years.sort()
  for year in ordered_years:
    #print year, total_years[year]
    print '%s' % (str(year))

if __name__ == "__main__":
  main()
