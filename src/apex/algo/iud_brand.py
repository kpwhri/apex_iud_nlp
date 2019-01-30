from collections import Counter

from apex.algo.pattern import Document, Pattern
from apex.algo.result import Status, Result


hypothetical = r'(risks?|benefits?|\bvs\b|\bor\b|questions?|please|stocked|order|' \
               r'pamphlet|brochure|\bif\b|option|availab|decid|plan|interest|consult|' \
               r'want|desir[ei]\w*|appt|appointment|can|could|would|believe|think|switch|' \
               r'information)'
negative = r'(cannot|\bnot\b)'
PARAGARD = Pattern(r'(paragu?ard)', negates=[hypothetical])
MIRENA = Pattern(r'(mirena)', negates=[hypothetical])
LILETTA = Pattern(r'(lilett?a)', negates=[hypothetical])
KYLEENA = Pattern(r'(kyleena)', negates=[hypothetical])
SKYLA = Pattern(r'(skyla)\b', negates=[hypothetical])
COPPER = Pattern(r'(copper) (\w+ )?iu[sd]\b', negates=[hypothetical])
LNG = Pattern(r'(levonorgestrel|lng) (\w+ )?iu[sd]\b',
              negates=['oral tab', hypothetical, 'plan b'])
IUD = (PARAGARD, MIRENA, LILETTA, KYLEENA, SKYLA, COPPER, LNG)
# not sure how to use? e.g., 'skyla in place but pain exam scheduled [date]'
SCHEDULED = Pattern(r'schedul\w+', negates=['today'])
USING = Pattern(r'(ha[sd]|us(es?|ing)|insert(ed|ion)|iud type|contracepti(on|ve)|in (situ|place)|(re)?placed)',
                negates=['(expel|remove)'])


class BrandStatus(Status):
    NONE = -1
    PARAGARD = 1
    MIRENA = 2
    LILETTA = 3
    KYLEENA = 4
    SKYLA = 5
    COPPER = 6
    LNG = 7
    SKIP = 99


def get_iud_brand(document: Document, expected=None):
    """
    Heuristics:
        * there can be multiple brands mentioned in a single sentence,
            but more frequent usually selecte
        * context which discusses 'use'/'had'/'insert'/'contraception' retained prior
            to other mentions
    :param document:
    :param expected:
    :return:
    """
    brands = determine_iud_brand(document)
    if len(brands) > 1:
        # if any has_using ('use', 'insert', 'contraception') values, only retain those
        has_using = bool([u for _, u, _ in brands if u])
        # get most frequent (sometimes there is discussion of more than one)
        brands = ((b, u, t) for b, u, t in brands if u == has_using)
        c = Counter(b for b, u, _ in brands)
        if len(c) > 1:  # still multiple brands
            v1, v2 = c.most_common(2)
            if v1[1] == v2[1]:  # equally frequent, likely hypothetical discussion
                yield Result(BrandStatus.NONE, -1, expected, text=document.text)
                raise StopIteration
            brands = ((b, u, t) for b, u, t in brands if c[b] == v1[1])
    for brand, using, text in brands:
        if brand.value in [1, 2, 3, 4, 5, 6]:
            yield Result(brand, brand.value, expected, text=text)


def determine_iud_brand(document: Document):
    if document.has_patterns(*IUD, ignore_negation=True):
        brands = []
        for section in document.select_sentences_with_patterns(*IUD, neighboring_sentences=1):
            # scheduled = bool(section.has_patterns(SCHEDULED))
            if section.has_patterns(PARAGARD, COPPER):
                brands.append((BrandStatus.PARAGARD, section.has_patterns(USING), section.text))
            if section.has_patterns(MIRENA):
                brands.append((BrandStatus.MIRENA, section.has_patterns(USING), section.text))
            if section.has_patterns(LILETTA):
                brands.append((BrandStatus.LILETTA, section.has_patterns(USING), section.text))
            if section.has_patterns(KYLEENA):
                brands.append((BrandStatus.KYLEENA, section.has_patterns(USING), section.text))
            if section.has_patterns(SKYLA):
                brands.append((BrandStatus.SKYLA, section.has_patterns(USING), section.text))
        if not brands:  # only look for LNG if no brand name
            if document.has_patterns(LNG):
                brands.append((BrandStatus.LNG,  False, document.text))
            else:
                brands.append((BrandStatus.NONE, False, None))
        return brands
    else:
        return [(BrandStatus.SKIP, False, None)]
