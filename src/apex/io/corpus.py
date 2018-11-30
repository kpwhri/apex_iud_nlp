import os

from apex.algo.iud_insertion import Document


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
