# encoding: utf-8
'''
File: analyzer.py
Author: Oliver Zscheyge
Description:
    Analyzer class bundling all metrics, rules and reports.
'''

from localizable import Localizable
from corpus import Corpus, NO_WORDS
from metric import Metric
from rule import Rule
from report import Report
import confopy.config as C


class Analyzer(object):
    """Bundles all available Metrics, Rules and Reports by IDs and languages.
    """

    _instances = dict()
    _PAD = u"  "

    @staticmethod
    def instance(lang=C.DEFAULT_LANG):
        """Yields the Analyzer instance for a given language.
        Args:
            lang: The language of the wanted Analyzer object.
        Return:
            Analyzer instance.
        """
        if Analyzer._instances.get(lang, None) == None:
            Analyzer._instances[lang] = Analyzer()
        return Analyzer._instances.get(lang)

    def __init__(self):
        """Initializer.
        """
        super(Analyzer, self).__init__()
        self._metrics = dict()
        self._rules = dict()
        self._reports = dict()
        self._corpora = dict()

    @staticmethod
    def register(obj):
        """Registers a given metric, rule, report or corpus with the Analyzer.
        Args:
            obj: A metric, rule, report or corpus object to register.
        """
        if isinstance(obj, Metric) or \
           isinstance(obj, Rule) or \
           isinstance(obj, Report) or \
           isinstance(obj, Corpus):
            lang = obj.language
            analyzer = Analyzer.instance(lang)
            analyzer._register(obj)

    def _register(self, obj):
        if isinstance(obj, Metric):
            self._metrics[obj.ID] = obj
        elif isinstance(obj, Rule):
            self._rules[obj.ID] = obj
        elif isinstance(obj, Report):
            self._reports[obj.ID] = obj
        elif isinstance(obj, Corpus):
            self._corpora[obj.ID] = obj

    def get(self, metric=None, rule=None, report=None, corpus=None):
        """Gets a given metric, rule, report or corpus by its ID.
        Args:
            metric: ID of the metric to get.
            rule:   ID of the rule to get.
            report: ID of the report to get.
            corpus: ID of the corpus to get.
        Return:
            Metric, Rule, Report or Corpus object.
        """
        if metric:
            return self._metrics.get(metric, None)
        elif rule:
            return self._rules.get(rule, None)
        elif report:
            return self._reports.get(report, None)
        elif corpus:
            return self._corpora.get(corpus, None)
        return None

    def metrics(self):
        """Yields all registered metrics.
        """
        return {k: self._metrics[k] for k in self._metrics}
        #return {k: self._metrics[k] for k in self._metrics if self._metrics[k].language == lang}

    def rules(self):
        """Yields all registered rules.
        """
        return {k: self._rules[k] for k in self._rules}
        #return {k: self._rules[k] for k in self._rules if self._rules[k].language == lang}

    def reports(self):
        """Yields all registered reports.
        """
        #ret = list()
        #if lang != u"":
        #    ret.extend([r for r in self._reports.values() if r.language == lang])
        #return ret
        return {k: self._reports[k] for k in self._reports}
        #return {k: self._reports[k] for k in self._reports if self._reports[k].language == lang}

    def _languages(self, dictionary):
        """Returns a list of unique ISO 639-1 language codes denoting
            all languages supported by Localizable objects in the passed dict.
        Args:
            dictionary Dict of Localizable objects (Metrics, Rules, Reports).
        Return:
            List of unique unicode strings (ISO 639-1 language codes).
        """
        langs = [v.language for v in dictionary.values()]
        return sorted(set(langs))

    def reportlist(self, lang=u""):
        """Returns a pretty formatted list of reports as a unicode string.
        Args:
            lang: List only reports of this language. Optional.
                  If omitted all reports of all languages are included
                  in the string.
        Return:
            A unicode string.
        """
        if len(self._reports) == 0:
            return u"No reports known to Confopy!"

        buf = list()
        langs = list()
        max_ID_len = 0
        if lang != u"":
            langs.append(lang)
            report_IDs = sorted(self.reports().keys())
            max_ID_len = max([len(rID) for rID in report_IDs])
        else:
            langs.extend(self._languages(self._reports))
            max_ID_len = max([len(rID) for rID in self._reports])
        pad_width = max_ID_len + 2 * len(Analyzer._PAD)

        for l in langs:
            buf.append(u'Reports for language "%s":' % (l, ))
            report_IDs = sorted(self.reports().keys())
            for report_ID in report_IDs:
                report = self._reports.get(report_ID)
                line = u"%s%s%s" % (Analyzer._PAD, report_ID.ljust(pad_width), report.brief)
                buf.append(line)
                line = u"%s%s%s" % (Analyzer._PAD, Analyzer._PAD, report.description)
                buf.append(line)
                if report.description is not u"":
                    buf.append(u"")

        return u"\n".join(buf)

    def metriclist(self, lang=u""):
        """Returns a pretty formatted list of metrics as a unicode string.
        Return:
            A unicode string.
        """
        buf = list()
        buf.append(u"Metrics for language \"" + lang + u"\":")
        keys = sorted(self._metrics.keys())
        pad_width = reduce(max, [len(k) for k in keys], 0) + 2 * len(Analyzer._PAD)
        for k in keys:
            metric = self._metrics[k]
            buf.append(u"%s%s%s" % (Analyzer._PAD, k.ljust(pad_width), metric.brief))
            buf.append(u"%s%s%s" % (Analyzer._PAD, Analyzer._PAD, metric.description))
            if self._metrics[k].description is not u"":
                buf.append(u"")
        return u"\n".join(buf)


if __name__ == '__main__':
    print "Demo for %s" % __file__

    analyzer = Analyzer.instance()

    analyzer.register(Report(u"test-en" , u"en", u"Easy to parse report using all metrics."))
    analyzer.register(Report(u"test-aa" , u"aa"))
    analyzer.register(Report(u"test-de1", u"de", u"Wortlängenreport"))
    analyzer.register(Report(u"test-de2", u"de"))
    analyzer.register(Report(u"test-fr1", u"fr"))
    analyzer.register(Report(u"test-fr2", u"fr"))
    analyzer.register(Report(u"test-fr3", u"fr"))
    assert len(analyzer.reports()) == 2

    print analyzer.reportlist(u"de")
    print analyzer.reportlist()
