from apex.algo.breastfeeding import confirm_breastfeeding
from apex.algo.iud_brand import get_iud_brand
from apex.algo.iud_difficult_insertion import confirm_difficult_insertion
from apex.algo.iud_expulsion import confirm_iud_expulsion
from apex.algo.iud_insertion import confirm_iud_insertion
from apex.algo.iud_perforation import confirm_iud_perforation
from apex.algo.iud_removal import confirm_iud_removal
from apex.algo.parity import get_parity

ALGORITHMS = {
    'iud_insertion': confirm_iud_insertion,
    'iud_perforation': confirm_iud_perforation,
    'iud_brand': get_iud_brand,
    'iud_difficult_insertion': confirm_difficult_insertion,
    'iud_removal': confirm_iud_removal,
    'iud_expulsion': confirm_iud_expulsion,
    'parity': get_parity,
    'breastfeeding': confirm_breastfeeding,
}
