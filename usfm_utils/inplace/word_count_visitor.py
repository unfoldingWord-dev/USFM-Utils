from __future__ import unicode_literals

from usfm_utils.elements import ElementVisitor

class WordCountVisitor(ElementVisitor):
    def __init__(self):
        self._word_count = 0

    @property
    def word_count(self):
        return self._word_count

    def text(self, text):
        """
        :param Text text:
        """
        self._word_count += len(text.content.split())
