import csv
import datetime
import os

from cronkd.conn.db import sqlai


DATETIME_STR = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')


class NullFileWrapper:

    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def writeline(self, line):
        pass


class FileWrapper:

    def __init__(self, file, path=None, header=None, **kwargs):
        if path:
            self.fp = os.path.join(path, file)
            os.makedirs(path, exist_ok=True)
        else:
            self.fp = file
        self.fh = None
        self.header = header or []

    def __enter__(self):
        if self.fp:
            self.fh = open(self.fp, 'w')
            self.writeline(self.header)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.fh:
            self.fh.close()

    def writeline(self, line, sep=None):
        if sep:
            self.fh.write(sep.join(str(s) for s in line) + '\n')
        else:
            self.fh.write(str(line) + '\n')


class CsvFileWrapper(FileWrapper):

    def __init__(self, file, path=None, header=None, **kwargs):
        super().__init__(file, path=path, header=header, **kwargs)
        self.writer = None

    def __enter__(self):
        if self.fp:
            self.fh = open(self.fp, 'w', newline='')
            self.writer = csv.writer(self.fh)
            self.writeline(self.header)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.fh:
            self.fh.close()

    def writeline(self, line, **kwargs):
        if self.writer:
            self.writer.writerow(line)


class TsvFileWrapper(FileWrapper):

    def __init__(self, file, path=None, header=None, **kwargs):
        super().__init__(file, path=path, header=header, **kwargs)

    def writeline(self, line, sep='\t'):
        super().writeline(line, sep=sep)


class TableWrapper:

    def __init__(self, tablename, driver, server, database, **kwargs):
        self.eng = sqlai.get_engine(driver=driver, server=server, database=database)
        self.tablename = f'{tablename}_{DATETIME_STR}'

    def __enter__(self):
        self.eng.execute(f'create table {self.tablename} (name varchar(100), algorithm varchar(100), value int)')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.eng.dispose()

    def writeline(self, line):
        self.eng.execute(f"insert into {self.tablename} (name, algorithm, value) "
                         f"VALUES ('{line[0]}', '{line[1]}', {line[2]})")


def get_file_wrapper(name=None, kind=None, path=None,
                     driver=None, server=None, database=None, **kwargs):
    if not name:
        return NullFileWrapper()
    name = name.replace('{datetime}', DATETIME_STR)
    if kind == 'csv':
        return CsvFileWrapper(name, path, header=['name', 'algorithm', 'value'])
    elif kind == 'sql':
        return TableWrapper(name, driver, server, database)
    else:
        raise ValueError('Unrecognized output file type.')


def get_logging(directory='.', ignore=False):
    if ignore:
        return NullFileWrapper()
    else:
        return TsvFileWrapper(path=directory,
                              file=f'text_{DATETIME_STR}.out',
                              header=['name', 'algorithm', 'status', 'result', 'matches', 'text'])
