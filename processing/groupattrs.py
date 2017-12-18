# -*- coding: utf-8 -*-


def set_groupattrs(doc):
    # just a wrapper, see the functions below
    _collect_groupattr(doc, "linked_fragments")
    _set_id(doc)


def _collect_groupattr(doc, attr_name):
    """
    Gets all values corresponding to attr_name in a list of tuples stored in
    doc["Attrs"] and merge them into a single "|"-separated line; then store
    the line by the "gr_{attr_name}" key in doc["GroupAttrs"].

    """
    values = list()
    for name, value in doc["Attrs"]:
        if name == attr_name:
            values.append(value)
    if values:
        joinedValue = "|".join(sorted(values))
        _set_groupattr(doc, "gr_" + attr_name, joinedValue)


def _set_groupattr(doc, attr_name, value):
    # too obvious for a docstring
    doc["GroupAttrs"][attr_name] = value


def _set_id(doc):
    """
    Find, parse and set doc_id (if present).

    """
    for name, value in doc["Attrs"]:
        if name == "fragment_id":
            frag_id = int(value.rsplit("_", 1)[-1].split(".", 1)[0])  # lol
            _set_groupattr(doc, "gr_id",  str(frag_id))
            return
