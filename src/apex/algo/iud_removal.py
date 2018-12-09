from apex.algo.shared import IUD, boilerplate, safe_may, hypothetical, in_place
from apex.algo.pattern import Document, Pattern
from apex.algo.result import Status, Result

negation = r'(ready|should|sometimes|must|decline|\bnot\b)'
other = r'(fibroid|v25.1\d|tampon)'
tool_remove = r'(introducer|inserter|tenaculum|instruments?)( (was|were))? removed'

REMOVE = Pattern(r'(remov\w+|replac\w+)',
                 negates=[negation, boilerplate, hypothetical, in_place,
                          other, tool_remove, safe_may])
# describe tool or the "how" of removal
TOOL = Pattern(r'((ring )?forceps?|hook|speculum|fashion|(alligator )? clamp|'
               r'strings? (grasp|clasp)|(grasp|clasp)\w* strings?|'
               r'(with|gentle|more|\bw) traction|technique)')
PLAN = Pattern(r'\brem intrauterine device\b',
               negates=[])


class RemoveStatus(Status):
    NONE = -1
    REMOVE = 1
    TOOL_REMOVE = 2
    PLAN = 3
    SKIP = 99


def confirm_iud_removal(document: Document, expected=None):
    for value, text in determine_iud_removal(document):
        yield Result(value, value.value, expected, text)


def determine_iud_removal(document: Document):
    if document.has_patterns(REMOVE, PLAN, ignore_negation=True):
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
