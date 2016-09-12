from __future__ import unicode_literals

import itertools

import ply.lex as lex

from usfm_utils.elements.footnote_utils import AutomaticFootnoteLabel, \
    NoFootnoteLabel, CustomFootnoteLabel
from usfm_utils.usfm.escape_text import escape_text, unescape_text
from usfm_utils.usfm.flags import paragraphs, indented_paragraphs, \
    lower_open_closes, higher_open_closes, headings, one_word_arguments, \
    higher_rest_of_lines, lower_until_next_flags, whitespace, ignore_rest_of_lines, \
    footnotes
from usfm_utils.usfm.lex_utils import standalone, open_token, close_token, one_arg, \
    until_next_flag, rest_of_line, open_token_regex, FLAG_PREFIX, scale, \
    scale_and_rest_of_line
from usfm_utils.usfm.tokens import Position, Token
from usfm_utils.usfm.usfm_error import UsfmInputError

# TODO
# unimplemented USFM tags:
# - tables
# - images


class UpdateablePosition(object):
    def __init__(self, index_from=1):
        self._line = index_from
        self._col = index_from
        self._index_from = index_from

    @property
    def position(self):
        return Position(self._line, self._col)

    def update(self, text):
        for char in text:
            if char == "\n":
                self._line += 1
                self._col = self._index_from
            else:
                self._col += 1


def lex_open_footnote(flag):
    def lex_open_footnote_inner(token):
        token.value = Token.Builder(token.value)
        token.lexer.begin("footnotelabel")
        return token
    lex_open_footnote_inner.__doc__ = open_token_regex(flag)
    return lex_open_footnote_inner


class UsfmLexer(object):
    states = (("footnotelabel", "exclusive"),)

    def __init__(self):
        self.token_list = ["EOF"]
        self.tokens = None
        self.pos = UpdateablePosition()
        self.lexer = None

        self.reached_eof = False

    @staticmethod
    def create():
        """
        Factory method for constructing new instances. Should be used instead of
        "normal" initialization
        """
        usfm_lexer = UsfmLexer()
        usfm_lexer.init()
        return usfm_lexer

    def register(self, name, func, state=None, discard=False):
        """
        "Registers" a lexical rule so that PLY will recognize it
        :param str|unicode name: name of token
        :param callable func: lexical rule to register
        :param str|unicode state: lexer state to which the rule applies
        :param bool discard: if token should be discarded
        """
        def register_helper(this, token):  # this to avoid collision with self
            s = token.value
            if func(token) is None:
                this.pos.update(s)
                return
            token.value = token.value.build(this.pos.position)
            this.pos.update(s)
            if not discard:
                return token
        register_helper.__doc__ = func.__doc__
        qualified_name = name if state is None else "{}_{}".format(state, name)
        setattr(UsfmLexer, "t_" + qualified_name, register_helper)
        self.token_list.append(name)

    def init(self):
        """
        Initialize the lexer, adding rules for PLY
        """
        if self.tokens is not None:
            return
        self.register("TEXT", self.t_text)

        for name, (flag, _) in paragraphs.items():
            self.register(name, standalone(flag))

        for name, (flag, _) in indented_paragraphs.items():
            self.register(name, scale(flag))

        for name, (flag, _) in headings.items():
            self.register(name, scale_and_rest_of_line(flag))

        for name, (flag, _) in one_word_arguments.items():
            self.register(name, one_arg(flag))

        for name, (flag, _) in itertools.chain(lower_open_closes.items(),
                                               higher_open_closes.items()):
            self.register("OPEN_" + name, open_token(flag))
            self.register("CLOSE_" + name, close_token(flag))

        for name, (flag, _) in higher_rest_of_lines.items():
            self.register(name, rest_of_line(flag))

        for name, flag in ignore_rest_of_lines.items():
            self.register(name, rest_of_line(flag), discard=True)

        for name, (flag, _) in lower_until_next_flags.items():
            self.register(name, until_next_flag(flag))

        for name, (flag, _) in footnotes.items():
            self.register("OPEN_" + name, lex_open_footnote(flag))
            self.register("CLOSE_" + name, close_token(flag))

        def footnote_label(token):
            marker = token.value
            if marker == "+":
                token.value = Token.Builder(AutomaticFootnoteLabel())
            elif marker == "-":
                token.value = Token.Builder(NoFootnoteLabel())
            else:
                token.value = Token.Builder(CustomFootnoteLabel(marker))

            token.lexer.begin("INITIAL")
            return token
        footnote_label.__doc__ = r"[^\s{prefix}]+".format(prefix=FLAG_PREFIX)
        self.register("FOOTNOTE_LABEL", footnote_label, "footnotelabel")

        for name, (flag, _) in whitespace.items():
            self.register(name, standalone(flag))

        self.register("CHAPTER_LABEL", rest_of_line("cl"))

        self.tokens = tuple(self.token_list)

        self.lexer = lex.lex(module=self)

    def t_text(self, token):
        text = token.value
        if len(text.strip()) == 0:
            return  # ignore text that is purely whitespace
        token.value = Token.Builder(text)
        return token
    t_text.__doc__ = r"[^\{prefix}]+".format(prefix=FLAG_PREFIX)

    def t_error(self, token):
        text = token.value
        newline_index = text.find("\n")
        max_index = 80 if newline_index < -1 or newline_index > 80 else newline_index
        text_to_display = "\"{}\"".format(unescape_text(text[:max_index]))
        raise UsfmInputError("Unrecognized token: {}".format(text_to_display),
                             self.pos.position)

    def t_footnotelabel_error(self, token):
        raise UsfmInputError("Expected a footnote label", self.pos.position)

    def t_whitespace(self, t):
        r"""[ \t\r\n]+"""
        pass

    t_footnotelabel_whitespace = t_whitespace

    def t_eof(self, token):
        if not self.reached_eof:
            token.value = Token(self.pos.position, None)
            token.type = "EOF"
            self.reached_eof = True
            return token

    def input(self, s):
        self.lexer.begin("INITIAL")
        self.reached_eof = False
        self.pos = UpdateablePosition()
        s = escape_text(s)
        if s[-1] != "\n":
            s += "\n"
        self.lexer.input(s)

    def token(self):
        token = self.lexer.token()
        return token

    def get_tokens(self):
        return self.tokens

lexer = UsfmLexer.create()
tokens = lexer.get_tokens()  # a "tokens" global variable for parse.py
