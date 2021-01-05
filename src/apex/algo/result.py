import enum
from functools import total_ordering


class Status(enum.Enum):
    pass


class Source(enum.Enum):
    pass


class DefaultStatus(Status):
    SKIP = 99


class Confidence(enum.Enum):
    NONE = 0
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5
    ABSOLUTE = 6


@total_ordering
class Result:
    """
    Result of processing.
    Equality/comparisons are based on confidence.
    """

    __slots__ = ['_value', 'result', 'expected', '_text', 'correct',
                 '_extras', 'date', 'confidence']

    def __init__(self, value: Status, result=None, expected=None,
                 text=None, date=None, extras=None, confidence: Confidence = Confidence.MEDIUM):
        self._value = value
        self.result = result or value.value
        self.expected = expected
        self._text = text
        self.correct = None
        self.date = date
        self.confidence = confidence.value
        if not extras:
            self._extras = list()
        elif isinstance(extras, list):
            self._extras = extras
        else:
            self._extras = [extras]
        if self.expected:
            self.correct = self.result == self.expected

    @property
    def value(self):
        return self._value.name

    @property
    def extras(self):
        return ','.join(x.name if isinstance(x, enum.Enum) else str(x) for x in self._extras)

    @property
    def text(self):
        if self._text:
            return ' '.join(self._text.split())

    def is_skip(self):
        return self._value.value == 99

    def __repr__(self):
        return f'<Result:{self.correct}:{self.result}==exp({self.expected})>'

    def __str__(self):
        return repr(self)

    def __bool__(self):
        return self.result >= 0 and not self.is_skip()

    def __gt__(self, other):
        return self.confidence > other.confidence

    def __eq__(self, other):
        return self.confidence == other.confidence
