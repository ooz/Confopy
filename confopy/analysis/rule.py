# coding: utf-8
'''
File: rule.py
Author: Oliver Zscheyge
Description:
    Rule superclass.
'''

from localizable import Localizable
from confopy.model.document import *



class RuleKind(object):
    """Kind of a rule.
    Suitable for masking.
    """

    UNSPECIFIED = 0 << 0

    # Scope
    DOCUMENT  = 1 << 0
    SECTION   = 1 << 1
    PARAGRAPH = 1 << 2
    FLOAT     = 1 << 3


class Rule(Localizable):
    """Base class to describe rule based knowledge.
    """
    def __init__(self, ID=u"", language=u"", brief=u"", description=u"", kind=RuleKind.UNSPECIFIED):
        """Initializer.
        """
        super(Rule, self).__init__(ID, language, brief, description)
        self.kind = kind

    def evaluate(self, node):
        """Evaluates the rule on a Node.
        Return:
            Bool whether this Rule is satisfied or not.
        """
        return False

    def message(self):
        return u""

#    def __str__(self):
#        return "Rule(%s, %s, %s)" % (self.ID, self.language, self.brief)
#
#    def __repr__(self):
#        return self.__str__()


# Predicates

def is_chapter(node):
    if isinstance(node, Chapter):
        return True
    elif isinstance(node, Section):
        parent = node.parent
        if parent is not None and isinstance(parent, Document):
            return True
    return False

def has_introduction(node):
    children = node.children
    if len(children) > 0:
        first_child = children[0]
        if isinstance(first_child, Paragraph):
            return True
    return False

def count_subsections(node):
    subsections = [child for child in node.children() if isinstance(child, Section)]
    return len(subsections)

def is_referenced(flt):
    parent = flt.parent()
    if parent is not None:
        siblings = list()
        children = parent.children()
        for child in children:
            if child.is_paragraph():
                siblings.append(child)
        para_texts = [sib.text for sib in siblings]
        para_texts = u"".join(para_texts)

        if flt.number != u"":
            return flt.number in para_texts
        flt_text = flt.text.strip().split(" ")
        if len(flt_text) >= 2:
            flt_text = flt_text[0].strip() + " " + flt_text[1].strip()
            flt_text = flt_text.replace(u":", u"")
            return flt_text in para_texts

    return False


# Utility functions

def eval_doc(document, rules):
    """Evaluates a list of rules on a given document.
    Recursive: can be used for other nodes than Document nodes as well.
    Args:
        document: The Document to check.
        rules:    The rules to evaluate on document.
    Return:
        A list of unicode strings representing the messages
        of violated rules.
    """
    messages = list()

    if isinstance(document, Document):
        doc_rules = [r for r in rules if r.kind == RuleKind.DOCUMENT]
        messages = _eval_rules(document, doc_rules)
        children = document.children()
        for child in children:
            messages = messages + eval_doc(child, rules)

    elif isinstance(document, Section):
        sec_rules = [r for r in rules if r.kind == RuleKind.SECTION]
        messages = messages + _eval_rules(document, sec_rules)
        children = document.children()
        for child in children:
            messages = messages + eval_doc(child, rules)

    elif isinstance(document, Paragraph):
        para_rules = [r for r in rules if r.kind == RuleKind.PARAGRAPH]
        messages = _eval_rules(document, para_rules)

    elif document.is_float():
        float_rules = [r for r in rules if r.kind == RuleKind.FLOAT]
        messages = _eval_rules(document, float_rules)

    return messages

def _eval_rules(node, rules):
    msgs = list()
    for rule in rules:
        if not rule.evaluate(node):
            msgs.append(rule.message(node))
    return msgs


if __name__ == '__main__':
    print "Demo for " + __file__
    assert False, "woah, this isnt implemented yet!"
