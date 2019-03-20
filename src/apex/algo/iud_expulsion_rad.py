import re

from apex.algo.iud_expulsion import ExpulsionStatus, PARTIAL_EXP, nose
from apex.algo.pattern import Document, Pattern
from apex.algo.result import Result
from apex.algo.shared import IUD, negation, boilerplate

SECTIONS = re.compile(r'([A-Z]+|Impression|Transvaginal|Transabdominal|Findings)\W*:')
IUD_PRESENT = Pattern(r'(present|place|evaluate|position|absent|locat)')
STRINGS = Pattern(r'string')
VISIBLE = Pattern(r'(unable|visible|see|absent|\bnot?\b|inability|palpable)')

MISSING_IUD = Pattern(f'(({IUD})( was)?not (seen|visualiz|noted|in place|position|present))')
MALPOSITION = Pattern(r'('
                      r'(visible|found|locate|position)\w* (within|inside|in)'
                      r' (the )?(lower uterine|inferior body)'
                      r'|iud (note|found|seen|visualiz|locate|position)\w*\s+(\w+\s+){,4}in'
                      r' (the )?(inferior body|lower uterine)'
                      r')',
                      negates=[nose, negation, 'string', 'polyp', boilerplate])


def confirm_iud_expulsion_rad(document: Document, expected=None):
    for status, text in determine_iud_expulsion_rad(document):
        yield Result(status, status.value, expected, text)


def determine_iud_expulsion_rad(document: Document):
    sections = document.split(SECTIONS)
    start_section = sections.get_sections('HST', 'SAS')
    impression = sections.get_section('IMPRESSION')
    other = sections.get_sections('FINDINGS', 'TRANSVAGINAL')
    found = False
    if start_section.has_patterns(IUD, IUD_PRESENT, has_all=True) or \
            start_section.has_patterns(STRINGS, VISIBLE, has_all=True):
        if impression.has_patterns(PARTIAL_EXP):
            found = True
            yield ExpulsionStatus.PARTIAL, impression.text
        if impression.has_patterns(MISSING_IUD):
            found = True
            yield ExpulsionStatus.LOST, impression.text
        if impression.has_patterns(MALPOSITION):
            found = True
            yield ExpulsionStatus.MALPOSITION, impression.text
        if not found and other.has_patterns(PARTIAL_EXP):
            yield ExpulsionStatus.PARTIAL, impression.text
    else:
        yield ExpulsionStatus.SKIP, document.text
