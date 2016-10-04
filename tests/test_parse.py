from __future__ import unicode_literals

import random
import unittest

from past.builtins import basestring

from tests import test_utils
from usfm_utils.elements.abstract_elements import Element
from usfm_utils.elements.document import Document
from usfm_utils.elements.element_impls import ChapterNumber, Paragraph, \
    FormattedText, Text, Heading, Whitespace, Footnote
from usfm_utils.elements.paragraph_utils import LeftAligned
from usfm_utils.usfm.flags import paragraphs, indented_paragraphs, \
    lower_open_closes, higher_open_closes, headings, higher_rest_of_lines, \
    lower_until_next_flags, whitespace, footnotes
from usfm_utils.usfm.lex import UsfmLexer
from usfm_utils.usfm.parse import UsfmParser
from usfm_utils.usfm.usfm_error import UsfmInputError


class UsfmParserTests(unittest.TestCase):
    longMessage = True

    lexer = UsfmLexer.create()
    parser = UsfmParser.create()

    @staticmethod
    def parse(*lines):
        """
        :rtype: Document
        """
        UsfmParserTests.parser.reset()
        text = "\n".join(lines)
        UsfmParserTests.lexer.input(text)
        return UsfmParserTests.parser.parse(UsfmParserTests.lexer)

    def test_published_verse(self):
        word = test_utils.word()
        document = self.parse(r"\p \v 4 \vp 5 \vp* {w}".format(w=word))
        elements = document.elements
        paragraph = elements[0]
        self.assertIsInstance(paragraph, Paragraph)
        verse = paragraph.children[0]
        self.assertIsInstance(verse, FormattedText)
        self.assertIn("5", verse.children[0].content)

    # test chapter labels

    def test_chapter_label_before(self):
        word = test_utils.word()
        document = self.parse(r"\cl {w}".format(w=word), r"\c 4")
        elements = document.elements
        chapter_no = elements[0]
        self.assertIsInstance(chapter_no, ChapterNumber)
        self.assertEqual(chapter_no.children[0].content, "{w} 4".format(w=word))

    def test_chapter_label_after(self):
        word = test_utils.word()
        document = self.parse(r"\c 4", r"\cl {}".format(word))
        elements = document.elements
        chapter_no = elements[0]
        self.assertIsInstance(chapter_no, ChapterNumber)
        self.assertEqual(chapter_no.children[0].content, word)

    def test_ambiguous_chapter_labels(self):
        document = self.parse(r"\c 4", r"\cl Hello", r"\c 5")
        elements = document.elements
        chapter_no_1 = elements[0]
        self.assertIsInstance(chapter_no_1, ChapterNumber)
        self.assertEqual(chapter_no_1.children[0].content, "Hello")
        chapter_no_2 = elements[1]
        self.assertIsInstance(chapter_no_2, ChapterNumber)
        self.assertEqual(chapter_no_2.children[0].content, "5")

    # test token "groups"

    def test_lower_open_closes(self):
        for name, (flag, builder) in lower_open_closes.items():
            if builder is None:
                continue
            word = test_utils.word(allow_empty=False)
            s = r"\p \{flag} {word}\{flag}*".format(flag=flag, word=word)
            document = self.parse(s)
            elements = document.elements
            self.assertEqual(len(elements), 1)
            paragraph = elements[0]
            self.assertIsInstance(paragraph, Paragraph)
            self.assertEqual(len(paragraph.children), 1)
            formatted = paragraph.children[0]
            self.assertIsInstance(formatted, FormattedText)
            self.assertEqual(len(formatted.children), 1)
            if len(formatted.children) > 0 and isinstance(formatted.children[0], Text):
                self.assertEqual(formatted.children[0].content, word)

    def test_higher_open_closes(self):
        for name, (flag, builder) in higher_open_closes.items():
            if builder is None:
                continue
            s = r"\{flag} hey\{flag}*".format(flag=flag)
            document = self.parse(s)
            elements = document.elements
            self.assertEqual(len(elements), 1)
            element = elements[0]
            self.assertIsInstance(element, Element)

    def test_paragraphs(self):
        for name, (flag, builder) in paragraphs.items():
            if builder is None:
                continue
            num_words = random.randint(0, 10)
            words = " ".join(test_utils.word() for _ in range(num_words))
            s = r"\{flag} {words}".format(flag=flag, words=words)
            document = self.parse(s)
            elements = document.elements
            self.assertEqual(len(elements), 1)
            paragraph = elements[0]
            self.assertIsInstance(paragraph, Paragraph)
            self.assertIn(len(paragraph.children), [0, 1])

    def test_indented_paragraphs(self):
        for name, (flag, builder) in indented_paragraphs.items():
            if builder is None:
                continue
            for indent in ["", "1", "2", "3", "4", "5", "6"]:
                s = r"\{flag}{indent} \bd goodbye \bd*".format(flag=flag,
                                                               indent=indent)
                document = self.parse(s)
                elements = document.elements
                self.assertEqual(len(elements), 1)
                paragraph = elements[0]
                self.assertIsInstance(paragraph, Paragraph)
                self.assertIsInstance(paragraph.layout, LeftAligned)
                expected_indent = 1 if indent == "" else int(indent)
                self.assertEqual(paragraph.layout.left_margin_indent, expected_indent)

    def test_headings(self):
        for name, (flag, kind) in headings.items():
            if kind is None:
                continue
            for weight in ["", "1", "2", "3", "4", "5", "6"]:
                err_msg = "flag: {}, weight: {}".format(flag, weight)
                document = self.parse(r"\{f}{w} hello world".format(f=flag, w=weight), "hey there")
                elements = document.elements
                self.assertEqual(len(elements), 2, err_msg)
                heading = elements[0]
                self.assertIsInstance(heading, Heading, err_msg)
                if weight == "":
                    self.assertEqual(heading.weight, 1)
                else:
                    self.assertEqual(heading.weight, int(weight))
                self.assertEqual(len(heading.children), 1, err_msg)
                text = heading.children[0]
                self.assertIsInstance(text, Text, err_msg)
                self.assertEqual(text.content, "hello world", err_msg)

    def test_until_next_flags(self):
        for name, (flag, builder) in lower_until_next_flags.items():
            if builder is None:
                continue
            document = self.parse(r"\p \{} hello \p world".format(flag))
            elements = document.elements
            self.assertEqual(len(elements), 2)
            self.assertIsInstance(elements[0], Paragraph)
            self.assertEqual(len(elements[0].children), 1)
            child = elements[0].children[0]
            self.assertIsInstance(child, FormattedText)
            self.assertEqual(len(child.children), 1)
            text = child.children[0]
            self.assertIsInstance(text, Text)
            self.assertIsInstance(text.content, basestring)
            self.assertIsInstance(elements[1], Paragraph)

    def test_higher_rest_of_lines(self):
        for name, (flag, builder) in higher_rest_of_lines.items():
            if builder is None:
                continue
            document = self.parse(r"\p hello", "\{} world".format(flag))
            elements = document.elements
            self.assertEqual(len(elements), 2)
            self.assertIsInstance(elements[0], Paragraph)
            self.assertIsInstance(elements[1], Element)

    def test_whitespace(self):
        for name, (flag, kind) in whitespace.items():
            document = self.parse(r"\{}".format(flag))
            elements = document.elements
            self.assertEqual(len(elements), 1)
            self.assertIsInstance(elements[0], Whitespace)
            self.assertEqual(elements[0].kind, kind)

    def test_heading(self):
        heading = test_utils.word()
        document = self.parse(
            r"\id {}".format(test_utils.word()),
            r"",
            r"\h   {}".format(heading),
            r"\p {}".format(test_utils.word())
        )
        self.assertEqual(document.heading, heading)
        elements = document.elements
        self.assertEqual(len(elements), 1)

    def test_table_of_contents(self):
        word1 = test_utils.word()
        word2 = test_utils.word()
        word3 = test_utils.word()
        document = self.parse(
            r"\toc1 {}".format(word1),
            r"\toc2 {}".format(word2),
            r"\toc3 {}".format(word3)
        )
        elements = document.elements
        self.assertEqual(len(elements), 0)
        toc = document.table_of_contents
        self.assertEqual(toc.long_description, word1)
        self.assertEqual(toc.short_description, word2)
        self.assertEqual(toc.abbreviation, word3)

    def test_footnotes1(self):
        for name, (flag, kind) in footnotes.items():
            for label in ("+", "-", "4"):
                word = test_utils.word()
                paragraph_flag = random.choice(["p", "m", "pi", "ipr"])
                lines = (
                    r"\{}".format(paragraph_flag),
                    r"\{f} {l} {w} \{f}*".format(f=flag, l=label, w=word)
                )
                document = self.parse(*lines)
                self.assertIsNone(document.heading)
                elements = document.elements
                self.assertEqual(len(elements), 1)
                paragraph = elements[0]
                self.assertIsInstance(paragraph, Paragraph)
                children = paragraph.children
                self.assertEqual(len(children), 1)
                footnote = children[0]
                self.assertIsInstance(footnote, Footnote)
                self.assertEqual(footnote.kind, kind)

    def test_footnotes2(self):
        for name, (flag, kind) in footnotes.items():
            for label in ("+", "-", "4"):
                word1 = test_utils.word(allow_empty=False)
                word2 = test_utils.word(allow_empty=False)
                paragraph_flag = random.choice(["p", "m", "pi", "ipr"])
                lines = (
                    r"\{p}".format(p=paragraph_flag),
                    r"\{f} {l} {w1} \fqa {w2} \{f}*".format(f=flag, l=label,
                                                            w1=word1, w2=word2),
                )
                document = self.parse(*lines)
                self.assertIsNone(document.heading)
                elements = document.elements
                self.assertEqual(len(elements), 1)
                paragraph = elements[0]
                self.assertIsInstance(paragraph, Paragraph)
                children = paragraph.children
                self.assertEqual(len(children), 1)
                footnote = children[0]
                self.assertIsInstance(footnote, Footnote)
                self.assertEqual(footnote.kind, kind)
                self.assertEqual(len(footnote.children), 2)

    def test_no_break(self):
        for _ in range(10):
            paragraph_flag = random.choice(["p", "m", "pmo", "pi", "q"])
            text = " ".join(test_utils.word() for _ in range(10)) + "a"
            lines = (
                r"\{p}".format(p=paragraph_flag),
                r"\nb",
                r"{t}".format(t=text)
            )
            document = self.parse(*lines)
            elements = document.elements
            self.assertEqual(len(elements), 2)
            p0 = elements[0]
            self.assertIsInstance(p0, Paragraph)
            p1 = elements[1]
            self.assertIsInstance(p1, Paragraph)
            self.assertEqual(p0.embedded, p1.embedded)
            self.assertEqual(p0.poetic, p1.poetic)
            self.assertEqual(p0.introductory, p1.introductory)
            self.assertFalse(p0.continuation)
            self.assertTrue(p1.continuation)
            self.assertEqual(len(p1.children), 1)
            child = p1.children[0]
            self.assertIsInstance(child, Text)
            self.assertEqual(child.content.strip(), text.strip())

    # tests for errors

    def test_unrecognized_flag(self):
        for _ in range(10):
            word = test_utils.word()
            lines = (
                r"\{}".format(random.choice(["p", "m", "pi", "ipr"])),
                r"\{flag}".format(flag=word),
            )
            self.assert_raises_at(lines, line_no=2, col=1)

    def test_no_footnote_label(self):
        for name, (flag, kind) in footnotes.items():
            lines = (
                r"\mt1 {}".format(test_utils.word()),
                r"\{f} \{f}*".format(f=flag),
            )
            self.assert_raises_at(lines, line_no=2, col=len(flag) + 3)

    def test_unmatched(self):
        for name, (flag, kind) in lower_open_closes.items():
            if kind is None:
                continue
            lines = (
                r"\{}".format(random.choice(["p", "m", "pi", "ipr"])),
                r"\{f} {w}".format(f=flag, w=test_utils.word()),
                r"   "
            )
            self.assert_raises_at(lines, line_no=4, col=1)
            word = test_utils.word()
            lines = (
                r"\{}".format(random.choice(["p", "m", "pi", "ipr"])),
                r"{w} \{f}*".format(w=word, f=flag),
                r"  "
            )
            self.assert_raises_at(lines, line_no=2, col=len(word) + 2)

    # helper function

    def assert_raises_at(self, lines, line_no, col=None):
        try:
            self.parse(*lines)
            self.fail()
        except UsfmInputError as e:
            self.assertIsNotNone(e.message)
            self.assertEqual(e.position.line, line_no)
            if col is not None:
                self.assertEqual(e.position.col, col)


if __name__ == "__main__":
    unittest.main(verbosity=0)
