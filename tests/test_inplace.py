import unittest

from usfm_utils.elements.document import Document
from usfm_utils.elements.element_impls import FormattedText, Text, Paragraph, Footnote
from usfm_utils.elements.footnote_utils import AutomaticFootnoteLabel
from usfm_utils.inplace import WordCountVisitor

from tests import test_utils


class WordCountTest(unittest.TestCase):
    def assert_word_count(self, elements, expected):
        doc = Document(elements)
        word_count_visitor = WordCountVisitor()
        doc.accept(word_count_visitor)
        self.assertEqual(word_count_visitor.word_count, expected)

    def test_footnote(self):
        footnote = Footnote(Footnote.Kind.footnote,
                [Text(test_utils.words(5))],
                AutomaticFootnoteLabel())
        paragraph = Paragraph([footnote, Text(test_utils.words(3))])
        self.assert_word_count([paragraph], 8)

    def test_formatted_text(self):
        formatted_text = FormattedText(FormattedText.Kind.bold,
                [Text(test_utils.words(3))])
        normal_text = Text(test_utils.words(1))
        paragraph = Paragraph([formatted_text, normal_text], embedded=True)
        self.assert_word_count([paragraph], 4)


if __name__ == "__main__":
    unittest.main()
