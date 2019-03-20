from apex.algo.shared import IUD, POSSIBLE, boilerplate, hypothetical, historical, negation, in_place
from apex.algo.pattern import Document, Pattern
from apex.algo.result import Status, Result


nose = r'(\bnose\b|%)'

INCORRECT = Pattern(r'(incorrect(ly)?|poor(ly)?|wrong(ly)?|bad|\bmal\b)',
                    negates=[nose, hypothetical, negation, boilerplate])
PLACEMENT = Pattern(r'(plac\w+|position\w*|location)',
                    negates=[nose, hypothetical, negation, boilerplate])
MALPOSITION = Pattern(r'(mal (position|place)|trans located)',
                      negates=[nose, hypothetical, negation, boilerplate, in_place])
DISPLACEMENT = Pattern(r'(\brotat\w+|(lower|inferior) uter(ine|us)|'
                       r'displac\w+|dislodg\w+)',
                       negates=[nose, hypothetical, negation, historical, boilerplate, in_place])
IN_CERVIX = Pattern(r'(within|inside|in) (the )?(cx|cervical|cervix)',
                    negates=[negation])
PARTIAL_EXP = Pattern(r'(partial\w* (expel|expul)'
                      r'|(expel|expul)\w* partial'
                      r'|(visible|found|locate|position)\w* (within|inside|in)'
                      r' (the )?(lower uter(ine segment|us) and (the )?)?(cx|cervical|cervix|os)'
                      r'|protrud\w+ from (the )?(cx|cervical|cervix|os)'
                      r')',
                      negates=[nose, negation, 'string', 'polyp', boilerplate])
VISUALIZED = Pattern(f'(({IUD})( was)? (seen|visualiz|noted|in place|position|present))',
                     negates=[nose, negation, hypothetical, boilerplate])
MISSING = Pattern(r'(missing|lost|(can(no|\W)?t|(unable|inability) to) (feel|find))',
                  negates=[nose, hypothetical, boilerplate, 'resume'])

COMPLETE = Pattern(r'(fell out|(spontaneous|complete)\w* exp[ue]l\w+'
                   r'|iud (note|found|seen|visualiz|locate|position)\w*\s+(\w+\s+){,4}in vagina'
                   r')',
                   negates=['in case', 'applicator', 'inserter', 'insertion', 'in the past', 'history',
                            hypothetical, boilerplate, nose, in_place, negation, 'string', 'polyp'])

STRINGS = Pattern(r'strings?', negates=['bothersome', 'noted', 'in place', 'seen',
                                        'visualized', 'cut', 'check', 'trim'])
ANY = (PLACEMENT, MALPOSITION, MISSING,
       VISUALIZED, PARTIAL_EXP, COMPLETE)


class ExpulsionStatus(Status):
    NONE = -1
    EXPULSION = 1
    MALPOSITION = 2
    PROTRUDING = 3
    MISSING_STRING = 4
    PARTIAL = 5
    LOST = 6
    DISPLACEMENT = 7
    POSSIBLE = 8
    POSS_DISPLACEMENT = 9
    SKIP = 99


def confirm_iud_expulsion(document: Document, expected=None):
    for status, text in determine_iud_expulsion(document):
        yield Result(status, status.value, expected, text)


def determine_iud_expulsion(document: Document):
    if document.has_patterns(*ANY):
        for section in document.select_sentences_with_patterns(IUD):
            if section.has_patterns(INCORRECT, PLACEMENT, has_all=True) or \
                    section.has_patterns(MALPOSITION) or \
                    section.has_patterns(DISPLACEMENT):
                if not section.has_patterns(IN_CERVIX):
                    yield ExpulsionStatus.MALPOSITION, section.text
            if section.has_patterns(COMPLETE):
                yield ExpulsionStatus.EXPULSION, section.text
            if section.has_patterns(PARTIAL_EXP):
                yield ExpulsionStatus.PARTIAL, section.text
            if section.has_patterns(MISSING, STRINGS, has_all=True):
                yield ExpulsionStatus.MISSING_STRING, section.text
    else:
        yield ExpulsionStatus.SKIP, document.text
