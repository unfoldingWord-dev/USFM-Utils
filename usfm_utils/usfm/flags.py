"""
This module stores info about USFM flags that is used by the lexer and parser.

Most of this info is store in dictionaries whose keys are flag names (used as token
names in lexing), and whose values are (flag, constructor) pairs, where flag is the
string literal that is used inside USFM files, and constructor is a function for
constructing the corresponding Element.

In general, a constructor of None means that a particular flag has special functionality,
and needs to be handled separately during parsing
"""

from usfm_utils.elements.element_impls import Paragraph, FormattedText, \
    ChapterNumber, OtherText, Text, Heading, Whitespace, Footnote
from usfm_utils.elements.paragraph_utils import Centered, LeftAligned, \
    RightAligned


# TOKEN_NAME: (flag, callable[children -> Paragraph])
paragraphs = {
    "CENTERED_PARAGRAPH": ("pc", Paragraph.Builder(layout=Centered())),
    "PARAGRAPH": ("p", Paragraph.Builder()),
    "FLUSH_PARAGRAPH": ("m", Paragraph.Builder(layout=LeftAligned(LeftAligned.FirstLineIndent.none))),
    "EMBEDDED_OPENING": ("pmo", Paragraph.Builder(layout=LeftAligned(LeftAligned.FirstLineIndent.none),
                                                  embedded=True)),
    "EMBEDDED_PARAGRAPH": ("pm", Paragraph.Builder(embedded=True)),
    "EMBEDDED_CLOSING": ("pmc", Paragraph.Builder(layout=LeftAligned(LeftAligned.FirstLineIndent.none),
                                                  embedded=True)),
    "EMBEDDED_REFRAIN": ("pmr", Paragraph.Builder(embedded=True,
                                                  layout=RightAligned())),
    "NO_BREAK": ("nb", None),
    "POETIC_RIGHT_ALIGNED": ("qr", Paragraph.Builder(layout=RightAligned(),
                                                     poetic=True)),
    "POETIC_CENTERED": ("qc", Paragraph.Builder(layout=Centered(), poetic=True)),

    # introductory paragraphs
    "INTRO_PARAGRAPH": ("ip", Paragraph.Builder(introductory=True)),
    "INTRO_INDENTED": ("ipi", Paragraph.Builder(layout=LeftAligned(left_margin_indent=1),
                                                introductory=True)),
    "INTRO_FLUSH": ("im", Paragraph.Builder(layout=LeftAligned(LeftAligned.FirstLineIndent.none),
                                            introductory=True)),
    "INTRO_INDENTED_FLUSH": ("imi", Paragraph.Builder(layout=LeftAligned(
        LeftAligned.FirstLineIndent.none, left_margin_indent=1), introductory=True)),
    "INTRO_QUOTE": ("ipq", lambda children: Paragraph.Builder(introductory=True)
                    .build([FormattedText.Kind.quotation.construct(children)])),
    "INTRO_FLUSH_QUOTE": ("imq", lambda children: Paragraph.Builder(introductory=True)
                          .build([FormattedText.Kind.quotation.construct(children)])),
    "INTRO_RIGHT_ALIGNED": ("ipr", Paragraph.Builder(
        layout=RightAligned(), introductory=True))
}


# TOKEN_NAME: (flag, callable[children, indent -> Paragraph])
indented_paragraphs = {
    "INDENTED_PARAGRAPH":
        ("pi",
         lambda children, indent: Paragraph.Builder(
            layout=LeftAligned(left_margin_indent=indent)
         ).build(children)),
    "LIST_ITEM":
        ("li",
         lambda children, indent: Paragraph.Builder(
             layout=LeftAligned(LeftAligned.FirstLineIndent.outdent, left_margin_indent=indent),
             embedded=True
         ).build(children)),
    "POETIC_LINE":
        ("q",
         lambda children, indent: Paragraph.Builder(
             layout=LeftAligned(left_margin_indent=indent),
             poetic=True
         ).build(children)),
    "EMBEDDED_POETIC":
        ("qm",
         lambda children, indent: Paragraph.Builder(
             layout=LeftAligned(left_margin_indent=indent),
             embedded=True,
             poetic=True
         ).build(children)),

    # introductory
    "INTRO_LIST_ITEM":
        ("ili",
         lambda children, indent: Paragraph.Builder(
             layout=LeftAligned(LeftAligned.FirstLineIndent.outdent, left_margin_indent=indent),
             introductory=True
         ).build(children)),
    "INTRO_POETIC":
        ("iq",
         lambda children, indent: Paragraph.Builder(
             layout=LeftAligned(left_margin_indent=indent),
             introductory=True,
             poetic=True
         ).build(children)),
}


