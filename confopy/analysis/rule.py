# coding: utf-8
'''
File: rule.py
Author: Oliver Zscheyge
Description:
    Rule superclass.
'''

from localizable import Localizable
from confopy.model.document import *



class Rule(Localizable):
    """Base class to describe rule based knowledge.
    """
    def __init__(self, ID=u"", language=u"", brief=u"", description=u""):
        """Initializer.
        """
        super(Rule, self).__init__(ID, language, brief, description)

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

def is_section(node):
    return isinstance(node, Section)

def is_float(node):
    return node.is_float()

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
        flt_text = flt.text.strip().split(u" ")
        if len(flt_text) >= 2:
            flt_text = flt_text[0].strip() + u" " + flt_text[1].strip()
            flt_text = flt_text.replace(u":", u"")
            return flt_text in para_texts

    return False

FLT_CAPTION_MIN_SIZE = 3
FLT_CAPTION_NR_SIZE = 2
def has_caption(flt):
    flt_text = flt.text.strip().replace(u"\n", u" ").split(u" ")
    if flt.number != u"":
        return len(flt_text) >= FLT_CAPTION_MIN_SIZE
    return len(flt_text) >= FLT_CAPTION_MIN_SIZE + FLT_CAPTION_NR_SIZE



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
    for rule in rules:
        if not rule.evaluate(document):
            messages.append(rule.message(document))

    children = document.children()
    for child in children:
        messages = messages + eval_doc(child, rules)

    return messages



if __name__ == '__main__':
    print "Demo for " + __file__
    assert False, "woah, this isnt implemented yet!"
