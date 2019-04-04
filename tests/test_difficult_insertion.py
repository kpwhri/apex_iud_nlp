import pytest

from apex.algo.iud_difficult_insertion import SUCCESSFUL_INSERTION, UNSUCCESSFUL_INSERTION, CANNOT_PLACE


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
