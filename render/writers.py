# -*- coding: utf-8 -*-

import base64
import logging
import collections
import unicodedata

from xml.sax.saxutils import escape, quoteattr

from common.utils import remove_accents


class WriterFactory(object):
    FACTORY_MAPPING = dict()

    @classmethod
    def get_writer(cls, item):
        builder = cls.FACTORY_MAPPING.get(item["type"])
        if builder:
            return builder
        else:
            return BaseItemWriter()

    @classmethod
    def register_writer(cls, item_name, writer):
        cls.FACTORY_MAPPING[item_name] = writer


class BaseItemWriter(object):

    @classmethod
    def write(cls, out, item, **kwargs):
        cls.open_item(out, item, **kwargs)
        cls.process_content(out, item, **kwargs)
        cls.close_item(out, item, **kwargs)

    @classmethod
    def open_item(cls, out, item, **kwargs):
        pass

    @classmethod
    def process_content(cls, out, item, **kwargs):
        if "content" in item:
            SimpleTextWriter.write(out, item, **kwargs)
        if "items" in item:
            for item in item["items"]:
                writer = WriterFactory.get_writer(item)
                writer.write(out, item, **kwargs)

    @classmethod
    def close_item(cls, out, item, **kwargs):
        pass


class BodyWriter(BaseItemWriter):

    @classmethod
    def open_item(cls, out, item, **kwargs):
        pass

    @classmethod
    def close_item(cls, out, item, **kwargs):
        pass


class GenericWriter(BaseItemWriter):

    @classmethod
    def open_item(cls, out, item, **kwargs):
        total_hits = item.get("total_hits", "0")
        attrs = collections.defaultdict(list)
        for key, val in item.get("Attrs", []):
            attrs[key].append(val)
        docid = base64.b64encode(item.get("document_url", "NoURL"))
        title = cls._get_title(attrs)
        # This section is made for the `orthlib` corpus to work. It seems like
        # the sources have inconsistent attribute names. Maybe we should
        # contanct the people who maintain those sources.
        if not title:
            title = ". ".join(attrs.get("title", []))
        tagging = "manual" if "manual" in attrs.get("tagging", []) else "none"
        document_header = None
        if kwargs.get("text") == "meta":
            document_header = "<document id=%s title=%s tagging=%s>" % tuple(
                map(quoteattr, (docid, title, tagging))
            )
        else:
            document_header = "<document id=%s title=%s tagging=%s snippets=%s>" % tuple(
                map(quoteattr, (docid, title, tagging, total_hits))
            )
        out.append(document_header)
        out.append("<attributes>")
        linked_fragments = []
        for name in attrs:
            for value in attrs[name]:
                out.append("<attr name=%s value=%s/>" % (
                    quoteattr(name), quoteattr(value))
                )
            if name == "linked_fragments":
                linked_fragments += list(attrs[name])
        if linked_fragments:
            linked_fragments = "|".join(sorted(set(linked_fragments)))
            out.append("<attr name=\"gr_linked_fragments\" value=%s/>" %
                       quoteattr(linked_fragments))
        out.append("</attributes>")

    @classmethod
    def close_item(cls, out, item, **kwargs):
        out.append("</document>")

    @classmethod
    def _get_title(cls, attrs):
        title_author = " ".join(attrs.get("author", []))
        title_header = " ".join(attrs.get("header", []))
        title_created = " ".join(attrs.get("grcreated", []))
        title = ""
        if title_author:
            title += "%s." % title_author
        if title_header:
            title += " %s" % title_header
        if title_created:
            title += " (%s)" % title_created
        return title


class SnippetWriter(BaseItemWriter):

    @classmethod
    def open_item(cls, out, item, **kwargs):
        sid = item.get("_extend_at", "")
        lang = dict(item.get("Attrs", {})).get("lang", "")
        out.append(
            "<snippet sid=\" % s\" language=\" % s\" compound=\"1\">" % (
                sid, lang)
        )

    @classmethod
    def close_item(cls, out, item, **kwargs):
        out.append("</snippet>")


# Multilangual and parallel corpora

class ParaWriter(BaseItemWriter):

    @classmethod
    def open_item(cls, out, item, **kwargs):
        out.append("<para>")

    @classmethod
    def close_item(cls, out, item, **kwargs):
        out.append("</para>")


class SpeechWriter(BaseItemWriter):

    @classmethod
    def open_item(cls, out, item, **kwargs):
        sp_attrs = dict(item.get("Attrs", {})).values()
        out.append("<snippet>")
        out.append("<text>[%s] </text>" % escape(", ".join(sp_attrs)))

    @classmethod
    def close_item(cls, out, item, **kwargs):
        out.append("</snippet>")


class SimpleTextWriter(BaseItemWriter):

    @classmethod
    def open_item(cls, out, item, **kwargs):
        pass

    @classmethod
    def process_content(cls, out, item, **kwargs):
        nodia = kwargs.get("nodia", True)
        for sent in item["content"]:
            for word_idx in xrange(len(sent["Words"])):
                word = sent["Words"][word_idx]
                prev_word = sent["Words"][word_idx - 1]
                word["Text"] = cls.fix_accent(
                    word["Text"], nodia=nodia)
                if word["Punct"]:
                    # WARNING: we add a space after each punctuation char.
                    out.append("<text>%s</text>" % escape(word["Punct"]))
                if prev_word.get("Rhyme"):
                    out.append("<br />")
                text = quoteattr(word["Text"])
                src = quoteattr(base64.b64encode(word["Source"]))
                target = "target=\"1\"" if word.get("is_hit", False) else ""
                out.append("<word text=%s source=%s %s/>" %
                           (text, src, target))
            if sent["Punct"]:
                # WARNING: we add a space after each end-of-sentence
                # punctuation char.
                out.append("<text>%s </text>" % escape(sent["Punct"]))

    @classmethod
    def close_item(cls, out, item, **kwargs):
        pass

    @classmethod
    def fix_accent(cls, word, nodia=True):
        """
        For some reason accented words look like "Пересм`ешник", and I"m
        not sure that we want to change this at indexing time; so we fix
        those words while rendering.
        """
        word = cls._duct_tape_for_multiparc(word)
        try:
            word = word.decode("utf-8")
        except Exception:
            pass
        if nodia:
            word = unicodedata.normalize('NFD', word)
            word = word.replace(u'\u0300', "")
            word = word.replace(u'\u0301', "")
            # word = word.replace(u'`', "")
            return word
        else:
            dst_idx = None
            for idx in range(len(word) - 1):
                if word[idx] == "`":
                    dst_idx = idx
                    break
            if dst_idx is None:
                return word
            word = word.replace("`", "")
            return word[:dst_idx + 1] + u"\u0301" + word[dst_idx + 1:]

    @classmethod
    def _duct_tape_for_multiparc(cls, word):
        if word in ["ll", "t", "s", "re"]:
            word = "'%s" % word
        else:
            word = " %s" % word
        return word
