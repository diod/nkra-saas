# -*- coding: utf-8 -*-

from render.writers import *


class WriterFactory(object):
    FACTORY_MAPPING = dict()

    @classmethod
    def get_writer(cls, item):
        builder = cls.FACTORY_MAPPING.get(item['type'])
        if builder:
            return builder
        else:
            return BaseItemWriter

    @classmethod
    def register_writer(cls, item_name, writer):
        cls.FACTORY_MAPPING[item_name] = writer
