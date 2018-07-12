# -*- Encoding: utf-8 -*-
import codecs
import MySQLdb
import MySQLdb.cursors
import time
import urllib

import attribute

max_time = 60 * 5 # 5 minutes

_parser = attribute.Parser()

def _quotetext(s):
    if not s:
        return ""
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def _quoteattr(s):
    return _quotetext(s).replace("'", '&#39;').replace('"', '&#34;').replace('\n', '&#xA;').replace('\r', '&#xD;').replace('\t', '&#x9;')

def ProduceCondition(tableName, fieldName, data):
    l = []

    for el in data:
        y = []

        for e in el:
            neg = ""
            if e[0] == "-":
                neg = "NOT "
                e = e.replace("-", "")
            y.append(u"%sEXISTS(SELECT * FROM %s WHERE %s.id = words.%s AND %s.value = '%s')" % (neg, tableName, tableName, fieldName, tableName, e))

        if y:
            l.append("(%s)" % " AND ".join(y))
    if l:
        return "(%s)" % " OR ".join(l)

    return None

class Attributes:
    def __init__(self, cursor, tableName):
        self.cursor = cursor
        self.tableName = tableName

    def getId(self, val):
        self.cursor.execute(u"SELECT id FROM %s WHERE value = '%s';" % (self.tableName, val))
        res = self.cursor.fetchall()
        if len(res) > 0:
            return res[0][0]
        else:
            return None

    def getValue(self, n):
        self.cursor.execute(u"SELECT value FROM %s WHERE id = %s;" % (self.tableName, n))

        return [x[0] for x in self.cursor.fetchall()]

