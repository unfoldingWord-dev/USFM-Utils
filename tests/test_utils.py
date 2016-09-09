"""
Various utilities for tests
"""
import random

from builtins import chr


def word():
    """
    :return: a randomly generated (non-ASCII) word
    :rtype: unicode
    """
    length = random.randint(0, 10)
    return u"".join(chr(random.randint(256, 512)) for _ in range(length))
