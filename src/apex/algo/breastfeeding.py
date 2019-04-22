import re
from functools import partial

from apex.algo.pattern import Document, Pattern
from apex.algo.result import Status, Result
from apex.algo.shared import hypothetical, negation, historical, boilerplate, possible

pain = r'(sore|pain\w*|infection|excoriat\w+|infection|yeast|candida|engorg\w+)'
breast = r'(breast|nipple)'
words_3 = r'( \w+){0,3} '
ANY_BREAST = Pattern(r'(breast|nipple|milk|lactat\w+|\bbf\b|latch)')
BREAST_PAIN = Pattern(f'({pain}{words_3}{breast}|{breast}{words_3}{pain})',
                      negates=[negation, hypothetical, historical, boilerplate])
LATCHING = Pattern('(difficulty latching|latch(ing)? difficulty)')
NIPPLE_SHIELD = Pattern(r'((us(es|ing)|wean\w+ from|yes|with)( the)? nipple shield|'
                        r'nipple shield in use)',
                        negates=[negation, hypothetical, historical, boilerplate])
MILK_TRANSFER = Pattern('(milk transfer)')
BREAST_MILK = Pattern(f'(breast milk|lactating|milk supply|supply{words_3}milk)',
                      negates=['healthiest', 'wonders', 'orientation'])
EXPRESSED_MILK = Pattern(r'(express\w+( breast)? milk)',
                         negates=[negation, hypothetical, historical, boilerplate])
EXPRESSED_MILK_EXACT = Pattern(
    r'('
    r'expressed breast milk: (most|some|all|[\d/\-\.\s]+ (oz|ounce|g|ml)|yes)'
    r'|(oz|ounces?|g|ml) of expressed breast milk'
    r')'
)
LACTATION_VISIT = Pattern(r'\b(lactation) (visit|service|consult|specialist|assessment)',
                          negates=[r'\bif\b', 'please', hypothetical, '(capitol|campus|206|253)'])
BF_DURATION = Pattern(r'(duration at breast|time breast feeding|total intake this feeding)')
BF_TYPE = Pattern(r'(feeding methods? breast|type feeding breast|nourishment method breast)')
BF_UNKNOWN = Pattern(r'('
                     r'breast feeding (\*|na|yes/no/na|not applicable)'
                     r'|breast feeding: YES NO'
                     r')')
BF_BOILERPLATE_EXCLUDE = Pattern(r'('
                                 r'initial ob provider visit'
                                 r'|prenatal (visit|care)'
                                 r'|your care instructions'
                                 r'|calcium requirements'
                                 r'|establish a milk supply'
                                 r'|baby feeding cues'
                                 r'|sig'
                                 r'|learning how to breast-feed'
                                 r'|folic acid'
                                 r')')
BF_BOILERPLATE = Pattern(r'(breastfeeding plan|most breastfeeding problems|use different positions|'
                         r'express some breastmilk|have the lactation nurse check out|breastfeeding questions|'
                         r'breastfeeding 101|how to breast feed|first few weeks of breast feeding|'
                         r'most breast feeding challenges can be solved at home|'
                         r'basic breast feeding positions include|gently massage your breasts|'
                         r'massage the affected area before breast-feeding|doctor may prescribe oxytocin|'
                         r'blocked milk ducts may cause|more frequent breastfeeding usually helps to increase|'
                         r'get some helpful pointers|not use a suppository while you|'
                         r'suddenly stopping breast feeding|'
                         r'breast feeding for at least the first year|'
                         r'introduce solid foods at the appropriate time|'
                         r'the foods you eat may affect your breast milk|'
                         r'always nurse baby with a deep latch|'
                         r'breastmilk on the nipples|'
                         r'breastmilk is the healthiest food for your baby|'
                         r'we are happy to connect you with local resources|'
                         r'are considering stopping breastfeeding because|'
                         r'congratulations|'
                         r'buspirone|'
                         r'patient education|'
                         r'circumcision|'
                         r'when to call a doctor|'
                         r'baby feeding cues|'
                         r'newborn condition center|'
                         r'come to the hospital if'
                         r')')
