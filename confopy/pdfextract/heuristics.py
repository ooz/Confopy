# coding: utf-8
'''
File: heuristics.py
Author: Oliver Zscheyge
Description:
    Heuristics used to convert the pdfminer pages to a proper
    structured document.
'''

import re

from confopy.model.document import Node, Document, Section, Paragraph, Float, Footnote
from confopy.model.document import DocumentChecker
from confopy.model import match, match_each, avg_word_length, lines2unicode, lines_using, words_using
from confopy.pdfextract.pdfminer_xml_bindings import find_primary_font


class HeuristicRegExes(object):
    PAGE_NR = r"\d+"
    SECTION_NR = r"(\.\s?)*(\d\.?)+"

    _WHITE = u"[\\s\xa0]"
    _NOT_WHITE = u"[^\\s\xa0]"

    _FLOAT_NR       = _WHITE + r"*" + SECTION_NR + r":?"
    FIGURE_CAP      = r"((Abbildung)|(Abb\.?)|(Figur)|(Fig\.?)|(Grafik)|(Bild))" + _FLOAT_NR
    TABLE_CAP       = r"((Tabelle)|(Tab\.?))" + _FLOAT_NR
    LISTING_CAP     = r"((Quelltext)|(Sourcecode)|(Source [Cc]ode))" + _FLOAT_NR
    DEFINITION_CAP  = r"((Definition)|(Def\.?))" + _FLOAT_NR
    FORMULA_CAP     = r"((Formel))" + _FLOAT_NR
    THEOREM_CAP     = r"((Theorem)|(Satz))" + _FLOAT_NR
    PROOF_CAP       = r"((Beweis))" + _FLOAT_NR

    """Facts about LaTeX footnotes:
        1. Matching SECTION_NR
        2. No whitespace after the number
        3. Number is in emph (emphasis of the textbox)
    """
    LATEX_FOOTNOTE = SECTION_NR + u"[^\\s\xa0\\d\\.]+"

    ERROR_SECTION_RELATION = -42

    @staticmethod
    def compare_sections(a, b):
        """Gives the hierarchical relation of two section headings.
        Examples:
            ("4.", "4.1")   -> 1
            ("2.3", "1.4")  -> 0
            ("1.2.3", "5.") -> -2
            ("foo", "2.")   -> ERROR_SECTION_RELATION

        Args:
            a:  A section's heading.
            b:  Other section's heading.
        Return:
            Integer:
            -1  if a is a subsection of b
            -2  if a is a subsubsection of b
            0   if a and b are on the same hierarchical level
            1   if b is a subsection of a
            ERROR_SECTION_RELATION  error case
        """
        match_a = re.match(HeuristicRegExes.SECTION_NR, a)
        match_b = re.match(HeuristicRegExes.SECTION_NR, b)
        if match_a and match_b:
            number_a = a[:match_a.end()]
            number_b = b[:match_b.end()]
            split_a = filter(lambda s: s.strip() is not u"", number_a.split(u"."))
            split_b = filter(lambda s: s.strip() is not u"", number_b.split(u"."))
            return len(split_b) - len(split_a)
        return HeuristicRegExes.ERROR_SECTION_RELATION

#    @staticmethod
#    def _remove_dots(string):
#        """Removes '.' at the beginning of a string.
#        Example:
#            "....4" -> "4"
#            "5."    -> "5."
#        Args:
#            string  Some string.
#        Return:
#            Unicode string without dots at the beginning.
#        """
#        if len(string) > 0:
#            c = string[0]
#            if c == u".":
#                return HeuristicRegExes._remove_dots(string[1:])
#        return string



class HeuristicType(object):
    """Analysis level of a heuristic.
    """
    WORD_COUNT = 0     # Based on number of words
    CONTENT    = 1     # Based on content of a textbox (e.g. matching RegEx)
    FONT       = 2     # Based on font/font size
    POSITION   = 3     # Based on position on the page
    FLOW       = 4     # Based on textbox flow over multiple pages
    GROUPING   = 5     # Based on hierarchical grouping of textboxes
    COMPLEX    = 6     # Based on multiple heuristics


