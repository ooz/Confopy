# coding: utf-8
'''
File: metrics.py
Author: Oliver Zscheyge
Description:
    Language specific metric implementations.
'''

from math import fsum

from confopy.analysis import Metric, Analyzer, SpellChecker, NO_WORDS
from pattern.de import lemma, tenses

# General German metrics

class WordLengthMetric(Metric):
    """Average word length of all words of a Node.
    """
    def __init__(self):
        super(WordLengthMetric, self).__init__(u"wordlength", u"de", u"Word length")

    def evaluate(self, node):
        A = Analyzer.instance()
        #corp = A.get(corpus=u"TIGER")
        words = node.words()
        word_count = len(words)
        word_len = reduce(lambda w, v: w + v, [len(w) for w in words], 0)
        if len(words) > 0:
            return word_len / float(len(words))
        return 0.0
Analyzer.register(WordLengthMetric())


class SpellCheckMetric(Metric):
    """Number of spelling errors relative to number of all words.
    """
    def __init__(self):
        super(SpellCheckMetric, self).__init__(u"spellcheck", u"de", u"Spell errors relative to #words")

    def evaluate(self, node):
        """Value range: [0.0, 1.0]
        """
        checker = SpellChecker(self.language)
        words = [w for w in node.words() if w not in NO_WORDS]
        n_errors = 0
        for w in words:
            if not checker.check(w):
                n_errors += 1
        if len(words) > 0:
            return n_errors / float(len(words))
        return 0.0
Analyzer.register(SpellCheckMetric())


### Wortschatz (auf Lemma reduzieren)

class LexiconMetric(Metric):
    """Number of unique words (lemmata) relative to total number of words.
    """
    def __init__(self):
        super(LexiconMetric, self).__init__(u"lexicon", u"de", u"Number of unique lemmata relative to total #words.")

    def evaluate(self, node):
        words = node.words()
        words_no_no_words = [w for w in words if w not in NO_WORDS]
        A = Analyzer.instance()
        corp = A.get(corpus=u"TIGER")
        tagger = corp.tagger(True)
        tagged_words = tagger.tag(words)
        unique_words = set()
        if len(tagged_words) > 0 and len(words_no_no_words) > 0:
            for w in tagged_words:
                if w[0] not in NO_WORDS:
                    if w[1] and w[1].startswith(u"V"):
                        lemm = lemma(w[0])
                        unique_words.add(lemm)
                    else:
                        unique_words.add(w[0])
            return float(len(unique_words)) / len(words_no_no_words)
        return 0.0
Analyzer.register(LexiconMetric())

### Satzkomplexität
class SentLengthMetric(Metric):
    """Average sentence length.
    """
    def __init__(self):
        super(SentLengthMetric, self).__init__(u"sentlength", u"de", u"Average sentence length")

    def evaluate(self, node):
        A = Analyzer.instance()
        corp = A.get(corpus=u"TIGER")
        sents = node.sents(tokenizer=corp.sent_tokenizer())
        summ = 0
        for s in sents:
            s = [w for w in s if w not in NO_WORDS]
            summ += len(s)
        if len(sents) > 0:
            return summ / len(sents)
        return 0.0
Analyzer.register(SentLengthMetric())

#### mittlere Tiefe des Syntaxbaumes



# Special metrics for scientific texts

### unpersönlicher Schreibstil (sie, wir, ich je Satz zählen)
class PersonalStyleMetric(Metric):

    PERSONAL = [u"ich", u"wir", u"sie"]

    def __init__(self):
        super(PersonalStyleMetric, self).__init__(u"personalstyle", u"de", u"Persönlicher Schreibstil", u"Vorkommen von 'ich', 'wir', 'sie' relativ zur Satzanzahl.")

    def evaluate(self, node):
        words = node.words()
        A = Analyzer.instance()
        corp = A.get(corpus=u"TIGER")
        sents_count = len(node.sents(tokenizer=corp.sent_tokenizer()))
        count = 0
        for w in words:
            low = w.lower()
            if low in PersonalStyleMetric.PERSONAL:
                count += 1
        if sents_count > 0:
            return float(count) / sents_count
        return 0.0
Analyzer.register(PersonalStyleMetric())

#### durchschnittliche Anzahl von Passiv-/"Man"-Konstrukten pro Satz
class ImpersonalStyleMetric(Metric):
    def __init__(self, ID=u"impersonalstyle", lang=u"de", description=u"Unpersönlicher Schreibstil"):
        super(ImpersonalStyleMetric, self).__init__(ID, lang, description)
        self.IMPERSONAL = [u"man"]

    def evaluate(self, node):
        words = node.words()
        A = Analyzer.instance()
        corp = A.get(corpus=u"TIGER")
        sents_count = len(node.sents(tokenizer=corp.sent_tokenizer()))
        count = 0
        for w in words:
            low = w.lower()
            if low in self.IMPERSONAL:
                count += 1
        if sents_count > 0:
            return float(count) / sents_count
        return 0.0
Analyzer.register(ImpersonalStyleMetric())

### Passivkonstrukte mit "werden"
class PassiveConstructsMetric(ImpersonalStyleMetric):
    """docstring for PassiveConstructsMetric"""
    def __init__(self):
        super(PassiveConstructsMetric, self).__init__(u"passiveconstructs", u"de", "Passivkonstrukte mit \"werden\"")
        self.IMPERSONAL = [u"werden"]
Analyzer.register(PassiveConstructsMetric())

