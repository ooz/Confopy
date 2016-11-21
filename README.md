Confopy
=======

Asserts the linguistic and structural quality of scientific texts.

Confopy is a command-line tool that accepts one or multiple PDF documents and prints textual reports.
Currently it only works for German papers.

Name origin: Confopy := Conform + Python 


Installation
============

Installation using pypi (preferred)
-----------------------------------

    sudo pip install -U Confopy

Launch Confopy with

    confopy --help
    confopy -r document your_paper.pdf

Manual installation
-------------------

Dependencies:

    sudo apt-get install python-pdfminer

    sudo pip install -U lxml
    sudo pip install numpy==1.6.2
    sudo pip install pyyaml nltk==3.0.0
    sudo pip install pyenchant==1.6.5
    sudo pip install pattern==2.6

Launch Confopy with

    python confopy/ --help
    python confopy/ -r document your_paper.pdf


Usage
=====

    $ confopy -h
    usage: confopy [-h] [-l LANGUAGE] [-lx] [-ml] [-o OUTFILE] [-r REPORT] [-rl]
                   [-ul] [-vl] [-x]
                   [file [file ...]]

    Language and structure checker for scientific documents.

    positional arguments:
      file                  Document file to analyze (PDF).

    optional arguments:
      -h, --help            show this help message and exit
      -l LANGUAGE, --language LANGUAGE
                            Language to use for PDF extraction and document
                            analysis. Default: de
      -lx, --latex          Tell the specified report to format output as LaTeX
                            (if supported by the report).
      -ml, --metriclist     Lists all available metrics by language and exits.
      -o OUTFILE, --outfile OUTFILE
                            File to write the output too. Default: terminal
                            (stdout).
      -r REPORT, --report REPORT
                            Analyses the given document according to the specified
                            report.
      -rl, --reportlist     Lists all available reports by language and exits.
      -ul, --rulelist       Lists all rules and exits.
      -vl, --validate       Validates a given XML against the XSD for the Confopy
                            data model.
      -x, --xml             Converts the PDF file(s) to Confopy XML (structure
                            orientated).


Getting a corpus
================

Confopy needs a corpus (collection of language data) to run.

For German (TIGER treebank):

Automated download:

    1. Go to 
       <your python package directory>/confopy/localization/de/corpus\_de/
    2. Execute the script
       tiger_dl_patch.py
       within that folder

Manual download:

    1. Go to: 
       http://www.ims.uni-stuttgart.de/forschung/ressourcen/korpora/TIGERCorpus/license/htmlicense.html
    2. Accept the license and download TIGER-XML Release 2.2: 
       http://www.ims.uni-stuttgart.de/forschung/ressourcen/korpora/TIGERCorpus/download/tigercorpus-2.2.xml.tar.gz
    3. Unpack the archive into confopy/localization/de/corpus\_de/
    4. Run the patch tiger\_release\_aug07.corrected.16012013\_patch.py in the same folder
    5. Verify that the generated file is named exactly like in confopy/config.py


Python 3
========

 * The package python-pdfminer only works with python 2.4 or newer, but not with python 3


Known Issues and Workarounds
===============================

enchant.errors.DictNotFoundError: Dictionary for language 'de_DE' could not be found
------------------------------------------------------------------------------------

Install the German aspell package. E.g. on Ubuntu 16.04:

```
sudo apt install aspell-de
```

Unicode errors
--------------

 * Configure terminal to use unicode!
 * For Python devs:
    http://docs.python.org/2/howto/unicode.html#the-unicode-type
 * Convert the TIGER Treebank file
    "tiger_release_aug07.corrected.16012013.xml"
   to utf-8 encoding before using Confopy!
