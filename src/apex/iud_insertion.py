"""
Confirm IUD Insertion on specified date
"""
import enum
import logging
import re
from collections import namedtuple


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


Result = namedtuple('Result', 'value correct')


class InsertionStatus(enum.Enum):
    FAILED = 0
    HYPOTHETICAL = 1
    SUCCESS = 2
    LIKELY_SUCCESS = 3
    UNKNOWN = 4
    NO_MENTION = 5


class Pattern:

    def __init__(self, pattern, negates=None, flags=re.IGNORECASE):
        self.pattern = re.compile(pattern, flags)
        self.negates = []
        for negate in negates or []:
            self.negates.append(re.compile(negate, flags))

    def matches(self, text):
        m = self.pattern.search(text)
        if m:
            for negate in self.negates:
                if negate.search(text):
                    return False
            return m
        return False


IUD = Pattern(r'\b(mirena|paragard|iud|ius)\b')
INSERTION = Pattern(r'\b(insert|place)')
STRINGS = Pattern(r'\b(strings)')
NOT_SUCCESSFUL = Pattern(r'(n[o\']t|without|no)\W*(success)')
UNSUCCESSFUL = Pattern(r'(unsuccess|abandon)')
HYPOTHETICAL = Pattern(r'(following|remember)')
POST_SUCCESS = Pattern(r'(success|length of string|strings (cut|trim)|iud was( then)? insert)')
PRE_SUCCESS = Pattern(r'(without(\W*any)?\W*(difficult|problem)|as usual|usual( sterile)? fashion|strings were trimmed|'
                      r'per manufacturer[\'s]*\W*recommend)')
POST_OP = Pattern(r'(you think are related to the iud|check the (iud )?strings|'
                  r'have your iud removed or replaced)')
HISTORICAL = Pattern(r'(in the past|previous|months ago|days ago|last week|last month)')
APPOINTMENT = Pattern(r'(appt|appointment)')
DATE = Pattern(r'(\d{1,2}/\d{1,2}|january|february|march|'
               r'april|may|june|july|august|sept(ember)?|october|november|december|20\d{2})',
               negates=[r'\b(exp|expires?)'])
NEGATED = Pattern(r'not\W*inserted')


def classify_result(res: InsertionStatus):
    if res == InsertionStatus.SUCCESS:
        return 1
    elif res == InsertionStatus.LIKELY_SUCCESS:
        return 0
    elif res == InsertionStatus.FAILED:
        return -1
    elif res == InsertionStatus.HYPOTHETICAL:
        return -1
    elif res == InsertionStatus.NO_MENTION:
        return -1
    elif res == InsertionStatus.UNKNOWN:
        return -1
    return 0


def confirm_iud_insertion(document: Document, expected=None):
    value = determine_iud_insertion(document)
    res = classify_result(value)
    if expected is None:
        return Result(res, None)
    elif res == expected:
        return Result(res, res == expected)
    else:  # failed
        logging.warning(f'{document.name}:{value}=={expected}:{document.matches}')
        return Result(res, res == expected)


def determine_iud_insertion(document: Document):
    # discusses iud
    if document.has_patterns(IUD, INSERTION, has_all=True):
        section = document.select_sentences_with_patterns(IUD, INSERTION, STRINGS,
                                                          negation=[HISTORICAL, APPOINTMENT, DATE, NEGATED],
                                                          neighboring_sentences=1)
        if section:
            if section.has_patterns(PRE_SUCCESS):
                return InsertionStatus.SUCCESS
            elif section.has_patterns(UNSUCCESSFUL, NOT_SUCCESSFUL):
                return InsertionStatus.FAILED
            elif section.has_patterns(HYPOTHETICAL):
                return InsertionStatus.HYPOTHETICAL
            elif section.has_patterns(POST_SUCCESS):
                return InsertionStatus.SUCCESS
            elif section.has_patterns(POST_OP):
                return InsertionStatus.LIKELY_SUCCESS
            else:
                return InsertionStatus.UNKNOWN
        else:
            return InsertionStatus.UNKNOWN
    return InsertionStatus.NO_MENTION
