import base64
import sys
import time
import logging
from string import Template
from xml.sax.saxutils import escape, quoteattr

from processing import doc_iters


def render_snippets(results, wfile, stat, query_type="lexgramm", search_type="all-documents"):
    out = []
    out.append('<body>')
    out.append('<result documents="%d" contexts="%d" search-type="%s">' %
               (stat["Docs"], stat["Hits"], search_type))
    out.append('<corp-stat>')
    out.append('<documents total="%s"/>' % stat.get("TotalDocs", 0))
    out.append('</corp-stat>')
    for doc in results:
        attrs = doc["Attrs"]
        docid = base64.b64encode(doc["Url"])
        title = ". ".join(attrs.get("header", []))
        tagging = "manual" if "manual" in attrs.get("tagging", []) else "none"
        out.append('<document id=%s title=%s tagging=%s>' %
                   tuple(map(quoteattr, (docid, title, tagging))))
        out.append('<attributes>')
        for name in attrs:

            # # The following code is some duct tape which we had to use
            # # after some changes in the indexing process. I actually don't
            # # know what went wrong with attr values, but they may be lists
            # # or strings, and we have to handle that.
            # if isinstance(attrs[name], list):
            #     values = attrs[name]
            # else:
            #     values = [attrs[name]]
            for value in attrs[name]:
                out.append('<attr name=%s value=%s/>' %
                           (quoteattr(name), quoteattr(value)))
        out.append('</attributes>')
        out.append('</document>')
    out.append('</result>')
    out.append('</body>\n')
    wfile.write("\n".join(out).encode("utf-8"))


def render_doc_info(results, wfile, stat):
    return render_snippets(results, wfile, stat, query_type="document_info", search_type="document_info")


def render_word_info(word, wfile):
    start = time.time()
    text = word["Text"]
    anas = word["Anas"]
    out = []
    out.append('<body>')
    out.append('<result search-type="word-info">')
    out.append('<word text=%s>' % quoteattr(text))
    for ana in anas:
        out.append('<ana>')
        for key, values in doc_iters.ordered_attrs(ana, subcorpus="main"):
            key2 = "gramm" if key == "gr" else key
            out.append('<el name=%s>' % quoteattr(key2))
            out.append('<el-group><el-atom>%s</el-atom></el-group>' %
                       escape(", ".join(values)))
            out.append('</el>')
        out.append('</ana>')
    for key, values in doc_iters.attrs(word):
        out.append('<ana>')
        out.append('<el name=%s>' % quoteattr(key))
        out.append('<el-group><el-atom>%s</el-atom></el-group>' %
                   escape(", ".join(values)))
        out.append('</el>')
        out.append('</ana>')
    out.append('</word>')
    out.append('</result>')
    out.append('</body>')
    wfile.write("".join(out).encode("utf-8"))
    end = time.time()
    print "render_word_info:", end - start


# console text output
def render_text(results):
    out = []
    for doc in results:
        for name, value in doc["Attrs"].items():
            out.append("%s: %s\n" % (name, value))
        for snippet in doc["Snippets"]:
            for item in snippet:
                if item[0] == "Punct":
                    out.append(item[1])
                elif item[0] == "Word":
                    text, coords, has_hit = item[1:]
                    if has_hit:
                        out.append("**%s**" % text)
                    else:
                        out.append(text)
            out.append("\n------------\n")
        out.append("=============\n")
    sys.stdout.write("".join(out).encode("utf-8"))
