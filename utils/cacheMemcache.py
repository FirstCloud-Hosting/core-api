#!flask/bin/python
# -*- coding: utf8 -*-

import memcache


class Cache():
    def __init__(self, enable=False, host=None, port=None):
        self.enable = enable
        if enable is True:
            self.cache = memcache.Client([(host, int(port))])

    def set(self, key, value, time=0):
        if self.enable is True:
            if time == 0:
                self.cache.set(key, value)
            else:
                self.cache.set(key, value, time=time)

    def get(self, key):
        if self.enable is True:
            return self.cache.get(key)
        return None

    def delete(self, key):
        if self.enable is True:
            self.cache.delete(key)
