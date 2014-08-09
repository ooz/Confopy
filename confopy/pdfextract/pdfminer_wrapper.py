#!/usr/bin/python
# coding: utf-8

import StringIO
import re

from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.pdfdevice import PDFDevice
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams

# For NoCidXMLConverter implementation:
from pdfminer.layout import LTChar
from pdfminer.pdffont import PDFUnicodeNotDefined


RE_XML_ILLEGAL = u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + \
                    u'|' + \
                    u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \
                    (unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                    unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                    unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                    )
RE_XML_ILLEGAL_ASCII = r"[\x01-\x09\x0B\x0C\x0E-\x1F\x7F]"


class Options:
    def __init__(self):
        self.pagenos = list()
        self.maxpages = 0
        self.password = ""
        self.caching = True
        self.codec = "utf-8"
        self.layoutmode = "normal"
        self.pageno = 1
        self.scale = 1
        self.showpageno = True
        self.laparams = LAParams()

class NoCidXMLConverter(XMLConverter):
    """
    Attempts to fix the (cid:<number>) errors produced by the original pdfminer implementation.
    See:
        http://stackoverflow.com/questions/16523767/what-is-this-cid51-in-the-output-of-pdf2txt
    """
    def __init__(self, rsrcmgr, outfp, codec="utf-8", pageno=1, laparams=None, outdir=None):
        super(NoCidXMLConverter, self).__init__(rsrcmgr, outfp, codec, pageno, laparams, outdir)

    def render_char(self, matrix, font, fontsize, scaling, rise, cid):
        try:
            text = font.to_unichr(cid)
            assert isinstance(text, unicode), text
        except PDFUnicodeNotDefined:
            text = self.handle_undefined_char(font, cid)
        textwidth = font.char_width(cid)
        textdisp = font.char_disp(cid)
        item = LTChar(matrix, font, fontsize, scaling, rise, text, textwidth, textdisp)
        self.cur_item.add(item)
        return item.adv

    def handle_undefined_char(self, font, cid):
        #print "Undefined: %r, %r" % (font, cid)
        return "(cid:%d)" % cid

class _PDFMiner:
    def __init__(self, options=Options()):
        self.options = options
        self.resmgr = PDFResourceManager(caching=self.options.caching)

    def _process(self, fp, device):
        process_pdf( self.resmgr
                   , device
                   , fp
                   , self.options.pagenos
                   , maxpages=self.options.maxpages
                   , password=self.options.password
                   , caching=self.options.caching
                   , check_extractable=True
                   )

    def to_txt(self, fp):
        out_buf = StringIO.StringIO()
        device = TextConverter( self.resmgr
                              , out_buf
                              , codec=self.options.codec
                              , laparams=self.options.laparams
                              )
        self._process(fp, device)
        device.close()
        result = out_buf.getvalue()
        out_buf.close()
        return result

    def to_html(self, fp):
        out_buf = StringIO.StringIO()
        device = HTMLConverter( self.resmgr
                              , out_buf
                              , codec=self.options.codec
                              , scale=self.options.scale
                              , layoutmode=self.options.layoutmode
                              , laparams=self.options.laparams
                              , outdir=None
                              )
        self._process(fp, device)
        device.close()
        result = out_buf.getvalue()
        out_buf.close()
        return result

    def to_xml(self, fp):
        out_buf = StringIO.StringIO()
        device = NoCidXMLConverter( self.resmgr
                                  , out_buf
                                  , codec=self.options.codec
                                  , laparams=self.options.laparams
                                  , outdir=None
                                  )
        self._process(fp, device)
        device.close()
        result = out_buf.getvalue()
        out_buf.close()
        return self._replace_control_chars(result)

    def _replace_control_chars(self, s, replace=u""):
        """Stolen from:
        http://chase-seibert.github.io/blog/2011/05/20/stripping-control-characters-in-python.html
        """
        if s:
            s = s.decode("utf-8")
            # unicode invalid characters
            s = re.sub(RE_XML_ILLEGAL, replace, s)

            # ascii control characters
            #s = re.sub(r"[\x01-\x1F\x7F]", replace, s)
            s = re.sub(RE_XML_ILLEGAL_ASCII, replace, s)

            s = s.encode("utf-8")
            return s

class PDFMinerWrapper:
    """ Wrapper for pdfminer package functionality """

    def __init__(self):
        pass

    def pdf2txt(self, filename, options=Options()):
        result = ""
        with open(filename, "rb") as fp:
            conv = _PDFMiner(options)
            result = conv.to_txt(fp)
        return result

    def pdf2html(self, filename, options=Options()):
        result = ""
        with open(filename, "rb") as fp:
            conv = _PDFMiner(options)
            result = conv.to_html(fp)
        return result

    def pdf2xml(self, filename, options=Options()):
        result = ""
        with open(filename, "rb") as fp:
            conv = _PDFMiner(options)
            result = conv.to_xml(fp)
        return result

