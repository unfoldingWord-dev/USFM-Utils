import itertools

import enum

from usfm_utils.elements.abstract_elements import Element, KindedElement, MaybeIntroductoryElement,\
    ParentElement, WeightedElement
from usfm_utils.elements.footnote_utils import FootnoteLabel
from usfm_utils.elements.paragraph_utils import LeftAligned


class Text(Element):
    def __init__(self, content):
        """
        :param str|unicode content:
        """
        self._content = content

    @property
    def content(self):
        """
        :rtype: str
        """
        return self._content

    def accept(self, visitor):
        return visitor.text(self)


class FormattedText(KindedElement, ParentElement):
    def __init__(self, kind, children):
        KindedElement.__init__(self, kind)
        ParentElement.__init__(self, children)

    def accept(self, visitor):
        visitor.before_formatted_text(self)
        self.visit_children(visitor)
        visitor.after_formatted_text(self)

    @enum.unique
    class Kind(enum.Enum):
        c = itertools.count()  # for generating unique numbers

        # text formatting
        bold = next(c)
        emphasis = next(c)
        italics = next(c)
        normal = next(c)
        lower_case = next(c)

        # special text
        translator_addition = next(c)
        book_title = next(c)
        deuterocanonical = next(c)
        keyword = next(c)
        liturgical = next(c)
        name_of_god = next(c)
        ordinal = next(c)  # e.g. 1st === 1 ordinal(st)
        proper_name = next(c)
        quotation = next(c)
        signature = next(c)
        secondary_language = next(c)
        transliterated = next(c)
        words_of_jesus = next(c)

        # numbers
        verse_no = next(c)
        alternate_verse_no = next(c)

        # footnotes
        footnote_alternate_quotation = next(c)
        footnote_keyword = next(c)
        footnote_label = next(c)
        footnote_new_testament = next(c)
        footnote_old_testament = next(c)
        footnote_origin = next(c)
        footnote_quotation = next(c)
        footnote_reference = next(c)
        footnote_reference_mark = next(c)
        footnote_target = next(c)
        footnote_verse = next(c)

        # poetry
        poetic_acrositc = next(c)

        # no_formatting
        no_effect = next(c)  # useful in some lexing/parsing situations

        def construct(self, children):
            return FormattedText(self, children)


class Heading(KindedElement, MaybeIntroductoryElement, ParentElement, WeightedElement):
    def __init__(self, kind, children, weight=1, introductory=False):
        KindedElement.__init__(self, kind)
        ParentElement.__init__(self, children)
        WeightedElement.__init__(self, weight)
        MaybeIntroductoryElement.__init__(self, introductory)

    def accept(self, visitor):
        visitor.before_heading(self)
        self.visit_children(visitor)
        visitor.after_heading(self)

    @enum.unique
    class Kind(enum.Enum):
        major_title = 0
        major_title_end = 1
        major_section = 2
        section = 3
        outline_title = 4

    class Builder(object):
        def __init__(self, kind, weight=1, introductory=False):
            self._kind = kind
            self._weight = weight
            self._introductory = introductory

        def __call__(self, children, weight=None):
            return self.build(children, weight=weight)

        def build(self, children, weight=None):
            weight = self._weight if weight is None else weight
            return Heading(self._kind, children, weight=weight,
                           introductory=self._introductory)


class OtherText(KindedElement, ParentElement):
    def __init__(self, kind, children):
        KindedElement.__init__(self, kind)
        ParentElement.__init__(self, children)

    def accept(self, visitor):
        visitor.before_other(self)
        self.visit_children(visitor)
        visitor.after_other(self)

    @enum.unique
    class Kind(enum.Enum):
        selah = 0
        acrostic_heading = 1
        explanatory = 2
        speaker_id = 3
        descriptive_title = 4

        def construct(self, children):
            return OtherText(self, children)


class Paragraph(MaybeIntroductoryElement, ParentElement):

    def __init__(self, children, layout=None, embedded=False,
                 introductory=False, poetic=False, continuation=False):
        """
        :param iterable<SmallElement> children:
        :param ParagraphLayout layout:
        :param bool embedded:
        :param bool introductory:
        :param bool poetic:
        :param bool continuation:
        """
        ParentElement.__init__(self, children)
        self._children = tuple(children)
        if layout is None:
            self._layout = LeftAligned(LeftAligned.FirstLineIndent.default)
        else:
            self._layout = layout
        self._embedded = embedded
        MaybeIntroductoryElement.__init__(self, introductory)
        self._poetic = poetic
        self._continuation = continuation

    @property
    def layout(self):
        """
        :rtype: ParagraphLayout
        """
        return self._layout

    @property
    def embedded(self):
        """
        :rtype: bool
        """
        return self._embedded

    @property
    def poetic(self):
        return self._poetic

    @property
    def continuation(self):
        return self._continuation

    def accept(self, visitor):
        visitor.before_paragraph(self)
        self.visit_children(visitor)
        visitor.after_paragraph(self)

    class Builder(object):
        def __init__(self, layout=None, embedded=False, introductory=False,
                     poetic=False, continuation=False):
            self._layout = layout
            self._embedded = embedded
            self._introductory = introductory
            self._poetic = poetic
            self._continuation = continuation

        def __call__(self, children):
            return self.build(children)

        def set_layout(self, layout):
            self._layout = layout
            return self

        def build(self, children):
            return Paragraph(children,
                             layout=self._layout,
                             embedded=self._embedded,
                             introductory=self._introductory,
                             poetic=self._poetic,
                             continuation=self._continuation)


class Reference(KindedElement, ParentElement):
    """
    Different than cross-references
    """
    def __init__(self, kind, children):
        KindedElement.__init__(self, kind)
        ParentElement.__init__(self, children)

    def accept(self, visitor):
        visitor.before_reference(self)
        self.visit_children(visitor)
        visitor.after_refence(self)

    @enum.unique
    class Kind(enum.Enum):
        section_range = 0
        parallel = 1
        inline = 2


class ChapterNumber(KindedElement, ParentElement):
    def __init__(self, kind, children):
        KindedElement.__init__(self, kind)
        ParentElement.__init__(self, children)

    def accept(self, visitor):
        visitor.before_chapter_no(self)
        self.visit_children(visitor)
        visitor.after_chapter_no(self)

    @enum.unique
    class Kind(enum.Enum):
        standard = 0
        alternate = 1

        def construct(self, children):
            return ChapterNumber(self, children)


class Footnote(KindedElement, ParentElement):
    def __init__(self, kind, children, label):
        """
        :param Iterable[Element] children:
        :param FootnoteLabel label:
        """
        KindedElement.__init__(self, kind)
        ParentElement.__init__(self, children)
        assert(isinstance(label, FootnoteLabel))
        self._label = label

    @property
    def label(self):
        return self._label

    def accept(self, visitor):
        visitor.before_footnote(self)
        self.visit_children(visitor)
        visitor.after_footnote(self)

    @enum.unique
    class Kind(enum.Enum):
        footnote = 1
        endnote = 2
        cross_reference = 3


class Whitespace(KindedElement):
    def __init__(self, kind):
        KindedElement.__init__(self, kind)

    def accept(self, visitor):
        visitor.whitespace(self)

    @enum.unique
    class Kind(enum.Enum):
        new_line = 0
        page_break = 1

        def construct(self):
            return Whitespace(self)
