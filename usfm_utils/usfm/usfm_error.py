from __future__ import unicode_literals

class UsfmInputError(Exception):
    """
    Raised when invalid USFM input is encountered.
    """
    def __init__(self, message, position):
        Exception.__init__(self)
        self._message = message
        self._position = position

    @property
    def message(self):
        """
        :return: the error's message
        :rtype: str
        """
        return self._message

    @property
    def position(self):
        """
        :return: the position where the error occurred
        :rtype: Position
        """
        return self._position

    def __str__(self):
        msg = "{m} at {p}".format(m=self._message, p=self._position)
        if isinstance(msg, str):
            # python 3
            return msg
        # python 2, we need to encode into a string (i.e. byte string),
        # otherwise the caller might get a UnicodeEncodeError
        return msg.encode('utf-8')
