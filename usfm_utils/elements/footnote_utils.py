

class FootnoteLabel(object):
    def accept(self, visitor):
        raise NotImplementedError()


class AutomaticFootnoteLabel(FootnoteLabel):
    def accept(self, visitor):
        visitor.automatic(self)


class NoFootnoteLabel(FootnoteLabel):
    def accept(self, visitor):
        visitor.no_label(self)


class CustomFootnoteLabel(FootnoteLabel):
    def __init__(self, content):
        self._content = content

    @property
    def content(self):
        return self._content

    def accept(self, visitor):
        visitor.custom(self)


class FootnoteLabelVisitor(object):
    def automatic(self, automatic):
        raise NotImplementedError()

    def no_label(self, no_label):
        raise NotImplementedError()

    def custom(self, custom):
        raise NotImplementedError()
