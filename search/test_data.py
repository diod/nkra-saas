# -*- coding: utf-8 -*-

##############################################################################
#
# This file contains data used by all test_* files in the module.
#
##############################################################################

DATA_SEARCH_ENGINE = {
    'test_serve_lexform': {
        'expected_checksum': '06dd57eb43a633d6de207c2bdf361d3b9cb466c'
                             'fa9c0554ae545256c2646d3e5',
        'params': {
            'sort': ['gr_tagging'],
            'lang': ['ru'],
            'text': ['lexform'],
            'req': ['\xe4\xee\xec\xfa'], 'mode': ['old_rus'],
            'env': ['saas-test'], 'nodia': ['1']
        }
    },
    'test_serve_lexgramm': {
        'expected_checksum': '945cc3d90a08aaad57a31e286b3f77881f45e61e'
                             '1939118fc571da66cea767e3',
        'params': {
            'sort': ['gr_tagging'],
            'lang': ['ru'],
            'parent1': ['0'],
            'max2': ['1'],
            'text': ['lexgramm'],
            'sem-mod2': ['sem', 'sem2'],
            'gramm1': ['f'],
            'sem-mod1': ['sem', 'sem2'],
            'level1': ['0'],
            'level2': ['0'],
            'mode': ['old_rus'],
            'env': ['saas-test'],
            'min2': ['1'],
            'nodia': ['1'],
            'parent2': ['0']
        }
    },
    'test_serve_word_info': {
        'expected_checksum': 'dff9e27aa0b96d13cdfa074f589c5db6d849db24'
                             'b63e728b895e4b0940eb94f4',
        'params': {
            'sort': ['gr_tagging'],
            'lang': ['ru'],
            'language': ['ru'],
            'text': ['word-info'],
            'req': ['\xe4\xee\xec\xfa'],
            'source': [
                'Li4vLi4vcmVzL29sZF9ydXMvZ2FsaWNpYW4vZ2Fsa'
                'WNpYW4ueG1sIzAwMTAJMTU2CTU='
            ],
            'mode': ['old_rus'],
            'env': ['saas-test'],
            'nodia': ['1'],
            'requestid': ['1455758811703']
        },
    }
}

DATA_SEARCH_PARAMS = {
    'test_lexform_query': {
        'expected': {
            'raw': {
                'sort': ['gr_tagging'], 'lang': ['ru'],
                'text': ['lexform'], 'req': ['\xe4\xee\xec\xfa'],
                'mode': ['old_rus'], 'env': ['saas-test'], 'nodia': ['1']
            },
            'subcorpus': None, 'diacritic': 0,
            'text': 'lexform', 'req': '\xe4\xee\xec\xfa',
            'join_grouped_docs': True, 'sort_by': 'gr_tagging',
            'source': None, 'expand_snippets': False,
            'group_by': 's_url', 'radius': 1,
            'mode': None, 'docs_per_page': 10,
            'doc_id': None, 'page': 0,
            'snippets_per_doc': 10
        },
        'input': {
            'sort': ['gr_tagging'],
            'lang': ['ru'],
            'text': ['lexform'],
            'req': ['\xe4\xee\xec\xfa'], 'mode': ['old_rus'],
            'env': ['saas-test'], 'nodia': ['1']
        }
    },
    'test_lexgram_query': {
        'expected': {
            'raw': {
                'sort': ['gr_tagging'], 'env': ['saas-test'],
                'text': ['lexgramm'], 'gramm1': ['f'],
                'level1': ['0'], 'level2': ['0'], 'min2': ['1'],
                'lang': ['ru'], 'max2': ['1'], 'sem-mod2': ['sem', 'sem2'],
                'sem-mod1': ['sem', 'sem2'], 'mode': ['old_rus'],
                'parent1': ['0'], 'nodia': ['1'], 'parent2': ['0']
            },
            'subcorpus': None, 'diacritic': 0,
            'text': 'lexgramm', 'req': '',
            'join_grouped_docs': True, 'sort_by': 'gr_tagging',
            'source': None, 'expand_snippets': False,
            'group_by': 's_url', 'radius': 1, 'mode': None,
            'docs_per_page': 10, 'doc_id': None,
            'page': 0, 'snippets_per_doc': 10
        },
        'input': {
            'sort': ['gr_tagging'],
            'lang': ['ru'],
            'parent1': ['0'],
            'max2': ['1'],
            'text': ['lexgramm'],
            'sem-mod2': ['sem', 'sem2'],
            'gramm1': ['f'],
            'sem-mod1': ['sem', 'sem2'],
            'level1': ['0'],
            'level2': ['0'],
            'mode': ['old_rus'],
            'env': ['saas-test'],
            'min2': ['1'],
            'nodia': ['1'],
            'parent2': ['0']
        }
    },
}