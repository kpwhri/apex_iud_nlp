import csv
import datetime
import os

from cronkd.conn.db import sqlai


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
