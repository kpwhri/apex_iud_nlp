from apex.algo.pattern import Document, Pattern
from apex.algo.result import Result, Status
from apex.algo.shared import DATE_PAT, IUD, boilerplate, possible, negation, historical, POSSIBLE

embedded = r'([ie]mbedded|impacted)'
# removed: |foreign body
migrated = r'\b(stuck|migrat\w+|extrauterine|omentum|displac\w+|(intra)?peritoneal)'

impact_neg = r'(cerumen|tympanic|ear|hormon\w+)'

COMPLETE = Pattern('(intra (peritoneal|abdominal)|complete(ly)? perforat(ion|ed|e)s?)',
                   negates=[boilerplate, historical, negation, impact_neg])
PERFORATION = Pattern(r'('
                      r'perforat(ion|ed|e)s?|(pierc\w+|thr(ough|u))( the)?( uterine)? '
                      r'(endometrium|wall|myometrium|serosa|perimetrium)'
                      r')',
                      negates=[boilerplate, historical, negation, impact_neg])
PARTIAL = Pattern(r'partial(ly)? perforat(ion|ed|e)s?',
                  negates=[boilerplate, historical, possible, negation, impact_neg])
EMBEDDED = Pattern(f'({embedded})',
                   negates=[boilerplate, historical, possible, negation, impact_neg])
MIGRATED = Pattern(f'{migrated}',
                   negates=[boilerplate, historical, possible, negation])
LAPAROSCOPIC_REMOVAL = Pattern(r'('
                               r'(lap[ao]r[ao](scop|tom)|pelviscop)(\w+\W+){0,10} remov\w+|'
                               r'remov\w+(\w+\W+){0,10}lap[ao]r[ao]scop\w+'
                               r')',
                               negates=[historical, boilerplate])
ALL = (COMPLETE, PERFORATION, EMBEDDED, MIGRATED, LAPAROSCOPIC_REMOVAL)


class PerforationStatus(Status):
    NONE = 0
    PERFORATION = 1
    EMBEDDED = 2
    UNKNOWN = 3
    MIGRATED = 4
    PARTIAL = 5
    POSSIBLE = 6
    LAPAROSCOPIC_REMOVAL = 7
    COMPLETE = 8
    SKIP = 99


def confirm_iud_perforation(document: Document, expected=None):
    for value, text, date in determine_iud_perforation(document):
        yield Result(value, value.value, expected, text, date=date)


def determine_iud_perforation(document: Document):
    if document.has_patterns(*ALL, ignore_negation=True):
        # see if any sentences that contain "IUD" also contain perf/embedded
        for section in document.select_sentences_with_patterns(IUD):
            date = section.get_pattern(DATE_PAT)
            if section.has_patterns(COMPLETE):
                yield PerforationStatus.COMPLETE, section.text, date
            elif section.has_patterns(PARTIAL):
                yield PerforationStatus.PARTIAL, section.text, date
            elif section.has_patterns(PERFORATION):
                if section.has_pattern(POSSIBLE):
                    yield PerforationStatus.POSSIBLE, section.text, date
                else:
                    yield PerforationStatus.PERFORATION, section.text, date
            elif section.has_patterns(EMBEDDED):
                yield PerforationStatus.EMBEDDED, section.text, date
            elif section.has_patterns(MIGRATED):
                yield PerforationStatus.MIGRATED, section.text, date
            # check for laparoscopic removal -> suggests complete perf
            if section.has_patterns(LAPAROSCOPIC_REMOVAL):
                yield PerforationStatus.LAPAROSCOPIC_REMOVAL, section.text, date
        yield PerforationStatus.NONE, document.text, None
    else:
        yield PerforationStatus.SKIP, None, None
