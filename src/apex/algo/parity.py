import logging

from apex.algo.pattern import Document, Pattern
from apex.algo.result import Result, Status, Source

GRAVIDA_0 = Pattern(r'(\b(g|grav\w*) 0\W|'
                    r'grav para term preterm abortions tab sab ect mult living 0)')
PARA_0 = Pattern(r'(\bg \d{1,2} p 0|'
                 r'g \d{1,2} p 0|'
                 r'para (0|zero|none|0\d\d\d)\b|'
                 r'grav para term preterm abortions tab sab ect mult living \d{1,2} 0)')
NULLIPAROUS = Pattern(r'(virginal|null?i?(par(a|ity|ous)|grav))')
MULTIPAROUS = Pattern(r'(multipar(a|ity|ous)]|c(ervi)?x\b( \w+){0,5} par(a|ous|ity)\b)')
CHILD_0 = Pattern(r'children: (none|0)')

PARA_NNNN = Pattern(r'para (\d)\d\d\d')
PARA_N = Pattern(r'para (\d{1,2})\b')
G_PARA_N = Pattern(r'(?:g(\d)p(\d)\d\d\d\W|'  # "x is a G2P1001 with ..."
                   r'\bg (\d{1,2}) p (\d{1,2})|'
                   r'g (\d{1,2}) p (\d{1,2})|'
                   r'grav para term preterm abortions tab sab ect mult living (\d{1,2}) (\d{1,2}))',
                   capture_length=2)
CHILD_NUM = Pattern(r'number of children: ([1-9]{1,2})\W')
CHILD_N = Pattern(r'number of children: (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)')
# "one child" has two many false positives, discussing "one child...[did this or that]"
N_CHILD = Pattern(r'(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve) children')


class ParitySource(Source):
    NONE = -1
    PARITY = 1
    GRAVIDA = 2
    CHILDREN = 3


class ParityStatus(Status):
    NONE = -1
    P0 = 0
    P1 = 1
    P2 = 2
    P3 = 3
    P4 = 4
    P5 = 5
    P6 = 6
    P7 = 7
    P8 = 8
    P9 = 9
    P10 = 10
    P11 = 11
    P12 = 12
    MULTIPAROUS = 100
    SKIP = 99


def get_parity(document: Document, expected=None):
    status, text, source = determine_parity(document)
    yield Result(status, status.value, expected, text, extras=source)


def determine_parity(document: Document):
    res = document.get_patterns(GRAVIDA_0, PARA_0, NULLIPAROUS, CHILD_0,
                                names=[ParitySource.GRAVIDA, ParitySource.PARITY,
                                       ParitySource.PARITY, ParitySource.CHILDREN])
    if res:
        text, src = res
        if text:
            return ParityStatus.P0, text, src
    # patterns for grav and para; confirm grav >= para
    res = document.get_patterns(G_PARA_N, index=(0, 1, 2))
    if res:
        text, capt_g, capt_p = res
        try:
            g = int(capt_g)
            p = int(capt_p)
        except ValueError:
            raise ValueError(f'Values of g/p do not appear to be numeric: {capt_p}, {capt_g} in {text}')
        except TypeError:
            raise TypeError(f'Values of g/p are None (or similar): {capt_p}, {capt_g} in {text}')
        else:
            if g >= p:
                status = extract_status(capt_p)
                if status:
                    return status, text, ParitySource.PARITY
            else:
                logging.info(f'Gravida {g} < Parity {p}: {document.name}')

    res = document.get_patterns(PARA_NNNN, PARA_N, CHILD_N, CHILD_NUM, index=(0, 1),
                                names=[ParitySource.PARITY, ParitySource.PARITY,
                                       ParitySource.CHILDREN, ParitySource.CHILDREN])
    if res and res[0]:
        (text, captured), src = res
        if captured:
            status = extract_status(captured)
            if status:
                return status, text, src
            else:
                logging.info(f'Unrecognized parity value for {document.name}: {status} in "{text}" from {src}')
    text = document.get_patterns(MULTIPAROUS)
    if text:
        return ParityStatus.MULTIPAROUS, text, ParitySource.PARITY
    return ParityStatus.SKIP, None, ParitySource.NONE


def extract_status(captured):
    captured = captured.strip().lower()
    if captured in ('0', '00', 'zero', 'none'):
        return ParityStatus.P0
    if captured in ('1', '01', 'one'):
        return ParityStatus.P1
    if captured in ('2', '02', 'two', 'twice'):
        return ParityStatus.P2
    if captured in ('3', '03', 'three', 'thrice'):
        return ParityStatus.P3
    if captured in ('4', '04', 'four'):
        return ParityStatus.P4
    if captured in ('5', '05', 'five'):
        return ParityStatus.P5
    if captured in ('6', '06', 'six'):
        return ParityStatus.P6
    if captured in ('7', '07', 'seven'):
        return ParityStatus.P7
    if captured in ('8', '08', 'eight'):
        return ParityStatus.P8
    if captured in ('9', '09', 'nine'):
        return ParityStatus.P9
    if captured in ('10', 'ten'):
        return ParityStatus.P10
    if captured in ('11', 'eleven'):
        return ParityStatus.P11
    if captured in ('12', 'twelve'):
        return ParityStatus.P12
    return None
