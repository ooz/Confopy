#!/usr/bin/python -OO
# coding: utf-8

import unittest

from pdfextract import *

TEST_FILE = "./test/data/test_doc.pdf"

class TestPdfextract(unittest.TestCase):
    """ Unit tests for pdfconvert. """

    def test_PDFMinerWrapper(self):
        """  """
        w = PDFMinerWrapper()
        result = w.pdf2txt(TEST_FILE).strip()
        expected = """

This is a test PDF document.
If you can read this, you have Adobe Acrobat Reader installed on your computer.

""".strip()
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()

