import re


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

    def matches(self, text):
        m = self.pattern.search(text)
        if m:
            for negate in self.negates:
                if negate.search(text):
                    return False
            return m
        return False


class MatchCask:

    def __init__(self):
        self.matches = []

    def add(self, m):
        self.matches.append(m)

    def __repr__(self):
        return repr(set(m.group() for m in self.matches))

    def __str__(self):
        return str(set(m.group() for m in self.matches))


class Sentence:

    def __init__(self, text, mc: MatchCask):
        self.text = text
        self.matches = mc

    def has_pattern(self, pat):
        m = pat.matches(self.text)
        if m:
            self.matches.add(m)
        return bool(m)

    def has_patterns(self, *pats, has_all=False):
        for pat in pats:
            if has_all and not self.has_pattern(pat):
                return False
            elif not has_all and self.has_pattern(pat):
                return True
        return has_all


class Section:

    def __init__(self, sentences, mc: MatchCask):
        self.sentences = sentences
        self.text = '\n'.join(sent.text for sent in sentences)
        self.matches = mc

    def has_pattern(self, pat):
        m = pat.matches(self.text)
        if m:
            self.matches.add(m)
        return bool(m)

    def has_patterns(self, *pats, has_all=False):
        for pat in pats:
            if has_all and not self.has_pattern(pat):
                return False
            elif not has_all and self.has_pattern(pat):
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

    def has_pattern(self, pat):
        m = pat.matches(self.text)
        if m:
            self.matches.add(m)
        return bool(m)

    def has_patterns(self, *pats, has_all=False):
        for pat in pats:
            if has_all and not self.has_pattern(pat):
                return False
            elif not has_all and self.has_pattern(pat):
                return True
        return has_all

    def select_sentences_with_patterns(self, *pats, negation=None, has_all=False, get_range=False,
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
            return Section(self.sentences, self.matches)
        elif get_range:
            return Section(self.sentences[sents[0]:sents[-1] + 1], self.matches)
        else:
            return Section([self.sentences[i] for i in sents], self.matches)
