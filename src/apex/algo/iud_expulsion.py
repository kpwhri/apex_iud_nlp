from apex.algo.iud_perforation import IUD
from apex.algo.pattern import Document, Pattern
from apex.algo.result import Status, Result


possible = r'\b(unlikely|possib(ly|le|ility)|improbable|potential|suspect|chance|may\b|afraid|concern|tentative)'
hypothetical = r'(\bif\b|\bnose\b|contact|doctor|should|can|includ|failure|' \
               r'how|call|rare|risk|associated|avoid)'
historical = r'(hx|history|previous)'
negation = r'(\bnot\b|\bor\b|\bno\b)'

POSSIBLE = Pattern(possible)
INCORRECT = Pattern(r'(incorrect(ly)?|poor(ly)?|wrong(ly)?|bad|\bmal\b)',
                    negates=[hypothetical, negation])
PLACEMENT = Pattern(r'(plac\w+|position\w*|location)',
                    negates=[hypothetical, negation])
MALPOSITION = Pattern(r'(mal (position|place)|trans located)',
                      negates=[hypothetical, negation])
DISPLACEMENT = Pattern(r'(\brotat\w+|(lower|inferior) (uter(ine|us)|cervi(x|cal))|'
                       r'displac\w+|dislodg\w+)',
                       negates=[hypothetical, negation, historical])
EXPULSION = Pattern(r'(expel|expuls)',
                    negates=[hypothetical, historical, negation])
DEF_EXPULSION = Pattern(r'spontan\w+ (expel|expul)',
                        negates=[hypothetical, historical, negation])
PARTIAL_EXP = Pattern(r'(partial\w* (expel|expul)|(expel|expul)\w* partial)',
                      negates=[negation, 'strings? of'])
VISUALIZED = Pattern(r'({IUD})( was)? (seen|visualiz)',
                     negates=[negation, hypothetical])
PROTRUDES = Pattern(r'protrud',
                    negates=['strings?', hypothetical])
LOST = Pattern(r'(toilet|fell)')
MISSING = Pattern(r'(missing|lost|can(no|\W)?t feel)',
                  negates=[hypothetical])
STRINGS = Pattern(r'strings?', negates=['bothersome'])
ANY = (PLACEMENT, MALPOSITION, EXPULSION, LOST, MISSING,
       PROTRUDES, VISUALIZED, PARTIAL_EXP, DEF_EXPULSION)


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
        found = False
        for section in document.select_sentences_with_patterns(IUD):
            if section.has_patterns(INCORRECT, PLACEMENT, has_all=True) or \
                    section.has_patterns(MALPOSITION):
                yield ExpulsionStatus.MALPOSITION, section.text
                found = True
            if section.has_patterns(EXPULSION):
                if section.has_patterns(POSSIBLE):
                    yield ExpulsionStatus.POSSIBLE, section.text
                elif section.has_patterns(PARTIAL_EXP):
                    yield ExpulsionStatus.PARTIAL, section.text
                else:
                    yield ExpulsionStatus.EXPULSION, section.text
                found = True
            if section.has_patterns(MISSING, STRINGS, has_all=True):
                yield ExpulsionStatus.MISSING_STRING, section.text
                found = True
            if section.has_patterns(LOST):
                yield ExpulsionStatus.LOST, section.text
                found = True
            if section.has_patterns(DISPLACEMENT):
                if section.has_patterns(POSSIBLE):
                    yield ExpulsionStatus.POSS_DISPLACEMENT, section.text
                else:
                    yield ExpulsionStatus.DISPLACEMENT, section.text
                found = True
        # if not found:
        #     yield ExpulsionStatus.NONE, document.text
    else:
        yield ExpulsionStatus.SKIP, document.text
