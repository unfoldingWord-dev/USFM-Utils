"""
Various constants and utility functions for lexing
"""

import re

from usfm_utils.usfm.tokens import Token

UNESCAPED_FLAG_PREFIX = "$"
FLAG_PREFIX = re.escape(UNESCAPED_FLAG_PREFIX)

WHITESPACE = " \r\t\n"


def make_flag(flag, boundary=True):
    """
    A regex-compatible USFM flag
    :param str flag: flag of USFM marker (i.e. "v" for verse numbers)
    :param bool boundary: whether returned regex should assert that the flag doesn't
    occur inside a larger word
    :rtype: str
    """
    assert(isinstance(flag, str) or isinstance(flag, unicode))
    bound = r"\b" if boundary else ""
    return r"{prefix}{flag}{b}".format(prefix=FLAG_PREFIX, flag=flag, b=bound)


def thunk(regex):
    """
    :param str regex: regular expression for
    """
    def regex_inner(token):
        token.value = Token.Builder(token.value)
        # raise AssertionError()
        return token
    regex_inner.__doc__ = regex
    return regex_inner


def standalone(flag):
    return thunk(make_flag(flag))


def one_arg_regex(flag):
    return r"{flag}\s+[^{prefix}\s]+".format(flag=make_flag(flag), prefix=FLAG_PREFIX)


def one_arg(flag):
    def one_arg_inner(token):
        token.value = Token.Builder(token.value.split()[1])
        return token
    one_arg_inner.__doc__ = one_arg_regex(flag)
    return one_arg_inner


def open_token_regex(flag):
    return r"{flag}[^\*]".format(flag=make_flag(flag))


def open_token(flag):
    return thunk(open_token_regex(flag))


def close_token_regex(flag):
    return r"{flag}\*".format(flag=make_flag(flag))


def close_token(flag):
    return thunk(close_token_regex(flag))


def rest_of_line(flag):
    def rest_of_line_inner(token):
        line = token.value[:-1]  # ignore newline
        token.value = Token.Builder(drop_first_word(line))
        return token
    rest_of_line_inner.__doc__ = r"{flag}(\s[^\n]*)?\n".format(flag=make_flag(flag))
    return rest_of_line_inner


def until_next_flag(flag):
    def until_next_flag_inner(token):
        text = token.value
        token.value = Token.Builder(drop_first_word(text))
        return token
    until_next_flag_inner.__doc__ = r"{flag}\s[^{prefix}]*".format(flag=make_flag(flag), prefix=FLAG_PREFIX)
    return until_next_flag_inner


def drop_first_word(line):
    """
    :param str line:
    :rtype: str
    """
    match = re.match(r"[^\s]*[\s]*", line)
    if match is None:
        msg = "Could not drop first word from {}".format(repr(line))
        raise ValueError(msg)
    return line[match.end():]


def scale(flag):
    def scale_inner(token):
        text = token.value
        match = re.search(r"[0-9]*$", text)
        if match is None:
            raise ValueError("Malformatted input: {}".format(token.value))
        number_str = match.group()
        number = 1 if len(number_str) == 0 else int(number_str)
        token.value = Token.Builder(text).set_number(number)
        return token
    scale_inner.__doc__ = r"{flag}[0-9]*\b".format(flag=make_flag(flag, boundary=False))
    return scale_inner


def scale_and_rest_of_line(flag):
    def scale_and_rest_of_line_inner(token):
        line = token.value[:-1]
        rgx = r"{flag}([0-9]+)".format(flag=make_flag(flag, boundary=False))
        number_match = re.match(rgx, line)
        if number_match is None:
            number = 1
        else:
            number = int(number_match.group(1))
        rest = drop_first_word(line)
        token.value = Token.Builder(rest).set_number(number)
        return token
    scale_and_rest_of_line_inner.__doc__ = r"{flag}[0-9]*([ \r\t][^\n]*)?\n"\
        .format(flag=make_flag(flag, boundary=False))
    return scale_and_rest_of_line_inner
