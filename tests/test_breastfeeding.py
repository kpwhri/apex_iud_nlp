import pytest

from apex.algo.breastfeeding import LACTATION_VISIT, BF_UNKNOWN


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


# NOT

@pytest.mark.parametrize('text', [
    'prelactation consultation',
    'The lactation consultant usually advises waiting 4-5 days between offering new foods',
])
def test_not_lactationvisit_regex_match(text):
    assert not LACTATION_VISIT.matches(text)
