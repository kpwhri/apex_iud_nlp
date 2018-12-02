import enum


class Result:  # = namedtuple('Result', 'value correct')

    __slots__ = ['_value', 'result', 'expected', '_text', 'correct']

    def __init__(self, value: enum.Enum, result, expected=None, text=None):
        self._value = value
        self.result = result
        self.expected = expected
        self._text = text
        self.correct = None
        if self.expected:
            self.correct = self.result == self.expected

    @property
    def value(self):
        return self._value.name

    @property
    def text(self):
        return ' '.join(self._text.split())

    def __repr__(self):
        return f'<Result:{self.correct}:{self.result}==exp({self.expected})>'

    def __str__(self):
        return repr(self)

    def __bool__(self):
        return self.result >= 0
