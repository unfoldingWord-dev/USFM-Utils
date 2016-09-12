from __future__ import unicode_literals

from usfm_utils.elements.footnote_utils import FootnoteLabelVisitor

from usfm_utils.elements.document import Document
from usfm_utils.elements.element_impls import FormattedText, ChapterNumber, \
    Whitespace
from usfm_utils.elements.element_visitor import ElementVisitor
from usfm_utils.elements.paragraph_utils import ParagraphLayoutVisitor
from usfm_utils.html.html_utils import open_tag, close_tag, open_span, \
    close_span, add_class


class HtmlVisitor(ElementVisitor):
    def __init__(self, writable_file, stylesheets=()):
        """
        :param file writable_file: file to write to
        :param iterable[str|unicode] stylesheets: filenames for stylesheets
        """
        self._file = writable_file
        self._stylesheets = stylesheets

        # footnotes
        self._next_footnote_id = 1
        self._accumulated_footnotes = []
        self._current_footnotes = []

        # paragraphs
        self._layout_visitor = HtmlVisitor.HtmlParagraphLayoutVisitor()

    def write(self, document):
        """
        :param Document document:
        :return:
        """
        self._file.write(html_header(title=document.heading,
                                     stylesheets=self._stylesheets))
        for element in document.elements:
            element.accept(self)
        self.write_footnotes()
        self._file.write(html_footer())

    def record(self, s):
        if len(self._current_footnotes) == 0:
            self._file.write(s)
        else:
            current_footnote = self._current_footnotes[-1]
            current_footnote.write(s)

    def write_footnotes(self):
        for entry in self._accumulated_footnotes:
            self.record(entry.content)
        self._accumulated_footnotes = []

    def before_paragraph(self, paragraph):
        paragraph.layout.accept(self._layout_visitor)
        attributes = self._layout_visitor.attributes
        if paragraph.embedded:
            add_class(attributes, "embedded")
        if paragraph.introductory:
            add_class(attributes, "introductory")
        if paragraph.poetic:
            add_class(attributes, "poetic")
        if paragraph.continuation:
            add_class(attributes, "continuation")
        self.record(open_tag("p", **attributes))

    def after_paragraph(self, paragraph):
        self.record(close_tag("p"))

    def before_chapter_no(self, chapter_no):
        kind = chapter_no.kind
        if kind == ChapterNumber.Kind.standard:
            self.record(open_span(clazz="chapter_no"))
        elif kind == ChapterNumber.Kind.alternate:
            self.record(open_span(classes=["chapter_no", "alt_chapter_no"]))
        else:
            msg = "Unknown chapter number kind: {}".format(kind)
            raise ValueError(msg)

    def after_chapter_no(self, chapter_no):
        self.record(close_span())

    def before_footnote(self, footnote):
        footnote_id = self._next_footnote_id
        self._next_footnote_id = footnote_id + 1

        visitor = HtmlVisitor.HtmlFootnoteLabelVisitor(str(footnote_id))
        footnote.label.accept(visitor)
        self.record("<sup><a href=\"#fn{id}\" id=\"ref{id}\">{lbl}</a></sup>"
                    .format(id=footnote_id, lbl=visitor.result))
        entry = HtmlVisitor.Entry(footnote_id, footnote.kind)
        self._accumulated_footnotes.append(entry)
        self._current_footnotes.append(entry)
        self.record(open_span(clazz=footnote.kind.name, identifier="fn{id}".format(id=footnote_id)))

    def after_footnote(self, footnote):
        entry = self._current_footnotes.pop()
        entry.write("<a href=\"#ref{id}\">^</a>".format(id=entry.identifier))
        entry.write(close_span())

    def before_formatted_text(self, formatted_text):
        if formatted_text.kind in non_span_formatting:
            self.record(non_span_formatting[formatted_text.kind][0])
        else:
            self.record(open_span(clazz=formatted_text.kind.name))

    def after_formatted_text(self, formatted_text):
        if formatted_text.kind in non_span_formatting:
            self.record(non_span_formatting[formatted_text.kind][1])
        else:
            self.record(close_span())

    def before_heading(self, heading):
        flag = "h" + str(heading.weight)
        clazz = heading.kind.name
        self.record(open_tag(flag, clazz=clazz))

    def after_heading(self, heading):
        flag = "h" + str(heading.weight)
        self.record(close_tag(flag))

    def before_other(self, other):
        clazz = other.kind.name
        self.record(open_span(classes=[clazz]))

    def after_other(self, other):
        self.record(close_span())

    def text(self, raw_text):
        self.record(raw_text.content)

    def whitespace(self, whitespace):
        kind = whitespace.kind
        if kind == Whitespace.Kind.new_line:
            self.record("<br>")
        elif kind == Whitespace.Kind.page_break:
            self.record("<p style=\"page-break-after:always;\"></p>")
        else:
            raise ValueError("Unrecognized whitespace: {}".format(kind))

    class Entry(object):
        def __init__(self, identifier, kind):
            self._identifier = identifier
            self._kind = kind
            self._content = ""

        @property
        def content(self):
            return self._content

        @property
        def identifier(self):
            return self._identifier

        def write(self, s):
            self._content += s

    class HtmlFootnoteLabelVisitor(FootnoteLabelVisitor):
        def __init__(self, default):
            self._default = default
            self._result = None

        @property
        def result(self):
            return self._result

        def automatic(self, auto):
            self._result = self._default

        def no_label(self, no_label):
            self._result = ""

        def custom(self, custom):
            self._result = custom.content

    class HtmlParagraphLayoutVisitor(ParagraphLayoutVisitor):
        def __init__(self):
            self._attributes = None

        @property
        def attributes(self):
            return self._attributes

        def right_aligned(self, right_aligned):
            self._attributes = {"align": "right"}

        def centered(self, centered):
            self._attributes = {"align": "center"}

        def left_aligned(self, left_aligned):
            classes = [
                "first_line_" + left_aligned.first_line_indent.name,
                "left_margin_" + str(left_aligned.left_margin_indent)
            ]
            self._attributes = {"class": " ".join(classes)}


# formatting kinds that do not use span/classes
non_span_formatting = {
    FormattedText.Kind.bold: ("<b>", "</b>"),
    FormattedText.Kind.emphasis: ("<em>", "</em>"),
    FormattedText.Kind.italics: ("<i>", "</i>"),
    FormattedText.Kind.no_effect: ("", "")
}


def html_header(title="", stylesheets=()):
    styles = "\n".join("<link rel=\"stylesheet\" href=\"{}\">".format(stylesheet)
                       for stylesheet in stylesheets)
    return u"""<!DOCTYPE html>
        <meta charset=\"utf-8\">
        <head>
        <title>{title}</title>
        {styles}
        </head>
        <html>
        <body>
        """.format(title=title, styles=styles)


def html_footer():
    return """</body></html>"""