BF_BOILERPLATE_SECTION = Pattern(r'('
                                 r'Bottle-Feeding: Promoting Healthy Growth and Development'
                                 r'|practice deep latching techniques'
                                 r'|after your visit'
                                 r'|what to expect'
                                 r'|information for parents and caregivers'
                                 r'|some suggestions'
                                 r'|things to start thinking about'
                                 r').*', flags=re.IGNORECASE | re.MULTILINE)
BF_HISTORY = Pattern(r'(breastfeeding history: y)')
BF_FEEDING = Pattern(
    r'('
    r'feeding: breast'
    r'|nutrition: (both|continue to|from)? breast'
    r')',
    negates=['Teaching/Guidance:', 'Discussed:', 'provided:']
)
BF_EXACT = Pattern(
    r'(breast feeding(:|\?) y'
    r'|breastfeeding: offered: y'
    r'|taking breast: (y|(for )\d)'
    r'|(breast\s?(feeding|milk)|nursing) (frequency )?(every )?\d{1,2}(\.\d{1,2})?(-\d{1,2}(\.\d{1,2})?)?'
    r' (x|times){0,2} \d{0,2} [hmd]'
    r'|pumping every (\d{1,2}(.\d{1,2})? (\d{1,2}(.\d{1,2})?)?)? [hm]'
    r'|intake at breast: [\d/\-\.\s]+ (ml|g|oz|ounce)'
    r'|breast feeding and (bottle feeding|supplementing|doing well)'
    r'|breastfeeding issues: (yes|no problems)'
    r')'
)
BF_NO_EXACT = Pattern(r'(breast feeding|breastfeeding: offered): (n[o\s]|denies)',
                      negates=['previous', 'history', 'hx', 'problems'])
BF_NOT = Pattern(r'('
                 r'(pt|is|been) not ((currently|now|presently) )?(breast feeding|\bbf\b)'
                 r')')
BF_YES = Pattern(r'((breast feeding|\bbf\b) (has been )?(going )?(very )?well'
                 r'|(pt|is|been) ((currently|now|presently|exclusively) )?(breast feeding|\bbf\b)'
                 r'|breast feeding without difficulty'
                 r'|still (\bbf\b|breast feeding|nurses)'
                 r'|continues to breast feed'
                 r'|(exclusive|current)ly breast feeding'
                 r'|breast feeding exclusively'
                 r')',
                 negates=[negation, hypothetical, 'advise', 'some'])
BF = Pattern(r'(feed\w+ breast|breast feeding|breast fed|\bbf\b)',
             negates=[negation, hypothetical, historical, boilerplate])
FORMULA_EXACT = Pattern(r'(formula offered: y|formula: y)', space_replace=r'\s*')
FORMULA_NO = Pattern(r'(formula: no)')
PUMPING_EXACT = Pattern(r'(yes breast pump|problems with pumping: no)')
PUMPING_ACTIVE = Pattern(r'(breast pumping|is using( a)? breast pump)',
                         negates=[negation, hypothetical, historical, possible])
PUMPING = Pattern(r'(breast pump)',
                  negates=[negation, hypothetical, historical, boilerplate])
BOTTLE_EXACT = Pattern(r'(taking bottle: y|method: bottle)')
BF_SUPPLEMENT = Pattern(r'supplement breast feeding',
                        negates=[negation, hypothetical, historical, boilerplate])
BF_STOP = Pattern(r'('
                  r'(stop\w+|no longer|quit) (breast feeding|nursing)'
                  r'|just stopped breast feeding'
                  r')',
                  negates=[negation, hypothetical, historical, boilerplate,
                           'for a few days', 'had', 'on that side', 'cause', 'conflicted',
                           'thinking', 'planning', 'since', 'start', 'process'])
# handle "7 mo infant, stopped breastfeeding at approx 1 mo age"
BF_STOP_BAD = Pattern(r'('
                      r'\d{1,2} \b(wk?|week|mo?|month|yr?|year)s?\b'
                      r'|\b[ap]m\b'
                      r'|\bpump'
                      r'|resumed'
                      r'|bottle'
                      r')')
# whole milk, no breast
WHOLE_MILK = Pattern(r'('
                     r'nutrition: (\w+ ){0,4}((cow s|whole) milk|formula)'
                     r')',
                     negates=[r'\bwean\b', 'breast', 'Teaching/Guidance:', 'Discussed:', 'provided:'])
