

class Position(object):
    def __init__(self, line, col):
        self._line = line
        self._col = col

    @property
    def line(self):
        return self._line

    @property
    def col(self):
        return self._col

    def __str__(self):
        return "line: {}, col: {}".format(self._line, self._col)


class Token(object):
    def __init__(self, position, value, number=None):
        self._position = position
        self._value = value
        self._number = number

    @property
    def position(self):
        return self._position

    @property
    def value(self):
        return self._value

    @property
    def number(self):
        return self._number

    class Builder(object):
        def __init__(self, value):
            self._position = None
            self._value = value
            self._number = None

        def set_number(self, number):
            """
            :param int number:
            :rtype: Builder
            """
            self._number = number
            return self

        def build(self, position):
            """
            :param Position position:
            :rtype: Token
            """
            return Token(position, self._value, number=self._number)
