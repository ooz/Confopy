# coding: utf-8
'''
File: corpus.py
Author: Oliver Zscheyge
Description:
    Confopy corpus superclass.
'''

from nltk.corpus.reader.api import CorpusReader
from localizable import Localizable
from confopy.model import Document

NO_WORDS = [
      u"."
    , u","
    , u";"
    , u":"
    , u"+"
    , u"/"
    , u"!"
    , u"?"
    , u"("
    , u")"
    , u"["
    , u"]"
    , u"{"
    , u"}"
    , u"-"
    , u"//"
    , u"%"
    , u"\u2013"
    , u"\uf0f1"
]

class Corpus(Localizable, CorpusReader, Document):
    """A corpus is a body of language data.
    """

    def __init__(self, ID, language, brief=u"", description=u""):
        """Initializer.
        Args:
            ID:          ID of the corpus (unicode string).
            language:    Language code, e.g. u"de" or u"en".
            brief:       Brief description of the corpus.
            description: Long/full description of the corpus.
        """
        self.ID = ID
        self.language = language
        self.brief = brief
        self.description = description

    def tagger(self):
        """Returns the POS tagger.
        """
        return None

    def parser(self):
        """Returns the syntax tree parser.
        """
        return None

    def sent_tokenizer(self):
        """Returns the sentence tokenizer.
        """
        return None

    def fillers(self):
        """Returns a list of fill words for the corpus language.
        """
        return list()

