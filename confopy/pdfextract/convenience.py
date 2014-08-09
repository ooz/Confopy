# coding: utf-8
'''
File: convenience.py
Author: Oliver Zscheyge
Description:
    Convenience functions for handling PDF conversions.
'''

from xml.dom.minidom import parseString

from confopy.pdfextract.pdfminer_wrapper import PDFMinerWrapper
from confopy.pdfextract.pdfminer_xml_bindings import DOM2pages
from confopy.pdfextract.heuristics import HeuristicManager


def PDF2XMLstring(filepath):
    pdfminer = PDFMinerWrapper()
    return pdfminer.pdf2xml(filepath)

def PDF2pages(filepath):
    pdfminer = PDFMinerWrapper()
    xml_str = pdfminer.pdf2xml(filepath)
    dom = parseString(xml_str)
    return DOM2pages(dom)

def PDF2document(filepath):
    pdfminer = PDFMinerWrapper()
    xml_str = pdfminer.pdf2xml(filepath)
    dom = parseString(xml_str)
    pages = DOM2pages(dom)
    hm = HeuristicManager()
    return hm.generate_document(pages)

def PDFs2documents(filepaths):
    return map(PDF2document, filepaths)
