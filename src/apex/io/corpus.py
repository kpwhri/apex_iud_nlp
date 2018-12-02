import os

from apex.algo.pattern import Document


def get_next_from_corpus(directory=None, version=None, start=0, end=None):
    """

    :param directory:
    :param version:
    :param start:
    :param end:
    :return: iterator yielding documnets
    """
    corpus_dir = os.path.join(directory, version)
    for i, entry in enumerate(os.scandir(corpus_dir)):
        if i < start:
            continue
        elif end and i >= end:
            break
        doc_name = entry.name.split('.')[0]
        yield Document(doc_name, file=entry.path)
