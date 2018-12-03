import re
from copy import copy


class Pattern:

    def __init__(self, pattern, negates=None, space_replace=r'\W*', flags=re.IGNORECASE):
        if space_replace:
            pattern = space_replace.join(pattern.split(' '))
        self.pattern = re.compile(pattern, flags)
        self.negates = []
        for negate in negates or []:
            if space_replace:
                negate = space_replace.join(negate.split(' '))
            self.negates.append(re.compile(negate, flags))

    def matches(self, text, ignore_negation=False):
        m = self.pattern.search(text)
        if m:
            if not ignore_negation:
                for negate in self.negates:
                    if negate.search(text):
                        return False
            return m
        return False

    def matchgroup(self, text, index=0):
        m = self.matches(text)
        if m:
            return m.group(0)
        return m


class MatchCask:

    def __init__(self):
        self.matches = []

    def add(self, m):
        self.matches.append(m)

    def add_all(self, matches):
        self.matches += matches

    def copy(self):
        mc = MatchCask()
        mc.matches = copy(self.matches)
        return mc

    def __repr__(self):
        return repr(set(m.group() for m in self.matches))

    def __str__(self):
        return str(set(m.group() for m in self.matches))


class Sentence:

    def __init__(self, text, mc: MatchCask):
        self.text = text
        self.matches = mc

    def has_pattern(self, pat, ignore_negation=False):
        m = pat.matches(self.text, ignore_negation=ignore_negation)
        if m:
            self.matches.add(m)
        return bool(m)

    def has_patterns(self, *pats, has_all=False, ignore_negation=False):
        for pat in pats:
            if has_all and not self.has_pattern(pat, ignore_negation=ignore_negation):
                return False
            elif not has_all and self.has_pattern(pat, ignore_negation=ignore_negation):
                return True
        return has_all

    def get_pattern(self, pat, index=0):
        m = pat.matches(self.text)
        if m:
            self.matches.add(m)
            return m.group(index)
        return m


class Section:

    def __init__(self, sentences, mc: MatchCask, add_matches=False):
        """

        :param sentences:
        :param mc:
        :param add_matches: use if you are copying data rather than
            passing around the same match object (default)
        """
        self.sentences = sentences
        self.text = '\n'.join(sent.text for sent in sentences)
        self.matches = mc
        if add_matches:
            for sent in self.sentences:
                self.matches.add_all(sent.matches.matches)

    def has_pattern(self, pat, ignore_negation=False):
        m = pat.matches(self.text, ignore_negation=ignore_negation)
        if m:
            self.matches.add(m)
        return bool(m)

    def get_pattern(self, pat, index=0):
        m = pat.matches(self.text)
        if m:
            self.matches.add(m)
            return m.group(index)
        return m

    def has_patterns(self, *pats, has_all=False, ignore_negation=False):
        for pat in pats:
            if has_all and not self.has_pattern(pat, ignore_negation=ignore_negation):
                return False
            elif not has_all and self.has_pattern(pat, ignore_negation=ignore_negation):
                return True
        return has_all


class Document:

    def __init__(self, name, file=None, text=None, encoding='utf8'):
        self.name = name
        self.text = text
        self.matches = MatchCask()
        if file:
            with open(file, encoding=encoding) as fh:
                self.text = fh.read()
        self.sentences = [Sentence(x, self.matches) for x in self.text.split('\n') if x.strip()]

    def has_pattern(self, pat, ignore_negation=False):
        m = pat.matches(self.text, ignore_negation=ignore_negation)
        if m:
            self.matches.add(m)
        return bool(m)

    def get_pattern(self, pat, index):
        m = pat.matches(self.text)
        if m:
            self.matches.add(m)
            return m.group(index)
        return m

    def has_patterns(self, *pats, has_all=False, ignore_negation=False):
        for pat in pats:
            if has_all and not self.has_pattern(pat, ignore_negation):
                return False
            elif not has_all and self.has_pattern(pat, ignore_negation):
                return True
        return has_all

    def select_sentences_with_patterns(self, *pats, negation=None, has_all=False,
                                       neighboring_sentences=0):
        for i, sentence in enumerate(self.sentences):
            sents = set()
            if sentence.has_patterns(*pats, has_all=has_all):
                if negation:
                    if sentence.has_patterns(*negation):
                        continue
                sents.add(i)
                for j in range(neighboring_sentences):
                    if i + j < len(self.sentences):
                        sents.add(i + j)
                    if i - j >= 0:
                        sents.add(i - j)
            yield Section([self.sentences[i] for i in sorted(list(sents))], self.matches)

    def select_all_sentences_with_patterns(self, *pats, negation=None, has_all=False, get_range=False,
                                           neighboring_sentences=0):
        sents = set()
        for i, sentence in enumerate(self.sentences):
            if sentence.has_patterns(*pats, has_all=has_all):
                if negation:
                    if sentence.has_patterns(*negation):
                        continue
                sents.add(i)
                for j in range(neighboring_sentences):
                    if i + j < len(self.sentences):
                        sents.add(i + j)
                    if i - j >= 0:
                        sents.add(i - j)
        sents = sorted(list(sents))
        if not sents:
            return None
        elif len(sents) == 1:
            return Section([self.sentences[sents[0]]], self.matches)
        elif get_range:
            return Section(self.sentences[sents[0]:sents[-1] + 1], self.matches)
        else:
            return Section([self.sentences[i] for i in sents], self.matches)
