# coding: utf-8
'''
File: metric.py
Author: Oliver Zscheyge
Description:
    Metric superclass implemented by all language specific
    Metrics.
'''

from localizable import Localizable

#import nltk
#
#import nltk_contrib.tiger as tiger
#
#TIGER_XML_PATH = "../contrib/tiger_corpus/tiger_release_aug07.corrected.16012013.xml"
#TIGER_PENN_PATH = "../contrib/tiger1/tiger_release_july03.penn"
#text = u"Der Hase besiegte den blauen Wolf, obwohl dieser größer war.\n\
#Danach war ersterer sehr glücklich."


class Metric(Localizable):
    """Superclass for all Metrics.
    """
    def __init__(self, ID, language, brief=u"", description=u""):
        super(Metric, self).__init__(ID=ID, language=language, brief=brief, description=description)

    def evaluate(self, node):
        return 0.0



#def nltk_test():
#    print "nltk %s" % (nltk.__version__, )
#    tokens = nltk.word_tokenize(text)
#    print tokens
#    nltk_text = nltk.Text(tokens)
#    print nltk_text
#    #tagged_text = nltk.pos_tag(nltk_text)
#
#def tiger_test():
#    corpus = tiger.open_corpus("tiger", TIGER_XML_PATH, False, False)
#    print corpus
#    print "Corpus size: %i graphs. " % (len(corpus, ))
#    terms = corpus.get_graph(1).terminals()
#    for t in terms:
#        print t
#    evaluator = corpus.get_query_evaluator()
#    print evaluator
#    eval_result = evaluator.evaluate('[word="lacht"]')
#    print eval_result
#
#def pattern_test():
#    import pattern.de as de
#    s = de.parse(text, tagset="STTS", lemmata=True, relations=True)
#    de.pprint(s)
#
#    #import pattern.de.wordlist as wl
#    #print wl.ACADEMIC

#if __name__ == '__main__':
    #nltk_test()
    #tiger_test()
    #pattern_test()


