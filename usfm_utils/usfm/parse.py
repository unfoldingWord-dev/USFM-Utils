import ply.yacc as yacc
from usfm_utils.elements.paragraph_utils import LeftAligned

from usfm_utils.elements.document import Document, TableOfContentsInfo
from usfm_utils.elements.element_impls import Footnote, FormattedText, \
    Paragraph, Text, ChapterNumber
from usfm_utils.usfm.flags import paragraphs, indented_paragraphs, \
    lower_open_closes, higher_open_closes, headings, higher_rest_of_lines, \
    lower_until_next_flags, whitespace
from usfm_utils.usfm.lex import tokens
from usfm_utils.usfm.usfm_error import UsfmInputError


def parse_paragraph(name, builder):
    def parse_paragraph_inner(self, t):
        paragraph = builder(t[2])
        self._previous_paragraph = paragraph
        t[0] = [paragraph]
    parse_paragraph_inner.__doc__ = "higher_element : {} lower_elements".format(name)
    return parse_paragraph_inner


def parse_indented_paragraph(name, constructor):
    def parse_indented_paragraph_inner(self, t):
        indent = t[1].number
        children = t[2]
        paragraph = constructor(children, indent)
        self._previous_paragraph = paragraph
        t[0] = [paragraph]
    parse_indented_paragraph_inner.__doc__ = "higher_element : {} lower_elements".format(name)
    return parse_indented_paragraph_inner


def parse_heading(name, builder):
    """
    :param str name:
    :param callable[children, weight -> Heading] builder:
    :return:
    """
    def parse_heading_inner(self, t):
        rest_of_line = t[1].value
        weight = t[1].number
        text = Text(rest_of_line)
        heading = builder([text], weight)
        t[0] = heading
    result = higher_rule(parse_heading_inner, 2)
    result.__doc__ = "higher_element : {} lower_elements".format(name)
    return result


def parse_whitespace(name, kind):
    """
    :param str name:
    :param Whitespace.Kind kind:
    :return:
    """
    def parse_whitespace_inner(self, t):
        t[0] = kind.construct()
    result = higher_rule(parse_whitespace_inner, 2)
    result.__doc__ = "higher_element : {} lower_elements".format(name)
    return result


def of_text(func):
    """
    Returns a function that produces an Element from a string of text
    :param callable[children -> Element] func:
    :rtype: callable[str -> Element]
    """
    return lambda text: func([Text(text)])


def higher_rule(lower_rule, lower_elements_index):
    """
    Converts a "lower-element" rule into the corresponding "higher-element" rule
    :param callable[(self, t)] lower_rule: a rule for a "lower" element
    :param int lower_elements_index: index of preceding lower_elements in rule
    """
    def higher_rule_inner(self, t):
        lower_rule(self, t)
        t[0] = [t[0]]
        if len(t[lower_elements_index]) > 0:
            t[0].append(Paragraph(t[lower_elements_index]))
    return higher_rule_inner


def unary_rule(f, index, extract=False):
    def unary_rule_inner(self, t):
        value = t[index].value if extract else t[index]
        t[0] = f(value)
    return unary_rule_inner



