import enum
import logging
from collections import namedtuple

from apex.algo.pattern import Document, Pattern


iuds = r'\b(iuds?|intrauterine( contraceptive)? devices?)'
lng_iuds = r'(lng ius|levonorgestrel( (releasing|rlse))? (intrauterine|us))'
brand = r'(mirena|paragu?ard|skyla|liletta|copper)'
embedded = r'([ie]mbedded|impacted)'
# removed: |foreign body
migrated = r'\b(stuck|migrat\w+|extrauterine|omentum|displac\w+|(intra)?peritoneal)'
hypothetical = r'\b(risk|complication|warning|information|review|side effect|counsel)'
negation = r'(no evidence|without|r/o|rule out|normal)'

PERFORATION = Pattern(r'perforat\w*', negates=[hypothetical, negation])
IUD = Pattern(f'({iuds}|{lng_iuds}|{brand})')
EMBEDDED = Pattern(f'({embedded}|{migrated})', negates=[hypothetical, negation])


Result = namedtuple('Result', 'value correct')


class PerforationStatus(enum.Enum):
    NONE = 0
    PERFORATION = 1
    EMBEDDED = 2
    UNKNOWN = 3


def classify_result(res: PerforationStatus):
    if res == PerforationStatus.PERFORATION:
        return 1
    elif res == PerforationStatus.EMBEDDED:
        return 1
    return -1


def confirm_iud_perforation(document: Document, expected=None):
    value = determine_iud_perforation(document)
    res = classify_result(value)
    if expected is None:
        return Result(res, None)
    elif res == expected:
        return Result(res, res == expected)
    else:  # failed
        # logging.warning(f'{document.name}:{value}=={expected}:{document.matches}')
        return Result(res, res == expected)


def determine_iud_perforation(document: Document):
    if document.has_patterns(PERFORATION, EMBEDDED):
        # see if any sentences that contain "IUD" also contain perf/embedded
        section = document.select_sentences_with_patterns(IUD)
        if section:
            if section.has_patterns(PERFORATION):
                print('* Perforation:', section.text)
                return PerforationStatus.PERFORATION
            elif section.has_patterns(EMBEDDED):
                print('* Embedded:', section.text)
                return PerforationStatus.EMBEDDED
    return PerforationStatus.NONE
