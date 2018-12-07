from apex.algo.pattern import Document, Pattern
from apex.algo.result import Result, Status


GRAVIDA_0 = Pattern(r'(\b(g|grav\w*) 0|'
                    r'grav para term preterm abortions tab sab ect mult living 0)')
PARA_0 = Pattern(r'(\bg \d{1,2} p 0|'
                 r'g \d{1,2}.{0,20}? p 0|'
                 r'para (0|zero|none|na)|'
                 r'grav para term preterm abortions tab sab ect mult living \d 0)')
NULLIPAROUS = Pattern(r'(virginal|null?i?(par[ao]|grav))')
MULTIPAROUS = Pattern(r'(multipar|c(ervi)?x( \w+){0,5} par[ao])')
CHILD_0 = Pattern(r'children: (none|0)')

PARA_N = Pattern(r'(?:\bg \d{1,2} p (\d)|'
                 r'g \d{1,2}.{0,20}? p (\d)|'
                 r'para (\d)|'
                 r'grav para term preterm abortions tab sab ect mult living \d (\d))')
CHILD_NUM = Pattern(r'children: ([1-9])')
CHILD_N = Pattern(r'children: (one|two|three|four|five|six|seven|eight|nine|ten)')
N_CHILD = Pattern(r'(one|two|three|four|five|six|seven|eight|nine|ten) child')


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
    status, text = determine_parity(document)
    return Result(status, status.value, expected, text)


def determine_parity(document: Document):
    text = document.get_patterns(GRAVIDA_0, PARA_0, NULLIPAROUS, CHILD_0)
    if text:
        return ParityStatus.P0, text
    res = document.get_patterns(PARA_N, CHILD_N, CHILD_NUM, index=(0, 1))
    if res:
        text, captured = res
        status = extract_status(captured)
        if status:
            return status, text
        else:
            print(status, text)
    text = document.get_patterns(MULTIPAROUS)
    if text:
        return ParityStatus.MULTIPAROUS, text
    return ParityStatus.SKIP, None


def extract_status(captured):
    captured = captured.strip()
    if captured in ('1', 'one'):
        return ParityStatus.P1
    if captured in ('2', 'two', 'twice'):
        return ParityStatus.P2
    if captured in ('3', 'three', 'thrice'):
        return ParityStatus.P3
    if captured in ('4', 'four'):
        return ParityStatus.P4
    if captured in ('5', 'five'):
        return ParityStatus.P5
    if captured in ('6', 'six'):
        return ParityStatus.P6
    if captured in ('7', 'seven'):
        return ParityStatus.P7
    if captured in ('8', 'eight'):
        return ParityStatus.P8
    if captured in ('9', 'nine'):
        return ParityStatus.P9
    if captured in ('10', 'ten'):
        return ParityStatus.P10
    if captured in ('11', 'eleven'):
        return ParityStatus.P11
    if captured in ('12', 'twelve'):
        return ParityStatus.P12
    return None
