#!/usr/bin/python
# coding: utf-8
'''
File: tiger_release_aug07.corrected.16012013_patch.py
Author: Oliver Zscheyge
Description:
    Fixes wrong morph values in the TIGER corpus:
        tiger_release_aug07.corrected.16012013.xml

    Also converts XML file to utf-8 encoding.
'''

import urllib
import tarfile
import codecs
import fileinput
import os

TIGER_URL = "http://www.ims.uni-stuttgart.de/forschung/ressourcen/korpora/TIGERCorpus/download/tigercorpus-2.2.xml.tar.gz"
TIGER_PKG_FILE = "tiger.tar.gz"

TIGER_FILE              = "tiger_release_aug07.corrected.16012013.xml"
TIGER_FILE_UTF8         = "tiger_release_aug07.corrected.16012013_utf8.xml"
TIGER_FILE_UTF8_PATCHED = "tiger_release_aug07.corrected.16012013_utf8_patched.xml"
SOURCE_ENC = "iso-8859-1"
TARGET_ENC = "utf-8"


def main():
    print(u"By using this script you agree with the license at:")
    print(u"http://www.ims.uni-stuttgart.de/forschung/ressourcen/korpora/TIGERCorpus/license/htmlicense.html")
    print(u"Downloading and extracting TIGER corpus...")
    download_extract()
    print(u"Converting the corpus to UTF-8 and fixing strings...")
    convert_to_utf8()
    fix_strings()
    print(u"Cleaning up downloaded and generated files...")
    cleanup()
    print(u"Done!")

def download_extract():
    urllib.urlretrieve(TIGER_URL, TIGER_PKG_FILE)
    tar = tarfile.open(TIGER_PKG_FILE)
    tar.extractall()
    tar.close()

def convert_to_utf8():
    """Converting the TIGER_FILE to utf-8 encoding.
    Taken from:
        http://stackoverflow.com/questions/191359/how-to-convert-a-file-to-utf-8-in-python
    """
    BLOCKSIZE = 1048576 # or some other, desired size in bytes
    with codecs.open(TIGER_FILE, "r", SOURCE_ENC) as sourceFile:
        with codecs.open(TIGER_FILE_UTF8, "w", TARGET_ENC) as targetFile:
            while True:
                contents = sourceFile.read(BLOCKSIZE)
                if not contents:
                    break
                targetFile.write(contents)

def fix_strings():
    replacements = {
          1       : [u"ISO-8859-1", u"utf-8"]
        , 293648  : [u"Pl.1.Pres.Ind", u"1.Pl.Pres.Ind"]
        , 543756  : [u"Pl.3.Pres.Ind", u"3.Pl.Pres.Ind"]
        , 1846632 : [u"Pl.3.Pres.Ind", u"3.Pl.Pres.Ind"]
        , 2634040 : [u"Pl.3.Pres.Ind", u"3.Pl.Pres.Ind"]
    }
    linenr = 1
    with codecs.open(TIGER_FILE_UTF8_PATCHED, "w", TARGET_ENC) as outfile:
        with codecs.open(TIGER_FILE_UTF8, "r", TARGET_ENC) as infile:
            for line in infile:
                line = unicode(line).replace(u"\r", u"") # Replace Window's carriage returns
                replacement = replacements.get(linenr, [])
                if replacement != []:
                    line = line.replace(replacement[0], replacement[1], 1)
                linenr += 1
                outfile.write(line)

#    for line in fileinput.input(TIGER_FILE_FIXED, inplace=True):
#        replacement = replacements.get(fileinput.filelineno(), [])
#        if replacement == []:
#            print line,
#        else:
#            print line.replace(replacement[0], replacement[1], 1),

def cleanup():
    os.remove(TIGER_PKG_FILE)
    os.remove(TIGER_FILE)
    os.remove(TIGER_FILE_UTF8)



if __name__ == '__main__':
    main()

