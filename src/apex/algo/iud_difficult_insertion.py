from apex.algo.pattern import Document, Pattern
from apex.algo.result import Status, Result

negation = r'(\bor\b|without|\bno\b|w/?o|v25|pamphlet|brochure|possib)'
past = r'(past|has had)'

INSERTION = Pattern(r'insert(ed|ion)', negates=[past])
PROVIDER = Pattern(r'(difficult|complicat\w*|(with|more) traction|'
                   r'excessive instrument|challeng|'
                   r'cervi\w+ (stenosi|tight)|(stenosi|tight)\w+ cervi|'
                   r'severe flexion)',
                   negates=[negation])
US_GUIDE = Pattern(r'(u/?s|ultrasound) guid(ed?|ance)',
                   negates=[negation])
CERV_DIL = Pattern(r'(cervical (dilat|ripen)\w+|(dilat|ripen)\w*( of)?( the?) cervix)',
                   negates=[negation])
PARACERV = Pattern(r'(lidocaine|xylocaine|lignocaine|paracervical block|anesthe)',
                   negates=[negation])
MISPROSTOL = Pattern(r'(cytotec|misoprostol)',
                     negates=[negation])


class DiffInsStatus(Status):
    NONE = -1
    PROVIDER_STATEMENT = 1
    ULTRASOUND_GUIDANCE = 2
    CERVICAL_DILATION = 3
    PARACERVICAL_BLOCK = 4
    MISOPROSTOL = 5
    SKIP = 99


def confirm_difficult_insertion(document: Document, expected=None):
    for status, text in determine_difficult_insertion(document):
        yield Result(status, status.value, expected, text)


def determine_difficult_insertion(document: Document):
    """
    :param document:
    :return:
    """
    if document.has_patterns(INSERTION, ignore_negation=True):
        found = False
        for section in document.select_sentences_with_patterns(INSERTION, neighboring_sentences=1):
            if section.has_patterns(PROVIDER):
                yield DiffInsStatus.PROVIDER_STATEMENT, section.text
                found = True
            if section.has_patterns(US_GUIDE):
                yield DiffInsStatus.ULTRASOUND_GUIDANCE, section.text
                found = True
            if section.has_patterns(PARACERV):
                yield DiffInsStatus.PARACERVICAL_BLOCK, section.text
                found = True
            if section.has_patterns(MISPROSTOL):
                yield DiffInsStatus.MISOPROSTOL, section.text
                found = True
            if section.has_patterns(CERV_DIL):
                yield DiffInsStatus.CERVICAL_DILATION, section.text
                found = True
        if not found:
            pass
            # yield DiffInsStatus.NONE, document.text
    else:
        yield DiffInsStatus.SKIP, None  # change to skip
