# coding: utf-8
'''
File: document.py
Author: Oliver Zscheyge
Description:
    General classes to represent a structured (scientific) document.
'''

from nltk import word_tokenize

##################################################################
# NODE SUPER CLASS
##################################################################

class Node(object):
    """Super class for all document components.
    """

    def __init__(self, text=u"", pagenr=u"", parent=None, children=[]):
        """Initializer.
        Args:
            text:     Unicode text of the node.
            pagenr:   Page number of the textbox in the original document.
            parent:   Parent node.
            children: List of child nodes.
        """
        self.text = text
        self.pagenr = pagenr
        self._parent = parent
        self._children = list(children)
        for c in self._children:
            c._parent = self

    def parent(self):
        return self._parent

    def children(self):
        return self._children

    def is_root(self):
        return self._parent == None

    def is_leaf(self):
        return self._children == []

    def is_section(self):
        return False

    def is_paragraph(self):
        return False

    def is_float(self):
        return False

    def is_footnote(self):
        return False

    def add_child(self, child, relation=1):
        """Adds another child.
        Args:
            child:    The child node to add.
            relation: Optional argument. Describes the hierarchical relation of
                      this node and the child to add.
                      1  - this node is the parent of child (default)
                      0  - this node is a sibling of child. Instead of adding it
                           to this nodes children, child is going to be added to
                           the children of the parent of this node.
                      -1 - child is actually and uncle of this node and is
                           added accordingly.
                      -2 - child is actually the great uncle of this node etc.
        """
        if child:
            if relation == 1:
                child._parent = self
                self._children.append(child)
            elif relation < 1 and self._parent:
                self.parent().add_child(child, relation + 1)

    def remove_child(self, child):
        """Removes a child node.
        """
        if child in self._children:
            child._parent = None
            self._children.remove(child)

    def sections(self):
        """Returns all children being section nodes.
        """
        return [s for s in self._children if s.is_section()]

    def paragraphs(self, recursive=True):
        """Returns all children being paragraph nodes.
        Args:
            recursive: Include paragraph children of child nodes.
        """
        paras = list()
        for c in self._children:
            if c.is_paragraph():
                paras.append(c)
            elif c.is_section() and recursive:
                paras.extend(c.paragraphs(True))
        return paras

    def floats(self, recursive=True):
        """Returns all children being float nodes (floating objects).
        Args:
            recursive: Include float children of child nodes.
        """
        floats = list()
        for c in self._children:
            if c.is_float():
                floats.append(c)
            elif c.is_section() and recursive:
                floats.extend(c.floats(True))
        return floats

    def lines(self, recursive=True, ignore_floats=True):
        """Returns a list of unicode strings (lines).
        Args:
            recursive: Include lines from non-leaf child nodes.
            ignore_floats: Ignore floats and footnotes.
        """
        lines = list()
        for c in self._children:
            if c.is_section() and recursive:
                lines.extend(c.lines(True, ignore_floats))
            elif (c.is_float() or c.is_footnote()) and not ignore_floats:
                lines.extend(c.lines(recursive, False))
            else:
                lines.extend(c.lines(recursive, ignore_floats))
        return lines

    def raw(self, recursive=True, ignore_floats=True):
        """Returns the text of this node as a single unicode string.
        Lines are separated by a newline character.
        Args:
            recursive: Include text from non-leaf child nodes.
            ignore_floats: Ignore floats and footnotes.
        """
        buf = list()
        buf.append(self.text)
        for c in self._children:
            if c.is_section() and recursive:
                buf.append(c.raw(True, ignore_floats))
            elif (c.is_float() or c.is_footnote()) and not ignore_floats:
                buf.append(c.raw(recursive, False))
            else:
                buf.append(c.raw(recursive, ignore_floats))
        return u" ".join(buf)

    def words(self, recursive=True, ignore_floats=True):
        """Returns this node's text as a list of words.
        Args:
            recursive:     Boolean. Include words of child nodes?
            ignore_floats: Boolean. Exclude words of floating object captions?
        Return:
            List of words.
        """
        words = list()
        words.extend(word_tokenize(self.text))
        for c in self._children:
            if c.is_section() and recursive:
                words.extend(c.words(True, ignore_floats))
            elif (c.is_float() or c.is_footnote()) and not ignore_floats:
                words.extend(c.words(recursive, False))
            else:
                words.extend(c.words(recursive, ignore_floats))
        return words

    def sents(self, recursive=True, ignore_floats=True, tokenizer=None):
        """Returns this node's text as a list of sentences
        Args:
            recursive:     Boolean. Include sentences of child nodes?
            ignore_floats: Boolean. Exclude sentences of floating object captions?
            tokenizer:     A NLTK sentence tokenizer. Must be specified otherwise
                           this method will return an empty list.
        Return:
            List of sentences.
        """
        if tokenizer is None:
            return list()
        full_text = self.raw(recursive, ignore_floats)
        sents = tokenizer.tokenize(full_text)
        return [word_tokenize(s) for s in sents]

    def __unicode__(self):
        return "Node(children=%s)" % unicode(self._children)

    def __str__(self):
        return "Node(children=%s)" % str(self._children)

    def __repr__(self):
        return self.__str__()


