# -*- coding: utf-8 -*-

import base64
import urllib
import logging
import itertools

from processing.simplifier import simplify_inner_utf8
from processing.simplifier import simplify_modern_utf8

"""
This file contains classes and functions for incoming request params
processing.

"""


class SearchParams(object):
    """
    This class is used as a pre-processor and container for the search
    parameters received in the HTTP request.

    """

    def __init__(self, query=None):
        """
        Load query parameters as SearchParams' attributes.

        :param query: the query dict as returned by urlparse.parse_qs().

        """
        if query:
            self._cleanse(query)
        if query.get("text") == ["meta"]:
            query["req"] = ["*"]
        logging.info(query)
        self.subcorpus = ""
        self.expand_snippets = False
        self.join_grouped_docs = True
        self.req = self._load(query, 'req', self._first, default='')
        self.text = self._load(query, 'text', self._first)
        self.page = self._load(query, 'p', self._first_int, default=0)
        self.mode = self._load(query, 'mode', self._resolve_mode)
        self.source = self._load(query, 'source', self._base64_decode)
        self.radius = self._load(query, 'sr', self._first_int, default=1)
        self.sent_id = self._load(query, 'sid', self._first)
        self.doc_id = self._load(query, 'docid', self._base64_decode)
        self.sort_by = self._load(query, 'sort', self._first, default='')
        self.seed = self._load(query, 'seed', self._first_int, default=0)
        self.group_by = self._load(query, 'g', self._first, default='s_url')
        self.diacritic = self._load(
            query, 'nodia', self._first_bool, default=0)
        self.docs_per_page = self._load(query, 'dpp', self._first_int, 10)
        self.snippets_per_doc = self._load(query, 'spd', self._first_int, 5)
        self.subcorpus = self._load_subcorpus(query)
        # We need this for correct doc info and all examples queries
        if self.doc_id and "#" in self.doc_id:
            self.doc_id = self.doc_id.split("#")[0]
        # incorporate raw parameters
        self.raw = query
        self.expand_all_snippets = False
        self.search_type = self._load_search_type()
        if self.mode in ["murco"] and self.text == "meta":
            self.group_by = "gr_author"

    def __iter__(self):
        """
        Implemented to conform to the iterator protocol.

        """
        return iter(self.raw)

    def __getitem__(self, item):
        """
        Implemented to provide dictionary-like functionality for querying.

        """
        return self.raw[item]

    def _cleanse(self, raw_query):
        """
        """
        for k, v in raw_query.items():
            raw_query[k] = [x.replace(" | ", "|") for x in v]
            raw_query[k] = [x.replace(" & ", " ") for x in v]

    def _load(self, query, key, using=None, default=None):
        """
        Return @query[@key] applying the @using callback if it's provided. If
        there's no such key in the query, the @default value is returned.

        """
        value = query.get(key, None)
        if value:
            if using:
                value = using(value)
            return value
        else:
            return default

    def _first(self, value):
        """
        Treats the @value as list; returns the first element.

        """
        return value[0]

    def _first_int(self, value):
        """
        Treats the @value as list; return the first element cast to an integer.

        """
        return int(value[0])

    def _first_bool(self, value):
        """
        Treats the @value as list; return the first element cast to an boolean.

        """
        return True if value[0] == "1" else False

    def _resolve_mode(self, value):
        """
        Treats the @value as list; checks the first element for a concrete
        value.

        """
        if value[0] == 'multiparc':
            self.expand_all_snippets = True
            self.sort_by = 'url'
        return value[0]

    def _base64_decode(self, value):
        """
        Treats the @value as list; base64-encodes the first element.

        """
        return base64.b64decode(value[0])

    def _load_subcorpus(self, query):
        """Loads all parameters that start with doc_. Initializes
        self.subcorpus and fills it with doc_*-params' values.

        Subcorpus details are later appended to the `text` parameter
        value in final SAAS request string (see search_result.py).

        Args:
            query: a dictionary of url key-value parameter pairs.
        Returns:
            A string representing the final query (augmented with
            subcorpus details).
        """
        if 'mode' not in query:
            return ""
        if 'mycorp' in query:
            mycorp = urllib.unquote(query['mycorp'][0])
            if "main" in mycorp:
                return " s_tagging:\"manual\""
            else:
                out = mycorp.replace("lang", "s_lang")
                out = " " + out.replace("|", " | ")
                return out
        subcorpus = ""
        sub_params = [k for k in query.keys() if k.startswith('doc_') or "_sp_" in k]
        if sub_params:
            for sub_param in sub_params:
                subcorpus += self._process_doc_param(
                    sub_param, query[sub_param][0])
            return subcorpus
        else:
            return ""

    def _process_doc_param(self, param, val):
        """Parses a subcorpus param/value pair.

        What goes on here is translation from initital query (as it comes
        from frontend) to what can be understood by SAAS.

        Args:
            param: a string parameter name, always starting with `doc`.
            val: a string parameter value.

        Returns:
            A string with finalized param/value representation (suitable
            for SAAS).
        """
        s_param = param.replace("doc_", "s_")
        # It's a logical "not".
        if val.startswith("-"):
            return '(%s:"*" ~~ %s:"%s")' % (s_param, s_param, val[1:])
        # Disjunctive queries. `doc_sex=муж|жен` should be translated to
        # `(s_sex="муж" | s_sex="жен")`.
        if "|" in val:
            decomposed_query = " | ".join(
                ['%s:"%s"' % (s_param, x.strip()) for x in val.split("|")])
            return " (%s)" % decomposed_query
        # Less than queries. `doc_l_created=1900` should be translated to
        # `s_created:<1900`.
        if "_l_" in s_param:
            s_param = s_param.replace("l_", "")
            val = '<"%s"' % val
            return ' (%s:%s)' % (s_param, val)
        # Greater than queries. `doc_g_created=1900` should be translated to
        # `s_created:>1900`.
        if "_g_" in s_param:
            s_param = s_param.replace("g_", "")
            val = '>"%s"' % val
            return ' (%s:%s)' % (s_param, val)
        return ' (%s:"%s")' % (s_param, val)

    def _load_search_type(self):
        search_type = "all-documents"
        if self.text == "meta":
            search_type = self.text
        if self.sort_by in ["cont1", "cont2"]:
            search_type = "snippets-titles"
        return search_type


