# coding: utf-8
'''
File: reports.py
Author: Oliver Zscheyge
Description:
    Implementation of all reports
'''

from confopy.analysis import Report, Analyzer, mean_stdev
from confopy.analysis.rule import eval_doc


METRIC_NAMES = [u"wordlength", u"spellcheck", u"lexicon", u"sentlength", u"ari", u"personalstyle", u"impersonalstyle", u"passiveconstructs", u"simplepres", u"adverbmodifier", u"deadverbs", u"fillers", u"examplecount", u"sentlengthvar"]
RULE_NAMES = [u"introduction", u"subsections", u"floatreference", u"floatreferencebefore", u"floatcaption"]
MAX_METRIC_STR_LEN = reduce(max, [len(name) for name in METRIC_NAMES])
PAD = 2
METRIC_COL_WIDTH = MAX_METRIC_STR_LEN + PAD

ROUND = 2
class DocumentAverages(Report):
    """Average metric values for multiple documents.
    """
    def __init__(self):
        super(DocumentAverages, self).__init__(u"docsavg",
                                               u"de",
                                               u"Durchschnitt über mehrere Dokumente",
                                               u"""\
Evaluiert die Metriken für mehrere Dokumente, berechnet den Durchschnitt
    und die Standardabweichung.
    Listet in der letzten Spalte die Metrikwerte des TIGER-Corpus (deutsche
    Sprachreferenz).
    Unterstützt die Option --latex.""")

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
            output.append(u"# Bericht \"%s\"" % self.ID)
            output.append(u"")
            output.append(u" * MEAN:  der Mittelwert über alle Dokumente")
            output.append(u" * STDEV: die dazugehörige Standardabweichung")
            output.append(u" * TIGER: Metrikwert für die deutsche Sprachereferenz,")
            output.append(u"          den TIGER-Corpus")
            output.append(u"")
            output.append(u"%s | MEAN  | STDEV | TIGER" % u"METRIC".ljust(METRIC_COL_WIDTH))
            output.append(u"%s-+-------+-------+------" % u"".ljust(METRIC_COL_WIDTH, u"-"))
        for i in range(len(metrics)):
            # Execute metrics on reference corpus
            val = metrics[i].evaluate(corp)
            val = round(val, ROUND)
            if args.latex:
                output.append(u"    %s & %s & %s & %s \\\\" % (metric_names[i].ljust(METRIC_COL_WIDTH), stats[i][0], stats[i][1], val))
            else:
                output.append(u"%s | %05.2f | %05.2f | %05.2f" % (metric_names[i].ljust(METRIC_COL_WIDTH), stats[i][0], stats[i][1], val))
        if args.latex:
            output.append(u"\\end{tabular}")
        return u"\n".join(output)

Analyzer.register(DocumentAverages())

