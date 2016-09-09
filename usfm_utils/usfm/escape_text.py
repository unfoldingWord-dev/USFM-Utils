

from usfm_utils.usfm.lex_utils import UNESCAPED_FLAG_PREFIX


def escape_text(text):
    """
    :param str text:
    :rtype: str
    """
    return text.replace("\\", UNESCAPED_FLAG_PREFIX)


def unescape_text(text):
    """
    :param str text:
    :rtype: str
    """
    return text.replace(UNESCAPED_FLAG_PREFIX, "\\")
