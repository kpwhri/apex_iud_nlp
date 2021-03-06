import re

from apex.algo.iud_expulsion import ExpulsionStatus, PARTIAL_EXP, misc_excl, LOWER_UTERINE, NOTED, INSIDE, \
    PROPER_LOCATION, IN_UTERUS, LOWER_UTERINE_SEGMENT
from apex.algo.pattern import Document, Pattern
from apex.algo.result import Result
from apex.algo.shared import IUD, negation, boilerplate

SECTIONS = re.compile(r'([A-Z]+( [A-Z]+)?|Impression|Imp|Transvaginal|Transabdominal'
                      r'|Findings|Examination|History)\W*?:')
IUD_PRESENT = Pattern(f'({NOTED}|absent)')
STRING = Pattern(r'string')
VISIBLE = Pattern(r'(unable|missing|visible|see|absent|\bnot?\b|inability|palpable)')

IUD_NOT_SEEN = Pattern(f'(({IUD})( was)? n[o\\W]t {NOTED})')
NOT_SEEN_IUD = Pattern(f'no {IUD} {NOTED}')
MISSING_IUD = Pattern(f'({IUD} (absent|missing)|(absent|missing) {IUD})')
MALPOSITION = Pattern(r'('
                      f'{NOTED} {INSIDE} (the )?{LOWER_UTERINE}'
                      f'|{IUD} {NOTED}'
                      r'\s+(\w+\s+){,4}in'
                      f' (the )?{LOWER_UTERINE}'
                      r'|(inferior|distal) to (the )?(expect|desir|typical)'
                      r')',
                      negates=[misc_excl, negation, 'string', 'polyp', boilerplate])
MALPOSITION_IUD = Pattern(f'((mal position) {IUD}|{IUD} (is )?mal position)',
                          negates=[negation, 'string', boilerplate, misc_excl])


def confirm_iud_expulsion_rad(document: Document, expected=None):
    for status, text in determine_iud_expulsion_rad(document):
        yield Result(status, status.value, expected, text)


def determine_iud_expulsion_rad(document: Document):
    sections = document.split(SECTIONS)
    start_section = sections.get_sections('HST', 'SAS', 'HISTORY',
                                          'CLINICAL INFORMATION', 'CLINICAL HISTORY AND QUESTION')
    impression = sections.get_sections('IMPRESSION', 'IMPRESSIONS', 'IMP')
    other = sections.get_sections('FINDINGS', 'TRANSVAGINAL', 'FINDING')
    found = False
    if impression:
        if impression.has_patterns(PARTIAL_EXP):
            found = True
            yield ExpulsionStatus.PARTIAL, impression.text
        if impression.has_patterns(NOT_SEEN_IUD, IUD_NOT_SEEN):
            found = True
            yield ExpulsionStatus.LOST, impression.text
        if impression.has_patterns(MALPOSITION, MALPOSITION_IUD):
            found = True
            yield ExpulsionStatus.MALPOSITION, impression.text
        if impression.has_patterns(PROPER_LOCATION):
            found = True
            yield ExpulsionStatus.PROPER_PLACEMENT, impression.text
        if impression.has_patterns(IN_UTERUS):
            found = False  # don't count this one
            yield ExpulsionStatus.IN_UTERUS, impression.text
        if impression.has_patterns(LOWER_UTERINE_SEGMENT):
            found = False
            yield ExpulsionStatus.LOWER_UTERINE_SEGMENT, impression.text
    if found:
        return
    elif start_section.has_patterns(IUD, IUD_PRESENT, has_all=True) or \
            start_section.has_patterns(STRING, VISIBLE, has_all=True):
        if other.has_patterns(PARTIAL_EXP):
            yield ExpulsionStatus.PARTIAL, other.text
        if other.has_patterns(MALPOSITION, MALPOSITION_IUD):
            yield ExpulsionStatus.MALPOSITION, other.text
        if other.has_patterns(PROPER_LOCATION):
            yield ExpulsionStatus.PROPER_PLACEMENT, other.text
        if other.has_patterns(IN_UTERUS):
            yield ExpulsionStatus.IN_UTERUS, other.text
        if other.has_patterns(LOWER_UTERINE_SEGMENT):
            yield ExpulsionStatus.LOWER_UTERINE_SEGMENT, other.text
    else:
        sentences = list(document.select_sentences_with_patterns(IUD))
        if sentences:
            for sentence in sentences:
                if sentence.has_patterns(PARTIAL_EXP):
                    yield ExpulsionStatus.PARTIAL, sentence.text
                if sentence.has_patterns(MALPOSITION, MALPOSITION_IUD):
                    yield ExpulsionStatus.MALPOSITION, sentence.text
                if sentence.has_patterns(PROPER_LOCATION):
                    yield ExpulsionStatus.PROPER_PLACEMENT, sentence.text
                if sentence.has_patterns(IN_UTERUS):
                    yield ExpulsionStatus.IN_UTERUS, sentence.text
                if sentence.has_patterns(LOWER_UTERINE_SEGMENT):
                    yield ExpulsionStatus.LOWER_UTERINE_SEGMENT, sentence.text
        else:
            yield ExpulsionStatus.SKIP, None
