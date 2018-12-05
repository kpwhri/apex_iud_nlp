from apex.algo.iud_perforation import IUD
from apex.algo.pattern import Document, Pattern
from apex.algo.result import Status


INSERTION = Pattern(r'insert(ed|ion)')
PROVIDER = Pattern(r'(((difficult|complicated)( \w+)? insertion)|insertion( \w+)? (difficult|complicated))')
US_GUIDE = Pattern(r'(u/s|ultrasound) guid(ed?|ance)')
CERV_DIL = Pattern(r'')
PARACERV = Pattern(r'lidocaine')
MISPROSTOL = Pattern(r'cytotec')


class DiffInsStatus(Status):
    NONE = -1
    PROVIDER_STATEMENT = 1
    ULTRASOUND_GUIDANCE = 2
    CERVICAL_DILATION = 3
    PARACERVICAL_BLOCK = 4
    MISOPROSTOL = 5
    SKIP = 99


def confirm_difficult_insertion(document: Document, expected=None):
    determine_difficult_insertion(document)


def determine_difficult_insertion(document: Document):
    """
    :param document:
    :return:
    """
    if document.has_patterns(PROVIDER, ignore_negation=True):
        for section in document.select_sentences_with_patterns(IUD):
            pass
    else:
        return DiffInsStatus.NONE  # change to skip
