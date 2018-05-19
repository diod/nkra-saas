# -*- coding: utf-8 -*-

import logging
import urllib

from xml.sax.saxutils import quoteattr


class OutputDocumentSimple(object):

    def __init__(self):
        self.w = ""

    def append(self, text):
        self.w += text

    def text(self):
        return self.w


class OutputDocumentWeb(object):
    def __init__(self,
                 out,
                 page=0,
                 stat=None,
                 info=None,
                 search_type=None,
                 subcorpus=""):
        self.w = out
        if not stat:
            raise Exception("No stats for document, rejected")
        if not info:
            info = [{"lex": u"", "gramm": u"",  "sem": u""}]
        for word in info:
            for k, v in word.items():
                word[k] = v.encode("utf-8")
        out.write('<body>')
        out.write('<request page="%d">' % page)
        out.write(
            '<format documents-per-page="10" snippets-per-document="10" snippets-per-page="50"/>')
        out.write('<query request="123" document=%s type="%s">' %
                  (quoteattr(urllib.quote(subcorpus)), "lexform"))
        for word in info:
            out.write('<word ')
            if 'min' in word:
                out.write('distance-min="%s" ' % word["min"])
            if 'max' in word:
                out.write('distance-max="%s" ' % word["max"])
            out.write(
                'lex=%s gramm=%s sem=%s form=%s flags="" />' % tuple(
                    map(quoteattr, (word["lex"], word[
                        "gramm"], word.get("form", ""), word.get("sem", "")))
                )
            )
        out.write('</query>')
        out.write('</request>')
        out.write('<result documents="%d" contexts="%d" search-type="%s">' % (
            stat["Docs"], stat["Hits"], search_type))
        out.write('<corp-stat>')
        out.write('<documents total="%s"/>' % stat["TotalDocs"])
        out.write('<words total="%s"/>' % stat["TotalWords"])
        out.write('</corp-stat>')
        out.write('<subcorp-stat>')
        out.write('<documents total="%s"/>' % stat["Docs"])
        out.write('<sentences total="%s"/>' % 0)
        out.write('<words total="%s"/>' % stat["Hits"])
        out.write('</subcorp-stat>')

    def append(self, text):
        self.w.write(text.encode('utf-8'))

    def text(self):
        raise NotImplementedError

    def finalize(self):
        self.w.write('</result>')
        self.w.write('</body>\n')
