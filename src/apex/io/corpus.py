import os

from apex.algo.pattern import Document


def get_next_from_corpus(directory=None, directories=None, version=None, skipper=None, start=0, end=None):
    """

    :param directories: list of directories to look through
    :param skipper:
    :param directory: first to look through (for backwards compatibility)
    :param version: text|lemma|token
    :param start:
    :param end:
    :return: iterator yielding documents
    """
    directories = directories or []
    if directory:
        directories.insert(0, directory)
    i = -1
    for directory in directories:
        corpus_dir = os.path.join(directory, version)
        for entry in os.scandir(corpus_dir):
            doc_name = entry.name.split('.')[0]
            if skipper and doc_name in skipper:
                continue
            i += 1
            if i < start:
                continue
            elif end and i >= end:
                break
            yield Document(doc_name, file=entry.path)


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
