from apex.algo.shared import IUD, boilerplate, hypothetical, historical, negation, in_place
from apex.algo.pattern import Document, Pattern
from apex.algo.result import Status, Result


misc_excl = r'(\bnose\b|%|hook)'

UTERINE = r'(uter(ine|us))'
LOWER_UTERINE = f'((lower|inferior) (({UTERINE}|segment|body) )+)'
NOTED = r'((see|visible|found|in place|visualiz|note|locate|position|present|identif)\w*)'
INSIDE = r'(within|inside|in)'
CX = r'(\bcx\b|cervical|cervix)'
CX_OS = f'({CX}|os)'

PROPER_LOCATION = Pattern(
    rf'('
    rf'in( a)? (expected|proper|appropriate|satisfactory|normal|regular|good|correct) (location|position|place)'
    rf'|(expected|proper|appropriate|satisfactori|normal|correct)ly (locat|position|plac)\w+'
    rf'|(present|locat\w+|position\w*|visuali[sz]ed|seen) (with)?in the (uter\w+|endometri\w+)'
    rf'|{IUD}\s*((is|was) )?in (place|situ)'
    rf')',
    negates=[negation, r'\b(confirm|check|difficult|determine|if\b|option|talk)',
             'strings?', 'especially', 'negative', 'plan', r'cervi\w+']
)
LOWER_UTERINE_SEGMENT = Pattern(r'(lower uterine segment|low lying|\blus\b)',
                                negates=[negation, 'strings?', 'negative',
                                         r'\b(confirm|check|difficult|determine|if\b|option|talk)'])
IN_UTERUS = Pattern(
    rf'('
    rf'(with)?in the (uter\w+|endometri\w+)'
    rf')',
    negates=[negation, r'\b(confirm|check|difficult|determine|if\b|option|talk)',
             'strings?', 'especially', 'negative', 'plan', r'cervi\w+']
)
PREVIOUS = Pattern(r'(previous|history|\bprior\b|\blast\b)',
                   negates=[r'\bago\b', r'\brecent'])
INCORRECT = Pattern(r'(incorrect(ly)?|poor(ly)?|wrong(ly)?|badly|\bmal\b)',
                    negates=[misc_excl, hypothetical, negation, boilerplate, r'diff\w+', 'carcinoma'])
PLACEMENT = Pattern(r'(plac\w+|position\w*|location)',
                    negates=[misc_excl, hypothetical, negation, boilerplate])
MALPOSITION = Pattern(r'(mal (position|place)|trans located)',
                      negates=[misc_excl, hypothetical, negation, boilerplate, in_place])
DISPLACEMENT = Pattern(r'(\brotate\w+'
                       f'|{LOWER_UTERINE}'
                       r'|(displace|dislodge)(d|ment))',
                       negates=[misc_excl, hypothetical, negation, historical, boilerplate, in_place,
                                r'fractures?\b'])
IN_CERVIX = Pattern(f'{INSIDE} (the )?{CX}',
                    negates=[negation])
PARTIAL_EXP = Pattern(r'(partial\w* exp[eu]l'
                      r'|exp[ue]l\w* partial'
                      f'|{NOTED} (it )?{INSIDE}'
                      r' (\w+\s+){,4}'
                      r' (the )?'
                      f'({LOWER_UTERINE}( and)?'
                      r' (the )?(\w+\s+){,4})?'
                      f' {CX_OS}'
                      f'|(pro|ex)trud\\w+ from (the )?{CX_OS}'
                      r')',
                      negates=[misc_excl, negation, 'strings?', 'polyp', boilerplate])
VISUALIZED = Pattern(f'(({IUD})( was)? {NOTED})',
                     negates=[misc_excl, negation, hypothetical, boilerplate])
MISSING = Pattern(r'(missing|lost|(can(no|\W)?t|(unable|inability) to) (feel|find|locat))',
                  negates=[misc_excl, hypothetical, boilerplate, 'resume', r'\btip\b'])

COMPLETE = Pattern(r'(fell out'
                   r'|(spontaneous|complete)\w* exp[ue]l\w+'
                   r'|exp[ue]l\w+ (spontaneous|complete)'
                   f'|{IUD} {NOTED}'
                   r'\w*\s+(\w+\s+){,4}in vagina'
                   r')',
                   negates=['in case', 'applicator', 'inserter', 'insertion', 'in the past', 'history', r'\bh\W*o\b',
                            hypothetical, boilerplate, misc_excl, in_place, negation, 'string', 'polyp'])

STRINGS = Pattern(r'strings?', negates=['bothersome', NOTED, 'cut', 'check', 'trim'])


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
    PROPER_PLACEMENT = 10
    IN_UTERUS = 11
    LOWER_UTERINE_SEGMENT = 12
    HISTORY = 98
    SKIP = 99


def confirm_iud_expulsion(document: Document, expected=None):
    for status, history, text in determine_iud_expulsion(document):
        yield Result(status, status.value, expected, text, extras=ExpulsionStatus.HISTORY if history else None)


def determine_iud_expulsion(document: Document):
    if document.has_patterns(IUD):
        for section in document.select_sentences_with_patterns(IUD):
            history = bool(section.has_patterns(PREVIOUS))
            if section.has_patterns(INCORRECT, PLACEMENT, has_all=True) or \
                    section.has_patterns(MALPOSITION) or \
                    section.has_patterns(DISPLACEMENT):
                if not section.has_patterns(IN_CERVIX):
                    yield ExpulsionStatus.MALPOSITION, history, section.text
            if section.has_patterns(LOWER_UTERINE_SEGMENT):
                yield ExpulsionStatus.LOWER_UTERINE_SEGMENT, history, section.text
            if section.has_patterns(COMPLETE):
                yield ExpulsionStatus.EXPULSION, history, section.text
            if section.has_patterns(PARTIAL_EXP):
                yield ExpulsionStatus.PARTIAL, history, section.text
            if section.has_patterns(MISSING, STRINGS, has_all=True):
                yield ExpulsionStatus.MISSING_STRING, history, section.text
            if section.has_patterns(PROPER_LOCATION):
                yield ExpulsionStatus.PROPER_PLACEMENT, history, section.text
            if section.has_patterns(IN_UTERUS):
                yield ExpulsionStatus.IN_UTERUS, history, section.text
    else:
        yield ExpulsionStatus.SKIP, None, document.text
