
class UsfmInputError(Exception):
    """
    Raised when invalid USFM input is encountered.
    """
    def __init__(self, message, position):
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
        return "{m} at {p}".format(m=self._message, p=self._position)
