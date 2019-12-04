import sys

from apex.main import main

if __name__ == '__main__':
    try:
        main(sys.argv[1])
    except IndexError:
        print('Usage: python -m apex config.py')
