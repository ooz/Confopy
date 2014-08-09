#!/usr/bin/python
# coding: utf-8

"""__main__.py: """
__author__  = "Oliver Zscheyge"
__email__   = "oliverzscheyge@gmail.com"
__version__ = "0.1.0"

import sys
from   optparse import OptionParser

from pdfminer_wrapper import *

def main(options, args):
    for fname in args:
        w = PDFMinerWrapper()
        result = ""
        if options.xml:
            result = w.pdf2xml(fname)
        elif options.html:
            result = w.pdf2html(fname)
        elif options.text:
            result = w.pdf2txt(fname)
        print result.strip()


if __name__ == "__main__":
    usage  = "Usage: %prog [options] file(s)"
    parser = OptionParser(usage = usage)
    parser.add_option( "-v", "--verbose"
                     , action="store_true", dest="verbose", default=False
                     , help="Verbose output.")
    parser.add_option( "-t", "--text"
                     , action="store_true", dest="text", default=True
                     , help="Convert to text (default). Option can be omitted.")
    parser.add_option( "-m", "--html"
                     , action="store_true", dest="html", default=False
                     , help="Convert to HTML. Overrides default setting.")
    parser.add_option( "-x", "--xml"
                     , action="store_true", dest="xml", default=False
                     , help="Convert to XML. Overrides default setting.")

    (options, args) = parser.parse_args()
    main(options, args)