# TOKEN_NAME: (flag, callable[children -> Element])
lower_open_closes = {
    "ALT_VERSE": ("va", FormattedText.Kind.alternate_verse_no.construct),
    "BOLD": ("bd", FormattedText.Kind.bold.construct),
    "BOLD_AND_ITALICS": ("bdit", lambda children: FormattedText(
        FormattedText.Kind.bold, [FormattedText(FormattedText.Kind.italics, children)])),
    "BOOK_TITLE": ("bk", FormattedText.Kind.book_title.construct),
    "CROSS_REF_DEUTEROCANONICAL": ("xdc", FormattedText.Kind.deuterocanonical.construct),
    "CROSS_REF_NEW_TESTAMENT": ("xnt", FormattedText.Kind.footnote_new_testament.construct),
    "CROSS_REF_OLD_TESTAMENT": ("xot", FormattedText.Kind.footnote_old_testament.construct),
    "DEUTEROCANONICAL": ("dc", FormattedText.Kind.deuterocanonical.construct),
    "EMPHASIS": ("em", FormattedText.Kind.emphasis.construct),
    "FOOTNOTE_DEUTEROCANONICAL": ("fdc", FormattedText.Kind.deuterocanonical.construct),
    "FOOTNOTE_REFERENCE_MARK": ("fm", FormattedText.Kind.footnote_reference_mark.construct),

    "ITALICS": ("it", FormattedText.Kind.italics.construct),
    "KEYWORD": ("k", FormattedText.Kind.keyword.construct),
    "NAME_OF_GOD": ("nd", FormattedText.Kind.name_of_god.construct),
    "NORMAL": ("no", FormattedText.Kind.normal.construct),
    "ORDINAL": ("ord", FormattedText.Kind.ordinal.construct),
    "PROPER_NAME": ("pn", FormattedText.Kind.proper_name.construct),
    "PUBLISHED_VERSE": ("vp", None),
    "QUOTED_TEXT": ("qt", FormattedText.Kind.quotation.construct),
    "SECONDARY_LANG": ("sls", FormattedText.Kind.secondary_language.construct),
    "SIGNATURE": ("sig", FormattedText.Kind.signature.construct),
    "SMALL_CAPS": ("sc", FormattedText.Kind.lower_case.construct),
    "TRANSLATOR_ADDITION": ("add", FormattedText.Kind.translator_addition.construct),
    "WORDS_OF_JESUS": ("wj", FormattedText.Kind.words_of_jesus.construct)
}

# TOKEN_NAME: (flag, callable[children -> Element])
higher_open_closes = {
    "ALT_CHAPTER": ("ca", ChapterNumber.Kind.alternate.construct),
    "SELAH": ("qs", OtherText.Kind.selah.construct),
}


# TOKEN_NAME: (flag, callable[children -> Element])
headings = {
    "HEADING": ("h", None),
    "TABLE_OF_CONTENTS": ("toc", None),
    "MAJOR_TITLE": ("mt", Heading.Builder(Heading.Kind.major_title)),
    "MAJOR_TITLE_END": ("mte", Heading.Builder(Heading.Kind.major_title_end)),
    "MAJOR_SECTION": ("ms", Heading.Builder(Heading.Kind.major_section)),
    "SECTION": ("s", Heading.Builder(Heading.Kind.section)),
    "INTRO_MAJOR_TITLE": ("imt", Heading.Builder(Heading.Kind.major_title,
                                                 introductory=True)),
    "INTRO_MAJOR_TITLE_END": ("imte", Heading.Builder(Heading.Kind.major_title_end,
                                                      introductory=True)),
    "INTRO_SECTION": ("is", Heading.Builder(Heading.Kind.section,
                                            introductory=True)),
    "INTRO_OUTLINE_TITLE": ("iot", Heading.Builder(Heading.Kind.outline_title,
                                                   introductory=True))
}

# Flags that take a one-word argument
# TOKEN_NAME: (flag, callable[children -> Element])
one_word_arguments = {
    "CHAPTER": ("c", None),
    "VERSE": ("v", FormattedText.Kind.verse_no.construct)
}

# TOKEN_NAME: (flag, callable[children -> Element])
higher_rest_of_lines = {
    "ACROSTIC_HEADING": ("qa", OtherText.Kind.acrostic_heading.construct),
    "DESCRIPTIVE_TITLE": ("d", OtherText.Kind.explanatory.construct),
    "EXPLANATORY": ("iex", OtherText.Kind.explanatory.construct),
    "SPEAKER_ID": ("sp", OtherText.Kind.speaker_id.construct),
}

# TOKEN_NAME: flag
ignore_rest_of_lines = {
    "FILE_ID": "id",
    "ENCODING": "ide",
    "STATUS": "sts",
    "REM_TEXT": "rem_text",
}

# TOKEN_NAME: (flag, callable[children -> Element])
lower_until_next_flags = {
    # footnotes
    "FOOTNOTE_ALT_QUOTATION": ("fqa", FormattedText.Kind.footnote_alternate_quotation.construct),
    "FOOTNOTE_KEYWORD": ("fk", FormattedText.Kind.footnote_keyword.construct),
    "FOOTNOTE_TEXT": ("ft", FormattedText.Kind.no_effect.construct),
    "FOOTNOTE_QUOTATION": ("fq", FormattedText.Kind.footnote_quotation.construct),
    "FOOTNOTE_REFERENCE": ("fr", FormattedText.Kind.footnote_reference.construct),
    "FOOTNOTE_VERSE": ("fv", FormattedText.Kind.footnote_verse.construct),

    # cross-references
    "CROSS_REF_ORIGIN": ("xo", FormattedText.Kind.footnote_origin.construct),
    "CROSS_REF_KEYWORD": ("xk", FormattedText.Kind.footnote_keyword.construct),
    "CROSS_REF_QUOTATION": ("xq", FormattedText.Kind.footnote_quotation.construct)
}

# TOKEN_NAME: (flag, Footnote.Kind)
footnotes = {
    "FOOTNOTE": ("f", Footnote.Kind.footnote),
    "ENDNOTE": ("fe", Footnote.Kind.endnote),
    "CROSS_REFERENCE": ("x", Footnote.Kind.cross_reference)
}


# TOKEN_NAME: (flag, Whitespace.Kind)
whitespace = {
    "BLANK_LINE": ("b", Whitespace.Kind.new_line),
    "INTRO_BLANK_LINE": ("ib", Whitespace.Kind.new_line),
    "PAGE_BREAK": ("pb", Whitespace.Kind.page_break)
}
