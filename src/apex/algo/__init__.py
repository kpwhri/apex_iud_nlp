from apex.algo.iud_brand import get_iud_brand
from apex.algo.iud_insertion import confirm_iud_insertion
from apex.algo.iud_perforation import confirm_iud_perforation

ALGORITHMS = {
    'iud_insertion': confirm_iud_insertion,
    'iud_perforation': confirm_iud_perforation,
    'iud_brand': get_iud_brand,
}
