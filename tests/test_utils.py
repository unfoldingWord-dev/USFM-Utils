"""
Various utilities for tests
"""
from __future__ import unicode_literals

import random

# pylint: disable=redefined-builtin
from builtins import chr


def word(allow_empty=True):
    """
    :return: a randomly generated (non-ASCII) word
    :rtype: unicode
    """
    length = random.randint(0 if allow_empty else 1, 10)
    return "".join(chr(random.randint(256, 512)) for _ in range(length))

def words(n):
    """
    :return: a randomly generated sequence of (non-ASCII, non-empty) words
    :rtype: unicode
    """
    return " ".join(word(allow_empty=False) for _ in range(n))
