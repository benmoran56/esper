# -*- coding: utf-8 -*-

class Processor(object):
    def __init__(self):
        self.world = None

    def process(self, *args):
        raise NotImplementedError
