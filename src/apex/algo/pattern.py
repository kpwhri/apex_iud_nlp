import re
from copy import copy


class Match:

    def __init__(self, match, groups=None):
        self.match = match
        self._groups = groups

    def group(self, *index):
        if not self._groups or not index or len(index) == 1 and index[0] == 0:
            return self.match.group(*index)
        res = []
        if not isinstance(index, tuple):
            index = (index,)
        for idx in index:
            if idx == 0:
                res.append(self.match.group())
            else:
                res.append(self._groups[idx-1])

    def groups(self):
        if not self._groups:
            return self.match.groups()
        else:
            return tuple(self._groups)


class Pattern:

    def __init__(self, pattern, negates=None, space_replace=r'\W*',
                 capture_length=None,
                 flags=re.IGNORECASE):
        """

        :param pattern:
        :param negates:
        :param space_replace:
        :param capture_length: for 'or:d' patterns, this is the number
            of actual capture groups (?:(this)|(that)|(thes))
            has capture_length = 1
            None: i.e., capture_length == max
        :param flags:
        """
        if space_replace:
            pattern = space_replace.join(pattern.split(' '))
        self.pattern = re.compile(pattern, flags)
        self.negates = []
        for negate in negates or []:
            if space_replace:
                negate = space_replace.join(negate.split(' '))
            self.negates.append(re.compile(negate, flags))
        self.capture_length = capture_length

    def matches(self, text, ignore_negation=False):
        m = self.pattern.search(text)
        if m:
            if not ignore_negation:
                for negate in self.negates:
                    if negate.search(text):
                        return False

            return Match(m, groups=self._compress_groups(m))
        return False

    def _compress_groups(self, m):
        if self.capture_length:
            groups = m.groups()
            assert len(groups) % self.capture_length == 0
            for x in zip(*[iter(m.groups())] * self.capture_length):
                if x[0] is None:
                    continue
                else:
                    return x
        else:
            return None

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
        """

        :param name:
        :param file:
        :param text:
        :param encoding:
        """
        self.name = name
        self.text = text
        self.matches = MatchCask()
        if file:
            with open(file, encoding=encoding) as fh:
                self.text = fh.read()
        if not self.text:
            raise ValueError(f'Missing text for {name}')
        self.sentences = [Sentence(x, self.matches) for x in self.text.split('\n') if x.strip()]

    def has_pattern(self, pat, ignore_negation=False):
        m = pat.matches(self.text, ignore_negation=ignore_negation)
        if m:
            self.matches.add(m)
        return bool(m)

    def get_pattern(self, pat, index=0):
        m = pat.matches(self.text)
        if m:
            self.matches.add(m)
            if not isinstance(index, (list, tuple)):
                index = (index,)
            return m.group(*index)
        return m

    def get_patterns(self, *pats, index=0, names=None):
        """

        :param pats:
        :param index:
        :param names: if included, return name of matched pattern
            list same length as number of patterns
        :return:
        """
        for i, pat in enumerate(pats):
            res = self.get_pattern(pat, index=index)
            if res:
                if names:
                    return res, names[i]
                return res
        return None

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
            if sents:
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
