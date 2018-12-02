import logging
from collections import defaultdict

from apex.algo import ALGORITHMS
from apex.io.corpus import get_next_from_corpus, Skipper
from apex.io.out import get_file_wrapper, get_logging
from apex.io.report import Reporter
from apex.schema import validate_config
from apex.util import kw


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


def process(corpus=None, annotation=None, output=None, select=None, algorithm=None,
            loginfo=None, skipinfo=None):
    truth = parse_annotation_file(**kw(annotation))
    algos = get_algorithms(**kw(algorithm))
    results = {name: Reporter() for name in algos}
    with get_file_wrapper(**output) as out, \
            get_logging(**kw(loginfo)) as log, \
            Skipper(**skipinfo) as skipper:
        for i, doc in enumerate(get_next_from_corpus(**corpus, **select, skipper=skipper)):
            for name, alg_func in algos.items():
                res = alg_func(doc, truth[doc.name])
                if res:
                    out.writeline([doc.name, name, res.result])
                    log.writeline([doc.name, name, res.value, res.result, doc.matches, res.text])
                elif res.is_skip():
                    skipper.add(doc.name)
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
