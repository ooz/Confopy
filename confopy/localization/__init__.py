# coding: utf-8

#from confopy.localization.corpora import *

import confopy.config as C

def load_language(lang=C.DEFAULT_LANG):
    if lang == u"de":
        #from confopy.localization.de import *
        import confopy.localization.de
        #from confopy.localization.de import *
    elif lang == u"en":
        pass

#from confopy.localization.metrics import *
#from confopy.localization.rules import *
#from confopy.localization.reports import *
