# coding: utf-8
'''
File: spellcheck.py
Author: Oliver Zscheyge
Description:
    Wrapper for PyEnchant.
'''

import enchant as e
import confopy.config as C

ENCHANT_LANG_MAP = {
      u"de": u"de_DE"
    , u"en": u"en"
}

def list_languages():
    pyenchant_langs = e.list_languages()
    supported_langs = list()
    for l in ENCHANT_LANG_MAP:
        pyel = ENCHANT_LANG_MAP[l]
        if pyel in pyenchant_langs:
            supported_langs.append(l)
    return supported_langs


class SpellChecker(object):
    """Wrapper for PyEnchant.
    """
    def __init__(self, lang=C.DEFAULT_LANG):
        """Initializes a spellchecker with a given language.
        Args:
            lang: Language code, e.g. u"de" or u"en", for the spellchecker.
        """
        super(SpellChecker, self).__init__()
        pyenchant_lang = ENCHANT_LANG_MAP.get(lang, u"de_DE")
        self._enchant_dict = e.Dict(pyenchant_lang)

    def check(self, word):
        """Checks a given word.
        Args:
            word: A unicode string.
        Return:
            Boolean. True if word is spelled correctly.
        """
        return self._enchant_dict.check(word)

    def suggest(self, word):
        return self._enchant_dict.suggest(word)


if __name__ == '__main__':
    print u"Test for %s" % __file__

    print u"  Testing SpellChecker..."
    checker = SpellChecker(u"de")
    word_de = u"Hallo"
    word_en = u"Hello"
    assert checker.check(word_de)
    assert not checker.check(word_en)
    assert len(checker.suggest(word_en)) == 6

    print u"  Testing list_languages..."
    assert list_languages() == [u"de", u"en"]

    print u"Passed all tests!"
