from apex.algo.iud_insertion import Result


class Reporter:

    def __init__(self):
        # conf matrix
        self.tp = 0
        self.fp = 0
        self.fn = 0
        self.tn = 0
        # errors
        self.error = 0  # error, guessed positive
        # prevalence
        self.pos = 0
        self.neg = 0
        self.neutral = 0
        self.unk = 0

    def update(self, result: Result):
        if result.result >= 1:
            self.pos += 1
            if result.expected == result.result:
                self.tp += 1
            elif result.expected == -1:
                self.fp += 1
            elif result.expected is not None:
                self.error += 1
        elif result.result == -1:
            self.neg += 1
            if result.expected == 1:
                self.fn += 1
            elif result.expected == -1:
                self.tn += 1
        elif result.result == 0:
            self.neutral += 1
            if result.expected == 0:
                self.tp += 1
            elif result.expected == -1:
                self.fp += 1
        else:
            self.unk += 1

    def __repr__(self):
        return f'[{self.tp}-{self.fp} ({self.error})/{self.fn}-{self.tn}]:{self.pos}+{self.neutral}/{self.neg}:{self.unk}'

    def __str__(self):
        return f'[{self.tp}-{self.fp} ({self.error})/{self.fn}-{self.tn}]:{self.pos}+{self.neutral}/{self.neg}:{self.unk}'
