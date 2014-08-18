# coding: utf-8
'''
File: reports.py
Author: Oliver Zscheyge
Description:
    Implementation of all reports
'''

from confopy.analysis import Report, Analyzer, mean_stdev
from confopy.analysis.rule import eval_doc


METRIC_NAMES = [u"wordlength", u"spellcheck", u"lexicon", u"sentlength", u"personalstyle", u"impersonalstyle", u"passiveconstructs", u"simplepres", u"adverbmodifier", u"deadverbs", u"fillers", u"examplecount", u"sentlengthvar"]
MAX_METRIC_STR_LEN = reduce(max, [len(name) for name in METRIC_NAMES])
PAD = 2
METRIC_COL_WIDTH = MAX_METRIC_STR_LEN + PAD

ROUND = 2
class MultiDocReport(Report):
    """Overview/statistics for multiple documents.
    """
    def __init__(self):
        super(MultiDocReport, self).__init__(u"multidoc", u"de", u"Überblick über mehrere Dokumente")

    def execute(self, docs, args):
        output = list()
        metric_names = METRIC_NAMES
        A = Analyzer.instance()
        metrics = [A.get(metric=m) for m in metric_names]
        metrics = [m for m in metrics if m != None]
        corp = A.get(corpus=u"TIGER")
        results = list()
        for m in metrics:
            results.append([m.evaluate(d) for d in docs])
        stats = [mean_stdev(r, ROUND) for r in results]
        if args.latex:
            output.append(u"\\begin{tabular}{l|l l|r}")
            output.append(u"    Metric & mean & stdev & TIGER \\\\")
            output.append(u"    \\hline")
        else:
            output.append(u"METRIC MEAN STDEV REFERENCE")
        for i in range(len(metrics)):
            # Execute metrics on reference corpus
            val = metrics[i].evaluate(corp)
            val = round(val, ROUND)
            if args.latex:
                output.append(u"    %s & %s & %s & %s \\\\" % (metric_names[i].ljust(METRIC_COL_WIDTH), stats[i][0], stats[i][1], val))
            else:
                output.append(u"%s %s %s %s" % (metric_names[i].ljust(METRIC_COL_WIDTH), stats[i][0], stats[i][1], val))
        if args.latex:
            output.append(u"\\end{tabular}")
        return u"\n".join(output)

    def _nltk_test(self, doc, corp):
        #sent_tokenizer = corp.sent_tokenizer()
        #sents = doc.sents(tokenizer=sent_tokenizer)
        #for s in sents:
        #    print u"SENTENCE"
        #    print s
        import sys
        #sys.exit(0)

Analyzer.register(MultiDocReport())

class DocumentComparison(Report):
    """Compares the metrics of 2 documents side by side
    """
    PAD = 2

    def __init__(self):
        super(DocumentComparison, self).__init__(u"doccomp", u"de", u"Vergleicht 2 Dokumente")

    def _compare(self, vals):
        return u"="

    def execute(self, docs, args):
        output = list()
        if len(docs) < 2 or len(docs) % 2 != 0:
            output.append(u"Error: Need an even number of documents (at least 2) for the document comparison report!")
        else:
            metric_names = METRIC_NAMES
            A = Analyzer.instance()
            metrics = [A.get(metric=m) for m in metric_names]
            metrics = [m for m in metrics if m != None]
            if len(docs) == 2:
                for m in metrics:
                    vals = [m.evaluate(doc) for doc in docs]
                    progress = u"="
                    if vals[0] > vals[1]:
                        progress = u"-"
                    elif vals[0] < vals[1]:
                        progress = u"+"
                    output.append(u"%s %.2f --> %.2f \t (%s)" % (m.ID, vals[0], vals[1], progress))

            else:
                half = len(docs) / 2
                if args.latex:
                    output.append(u"\\begin{tabular}{l|l l|l l|r}")
                    output.append(u"\\multirow{2}{*}{\\textbf{Metrik}} & \\multicolumn{2}{|c|}{\\textbf{Erhöhung}} & \\multicolumn{2}{|c|}{\\textbf{Verringerung}} & \\textbf{gleichbleibend} \\\\")
                    output.append(u"                                 & \\multicolumn{1}{|c}{$\\#$} & \\multicolumn{1}{c|}{$\\Delta$} & \\multicolumn{1}{|c}{$\\#$} & \\multicolumn{1}{c|}{$\\Delta$} & \\multicolumn{1}{c}{$\\#$} \\\\")
                    output.append(u"    \\hline")
                else:
                    output.append(u"m.ID + delta+ - delta- =")
                for m in metrics:
                    results = list()
                    for i in range(half):
                        results.append((m.evaluate(docs[i]), m.evaluate(docs[i + half])))
                    counts = [0, 0, 0] # greater, less, equal
                    avg_diffs = [0.0, 0.0]
                    for r in results:
                        if r[0] > r[1]:
                            counts[1] += 1
                            avg_diffs[1] += r[0] - r[1]
                        elif r[0] < r[1]:
                            counts[0] += 1
                            avg_diffs[0] += r[1] - r[0]
                        else:
                            counts[2] += 1
                    if counts[0] > 0:
                        avg_diffs[0] /= float(counts[0])
                        avg_diffs[0] = round(avg_diffs[0], ROUND + 1)
                    if counts[1] > 0:
                        avg_diffs[1] /= float(counts[1])
                        avg_diffs[1] = round(avg_diffs[1], ROUND + 1)
                    if args.latex:
                        output.append(u"    %s & %s & %s & %s & %s & %s \\\\" % (m.ID, counts[0], avg_diffs[0], counts[1], avg_diffs[1], counts[2]))
                    else:
                        output.append(u"%s (%s; %s) (%s; %s) %s" % (m.ID, counts[0], avg_diffs[0], counts[1], avg_diffs[1], counts[2]))
                if args.latex:
                    output.append(u"\\end{tabular}")
        return u"\n".join(output)

