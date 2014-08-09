# Confopy

Asserting the linguistic and structural quality of scientific texts. Written in Python.
Name origin: Confopy := Conform + Python 


# Installation

## Installation using pypi

    sudo pip install -U Confopy

## Manual installation

Dependencies:

    sudo apt-get install python-pdfminer

    sudo pip install -U lxml
    sudo pip install -U numpy
    sudo pip install -U pyyaml nltk
    sudo pip install -U pyenchant
    sudo pip install -U pattern

Launch Confopy with

    python confopy/

## Issues with NLTK

If you get the following error while launching confopy:

    Traceback (most recent call last):
      File "/usr/local/bin/confopy", line 21, in <module>
        from confopy.pdfextract import *
      File "/usr/local/lib/python2.7/dist-packages/confopy/pdfextract/__init__.py",
    line 6, in <module>
        from confopy.pdfextract.convenience import PDF2XMLstring,
    PDF2pages, PDF2document, PDFs2documents
      File "/usr/local/lib/python2.7/dist-packages/confopy/pdfextract/convenience.py",
    line 13, in <module>
        from confopy.pdfextract.heuristics import HeuristicManager
      File "/usr/local/lib/python2.7/dist-packages/confopy/pdfextract/heuristics.py",
    line 12, in <module>
        from confopy.model.document import Node, Document, Section,
    Paragraph, Float, Footnote
      File "/usr/local/lib/python2.7/dist-packages/confopy/model/__init__.py",
    line 3, in <module>
        from confopy.model.document import *
      File "/usr/local/lib/python2.7/dist-packages/confopy/model/document.py",
    line 9, in <module>
        from nltk import word_tokenize
      File "/usr/local/lib/python2.7/dist-packages/nltk/__init__.py", line
    40, in <module>
        __doc__ += '\n@version: ' + __version__
    TypeError: unsupported operand type(s) for +=: 'NoneType' and 'str'

Comment line 40 in the file:

      /usr/local/lib/python2.7/dist-packages/nltk/__init__.py


# Getting a corpus

Confopy needs a corpus (collection of language data) to run.

For German (TIGER treebank):

    1. Go to: 
       http://www.ims.uni-stuttgart.de/forschung/ressourcen/korpora/TIGERCorpus/license/htmlicense.html
    2. Accept the license and download TIGER-XML Release 2.2: 
       http://www.ims.uni-stuttgart.de/forschung/ressourcen/korpora/TIGERCorpus/download/tigercorpus-2.2.xml.tar.gz
    3. Unpack the archive into confopy/localization/de/corpus\_de/
    4. Run the patch tiger\_release\_aug07.corrected.16012013\_patch.py in the same folder
    5. Verify that the generated file is named exactly like in confopy/config.py


# Python 3

 * The package python-pdfminer only works with python 2.4 or newer, but not with python 3


# Unicode errors

 * Configure terminal to use unicode!
 * For Python devs:
    http://docs.python.org/2/howto/unicode.html#the-unicode-type
 * Convert the TIGER Treebank Version 1 file
    "tiger_release_july03.penn"
   to utf-8 encoding before using Confopy!
