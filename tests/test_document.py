from apex.algo.pattern import Document


def test_clean_breastfeeding_document():
    text = 'Breastfeeding?\nYes'
    exp_text = 'Breastfeeding: Yes'
    doc = Document(None, text=text)
    assert doc.new_text == exp_text
