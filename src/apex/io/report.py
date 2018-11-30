from apex.algo.iud_insertion import Result


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
