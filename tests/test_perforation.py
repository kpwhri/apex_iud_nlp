import pytest

from apex.algo.iud_perforation import COMPLETE, PERFORATION, PARTIAL, EMBEDDED, MIGRATED, LAPAROSCOPIC_REMOVAL


@pytest.mark.parametrize(('s', 'rx'), [
    ('completely perforated', COMPLETE),
    ('pierced the uterine perimetrium', COMPLETE),
    ('mirena visible in vagina', COMPLETE),
    ('perforation', PERFORATION),
    ('into the uterine wall', PERFORATION),
    ('partially perforated', PARTIAL),
    ('arm broke', PARTIAL),
    ('paraguard visible in cervix', PARTIAL),
    ('impacted iud', EMBEDDED),
    ('iud was displaced', MIGRATED),
    ('laporascopically removed', LAPAROSCOPIC_REMOVAL),
    ('retrieved with laparoscope', LAPAROSCOPIC_REMOVAL),
])
def test_positive(s, rx):
    assert rx.matches(s)
