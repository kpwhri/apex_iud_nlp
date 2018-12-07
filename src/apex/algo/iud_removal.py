from apex.algo.iud_perforation import IUD
from apex.algo.pattern import Document, Pattern
from apex.algo.result import Status, Result

in_place = r'(?<!not) in (place|situ)\b'
negation = r'(ready|should|sometimes|must|decline|\bnot\b)'
hypothetical = r'(option|possib\w+|desire|want|will|\bcan\b|' \
               r'\bor\b|like|would|need|until|request|when|you ll|' \
               r'\bif\b|consider|concern|return|nervous|anxious|to be remov|could|' \
               r'discuss|inform)'
boilerplate = r'(risk|after your visit|chance|conceive|appt|appointment|due (to|for|at)|recommend|' \
              r'pregnan|pamphlet|schedul|doctor)'
other = r'(fibroid|v25.1\d|tampon)'
tool_remove = r'(introducer|inserter|tenaculum|instruments?)( (was|were))? removed'
# avoid months (followed by day/year)
# avoid 'last' or 'in' or 'since'
safe_hypo_may = r'(?<!in|st|ce) may (?!\d)'

REMOVE = Pattern(r'(remov\w+|replac\w+)',
                 negates=[negation, boilerplate, hypothetical, in_place,
                          other, tool_remove, safe_hypo_may])
# describe tool or the "how" of removal
TOOL = Pattern(r'((ring )?forceps?|hook|speculum|fashion|'
               r'strings? (grasp|clasp)|(grasp|clasp)\w* strings?|'
               r'(with|gentle|more|\bw) traction|technique)')
PLAN = Pattern(r'\brem intrauterine device\b',
               negates=[hypothetical, boilerplate, negation, other, safe_hypo_may])


class RemoveStatus(Status):
    NONE = -1
    REMOVE = 1
    TOOL_REMOVE = 2
    PLAN = 3
    SKIP = 99


def classify_result(res: RemoveStatus):
    if res == RemoveStatus.REMOVE:
        return 1
    elif res == RemoveStatus.TOOL_REMOVE:
        return 2
    else:
        return -1


def confirm_iud_removal(document: Document, expected=None):
    for value, text in determine_iud_removal(document):
        res = classify_result(value)
        yield Result(value, res, expected, text)


def determine_iud_removal(document: Document):
    if document.has_patterns(REMOVE, ignore_negation=True):
        section_text = []
        for section in document.select_sentences_with_patterns(IUD):
            # these definitely have correct language
            if section.has_patterns(REMOVE, PLAN):
                # require either REMOVE/PLAN since this could have other refs
                if section.has_patterns(TOOL):
                    yield RemoveStatus.TOOL_REMOVE, section.text
                if section.has_patterns(REMOVE):
                    yield RemoveStatus.REMOVE, section.text
                if section.has_patterns(PLAN):
                    yield RemoveStatus.PLAN, section.text
            else:
                section_text.append(section.text)
        if section_text:
            yield RemoveStatus.NONE, ' '.join(section_text)
        else:
            yield RemoveStatus.SKIP, document.text
    else:
        yield RemoveStatus.SKIP, document.text
