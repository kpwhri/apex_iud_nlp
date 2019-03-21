import re

from apex.algo.iud_expulsion import ExpulsionStatus, PARTIAL_EXP, nose
from apex.algo.pattern import Document, Pattern
from apex.algo.result import Result
from apex.algo.shared import IUD, negation, boilerplate

SECTIONS = re.compile(r'([A-Z]+( [A-Z]+)?|Impression|Transvaginal|Transabdominal'
                      r'|Findings|Examination|History)\W*?:')
IUD_PRESENT = Pattern(r'(present|place|evaluate|position|absent|locat|exp[eu]l|see)')
STRING = Pattern(r'string')
VISIBLE = Pattern(r'(unable|missing|visible|see|absent|\bnot?\b|inability|palpable)')

IUD_NOT_SEEN = Pattern(f'(({IUD})( was)? n[o\\W]t (seen|visualiz|noted|in place|position|present|identified))')
NOT_SEEN_IUD = Pattern(f'no {IUD} (seen|visualiz|noted|in place|position|present|identified)')
MISSING_IUD = Pattern(f'({IUD} (absent|missing)|(absent|missing) {IUD})')
MALPOSITION = Pattern(r'('
                      r'(visible|found|locate|position)\w* (within|inside|in)'
                      r' (the )?(lower uterine|inferior body)'
                      f'|{IUD} (note|found|seen|visualiz|locate|position)\\w*'
                      r'\s+(\w+\s+){,4}in'
                      r' (the )?(inferior body|lower uterine)'
                      r'|(inferior|distal) to (the )?(expect|desire)'
                      r')',
                      negates=[nose, negation, 'string', 'polyp', boilerplate])
MALPOSITION_IUD = Pattern(f'((mal position) {IUD}|{IUD} (is )?mal position)',
                          negates=[negation, 'string', boilerplate, nose])


def confirm_iud_expulsion_rad(document: Document, expected=None):
    for status, text in determine_iud_expulsion_rad(document):
        yield Result(status, status.value, expected, text)


def determine_iud_expulsion_rad(document: Document):
    sections = document.split(SECTIONS)
    start_section = sections.get_sections('HST', 'SAS', 'HISTORY',
                                          'CLINICAL INFORMATION', 'CLINICAL HISTORY AND QUESTION')
    impression = sections.get_section('IMPRESSION', 'IMPRESSIONS')
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
    if found:
        return
    elif start_section.has_patterns(IUD, IUD_PRESENT, has_all=True) or \
            start_section.has_patterns(STRING, VISIBLE, has_all=True):
        if other.has_patterns(PARTIAL_EXP):
            yield ExpulsionStatus.PARTIAL, impression.text
        if other.has_patterns(MALPOSITION, MALPOSITION_IUD):
            yield ExpulsionStatus.MALPOSITION, impression.text
    else:
        sentences = list(document.select_sentences_with_patterns(IUD))
        if sentences:
            for sentence in sentences:
                if sentence.has_patterns(PARTIAL_EXP):
                    yield ExpulsionStatus.PARTIAL, sentence.text
                if sentence.has_patterns(MALPOSITION, MALPOSITION_IUD):
                    yield ExpulsionStatus.MALPOSITION, sentence.text
        else:
            yield ExpulsionStatus.SKIP, None
