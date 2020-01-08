from apex.algo.shared import IUD, boilerplate, safe_may, hypothetical, in_place
from apex.algo.pattern import Document, Pattern
from apex.algo.result import Status, Result

negation = r'(ready|should|sometimes|must|decline|\bnot\b)'
other = r'(fibroid|v25.1\d|tampon)'
tool_remove = r'(introducer|inserter|tenaculum|instruments?)( (was|were))? removed'
words_3 = r'( \w+){0,3}'

REMOVE_BY = Pattern(f'(remov\\w+|replac\\w+){IUD} by')

REMOVE = Pattern(r'(remov\w+|replac\w+)',
                 negates=[negation, boilerplate, hypothetical, in_place,
                          other, tool_remove, safe_may, 'rtc', 'easiest time', r'\bplan\b'])
PROB_REMOVE = Pattern(f'{IUD} was removed')
DEF_REMOVE = Pattern(f'{IUD} ('
                     f'(was )?remov(ed|al|e) '
                     f'({words_3} (difficulty|problem|traction|easy)|easily|quickly)'
                     f'|((easily|quickly|(un)?complicat) remov(ed|al|e))'
                     f'|{words_3} ?grasp(ed|ing)? {words_3} remov(ed|al|e)'
                     f')', negates=['risk', 'to (have|get)', 'come in'])

DEF_REPLACE = Pattern(f'{IUD} remov(ed|al) {words_3} replac')
TOOL = Pattern(r'((ring )?forceps?|hook|speculum|fashion|(alligator )? clamp|'
               r'strings? (grasp|clasp)|(grasp|clasp)\w* strings?|'
               r'(with|gentle|more|\bw) traction|technique)',
               negates=[r'\bplaced\b', 'insertion', 'trimmed',
                        'unsuccessful', 'unable', r'not (recover|retriev|remove)\w+'])
PLAN = Pattern(r'\brem intrauterine device\b',
               negates=[])
ALL = (REMOVE, DEF_REMOVE, PROB_REMOVE, DEF_REPLACE, TOOL, PLAN)


class RemoveStatus(Status):
    NONE = -1
    REMOVE = 1
    TOOL_REMOVE = 2
    PLAN = 3
    DEF_REMOVE = 4
    DEF_REPLACE = 5
    SKIP = 99


def confirm_iud_removal(document: Document, expected=None):
    for value, text in determine_iud_removal(document):
        if value.value in [1, 2, 3, 4, 5]:
            yield Result(value, value.value, expected, text)


def determine_iud_removal(document: Document):
    if document.has_patterns(*ALL, ignore_negation=True):
        section_text = []
        for section in document.select_sentences_with_patterns(IUD):
            if section.has_pattern(REMOVE_BY):
                continue
            # these definitely have correct language
            if section.has_patterns(*ALL):
                # require either REMOVE/PLAN since this could have other refs
                if section.has_patterns(DEF_REMOVE):
                    yield RemoveStatus.DEF_REMOVE, section.text
                if section.has_patterns(DEF_REPLACE):
                    yield RemoveStatus.DEF_REPLACE, section.text
                if section.has_patterns(PROB_REMOVE):
                    yield RemoveStatus.REMOVE, section.text
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
