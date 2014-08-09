# coding: utf-8
'''
File: document_converter.py
Author: Oliver Zscheyge
Description:
    Class for converting Document objects to other representations.
'''

from xml.sax.saxutils import escape
from lxml import etree

from confopy.model.document import Node, Float, Paragraph, Section, Chapter, Document, Meta, Footnote


XML_HEADER = u"<?xml version=\"1.0\" encoding=\"utf-8\" ?>"
PRETTY_IDENT = u"  "
EMPH_SEPARATOR = u","


class DocumentConverter(object):
    """Converts a Document to other representations (e.g. XML).
       Or the other way around.
    """
    def __init__(self):
        """Initializer.
        """
        super(DocumentConverter, self).__init__()

    def to_Documents(self, xml_paths):
        """Converts Confopy XML file(s) to a list of Documents.
        Args:
            xml_paths: Path of the XML file(s) to parse.
        Return:
            A list of Documents.
        """
        docs = list()
        if type(xml_paths) == list:
            for f in xml_paths:
                docs.expand(self.to_Documents(f))
        else:
            context = etree.iterparse(xml_paths, events=("end",), tag=u"document", encoding=u"utf-8")
            docs.extend(self._fast_iter(context, self._parse_xml_document))
            docs = [doc for doc in docs if doc != None]
        return docs

    def _parse_xml_document(self, node):
        if node.tag == u"paragraph":
            pagenr = unicode(node.get(u"pagenr", u""))
            font = unicode(node.get(u"font", u""))
            fontsize = unicode(node.get(u"fontsize", u""))
            emph = unicode(node.get(u"emph", u""))
            emph = emph.split(EMPH_SEPARATOR)
            if len(emph) == 1 and emph[0] == u"":
                emph = []
            text = unicode(node.text)
            return Paragraph(text=text, pagenr=pagenr, font=font, fontsize=fontsize, emph=emph)

        elif node.tag == u"section":
            pagenr = unicode(node.get(u"pagenr", u""))
            title = unicode(node.get(u"title", u""))
            number = unicode(node.get(u"number", u""))
            children = [self._parse_xml_document(c) for c in node]
            return Section(pagenr=pagenr, title=title, number=number, children=children)

        elif node.tag == u"float":
            pagenr = unicode(node.get(u"pagenr", u""))
            number = unicode(node.get(u"number", u""))
            text = unicode(node.text)
            return Float(pagenr=pagenr, number=number, text=text)

        elif node.tag == u"footnote":
            pagenr = unicode(node.get(u"pagenr", u""))
            number = unicode(node.get(u"number", u""))
            text = unicode(node.text)
            return Footnote(pagenr=pagenr, number=number, text=text)

        elif node.tag == u"chapter":
            pagenr = unicode(node.get(u"pagenr", u""))
            title = unicode(node.get(u"title", u""))
            number = unicode(node.get(u"number", u""))
            children = [self._parse_xml_document(c) for c in node]
            return Chapter(pagenr=pagenr, title=title, number=number, children=children)

        elif node.tag == u"document":
            meta = None
            children = [self._parse_xml_document(c) for c in node]
            for c in children:
                if type(c) == Meta:
                    meta = c
            if meta:
                children.remove(meta)
            return Document(meta=meta, children=children)

        elif node.tag == u"meta":
            title = u""
            authors = list()
            language = u""
            for c in node:
                if c.tag == u"title":
                    title = unicode(c.text)
                elif c.tag == u"author":
                    authors.append(unicode(c.text))
                elif c.tag == u"language":
                    language = unicode(c.text)
            return Meta(title=title, authors=authors, language=language)

        return None

    def _fast_iter(self, context, func):
        buf = list()
        for event, elem in context:
            buf.append(func(elem))
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
        del context
        return buf

    def to_XML(self, doc, pretty=False, linesep=u"", ident=u"", header=True):
        """Converts a Document to structure oriented XML.
        Args:
            doc:     The Document or part of a document or list of Documents
                     to convert.
            pretty:  If true: returns a human readable XML string.
                     Takes care of parameters linesep and ident automatically.
            linesep: Line seperator. Is overridden in case pretty is set.
            ident:   Ident for each line. Mainly used for recursion.
            header:  Place the XML header with version and encoding at the
                     beginning of the XML string.
        Return:
            Unicode string (XML markup).
        """
        if doc == None:
            return u""

        buf = list()
        if header:
            buf.append(XML_HEADER)
        if pretty:
            linesep = u"\n"

        if type(doc) == list:
            buf.append(u"<documents>")
            for d in doc:
                buf.append(self.to_XML(d, linesep=linesep, ident=PRETTY_IDENT, header=False))
            buf.append(u"</documents>")

        elif type(doc) == Document:
            buf.append(ident + u"<document>")
            if doc.meta:
                buf.append(self.to_XML(doc.meta, linesep=linesep, ident=ident + PRETTY_IDENT, header=False))
            for c in doc.children():
                buf.append(self.to_XML(c, linesep=linesep, ident=ident + PRETTY_IDENT, header=False))
            buf.append(ident + u"</document>")

        elif type(doc) == Meta:
            buf.append(ident + u"<meta>")
            if doc.title != u"":
                title = u"%s%s<title>%s</title>" % (ident, PRETTY_IDENT, escape(doc.title))
                buf.append(title)
            for author in doc.authors:
                author_xml = u"%s%s<author>%s</author>" % (ident, PRETTY_IDENT, escape(author))
                buf.append(author_xml)
            if doc.language != u"":
                lang = u"%s%s<langauge>%s</language>" % (ident, PRETTY_IDENT, escape(doc.language))
                buf.append(lang)
            buf.append(ident + u"</meta>")

        elif type(doc) == Section:
            buf.append(u"%s<section%s>" % (ident, self._section_attrs(doc)))
            for c in doc.children():
                buf.append(self.to_XML(c, linesep=linesep, ident=ident + PRETTY_IDENT, header=False))
            buf.append(ident + u"</section>")

        elif type(doc) == Chapter:
            buf.append(u"%s<chapter%s>" % (ident, self._section_attrs(doc)))
            for c in doc.children():
                buf.append(self.to_XML(c, linesep=linesep, ident=ident + PRETTY_IDENT, header=False))
            buf.append(ident + u"</chapter>")

        elif type(doc) == Paragraph:
            buf.append(u"%s<paragraph%s>" % (ident, self._paragraph_attrs(doc)))
            buf.append(escape(doc.text))
            buf.append(ident + u"</paragraph>")

        elif type(doc) == Float:
            buf.append(ident + u"%s<float%s>" % (ident, self._float_attrs(doc)))
            buf.append(escape(doc.text))
            buf.append(ident + u"</float>")

        elif type(doc) == Footnote:
            buf.append(ident + u"%s<footnote%s>" % (ident, self._float_attrs(doc)))
            buf.append(escape(doc.text))
            buf.append(ident + u"</footnote>")

        return linesep.join(buf)

    def _section_attrs(self, sec):
        buf = list()
        if sec.number != u"":
            buf.append(u' number="%s"' % escape(sec.number))
        buf.append(u' title="%s"' % sec.title)
        if sec.pagenr != u"":
            buf.append(u' pagenr="%s"' % escape(sec.pagenr))
        return u"".join(buf)

    def _paragraph_attrs(self, para):
        buf = list()
        if para.pagenr != u"":
            buf.append(u' pagenr="%s"' % escape(para.pagenr))
        if para.font != u"":
            buf.append(u' font="%s"' % escape(para.font))
        if para.fontsize != u"":
            buf.append(u' fontsize="%s"' % escape(para.fontsize))
        if len(para.emph) > 0:
            emph_str = EMPH_SEPARATOR.join(para.emph)
            if emph_str != u"":
                buf.append(u' emph="%s"' % escape(emph_str))
        return u"".join(buf)

    def _float_attrs(self, flt):
        buf = list()
        if flt.number != u"":
            buf.append(u' number="%s"' % escape(flt.number))
        if flt.pagenr != u"":
            buf.append(u' pagenr="%s"' % escape(flt.pagenr))
        return u"".join(buf)
