from apex.algo.pattern import Document


def test_clean_breastfeeding_document():
    text = 'Breastfeeding?\nYes'
    exp_text = 'Breastfeeding: Yes'
    doc = Document(None, text=text)
    assert doc.new_text == exp_text


def test_teaching_boilerplate_document():
    text = 'Teaching/Guidance provided:\nNutrition:  \nwhole milk'
    exp_text = 'Teaching/Guidance provided: Nutrition: whole milk'
    doc = Document(None, text=text)
    assert doc.new_text == exp_text