class UsfmParser(object):
    start = "document"

    # right associativity favors shifting
    precedence = (("right", "CHAPTER_LABEL", "CHAPTER"),)

    def __init__(self):
        # tracking chapter labels
        self.relative_chapter_label = None
        self.tokens = None

        # tracking text formatting
        self._formattings = []
        self._parser = None

        # previous paragraph
        self._previous_paragraph = None

        # metadata
        self._heading = None
        self._toc_builder = TableOfContentsInfo.Builder()

    def reset(self):
        self.relative_chapter_label = None
        self._formattings = None

    @staticmethod
    def create():
        """
        Factory method for constructing new instances. Should be used instead of
        "normal" initialization
        """
        usfm_parser = UsfmParser()
        usfm_parser.init()
        return usfm_parser

    def register(self, name, func):
        setattr(UsfmParser, "p_" + name, func)

    def p_document(self, t):
        """document : higher_elements EOF"""
        t[0] = Document(t[1],
                        heading=self._heading,
                        table_of_contents=self._toc_builder.build())

    def p_higher_elements(self, t):
        """higher_elements : higher_elements higher_element
                           | """
        if len(t) <= 1:
            t[0] = []
            return
        l = t[1]
        l.extend(t[2])
        t[0] = l

    def init(self):
        self.tokens = tokens

        for (name, (flag, builder)) in paragraphs.items():
            if builder is None:
                continue
            self.register(name, parse_paragraph(name, builder))

        for (name, (flag, constructor)) in indented_paragraphs.items():
            self.register(name, parse_indented_paragraph(name, constructor))

        for name in headings:
            _, builder = headings[name]
            if builder is not None:
                rule = parse_heading(name, builder)
                self.register(name, rule)

        for name in lower_open_closes:
            _, constructor = lower_open_closes[name]
            if constructor is not None:
                rule = unary_rule(constructor, 2)
                rule.__doc__ = "lower_element : {} lower_elements {}".format("OPEN_" + name, "CLOSE_" + name)
                self.register(name, rule)

        for name in higher_open_closes:
            _, constructor = higher_open_closes[name]
            if constructor is not None:
                rule = higher_rule(unary_rule(constructor, 2), 4)
                rule.__doc__ = "higher_element : {} lower_elements {} lower_elements".format(
                    "OPEN_" + name, "CLOSE_" + name)
                self.register(name, rule)

        for name in higher_rest_of_lines:
            _, constructor = higher_rest_of_lines[name]
            if constructor is not None:
                rule = higher_rule(unary_rule(of_text(constructor), 1, extract=True), 2)
                rule.__doc__ = "higher_element : {} lower_elements".format(name)
                self.register(name, rule)

        for name in lower_until_next_flags:
            _, builder = lower_until_next_flags[name]
            if builder is not None:
                rule = unary_rule(of_text(builder), 1, extract=True)
                rule.__doc__ = "lower_element : {}".format(name)
                self.register(name, rule)

        for name in whitespace:
            _, kind = whitespace[name]
            rule = parse_whitespace(name, kind)
            self.register(name, rule)

        self._parser = yacc.yacc(module=self)

    def p_chapter(self, t):
        """higher_element : CHAPTER lower_elements"""
        if self.relative_chapter_label is not None:
            text = self.relative_chapter_label + " " + t[1].value
        else:
            text = t[1].value
        chapter = ChapterNumber(ChapterNumber.Kind.standard, [Text(text)])
        if len(t[2]) == 0:
            t[0] = [chapter]
        else:
            t[0] = [chapter, Paragraph(t[2])]

    def p_chapter_label_before(self, t):
        """higher_element : CHAPTER_LABEL CHAPTER lower_elements"""
        self.relative_chapter_label = t[1].value
        text = self.relative_chapter_label + " " + t[2].value
        chapter = ChapterNumber(ChapterNumber.Kind.standard, [Text(text)])
        if len(t[3]) == 0:
            t[0] = [chapter]
        else:
            t[0] = [chapter, Paragraph(t[3])]

    def p_chapter_label_after(self, t):
        """higher_element : CHAPTER CHAPTER_LABEL lower_elements"""
        chapter = ChapterNumber(ChapterNumber.Kind.standard, [Text(t[2].value)])
        if len(t[3]) == 0:
            t[0] = [chapter]
        else:
            t[0] = [chapter, Paragraph(t[3])]

    def p_heading(self, t):
        """higher_element : HEADING"""
        heading = t[1].value
        self._heading = heading
        t[0] = []

    def p_no_break(self, t):
        """higher_element : NO_BREAK lower_elements"""
        prev = self._previous_paragraph
        if prev is None:
            paragraph = Paragraph(t[2])
        else:
            paragraph = Paragraph(
                t[2],
                layout=LeftAligned(LeftAligned.FirstLineIndent.none),
                embedded=prev.embedded,
                introductory=prev.introductory,
                poetic=prev.poetic,
                continuation=True
            )
        self._previous_paragraph = paragraph
        t[0] = [paragraph]

    def p_toc(self, t):
        """higher_element : TABLE_OF_CONTENTS"""
        value = t[1].value
        weight = t[1].number
        if weight == 1:
            self._toc_builder.set_long_description(value)
        elif weight == 2:
            self._toc_builder.set_short_description(value)
        elif weight == 3:
            self._toc_builder.set_abbreviation(value)
        else:
            pass  # TODO warning?
        t[0] = []

    def p_lower_elements(self, t):
        """lower_elements : lower_elements lower_element
                          | """
        if len(t) <= 1:
            t[0] = []
            return
        l = t[1]
        l.append(t[2])
        t[0] = l

    def p_lower_element_as_text(self, t):
        """lower_element : TEXT"""
        t[0] = Text(t[1].value)

    def p_lower_element_as_verse(self, t):
        """lower_element : VERSE"""
        t[0] = FormattedText.Kind.verse_no.construct([Text(t[1].value)])

    def p_lower_element_as_published_verse(self, t):
        r"""lower_element : VERSE OPEN_PUBLISHED_VERSE lower_elements CLOSE_PUBLISHED_VERSE"""
        t[0] = FormattedText.Kind.verse_no.construct(t[3])

    def p_footnote(self, t):
        """lower_element : OPEN_FOOTNOTE FOOTNOTE_LABEL lower_elements CLOSE_FOOTNOTE"""
        t[0] = Footnote(Footnote.Kind.footnote, t[3], t[2].value)

    def p_endnote(self, t):
        """lower_element : OPEN_ENDNOTE FOOTNOTE_LABEL lower_elements CLOSE_ENDNOTE"""
        t[0] = Footnote(Footnote.Kind.endnote, t[3], t[2].value)

    def p_cross_reference(self, t):
        """lower_element : OPEN_CROSS_REFERENCE FOOTNOTE_LABEL lower_elements CLOSE_CROSS_REFERENCE"""
        t[0] = Footnote(Footnote.Kind.cross_reference, t[3], t[2].value)

    def p_error(self, token):
        msg = "Unexpected token of type {}".format(token.type)
        raise UsfmInputError(msg, token.value.position)

    def parse(self, lexer):
        return self._parser.parse(lexer=lexer)
