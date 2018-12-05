from apex.algo.iud_perforation import IUD
from apex.algo.pattern import Document, Pattern
from apex.algo.result import Status, Result

in_place = r'(?<!not) in (place|situ)\b'
negation = r'(ready|should|sometimes|must|decline|\bnot\b)'
hypothetical = r'(option|possib\w+|desire|want|\bor\b|like|would|until|request)'
boilerplate = r'(risk|after your visit|chance|conceive|appt|appointment|due (to|for|at)|recommend|' \
              r'pregnan|pamphlet|schedul|doctor)'
other = r'(fibroid|v25.13)'

REMOVE = Pattern(r'(remov\w+|replac\w+)',
                 negates=[negation, boilerplate, hypothetical, in_place, other])
# describe tool or the "how" of removal
TOOL = Pattern(r'((ring )?forceps?|fashion|strings? grasp|grasp\w+ strings?)')


class RemoveStatus(Status):
    NONE = -1
    REMOVE = 1
    TOOL_REMOVE = 2
    SKIP = 99


def classify_result(res: RemoveStatus):
    if res == RemoveStatus.REMOVE:
        return 1
    elif res == RemoveStatus.TOOL_REMOVE:
        return 2
    else:
        return -1


def confirm_iud_removal(document: Document, expected=None):
    value, text = determine_iud_removal(document)
    res = classify_result(value)
    yield Result(value, res, expected, text)


def determine_iud_removal(document: Document):
    if document.has_patterns(REMOVE, ignore_negation=True):
        section_text = []
        for section in document.select_sentences_with_patterns(IUD):
            if section.has_patterns(REMOVE):
                if section.has_patterns(TOOL):
                    return RemoveStatus.TOOL_REMOVE, section.text
                return RemoveStatus.REMOVE, section.text
            else:
                section_text.append(section.text)
        if section_text:
            return RemoveStatus.NONE, ' '.join(section_text)
        else:
            return RemoveStatus.SKIP, document.text
    else:
        return RemoveStatus.SKIP, document.text
