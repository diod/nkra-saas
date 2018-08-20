# -*- coding: utf-8 -*-

SAAS_HOST = "https://saas-searchproxy-outgone.yandex.net/yandsearch?service=" \
            "ruscorpora&format=json&timeout=2147483647&"

# A set of default values used by response.py.SearchResponse.__init__()

EXTENDED_QUERY = '(%s)&s_url:"%s"'

BASE_PARAMS = lambda query, kps: (
    ('text', query),
    ('kps', str(kps)),
    ('relev', 'attr_limit=1000000'),
    ('fsgta', 's_url'),
)

GRAPHIC_BASE_PARAMS = lambda query, kps: (
    ('text', query),
    ('kps', str(kps)),
)

NGRAMS_BASE_PARAMS = lambda query, kps: (
    ('text', query),
    ('kps', str(kps)),
)

# Inject sentence number into query (for info only)
PROPS_PARAMS = {
    'serp': lambda sentence_num: (
        ('gta', 'p_serp_part'),
        ('gta', 's_header'),
        ('gta', 'p_url'),
    ),
    'info': lambda sentence_num: (
        ('gta', 'p_info_part_%s' % sentence_num),
    )
}

HITS_COUNT_PARAMS = (
    ('rty_hits_detail', 'da'),
    ('qi', 'rty_hits_count'),
    ('qi', 'rty_hits_count_full'),
)

HITS_INFO_PARAMS = (
    ('fsgta', '__HitsInfo'),
)

SORT_PARAMS = lambda sort, asc: (
    ('how', sort),
    ('asc', '1' if asc else '0'),
)

GRAPHIC_SORT_PARAMS = lambda sort: (
    ('how', sort),
)

GRP_PARAMS = lambda grp_attr, max_docs, docs_per_grp: (
    ('g', '1.%s.%d.%d.....s_subindex.1' % (grp_attr, max_docs, docs_per_grp)),
)

GRAPHIC_GRP_PARAMS = lambda grp_attr, max_docs, docs_per_grp: (
    ('g', '1.%s.%d.%d......1' % (grp_attr, max_docs, docs_per_grp)),
)

DEFAULT_GRP_PARAMS = lambda max_docs: (
    ('numdoc', str(max_docs)),
)
