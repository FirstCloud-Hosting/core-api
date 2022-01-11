#!flask/bin/python
# -*- coding: utf8 -*-
"""Memcache module
"""

import memcache


class Cache():

    """Cache module used to reduce loading times  

    Args:
        enable (bool, optional): Enable system cache
        host (str, optional): IP or DNS name of host system cache
        port (int, optional): Port system cache 
    """
    
    def __init__(self, enable=False, host=None, port=None):
        self.enable = enable
        if enable is True:
            self.cache = memcache.Client([(host, int(port))])

    def set(self, key, value, time=0):
        """Set value in system cache
        
        Args:
            key (str): Key of data
            value (str): Value of data
            time (int, optional): Time cache duration
        """
        if self.enable is True:
            if time == 0:
                self.cache.set(key, value)
            else:
                self.cache.set(key, value, time=time)

    def get(self, key):
        """Get value in system cache
        
        Args:
            key (str): Key of data
        
        Returns:
            str: Value in system cache
        """
        if self.enable is True:
            return self.cache.get(key)
        return None

    def delete(self, key):
        """Delete value in system cache
        
        Args:
            key (str): Key of data
        """
        if self.enable is True:
            self.cache.delete(key)
