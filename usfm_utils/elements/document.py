

class Document(object):

    def __init__(self, elements, heading=None, table_of_contents=None):
        self._elements = elements
        self._heading = heading
        self._table_of_contents = table_of_contents

    @property
    def elements(self):
        return self._elements

    @property
    def heading(self):
        return self._heading

    @property
    def table_of_contents(self):
        return self._table_of_contents


class TableOfContentsInfo(object):
    def __init__(self, long_description=None, short_description=None, abbreviation=None):
        self._long_description = long_description
        self._short_description = short_description
        self._abbreviation = abbreviation

    @property
    def long_description(self):
        return self._long_description

    @property
    def short_description(self):
        return self._short_description

    @property
    def abbreviation(self):
        return self._abbreviation

    class Builder(object):

        def __init__(self):
            self._long_description = None
            self._short_description = None
            self._abbreviation = None

        def set_long_description(self, long_description):
            self._long_description = long_description

        def set_short_description(self, short_description):
            self._short_description = short_description

        def set_abbreviation(self, abbreviation):
            self._abbreviation = abbreviation

        def build(self):
            return TableOfContentsInfo(
                long_description=self._long_description,
                short_description=self._short_description,
                abbreviation=self._abbreviation)
