
class ElementVisitor(object):
    def before_paragraph(self, paragraph):
        """
        :param Paragraph paragraph:
        """
        pass

    def after_paragraph(self, paragraph):
        """
        :param Paragraph paragraph:
        """
        pass

    def before_formatted_text(self, formatted_text):
        """
        :param FormattedText formatted_text:
        """
        pass

    def after_formatted_text(self, formatted_text):
        """
        :param FormattedText formatted_text:
        """
        pass

    def before_heading(self, heading):
        """
        :param Heading heading:
        """
        pass

    def after_heading(self, heading):
        """
        :param Heading heading:
        """
        pass

    def before_chapter_no(self, chapter_no):
        """
        :param ChapterNumber chapter_no:
        """
        pass

    def after_chapter_no(self, chapter_no):
        """
        :param ChapterNumber chapter_no:
        """
        pass

    def before_other(self, other):
        """
        :param OtherText other:
        """
        pass

    def after_other(self, other):
        """
        :param OtherText other:
        """
        pass

    def before_footnote(self, footnote):
        """
        :param Footnote footnote:
        """
        pass

    def after_footnote(self, footnote):
        """
        :param Footnote footnote:
        """
        pass

    def text(self, text):
        """
        :param Text text:
        """
        pass

    def whitespace(self, whitespace):
        """
        :param Whitespace whitespace:
        """
        pass