Analyzer.register(DocumentComparison())



class _MetricExpectation(object):
    """docstring for _MetricExpectation"""
    def __init__(self, low=None, high=None, msg_toolow=u"", msg_toohigh=u"", msg_ok=u"OK!"):
        super(_MetricExpectation, self).__init__()
        self.low = low
        self.high = high
        self.msg_toolow = msg_toolow
        self.msg_toohigh = msg_toohigh
        self.msg_ok = msg_ok

_METRIC_EXPECTATIONS = {
    u"adverbmodifier":    _MetricExpectation(None       , 0.02 + 0.01, u"", u"Versuche weniger verstärkende/unpräzise Adverbien zu verwenden!"),
    u"deadverbs":         _MetricExpectation(None       , 0.03 + 0.03, u"", u"Versuche weniger tote Verben wie gehören, liegen, befinden, beinhalten, geben, bewirken etc. zu verwenden!"),
    u"examplecount":      _MetricExpectation(1.74 - 1.73 , None       , u"Versuche mehr Beispiele zu nennen!", u""),
    u"fillers":           _MetricExpectation(None       , 0.02 + 0.01, u"", u"Zu viele Füllwörter!"),
    u"impersonalstyle":   _MetricExpectation(None       , 0.02 + 0.03, u"", u"Zu viele Sätze mit 'man'."),
    u"lexicon":           _MetricExpectation(0.49 - 0.05, 0.49 + 0.05, u"Zu geringer Wortschatz", u"Zu vielfältiger Wortschatz (viele Fremdwörter?)"),
    u"passiveconstructs": _MetricExpectation(0.16 - 0.08, None       , u"Versuche mehr passive Sätze zu bilden!"),
    u"personalstyle":     _MetricExpectation(None       , 0.03 + 0.03, u"", u"Zu persönlicher Schreibstil! Sätze mit 'ich', 'wir', 'sie' umschreiben!"),
    u"sentlength":        _MetricExpectation(None       , 17.38 + 3.1, u"", u"Zu viele lange Sätze!"),
    u"sentlengthvar":     _MetricExpectation(8.93 - 2.55, None       , u"Versuche kürze und lange Sätze mehr abzuwechseln!"),
    u"simplepres":        _MetricExpectation(0.64 - 0.12, None       , u"Zu wenig Sätze sind in Präsenz geschrieben!"),
    u"spellcheck":        _MetricExpectation(0.22 - 0.17, 0.22 + 0.17, u"Sehr armer Wortschatz!", u"Entweder zu viele Rechtschreibfehler oder zu viele Fremdwörter!"),
    u"wordlength":        _MetricExpectation(None       , 5.81 + 0.38, u"", u"Versuche kürzere Wörter zu verwenden!"),
}

class DocumentReport(Report):
    """Overview over a single document.
    """
    def __init__(self):
        super(DocumentReport, self).__init__(u"document", u"de", u"Überblick über ein einzelnes Dokument")

    def execute(self, docs, args):
        if len(docs) < 1:
            return u""
        output = list()
        output.append(u"# Dokumentbericht")
        output.append(u"")
        output.append(u"## Metriken")
        output.append(u"")
        doc = docs[0]
        for metric_ID in sorted((_METRIC_EXPECTATIONS.keys())):
            output.append(self._execute_metric(metric_ID, doc))
        output.append(u"")
        output.append(u"## Regeln")
        output.append(u"")
        rule_IDs = [u"introduction", u"subsections", u"floatreference", u"floatcaption"]
        A = Analyzer.instance()
        rules = [A.get(rule=ID) for ID in rule_IDs if A.get(rule=ID) is not None]
        rule_messages = eval_doc(doc, rules)
        if len(rule_messages) == 0:
            output.append(u"Es liegen keine Regelverletzungen vor!")
        else:
            for m in rule_messages:
                output.append(m)
        return u"\n".join(output)

    def _execute_metric(self, metric_ID, node):
        A = Analyzer.instance()
        metric = A.get(metric=metric_ID)
        val = metric.evaluate(node)
        expect = _METRIC_EXPECTATIONS.get(metric_ID, None)
        output = u""
        if expect is not None:
            val_str = str(round(val, ROUND))
            if (expect.low is not None) and (expect.high is not None):
                output = u" * %s %s (erwartet: zw. %.2f und %.2f)" % (metric_ID, val_str, expect.low, expect.high)
            elif expect.low is not None:
                output = u" * %s %s (erwartet: min. %.2f)" % (metric_ID, val_str, expect.low)
            elif expect.high is not None:
                output = u" * %s %s (erwartet: max. %.2f)" % (metric_ID, val_str, expect.high)
            if (expect.low is not None) and val < expect.low:
                output += u"\n     %s" % expect.msg_toolow
            elif (expect.high is not None) and val > expect.high:
                output += u"\n     %s" % expect.msg_toohigh
            else:
                output += u"\n     %s" % expect.msg_ok
        return output

Analyzer.register(DocumentReport())



class DocumentDetailedReport(Report):
    """Detailed analysis of a single document.
    """
    def __init__(self):
        super(DocumentDetailedReport, self).__init__(u"document-detail", u"de", u"Detaillierte Analyse eines Dokuments")

    def execute(self, docs, args):
        output = list()
        return u"\n".join(output)

Analyzer.register(DocumentDetailedReport())