### Zeitform (Präsens), Anzahl der Verben in Präs. durch Gesamtanzahl an Verben
class SimplePresentMetric(Metric):
    def __init__(self):
        super(SimplePresentMetric, self).__init__(u"simplepres", u"de", u"Verben im Präsenz im Verhältnis zu #verbs")

    def evaluate(self, node):
        A = Analyzer.instance()
        corp = A.get(corpus=u"TIGER")
        tagger = corp.tagger(True)
        tagged_words = tagger.tag(node.words())
        pres_verbs = 0
        total_verbs = 0
        for w in tagged_words:
            if w[1] and w[1].startswith(u"V"):
                #if w[1].startswith(u"VVFIN") or\
                #   w[1].startswith(u"VAFIN") or\
                #   w[1].startswith(u"VVINF") or\
                #   w[1].startswith(u"VVIZU"): # beinhaltet noch vergangenheit!
                #    pres_verbs += 1
                total_verbs += 1
                tense = tenses(w[0])
                if tense is not []:
                    tense = [t[0] for t in tense]
                    past_count = 0
                    present_count = 0
                    for t in tense:
                        if t == "past":
                            past_count += 1
                        elif t == "present":
                            present_count += 1
                    if present_count > past_count:
                        pres_verbs += 1
                #print w
        if total_verbs > 0:
            return float(pres_verbs) / total_verbs
        return 0.0
Analyzer.register(SimplePresentMetric())

### Vermeidung verstärkender/unpräziser Adverbien (leicht, sehr, viel)
class AdverbModifierMetric(Metric):
    """
    """
    def __init__(self):
        super(AdverbModifierMetric, self).__init__(u"adverbmodifier", u"de", u"Verstärkende/unpräzise Adverbien")

    def evaluate(self, node):
        A = Analyzer.instance()
        corp = A.get(corpus=u"TIGER")
        tagger = corp.tagger(True)
        words = node.words()
        words_no_no_words = [w for w in words if w not in NO_WORDS]
        tagged_words = tagger.tag(words)
        word_count = len(words_no_no_words)
        count = 0
        for w in tagged_words:
            if w[1] and u"ADV-MO" == w[1]:
                count += 1
        if word_count > 0:
            return float(count) / word_count
        return 0.0
Analyzer.register(AdverbModifierMetric())


### Vermeidung toter Verben (Gehören, liegen, beinhalten)
class DeadVerbsMetric(Metric):
    """docstring for DeadVerbsMetric"""
    def __init__(self, ID=u"deadverbs", lang=u"de", description=u"Anzahl toter Verben"):
        super(DeadVerbsMetric, self).__init__(ID, lang, description)
        # weitere tote Verben aus:
        #  http://www.marcoprestel.de/stil12.html
        self.VERBS = [u"gehören", u"liegen", u"beinhalten", u"enthalten", u"befinden", u"geben", u"bewirken", u"bewerkstelligen", u"vergegenwärtigen"]

    def evaluate(self, node):
        words = node.words()
        A = Analyzer.instance()
        corp = A.get(corpus=u"TIGER")
        sents_count = len(node.sents(tokenizer=corp.sent_tokenizer()))
        tagger = corp.tagger(True)
        tagged_words = tagger.tag(words)
        count = 0
        if len(tagged_words) > 0:
            for w in tagged_words:
                if w[1] and w[1].startswith(u"V"):
                    lemm = lemma(w[0])
                    if lemm in self.VERBS:
                        count += 1
            return float(count) / sents_count
        return 0.0
Analyzer.register(DeadVerbsMetric())

class FillerMetric(Metric):
    """Number of fillers relative to total number of words of a given Node.
    """
    def __init__(self):
        super(FillerMetric, self).__init__(u"fillers", u"de", u"Analysiert Füllwortdichte", u"")

    def evaluate(self, node):
        A = Analyzer.instance()
        corp = A.get(corpus=u"TIGER")
        fillers = list()
        if corp:
            fillers = corp.fillers()
        words = node.words()
        words_no_no_words = [w for w in words if w not in NO_WORDS]
        filler_count = 0
        for w in words:
            if w in fillers:
                filler_count += 1
        if len(words_no_no_words) > 0:
            return float(filler_count) / len(words_no_no_words)
        return 0.0

Analyzer.register(FillerMetric())

### Beispiel-/Illustrationsdichte
#### Vorkommnisse von "Beispiel", "beispielsweise", "z.B."
#### nahe beieinander liegende Vorkommen weniger positiv beurteilen (da wahrsch. selbes Bsp.)
class ExampleCountMetric(Metric):
    BSP_INDICATORS = [u"beispiel", u"bsp", u"bsp.", u"zb", u"z.b.", u"beispielsweise", u"bspw", u"bspw."]
    def __init__(self):
        super(ExampleCountMetric, self).__init__(u"examplecount", u"de", u"Zählt Beispiele")

    def evaluate(self, node):
        words = node.words()
        bsp_count = 0
        for w in words:
            lo = w.lower()
            if lo in ExampleCountMetric.BSP_INDICATORS:
                bsp_count += 1
        return bsp_count

Analyzer.register(ExampleCountMetric())


class SentenceLengthVariationMetric(Metric):
    """Determines the variation of sentence length of subsequent sentences.
    """
    def __init__(self):
        super(SentenceLengthVariationMetric, self).__init__(u"sentlengthvar", u"de", u"Variation der Satzlänge", u"")

    def evaluate(self, node):
        A = Analyzer.instance()
        corp = A.get(corpus=u"TIGER")
        sents = node.sents(tokenizer=corp.sent_tokenizer())
        sent_len_diff = 0
        last_sent = None
        for s in sents:
            s = [w for w in s if w not in NO_WORDS]
            if last_sent is not None:
                sent_len_diff += abs(len(last_sent) - len(s))
            last_sent = s
        if len(sents) > 1:
            return sent_len_diff / float(len(sents) - 1)
        return 0.0

Analyzer.register(SentenceLengthVariationMetric())

### Satzinformationsgehalt