class TextBoxType(object):
    """Type of a PDF textbox.
    """
    NONE           = 0
    SINGLE_NUMBER  = 1
    TOC_LIST       = 2
    HEADING        = 3 # Font, RegEx (Nummerierung), erscheint vor Paragraphen
    PARAGRAPH      = 4

    FLOAT          = 8 # RegEx
    FIGURE         = 9
    TABLE          = 10
    LISTING        = 11
    DEFINITION     = 12
    FORMULA        = 13
    THEOREM        = 14
    PROOF          = 15

    PAGE_NR                 = 16
    PAGE_NR_OR_HEADING_PART = 17
    FLOAT_CAPTION_PART      = 18
    HEADER_FOOTER           = 19

    HEADING_PART_NUMBER     = 20
    HEADING_PART_HEADING    = 21
    PARAGRAPH_WITH_HEADING  = 22

    TITLE          = 1 << 13 # Font, frühes Vorkommen
    FOOTNOTE       = 1 << 14 # kleine Schrift, wenige Worte, unterhalb von Paragraphen

    @staticmethod
    def is_float(tb_type):
        return (tb_type >= TextBoxType.FLOAT and tb_type <= TextBoxType.PROOF)

class HeuristicManager(object):
    """HeuristicManager"""
    def __init__(self):
        super(HeuristicManager, self).__init__()
        self.heuristics = list()

        self.heuristics.append(SimpleDocumentHeuristic())

    def generate_document(self, dom_pages):
        hints = self._apply_heuristics(dom_pages)
        return self._build_document_hierarchy(dom_pages, hints)

    def _apply_heuristics(self, dom_pages):
        hints = dict()
        for heu in self.heuristics:
            hints = heu.apply(pages=dom_pages, hints=hints)
        return hints

    def _build_document_hierarchy(self, dom_pages, hints):
        root = Document()
        node = root # current node to add children to
        last_title = u""
        accu_heading_nr = None

        for p in dom_pages:
            pagenr = unicode(p.ID)
            for tb in p.textboxes:
                tb_kind = hints.get(tb, TextBoxType.NONE)
                #print str(tb_kind) + " words: " + str(tb.word_count)
                #tb._print()

                if tb_kind == TextBoxType.HEADING:
                    title = lines2unicode(tb.lines, True, u"\n")
                    sec = Section(title=title, pagenr=pagenr)
                    relation = HeuristicRegExes.compare_sections(last_title, title)
                    if relation is not HeuristicRegExes.ERROR_SECTION_RELATION:
                        node.add_child(sec, relation)
                    else:
                        node.add_child(sec)
                    node = sec
                    last_title = title

                elif tb_kind == TextBoxType.HEADING_PART_NUMBER:
                    accu_heading_nr = tb
                elif tb_kind == TextBoxType.HEADING_PART_HEADING:
                    if accu_heading_nr:
                        title=lines2unicode(tb.lines, True, u"\n")
                        number=lines2unicode(accu_heading_nr.lines, True, u"\n")
                        sec = Section(title=title, number=number, pagenr=pagenr)
                        relation = HeuristicRegExes.compare_sections(last_title, number)
                        if relation is not HeuristicRegExes.ERROR_SECTION_RELATION:
                            node.add_child(sec, relation)
                        else:
                            node.add_child(sec)
                        node = sec
                        last_title = number
                        accu_heading_nr = None

                elif tb_kind == TextBoxType.FOOTNOTE:
                    node.add_child(Footnote(text=lines2unicode(tb.lines, True, u"\n"), pagenr=pagenr))
                elif tb_kind == TextBoxType.PARAGRAPH:
                    font = unicode(tb.font[0])
                    fontsize = unicode(tb.font[1])
                    emph = [unicode(e) for e in tb.emph]
                    node.add_child(Paragraph(text=lines2unicode(tb.lines, True, u"\n"), pagenr=pagenr, font=font, fontsize=fontsize, emph=emph))
                elif tb_kind == TextBoxType.PARAGRAPH_WITH_HEADING:
                    heading_line_count = lines_using(tb.lines, tb.emph, True)
                    heading_lines = tb.lines[:heading_line_count]
                    paragraph_lines = tb.lines[heading_line_count:]
                    title = lines2unicode(heading_lines, True, u"\n")
                    sec = Section(title=title, pagenr=pagenr)
                    relation = HeuristicRegExes.compare_sections(last_title, title)
                    if relation is not HeuristicRegExes.ERROR_SECTION_RELATION:
                        node.add_child(sec, relation)
                    else:
                        node.add_child(sec)
                    node = sec
                    last_title = title
                    font = unicode(tb.font[0])
                    fontsize = unicode(tb.font[1])
                    emph = [unicode(e) for e in tb.emph]
                    node.add_child(Paragraph(text=lines2unicode(paragraph_lines, True, u"\n"), pagenr=pagenr, font=font, fontsize=fontsize, emph=emph))

                elif TextBoxType.is_float(tb_kind):
                    node.add_child(Float(text=lines2unicode(tb.lines, True, u"\n"), pagenr=pagenr))

        doc_check = DocumentChecker()
        return doc_check.cleanup(root)