class DocumentComparison(Report):
    """Compares the metrics of 2 documents side by side
    """
    PAD = 2

    def __init__(self):
        super(DocumentComparison, self).__init__(u"doccomp",
                                                 u"de",
                                                 u"Vergleicht Vorher-/Nachher-Versionen",
                                                 u"""\
Benötigt eine gerade Anzahl n an Dokumenten (mind. 2).
    Vergleicht das erste Dokument mit dem (n / 2) + 1-sten Dokument usw.
    Bei 2 Dokumenten werden jeweils die Metriken bestimmt und gegenüber-
    gestellt.
    Bei mehr als 2 Dokumenten wird gezählt, wie häufig sich Metrikwerte
    verringert/erhöht haben oder gleich geblieben sind.
    Unterstützt die Option --latex.""")

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
                output.append(u"# Bericht \"%s\""% self.ID)
                output.append(u"")
                output.append(u" * PROGRESS: Vorher- --> Nachher-Wert.")
                output.append(u"             (+) ... Erhöhung         ")
                output.append(u"             (-) ... Verringerung     ")
                output.append(u"             (=) ... gleichbleibend   ")
                output.append(u"")
                output.append(u"%s | PROGRESS" % u"METRIC".ljust(METRIC_COL_WIDTH))
                output.append(u"%s-+---------------------" % u"".ljust(METRIC_COL_WIDTH, u"-"))
                for m in metrics:
                    vals = [m.evaluate(doc) for doc in docs]
                    progress = u"="
                    if vals[0] > vals[1]:
                        progress = u"-"
                    elif vals[0] < vals[1]:
                        progress = u"+"
                    output.append(u"%s | %05.2f --> %05.2f  (%s)" % (m.ID.ljust(METRIC_COL_WIDTH), vals[0], vals[1], progress))

            else:
                half = len(docs) / 2
                if args.latex:
                    output.append(u"\\begin{tabular}{l|l l|l l|r}")
                    output.append(u"\\multirow{2}{*}{\\textbf{Metrik}} & \\multicolumn{2}{|c|}{\\textbf{Erhöhung}} & \\multicolumn{2}{|c|}{\\textbf{Verringerung}} & \\textbf{gleichbleibend} \\\\")
                    output.append(u"                                 & \\multicolumn{1}{|c}{$\\#$} & \\multicolumn{1}{c|}{$\\Delta$} & \\multicolumn{1}{|c}{$\\#$} & \\multicolumn{1}{c|}{$\\Delta$} & \\multicolumn{1}{c}{$\\#$} \\\\")
                    output.append(u"    \\hline")
                else:
                    output.append(u"# Bericht \"%s\"" % self.ID)
                    output.append(u"")
                    output.append(u" * +:      Anzahl an Metrikerhöhungen")
                    output.append(u" * DELTA+: Durchschnittliche Erhöhung um diesen Wert")
                    output.append(u" * -:      Anzahl an Metrikverringerungen")
                    output.append(u" * DELTA-: Durchschnittliche Verringerung um diesen Wert")
                    output.append(u" * =:      Anzahl an Dokumentpaaren, bei denen der")
                    output.append(u"           Metrikwert gleich geblieben ist")
                    output.append(u"")
                    output.append(u"%s | +  | DELTA+ | -  | DELTA- | =  " % u"METRIC".ljust(METRIC_COL_WIDTH))
                    output.append(u"%s-+----+--------+----+--------+----" % u"".ljust(METRIC_COL_WIDTH, u"-"))
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
                        output.append(u"%s | %02d | %06.3f | %02d | %06.3f | %02d" % (m.ID.ljust(METRIC_COL_WIDTH), counts[0], avg_diffs[0], counts[1], avg_diffs[1], counts[2]))
                if args.latex:
                    output.append(u"\\end{tabular}")
        return u"\n".join(output)

Analyzer.register(DocumentComparison())