class Word:
    def __init__(self, query, n):
        place = n + 1
        self.n = n

        self.lex = query.get("lex%s" % place, [""])[0].lower()
        self.lexParsed = _parser.parse(self.lex)

        self.gramm = query.get("gramm%s" % place, [""])[0]
        self.grammParsed = _parser.parse(self.gramm)

        self.flags = query.get("flags%s" % place, [""])[0]
        self.flagsParsed = _parser.parse(self.flags)

        self.father = int(query.get("parent%s" % place, [0])[0]) - 1

        self.linkExists = "link%s" % place in query and self.father >= 0

        self.link = query.get("type%s" % place, [""])[0].lower()
        self.linkParsed = _parser.parse(self.link)

        self.lfVal = int(query.get("parent%s" % place, [0])[0]) - 1
        self.lfExists = "lf%s" % place in query and self.lfVal >= 0
        self.lfFunc = query.get("lf_func%s" % place, [""])[0]
        self.lfFuncParsed = _parser.parse(self.lfFunc)

        self.lfPrep = query.get("lf_prep%s" % place, [""])[0]
        self.lfPrepParsed = _parser.parse(self.lfPrep)

        self.lfTable = 'lf_%d' % self.n if self.lfPrep else 'lexical_functions'

        self.minDist = None
        self.maxDist = None

        self.level = None

        try:
            q = query.get("min%s" % place, [""])[0]
            if len(q) > 0:
                self.minDist = int(q)
        except:
            pass
        try:
            q = query.get("max%s" % place, [""])[0]
            if len(q) > 0:
                self.maxDist = int(q)
        except:
            pass

        if self.maxDist != None and self.minDist == None:
            self.minDist = 0

        if self.minDist != None and self.maxDist != None:
            x = [self.minDist, self.maxDist]
            self.minDist = min(x)
            self.maxDist = max(x)
        elif self.minDist != None:
            if self.minDist == 0:
                self.minDist = None
            elif self.minDist < 0:
                self.maxDist = self.minDist
                self.minDist = None

        try:
            q = query.get("level%s" % place, [""])[0]
            if len(q) > 0:
                self.level = int(q)
        except:
            pass

        # each SQL statement is of the form "CREATE <...> SELECT <...>"
        # so these two lists are in direct element-to-element correspondence
        self.create = []
        self.query = []

    def isWord(self):
        return len(self.lexParsed) > 0 or len(self.grammParsed) > 0 or len(self.flagsParsed) > 0

    def isRelated(self):
        return (self.father >= 0 or self.lfVal >= 0) \
               and ((self.minDist != None and self.maxDist != None) or self.linkExists or self.lfExists)

    def empty(self):
        return not self.isWord() and not self.isRelated()

    def value(self):
        x = 0
        if self.empty():
            x = -1
        else:
            if self.isWord():
                if len(self.lex) > 0:
                    x += 7
                if len(self.gramm) > 0:
                    x += 4
                if len(self.flags) > 0:
                    x += 4
            if self.isRelated():
                if self.linkExists:
                    if len(self.link) > 0:
                        x += 5
                    else:
                        x += 2
                if self.minDist != None or self.maxDist != None:
                    x += 1
        return x

    def xml(self, full=False):
        x = []
        if full:
            x.append(u'n="%s" value="%s"' % (self.n, self.value()))
        if self.level != None:
            x.append(u'level="%s"' % self.level)
        if self.minDist != None and self.maxDist != None:
            x.append(u'distance-min="%s"' % self.minDist)
            x.append(u'distance-max="%s"' % self.maxDist)
        elif self.minDist != None:
            x.append(u'distance-min="%s"' % self.minDist)
        elif self.maxDist != None:
            x.append(u'distance-min="%s"' % self.maxDist)

        if len(self.lex) > 0:
            x.append(u'lex="%s"' % _quoteattr(self.lex))
        if len(self.gramm) > 0:
            x.append(u'gramm="%s"' % _quoteattr(self.gramm))
        if self.flags > 0:
            x.append(u'flags="%s"' % _quoteattr(self.flags))
        if full and self.father >= 0:
            x.append(u'father="%s"' % self.father)
        if len(self.link) > 0:
            x.append(u'link="%s"' % self.link)
        if len(self.lfFunc) > 0:
            x.append(u'lf_func="%s"' % self.lfFunc)
        if full:
            if len(self.create) > 0:
                x.append(u'create="%s"' % '; '.join([_quoteattr(create_clause) for create_clause in self.create]))
            if len(self.query) > 0:
                x.append(u'query="%s"' % '; '.join([_quoteattr(query_clause) for query_clause in self.query]))
        return u'<word %s/>' % " ".join(x)

    def writeTraget(self, prevname, prevcolums, n, relation='syntax'):
        table_name = self.lfTable if relation == 'lexical_function' else 'words'
        from_element_name = 'father' if relation == 'syntax' else 'lf_val'
        x = None
        if n == self.n:
            x = "%s.%s" % (table_name, 'word')
        elif (self.linkExists and self.father == n) or (self.lfExists and self.lfVal == n):
            x = "%s.%s" % (table_name, from_element_name)
        elif n in prevcolums:
            x = "%s.word%s" % (prevname, n)
        return x

    def writeDist(self, prevname, prevcolums, dists, relation='syntax'):
        where = []
        rest = []
        for (son, father, minDist, maxDist) in dists:
            sonname = self.writeTraget(prevname, prevcolums, son, relation)
            fathername = self.writeTraget(prevname, prevcolums, father, relation)

            if sonname != None and fathername != None:
                if minDist != None and maxDist != None:
                    where.append(u"(%s - %s BETWEEN %s AND %s)" % (sonname, fathername, minDist, maxDist))
                elif minDist != None:
                    where.append(u"(%s - %s >= %s)" % (sonname, fathername, minDist))
                elif maxDist != None:
                    where.append(u"(%s - %s <= %s)" % (sonname, fathername, maxDist))
            else:
                rest.append((son, father, minDist, maxDist))
        return (where, rest)

    def formLfPrepQuery(self):
        if not self.lfPrep:
            return ''
        query = 'SELECT lexical_functions.* from lexical_functions, words'

        feature_matching = [('document', 'document'), ('sentence', 'sentence'), ('word', 'lf_prep')]
        # adding parsed attribute conditions (which concern the word form only)
        l = []
        where = []
        for el in self.lfPrepParsed:
            y = []
            for e in el:
                neg = ""
                if e[0] == "-":
                    neg = "!"
                    e = e[1:]
                if e != None:
                    y.append(u"words.form %s= '%s'" % (neg, e))
                if len(y) > 0:
                    l.append(" AND ".join(y))
            if len(l) > 0:
                where.append("(%s)" % " OR ".join(l))
                # basic table correspondence conditions
                join_features = ["words.%s = lexical_functions.%s" % (words_feature, lf_feature) \
                                 for (words_feature, lf_feature) in feature_matching]
                where.append(" AND ".join(join_features))
        query += ' where %s' % ' AND '.join(where)
        return query

    def sql(self, con, prev):
        colums = ["words.document", "words.sentence"]
        tables = []
        where = []
        res = [[], "temp%s" % self.n, []]

        tmpname = None
        if prev != None:
            res[0] = prev[0]
            tmpname = prev[1]
            for el in res[0]:
                colums.append("%s.word%s AS word%s" % (tmpname, el, el))
            if self.n in prev[0]:
                where.append(u"words.word = %s.word%s" % (tmpname, self.n))
            else:
                colums.append("words.word AS word%s" % self.n)
                res[0].append(self.n)
            tables = [prev[1], "words"]
            where.append(u"%s.document = words.document AND %s.sentence = words.sentence" % (tmpname, tmpname))
        else:
            tables.append("words")
            colums.append("words.word AS word%s" % self.n)
            res[0] = [self.n]

        l = []
        for el in self.lexParsed:
            y = []
            for e in el:
                neg = ""
                if e[0] == "-":
                    neg = "!"
                    e = e.replace("-", "")
                if e[0] == '"':
                    y.append(u"words.form %s= '%s'" % (neg, e.replace('"', "")))
                else:
                    y.append(u"words.lex %s= '%s'" % (neg, e))
            if len(y) > 0:
                l.append("(%s)" % " AND ".join(y))
        if len(l) > 0:
            where.append("(%s)" % " OR ".join(l))

        l = ProduceCondition("gramms", "gramm", self.grammParsed)
        if l:
            where.append(l)

        l = ProduceCondition("flags", "flags", self.flagsParsed)
        if l:
            where.append(l)

        if self.linkExists:
            if self.father not in res[0]:
                colums.append("words.father AS word%s" % self.father)
                res[0].append(self.father)
                where.append(u"words.father IS NOT NULL")
            else:
                where.append(u"words.father = %s.word%s" % (tmpname, self.father))

            l = []
            for el in self.linkParsed:
                y = []
                for e in el:
                    neg = ""
                    if e[0] == "-":
                        neg = "!"
                        e = e[1:]
                    e = con.links.getId(e)
                    if e != None:
                        y.append(u"words.link %s= '%s'" % (neg, e))
                if len(y) > 0:
                    l.append(" AND ".join(y))
            if len(l) > 0:
                where.append("(%s)" % " OR ".join(l))

        if self.lfExists:
            join_features = ["words.%s = %s.%s" % (feature, self.lfTable, feature) \
                             for feature in ['document', 'sentence', 'word']]
            where.append(" AND ".join(join_features))
            if self.lfPrep:
                create_tmp = 'CREATE TEMPORARY TABLE %s (' % self.lfTable
                create_tmp += 'document INTEGER,'
                create_tmp += 'sentence INTEGER,'
                create_tmp += 'word SMALLINT,'
                create_tmp += 'lf_val SMALLINT,'
                create_tmp += 'lf_prep SMALLINT,'
                create_tmp += 'lf_func VARCHAR(32),'
                create_tmp += 'PRIMARY KEY (document, sentence, word, lf_val, lf_prep, lf_func))'
                create_tmp += ' ENGINE = MyISAM'
                self.create.append(create_tmp)
                self.query.append(self.formLfPrepQuery())
            tables.append(self.lfTable)
            if self.lfVal not in res[0]:
                colums.append("%s.lf_val AS word%s" % (self.lfTable, self.lfVal))
                res[0].append(self.lfVal)
            elif tmpname:
                where.append(u"%s.lf_val = %s.word%s" % (self.lfTable, tmpname, self.lfVal))
            elif self.linkExists:
                where.append(u"%s.lf_val = words.father" % (self.lfTable))

            l = []
            for el in self.lfFuncParsed:
                y = []
                for e in el:
                    neg = ""
                    if e[0] == "-":
                        neg = "!"
                        e = e[1:]
                    if e != None:
                        y.append(u"%s.lf_func %s= '%s'" % (self.lfTable, neg, e))
                if len(y) > 0:
                    l.append(" AND ".join(y))
            if len(l) > 0:
                where.append("(%s)" % " OR ".join(l))

        # conditions on syntactic relation distance
        if self.linkExists:
            distances = self.makeDistances(self.father, tmpname, prev, 'syntax')
            if len(distances) > 1:
                where.extend(distances[0])
                res[2].extend(distances[1])
        # condition on lexical function relation distance
        if self.lfExists:
            distances = self.makeDistances(self.lfVal, tmpname, prev, 'lexical_function')
            if len(distances) > 1:
                where.extend(distances[0])
                res[2].extend(distances[1])

        if con.docid >= 0:
            where.append(u"words.document = %s" % (con.docid))

        if len(where) == 0:
            where.append("TRUE")
        self.query.append("SELECT DISTINCT %s FROM %s WHERE %s" % (", ".join(colums), ", ".join(tables), " AND ".join(where)))

        request = []
        request.append("CREATE TEMPORARY TABLE `%s` (" % res[1])
        request.append("`document` INTEGER NOT NULL,")
        request.append("`sentence` SMALLINT NOT NULL,")
        t = ["`document`", "`sentence`"]
        for el in res[0]:
            request.append("`word%s` SMALLINT NOT NULL," % el)
            t.append("`word%s`" % el)
        request.append("INDEX `KEY` (%s)" % ", ".join(t))
        request.append(") ENGINE = MEMORY")

        self.create.append(" ".join(request))

        res[0].sort()
        return res

    def makeDistances(self, in_from_element, in_tmpname, in_prev, in_relation):
        dists = []
        if self.minDist != None or self.maxDist != None:
            dists.append((self.n, in_from_element, self.minDist, self.maxDist))

        if in_prev != None:
            dists.extend(in_prev[2])

        if in_prev != None:
            dists = self.writeDist(in_tmpname, in_prev[0], dists, in_relation)
        else:
            dists = self.writeDist(in_tmpname, [], dists, in_relation)
        return dists

