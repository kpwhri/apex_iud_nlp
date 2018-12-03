from apex.algo.pattern import Document, Pattern
from apex.algo.result import Result, Status

iuds = r'\b(iuds?|intrauterine( contraceptive)? devices?)'
lng_iuds = r'(lng ius|levonorgestrel( (releasing|rlse))? (intrauterine|us))'
brand = r'(mirena|paragu?ard|skyla|liletta|copper)'
embedded = r'([ie]mbedded|impacted)'
# removed: |foreign body
migrated = r'\b(stuck|migrat\w+|extrauterine|omentum|displac\w+|(intra)?peritoneal)'
boilerplate = r'\b(complication|warning|information|review|side effect|counsel|sign|infection|ensure|cramps)'
hypothetical = r'\b(unlikely|improbable|potential|if\b|suspect|chance|may\b|risk|afraid|concern)'
negation = r'(no evidence|without|r/o|rule out|normal|\bnot?\b|\bor\b)'

impact_neg = r'(cerumen|tympanic|ear|hormon\w+)'

PERFORATION = Pattern(r'perforat(ion|ed|e)s?', negates=[boilerplate, hypothetical, negation, impact_neg])
PARTIAL_PERFORATION = Pattern(r'partial(ly)? perforat(ion|ed|e)s?',
                              negates=[boilerplate, hypothetical, negation, impact_neg])
IUD = Pattern(f'({iuds}|{lng_iuds}|{brand})')
EMBEDDED = Pattern(f'({embedded})', negates=[boilerplate, hypothetical, negation, impact_neg])
MIGRATED = Pattern(f'{migrated}', negates=[boilerplate, hypothetical, negation])

years_ago = r'(?:\d+ (?:year|yr|week|wk|month|mon|day)s? (?:ago|before|previous))'
date_pat = r'\d+[-/]\d+[-/]\d+'
date2_pat = r'\d+[/]\d+'
month_pat = r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)\w*(?:\W*\d{1,2})?\W*\d{4}'
month_only_pat = r'in\b(?:jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)\w*'
DATE_PAT = Pattern(f'({years_ago}|{date_pat}|{date2_pat}|{month_pat}|{month_only_pat})')


class PerforationStatus(Status):
    NONE = 0
    PERFORATION = 1
    EMBEDDED = 2
    UNKNOWN = 3
    MIGRATED = 4
    PARTIAL_PERFORATION = 5
    SKIP = 99


def classify_result(res: PerforationStatus, date):
    if res == PerforationStatus.PERFORATION:
        if date:
            return 0
        return 1
    elif res == PerforationStatus.EMBEDDED:
        if date:
            return 0
        return 1
    return -1


def confirm_iud_perforation(document: Document, expected=None):
    for value, text, date in determine_iud_perforation(document):
        res = classify_result(value, date)
        yield Result(value, res, expected, text, extras=date)


def determine_iud_perforation(document: Document):
    if document.has_patterns(PERFORATION, EMBEDDED, MIGRATED, ignore_negation=True):
        # see if any sentences that contain "IUD" also contain perf/embedded
        for section in document.select_sentences_with_patterns(IUD):
            date = section.get_pattern(DATE_PAT)
            if section.has_patterns(PARTIAL_PERFORATION):
                yield PerforationStatus.PARTIAL_PERFORATION, section.text, date
            elif section.has_patterns(PERFORATION):
                yield PerforationStatus.PERFORATION, section.text, date
            elif section.has_patterns(EMBEDDED):
                yield PerforationStatus.EMBEDDED, section.text, date
            elif section.has_patterns(MIGRATED):
                yield PerforationStatus.MIGRATED, section.text, date
        yield PerforationStatus.NONE, document.text, None
    else:
        yield PerforationStatus.SKIP, None, None