class MultiDocumentReport(Report):
    """Metric values for multiple documents.
    """
    def __init__(self,
                 ID=u"multidoc",
                 lang=u"de",
                 brief=u"Überblick über mehrere Dokumente",
                 description=u"""\
Berechnet die Metrikwerte für mehrere Dokumente.
    Zählt zusätzlich die Anzahl der Regelverletzungen und der
    Über-/Unterschreitungen der Metrikerwartungsbereiche.
    Unterstützt die Option --latex."""):
        super(MultiDocumentReport, self).__init__(ID, lang, brief, description)

    def compute_exceedances(self, metric_names, results):
        exceedances = list()
        for i in range(len(metric_names)):
            metric_name = metric_names[i]
            expect = _METRIC_EXPECTATIONS[metric_name]
            metric_results = results[i]
            exceedances_for_metric = list()
            for val in metric_results:
                val = round(val, 2)
                if ((expect.low is not None) and val < expect.low) or ((expect.high is not None) and val > expect.high):
                    exceedances_for_metric.append(1)
                else:
                    exceedances_for_metric.append(0)
            exceedances.append(exceedances_for_metric)
        return exceedances

    def execute(self, docs, args):
        output = []
        metric_names = METRIC_NAMES
        A = Analyzer.instance()
        metrics = [A.get(metric=m) for m in metric_names]
        metrics = [m for m in metrics if m != None]
        corp = A.get(corpus=u"TIGER")
        results = list()
        for m in metrics:
            results.append([m.evaluate(d) for d in docs])

        exceedances = self.compute_exceedances(metric_names, results)
        exceedances_transposed = list(map(list, zip(*exceedances)))

        # Metric matrix output
        doc_numbers = range(1, len(docs) + 1)
        if args.latex:
            tabular_format_str = [u" r" for d in docs]
            tabular_format_str = u"".join(tabular_format_str)
            output.append(u"\\begin{tabular}{l|%s}" % tabular_format_str)
            docs_header_str = map(u"& doc%02d ".__mod__, doc_numbers)
            docs_header_str = u"".join(docs_header_str)
            output.append(u"    Metrik %s\\\\" % docs_header_str)
            output.append(u"    \\hline")
            for i in range(len(metrics)):
                value_str = u""
                for doc_nr in range(len(results[i])):
                    if exceedances[i][doc_nr] == 1:
                        value_str = value_str + u"& \emph{%.2f} " % results[i][doc_nr]
                    else:
                        value_str = value_str + u"& %.2f " % results[i][doc_nr]
                #value_str = map(u"& %.2f ".__mod__, results[i])
                #value_str = u"".join(value_str)
                output.append(u"    %s %s\\\\" % (metric_names[i].ljust(METRIC_COL_WIDTH), value_str))
        else:
            output.append(u"# Bericht \"%s\"" % self.ID)
            output.append(u"")
            docs_header_str = map(u"| doc%02d ".__mod__, doc_numbers)
            docs_header_str = u"".join(docs_header_str)
            output.append(u"%s%s" % (u"METRIC".ljust(METRIC_COL_WIDTH), docs_header_str))
            dash_length = len(docs_header_str) - 2
            if dash_length < 0:
                dash_length = 0
            output.append(u"%s+%s" % (u"".ljust(METRIC_COL_WIDTH, u"-"), u"".ljust(dash_length, u"-")))
            for i in range(len(metrics)):
                value_str = map(u"| %05.2f ".__mod__, results[i])
                value_str = u"".join(value_str)
                output.append(u"%s%s" % (metric_names[i].ljust(METRIC_COL_WIDTH), value_str))

        # Exceedances/shortfalls
        exceedances_counts = map(sum, exceedances_transposed)
        if args.latex:
            output.append(u"    \\hline")
            exceedances_str = map(u"& %d ".__mod__, exceedances_counts)
            exceedances_str = u"".join(exceedances_str)
            output.append(u"    %s %s\\\\" % (u"Überschreitungen".ljust(METRIC_COL_WIDTH), exceedances_str))
        else:
            output.append(u"%s+%s" % (u"".ljust(METRIC_COL_WIDTH, u"-"), u"".ljust(dash_length, u"-")))
            exceedances_str = map(u"|    %02d ".__mod__, exceedances_counts)
            exceedances_str = u"".join(exceedances_str)
            output.append(u"%s%s" % (u"Transgressions".ljust(METRIC_COL_WIDTH), exceedances_str))

        # Rule violations
        rule_IDs = RULE_NAMES
        rules = [A.get(rule=ID) for ID in rule_IDs if A.get(rule=ID) is not None]
        violated_rule_counts = [len(eval_doc(doc, rules)) for doc in docs]

        if args.latex:
            violated_rule_counts_str = map(u"& %d ".__mod__, violated_rule_counts)
            violated_rule_counts_str = u"".join(violated_rule_counts_str)
            output.append(u"    %s %s\\\\" % (u"Regelverletzungen".ljust(METRIC_COL_WIDTH), violated_rule_counts_str))
            output.append(u"\\end{tabular}")
        else:
            violated_rule_counts_str = map(u"|    %02d ".__mod__, violated_rule_counts)
            violated_rule_counts_str = u"".join(violated_rule_counts_str)
            output.append(u"%s%s" % (u"Violated rules".ljust(METRIC_COL_WIDTH), violated_rule_counts_str))

        return u"\n".join(output)

Analyzer.register(MultiDocumentReport())



class _MetricExpectation(object):
    """Stores expected metric values.
    """
    def __init__(self, low=None, high=None, msg_toolow=u"", msg_toohigh=u"", msg_ok=u"OK!"):
        """Initializer.
        Args:
            low:         Lowest expected metric value.
            high:        Highest expected metric value.
            msg_toolow:  Message to print when metric value is lower than low.
            msg_toohigh: Message to print when metric value is higher than high.
            msg_ok:      Message to print when metric value is between low and high.
        """
        super(_MetricExpectation, self).__init__()
        self.low = low
        self.high = high
        self.msg_toolow = msg_toolow
        self.msg_toohigh = msg_toohigh
        self.msg_ok = msg_ok

