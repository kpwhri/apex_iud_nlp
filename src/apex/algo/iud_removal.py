from apex.algo.iud_perforation import IUD
from apex.algo.pattern import Document, Pattern
from apex.algo.result import Status, Result

negation = r'(ready|should|sometimes|must|decline)'
boilerplate = r'(risk|after your visit|chance)'

REMOVE = Pattern(r'(remov\w+|replac\w+)',
                 negates=[negation, boilerplate])


class RemoveStatus(Status):
    NONE = -1
    REMOVE = 1
    SKIP = 99


def classify_result(res: RemoveStatus):
    if res == RemoveStatus.REMOVE:
        return 1
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
                return RemoveStatus.REMOVE, section.text
            else:
                section_text.append(section.text)
        return RemoveStatus.NONE, ' '.join(section_text)
    else:
        return RemoveStatus.SKIP, document.text
