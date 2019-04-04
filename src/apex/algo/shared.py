from apex.algo.pattern import Pattern

# date pattern
years_ago = r'(?:\d+ (?:year|yr|week|wk|month|mon|day)s? (?:ago|before|previous))'
date_pat = r'\d+[-/]\d+[-/]\d+'
date2_pat = r'\d+[/]\d+'
month_pat = r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)\w*(?:\W*\d{1,2})?\W*\d{4}'
month_only_pat = r'in\b(?:jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)\w*'
DATE_PAT = Pattern(f'({years_ago}|{date_pat}|{date2_pat}|{month_pat}|{month_only_pat})')

# iud pattern
iuds = r'\b(iuds?|intrauterine( contraceptive)? devices?)'
lng_iuds = r'(lng ius|levonorgestrel( (releasing|rlse))? (intrauterine|us))'
brand = r'(mirena|paragu?ard|skyla\b|lilett?a|kyleena|copper)'
IUD = Pattern(f'({iuds}|{lng_iuds}|{brand})')

# status annotation patterns
in_place = r'(?<!not) in (place|situ)\b'
boilerplate = r'\b(complication|pamphlet|warning|information|review|side effect|counsel|\bsign|infection|ensure|' \
              r'cramps|risk|\bif\b|after your visit|conceive|appt|appointment|due (to|for|at)|recommend|' \
              r'pregnan|pamphlet|schedul|doctor|contact|\brare|\bhow\b|\bcall|includ|failure|' \
              r'associated|avoid|instruct|guideline)'
possible = r'\b(unlikely|\bposs\b|possib(ly|le|ility)|improbable|potential|susp(ect|icious)|' \
           r'chance|may\b|afraid|concern|tentative|doubt|thought|think)'
POSSIBLE = Pattern(possible)
negation = r'(no evidence|without|r/o|rule out|normal|\bnot?\b|\bor\b)'
historical = r'(history|previous|\bhx\b|\bpast\b|\bh/o\b)'
# avoid months (followed by day/year)
# avoid 'last' or 'in' or 'since'
safe_may = r'(?<!in|st|ce) may (?!\d)'
hypothetical = r'(option|possib\w+|desire|want|will|\bcan\b|usual|' \
               r'\bor\b|like|would|need|until|request|when|you ll|' \
               r'\bif\b|consider|concern|return|nervous|anxious|to be remov|could|' \
               r'discuss|inform|should|\btry|once|worr(y|ied)|question|ideal)'
