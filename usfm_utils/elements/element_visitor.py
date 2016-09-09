
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

    def before_footnote(self, footnote):
        pass

    def after_footnote(self, footnote):
        pass

    def text(self, raw_text):
        """
        :param RawText raw_text:
        """
        pass

    def whitespace(self, whitespace):
        """
        :param Whitespace whitespace:
        """
        pass