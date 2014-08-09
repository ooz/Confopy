# coding: utf-8
'''
File: rules.py
Author: Oliver Zscheyge
Description:
    Rules governing structural properties of scientific texts.
'''

from confopy.analysis.rule import *
from confopy.analysis import Analyzer



class IntroductionRule(Rule):
    """Chapters must have introductions.
    """
    def __init__(self, ID=u"introduction", language=u"de", brief=u"Kapiteleinleitungen", description=u"Kapitel müssen eine Einleitung haben", kind=RuleKind.SECTION):
        super(IntroductionRule, self).__init__(ID, language, brief, description, kind)

    def evaluate(self, node):
        return not is_chapter(node) or has_introduction(node)

    def message(self, node):
        return u"Kapitel \"%s\" hat keine Einleitung!" % node.title

Analyzer.register(IntroductionRule())


class SubsectionRule(Rule):
    """Sections must have at least 2 subsections or none at all.
    """
    def __init__(self, ID=u"subsections", language=u"de", brief=u"Mind. 2 Unterabschnitte", description=u"Sektionen haben entweder 2 oder keine Untersektionen", kind=RuleKind.SECTION):
        super(SubsectionRule, self).__init__(ID, language, brief, description, kind)

    def evaluate(self, node):
        return not (count_subsections(node) > 0) or (count_subsections(node) >= 2)

    def message(self, node):
        return u"Abschnitt \"%s\" hat nur einen Unterabschnitt!" % node.title

Analyzer.register(SubsectionRule())


class FloatReferenceRule(Rule):
    """Floating objects must be referenced in the surrounding text.
    """
    def __init__(self, ID=u"floatreference", language=u"de", brief=u"Gleitobjekte-Referenzen", description=u"Gleitobjekte müssen in den umliegenden Paragraphen referenziert werden", kind=RuleKind.FLOAT):
        super(FloatReferenceRule, self).__init__(ID, language, brief, description, kind)

    def evaluate(self, node):
        return is_referenced(node)

    def message(self, node):
        return u"Gleitobjekt \"%s\" wird nicht im Text referenziert!" % node.text.strip()

Analyzer.register(FloatReferenceRule())

#class MF(object):
#    """docstring for MF"""
#
#    PAGE = u""
#    SECTION = u""
#    SENTENCE = u""
#
#    def __init__(self, arg):
#        super(MF, self).__init__()
#        self.arg = arg
#
#
#RULES = [
#  Rule( "Foo"
#      , "Bar"
#      , Scope.UNSPECIFIED
#      , lambda doc, sec, par, sen:
#            (not 1 == 2) or (False)
#      )
#
#, Rule( "Template"
#      , "Template message"
#      , 0
#      , lambda doc, sec, par, sen:
#            (not False) or ()
#      )
#
#, Rule( "Subsections"
#      , "Section %s has only one subsection or/and lacks an introduction." % MF.SECTION
#      , Scope.SECTION | Scope.FORM
#      , lambda doc, sec, par, sen:
#            (not sec.count_subsections() > 0) or (sec.count_subsections() >= 2 and sec.has_introduction())
#      )
#
#, Rule( "Fillers"
#      , "Page %s: The sentence \"%s\" contains fillers." % (MF.PAGE, MF.SENTENCE)
#      , Scope.SENTENCE | Scope.LANGUAGE
#      , lambda doc, sec, par, sen:
#            (not sen.has_filler())
#      )
#
#, Rule( "Dead Verbs"
#      , "Page %s: The sentence \"%s\" contains dead verbs." % (MF.PAGE, MF.SENTENCE)
#      , Scope.SENTENCE | Scope.LANGUAGE
#      , lambda doc, sec, par, sen:
#            (not sen.has_dead_verbs())
#      )
#
#, Rule( "Boosting Adverbs"
#      , "Page %s: The sentence \"%s\" contains boosting adverbs." % (MF.PAGE, MF.SENTENCE)
#      , Scope.SENTENCE | Scope.LANGUAGE
#      , lambda doc, sec, par, sen:
#            (not sen.has_boosting_adverbs())
#      )
#
#, Rule( "Redundancies and Tautologies"
#      , "Page %s: The sentence \"%s\" contains a redundancy or tautology." % (MF.PAGE, MF.SENTENCE)
#      , Scope.SENTENCE | Scope.LANGUAGE
#      , lambda doc, sec, par, sen:
#            (not sen.has_redundancy()) and (not sen.has_tautology())
#      )
#]
