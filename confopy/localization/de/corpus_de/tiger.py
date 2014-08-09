#!/usr/bin/python
# coding: utf-8
'''
File: tiger.py
Author: Oliver Zscheyge
Description:
    Access the TIGER corpus with NLTK.

    Implementation based on (section "Loading your own Corpus"):

        http://nltk.org/book/ch02.html
'''

import os.path as op
from cPickle import dump, load
from lxml import etree

import nltk
from nltk.corpus.reader.api import CorpusReader
from nltk.corpus import BracketParseCorpusReader
from nltk.grammar import ContextFreeGrammar, Nonterminal, induce_pcfg
from nltk.tokenize.punkt import PunktTrainer, PunktSentenceTokenizer

from confopy.analysis.corpus import Corpus
import confopy.config as C
from fillers_de import FILLERS_DE

class _Terminal(object):
    """docstring for _Terminal"""
    def __init__(self, t_node):
        super(_Terminal, self).__init__()
        self.ID     = unicode(t_node.get(u"id")    )
        self.word   = unicode(t_node.get(u"word")  )
        self.lemma  = unicode(t_node.get(u"lemma") )
        self.pos    = unicode(t_node.get(u"pos")   )
        self.morph  = unicode(t_node.get(u"morph") )
        self.case   = unicode(t_node.get(u"case")  )
        self.number = unicode(t_node.get(u"number"))
        self.gender = unicode(t_node.get(u"gender"))
        self.person = unicode(t_node.get(u"person"))
        #self.degree = unicode(t_node.get(u"degree"))
        self.tense  = unicode(t_node.get(u"tense") )
        self.mood   = unicode(t_node.get(u"mood")  )

class _NonTerminal(object):
    """docstring for _NonTerminal"""
    def __init__(self, nt_node):
        super(_NonTerminal, self).__init__()
        self.ID  = unicode(nt_node.get(u"id") )
        self.cat = unicode(nt_node.get(u"cat"))
        self.edges = list()
        for e in nt_node.iter(u"edge"):
            self.edges.append((unicode(e.get(u"label")), unicode(e.get(u"idref"))))



class _TigerSentence(object):
    """Helper class for TigerCorpusReader
    Methods are based on nltk.corpus method, but only apply to a single sentence.
    """
    def __init__(self, sent_node):
        super(_TigerSentence, self).__init__()
        self.ID = sent_node.get(u"id")
        self.terminals = list()
        term_ids = set()
        for term in sent_node.iter(u"t"):
            _term = _Terminal(term)
            self.terminals.append(_term)
            term_ids.add(_term.ID)
        self.non_terminals = list()
        self.edges = dict()
        for nonterm in sent_node.iter(u"nt"):
            _nt = _NonTerminal(nonterm)
            for e in _nt.edges:
                if e[1] in term_ids:
                    self.edges[e[1]] = e[0]
            self.non_terminals.append(_nt)

    def words(self):
        buf = list()
        for terminal in self.terminals:
            buf.append(terminal.word)
        return buf

    def tagged_words(self, include_edgelabels=True):
        buf = list()
        for term in self.terminals:
            elabel = self.edges.get(term.ID, u"")
            tag = term.pos
            if include_edgelabels and elabel not in [u"", u"--"]:
                tag = u"%s-%s" % (tag, elabel)
            buf.append((term.word, tag))
        return buf

    def parsed(self, include_edgelabels=True):
        vroot = None
        nodes = dict()
        for t in self.terminals:
            nodes[t.ID] = t
        for nt in self.non_terminals:
            nodes[nt.ID] = nt
            if nt.cat == u"VROOT":
                vroot = nt
        if vroot is not None:
            return self._conv_etree2tree(vroot, nodes, include_edgelabels=include_edgelabels)
        return nltk.Tree(u"", [])

    def _conv_etree2tree(self, node, nodes, label=u"", include_edgelabels=True):
        if type(node) == _Terminal:
            pos = node.pos
            if include_edgelabels and label not in [u"", u"--"]:
                pos = pos + "-" + label
            return nltk.Tree(pos, [node.word])
        elif type(node) == _NonTerminal:
            cat = node.cat
            children = list()
            for e in node.edges:
                children.append(self._conv_etree2tree(nodes.get(e[1]), nodes, e[0], include_edgelabels))
            return nltk.Tree(cat, children)
        return None

def _cached(obj, filepath, constructor):
    if obj is not None:
        return obj

    new_obj = None
    try:
        with open(filepath, 'rb') as f:
            new_obj = load(f)
    except IOError as e:
        #print u"Cache: couldn't read from %s" % filepath
        #print unicode(e)
        pass
    if new_obj is None:
        new_obj = constructor()
        try:
            with open(filepath, 'wb') as f:
                dump(new_obj, f, -1)
        except IOError as e:
            #print u"Cache: couldn't write to %s" % filepath
            #print unicode(e)
            pass
    return new_obj


