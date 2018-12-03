import enum

from apex.algo.pattern import Document, Pattern
from apex.algo.result import Result, Status

iuds = r'\b(iuds?|intrauterine( contraceptive)? devices?)'
lng_iuds = r'(lng ius|levonorgestrel( (releasing|rlse))? (intrauterine|us))'
brand = r'(mirena|paragu?ard|skyla|liletta|copper)'
embedded = r'([ie]mbedded|impacted)'
# removed: |foreign body
migrated = r'\b(stuck|migrat\w+|extrauterine|omentum|displac\w+|(intra)?peritoneal)'
hypothetical = r'\b(risk|complication|warning|information|review|side effect|counsel|sign|chance)'
negation = r'(no evidence|without|r/o|rule out|normal|unlikely|improbable|potential|if|ensure|not?)'

impact_neg = r'(cerumen|tympanic|ear)'

PERFORATION = Pattern(r'perforat(ion|ed|e)s?', negates=[hypothetical, negation, impact_neg])
IUD = Pattern(f'({iuds}|{lng_iuds}|{brand})')
EMBEDDED = Pattern(f'({embedded})', negates=[hypothetical, negation, impact_neg])
MIGRATED = Pattern(f'{migrated}', negates=[hypothetical, negation])

years_ago = r'(?:\d+ (?:year|yr|week|wk|month|mon|day)s? (?:ago|before|previous))'
date_pat = r'\d+[-/]\d+(?:[-/]\d+)'
month_pat = r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)\w*(?:\W*\d{4})?'
DATE_PAT = Pattern(f'({years_ago}|{date_pat}|{month_pat})')


class PerforationStatus(Status):
    NONE = 0
    PERFORATION = 1
    EMBEDDED = 2
    UNKNOWN = 3
    MIGRATED = 4
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
    value, text, date = determine_iud_perforation(document)
    res = classify_result(value, date)
    return Result(value, res, expected, text, extras=date)


def determine_iud_perforation(document: Document):
    if document.has_patterns(PERFORATION, EMBEDDED, MIGRATED):
        # see if any sentences that contain "IUD" also contain perf/embedded
        section = document.select_sentences_with_patterns(IUD)
        if section:
            date = section.get_pattern(DATE_PAT)
            if section.has_patterns(PERFORATION):
                return PerforationStatus.PERFORATION, section.text, date
            elif section.has_patterns(EMBEDDED):
                return PerforationStatus.EMBEDDED, section.text, date
            elif section.has_patterns(MIGRATED):
                return PerforationStatus.MIGRATED, section.text, date
        return PerforationStatus.NONE, document.text, None
    else:
        return PerforationStatus.SKIP, None, None
