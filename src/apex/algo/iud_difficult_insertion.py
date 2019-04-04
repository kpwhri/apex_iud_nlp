import logging

from apex.algo.pattern import Document, Pattern
from apex.algo.result import Status, Result

# don't include "not" "insertion not completed since..."
from apex.algo.shared import IUD, hypothetical, possible, historical

negation = r'(\bor\b|with\W*out|\bno\b|w/?o|v25|pamphlet|brochure|possib|\bif\b|please|can be)'
past = r'(past|has had)'
other = r'(friends?)'
difficult = r'(remember)'

INSERTION = Pattern(r'insert(ed|ion)', negates=[past, 'forcep', 'clamp'])
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
CANNOT_PLACE = Pattern(
    r'('
    f'{IUD} (can)?n[o\']t( be)? place'
    f'|((can)?n[o\']t|unable)( to)? place {IUD}'
    f'|{IUD} (placement|insertion|attempt) (unsuccessful|failed|abandoned|aborted)'
    r')',
    negates=[possible, hypothetical, historical, r'\bi\b', r'\bdoes\b']
)
UNSUCCESSFUL_INSERTION = Pattern(r'(unsuccessful'
                                 r'|(procedure|insertion|attempt) (was )?(aborted|failed|terminated|abandoned)'
                                 r'|(aborted|failed|terminated|abandoned) (the )?(iud|procedure|insertion|attempt)'
                                 r')',
                                 negates=[possible, hypothetical, historical, 'string', 'speculum',
                                          'brush', 'forcep', 'clamp', r'remov\w+'])
SUCCESSFUL_INSERTION = Pattern(r'('
                               r'(trim|cut|clip|snip)\w* (the )?(stri?ng|thread)'
                               r'|(stri?ng|thread)s? ((was|were) )?(trim|cut|clip|snip)'
                               r'|length of (stri?ng|thread)'
                               r'|(stri?ng|thread) length'
                               f'|{IUD} placed'
                               f'|successful(ly)? ((removal and|{IUD}) )?insert'
                               r'|insert\w+ success'
                               r')',
                               negates=[possible, hypothetical])

US = Pattern(r'(\bu/?s\b|ultrasound|radiology)',
             negates=[negation])
US_USED = Pattern(r'('
                  r'guid(ed?|ance)|\bused?\b'
                  r'|(verif|determine|confirm)\w* (proper|correct)?'
                  f' ({IUD} )?(place|location|rotation)'
                  r')',
                  negates=[negation])
# uterine/uterus
CERV_DIL = Pattern(r'(cervical (dilat|ripen)\w+|(dilat|ripen)\w*( of)?( the?) cervix)',
                   negates=[negation])
PARACERV = Pattern(r'(\blido\b|\w+caine\b|paracervical block)',
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
    SUCCESSFUL = 8
    SKIP = 99


def confirm_difficult_insertion(document: Document, expected=None):
    for status, text in determine_difficult_insertion(document):
        logging.debug(f'{status}: {text}')
        if status.value in [1, 2, 3, 4, 5, 6]:
            yield Result(status, status.value, expected, text)


def determine_difficult_insertion(document: Document):
    """
    :param document:
    :return:
    """
    if document.has_patterns(NOT_IUD_INSERTION):
        yield DiffInsStatus.SKIP, None
    if document.has_patterns(CANNOT_PLACE):
        yield DiffInsStatus.UNSUCCESSFUL, document.text
    elif document.has_patterns(IUD, ignore_negation=True):
        if document.has_patterns(INSERTION, ignore_negation=True):
            if document.has_patterns(UNSUCCESSFUL_INSERTION, INSERTION, has_all=True):
                yield DiffInsStatus.UNSUCCESSFUL, document.text
            if document.has_patterns(SUCCESSFUL_INSERTION, INSERTION, has_all=True):
                yield DiffInsStatus.SUCCESSFUL, document.text
            found = False
            for section in document.select_sentences_with_patterns(INSERTION, neighboring_sentences=1):
                if section.has_patterns(EASY_INSERTION):
                    yield DiffInsStatus.NOT_DIFFICULT, section.text
                    continue
                if section.has_patterns(PROVIDER):
                    yield DiffInsStatus.PROVIDER_STATEMENT, section.text
                    found = True
                if section.has_patterns(US, US_USED, has_all=True):
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
