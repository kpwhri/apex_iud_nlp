"""
Confirm IUD Insertion on specified date
"""
import enum
import logging
from collections import namedtuple

from apex.algo.pattern import Pattern, Document

Result = namedtuple('Result', 'value correct')


class InsertionStatus(enum.Enum):
    FAILED = 0
    HYPOTHETICAL = 1
    SUCCESS = 2
    LIKELY_SUCCESS = 3
    UNKNOWN = 4
    NO_MENTION = 5


IUD = Pattern(r'\b(mirena|paragard|iud|ius)\b')
INSERTION = Pattern(r'\b(insert|place)')
STRINGS = Pattern(r'\b(strings)')
NOT_SUCCESSFUL = Pattern(r'(n[o\']t|without|no)\W*(success)')
UNSUCCESSFUL = Pattern(r'(unsuccess|abandon)')
HYPOTHETICAL = Pattern(r'(following|remember)')
POST_SUCCESS = Pattern(r'(success|length of string|strings (cut|trim)|iud was( then)? insert)')
PRE_SUCCESS = Pattern(r'(without(\W*any)?\W*(difficult|problem)|as usual|usual( sterile)? fashion|strings were trimmed|'
                      r'per manufacturer[\'s]*\W*recommend)')
POST_OP = Pattern(r'(you think are related to the iud|check the (iud )?strings|'
                  r'have your iud removed or replaced)')
HISTORICAL = Pattern(r'(in the past|previous|months ago|days ago|last week|last month)')
APPOINTMENT = Pattern(r'(appt|appointment)')
DATE = Pattern(r'(\d{1,2}/\d{1,2}|january|february|march|'
               r'april|may|june|july|august|sept(ember)?|october|november|december|20\d{2})',
               negates=[r'\b(exp|expires?)'])
NEGATED = Pattern(r'not\W*inserted')


def classify_result(res: InsertionStatus):
    if res == InsertionStatus.SUCCESS:
        return 1
    elif res == InsertionStatus.LIKELY_SUCCESS:
        return 0
    elif res == InsertionStatus.FAILED:
        return -1
    elif res == InsertionStatus.HYPOTHETICAL:
        return -1
    elif res == InsertionStatus.NO_MENTION:
        return -1
    elif res == InsertionStatus.UNKNOWN:
        return -1
    return 0


def confirm_iud_insertion(document: Document, expected=None):
    value = determine_iud_insertion(document)
    res = classify_result(value)
    if expected is None:
        return Result(res, None)
    elif res == expected:
        return Result(res, res == expected)
    else:  # failed
        logging.warning(f'{document.name}:{value}=={expected}:{document.matches}')
        return Result(res, res == expected)


def determine_iud_insertion(document: Document):
    # discusses iud
    if document.has_patterns(IUD, INSERTION, has_all=True):
        section = document.select_sentences_with_patterns(IUD, INSERTION, STRINGS,
                                                          negation=[HISTORICAL, APPOINTMENT, DATE, NEGATED],
                                                          neighboring_sentences=1)
        if section:
            if section.has_patterns(PRE_SUCCESS):
                return InsertionStatus.SUCCESS
            elif section.has_patterns(UNSUCCESSFUL, NOT_SUCCESSFUL):
                return InsertionStatus.FAILED
            elif section.has_patterns(HYPOTHETICAL):
                return InsertionStatus.HYPOTHETICAL
            elif section.has_patterns(POST_SUCCESS):
                return InsertionStatus.SUCCESS
            elif section.has_patterns(POST_OP):
                return InsertionStatus.LIKELY_SUCCESS
            else:
                return InsertionStatus.UNKNOWN
        else:
            return InsertionStatus.UNKNOWN
    return InsertionStatus.NO_MENTION