class ParamsProcessor(object):
    """
    This static class provides methods for preprocessing ceratin fields of
    SearchParams.

    """
    @classmethod
    def parse_lexform_cgi(cls, params):
        """
        Generates a final search string which will be passed to the search
        server. Used for queries with text=lexform.

        :param params: a SearchParams instance

        :return: a query string

        """
        words = params.req.split(' ')
        query_len = len(words)
        nodes = []
        for word in words:
            nodes.append('sz_form:"%s"' % word)
        full_query = ' /+1 '.join(nodes)
        return full_query, query_len

    @classmethod
    def parse_lexgramm_cgi(cls, params):
        """
        Generates a final search string which will be passed to the search
        server. Used for queries with text=lexgramm.

        :param params: a SearchParams instance

        :return: a params string

        """
        nodes, special = cls._extract_numerated_params(params)
        cls._maybe_simplify(nodes)
        full_query = ''
        query_len = 0
        nodes_count = len(nodes)
        for i, ind in enumerate(sorted(nodes.keys())):
            params = nodes.get(ind, {})
            spec_params = special.get(ind, {})
            min_dist = spec_params.get('min', '+1')
            max_dist = spec_params.get('max', '+1')
            if min_dist[0] not in '+-0':
                min_dist = '+%s' % min_dist
            if max_dist[0] not in '+-0':
                max_dist = '+%s' % max_dist
            node_query = []
            query_len = 0
            for param, value in params.items():
                if param not in ('min', 'max', 'sem-mod', 'parent', 'level'):
                    subnodes, subquery_len = cls._build_node_query(
                        param, value)
                    query_len += subquery_len
                    node_query.append(subnodes)
            node_query = ' /0 '.join(node_query)
            full_query += '(%s)' % node_query
            if i < nodes_count - 1:
                full_query += ' /(%s %s) ' % (min_dist, max_dist)
        if nodes_count > 1:
            query_len = nodes_count
        return full_query, query_len

    @classmethod
    def _maybe_simplify(cls, nodes):
        for param in nodes.values():
            for param_name, param_value in param.items():
                if param_name in ['lexi', 'formi']:
                    param[param_name] = simplify_inner_utf8(param_value)
                if param_name in ['lexm', 'formm']:
                    param[param_name] = simplify_modern_utf8(param_value)

    @classmethod
    def _extract_numerated_params(cls, query):
        nodes = {}
        special = {}
        for param in query:
            value = query[param][0]
            if not value:
                continue
            num = ''
            while param and param[-1] in '0123456789':
                num = param[-1] + num
                param = param[:-1]
            if not param or not num:
                continue
            if param in ('min', 'max', 'sem-mod', 'parent', 'level'):
                if num not in special:
                    special[num] = {}
                special[num][param] = value
            else:
                if num not in nodes:
                    nodes[num] = {}
                nodes[num][param] = value
        return nodes, special

    @classmethod
    def _build_node_query(cls, param, value):
        value = value.replace(' ', '&')
        value = value.replace(',', '&')
        tree = _parse(value)
        if param == 'gramm':
            param = 'gr'
            tree = _get_dnf(tree)
            tree = _join_disjuncts(tree)
        result = _get_subs(tree, param)
        return result