AGO = Pattern(r'\bago\b')


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
    STOP = 13
    STOPPED_BEFORE = 14  # stopped well before this date (age of child as reference)
    SKIP = 99


def confirm_breastfeeding(document: Document, expected=None):
    for res in determine_breastfeeding(document, expected=expected):
        if res.result in [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 13, 14]:
            yield res


def determine_breastfeeding(document: Document, expected=None):
    my_result = partial(Result, expected=expected)
    has_boilerplate = False
    document = document.remove_patterns(BF_BOILERPLATE_SECTION)
    if not document:  # only boilerplate
        return
    if document.has_patterns(BF_BOILERPLATE_EXCLUDE, BF_UNKNOWN):
        return
    if document.has_patterns(BF_BOILERPLATE):
        yield my_result(BreastfeedingStatus.BOILERPLATE)
        has_boilerplate = True
    non_exact_count = 0
    non_exact_count_snippets = []
    for section in document.select_sentences_with_patterns(ANY_BREAST):
        found_bf = False
        # pre boilerplate patterns: exact/not confused with boilerplate
        if section.has_patterns(BF_EXACT, BF_DURATION, BF_TYPE, BF_YES, BF_FEEDING):
            yield my_result(BreastfeedingStatus.BREASTFEEDING, text=section.text)
            found_bf = True
        if section.has_patterns(BF_NO_EXACT, BF_NOT, WHOLE_MILK):
            yield my_result(BreastfeedingStatus.NO, text=section.text)
            found_bf = True
        if section.has_patterns(EXPRESSED_MILK_EXACT):
            yield my_result(BreastfeedingStatus.EXPRESSED, text=section.text)
        if section.has_patterns(BF_HISTORY):
            yield my_result(BreastfeedingStatus.HISTORY, text=section.text)
        if section.has_patterns(FORMULA_EXACT):
            yield my_result(BreastfeedingStatus.FORMULA, text=section.text)
        if section.has_patterns(FORMULA_NO):
            yield my_result(BreastfeedingStatus.NO_FORMULA, text=section.text)
        if section.has_patterns(PUMPING_EXACT, PUMPING_ACTIVE):
            yield my_result(BreastfeedingStatus.PUMPING, text=section.text)
        if section.has_patterns(BOTTLE_EXACT):
            yield my_result(BreastfeedingStatus.BOTTLE, text=section.text)
        if section.has_patterns(BF_STOP):
            if section.has_patterns(AGO):  # "stopped 2 months ago"
                yield my_result(BreastfeedingStatus.STOP, text=section.text)
            elif section.has_patterns(BF_STOP_BAD):  # "stopped at 2 months age"
                yield my_result(BreastfeedingStatus.STOPPED_BEFORE, text=section.text)
            else:  # "stopped"
                yield my_result(BreastfeedingStatus.STOP, text=section.text)
            found_bf = True
        if section.has_patterns(LATCHING):
            yield my_result(BreastfeedingStatus.BREASTFEEDING, text=section.text)
            found_bf = True
        # boilerplate: there is at least some template language
        if not found_bf and not has_boilerplate:
            # only non-boilerplate
            if section.has_patterns(NIPPLE_SHIELD, BF_SUPPLEMENT):
                yield my_result(BreastfeedingStatus.BREASTFEEDING, text=section.text)
            if section.has_pattern(BF_FEEDING, ignore_negation=True):
                yield my_result(BreastfeedingStatus.MAYBE, text=section.text)
            cnt = section.has_patterns(BREAST_MILK, BF, PUMPING,
                                       EXPRESSED_MILK, MILK_TRANSFER,
                                       BREAST_PAIN,
                                       get_count=True)
            if cnt:
                non_exact_count += cnt
                non_exact_count_snippets.append(section.text)
            if section.has_patterns(LACTATION_VISIT):
                yield my_result(BreastfeedingStatus.LACTATION_VISIT, text=section.text)
    if non_exact_count >= 2:
        yield my_result(BreastfeedingStatus.MAYBE, text='\n'.join(non_exact_count_snippets))
