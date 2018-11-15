#!/usr/bin/python

# -*- encoding: utf-8 -*-

import StringIO
import logging
import lxml.etree as ET

parser = ET.XMLParser(load_dtd=True)
report_xslt = ET.parse("render/xsl/report.xsl", parser)
report_transformation = ET.XSLT(report_xslt)
explain_xslt = ET.parse("render/xsl/explain.xsl", parser)
explain_transformation = ET.XSLT(explain_xslt)

graphic_report_xslt = ET.parse("render/xsl/graphic_report.xsl", parser)
graphic_report_transformation = ET.XSLT(graphic_report_xslt)

ngram_xslt = ET.parse("render/xsl/ngram.xsl", parser)
ngram_transformation = ET.XSLT(ngram_xslt)

with open("render/xsl/langs.xml") as f:
    f.readline()
    langs = f.read().decode("utf-8").encode("utf-8")
    langs += "\n"

with open("render/xsl/settings.xml") as f:
    f.readline()
    settings = f.read().decode("utf-8").encode("utf-8")
    settings += "\n"

with open("render/xsl/graphic_years.xml") as f:
    f.readline()
    graphic_years = f.read().decode("utf-8").encode("utf-8")
    graphic_years += "\n"


def tostring(node, **kwargs):
    return ET.tostring(node, **kwargs);

def transform(search_result, params):
    mode = params.get('mode', [''])[0]

    output = StringIO.StringIO()
    output.write('<?xml version=\'1.0\' encoding=\'utf-8\'?>\n')
    output.write('<page>\n')
    output.write('<searchresult>\n')
    output.write(search_result)
    output.write('</searchresult>\n')
    output.write('<state>\n')

    if mode.startswith('graphic'):
        for key in ('lang', 'mode', 'startyear', 'endyear', 'smoothing'):
            value = params[key][0]
            if key == 'mode':
                value = value.replace('graphic_', '')
            output.write('<param name="%s">%s</param>\n' % (key, value))
        output.write('</state>\n')
        output.write(langs)
        output.write(settings)
        output.write(graphic_years)
        output.write('</page>\n')
        source_xml = ET.fromstring(output.getvalue())
        result = graphic_report_transformation(source_xml)

    else:
        for key in params:
            for value in params[key]:
                if "sem" in key:
                    continue
                output.write('<param name="%s">%s</param>\n' % (key, value))
        output.write('</state>\n')
        output.write(langs)
        output.write(settings)
        output.write('</page>\n')
        source_xml = ET.fromstring(output.getvalue())

        if mode.startswith('ngram'):
            return ngram_transformation(source_xml)

        if params.get("text", [""])[0] in ("document-info", "word-info"):
            result = explain_transformation(source_xml)
        else:
            result = report_transformation(source_xml)
    return result
