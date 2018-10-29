# -*- coding: utf-8 -*-

import sys
import json
import xml.sax

# Some corpora are "flat" in the sense that there's no larger elements
# than "se" that we can use for aligning. (See doc["align by"].)
# For such cases we need to add artificial align items of type
# self.flat_type.
FLAT_TYPE = "flat"
SINGLE_FILE_TYPE = "single_file"

# Field align_by defines the item by which the document will be split
# into subdocuments while indexing. Document splitting is required
# because some documents are to large to be read by the indexer.
#
# Field snippet_type defines the items that will form context of any
# hit. For example, if there is a hit in some sentence and we always
# want to show the preceding and following sentence, snippet_type
# should be "se".
#
# Field context defines the number of snippet_type-items to the left and
# to the right of the hit to be shown.
KNOWN_CORPUS_TYPES = {
    "old_rus": {
        "prefix": "old_rus",
        "align_by": "page",
        "snippet_type": "se",
        "context": (1, 1)
    },
    "mid_rus": {
        "prefix": "mid_rus",
        "align_by": "p",
        "snippet_type": "se",
        "context": (1, 1)
    },
    "birchbark": {
        "prefix": "birchbark",
        "align_by": "page",
        "snippet_type": "se",
        "context": (1, 1)
    },
    "orthlib": {
        "prefix": "orthlib",
        "align_by": FLAT_TYPE,
        "snippet_type": "se",
        "context": (1, 1)
    },
    "multilang": {
        "prefix": "multilang",
        "align_by": "para",
        "snippet_type": "para",
        "context": (1, 1)
    },
    "multiparc": {
        "prefix": "multiparc",
        "align_by": "para_item",
        "snippet_type": "para_item",
        "context": (1, 1)
    },
    "multiparc_rus": {
        "prefix": "multiparc_rus",
        "align_by": "para_item",
        "snippet_type": "para_item",
        "context": (1, 1)
    },
    "paper": {
        "prefix": "paper",
        "align_by": FLAT_TYPE,
        "snippet_type": "se",
        "context": (1, 1)
    },
    "main": {
        "prefix": "main",
        "align_by": FLAT_TYPE,
        "snippet_type": "se",
        "context": (1, 1)
    },
    "para": {
        "prefix": "para",
        "align_by": "para",
        "snippet_type": "para",
        "context": (1, 1)
    },
    "dialect": {
        "prefix": "dialect",
        "align_by": FLAT_TYPE,
        "snippet_type": "se",
        "context": (1, 1)
    },
    "poetic": {
        "prefix": "poetic",
        "align_by": "p",
        "snippet_type": "p",
        "context": (1, 1)
    },
    "accent": {
        "prefix": "accent",
        "align_by": "speach",
        "snippet_type": "speach",
        "context": (1, 1)
    },
    "accent_stihi": {
        "prefix": "accent_stihi",
        "align_by": "p",
        "snippet_type": "p",
        "context": (1, 1)
    },
    "accent_poetic": {
        "prefix": "accent_poetic",
        "align_by": "p",
        "snippet_type": "p",
        "context": (1, 1)
    },
    "spoken_spoken": {
        "prefix": "spoken_spoken",
        "align_by": "speach",
        "snippet_type": "speach",
        "context": (1, 1)
    },
    "spoken_accent": {
        "prefix": "spoken_accent",
        "align_by": "speach",
        "snippet_type": "speach",
        "context": (1, 1)
    },
    "murco": {
        "prefix": "murco",
        "align_by": SINGLE_FILE_TYPE,
        "snippet_type": "speach",
        "context": (1, 1)
    },
    "regional_rus": {
        "prefix": "regional_rus",
        "align_by": FLAT_TYPE,
        "snippet_type": "se",
        "context": (1, 1)
    },
    "school": {
        "prefix": "main",
        "align_by": FLAT_TYPE,
        "snippet_type": "se",
        "context": (1, 1)
    },
}


class OnlyMetaError(Exception):
    pass