class Heuristic(object):
    """Super class for all heuristics
    """

    def __init__(self, kind):
        """Constructor.
        Args:
            kind:   HeuristicType of the Heuristic.
        """
        super(Heuristic, self).__init__()
        self.kind = kind

    def apply(self, pages=[], page=None, box=None, hints={}):
        """Analyzes the kinds of textboxes.
        Args:
            pages: List of pages containing textboxes.
                   All textboxes on these pages are analyzed.
            page:  Single Page. All textboxes on this page are analyzed.
            box:   Single TextBox. Just this TextBox is analyzed.
            hints: TextBox --> TextBoxType dictionary.
        Return:
            Dictionary, same structure as parameter hints, should contain
            more info than the passed hints.
        """
        knowledge = hints
        if pages is not []:
            for p in pages:
                knowledge = self.apply(page=p, hints=knowledge)

        elif page is not None:
            for b in page.textboxes:
                knowledge = self.apply(box=b, hints=knowledge)

        elif box is not None:
            return hints


class SimpleDocumentHeuristic(Heuristic):
    """SimpleDocumentHeuristic."""
    def __init__(self):
        super(SimpleDocumentHeuristic, self).__init__(HeuristicType.COMPLEX)

    def apply(self, pages=[], page=None, box=None, hints={}):
        if hints == {}:
            hints = dict()
        prim_font = find_primary_font(pages=pages)
        for page in pages:
            for tb in page.textboxes:

                line_count = len(tb.lines)

                # TOC, heading/page numbers and footnotes
                if match_each(HeuristicRegExes.SECTION_NR, tb.lines):
                    if line_count > 1:
                        if (tb.word_count / float(line_count) > 1.0): # filter listing line numbering
                            hints[tb] = TextBoxType.TOC_LIST
                    else:
                        if tb.word_count > 1:
                            if match(HeuristicRegExes.LATEX_FOOTNOTE, tb.lines, True) and lines_using(tb.lines, tb.emph, True) == 0:
                                hints[tb] = TextBoxType.FOOTNOTE
                            else:
                                hints[tb] = TextBoxType.HEADING
                        else:
                            hints[tb] = TextBoxType.PAGE_NR_OR_HEADING_PART
                            #tb._print()
                elif match(HeuristicRegExes.SECTION_NR, tb.lines, True):
                    if match(HeuristicRegExes.LATEX_FOOTNOTE, tb.lines, True) and lines_using(tb.lines, tb.emph, True) == 0:
                        hints[tb] = TextBoxType.FOOTNOTE
                    else:
                        hints[tb] = TextBoxType.HEADING

                # Floating objects
                if match(HeuristicRegExes.FIGURE_CAP, tb.lines, True):
                    hints[tb] = TextBoxType.FIGURE
                elif match(HeuristicRegExes.TABLE_CAP, tb.lines, True):
                    hints[tb] = TextBoxType.TABLE
                elif match(HeuristicRegExes.LISTING_CAP, tb.lines, True):
                    hints[tb] = TextBoxType.LISTING
                elif match(HeuristicRegExes.DEFINITION_CAP, tb.lines, True):
                    hints[tb] = TextBoxType.DEFINITION
                elif match(HeuristicRegExes.FORMULA_CAP, tb.lines, True):
                    hints[tb] = TextBoxType.FORMULA
                elif match(HeuristicRegExes.THEOREM_CAP, tb.lines, True):
                    hints[tb] = TextBoxType.THEOREM
                elif match(HeuristicRegExes.PROOF_CAP, tb.lines, True):
                    hints[tb] = TextBoxType.PROOF

                # Checks whether textbox is paragraph (main text content)
                if tb.font[0] == prim_font[0] \
                   and tb.font[1] == prim_font[1] \
                   and avg_word_length(tb.lines) > 2 \
                   and (line_count and (tb.word_count / float(line_count)) > 1.8) \
                   and not (tb.word_count == 1 and match(HeuristicRegExes.PAGE_NR, tb.lines, True)) \
                   and hints.get(tb, TextBoxType.NONE) != TextBoxType.FOOTNOTE:
                    hints[tb] = TextBoxType.PARAGRAPH
                    if match(HeuristicRegExes.SECTION_NR, tb.lines, True):
                        heading_line_count = lines_using(tb.lines, tb.emph, True)
                        if heading_line_count:
                            hints[tb] = TextBoxType.PARAGRAPH_WITH_HEADING
                        elif len(tb.emph) == 1 and words_using(tb.lines, tb.emph, True) == 1:
                            # maybe add another condition: only if it's last textbox on page
                            hints[tb] = TextBoxType.FOOTNOTE

        # Layout (TextGroup) analysis
        layout_heu = SimpleLayoutHeuristic()
        hints = layout_heu.apply(pages=pages, hints=hints)

        return hints


