from apex.algo.parity import determine_parity, ParityStatus, ParitySource
from apex.algo.pattern import Document


def test_gNpNNNN():
    doc = Document(None, text='G 1 P 1001')
    status, capt, source = determine_parity(doc)
    assert status == ParityStatus.P1
    assert source == ParitySource.PARITY


def test_g_eq_p_plus_1():
    doc = Document(None, text='G 1 P 2')
    status, capt, source = determine_parity(doc)
    assert status == ParityStatus.P1
    assert source == ParitySource.GRAVIDA


def test_g_lt_p():
    doc = Document(None, text='G 3 P 7')
    status, capt, source = determine_parity(doc)
    assert status == ParityStatus.SKIP
    assert source == ParitySource.NONE