class ParseException(Exception):
    pass


def _parse(s):
    stack = []
    word = ''
    brackets = []
    for c in s:
        if c not in '()|&':
            word += c
        else:
            if word.strip():
                stack.append(word.strip())
                word = ''
            if c == '(':
                brackets.append(len(stack))
                stack.append(c)
            elif c == ')':
                if not brackets:
                    raise ParseException()
                stack[brackets[-1]
                    :] = [_parse_substack(stack[brackets[-1] + 1:])]
                brackets.pop()
            else:
                stack.append(c)
    if brackets:
        raise ParseException()
    if word.strip():
        stack.append(word.strip())
    return _parse_substack(stack)


def _parse_substack(substack):
    if len(substack) % 2 == 0:
        raise ParseException()
    conjuncts = []
    cur_conjunct = [substack[0]]
    for i in range(1, len(substack), 2):
        if substack[i] == '&':
            cur_conjunct.append(substack[i + 1])
        elif substack[i] == '|':
            conjuncts.append(cur_conjunct)
            cur_conjunct = [substack[i + 1]]
        else:
            raise ParseException()
    if cur_conjunct:
        conjuncts.append(cur_conjunct)
    for i in range(len(conjuncts)):
        if len(conjuncts[i]) == 1:
            conjuncts[i] = conjuncts[i][0]
        else:
            conjuncts[i] = ('&', conjuncts[i])
    if len(conjuncts) == 1:
        return conjuncts[0]
    return '|', conjuncts


def _get_child_operands(tree):
    if type(tree) is str:
        return [tree]
    operator, operands = tree
    child_operands = []
    for operand in operands:
        if type(operand) == str:
            child_operands.append(operand)
        else:
            suboperator, suboperands = operand
            if suboperator == "|":
                child_operands += suboperands
            else:
                child_operands.append(operand)
    return child_operands


def _flatten(tree):
    if type(tree) is str:
        return tree
    operator, operands = tree
    operands = list(map(_flatten, operands))
    if operator in "|&" and len(operands) == 1:
        return operands[0]
    i = 0
    while i < len(operands):
        operand = operands[i]
        if not (type(operand) is str) and operand[0] == operator:
            operands[i:i + 1] = operand[1]
        else:
            i += 1
    return operator, operands


def _get_dnf(tree):
    if type(tree) is str:
        return tree
    operator, operands = tree
    operands = map(_get_dnf, operands)
    operator, operands = _flatten((operator, operands))
    if operator == "&":
        operator = "|"
        sub_operands = list((_get_child_operands(sub_tree)
                             for sub_tree in operands))
        operands = []
        for item in itertools.product(*sub_operands):
            operands.append(('&', list(item)))
    return _flatten((operator, operands))


def _join_disjuncts(tree):
    if type(tree) is str:
        return tree
    operator, operands = tree
    operands = list(map(_join_disjuncts, operands))
    if operator == "&":
        return ",".join(sorted(operands))
    return operator, operands


def _get_clause(param, value):
    if param in ("form", "lex"):
        if value.startswith("*"):
            rparam = "r" + param
            rvalue = value.decode("utf-8")[::-1].encode("utf-8")
            return '(sz_%s:"%s")' % (rparam, rvalue), 1
        elif u"*" in value.decode("utf8")[1:-1]:
            rparam = "r" + param
            left, right = value.decode("utf-8").split("*", 1)
            left = left.encode("utf-8") + "*"
            rright = right[::-1].encode("utf-8") + "*"
            return '(sz_%s:"%s" /0 sz_%s:"%s")' % (param, left, rparam, rright), 2
    return 'sz_%s:"%s"' % (param, value), 1


def _get_subs(tree, param):
    if type(tree) is str:
        if tree.startswith("-"):
            return '(sz_lex:"*" ~/0 %s)' % _get_clause(param, tree[1:])[0], 1
        else:
            return _get_clause(param, tree)
    operator, operands = tree
    if operator == "&":
        operator = " /0 "
        nodes_count = len(operands)
    else:
        operator = " %s " % operator
        nodes_count = 1
    operands = map(lambda x: _get_subs(x, param)[0], operands)
    result = operator.join(operands)
    if operator != " /0 ":
        result = "(" + result + ")"
    return result, nodes_count


if __name__ == "__main__":
    pass
