import pytest

from apex.algo.iud_removal import REMOVE, PROB_REMOVE, DEF_REMOVE


@pytest.mark.parametrize(('s', 'rx'), [
    ('removed by', REMOVE),
    ('mirena was removed', PROB_REMOVE),
    ('skyla was removed with some difficulty', DEF_REMOVE),
])
def test_positive(s, rx):
    assert rx.matches(s)
