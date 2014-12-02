# coding: utf-8
'''
File: validate.py
Author: Oliver Zscheyge
Description:
    Contains validate method to check whether a given XML document conforms
    to the Confopy data model.
'''

import os.path as op
from lxml import etree

def validate(files):
    """Validates XML files according to the Confopy data model XML schema.
    Args:
        files: A list of file paths. The XML documents to validate.
    Return:
        A string message indicating the successful validation or listing all errors.
    """
    xsd_path = u"%s/confopy_document.xsd" % op.dirname(op.realpath(__file__))
    output = u""
    for f in files:
        xsd_doc = etree.parse(xsd_path)
        xml_schema = etree.XMLSchema(xsd_doc)
        doc = etree.parse(f)
        if xml_schema.validate(doc):
            output = output + "%s is a valid instance of %s!\n" % (f, xsd_path)
        else:
            output = output + "%s is invalid according to %s!\n\nError(s):\n%s\n" % (f, xsd_path, xml_schema.error_log)
    return output