_METRIC_EXPECTATIONS = {
    u"adverbmodifier":    _MetricExpectation(None       , 0.03 + 0.01, u"", u"Versuche weniger verstärkende/unpräzise Adverbien zu verwenden!"),
    u"ari":               _MetricExpectation(None       , 67.6 + 4.36, u"", u"Erschwerte Lesbarkeit (zu lange Wörter/Sätze!)"),
    u"deadverbs":         _MetricExpectation(None       , 0.03 + 0.03, u"", u"Versuche weniger tote Verben wie gehören, liegen, befinden, beinhalten, geben, bewirken etc. zu verwenden!"),
    u"examplecount":      _MetricExpectation(1.83 - 0.83, None       , u"Versuche mehr Beispiele zu nennen!", u""),
    u"fillers":           _MetricExpectation(None       , 0.02 + 0.01, u"", u"Zu viele Füllwörter!"),
    u"impersonalstyle":   _MetricExpectation(None       , 0.02 + 0.03, u"", u"Zu viele Sätze mit 'man'."),
    u"lexicon":           _MetricExpectation(0.51 - 0.05, 0.51 + 0.05, u"Zu geringer Wortschatz", u"Zu vielfältiger Wortschatz (viele Fremdwörter?)"),
    u"passiveconstructs": _MetricExpectation(None       , 0.27 + 0.1 , u"", u"Versuche mehr aktive Sätze zu bilden!"),
    u"personalstyle":     _MetricExpectation(None       , 0.03 + 0.03, u"", u"Zu persönlicher Schreibstil! Sätze mit 'ich', 'wir', 'sie' umschreiben!"),
    u"sentlength":        _MetricExpectation(None       , 14.6 + 2.78, u"", u"Zu viele lange Sätze!"),
    u"sentlengthvar":     _MetricExpectation(7.68 - 2.41, None       , u"Versuche kurze und lange Sätze mehr abzuwechseln!"),
    u"simplepres":        _MetricExpectation(0.8  - 0.06, None       , u"Zu wenig Sätze sind in Präsenz geschrieben!"),
    u"spellcheck":        _MetricExpectation(0.15 - 0.05, 0.15 + 0.05, u"Sehr armer Wortschatz!", u"Entweder zu viele Rechtschreibfehler oder zu viele Fremdwörter!"),
    u"wordlength":        _MetricExpectation(None       , 6.02 + 0.26, u"", u"Versuche kürzere Wörter zu verwenden!"),
}

class DocumentReport(Report):
    """Overview over a single document.
    """
    def __init__(self,
                 ID=u"document",
                 lang=u"de",
                 brief=u"Überblick über ein einzelnes Dokument",
                 description=u"""\
Berechnet die Metriken für ein Dokument und überprüft die Regeln.
    Kann auch auf mehreren Dokumenten nacheinander ausgeführt werden."""):
        super(DocumentReport, self).__init__(ID, lang, brief, description)

    def execute(self, docs, args):
        if len(docs) < 1:
            return u""
        output = []
        for doc in docs:
            output.append(u"# Dokumentbericht")
            output.append(u"")
            output.append(u"## Metriken")
            output.append(u"")
            for metric_ID in sorted((_METRIC_EXPECTATIONS.keys())):
                output.append(self._execute_metric(metric_ID, doc))
            output.append(u"")
            output.append(u"## Regeln")
            output.append(u"")
            rule_IDs = RULE_NAMES
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



class SectionsReport(DocumentReport):
    """Detailed analysis of a single document.
    """
    def __init__(self):
        super(SectionsReport, self).__init__(u"sections",
                                             u"de",
                                             u"Abschnittsweise Analyse eines Dokuments",
                                             u"""\
Berechnet die Metriken für jedes Kapitel einzeln.""")

    def execute(self, docs, args):
        output = list()
        output.append(u"# Abschnittsweiser Bericht")
        output.append(u"")
        doc = docs[0]
        sections = doc.sections()
        for sec in sections:
            output.append(u"## " + sec.title)
            output.append(u"")
            for metric_ID in sorted(_METRIC_EXPECTATIONS.keys()):
                output.append(self._execute_metric(metric_ID, sec))
            output.append(u"")

        return u"\n".join(output)

Analyzer.register(SectionsReport())
