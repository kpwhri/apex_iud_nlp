import itertools
import os

from cronkd.conn.db import sqlai

from apex.algo.pattern import Document


def get_next_from_directory(directory, directories, version):
    if directory or directories:
        directories = directories or []
        if directory:
            directories.insert(0, directory)
        for directory in directories:
            corpus_dir = os.path.join(directory, version)
            for entry in os.scandir(corpus_dir):
                doc_name = entry.name.split('.')[0]
                yield doc_name, entry.path, None


def get_next_from_sql(name, driver, server, database, name_col, text_col):
    if name and driver and server and database:
        eng = sqlai.get_engine(driver=driver, server=server, database=database)
        for doc_name, text in eng.execute(f'select {name_col}, {text_col} from {name}'):
            yield doc_name, None, text


def get_next_from_corpus(directory=None, directories=None, version=None,
                         name=None, driver=None, server=None, database=None,
                         name_col=None, text_col=None,
                         skipper=None, start=0, end=None):
    """

    :param name_col:
    :param text_col:
    :param name: tablename (if connecting to database)
    :param driver: db driver  (if connecting to database)
    :param server: name of server (if connecting to database)
    :param database: name of database (if connecting to database)
    :param directories: list of directories to look through
    :param skipper:
    :param directory: first to look through (for backwards compatibility)
    :param version: text|lemma|token
    :param start:
    :param end:
    :return: iterator yielding documents
    """
    i = -1
    for doc_name, path, text in itertools.chain(
        get_next_from_directory(directory, directories, version),
        get_next_from_sql(name, driver, server, database, name_col, text_col)
    ):
        if skipper and doc_name in skipper:
            continue
        i += 1
        if i < start:
            continue
        elif end and i >= end:
            break
        if not text or not path:  # one of these required
            continue
        yield Document(doc_name, file=path, text=text)


class Skipper:

    def __init__(self, path=None, rebuild=False, ignore=False):
        self.fp = path
        self.fh = None
        self.rebuild = rebuild
        self.ignore = ignore
        self.skips = self._read_skips()

    def _read_skips(self):
        if self.fp and os.path.exists(self.fp) and not self.ignore:
            with open(self.fp) as fh:
                return {x.strip() for x in fh if x.strip()}
        return set()

    def add(self, doc_name):
        if doc_name not in self.skips:
            self.skips.add(doc_name)
            if self.fp:
                self.fh.write(doc_name + '\n')

    def __contains__(self, item):
        return item in self.skips

    def __enter__(self):
        if self.fp:
            self.fh = open(self.fp, 'w' if self.rebuild else 'a')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.fp:
            self.fh.close()