class SimpleLayoutHeuristic(Heuristic):
    """Analyses hierarchical TextBox grouping to identify headings.
    """
    def __init__(self):
        super(SimpleLayoutHeuristic, self).__init__(HeuristicType.GROUPING)

    def apply(self, pages=[], page=None, box=None, hints={}):
                 #Page, TextBox, TextBoxType
        ndLast = (None, None,    TextBoxType.NONE)
        last   = (None, None,    TextBoxType.NONE)
        cur    = (None, None,    TextBoxType.NONE)

        for page in pages:
            for tb in page.textboxes:
                ndLast = last
                last = cur
                cur = (page, tb, hints.get(tb, TextBoxType.NONE))

                # Float being split into number + caption text
                if TextBoxType.is_float(last[2]) and last[1].word_count <= 2 \
                   and cur[0].is_sibling(last[1], cur[1]):
                    cur = (cur[0], cur[1], TextBoxType.FLOAT_CAPTION_PART)
                    hints[cur[1]] = cur[2]

                # Find heading split into number + heading
                if cur[2] == TextBoxType.PARAGRAPH and \
                   ndLast[2] == TextBoxType.PAGE_NR_OR_HEADING_PART and \
                   ndLast[0] == last[0]:
                    if cur[0].is_sibling(ndLast[1], last[1], cur[1]):
                        ndLast           = (ndLast[0], ndLast[1], TextBoxType.HEADING_PART_NUMBER)
                        hints[ndLast[1]] = ndLast[2]
                        last             = (last[0], last[1], TextBoxType.HEADING_PART_HEADING)
                        hints[last[1]]   = last[2]
                    else:
                        ndLast           = (ndLast[0], ndLast[1], TextBoxType.PAGE_NR)
                        hints[ndLast[1]] = ndLast[2]
                        last             = (last[0], last[1], TextBoxType.HEADER_FOOTER)
                        hints[last[1]]   = last[2]
        return hints


class FontHeuristic(object):
    """FontHeuristic
    """
    def __init__(self):
        super(FontHeuristic, self).__init__(kind=HeuristicType.FONT)


if __name__ == '__main__':
    """heuristics.py test"""
    chap = ".....4. Chapter"
    sect = "2.3 Section"
    sec2 = "1.2 Section"
    subs = "2.3.1 Subsection"
    result = re.match(HeuristicRegExes.SECTION_NR, subs)
    assert HeuristicRegExes.compare_sections(chap, sect) == 1
    assert HeuristicRegExes.compare_sections(sect, sec2) == 0
    assert HeuristicRegExes.compare_sections(subs, sect) == -1

    footnote = u"2Foo is part of bar."
    nofootnote = u"2.3 Foobar"
    nofootnoteeither = u"2.3"
    res1 = re.match(HeuristicRegExes.LATEX_FOOTNOTE, footnote, re.U)
    res2 = re.match(HeuristicRegExes.LATEX_FOOTNOTE, nofootnote, re.U)
    res3 = re.match(HeuristicRegExes.LATEX_FOOTNOTE, nofootnoteeither, re.U)
    assert res1 is not None
    assert res2 is None
    assert res3 is None

