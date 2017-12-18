# -*- coding: utf-8 -*-

from copy import copy, deepcopy


def slice_by_type(item_top, target_type, out=None, path=None, init=True):
    """
    Given a tree-like :item_top, returns slice of top-level :target_type
    elements found in the tree during depth-first search. This means that
    search doesn't proceed deeper down some path after the first hit.

    Each found item is returned with the path to root node (as a list of
    type-strings, stored by the "path" key).

    :param item_top: A dict with the following structure:
                     {
                         "type": "some_string",
                         "items": [item1, item2, ...]
                     }
    :param out:  for internal usage only, shouldn't be provided
    :param path: for internal usage only, shouldn't be provided
    :param init: for internal usage only, shouldn't be provided

    """
    # Initialize during the first call
    if init:
        out, path = list(), list()
    # If there's a match, don't go deeper
    if item_top["type"] == target_type:
        item_top["path"] = deepcopy(path)
        out.append(item_top)
    else:
        # If there are children, append yourself to the path and go deeper
        if "items" in item_top:
            trace = copy(item_top)
            trace["items"] = list()
            path.append(trace)
            for item in item_top["items"]:
                slice_by_type(
                    item, target_type, out=out, path=path, init=False
                )
        # After all children are processed, remove youself from the path
        if path:
            path.pop()
    if out:
        return out
    else:
        return None


def restore_hierarchy(items):
    """
    Given a slice of align-items with stored paths to root, restores as much
    of the initial hierarchy as possible.

    """
    items = [restore_root(item) for item in items]
    merged = items.pop(0)
    for item in items:
        merge_items(merged, item)
    return merged


def merge_items(dst, src):
    if not _equals(dst, src):
        raise Exception("Merged items have different roots!")
    for src_child in _children(src):
        dst_child = _get_child_with_id(dst, src_child["_id"])
        if dst_child:
            merge_items(dst_child, src_child)
        else:
            _children(dst).append(src_child)


def restore_root(item):
    # If there is no path, consider the item to be its own root
    if not item["path"]:
        return item
    path = item.pop("path") + [item]
    root = path.pop(0)
    pointer = root["items"]
    for node in path:
        pointer.append(node)
        if "items" in pointer[0]:
            pointer = pointer[0]["items"]
    return root


def _get_child_with_id(item, target_id):
    out = None
    for child in _children(item):
        if child["_id"] == target_id:
            out = child
            break
    return out


def _equals(a, b):
    return a["_id"] == b["_id"]


def _children(item):
    return item.get("items", [])


def _has_children(item):
    return "items" in item


def example(target_type):
    hchy = {
        "type": "a",
        "_id": "a:0",
        "items": [
            {
                "_id": "b:0",
                "type": "b",
                "items": [
                    {
                        "_id": "c:0",
                        "type": "c",
                        "items": [
                            {
                                "_id": "d:0",
                                "type": "d"
                            }
                        ]
                    },
                    {
                        "_id": "c:1",
                        "type": "c"
                    },
                    {
                        "_id": "c:2",
                        "type": "c"
                    },
                ]
            },
            {
                "_id": "b:1",
                "type": "b",
                "items": [
                    {
                        "_id": "c:3",
                        "type": "c"
                    },
                    {
                        "_id": "c:4",
                        "type": "c"
                    },
                    {
                        "_id": "c:5",
                        "type": "c"
                    },
                ]
            },
            {
                "_id": "x:0",
                "type": "x",
                "items": [
                    {
                        "_id": "b:2",
                        "type": "b",
                        "items": [
                            {
                                "_id": "c:6",
                                "type": "c"
                            },
                            {
                                "_id": "c:7",
                                "type": "c"
                            },
                            {
                                "_id": "c:8",
                                "type": "c"
                            },
                        ]
                    },
                ]
            },
            {
                "_id": "b:3",
                "type": "b",
                "items": [
                    {
                        "_id": "c:9",
                        "type": "c"
                    },
                    {
                        "_id": "c:10",
                        "type": "c"
                    },
                    {
                        "_id": "c:11",
                        "type": "c"
                    },
                ]
            },
        ]
    }
    out = slice_by_type(hchy, target_type)
    merged = restore_hierarchy(out)
    if hchy != merged:
        raise Exception("Source and restored hierarchies are not equal!")
    else:
        print "O.K."


if __name__ == "__main__":
    example("b")
