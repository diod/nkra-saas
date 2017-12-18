def all_sents(doc):
    for part in doc["Parts"]:
        for sent in part["Sents"]:
            yield sent


def all_words(doc):
    for sent in all_sents(doc):
        for word in sent["Words"]:
            yield word


def append_attr(node, attr, value):
    if attr not in node:
        node[attr] = value
    elif type(node[attr]) is list:
        if value not in node[attr]:
            node[attr].append(value)
    elif value != node[attr]:
        node[attr] = [node[attr], value]


def append_flags(word, prefix, values):
    for value in values:
        append_flag(word, prefix + value)


def append_flag(word, value):
    append_attr(word, "flags", value)


def _is_str(value):
    return type(value) is str or type(value) is unicode


def _is_list(value):
    return type(value) is list and len(value) > 0 and _is_str(value[0])


def is_attr_value(value):
    return _is_str(value) or _is_list(value)


def attr_values(value):
    if _is_str(value):
        yield value
    elif _is_list(value):
        for item in value:
            yield item


def _pack_value(value):
    if _is_str(value):
        return [value]
    elif _is_list(value):
        return value


def attrs(node):
    for key, value in node.items():
        if is_attr_value(value):
            yield (key, _pack_value(value))


def ordered_attrs(node, subcorpus):
    ATTRS_ORDER = ("lex", "gr")
    for attr in ATTRS_ORDER:
        if attr in node:
            yield attr, _pack_value(node[attr])
    for key, value in attrs(node):
        if key not in ATTRS_ORDER:
            yield key, value
