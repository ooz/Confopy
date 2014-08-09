# coding: utf-8
'''
File: report.py
Author: Oliver Zscheyge
Description:
    Report superclass.
'''

from localizable import Localizable

class Report(Localizable):
    """Superclass for all Reports.
    """
    def __init__(self, ID=u"", language=u"", brief=u"", description=u""):
        super(Report, self).__init__(ID, language, brief, description)

    def execute(self, docs, args):
        buf = list()
        return u"\n".join(buf)

