#!/usr/bin/python -OO
# coding: utf-8
'''
Description:
    Confopy entry point.
'''

__author__  = "Oliver Zscheyge"
__email__   = "oliverzscheyge@gmail.com"

import os.path as op
import sys
# Hack to find packages/modules with "confopy" prefix
#sys.path.append("./")
sys.path.append(op.split(op.dirname(op.realpath(__file__)))[:-1][0])

import argparse as AP

import confopy.config as C
from confopy.pdfextract import *
from confopy.model import DocumentConverter
from confopy.model.validate import validate
from confopy.analysis import Analyzer

from confopy.localization import load_language

TEST_LOC = "./test/data/"
TEST_FILE = TEST_LOC + "gjk_ozscheyg.pdf"
#TEST_FILE = TEST_LOC + "bachelorthesis_ozscheyg.pdf"
#TEST_FILE = TEST_LOC + "spanner-osdi2012.pdf"
TEST_FILE = TEST_LOC + "SEUH_Kompetenzerwerb.pdf"

PDF_SUFFIX = u".pdf"
XML_SUFFIX = u".xml"

def test(args):
    """Construction site."""
    #doc = PDF2document(TEST_FILE)

    ## Single page to SVG
    #if len(args) > 0:
    #    pageNr = int(args[0])
    #    if pageNr >= 0 and pageNr < len(pages):
    #        print pages[pageNr].as_svg()

    # Debug: print all pages as text
    #for page in pages:
    #    #print unicode(page)
    #    print ""
    #    page._print()

    #ind = 1
    #if ind < len(pages):
    #    pages[ind]._print()

def pdf2xml(args, output=u""):
    dc = DocumentConverter()
    doc = None
    if len(args.files) == 1:
        doc = PDF2document(args.files[0])
    elif len(args.files) > 1:
        doc = PDFs2documents(args.files)

    if doc:
        output = dc.to_XML(doc, pretty=True)
    return output

def report(args, output=u""):
    # Convert files to Documents
    dc = DocumentConverter()
    docs = list()
    for f in args.files:
        if op.isfile(f):
            if f.lower().endswith(PDF_SUFFIX):
                doc = PDF2document(f)
                docs.append(doc)
            elif f.lower().endswith(XML_SUFFIX):
                docs.extend(dc.to_Documents(f))

    # Fetch and execute report
    load_language(args.language)
    analyzer = Analyzer.instance()
    rep = analyzer.get(report=args.report)
    if rep:
        output += rep.execute(docs, args)
        pass
    else:
        output += 'No report named "%s" available!' % args.report
    return output


""" MAIN
"""
def main(args):
    output = u""

    if args.reportlist:
        load_language(args.language, True)
        analyzer = Analyzer.instance(args.language)
        output = analyzer.reportlist()

    elif args.metriclist:
        load_language(args.language, True)
        analyzer = Analyzer.instance(args.language)
        output = analyzer.metriclist(args.language)

    elif args.rulelist:
        load_language(args.language, True)
        analyzer = Analyzer.instance(args.language)
        output = analyzer.rulelist(args.language)

    elif args.validate:
        output = validate(args.files)

    elif args.xml:
        output = pdf2xml(args)

    elif args.report is not "":
        output = report(args)


    # Write output
    if args.outfile is not "":
        with open(args.outfile, "w") as f:
            f.write(output.encode("utf8"))
            f.write(u"\n".encode("utf8"))
    else:
        sys.stdout.write(output.encode("utf8"))
        sys.stdout.write(u"\n".encode("utf8"))


if __name__ == "__main__":
    parser = AP.ArgumentParser(description="Language and structure checker for scientific documents.")
    parser.add_argument("files", metavar="file",
                        type=str, nargs="*",
                        help="Document file to analyze (PDF).")
    parser.add_argument("-l", "--language",
                        type=str, default=C.DEFAULT_LANG,
                        help="Language to use for PDF extraction and document analysis. Default: " + C.DEFAULT_LANG)
    parser.add_argument("-lx", "--latex",
                        action="store_true", default=False,
                        help="Tell the specified report to format output as LaTeX (if supported by the report).")
    parser.add_argument("-ml", "--metriclist",
                        action="store_true", default=False,
                        help="Lists all available metrics by language and exits.")
    parser.add_argument("-o", "--outfile",
                        type=str, default="",
                        help="File to write the output too. Default: terminal (stdout).")
    parser.add_argument("-r", "--report",
                        type=str, default="",
                        help="Analyses the given document according to the specified report.")
    parser.add_argument("-rl", "--reportlist",
                        action="store_true", default=False,
                        help="Lists all available reports by language and exits.")
    parser.add_argument("-ul", "--rulelist",
                        action="store_true", default=False,
                        help="Lists all rules and exits.")
    parser.add_argument("-vl", "--validate",
                        action="store_true", default=False,
                        help="Validates a given XML against the XSD for the Confopy data model.")
    parser.add_argument("-x", "--xml",
                        action="store_true", default=False,
                        help="Converts the PDF file(s) to Confopy XML (structure orientated).")
    args = parser.parse_args()
    main(args)
