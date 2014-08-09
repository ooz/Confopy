# coding: utf-8

from confopy.analysis import Analyzer
from confopy.localization.de.corpus_de import TigerCorpusReader

Analyzer.register(TigerCorpusReader(cache=False))
