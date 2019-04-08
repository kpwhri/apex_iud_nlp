import pytest

from apex.algo.iud_difficult_insertion import SUCCESSFUL_INSERTION, UNSUCCESSFUL_INSERTION, CANNOT_PLACE, PROVIDER, \
    MISOPROSTOL


@pytest.mark.parametrize('text', [
    'Dr attempted insertion on 4/1/03 but had difficulty due to tight cervical os',
    'dilation was difficult',
])
def test_provider(text):
    assert PROVIDER.matches(text)


@pytest.mark.parametrize('text', [
    'miso',
    'misoprostol',
])
def test_misoprostol(text):
    assert MISOPROSTOL.matches(text)


@pytest.mark.parametrize('text', [
    'lack of miso',
    'misoprostol not done',
])
def test_not_misoprostol(text):
    assert not MISOPROSTOL.matches(text)


@pytest.mark.parametrize('text', [
    'strings trimmed',
    'strings were trimmed',
    'string was trimmed',
    'strings cut',
    'threads were snipped',
    'length of string',
    'successful removal and insertion of iud',
])
def test_successful_regex_match(text):
    assert SUCCESSFUL_INSERTION.matches(text)


@pytest.mark.parametrize('text', [
    'abandoned iud placement',
    'unsuccessful iud insertion',
    'unsuccessful due to narrow os',
    'procedure aborted',
    'procedure terminated',
    'I apologize for my unsuccessful insertion of your IUD',
])
def test_unsuccessful_regex_match(text):
    assert UNSUCCESSFUL_INSERTION.matches(text)


@pytest.mark.parametrize('text', [
    'history of pcos and failed iud insertion',
    'i don\'t place iuds',
    'i do not place iuds',
])
def test_not_cannotplace_regex_match(text):
    assert not CANNOT_PLACE.matches(text)


@pytest.mark.parametrize('text', [
    'cervix difficult to visualize',
    'complicated removal of existing IUD',
])
def test_not_provider(text):
    assert not PROVIDER.matches(text)
