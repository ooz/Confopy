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
    def __init__(self, ID=u"introduction", language=u"de", brief=u"Kapiteleinleitungen", description=u"Kapitel müssen eine Einleitung haben"):
        super(IntroductionRule, self).__init__(ID, language, brief, description)

    def evaluate(self, node):
        return not is_chapter(node) or has_introduction(node)

    def message(self, node):
        return u"Kapitel \"%s\" hat keine Einleitung!" % node.title

Analyzer.register(IntroductionRule())


class SubsectionRule(Rule):
    """Sections must have at least 2 subsections or none at all.
    """
    def __init__(self, ID=u"subsections", language=u"de", brief=u"Mind. 2 Unterabschnitte", description=u"Sektionen haben entweder 2 oder keine Untersektionen"):
        super(SubsectionRule, self).__init__(ID, language, brief, description)

    def evaluate(self, node):
        return not (is_section(node) and count_subsections(node) > 0) or (count_subsections(node) >= 2)

    def message(self, node):
        return u"Abschnitt \"%s\" hat nur einen Unterabschnitt!" % node.title

Analyzer.register(SubsectionRule())


class FloatReferenceRule(Rule):
    """Floating objects must be referenced in the surrounding text.
    """
    def __init__(self, ID=u"floatreference", language=u"de", brief=u"Gleitobjekte-Referenzen", description=u"Gleitobjekte müssen in den umliegenden Paragraphen referenziert werden"):
        super(FloatReferenceRule, self).__init__(ID, language, brief, description)

    def evaluate(self, node):
        return not is_float(node) or is_referenced(node)

    def message(self, node):
        return u"Gleitobjekt \"%s\" wird nicht im Text referenziert!" % node.text.strip()

Analyzer.register(FloatReferenceRule())


class FloatCaptionRule(Rule):
    """Floating objects must have a caption.
    """
    def __init__(self, ID=u"floatcaption", language=u"de", brief=u"Gleitobjekte-Beschriftung", description=u"Gleitobjekte müssen beschriftet sein"):
        super(FloatCaptionRule, self).__init__(ID, language, brief, description)

    def evaluate(self, node):
        return not is_float(node) or has_caption(node)

    def message(self, node):
        return u"Gleitobjekt \"%s\" hat keine Beschriftung!" % node.text.strip()

Analyzer.register(FloatCaptionRule())
