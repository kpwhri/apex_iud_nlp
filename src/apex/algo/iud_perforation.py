from apex.algo.pattern import Document, Pattern
from apex.algo.result import Result, Status

iuds = r'\b(iuds?|intrauterine( contraceptive)? devices?)'
lng_iuds = r'(lng ius|levonorgestrel( (releasing|rlse))? (intrauterine|us))'
brand = r'(mirena|paragu?ard|skyla\b|lilett?a|kyleena|copper)'
embedded = r'([ie]mbedded|impacted)'
# removed: |foreign body
migrated = r'\b(stuck|migrat\w+|extrauterine|omentum|displac\w+|(intra)?peritoneal)'
boilerplate = r'\b(complication|pamphlet|warning|information|review|side effect|counsel|sign|infection|ensure|' \
              r'cramps|risk|\bif\b)'
possible = r'\b(unlikely|possib(ly|le|ility)|improbable|potential|suspect|chance|may\b|afraid|concern|tentative)'
negation = r'(no evidence|without|r/o|rule out|normal|\bnot?\b|\bor\b)'
history = r'(history of|previous|hx|past)'

impact_neg = r'(cerumen|tympanic|ear|hormon\w+)'

COMPLETE = Pattern('(intra (peritoneal|abdominal)|complete(ly)? perforat(ion|ed|e)s?)',
                   negates=[boilerplate, history, negation, impact_neg])
POSSIBLE = Pattern(possible)
PERFORATION = Pattern(r'('
                      r'perforat(ion|ed|e)s?|(pierc\w+|thr(ough|u))( the)?( uterine)? '
                      r'(endometrium|wall|myometrium|serosa|perimetrium)'
                      r')',
                      negates=[boilerplate, history, negation, impact_neg])
PARTIAL = Pattern(r'partial(ly)? perforat(ion|ed|e)s?',
                  negates=[boilerplate, history, possible, negation, impact_neg])
IUD = Pattern(f'({iuds}|{lng_iuds}|{brand})')
EMBEDDED = Pattern(f'({embedded})',
                   negates=[boilerplate, history, possible, negation, impact_neg])
MIGRATED = Pattern(f'{migrated}',
                   negates=[boilerplate, history, possible, negation])
LAPAROSCOPIC_REMOVAL = Pattern(r'('
                               r'(lap[ao]r[ao](scop|tom)|pelviscop)(\w+\W+){0,10} remov\w+|'
                               r'remov\w+(\w+\W+){0,10}lap[ao]r[ao]scop\w+'
                               r')',
                               negates=[history, boilerplate])
ALL = (COMPLETE, PERFORATION, EMBEDDED, MIGRATED, LAPAROSCOPIC_REMOVAL)
years_ago = r'(?:\d+ (?:year|yr|week|wk|month|mon|day)s? (?:ago|before|previous))'
date_pat = r'\d+[-/]\d+[-/]\d+'
date2_pat = r'\d+[/]\d+'
month_pat = r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)\w*(?:\W*\d{1,2})?\W*\d{4}'
month_only_pat = r'in\b(?:jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)\w*'
DATE_PAT = Pattern(f'({years_ago}|{date_pat}|{date2_pat}|{month_pat}|{month_only_pat})')


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
        yield Result(value, value.value, expected, text, extras=date)


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
