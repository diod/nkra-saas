# -*- coding: utf-8 -*-

SAMPLE_HIERARCHY = {
    'items': [
        {
            'type': 'media',
            'media': 'id123456789',
            'items': [
                {
                    'type': 'para',
                    'items': [
                        {
                            'type': 'para_block',
                            'lang': 'rus',
                            'items': [
                                {
                                    'type': 'speech',
                                    'lang': 'rus',
                                    'person': 'Мистер А',
                                    'items': [
                                        {
                                            'type': 'text',
                                            'index': ['Привет, мистер А!']
                                        }
                                    ]
                                },
                                {
                                    'type': 'speech',
                                    'lang': 'rus',
                                    'person': 'Мистер Б',
                                    'items': [
                                        {
                                            'type': 'text',
                                            'index': ['Привет, мистер Б!']
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            'type': 'para_block',
                            'lang': 'eng',
                            'items': [
                                {
                                    'type': 'speech',
                                    'lang': 'eng',
                                    'person': 'Mister A',
                                    'items': [
                                        {
                                            'type': 'text',
                                            'index': ['Hello, Mister B!']
                                        }
                                    ]
                                },
                                {
                                    'type': 'speech',
                                    'lang': 'eng',
                                    'person': 'Mister B',
                                    'items': [
                                        {
                                            'type': 'text',
                                            'index': ['Hello, Mister B!']
                                        }
                                    ]
                                }
                            ]
                        },
                    ]
                }
            ]
        }
    ]
}