class TigerCorpusReader(Corpus):
    """Reads TIGER Corpus from XML file in Negra Format, Version 4.
    Parses the XML in a memory efficient fashion based on:
        http://www.ibm.com/developerworks/opensource/library/x-hiperfparse/index.html
    """

    STORAGE_ROOT = op.dirname(op.realpath(__file__))
    CORPUS_FILE = u"_tiger_corpus.pkl"
    TAGGER_FILE = u"_tiger_tagger.pkl"

    SENTS_FILE_SUFFIX = u"_sents.pkl"
    PCFG_FILE_SUFFIX  = u"_pcfg.pkl"
    PCFG_PARSER_FILE_SUFFIX = u"_pcfg_parser.pkl"
    SENT_TOKENIZER_FILE_SUFFIX = u"_sent_tkzr.pkl"

    GRAMMAR_START = u"VROOT"
    FEATURE_SEP = u"-"
    NO_VALUE = u"_"

    def __init__(self, tigerfile=None, cache=False):
        super(TigerCorpusReader, self).__init__(ID=u"TIGER", language=u"de", brief=u"TIGER Treebank v2.2", description=u"TIGER deutscher Corpus")
        self._tagger = None
        self._pcfg = None
        self._pcfg_parser = None
        self._sent_tokenizer = None
        self._tigerfile = tigerfile
        if self._tigerfile is None:
            #self._tigerfile = TigerCorpusReader.STORAGE_ROOT + u"/tiger_corpus/tiger_release_aug07.corrected.16012013_utf8_patched_half.xml"
            self._tigerfile = TigerCorpusReader.STORAGE_ROOT + u"/" + C.CORPUS_FILES.get(u"de", u"")
        self.tiger_sents = None
        if cache:
            try:
                with open(self._tigerfile + TigerCorpusReader.SENTS_FILE_SUFFIX, 'rb') as f:
                    self.tiger_sents = load(f)
            except IOError:
                self.tiger_sents = None
        if self.tiger_sents is None:
            try:
                context = etree.iterparse(self._tigerfile, events=("end",), tag=u"s", encoding=u"utf-8")
                self.tiger_sents = self._fast_iter(context, self._sent_func)
                if cache:
                    try:
                        with open(self._tigerfile + TigerCorpusReader.SENTS_FILE_SUFFIX, 'wb') as f:
                            dump(self.tiger_sents, f, -1)
                    except IOError:
                        self.tiger_sents = []
                        print u"Could not cache TIGER sentences to %s%s" % (self._tigerfile, TigerCorpusReader.SENTS_FILE_SUFFIX)
            except IOError:
                print u"Error: TIGER corpus file not found. Please follow README to download and place it properly."
                print u"       (A file named " + C.CORPUS_FILES.get(u"de", u"")
                print u"        needs to be placed here: " + TigerCorpusReader.STORAGE_ROOT + u")"
                import sys
                sys.exit(1)

    def _fast_iter(self, context, func):
        buf = list()
        for event, elem in context:
            buf.append(func(elem))
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
        del context
        return buf

    def _sent_func(self, sent):
        return _TigerSentence(sent)

    def words(self, recursive=True, tokenizer=None):
        buf = list()
        for s in self.tiger_sents:
            buf.extend(s.words())
        return buf

    def sents(self, recursive=True, tokenizer=None):
        return [s.words() for s in self.tiger_sents]

    def paras(self):
        return [self.sents()]

    def tagged_words(self, include_edgelabels=True):
        buf = list()
        for s in self.tiger_sents:
            buf.extend(s.tagged_words(include_edgelabels))
        return buf

    def tagged_sents(self, include_edgelabels=True):
        return [s.tagged_words(include_edgelabels) for s in self.tiger_sents]

    def tagged_paras(self, include_edgelabels=True):
        return [self.tagged_sents(include_edgelabels)]

    def parsed_sents(self, include_edgelabels=True):
        return [s.parsed(include_edgelabels) for s in self.tiger_sents]

    def parsed_paras(self, include_edgelabels=True):
        return [self.parsed_sents(include_edgelabels)]

    def xml(self):
        return u""

    def raw(self):
        return u""

    def tagger(self, include_edgelabels=True):
        """Creates a tagger from the TIGER Corpus.
        Depending on the corpus size, this can be a lengthy process.
        To speed up subsequent calls, the tagger is dumped to TAGGER_FILE in
        STORAGE_ROOT at the first call and only loaded for all following calls.
        Return:
            A nltk tagger for the TIGER Corpus.
        """
        if self._tagger:
            return self._tagger

        def constructor():
            tagged_sents = self.tagged_sents(include_edgelabels)
            unigram_tagger = nltk.UnigramTagger(tagged_sents)
            bigram_tagger = nltk.BigramTagger(tagged_sents, backoff=unigram_tagger)
            return bigram_tagger

        self._tagger = _cached(self._tagger, TigerCorpusReader.STORAGE_ROOT + u"/" + TigerCorpusReader.TAGGER_FILE, constructor)
        return self._tagger

    def pcfg(self, include_edgelabels=True):
        sents = self.parsed_sents(include_edgelabels)
        tiger_prods = set(prod for sent in sents for prod in sent.productions())
        pcfg = induce_pcfg(Nonterminal(TigerCorpusReader.GRAMMAR_START), list(tiger_prods))
        return pcfg

    def cfg(self, include_edgelabels=True):
        sents = self.parsed_sents(include_edgelabels)
        tiger_prods = set(prod for sent in sents for prod in sent.productions())
        cfg = ContextFreeGrammar(Nonterminal(TigerCorpusReader.GRAMMAR_START), list(tiger_prods))
        return cfg

    def parser(self, include_edgelabels=True):
        return self.viterbi_parser(include_edgelabels)

    def viterbi_parser(self, include_edgelabels=True):
        if self._pcfg_parser is not None:
            return self._pcfg_parser

        def constructor():
            return self.pcfg(include_edgelabels)

        self._pcfg = _cached(self._pcfg, TigerCorpusReader.STORAGE_ROOT + u"/" + TigerCorpusReader.PCFG_FILE_SUFFIX, constructor)
        self._pcfg_parser = nltk.ViterbiParser(self._pcfg)
        return self._pcfg_parser

    def sent_tokenizer(self):
        if self._sent_tokenizer is not None:
            return self._sent_tokenizer

        def constructor():
            trainer = PunktTrainer()
            trainer.INCLUDE_ALL_COLLOCS = True
            trainer.INCLUDE_ABBREV_COLLOCS = True
            trainer.train_tokens(self.words())
            params = trainer.get_params()
            return PunktSentenceTokenizer(params)

        self._sent_tokenizer = _cached(self._sent_tokenizer, TigerCorpusReader.STORAGE_ROOT + u"/" + TigerCorpusReader.SENT_TOKENIZER_FILE_SUFFIX, constructor)
        return self._sent_tokenizer

    def fillers(self):
        return FILLERS_DE