class Search:
    def __init__(self, query, db, out):
        self.db = db
        self.docid = -1
        self.stype = "all-documents"
        self.cursor = self.db.cursor()
        self.out = codecs.getwriter("utf8")(out, 'xmlcharrefreplace')
        self.time = 0
        self.page = 0
        self.dpp = 10 # documents per page
        self.spd = 10 # snippets per document
        self.spp = 50 # snippets per page
        self.gramms = Attributes(self.cursor, "gramms")
        self.flags = Attributes(self.cursor, "flags")
        self.links = Attributes(self.cursor, "links")
        self.words = []
        self.query = []
        self.colums = None
        self.table = None
        self.doSearch = True
        self.writeWordInfo = False
        self.get_corpus_stats()

        self.docid = int(query.get("docid", [-1])[0])
        if self.docid >= 0:
            self.stype = "document"
            self.page = int(query.get("ps", [self.page])[0])
        else:
            self.page = int(query.get("p", [self.page])[0])

        text = query.get("text", [""])[0]
        if text == "word-info":
            self.stype = "word-info"
            self.source = query.get("source", [""])[0]
            self.doSearch = False
            self.writeWordInfo = True
        elif text == 'document-info':
            self.doSearch = False
            self.stype = 'document-info'
        else:
            try:
                self.dpp = int(query.get("dpp", [self.dpp])[0])
                self.spd = int(query.get("spd", [self.spd])[0])
                self.spp = int(query.get("spp", [self.spp])[0])
            except:
                pass

            if text == "lexform":
                tokens = query.get("req", [""])[0].replace("&", " ").replace("|", " ").replace(",", " ").replace("(", " ").replace(")", " ").replace("\"", " ").split()
                for index, token in enumerate(tokens):
                    real_index = index + 1
                    query["lex%s" % real_index] = ['"%s"' % token]
                    if real_index > 1:
                        query["min%s" % real_index] = ["1"]
                        query["max%s" % real_index] = ["1"]
                        query["parent%s" % real_index] = [real_index - 1]

            while "lex%s" % (len(self.words) + 1) in query:
                self.words.append(Word(query, len(self.words)))

    def get_corpus_stats(self):
        self.cursor.execute("SELECT documents_number, sentences_number, words_number FROM corpus_stats;")
        self.total_documents, self.total_sentences, self.total_words = self.cursor.fetchall()[0]

    def request(self):
        self.query = [x for x in self.words if not x.empty()]
        self.query.sort(cmp=lambda x,y: cmp(x.value(), y.value()), reverse=True)

        table = None
        for el in self.query:
            table = el.sql(self, table)
        self.colums = table[0]
        self.table = table[1]

    def hit(self):
        self.time = 0
        begin = time.time()
        last = begin
        prev = None
        for el in self.query:
            if self.time > max_time:
                raise Exception
            if not el.empty():
                assert len(el.create) == len(el.query)
                for (create_clause, query_clause) in zip(el.create, el.query):
                    self.cursor.execute("%s %s" % (create_clause, query_clause))
                self.time += time.time() - last
                last = time.time()
                if prev != None:
                    self.cursor.execute("DROP TABLE IF EXISTS temp%s;" % (prev))
                prev = el.n

    def writeAnaEl(self, name, vals):
        self.out.write('<el name="%s">' % name)
        self.out.write("<el-group>")
        for el in vals:
            self.out.write("<el-atom>%s</el-atom>" % _quoteattr(el))
        self.out.write("</el-group>")
        self.out.write("</el>")

    def writeWord(self, lex, gramm, text, target = False):
        if text != None:
            source = "|".join((lex, str(gramm), text))
            source = urllib.quote(codecs.getencoder("utf8")(source)[0])
            self.out.write('<word text="%s" source="%s"' % (_quoteattr(text), _quoteattr(source)))
            if target:
                self.out.write(' target="1"')
            self.out.write(">")
            if self.writeWordInfo:
                self.out.write("<ana>")
                self.writeAnaEl("lex", [lex])
                self.writeAnaEl("gramm", self.gramms.getValue(gramm))
                self.out.write("</ana>")
            self.out.write("</word>")

    def searchResult(self):
        self.cursor.execute("SELECT DISTINCT COUNT(DISTINCT document), COUNT(DISTINCT document, sentence), COUNT(*) FROM `%s`;" % self.table)
        res = self.cursor.fetchall()
        documentCount = res[0][0]
        sentenceCount = res[0][1]
        hitCount = res[0][2]

        self.out.write('<result documents="%s" sentences="%s" contexts="%s" search-type="%s">' % (documentCount, sentenceCount, hitCount, _quoteattr(self.stype)))
        
        self.out.write('<corp-stat> <documents total="%d"/> <sentences total="%d"/> <words total="%d"/> </corp-stat>' % (self.total_documents, self.total_sentences, self.total_words))

        pmin = self.page * self.dpp
        pmax = self.dpp
        if self.stype == "document":
            pmin = 0
            pmax = 1

        self.cursor.execute(
            "SELECT DISTINCT document, url, title, image, COUNT(DISTINCT sentence) FROM `%s`, `documents` WHERE %s.document = documents.id GROUP BY document LIMIT %s, %s" %
            (self.table, self.table, pmin, pmax))

        docs = self.cursor.fetchall()

        if len(docs) > 2:
            self.cursor.execute("DELETE FROM `%s` WHERE document < %s OR document > %s;" % (self.table, docs[0][0], docs[-1][0]))

        for (document, url, title, image, snippets) in docs:
            self.out.write('<document id="%d" path = "%s" title="%s" tagging="manual" snippets="%s">' % (document, _quoteattr(url), _quoteattr(title), snippets))

            pmin = 0
            pmax = self.spd
            if self.stype == "document":
                pmin = self.page * self.spp
                pmax = self.spp

            self.cursor.execute("SELECT DISTINCT sentence FROM %s WHERE %s.document = %s LIMIT %s, %s" % (self.table, self.table, document, pmin, pmax))

            sentences = self.cursor.fetchall()
            if len(sentences) > 2:
                self.cursor.execute("DELETE FROM `%s` WHERE document = %s AND (sentence < %s OR sentence > %s);" % (self.table, document, sentences[0][0], sentences[-1][0]))

            for (sentence,) in sentences:
                self.out.write("<snippet sid=\"%d\" url=\"%s_%s\">" % (sentence, _quoteattr(image), sentence))

                tar = []
                for el in self.colums:
                    tar.append("%s.word%s = words.word" % (self.table, el))
                tar = "SELECT * FROM %s WHERE %s.document = %s AND %s.sentence = %s AND (%s)" % (self.table, self.table, document, self.table, sentence, " OR ".join(tar))
                self.cursor.execute("SELECT lex, gramm, trash, text, EXISTS(%s) FROM words WHERE document = %s AND sentence = %s" % (tar, document, sentence))

                for (lex, gramm, trash, text, target) in self.cursor.fetchall():
                    self.out.write("<text>%s</text>" % _quotetext(trash))
                    self.writeWord(lex, gramm, text, target)
                self.out.write("</snippet>")
            self.out.write("</document>")
        self.out.write("</result>")

    def writeDocumentInfo(self, in_docid):
        self.cursor.execute("SELECT title, url FROM documents WHERE id = %s" % in_docid)
        docs = self.cursor.fetchall()

        assert len(docs) == 1
        (title, url) = docs[0]
        self.out.write('<document id="%s" path = "%s" title="%s" tagging="manual" snippets="0">' % (in_docid, _quoteattr(url), _quoteattr(title)))
        self.out.write('<attributes>')
        self.out.write('<attr name="header" value="%s" />' % _quoteattr(title))
        self.out.write('</attributes>')
        self.out.write('</document>')


    def result(self):
        if self.doSearch:
            self.searchResult()
        else:
            self.out.write("<result>")
            if self.stype == 'document-info':
                self.writeDocumentInfo(self.docid)
            else:
                query = self.source.split("|")
                if len(query) > 2:
                    self.writeWord(query[0], int(query[1]), query[2])
            self.out.write("</result>")

    def execute(self):
        self.out.write(u"<body>")

        if self.doSearch:
            self.request()
            self.hit()
        self.out.write(u'<request page="%s">' % self.page)
        self.out.write(u'<format documents-per-page="%s" snippets-per-document="%s" snippets-per-page="%s"/>' % (self.dpp, self.spd, self.spp))
        self.out.write(u'<query request="something">')
        for el in self.words:
            self.out.write(el.xml())
        self.out.write(u"</query>")
        self.out.write(u'<sql>')
        for el in self.query:
            self.out.write(el.xml(True))
        self.out.write(u'</sql>')
        self.out.write(u"</request>")

        times = time.time()
        self.result()
        self.out.write(u'<sysinfo search-time="%s" write-time="%s"/>' % (self.time, time.time() - times))

        self.out.write(u"</body>")
