import enum

from apex.algo.pattern import Document, Pattern
from apex.algo.result import Result, Status

iuds = r'\b(iuds?|intrauterine( contraceptive)? devices?)'
lng_iuds = r'(lng ius|levonorgestrel( (releasing|rlse))? (intrauterine|us))'
brand = r'(mirena|paragu?ard|skyla|liletta|copper)'
embedded = r'([ie]mbedded|impacted)'
# removed: |foreign body
migrated = r'\b(stuck|migrat\w+|extrauterine|omentum|displac\w+|(intra)?peritoneal)'
hypothetical = r'\b(risk|complication|warning|information|review|side effect|counsel)'
negation = r'(no evidence|without|r/o|rule out|normal)'

PERFORATION = Pattern(r'perforat(ion|ed|e)s?', negates=[hypothetical, negation])
IUD = Pattern(f'({iuds}|{lng_iuds}|{brand})')
EMBEDDED = Pattern(f'({embedded})', negates=[hypothetical, negation])
MIGRATED = Pattern(f'{migrated}', negates=[hypothetical, negation])


class PerforationStatus(Status):
    NONE = 0
    PERFORATION = 1
    EMBEDDED = 2
    UNKNOWN = 3
    MIGRATED = 4
    SKIP = 99


def classify_result(res: PerforationStatus):
    if res == PerforationStatus.PERFORATION:
        return 1
    elif res == PerforationStatus.EMBEDDED:
        return 1
    return -1


def confirm_iud_perforation(document: Document, expected=None):
    value, text = determine_iud_perforation(document)
    res = classify_result(value)
    return Result(value, res, expected, text)


def determine_iud_perforation(document: Document):
    if document.has_patterns(PERFORATION, EMBEDDED, MIGRATED):
        # see if any sentences that contain "IUD" also contain perf/embedded
        section = document.select_sentences_with_patterns(IUD)
        if section:
            if section.has_patterns(PERFORATION):
                return PerforationStatus.PERFORATION, section.text
            elif section.has_patterns(EMBEDDED):
                return PerforationStatus.EMBEDDED, section.text
            elif section.has_patterns(MIGRATED):
                return PerforationStatus.MIGRATED, section.text
        return PerforationStatus.NONE, document.text
    else:
        return PerforationStatus.SKIP, None
