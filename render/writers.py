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
        sid = item.get("_extend_at", "")
        if sid:
            kwargs["_extend_at"] = sid
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
            for item_idx in range(len(item["items"])):
                sub_item = item["items"][item_idx]
                if item_idx == len(item["items"]) - 1:
                    kwargs["is_last"] = "1"
                else:
                    kwargs["is_last"] = "0"
                writer = WriterFactory.get_writer(sub_item)
                writer.write(out, sub_item, **kwargs)

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
    title_written = False

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
        # contact the people who maintain those sources.
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
            # Gestures are present only in murco and will be ignored in any other corpus
            # (gestures are processed in `self.close_item()`, see below).
            if name in ("gesture", 'ngrams_counter'):
                continue
            for value in attrs[name]:
                out.append("<attr name=%s value=%s/>" % (
                    quoteattr(name), quoteattr(value))
                           )
            out.append("<attr name=%s value=%s/>" % (
                quoteattr("path"), quoteattr(item.get("document_url")))
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
        attrs = collections.defaultdict(list)
        for key, val in item.get("Attrs", []):
            attrs[key].append(val)

        if attrs.get("gesture"):
            out.append("<gestures>")
            gest_info = ""
            for gest in attrs.get("gesture"):
                gest_info += "<gesture %s />\n" % gest
            out.append(gest_info)
            out.append("</gestures>")

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
        if not sid:
            sid = kwargs.get("_extend_at", "")
        lang = dict(item.get("Attrs", {})).get("lang", "")
        is_last = kwargs.get("is_last")
        out.append(
            "<snippet sid=\"%s\" language=\" % s\" compound=\"1\" is_last=%s>" % (sid, lang, quoteattr(is_last))
        )

    @classmethod
    def close_item(cls, out, item, **kwargs):
        out.append("</snippet>")


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
        is_last = kwargs.get("is_last")
        sp_attrs = dict(item.get("Attrs", {})).values()
        out.append("<snippet is_last=%s>" % tuple(map(quoteattr, is_last)))
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
        strip = False
        for sent in item["content"]:
            for word_idx in xrange(len(sent["Words"])):
                word = sent["Words"][word_idx]
                prev_word = sent["Words"][word_idx - 1]
                word["Text"] = cls.fix_accent(word["Text"], nodia=nodia)
                if word["Punct"]:
                    if word["Punct"] in ["-"]:
                        strip = True
                    out.append("<text>%s</text>" % escape(word["Punct"]))
                if prev_word.get("Rhyme"):
                    out.append("<br />")
                if strip:
                    text = quoteattr(word["Text"].strip())
                    strip = False
                else:
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


class GraphicWriter(BaseItemWriter):

    @classmethod
    def open_item(cls, out, item, **kwargs):
        result = cls.__compose_one_result(item)
        cls.__write(out, item, result, **kwargs)

    @classmethod
    def __compose_one_result(cls, item):
        start_year = int(item['params'].raw['startyear'][0])
        end_year = int(item['params'].raw['endyear'][0])

        data = item['results']
        parted_queries = data.keys()

        multiply_table_years = set()
        for key in parted_queries:
            for inkey, invalue in data[key]['multiply_years'].items():
                multiply_table_years.add((inkey, invalue[0], invalue[1],))

        table_result = [None] * (len(data[parted_queries[0]]['table']) + len(multiply_table_years))
        for i in range(len(data[parted_queries[0]]['table'])):
            # [str(i) + '-2-' + str(i), i, 0]
            years = data[parted_queries[0]]['table'][i][0]
            i_begin_year = data[parted_queries[0]]['table'][i][1]

            table_result[i] = [
                str(i_begin_year),
                {key: data[key]['graphic'][i_begin_year] for key in parted_queries},
                years
            ]

        index_start = len(data[parted_queries[0]]['table'])
        for i, years in enumerate(multiply_table_years):
            i_begin_year = max(start_year, years[1])
            i_finish_year = min(end_year, years[2])
            index = index_start + i

            table_result[index] = [str(years[1]) + '-' + str(years[2]), {}, years[0]]

            for key in parted_queries:
                value = data[key]['multiply_years'].get(years[0], None)
                if value is None:
                    value = 0
                else:
                    # (year[1], year[2], frequency)
                    for add_to_year in range(i_begin_year, i_finish_year + 1):
                        data[key]['graphic'][add_to_year] += 1

                    value = value[2]

                table_result[index][1][key] = value

        table_result.sort(key=lambda x: x[2], reverse=True)

        graphic_years = [years[1] for years in data[parted_queries[0]]['table']]
        graphic_result = {}
        for key in parted_queries:
            graphic_result[key] = [data[key]['graphic'][year] for year in graphic_years]

        return {'table': table_result, 'years': graphic_years, 'graphic': graphic_result}

    @classmethod
    def __write(cls, out, item, result, **kwargs):
        parted_queries = item['params'].queries_in_order

        for key in parted_queries:
            text = quoteattr(key.strip())
            out.append('\n  <parted_query query=%s />' % (text.decode('utf-8')))

        out.append('\n<tables>')
        for key in parted_queries:
            text = quoteattr(key.strip())
            out.append('\n  <table query=%s>' % (text.decode('utf-8')))
            for values in result['table']:
                cnt = values[1][key]
                out.append('\n    <row year=%s cnt=%s s_created=%s />' % (
                    quoteattr(values[0]), quoteattr(str(cnt)), quoteattr(values[2])))
            out.append('\n  </table>')
        out.append('\n</tables>')

        years = result['years']
        years.sort()
        for key in parted_queries:
            text = quoteattr(key.strip())
            out.append('\n<graphic query=%s>' % (text.decode('utf-8')))
            for i, year in enumerate(years):
                cnt = result['graphic'][key][i]
                out.append('\n    <year year=%s cnt=%s />' % (
                    quoteattr(str(year)), quoteattr(str(cnt))))
            out.append('\n  </graphic>')


class ExcelWriter(object):
    @classmethod
    def open_item(cls, out, item, **kwargs):
        pass

    @classmethod
    def write(cls, out, item, **kwargs):


    @classmethod
    def hchy_to_xlsx(cls, out, item):
        xlsx_object = None
        out.append(xlsx_object)

    @classmethod
    def close_item(cls, out, item, **kwargs):
        pass