##################################################################
# DOCUMENT COMPONENTS
##################################################################

class Float(Node):
    DUMMY, FIGURE, TABLE, LISTING, DEFINITION, FORMULA, THEOREM, PROOF = range(8)
    def __init__(self, text=u"", number=u"", pagenr=u""):
        super(Float, self).__init__(text=text, pagenr=pagenr)
        self.number = number

    def is_float(self):
        return True

#class Image(Float):
#    def __init__(self):
#        pass

#class LooseText(Node):
#class Misc(Node):
#    def __init__(self, box=None):
#        super(Misc, self).__init__(box=box)

class Footnote(Float):
    def __init__(self, text=u"", number=u"", pagenr=u""):
        super(Footnote, self).__init__(text=text, number=number, pagenr=pagenr)

    def is_float(self):
        return False

    def is_footnote(self):
        return True

#class Sentence(LooseText):
#    def __init__(self, text=""):
#        self.text = text
#
#    def length(self):
#        """Returns number of words."""
#        pass
#
#    def has_filler(self):
#        pass
#
#    def has_redundancy(self):
#        pass
#
#    def has_tautology(self):
#        pass
#
#    def has_dead_verbs(self):
#        pass
#
#    def has_boosting_adverbs(self):
#        pass

class Paragraph(Node):
    def __init__(self, text, pagenr=u"", font=u"", fontsize=u"", emph=[], word_count=0):
        super(Paragraph, self).__init__(text=text, pagenr=pagenr)
        self.font = font
        self.fontsize = fontsize
        self.emph = list(emph)
        self.word_count = word_count

    def is_paragraph(self):
        return True


class Section(Node):
    def __init__(self, pagenr=u"", title=u"", number=u"", children=[]):
        super(Section, self).__init__(pagenr=pagenr, children=children)
        self.title = title
        self.number = number

    def is_section(self):
        return True

#    def has_introduction(self):
#        pass
#
#    def count_subsections():
#        return 0

    def __unicode__(self):
        if self.number is not u"":
            return u"Section(number=%s, title=%s)" % (self.number, self.title)
        else:
            return u"Section(title=%s)" % self.title

    def __str__(self):
        if self.number is not u"":
            return u"Section(number=%s, title=%s)" % (self.number.encode("utf8"), self.title.encode("utf8"))
        else:
            return u"Section(title=%s)" % self.title.encode("utf8")

class Chapter(Section):
    def __init__(self, pagenr=u"", title=u"", number=u"", children=[]):
        super(Chapter, self).__init__(pagenr=pagenr, title=title, number=number, children=children)


class Document(Section):
    def __init__(self, meta=None, children=[]):
        super(Document, self).__init__(children=children)
        self.meta = meta

#    def has_title(self):
#        pass
#
#    def has_abstract(self):
#        pass
#
#    def has_TOC(self):
#        pass
#
#    def has_conclusion(self):
#        pass
#
#    def has_appendix(self):
#        pass
#
#    def has_bibliography(self):
#        pass

class Meta(object):
    def __init__(self, title=u"", authors=None, language=u""):
        super(Meta, self).__init__()
        self.title = title
        if authors == None or type(authors) != list:
            self.authors = list()
        else:
            self.authors = authors
        self.language = language


class DocumentChecker(object):
    """Checks and corrects a Document for consistency."""

    def __init__(self):
        super(DocumentChecker, self).__init__()

    def cleanup(self, doc):
        doc = self._strip(doc)
        return self._only_keep_real_sections(doc)

    def _strip(self, doc):
        """
        Strips the document of text before the first section and
        after the last section.
        """
        mark_for_rm = list()
        fst_sec_found = False
        lst_sec_found = False
        for c in doc.children():
            t = type(c)
            if t == Section:
                if not fst_sec_found:
                    fst_sec_found = True
            else:
                if not fst_sec_found:
                    mark_for_rm.append(c)
                else:
                    lst_sec_found = True
                if lst_sec_found:
                    mark_for_rm.append(c)

        if fst_sec_found:
            for to_rm in mark_for_rm:
                doc.remove_child(to_rm)

        return doc

    def _only_keep_real_sections(self, doc):
        last_nr = u""
        last_node = None
        mark_for_rm = list()
        for c in doc.children():
            if type(c) == Section:
                to_compare = c.number
                if to_compare is u"":
                    to_compare = c.title
                if last_nr > to_compare:
                    if last_node:
                        mark_for_rm.append(last_node)
                last_nr = to_compare
                last_node = c

        for to_rm in mark_for_rm:
            doc.remove_child(to_rm)

        return doc


if __name__ == '__main__':
    print "Demo for " + __file__
    doc = Document()
    sec = Section(title="FooTitle")
    print doc
    print sec
    doc.add_child(sec)
    print doc
    print sec
