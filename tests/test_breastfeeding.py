import pytest

from apex.algo.breastfeeding import LACTATION_VISIT, BF_UNKNOWN, BF_EXACT, BF_NO_EXACT


@pytest.mark.parametrize('text', [
    'lactation consultation',
])
def test_lactationvisit_regex_match(text):
    assert LACTATION_VISIT.matches(text)


@pytest.mark.parametrize('text', [
    'Breastfeeding: {YES NO:17553}',
])
def test_bfunknown_regex_match(text):
    assert BF_UNKNOWN.matches(text)


@pytest.mark.parametrize('text', [
    '9.	Breastfeeding frequency: every 2-2.5 hours one 3-4 hour interval at night',
])
def test_bfexact_regex_match(text):
    assert BF_EXACT.matches(text)
    assert not BF_NO_EXACT.matches(text)



# NOT

@pytest.mark.parametrize('text', [
    'prelactation consultation',
    'The lactation consultant usually advises waiting 4-5 days between offering new foods',
])
def test_not_lactationvisit_regex_match(text):
    assert not LACTATION_VISIT.matches(text)
