import csv
import datetime
import logging
import os
from collections import defaultdict

from cronkd.conn.db import sqlai

from apex.iud_insertion import confirm_iud_insertion, Document, Result
from apex.iud_perforation import confirm_iud_perforation
from apex.schema import validate_config


def parse_annotation_file(file=None):
    data = defaultdict(lambda: None)
    if file:
        with open(file) as fh:
            for line in fh:
                name, res, *comments = line.strip().split()
                data[name] = int(res)
    return data


def get_algorithms(names=None):
    algos = {
        'iud_insertion': confirm_iud_insertion,
        'iud_perforation': confirm_iud_perforation,
    }
    if not names:
        return algos
    return {x: algos[x] for x in algos if x in names}


class Reporter:

    def __init__(self):
        # conf matrix
        self.tp = 0
        self.fp = 0
        self.fn = 0
        self.tn = 0
        # prevalence
        self.pos = 0
        self.neg = 0
        self.unk = 0

    def update(self, result: Result):
        if result.value == 1:
            self.pos += 1
            if result.correct == 1:
                self.tp += 1
            elif result.correct == -1:
                self.fp += 1
        elif result.value == -1:
            self.neg += 1
            if result.correct == 1:
                self.tn += 1
            elif result.correct == -1:
                self.fn += 1
        else:
            self.unk += 1

    def __repr__(self):
        return f'[{self.tp}-{self.fp}/{self.fn}-{self.tn}]:{self.pos}/{self.neg}'

    def __str__(self):
        return f'[{self.tp}-{self.fp}/{self.fn}-{self.tn}]:{self.pos}/{self.neg}'


class NullFileWrapper:

    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def writeline(self, line):
        pass


class CsvFileWrapper:

    def __init__(self, file, path=None, **kwargs):
        if path:
            self.fp = os.path.join(path, file)
        else:
            self.fp = file
        self.fh = None
        self.writer = None

    def __enter__(self):
        if self.fp:
            self.fh = open(self.fp, 'w', newline='')
            self.writer = csv.writer(self.fh)
            self.writeline(['name', 'algorithm', 'value'])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.fh:
            self.fh.close()

    def writeline(self, line):
        if self.writer:
            self.writer.writerow(line)


class TableWrapper:

    def __init__(self, tablename, driver, server, database, **kwargs):
        self.eng = sqlai.get_engine(driver=driver, server=server, database=database)
        dt = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.tablename = f'{tablename}_{dt}'

    def __enter__(self):
        self.eng.execute(f'create table {self.tablename} (name varchar(100), algorithm varchar(100), value int)')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def writeline(self, line):
        self.eng.execute(f"insert into {self.tablename} (name, algorithm, value) "
                         f"VALUES ('{line[0]}', '{line[1]}', {line[2]})")


def get_file_wrapper(name=None, kind=None, path=None,
                     driver=None, server=None, database=None, **kwargs):
    if not name:
        return NullFileWrapper()
    elif kind == 'csv':
        return CsvFileWrapper(name, path)
    elif kind == 'sql':
        return TableWrapper(name, driver, server, database)
    else:
        raise ValueError('Unrecognized output file type.')


def make_kwargs(*args, **kwargs):
    for val in args:
        if val is None:
            continue
        elif isinstance(val, dict):
            kwargs.update(val)
        else:
            raise ValueError(f'Unrecognized kwargs: {val}')
    return kwargs


def get_next_from_corpus(directory=None, version=None, start=0, end=None):
    """

    :param directory:
    :param version:
    :param start:
    :param end:
    :return: iterator yielding documnets
    """
    corpus_dir = os.path.join(directory, version)
    for file in os.listdir(corpus_dir)[start:end]:
        doc_name = file.split('.')[0]
        fp = os.path.join(corpus_dir, file)
        yield Document(doc_name, file=fp)


def process(corpus=None, annotation=None, output=None, select=None, algorithm=None):
    truth = parse_annotation_file(**make_kwargs(annotation))
    algos = get_algorithms(**make_kwargs(algorithm))
    results = {name: Reporter() for name in algos}
    with get_file_wrapper(**output) as out:
        for i, doc in enumerate(get_next_from_corpus(**corpus, **select)):
            for name, alg_func in algos.items():
                res = alg_func(doc, truth[doc.name])
                logging.debug(f'{i}:{doc.name}[{res}==Expected({truth[doc.name]})]::{doc.matches}')
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
