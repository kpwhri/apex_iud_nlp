import pytest

from apex.algo.breastfeeding import LACTATION_VISIT, BF_UNKNOWN, BF_EXACT, BF_NO_EXACT, EXPRESSED_MILK_EXACT, BF_YES


@pytest.mark.parametrize('text', [
    'lactation consultation',
])
def test_lactationvisit_regex_match(text):
    assert LACTATION_VISIT.matches(text)


@pytest.mark.parametrize('text', [
    'breastfeeding has been going well',
    'pt breastfeeding well',
    'breastfeeding exclusively',
    'exclusively breastfeeding',
    'currently breastfeeding',
])
def test_yes_regex_match(text):
    assert BF_YES.matches(text)


@pytest.mark.parametrize('text', [
    'Breastfeeding: {YES NO:17553}',
])
def test_bfunknown_regex_match(text):
    assert BF_UNKNOWN.matches(text)


@pytest.mark.parametrize('text', [
    'expressed breast milk: all',
    'expressed breast milk: 12oz',
    'expressed breast milk: 1/2-1 ounce total',
])
def test_expressedexact_regex_match(text):
    assert EXPRESSED_MILK_EXACT.matches(text)


@pytest.mark.parametrize('text', [
    'Breastfeeding frequency: every 2-2.5 hours one 3-4 hour interval at night',
    'pumping every 2-3 hours',
    'pumping every hour',
    'Breastfeeding frequency:8-10 x 45 minutes',
    'nursing frequency: 7-8 times/24 hours',
    'Breastfeeding frequency:8x day',
    'Intake at breast: 2.5 oz',
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


@pytest.mark.parametrize('text', [
    'advised exclusively breastfeeding',
    'Some exclusively breast feeding babies stool infrequently',
])
def test_not_yes_regex_match(text):
    assert not BF_YES.matches(text)
