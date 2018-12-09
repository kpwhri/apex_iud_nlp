from functools import partial

from apex.algo.pattern import Document, Pattern
from apex.algo.result import Status, Result
from apex.algo.shared import hypothetical, negation, historical

pain = r'(sore|pain\w*|infection|excoriat\w+|infection|yeast|candida|engorg\w+)'
breast = r'(breast|nipple)'
words_3 = r'( \w+){0,3} '
ANY_BREAST = Pattern(r'(breast|nipple|milk|lactat\w+|\bbf\b|)')
BREAST_PAIN = Pattern(f'({pain}{words_3}{breast}|{breast}{words_3}{pain})',
                      negates=[negation, hypothetical, historical])
NIPPLE_SHIELD = Pattern(r'((us(es|ing)|wean\w+ from|yes|with)( the)? nipple shield|'
                        r'nipple shield in use)',
                        negates=[negation, hypothetical, historical])
BREAST_MILK = Pattern(f'(breast milk|lactating|milk supply|supply{words_3}milk)')
EXPRESSED_MILK = Pattern(r'(express\w+( breast)? milk)')
EXPRESSED_MILK_EXACT = Pattern(r'(expressed breast milk: y)')
LACTATION_VISIT = Pattern(r'(lactation) (visit|service|consult|specialist|assessment)')
BF_DURATION = Pattern(r'(duration at breast|time breast feeding|total intake this feeding)')
BF_TYPE = Pattern(r'(feeding methods? breast|type feeding breast)')
BF_BOILERPLATE = Pattern(r'(breastfeeding plan|most breastfeeding problems|use different positions|'
                         r'express some breastmilk|have the lactation nurse check out|breastfeeding questions|'
                         r'breastfeeding 101)')
BF_HISTORY = Pattern(r'(breastfeeding history: y)')
BF_EXACT = Pattern(r'(breast feeding: y|breastfeeding: offered: y|taking breast: (y|(for )\d))')
BF_NO_EXACT = Pattern(r'(breast feeding: no|breastfeeding: offered: no)',
                      negates=['previous', 'history', 'hx'])
BF_YES = Pattern(r'(breast feeding well|(is|been) breast feeding)',
                 negates=[negation, hypothetical])
BF = Pattern(r'(feed\w+ breast|breast feeding|breast fed|\bbf\b)')
FORMULA_EXACT = Pattern(r'(formula offered: y|formula: y)')
FORMULA_NO = Pattern(r'(formula: no)')
PUMPING_EXACT = Pattern(r'(yes breast pump|problems with pumping: no)')
PUMPING = Pattern(r'(breast pump)')
BOTTLE_EXACT = Pattern(r'(taking bottle: y)')


class BreastfeedingStatus(Status):
    NONE = -1
    NO = 0
    BREASTFEEDING = 1
    BREAST_PAIN = 2
    PUMPING = 3
    BOTTLE = 4
    FORMULA = 5
    MILK_SUPPLY = 6
    LACTATION_VISIT = 7
    MAYBE = 8
    BOILERPLATE = 9
    EXPRESSED = 10
    HISTORY = 11
    NO_FORMULA = 12
    SKIP = 99


def determine_breastfeeding(document: Document, expected=None):
    my_result = partial(Result, expected=expected)
    has_boilerplate = False
    if document.has_patterns(BF_BOILERPLATE):
        yield my_result(BreastfeedingStatus.BOILERPLATE)
        has_boilerplate = True
    for section in document.select_sentences_with_patterns(ANY_BREAST):
        found_bf = False
        # pre boilerplate patterns: exact/not confused with boilerplate
        if section.has_patterns(BF_EXACT, BF_DURATION, BF_TYPE, BF_YES):
            yield my_result(BreastfeedingStatus.BREASTFEEDING, text=section.text)
            found_bf = True
        if section.has_patterns(BF_NO_EXACT):
            yield my_result(BreastfeedingStatus.NO, text=section.text)
            found_bf = True
        if section.has_patterns(BREAST_PAIN):
            yield my_result(BreastfeedingStatus.BREAST_PAIN, text=section.text)
        if section.has_patterns(EXPRESSED_MILK_EXACT):
            yield my_result(BreastfeedingStatus.EXPRESSED, text=section.text)
        if section.has_patterns(BF_HISTORY):
            yield my_result(BreastfeedingStatus.HISTORY, text=section.text)
        if section.has_patterns(FORMULA_EXACT):
            yield my_result(BreastfeedingStatus.FORMULA, text=section.text)
        if section.has_patterns(FORMULA_NO):
            yield my_result(BreastfeedingStatus.NO_FORMULA, text=section.text)
        if section.has_patterns(LACTATION_VISIT):
            yield my_result(BreastfeedingStatus.LACTATION_VISIT, text=section.text)
        if section.has_patterns(PUMPING_EXACT):
            yield my_result(BreastfeedingStatus.PUMPING, text=section.text)
        if section.has_patterns(BOTTLE_EXACT):
            yield my_result(BreastfeedingStatus.BOTTLE, text=section.text)
        # boilerplate: there is at least some template language
        if has_boilerplate:
            pass
        elif not found_bf:
            # only non-boilerplate
            if section.has_patterns(NIPPLE_SHIELD):
                yield my_result(BreastfeedingStatus.BREASTFEEDING, text=section.text)
            if section.has_patterns(BREAST_MILK, BF, PUMPING, EXPRESSED_MILK):
                yield my_result(BreastfeedingStatus.MAYBE, text=section.text)
