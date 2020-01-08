import pytest

from apex.algo.iud_brand import PARAGARD, COPPER, LNG, SCHEDULED


@pytest.mark.parametrize(('s', 'rx'), [
    ('risks of paragard', PARAGARD),
    ('lng iud plan b', LNG),
    ('one option is a copper iud', COPPER),
    ('visit is scheduled for today', SCHEDULED),
])
def test_negated(s, rx):
    assert rx.matches(s, ignore_negation=True)
    assert not rx.matches(s)
