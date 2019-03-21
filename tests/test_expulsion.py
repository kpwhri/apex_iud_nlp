import pytest

from apex.algo.iud_expulsion import PARTIAL_EXP
from apex.algo.iud_expulsion_rad import MALPOSITION, NOT_SEEN_IUD, IUD_NOT_SEEN, IUD_PRESENT, STRING, VISIBLE
from apex.algo.shared import IUD


@pytest.mark.parametrize('text', [
    'There is an intrauterine device in place , however it is positioned in the cervix rather than the upper '
    'endometrial canal .',
    'IUD is malpositioned in the lower uterine segment / cervix',
    'IUD is very low and located in the cervix',
    'located in the cervical canal',
    'tip now located in the cervical region',
])
def test_partial_regex_match(text):
    assert PARTIAL_EXP.matches(text)


@pytest.mark.parametrize('text', [
    'a portion of the IUD that is still located within the lower uterine cavity',
    'IUD is malpositioned in the lower uterine segment',
    'distal to the expected / desired position',
])
def test_malposition_regex_match(text):
    assert MALPOSITION.matches(text)


@pytest.mark.parametrize('text', [
    'No intrauterine device identified',
])
def test_notseeniud_regex_match(text):
    assert NOT_SEEN_IUD.matches(text)


@pytest.mark.parametrize('text', [
    'IUD was not visualized transabdominally or transvaginally',
])
def test_iudnotseen_regex_match(text):
    assert IUD_NOT_SEEN.matches(text)


@pytest.mark.parametrize('text', [
    'Confirm no IUD seen in abdomen / pelvis',
    'Mirena not seen'
])
def test_iudpresent_regex_match(text):
    """Confirm proper hst/sas"""
    assert IUD_PRESENT.matches(text) and IUD.matches(text)


@pytest.mark.parametrize('text', [
    'strings missing',
])
def test_stringsmissing_regex_match(text):
    """Confirm proper hst/sas"""
    assert STRING.matches(text) and VISIBLE.matches(text)