CORPUS_PATH = TigerCorpusReader.STORAGE_ROOT + u"/" + TigerCorpusReader.CORPUS_FILE
def test_parse():
    print u"%s: Parse test" % (__file__, )
    print u"Using TIGER corpus to parse a sentence."
    tiger_corpus = _cached(None, CORPUS_PATH, TigerCorpusReader)

    sents = tiger_corpus.parsed_sents()
    print unicode(sents[3])
    #sents[3].draw()

    text = nltk.word_tokenize(u"Der Hase springt über den Baum, der sehr hoch gewachsen ist.")
    tiger_tagger = tiger_corpus.tagger()
    tagged_text = tiger_tagger.tag(text)
    tagged_text_ref = [(u'Der', u'ART-NK'), (u'Hase', u'NN-NK'), (u'springt', u'VVFIN-HD'), (u'\xfcber', u'APPR-AC'), (u'den', u'ART-NK'), (u'Baum', u'NN-NK'), (u',', u'$,'), (u'der', u'PRELS-SB'), (u'sehr', u'ADV-MO'), (u'hoch', u'ADJD-HD'), (u'gewachsen', u'VVPP-HD'), (u'ist', u'VAFIN-HD'), (u'.', u'$.')]
    print tagged_text
    assert tagged_text == tagged_text_ref


#chart_parser = nltk.ChartParser(tiger_grammar)
#chart_parser = nltk.ChartParser(pcfg)
#trees = chart_parser.nbest_parse(text, n=n)
def test_grammar_parse():
    """
    Deriving a CFG from a corpus (parse trees).
    Based on:

        http://stackoverflow.com/questions/7056996/how-do-i-get-a-set-of-grammar-rules-from-penn-treebank-using-python-nltk
    """
    print u"%s: Grammar test" % (__file__, )
    print u"Deriving grammar from parsed TIGER corpus sentences"
    #tiger_corpus = TigerCorpusReader()
    tiger_corpus = _cached(None, CORPUS_PATH, TigerCorpusReader)
    grammar_parser = tiger_corpus.viterbi_parser(False)
    grammar_parser.trace()

    text = nltk.word_tokenize(u"Der Hase springt über den Baum, der sehr hoch gewachsen ist.")
    #text = nltk.word_tokenize(u"Der kleine gelbe Hund beobachtete die Katze.")
    text = nltk.word_tokenize(u"Der kleine Hund blickte zu der Katze.")
    print u"Parsing unknown text"
    try:
        tree = grammar_parser.parse(text)
        if tree:
            tree.draw()
        print u"Printing parse tree for text..."
        print unicode(tree)
    except ValueError as e:
        print u"Input contains words not known by grammar!"
        print u"%s" % e

if __name__ == '__main__':
    test_parse()
    test_grammar_parse()

