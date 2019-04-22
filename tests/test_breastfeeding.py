import pytest

from apex.algo.breastfeeding import LACTATION_VISIT, BF_UNKNOWN, BF_EXACT, BF_NO_EXACT, EXPRESSED_MILK_EXACT, BF_YES, \
    PUMPING_ACTIVE, NIPPLE_SHIELD, BF_FEEDING, WHOLE_MILK, matches_nutrition_not_bf


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
    'she is currently breast feeding',
    'she is breast feeding',
])
def test_yes_regex_match(text):
    assert BF_YES.matches(text)


@pytest.mark.parametrize('text', [
    'weaning from nipple shield'
])
def test_nippleshield_regex_match(text):
    assert NIPPLE_SHIELD.matches(text)


@pytest.mark.parametrize('text', [
    'breast pumping',
    'is using a breast pump',
])
def test_pumpactive_regex_match(text):
    assert PUMPING_ACTIVE.matches(text)


@pytest.mark.parametrize('text', [
    'Breastfeeding: {YES NO:17553}',
])
def test_bfunknown_regex_match(text):
    assert BF_UNKNOWN.matches(text)


@pytest.mark.parametrize('text', [
    'expressed breast milk: all',
    'expressed breast milk: 12oz',
    'expressed breast milk: 1/2-1 ounce total',
    '10-20ml of expressed breastmilk',
])
def test_expressedexact_regex_match(text):
    assert EXPRESSED_MILK_EXACT.matches(text)


@pytest.mark.parametrize('text', [
    'nutrition: both breast and ebm',
])
def test_bffeeding_regex_match(text):
    assert BF_FEEDING.matches(text)


@pytest.mark.parametrize('text', [
    'Nutrition:  solids and formula and whole milk',
])
def test_wholemilk_regex_match(text):
    assert WHOLE_MILK.matches(text)


@pytest.mark.parametrize('text', [
    'Water: public water supply Nutrition: whole milk And still breast feeding',
    'Nutrition:  solids and breast and whole milk'
])
def test_not_wholemilk_regex_match(text):
    assert not WHOLE_MILK.matches(text)


@pytest.mark.parametrize('text', [
    'Breastfeeding frequency: every 2-2.5 hours one 3-4 hour interval at night',
    'pumping every 2-3 hours',
    'pumping every hour',
    'Breastfeeding frequency:8-10 x 45 minutes',
    'nursing frequency: 7-8 times/24 hours',
    'Breastfeeding frequency:8x day',
    'Intake at breast: 2.5 oz',
    'breast feeding every 3-4 hours for 10 minutes per side',
    'Problems with breastfeeding: yes',  # problems imply breastfeeding ongoing
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
    'ideally after breast-feeding exclusively',
])
def test_not_yes_regex_match(text):
    assert not BF_YES.matches(text)


@pytest.mark.parametrize('text', [
    'not initiating breast pumping',
    'Breast pumping and galactogogue therapy may help',
])
def test_not_pumpactive_regex_match(text):
    assert not PUMPING_ACTIVE.matches(text)


@pytest.mark.parametrize('text', [
    'breastfeeding: No    Tobacco Use: quit',
    'breastfeeding: None    Tobacco Use: quit',
    'breastfeeding: N    Tobacco Use: quit',
    'breastfeeding: denies    Tobacco Use: quit',
])
def test_bfno_regex_match(text):
    assert BF_NO_EXACT.matches(text)


@pytest.mark.parametrize('text', [
    'Problems with breastfeeding: no',
    'breastfeeding: NA    Tobacco Use: quit',
    'breastfeeding: N/A    Tobacco Use: quit',
])
def test_not_bfno_regex_match(text):
    assert not BF_NO_EXACT.matches(text)


@pytest.mark.parametrize('text', [
    'discussed: nutrition: both breast and ebm',
    'teaching/guidance:\nwhat?\nnutrition: both breast and ebm',
])
def test_not_bffeeding_regex_match(text):
    assert not BF_FEEDING.matches(text)


@pytest.mark.parametrize('text', [
    'nutrition: formula - similac, sometimes gets pedialite',
])
def test_matches_nutrition_not_bf(text):
    assert matches_nutrition_not_bf(text)


@pytest.mark.parametrize('text', [
    'nutrition: weaning from bottle',
    'Information provided: nutrition: breastfeeding',
])
def test_not_matches_nutrition_not_bf(text):
    assert not matches_nutrition_not_bf(text)
