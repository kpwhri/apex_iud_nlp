import logging
from collections import defaultdict

from apex.algo import ALGORITHMS
from apex.io.corpus import get_next_from_corpus, Skipper
from apex.io.out import get_file_wrapper, get_logging
from apex.io.report import Reporter
from apex.schema import validate_config
from apex.util import kw


def parse_annotation_file(file=None, data=None):
    if not data:
        data = defaultdict(lambda: None)
    if file:
        with open(file) as fh:
            for line in fh:
                name, res, *comments = line.strip().split()
                data[name] = int(res)
    return data


def parse_annotation_files(*configs, data=None):
    for config in configs:
        data = parse_annotation_file(data=data, **kw(config))
    return data


def get_algorithms(names=None):
    if not names:
        return ALGORITHMS
    return {x: ALGORITHMS[x] for x in ALGORITHMS if x in names}


def process(corpus=None, annotation=None, annotations=None, output=None, select=None,
            algorithm=None, loginfo=None, skipinfo=None, logger=None):
    if logger and not logger['verbose']:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    truth = parse_annotation_file(**kw(annotation))
    truth = parse_annotation_files(*annotations or list(), data=truth)
    algos = get_algorithms(**kw(algorithm))
    if not algos:
        raise ValueError('No algorithms specified!')
    results = {name: Reporter() for name in algos}
    with get_file_wrapper(**output) as out, \
            get_logging(**kw(loginfo)) as log, \
            Skipper(**kw(skipinfo)) as skipper:
        for i, doc in enumerate(get_next_from_corpus(**kw(corpus), **kw(select), skipper=skipper)):
            for name, alg_func in algos.items():
                max_res = None
                for res in alg_func(doc, truth[doc.name]):
                    if res:
                        logging.debug(f'{i}: {doc.name}: {res}')
                        out.writeline([doc.name, name, res.result, res.value, res.date, res.extras])
                    elif res.is_skip():  # always skip
                        skipper.add(doc.name)
                        break
                    log.writeline([doc.name, name, res.value, res.result, doc.matches, res.text])
                    # only take max
                    if not max_res or (res.result > max_res.result and res.confidence >= max_res.confidence ):
                        max_res = res
                else:  # avoid if skipped
                    if max_res is not None:
                        results[name].update(max_res)
                        if max_res.expected is not None:
                            logging.info(f'Validation for {doc.name}: {results}')
    logging.warning(f'Final results: {results}')


def main(config_file):
    conf = validate_config(config_file)
    process(**conf)


if __name__ == '__main__':
    import sys
    try:
        main(sys.argv[1])
    except IndexError:
        raise AttributeError('Missing configuration file: Usage: main.py file.(json|yaml|py)')
