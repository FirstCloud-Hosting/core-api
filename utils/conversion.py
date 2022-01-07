#!flask/bin/python
# -*- coding: utf-8 -*-

import math


def size_from_bytes(size_bytes):
    if size_bytes == 0:
        return "0KB"
    size_name = ("KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])
