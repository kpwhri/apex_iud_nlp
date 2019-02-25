from apex.algo.pattern import Document, Pattern
from apex.algo.result import Result, Status
from apex.algo.shared import DATE_PAT, IUD, boilerplate, possible, negation, historical, POSSIBLE, in_place, \
    hypothetical

embedded = r'([ie]mbedded|impacted)'
# removed: |foreign body
migrated = r'\b(migrat\w+|displac\w+)'
not_stuck_neg = r'(easily removed|removed with use)'  # only for partial
impact_neg = r'(cerumen|tympanic|ear|hormon\w+)'

COMPLETE = Pattern('('
                   'intra (peritoneal|abdominal)|'
                   'complete(ly)? perforat(ion|ed|e)s?|'
                   'extrauterine|omentum|abdominopelvic|'
                   r'perforat(ion|ed|e)s?|(pierc\w+|thr(ough|u)|into)( the)?( uterine)? '
                   r'(serosa|perimetrium|adnexa\w*)|'
                   f'{IUD} (visible|seen|visual\\w+)? in vagina'
                   r')',
                   negates=[boilerplate, historical, negation, impact_neg, possible,
                            hypothetical, 'against', 'free'])
PERFORATION = Pattern(r'('
                      r'perforat(ion|ed|e)s?|(pierc\w+|thr(ough|u)|into|to)'
                      r'( the)?( uterine)? (wall|myometrium|serosa)'
                      r')',
                      negates=[boilerplate, historical, negation, impact_neg, possible, hypothetical])
PARTIAL = Pattern(f'(partial(ly)? perforat(ion|ed|e)s?|arm broke|broken {IUD}|'
                  f'{IUD} (is|was)? (stuck|(visible|visual\\w+|seen) (at|in)? cervix)'
                  f')',
                  negates=[boilerplate, historical, possible, negation, impact_neg, possible, hypothetical])
EMBEDDED = Pattern(f'({embedded})',
                   negates=[boilerplate, historical, possible, negation, impact_neg, possible, hypothetical])
MIGRATED = Pattern(f'{migrated}',
                   negates=[boilerplate, historical, possible, negation, 'strings?', in_place])
LAPAROSCOPIC_REMOVAL = Pattern(r'('
                               r'(lap[ao]r[ao](scop|tom)|pelviscop)(\w+\s+){0,10} (remov|retriev)\w+|'
                               r'(remov|retriev)\w+(\w+\s+){0,10}lap[ao]r[ao]scop\w+'
                               r')',
                               negates=[historical, boilerplate, 'hysterectomy', r'excis\w+',
                                        'cysts?', 'tubal ligati\w+', r'steriliz\w+', r'bilat\w+',
                                        'diagnostic', 'tube', 'salping', 'btl', 'ovary',
                                        possible, hypothetical])

# displace + iud visible at/in cervix = PARTIAL
# iud visible [in cervix] == partial
#  [in vagina] == complete
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
        if value.value in [1, 5, 7, 8]:
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
            # elif section.has_patterns(EMBEDDED):
            #     yield PerforationStatus.EMBEDDED, section.text, date
            # elif section.has_patterns(MIGRATED):
            #     yield PerforationStatus.MIGRATED, section.text, date
            # check for laparoscopic removal -> suggests complete perf
            if section.has_patterns(LAPAROSCOPIC_REMOVAL):
                yield PerforationStatus.LAPAROSCOPIC_REMOVAL, section.text, date
        yield PerforationStatus.NONE, document.text, None
    else:
        yield PerforationStatus.SKIP, None, None
