import csv
import datetime
import logging
import os
from collections import defaultdict

from cronkd.conn.db import sqlai

from apex.iud_insertion import confirm_iud_insertion, Document, Result


def parse_truth_file(truth_file):
    data = defaultdict(lambda: None)
    if truth_file:
        with open(truth_file) as fh:
            for line in fh:
                name, res, *comments = line.strip().split()
                data[name] = int(res)
    return data


def get_algorithms():
    return {'iud_insert': confirm_iud_insertion}


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

    def __init__(self, fp=None, **kwargs):
        self.fp = fp
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


def get_file_wrapper(ofp, outformat, **kwargs):
    if not ofp:
        return NullFileWrapper()
    elif outformat == 'csv':
        return CsvFileWrapper(ofp, **kwargs)
    elif outformat == 'sql':
        return TableWrapper(ofp, **kwargs)
    else:
        print(ofp, outformat, kwargs)


def process(corpus_dir, truth_file=None, outfile=None, outformat=None, start=0, end=None, **kwargs):
    truth = parse_truth_file(truth_file)
    algorithms = get_algorithms()
    results = {name: Reporter() for name in algorithms}
    with get_file_wrapper(outfile, outformat, **kwargs) as out:
        for i, f in enumerate(os.listdir(corpus_dir)[start:end]):
            doc = Document(f.split('.')[0], file=os.path.join(corpus_dir, f))
            for name, algorithm in algorithms.items():
                res = algorithm(doc, truth[doc.name])
                logging.debug(f'{i}:{doc.name}[{res}==Expected({truth[doc.name]})]::{doc.matches}')
                if res.value >= 0:
                    out.writeline([doc.name, name, res.value])
                results[name].update(res)
    print(results)


def main():
    logging.basicConfig(level=logging.DEBUG)
    process(corpus_dir, truth_file, outfile, outformat, start, end, **kw)


if __name__ == '__main__':
    main()
