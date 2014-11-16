# coding: utf-8

#from confopy.localization.corpora import *

import confopy.config as C

def load_language(lang=C.DEFAULT_LANG, lightweight=False):
    """Loads a language package.
    Args:
        lang:        The ISO 639-1:2002 language code of the
                     language to load.
        lightweight: If True loads only metrics, reports, rules
                     and NO corpora.
                     False: load everything (might take some time)
    """
    if lang == u"de":
        #from confopy.localization.de import *
        if not lightweight:
            import confopy.localization.de.corpus
        import confopy.localization.de.metrics
        import confopy.localization.de.rules
        import confopy.localization.de.reports
    elif lang == u"en":
        pass

#from confopy.localization.metrics import *
#from confopy.localization.rules import *
#from confopy.localization.reports import *
