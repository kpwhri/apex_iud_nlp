import pytest

from apex.algo.iud_expulsion import PARTIAL_EXP, MISSING, STRINGS, DISPLACEMENT, INCORRECT, PLACEMENT, PREVIOUS, \
    PROPER_LOCATION
from apex.algo.iud_expulsion_rad import MALPOSITION, NOT_SEEN_IUD, IUD_NOT_SEEN, IUD_PRESENT, STRING, VISIBLE
from apex.algo.shared import IUD


@pytest.mark.parametrize('text', [
    'There is an intrauterine device in place , however it is positioned in the cervix rather than the upper '
    'endometrial canal .',
    'IUD is malpositioned in the lower uterine segment / cervix',
    'IUD is very low and located in the cervix',
    'located in the cervical canal',
    'tip now located in the cervical region',
    'partial expulsion',
    'IUD protruding from os',
    'IUD was located in the lower uterine segment/upper part of the cervix',
    'identified it in the anterior portion in the lower uterus and cervical canal',
    'visualized extruding from cervical os',
])
def test_partial_regex_match(text):
    assert PARTIAL_EXP.matches(text), PARTIAL_EXP.pattern.pattern


@pytest.mark.parametrize('text', [
    'strings visualized extruding from cervical os',
])
def test_not_partial_regex_match(text):
    assert not PARTIAL_EXP.matches(text), PARTIAL_EXP.pattern.pattern


@pytest.mark.parametrize('text', [
    'previous iud was expelled',
    'history of partially expelled iud',
    'her last iud was problematic',
])
def test_previous_regex_match(text):
    assert PREVIOUS.matches(text), PREVIOUS.pattern.pattern


@pytest.mark.parametrize('text', [
    'a portion of the IUD that is still located within the lower uterine cavity',
    'IUD is malpositioned in the lower uterine segment',
    'distal to the expected / desired position',
])
def test_malposition_regex_match(text):
    assert MALPOSITION.matches(text)


@pytest.mark.parametrize('text', [
    'Dislodgement of IUD',
])
def test_displacement_regex_match(text):
    assert DISPLACEMENT.matches(text)


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
    'Mirena not seen',
])
def test_iudpresent_regex_match(text):
    """Confirm proper hst/sas"""
    assert IUD_PRESENT.matches(text) and IUD.matches(text)


@pytest.mark.parametrize('text', [
    'strings missing',
])
def test_stringsearch_regex_match(text):
    """Confirm proper hst/sas"""
    assert STRING.matches(text) and VISIBLE.matches(text)


@pytest.mark.parametrize('text', [
    'Unable to find IUD string',
])
def test_stringsmissing_regex_match(text):
    """Confirm proper hst/sas"""
    assert MISSING.matches(text) and STRINGS.matches(text)


@pytest.mark.parametrize('text', [
    'iud is in expected position',
    'IUD appears to be in appropriate position within a retroverted uterus',
    'mirena iud in place',
    'An IUD is in appropriate position within the uterus',
    'appears appropriately positioned',
    'is appropriately positioned',
    'IUD in appropriate position',
    'IUD is visualized within the endometrial cavity',
    'IUD present in the uterus',
    'iud was in good position',
    'iud appears properly positioned in the uterus',
    'IUD located in the uterus'
])
def test_proper_location_match(text):
    assert PROPER_LOCATION.matches(text)


@pytest.mark.parametrize('text', [
    'iud is not in expected position',
    'Reviewed risks of IUD placement',
    'confirm proper placement of iud',
    'recent IUD placement who presents',
    'iud is out of place',
    'Difficult to determine if the IUD is within the endometrial cavity',
    'the option of leaving it in place for longer than 5 years',
])
def test_not_proper_location_match(text):
    assert not PROPER_LOCATION.matches(text)


# NOT
@pytest.mark.parametrize('text', [
    'removed IUD with tendon forceps and rotating IUD during removal'
])
def test_not_displacement_regex_match(text):
    assert not DISPLACEMENT.matches(text)


@pytest.mark.parametrize('text', [
    'Gently attempted to dislodge and bring IUD out by applying loop and moving it towards me',
])
def test_not_malposition_regex_match(text):
    assert not MALPOSITION.matches(text)


@pytest.mark.parametrize('text', [
    'After delivery she had an IUD placed and felt that her mood was bad the entire time she had it in'
])
def test_not_incorrectplacement_regex_match(text):
    assert not (INCORRECT.matches(text) and PLACEMENT.matches(text))


@pytest.mark.parametrize('text', [
    'IUD string was Localized in the OS, no evidence of the IUD itself, cannot feel the tip',
])
def test_not_stringsmissing_regex_match(text):
    """Confirm proper hst/sas"""
    assert not (MISSING.matches(text) and STRINGS.matches(text))


@pytest.mark.parametrize('text', [
    'previous iud was expelled recently',
    'her last iud was problematic, falling out 10 days ago',
])
def test_not_previous_regex_match(text):
    assert not PREVIOUS.matches(text), PREVIOUS.pattern.pattern
