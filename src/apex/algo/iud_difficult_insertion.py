import logging

from apex.algo.pattern import Document, Pattern
from apex.algo.result import Status, Result

# don't include "not" "insertion not completed since..."
from apex.algo.shared import IUD

negation = r'(\bor\b|with\W*out|\bno\b|w/?o|v25|pamphlet|brochure|possib|\bif\b|please|can be)'
past = r'(past|has had)'
other = r'(friends?)'
difficult = r'(remember)'

INSERTION = Pattern(r'insert(ed|ion)', negates=[past])
EASY_INSERTION = Pattern(r'(uncomplicat\w+|with out (difficulty|complication)|easily|'
                         r'complications? none|with ease)',
                         negates=['v25'])
PROVIDER = Pattern(r'(difficult|\bcomplicat\w*|(with|more) traction|'
                   r'excessive (instrument|force)|challeng|'
                   r'cervi\w+ (stenosi|tight)|(stenosi|tight)\w+ cervi'
                   r')',
                   negates=[negation, other, difficult])

NOT_IUD_INSERTION = Pattern(r'(implanon (was )?(placed|inserted)|'
                            f'{IUD} removal'
                            r')')
UNSUCCESSFUL_INSERTION = Pattern(r'(unsuccessful|'
                                 f'{IUD} (can)?n[o\']t( be)? place|'
                                 f'((can)?n[o\']t|unable)( to)? place {IUD}'
                                 r')')

# us "used", us "confirmed proper/correct placement" properly
US_GUIDE = Pattern(r'(u/?s|ultrasound) guid(ed?|ance)',
                   negates=[negation])
CERV_DIL = Pattern(r'(cervical (dilat|ripen)\w+|(dilat|ripen)\w*( of)?( the?) cervix)',
                   negates=[negation])
PARACERV = Pattern(r'(lidocaine|xylocaine|lignocaine|paracervical block)',
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
    UNSUCCESSFUL = 6
    NOT_DIFFICULT = 7
    SKIP = 99


def confirm_difficult_insertion(document: Document, expected=None):
    for status, text in determine_difficult_insertion(document):
        logging.debug(f'{status}: {text}')
        if status in [1, 2, 3, 4, 5, 6]:
            yield Result(status, status.value, expected, text)


def determine_difficult_insertion(document: Document):
    """
    :param document:
    :return:
    """
    if document.has_patterns(NOT_IUD_INSERTION):
        yield DiffInsStatus.SKIP, None
    elif document.has_patterns(IUD, ignore_negation=True):
        if document.has_patterns(UNSUCCESSFUL_INSERTION):
            yield DiffInsStatus.UNSUCCESSFUL, None
        elif document.has_patterns(INSERTION, ignore_negation=True):
            found = False
            for section in document.select_sentences_with_patterns(INSERTION, neighboring_sentences=1):
                if section.has_patterns(EASY_INSERTION):
                    yield DiffInsStatus.NOT_DIFFICULT, section.text
                    continue
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