class XMLHandler(xml.sax.handler.ContentHandler):
    word_type = "w"
    sentence_type = "se"
    paragraph_type = "p"
    meta_info_type = "meta"
    grammar_info_type = "ana"
    rhyme_zone_type = "rhyme-zone"
    line_break_type = "br"
    line_type = "line"

    def __init__(self, corpus_type=None, only_meta=False):
        if not corpus_type or corpus_type not in KNOWN_CORPUS_TYPES:
            raise Exception("Bad corpus type: %s" % corpus_type)
        self.last_speach_attrs = []
        self.only_meta = only_meta
        # Buffer for characters read from the document. Required because sax
        # parser may not always return the whole text in a single characters()
        # call.
        self.char_buffer = ""
        # The parsed document itself.
        self.doc = {"Attrs": [], "GroupAttrs": {}, "Parts": []}
        for key, value in KNOWN_CORPUS_TYPES[corpus_type].items():
            self.doc[key] = value
        # Processors for the startElement event.
        self.start_processors = {
            self.word_type: self.start_word,
            self.sentence_type: self.start_sentence,
            self.paragraph_type: self.start_paragraph,
            self.meta_info_type: self.start_meta,
            self.grammar_info_type: self.start_grammar_info,
            self.rhyme_zone_type: self.start_rhyme
        }
        # Processors for the endElement event.
        self.end_processors = {
            self.word_type: self.end_word,
            self.sentence_type: self.end_sentence,
            self.paragraph_type: self.end_paragraph,
            self.line_break_type: self.end_line_break,
            self.line_type: self.end_line
        }
        # Every document should have a hierarchy of items representing the
        # document's structure. Each node of this hierarchy keeps references
        # to the sentence-items that are "covered" by the node.
        self.items = [self.doc]
        # Field item_tags defines the types that go into hierarchy.
        self.item_tags = [
            SINGLE_FILE_TYPE, "speach", "para", "para_item", "se", "page", "p"
        ]
        # Some elements exist in many corpora, but each corpus may require some
        # special rendering of those elements. Such elements are prefixed.
        self.prefixed_types = {
            "se": "%s:%s" % (self.doc["prefix"], "se"),
        }
        # Re-define snippet type for prefixed_types
        snippet_type = self.doc["snippet_type"]
        if snippet_type in self.prefixed_types:
            self.doc["snippet_type"] = self.prefixed_types[snippet_type]
        self.other_tags = {}
        self.rhyme_flag = False
        # Stack currently processed tags.
        self.tags = []
        # Total sentences already processed.
        self.total_sents = 0
        # This mapping is used to generate unique ids for items of the same
        # type. So these ids look like "item_type:item_type_count".
        self.item_type_counts = {i_type: 0 for i_type in self.item_tags}
        # We add FLAT_TYPE align items each self.flat_type_size sentences.
        self.flat_type_size = 100
        # Current sentences that already went into the last align item.
        self.flat_count = 0
        if self.is_flat():
            self.item_tags.remove("p")
            self.item_type_counts[FLAT_TYPE] = 0
        if self.is_single_file():
            self.open_item(SINGLE_FILE_TYPE, [])
        self.ongoing_flat = False

    def characters(self, buf):
        """Overriden.
        """
        self.char_buffer += buf

    def startElement(self, name, attrs):
        """Overriden.
        """
        self.tags.append(name)
        if self.should_start_flat():
            self.ongoing_flat = True
            self.open_item(FLAT_TYPE, ())
        if name in self.item_tags:
            self.open_item(name, attrs.items())
        processor = self.start_processors.get(name)
        if processor:
            processor(attrs)

    def endElement(self, name):
        """Overriden.
        """
        del self.tags[-1]
        processor = self.end_processors.get(name)
        if processor:
            processor()
        if name in self.item_tags:
            self.close_item(name)
            if self.should_close_flat():
                self.ongoing_flat = False
                self.close_item(FLAT_TYPE)
                self.flat_count = 0

    def endDocument(self):
        """Overriden.

        If we've reached the document's end and there's still a `FLAT_TYPE`
        item, this item is closed. Here we suppose that a flat document is
        _really_ a flat document, with no item types other than "se".
        """
        if self.is_single_file():
            self.close_item(SINGLE_FILE_TYPE)

        if self.flat_item_tangling():
            self.close_item(FLAT_TYPE)
            self.flat_count = 0

    def start_word(self, attrs):
        self.get_last_sent()["Words"].append({"Anas": [], "flags": []})
        for _, val in attrs.items():
            self.get_last_word()["flags"].append(val)
        self.add_punct(self.get_last_word())

    def start_sentence(self, attrs):
        if self.only_meta:
            raise OnlyMetaError("O.K., only meta")
        self.total_sents += 1
        self.flat_count += 1
        self.get_last_part()["Sents"].append({
            "Words": [],
            "Attrs": self.last_speach_attrs
        })
        self.char_buffer = ""

    def start_meta(self, attrs):
        if attrs.get("name"):
            attr_name = self.normalize_attr_name(attrs["name"])
            attr_val = self.normalize_attr_val(attrs["content"])

            if attr_name in [u"gesture"]:
                self.doc["Attrs"].append((attr_name, attrs["content"]))
            else:
                self.doc["Attrs"].append((attr_name, attr_val))

    def start_paragraph(self, attrs):
        if not set(self.tags).intersection(self.item_tags):
            self.doc["Parts"].append({"Sents": []})

    def start_rhyme(self, attrs):
        self.rhyme_flag = True

    def start_grammar_info(self, attrs):
        self.get_last_word()["Anas"].append({})
        for key, val in attrs.items():
            if "/" in val:
                val = val.replace("/", ",")
            self.get_last_ana()[key] = val

    def end_word(self):
        self.get_last_word()["Text"] = self.char_buffer
        self.set_rhyme(self.get_last_word())
        self.char_buffer = ""

    def end_sentence(self):
        self.add_punct(self.get_last_sent())
        if not self.get_last_sent()["Words"]:
            self.get_last_part()["Sents"].pop()
            self.total_sents -= 1
        else:
            self.add_attrs(self.get_last_sent(), self.other_tags)

    def end_paragraph(self):
        self.rhyme_flag = False
        try:
            self.get_last_sent()["Punct"] += "\n\n"
        except Exception:
            self.char_buffer += "BB"

    def end_line_break(self):
        self.rhyme_flag = False
        try:
            self.get_last_sent()["Punct"] += "\n"
        except Exception:
            self.char_buffer += "B"  # WTF?

    def end_line(self):
        self.rhyme_flag = False

    def get_last_part(self):
        if not self.doc["Parts"]:
            self.doc["Parts"].append({"Sents": []})
        return self.doc["Parts"][-1]

    def open_item(self, name, attrs):
        if "items" not in self.get_last_item():
            self.get_last_item()["items"] = list()
        if "speach" in name:
            self.last_speach_attrs = [("sp_%s" % attr, value) for attr, value in attrs]
        item = {
            "type": self.prefixed_types.get(name, name),
            "_id": "%s:%s" % (name, self.item_type_counts[name]),
            "Attrs": attrs,
            "index": {
                "start": {"sent": self.total_sents, "word": -1},
                "end": {"sent": -1, "word": -1}
            }
        }
        self.get_last_item()["items"].append(item)
        self.items.append(item)
        self.item_type_counts[name] += 1

    def close_item(self, name):
        last_item_type = self.get_last_item().get("type")
        if self.prefixed_types.get(name, name) != last_item_type:
            raise Exception("closed item (%s) vs last item (%s) type mismatch" %
                            (self.prefixed_types.get(name, name), last_item_type))
        self.get_last_item()["index"]["end"]["sent"] = self.total_sents
        del self.items[-1]

    def get_last_sent(self):
        return self.get_last_part()["Sents"][-1]

    def get_last_word(self):
        return self.get_last_sent()["Words"][-1]

    def get_last_ana(self):
        return self.get_last_word()["Anas"][-1]

    def get_last_item(self):
        return self.items[-1]

    def add_punct(self, node):
        if self.char_buffer.endswith("\n"):
            self.char_buffer = self.char_buffer.rstrip()
            if not self.char_buffer:
                self.char_buffer = " "
        node["Punct"] = self.char_buffer.replace("\n", " ").replace("B", "\n")
        self.char_buffer = ""

    def set_rhyme(self, node):
        if self.rhyme_flag:
            node["Rhyme"] = 1

    def add_attrs(self, node, attrs_set):
        for elem in attrs_set:
            for key, val in attrs_set[elem]:
                node[elem + "_" + key] = val

    def should_start_flat(self):
        reopen_self = self.get_last_item().get("type") == FLAT_TYPE
        return self.is_flat() and not self.ongoing_flat

    def should_close_flat(self):
        return self.is_flat() and self.flat_count >= self.flat_type_size

    def flat_item_tangling(self):
        """Finds out whether the last opened item is `FLAT_TYPE`.
        """
        flat_inserted = self.get_last_item().get("type") == FLAT_TYPE
        return self.is_flat() and flat_inserted

    def is_flat(self):
        return self.doc["align_by"] == FLAT_TYPE

    def is_single_file(self):
        return self.doc["align_by"] == SINGLE_FILE_TYPE

    def normalize_attr_name(self, attr_name):
        """Replaces forbidden symbols in `attr_name`.

        Sometimes documents do not follow search engine's naming convention,
        and we have to make sure that our document won't be rejected by the
        cloud.
        """
        attr_name_clean = attr_name.replace("-", "_")
        return attr_name_clean

    @staticmethod
    def normalize_attr_val(attr_val):
        attr_val_clean = attr_val[:250]
        return attr_val_clean


def process(inpath, corpus_type=None, only_meta=False):
    handler = XMLHandler(corpus_type=corpus_type, only_meta=only_meta)
    try:
        xml.sax.parse(inpath, handler)
    except OnlyMetaError:
        pass
    return handler.doc


def dumps(inpath):
    doc = process(inpath)
    return json.dumps(doc, ensure_ascii=False, indent=0)


def main():
    inpath = sys.argv[1]
    result = dumps(inpath)
    with open(inpath + ".json", "w") as f:
        f.write(result.encode("utf-8"))


if __name__ == "__main__":
    main()
