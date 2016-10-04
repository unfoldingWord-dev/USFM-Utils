import itertools
import unittest

from usfm_utils.elements.document import Document
from usfm_utils.elements.element_impls import FormattedText, Text, Paragraph, Footnote
from usfm_utils.elements.footnote_utils import AutomaticFootnoteLabel, CustomFootnoteLabel
from usfm_utils.html.html_visitor import HtmlVisitor, non_span_formatting

from tests import test_utils


class HtmlRenderingTest(unittest.TestCase):

    @staticmethod
    def render_elements(*elements):
        return HtmlRenderingTest.render(Document(elements))

    @staticmethod
    def render(document):
        test_file = HtmlRenderingTest.TestFile()
        visitor = HtmlVisitor(test_file)
        visitor.write(document)
        return test_file.content()

    def test_footnotes(self):
        for kind in list(Footnote.Kind):
            word = test_utils.word()
            footnote = Footnote(kind, [Text(word)], AutomaticFootnoteLabel())
            paragraph = Paragraph([footnote])
            rendered = self.render_elements(paragraph)
            self.assertIn(kind.name, rendered)
            self.assertIn(word, rendered)
        for kind in list(Footnote.Kind):
            word = test_utils.word()
            label = test_utils.word(allow_empty=False)
            footnote = Footnote(kind, [Text(word)], CustomFootnoteLabel(label))
            paragraph = Paragraph([footnote])
            rendered = self.render_elements(paragraph)
            self.assertIn(kind.name, rendered)
            self.assertIn(word, rendered)
            self.assertIn(label, rendered)

    def test_formatted_text(self):
        for kind in list(FormattedText.Kind):
            text = " ".join(test_utils.word(allow_empty=False)
                            for _ in range(10))
            formatted_text = FormattedText(kind, [Text(text)])
            rendered = self.render_elements(formatted_text)
            self.assertIn(text, rendered)
            if kind in non_span_formatting:
                open_tag, close_tag = non_span_formatting[kind]
                self.assertIn(open_tag, rendered)
                self.assertIn(close_tag, rendered)
            else:
                self.assertIn(kind.name, rendered)  # kind.name should appear as a class

    def test_heading(self):
        word = test_utils.word()
        heading = test_utils.word()
        elements = [Paragraph([Text(word)])]
        document = Document(elements, heading=heading)
        rendered = self.render(document)
        self.assertIn(word, rendered)
        self.assertIn(heading, rendered)

    def test_paragraph(self):
        bools = (False, True)
        for embedded, poetic, introductory, continuation \
                in itertools.product(bools, bools, bools, bools):
            word = test_utils.word()
            text = Text(word)
            paragraph = Paragraph([text],
                                  embedded=embedded,
                                  poetic=poetic,
                                  introductory=introductory,
                                  continuation=continuation)
            rendered = self.render_elements(paragraph)
            self.assertIn(word, rendered)
            if embedded:
                self.assertIn("embedded", rendered)  # should appear as a class
            else:
                self.assertNotIn("embedded", rendered)
            if poetic:
                self.assertIn("poetic", rendered)
            else:
                self.assertNotIn("poetic", rendered)
            if introductory:
                self.assertIn("introductory", rendered)
            else:
                self.assertNotIn("introductory", rendered)
            if continuation:
                self.assertIn("continuation", rendered)
            else:
                self.assertNotIn("continuation", rendered)

    class TestFile(object):
        """
        A file-like string object used for mocking text files
        """
        def __init__(self):
            self._content = ""

        def content(self):
            return self._content

        def write(self, p_str):
            self._content += p_str


if __name__ == "__main__":
    unittest.main()
