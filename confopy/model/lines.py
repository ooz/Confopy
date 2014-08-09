# coding: utf-8
'''
File: lines.py
Author: Oliver Zscheyge
Description:
    Utility methods to handle lines (list of unicode strings).
'''

import operator
import re

def lines2unicode(lines=[], strip=False, sep=u"\n"):
    """Converts a list of strings to a single unicode string.
    Args:
        lines: The list of unicode strings to convert.
        strip: Boolean. Strip the lines and the resulting string?
        sep:   Line separator.
    Return:
        A single unicode string.
    """
    if strip:
        return reduce(lambda a, b: a.strip() + sep + b.strip(), lines, u"").strip()
    return reduce(lambda a, b: a + sep + b, lines, u"")

def is_empty(lines):
    """Checks whether a list of ustrings is empty.
    Return:
        True if list is empty or contains whitespace strings only.
        False otherwise.
    """
    if lines == [] or lines2unicode(lines).strip() == u"":
        return True
    return False

def match(regex, lines, strip=False):
    """Applies TODO"""
    return re.match(regex, lines2unicode(lines, strip), re.U)

def match_each(regex, lines, strip=False):
    """Returns true if regex matches for each line."""
    for line in lines:
        if strip:
            line = line.strip()
        if not re.match(regex, line, re.U):
            return False

    if lines == [] and regex != r"":
        return False
    return True

def lines_using(lines, words, strip=False, sep=u" "):
    """ lines_using
    Return:
        The number of lines from the beginning being fully and only
        composed by words from parameter words.
    """
    line_count = 0
    for line in lines:
        if strip:
            line = line.strip()
        if line != u"":
            line_words = line.split(sep)
            for word in [w for w in line_words if w != u""]:
                if word not in words:
                    return line_count
            line_count += 1
    return line_count

def words_using(lines, words, strip=False, sep=u" "):
    """
    Return:
        The number of consecutive words from the beginning that are
        contained in the parameter words.
    """
    word_count = 0
    for line in lines:
        if strip:
            line = line.strip()
        if line != u"":
            line_words = line.split(sep)
            for word in [w for w in line_words if w != u""]:
                if word not in words:
                    return word_count
                word_count += 1
    return word_count

def avg_word_length(lines):
    words = lines2unicode(lines, True, u" ").split()
    wc = 0.0
    wl = 0.0
    for w in words:
        w = w.strip()
        wl += len(w)
        if w != u"":
            wc += 1
    if wc > 0.0:
        return wl / wc
    return 0.0

def avg_words_per_line(lines):
    if len(lines) > 0:
        return reduce(operator.add, map(lambda line: len(line.split()), lines), 0) / float(len(lines))
    return 0.0




if __name__ == '__main__':
    """lines.py test"""
    l0 = []
    l1 = [u"Hello World!"]
    l2 = [u"Hello World,", u"how are you?", u"Sincerely", u"Universe"]
    l3 = [u"    ", u"\n", u""]

    print lines2unicode(l0)
    print lines2unicode(l1)
    print lines2unicode(l2)

    assert is_empty(l0)
    assert is_empty(l3)
    assert not is_empty(l1)
    assert not is_empty(l2)

    h0 = [u"     42", u" The Meaning of Life and Everything"]
    assert match(r"\d+", h0, True)
    print lines2unicode(h0, True)

    l4 = [u"x     2  ", u"  yz xz"]
    assert avg_word_length(l4) == 1.5
