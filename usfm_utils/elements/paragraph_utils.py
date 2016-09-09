import enum


class ParagraphLayout(object):
    def accept(self, visitor):
        raise NotImplementedError()


class LeftAligned(ParagraphLayout):
    def __init__(self, first_line_indent=None, left_margin_indent=0):
        if first_line_indent is None:
            first_line_indent = LeftAligned.FirstLineIndent.default
        self._first_line_indent = first_line_indent
        self._left_margin_indent = left_margin_indent

    @property
    def first_line_indent(self):
        return self._first_line_indent

    @property
    def left_margin_indent(self):
        return self._left_margin_indent

    def accept(self, visitor):
        visitor.left_aligned(self)

    class FirstLineIndent(enum.Enum):
        none = 0
        default = 1
        outdent = 2


class Centered(ParagraphLayout):
    def accept(self, visitor):
        visitor.centered(self)


class RightAligned(ParagraphLayout):
    def accept(self, visitor):
        visitor.right_aligned(self)



class ParagraphLayoutVisitor(object):
    def left_aligned(self, left_aligned):
        pass

    def centered(self, centered):
        pass

    def right_aligned(self, right_aligned):
        pass
