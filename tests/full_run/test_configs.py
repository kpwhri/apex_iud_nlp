import os

from apex.main import main

PATH = os.path.dirname(os.path.abspath(__file__))

OUTPUT_FILE = '''name,algorithm,value,category,date,extras
1,iud_expulsion,2,MALPOSITION,None,
1,iud_expulsion,12,LOWER_UTERINE_SEGMENT,None,
1,iud_expulsion,5,PARTIAL,None,
1,iud_expulsion_rad,5,PARTIAL,None,
1,iud_expulsion_rad,2,MALPOSITION,None,
1,iud_expulsion_rad,12,LOWER_UTERINE_SEGMENT,None,
2,iud_difficult_insertion,1,PROVIDER_STATEMENT,None,'''


def test_config_files():
    os.chdir(PATH)
    filename = 'config_files.py'
    main(os.path.join(PATH, filename))
    outpath = os.path.join(PATH, 'test_file_output')
    with open(outpath) as fh:
        assert OUTPUT_FILE == fh.read().strip()


def test_config_sqlite():
    os.chdir(PATH)
    filename = 'config_sqlite.py'
    main(os.path.join(PATH, filename))
    outpath = os.path.join(PATH, 'test_sqlite_output')
    with open(outpath) as fh:
        assert OUTPUT_FILE == fh.read().strip()
