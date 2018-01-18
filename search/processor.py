# -*- coding: utf-8 -*-

import re
import sys
import random
import logging
import operator
import traceback
from collections import OrderedDict

from common.hierarchy import restore_hierarchy, slice_by_type


class ResponseProcessor(object):
    """Provides methods preparing search response for rendering.

    Response is organized as (possibly) several hierarchies with content
    restored from direct index.
    """

    def __init__(self, snippets=5):
        self.num_added_ses = 0
        self.num_snippets = 0
        self.num_snippets_per_doc = snippets

    def process(self, params, response, extend_id=None, sort_by=None, subcorpus=None):
        """Process a SearchResponse object with "raw" response data.

        Args:
            response: A SearchResponse instance.
            extend_id: String identifier of the snippet that needs to be
                extended (not used in normal search). Is has the format
                `<align_item_id>:_<snippet_id>`.

        Returns:
            out: A list of dicts representing matching document hierarchies.
        """
        if sort_by in ["cont1", "cont2", "cont-1", "cont-2"]:
            return self._return_context(params, response)
        out = []
        min_doc = params.page * params.docs_per_page
        max_doc = min_doc + params.docs_per_page - 1
        for i, group in enumerate(response.get_groups()):
            if "multiparc" in subcorpus:
                self._squash_multipart_group(group)
            self._process_group(i, group, min_doc, max_doc, extend_id, out, subcorpus)
        if params.sort_by in ["random"]:
            random.seed(params.seed)
            random.shuffle(out)
        return out

    @staticmethod
    def _squash_multipart_group(group):
        group.obj['documents'] = group.obj['documents'][:1]

    def _process_group(self, i, group, min_doc, max_doc, extend_id, out, subcorpus):
        if not (min_doc <= i <= max_doc):
            return
        # Each group is the initial document (as it came to the indexing
        # engine), and each doc in a group is an initial document's part.
        # Retrieve results from each document part.
        results = list()
        for doc in group.get_documents():
            hits = doc.get_hits()
            doc_url = doc.get_url()
            hchy = doc.get_direct_index()["Hierarchy"]
            index = doc.get_direct_index()["Sents"]
            self._set_source_for_doc(index, doc_url)
            try:
                self._get_result(
                    results, index, hchy, hits, subcorpus, extend_id=extend_id)
            except Exception as ex:
                logging.info("! doc %s failed: %s", doc_url, ex)
                continue
        # Restore the initial document's hierarchy (now with hits only).
        restored_doc = restore_hierarchy(results)
        # Leave not more than self.num_snippets_per_doc snippets.
        reduced_doc = self._strip_snippets(restored_doc)
        reduced_doc["total_hits"] = str(group.get_hits_count())
        additional_info = {"document_url": doc_url}
        self._augment_with_info(reduced_doc, additional_info)
        out.append(reduced_doc)

    def _return_context(self, params, response):
        result = []
        sorted_entries = []
        for group in response.get_groups():
            for doc in group.get_documents():
                try:
                    hits = doc.get_hits()
                    attrs = doc.get_direct_index()[
                        "Hierarchy"]["path"][0]["Attrs"]
                    index = doc.get_direct_index()["Sents"]
                    doc_url = doc.get_url()
                    self.mark_hits(index, hits)
                    self._set_source_for_doc(index, doc_url)
                    for hit_sentence, hit_entries in hits.items():
                        words = index[hit_sentence]["Words"]
                        punct = index[hit_sentence]["Punct"]
                        any_hit = hit_entries.pop()
                        sorting_key = self._get_sorting_key(
                            words, punct, any_hit, params.sort_by)
                        sorted_entries.append((sorting_key.lower(), words,
                                               punct, doc_url, len(hits),
                                               attrs))
                except Exception:
                    pass
        sorted_entries.sort(key=operator.itemgetter(0))
        for _, sent, punct, doc_url, total_hits, attrs in sorted_entries:
            entry = {
                "type": "context:top",
                "Attrs": attrs,
                "items": [{
                    "Attrs": attrs,
                    "type": "context:entry",
                    "content": [{"Words": sent, "Punct": punct}],
                }]
            }
            additional_info = {
                "document_url": doc_url,
                "total_hits": "%s" % total_hits
            }
            self._augment_with_info(entry, additional_info)
            result.append(entry)
        return result

    @staticmethod
    def _get_sorting_key(words, end_punct, hit_idx, context="cont1"):
        """Build context key for sorting the `words`.
        """
        out = ""
        start, end = None, None
        # Sort by right context, icluding current word.
        if context == "cont1":
            start, end = hit_idx, len(words)
        # Sort by right context, ignoring current word.
        elif context == "cont2":
            start, end = hit_idx + 1, len(words)
        # Sort by left context, including current word.
        elif context == "cont-1":
            start, end = 0, hit_idx + 1
        # Sort by left context, ignoring current word.
        else:
            start, end = 0, hit_idx - 1
        # We need to include all the punctuation available.
        for word_idx in xrange(start, end):
            word = words[word_idx]
            if word.get("Punct"):
                out += word["Punct"].replace(" ", "")
            out += word["Text"]
        # Newlines count as symbols and should be removed.
        if context in ["cont1", "cont2"]:
            out += end_punct
        out = re.sub("\n", "", out)
        if context in ["cont-1", "cont-2"]:
            out = "".join(reversed(out))
        return out

    @staticmethod
    def _set_source_for_doc(direct_index, doc_url):
        """Saves info about the word's position in `direct_index`.

        Requesting info for separate words requires some info about the word's
        position in a document (along with the document's url). This info is
        stored as the "Source" field for each word.

        Args:
            direct_index: A list of dicts (sentences) storing lists of words
                (also dicts) by the `"Words"` key.
            doc_url: A string (with no specific structure).
        """
        for sent_idx in range(len(direct_index)):
            sent = direct_index[sent_idx]
            for word_idx in range(len(sent["Words"])):
                word = sent["Words"][word_idx]
                word["Source"] = "%s\t%s\t%s" % (doc_url, sent_idx, word_idx)

    def _get_result(self, out, direct_index, item_top, hits, subcorpus, extend_id=None):
        """
        Args:
            out: A list.
            direct_index: A list of dicts (sentences) storing lists of words
                (also dicts) by the `"Words"` key.
            item: A dictionary which represents a certain document as a
                hierarchy of items. It has the following keys:
                    * "type" (string type of the item);
                    * "_id" (string of the form <type>:<counter_inside_doc>);
                    * "index" (references to start/end sentence ids);
                    * "items" (a list of items of the same structure).
            hits: A list of (<sentence_id>, <word_id>) tuples.
            extend_id: String identifier of the snippet that needs to be
                extended (not used in normal search). Is has the format
                `<align_item_id>:_<snippet_id>`.
        """
        # `prefix` will be used to prefix the "type" field of snippets that are
        # generated in `self.build_snippets`.
        prefix = item_top["prefix"]
        context = None
        if "context" not in item_top:
            context = (1, 1)
        else:
            context = item_top["context"]
        # If we have the "extend this snippet" type of query, we need to filter
        # doc parts (i.e., item_tops, i.e., align_items).
        if extend_id:
            align_id, snippet_id = self._resolve_extended(extend_id)
            if item_top["_id"].strip() != align_id.strip():
                return
            # Extend both left and right contexts by 5 items.
            context[0] += 5
            context[1] += 5
            extend_id = snippet_id
        # Duct tape for single-file corpora.
        if subcorpus in ["murco"]:
            context[0] += 5
            context[1] += 5
        snip_type = None
        if "snippet_type" not in item_top:
            snip_type = "para_item"
        else:
            snip_type = item_top["snippet_type"]
        top_path = self._get_top_path(item_top)
        # We know for sure that item top contains at least one hit (because
        # it was returned by the search server). So mark the hits.
        self.mark_hits(direct_index, hits)
        # We know that for this document minimal hierarchy render unit must be
        # snippet_item type. Get a slice of top-level (most shallow) items of
        # this type.
        snip_items = slice_by_type(item_top, snip_type)
        # We allow left and right context. This means that for any snippet_item
        # with a hit in it we want to save some items without hits to the left
        # and some items without hits to the right. We must not try to take
        # negative/out of range indices, hence min_idx and max_idx.
        min_idx, max_idx = 0, len(snip_items)
        # hit_indices will store the indices of items that contain hits.
        hit_indices = list()
        for idx in xrange(len(snip_items)):
            item = snip_items[idx]
            if self._item_contains_hit(item, hits):
                hit_indices.append(idx)
            # If a document matches by some attribute, but there was no normal query,
            # this document will be returned by the search engine, but with hits equalling
            # {-1: set([-1])}. In this case we take all snippets into the result.
            if -1 in hits:
                hit_indices.append(idx)
        # result_hits will store the indices of items that contain hits PLUS
        # context items indices.
        result_indices = list()
        for idx in hit_indices:
            left_boundary = max(idx - context[0], min_idx)
            right_boundary = min(idx + context[1] + 1, max_idx)
            result_indices += range(left_boundary, right_boundary)
        # Remove duplicate indices (context intersections are possible because
        # hits might be very close to each other).
        result_indices = list(OrderedDict.fromkeys(result_indices))
        # Restore the initial item_top, but now only containing hit/context
        # items.
        snippets = self._build_snippets(
            result_indices, snip_items, prefix, item_top["_id"], extend_id,
        )

        # snippets = [x for x in snippets if not item_is_too_big(x)]
        item = restore_hierarchy(snippets)
        # item = restore_hierarchy([snippet_items[x] for x in result_indices])
        # Restore path to the global document hierarchy root.
        item["path"] = top_path
        # Retrieve contents from the direct index (document part).
        self._finalize_item(direct_index, item)
        out.append(item)

    def _get_top_path(self, item_top):
        # Save item_top's path to root and save the full snippet type.
        top_path = item_top.pop("path")
        top_path[0]["prefix"] = item_top["prefix"]
        return top_path

    def _build_snippets(self,
                        result_indices,
                        snippet_items,
                        prefix,
                        align_id,
                        extend_id=None):
        idx_snippets, idx_curr_snippet, final_snippets = [], [], []
        # result_indices keeps items with hits conbined with their context
        for idx in result_indices:
            # Just to initialize the list
            if not idx_curr_snippet:
                idx_curr_snippet.append(idx)
            else:
                # We start forming actual snippets by extracting strictly
                # adjacent items (their indices must not differ by more than
                # one)
                if idx - idx_curr_snippet[-1] > 1:
                    idx_snippets.append(idx_curr_snippet)
                    idx_curr_snippet = [idx]
                else:
                    idx_curr_snippet.append(idx)
        idx_snippets.append(idx_curr_snippet)
        # Now we merge the snippets.
        # A few words about the "extend_id" key. A user might ask us to extend
        # a certain snippet. (E.g.: she might want to see more context to the
        # left and to the right.) In order to allow the user to do so we need
        # to encode two things in our main response:
        #   1. The _id of the align item containing each snippet;
        #   2. The id of the snippet RELATIVE TO THE CONTAINING ALIGN ITEM.
        # The field self.num_snippets counts all snippets from all doc parts
        # returned by the search server. This is not what we need here; we need
        # the number of a snippet inside this current doc part, thus we need
        # the idx_snippet_id below.
        for idx_snippet_id in xrange(len(idx_snippets)):
            idx_snippet = idx_snippets[idx_snippet_id]
            # TODO: test that these two lines work properly. Note that we need
            # to test a corpus which has different `align_by` and
            # `snippet_type` types.
            if False and extend_id and idx_snippet != extend_id:
                continue
            snippet = {"_extend_at": "%s_%s" % (align_id, idx_snippet_id), "_id": "snippet:%s" % self.num_snippets,
                       "type": "%s:snippet" % prefix, "index": {}, "items": [snippet_items[x] for x in idx_snippet]}
            # All items here are restricted to a single align item, so they
            # all have the same path to root. We give this path to the snippet
            # item and remove it from the children.
            snippet["path"] = snippet["items"][0]["path"]
            snippet["hits"] = snippet["items"][0].get("hits")
            for item in snippet["items"]:
                item.pop("path")
            # Set up the indicesю
            start = snippet["items"][0]["index"]["start"]
            end = snippet["items"][-1]["index"]["end"]
            snippet["index"]["start"] = start
            snippet["index"]["end"] = end
            final_snippets.append(snippet)
            self.num_snippets += 1
        return final_snippets

    def _item_contains_hit(self, item_top, hits):
        """Tells whether a hierarchy item_top contains any of the `hits`.

        Args:
            item_top: A dictionary which represents a certain document as a
                hierarchy of item_tops. It has the following keys:
                    * "type" (string type of the item_top);
                    * "_id" (string of the form <type>:<counter_inside_doc>);
                    * "index" (references to start/end sentence ids);
                    * "item_tops" (a list of item_tops of the same structure).
            hits: A list of (<sentence_id>, <word_id>) tuples.
        Returns:
            contains_hit: Boolean.
        """
        fst_sent = item_top["index"]["start"]["sent"]
        lst_sent = item_top["index"]["end"]["sent"]
        contains_hit = False
        for sent_num in hits:
            if fst_sent <= sent_num <= lst_sent:
                contains_hit = True
                break
        if "items" not in item_top and contains_hit:
            item_top["hits"] = sorted([sent_id for sent_id in hits])
        for item in item_top.get("items", []):
            self._item_contains_hit(item, hits)
        return contains_hit

    def mark_hits(self, direct_index, hits):
        """Adds a boolean "is_hit" key to the words in direct index.

        Args:
            direct_index: A list of dicts (sentences) storing lists of words
                (also dicts) by the `"Words"` key.
            hits: A list of (<sentence_id>, <word_id>) tuples.
        """
        for sent_num, words in hits.items():
            sent = direct_index[sent_num]
            for word_idx in words:
                sent["Words"][word_idx]["is_hit"] = True

    def _finalize_item(self, direct_index, item_top):
        """Restores sentences from `direct_index` to `item_top`.

        Saves retrieved sentences in respective items by the "content" key.

        Args:
            direct_index: A list of dicts (sentences) storing lists of words
                (also dicts) by the `"Words"` key.
            item_top: A dictionary which represents a certain document as a
                hierarchy of items. It has the following keys:
                    * "type" (string type of the item);
                    * "_id" (string of the form <type>:<counter_inside_doc>);
                    * "index" (references to start/end sentence ids);
                    * "items" (a list of items of the same structure).
        """
        if "items" not in item_top:
            self._resolve_index(item_top, direct_index)
        else:
            # WARNING: the following is some fucked up duct tape for cases
            # when an item contains too many sentences. This is disgusting.
            items = item_top["items"]
            if not items[0].get("items") and len(items) > 15:
                item_top["items"] = [x for x in items if x.get("hits")]
            for item in item_top["items"]:
                self._finalize_item(direct_index, item)

    def _resolve_index(self, item_top, direct_index):
        """Retireves sentences from `direct_index`.

        Args:
            direct_index: A list of dicts (sentences) storing lists of words
                (also dicts) by the `"Words"` key.
            indices: Dict with references to start/end sentence ids.

        Returns:
            resolved_index: List of sentences (as in `direct_index`).
        """
        indices = item_top["index"]
        start_sent = indices["start"]["sent"]
        end_sent = indices["end"]["sent"]
        resolved_index = direct_index[start_sent:end_sent]
        item_top["content"] = resolved_index

    def _augment_with_info(self, item_top, info):
        """Percolates `info` recursively to `item_top`.

        Args:
            item_top: A dictionary which represents a certain document as a
                hierarchy of items. It has the following keys:
                    * "type" (string type of the item);
                    * "_id" (string of the form <type>:<counter_inside_doc>);
                    * "index" (references to start/end sentence ids);
                    * "items" (a list of items of the same structure).
            info: A flat dict with arbitrary keys.

        Raises:
            Exception("Tried to add an existent key, aborting") if any of the
            keys in `info` were already present in an item. We don't like
            overriding stuff, I guess.
        """
        for k, v in info.items():
            if k in item_top:
                raise Exception("Tried to add an existent key, aborting")
            item_top[k] = v
        if "items" in item_top:
            for item in item_top["items"]:
                self._augment_with_info(item, info)

    def _strip_snippets(self, restored_doc):
        """Leaves only `self.num_snippets_per_doc` left.

        Args:
            item_top: A dictionary which represents a certain document as a
                hierarchy of items. It has the following keys:
                    * "type" (string type of the item);
                    * "_id" (string of the form <type>:<counter_inside_doc>);
                    * "index" (references to start/end sentence ids);
                    * "items" (a list of items of the same structure).
        Returns:
            A dictionary which represents a certain document as a
            hierarchy of items. It has the following keys:
                * "type" (string type of the item);
                * "_id" (string of the form <type>:<counter_inside_doc>);
                * "index" (references to start/end sentence ids);
                * "items" (a list of items of the same structure).
        """
        # This is highly inefficient, but placing max_snippets logic
        # in self.split_snippets() looks very ugly.
        snip_type = "%s:snippet" % restored_doc["prefix"]
        all_snippets = slice_by_type(restored_doc, snip_type)
        reduced_snippets = all_snippets[:self.num_snippets_per_doc]
        return restore_hierarchy(reduced_snippets)

    def _resolve_extended(self, extend_id):
        """Parses the `extend_id` command.

        User can ask us to extend a certain snippet. The snippet is encoded by
        two identifiers: _id of the align_item containing it and _id of the
        snippet relative* to that align_item. Here we "parse" those two
        identifiers.

        Args:
            extend_id: String identifier of the snippet that needs to be
                extended (not used in normal search). Is has the format
                `<align_item_id>:_<snippet_id>`.
        Returns:
            align_id: A string (<align_by_type>:<counter_inside_doc>) OR None.
            snippet_id: A string id of the extended snippet OR None.
        """
        try:
            extended_qry_split = extend_id.split("_")
            align_id = extended_qry_split[0]
            snippet_id = int(extended_qry_split[1])
            return align_id, snippet_id
        except Exception as ex:
            logging.info(
                "Failed to extend snippet context, query '%s'; %s",
                extend_id, ex
            )
            return None, None
