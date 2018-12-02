import logging
from collections import defaultdict

from apex.algo import ALGORITHMS
from apex.io.corpus import get_next_from_corpus
from apex.io.out import get_file_wrapper
from apex.io.report import Reporter
from apex.schema import validate_config
from apex.util import make_kwargs


def parse_annotation_file(file=None):
    data = defaultdict(lambda: None)
    if file:
        with open(file) as fh:
            for line in fh:
                name, res, *comments = line.strip().split()
                data[name] = int(res)
    return data


def get_algorithms(names=None):
    if not names:
        return ALGORITHMS
    return {x: ALGORITHMS[x] for x in ALGORITHMS if x in names}


def process(corpus=None, annotation=None, output=None, select=None, algorithm=None):
    truth = parse_annotation_file(**make_kwargs(annotation))
    algos = get_algorithms(**make_kwargs(algorithm))
    results = {name: Reporter() for name in algos}
    with get_file_wrapper(**output) as out:
        for i, doc in enumerate(get_next_from_corpus(**corpus, **select)):
            for name, alg_func in algos.items():
                res = alg_func(doc, truth[doc.name])
                # logging.debug(f'{i}:{doc.name}[{res}==Expected({truth[doc.name]})]::{doc.matches}')
                if res.value >= 0:
                    out.writeline([doc.name, name, res.value])
                results[name].update(res)
    print(results)


def main(config_file):
    conf = validate_config(config_file)
    logging.basicConfig(level=logging.DEBUG)
    process(**conf)


if __name__ == '__main__':
    import sys
    try:
        main(sys.argv[1])
    except IndexError:
        raise AttributeError('Missing configuration file: Usage: main.py file.(json|yaml|py)')
