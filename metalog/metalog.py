import numpy
import random
import math


def closeness(metalog1, metalog2):
    STEP = 0.0005
    value = 0
    x = STEP
    while x < 1:
        value += STEP * math.pow(metalog1.quantile(x) - metalog2.quantile(x), 2)
        x += STEP
    return math.sqrt(value)


class Metalog:
    def __init__(self, dim):
        self.alpha = None
        self.dim = dim

    def cdf(self, x):
        PRECISION = 0.0000001
        l = PRECISION
        r = 1 - PRECISION
        lv = self.quantile(l)
        rv = self.quantile(r)
        if x < lv:
            return PRECISION
        elif x > rv:
            return 1 - PRECISION
        else:
            m = None
            for i in range(0, int(numpy.log2(1 / PRECISION))):
                m = (r + l) / 2
                mv = self.quantile(m)
                if x < mv:
                    r = m
                    rv = mv
                else:
                    l = m
                    lv = mv
            return m

    @staticmethod
    def quantile_kth_term(y, k):
        if k == 1:
            return 1
        elif k == 2:
            return numpy.log(y / (1 - y))
        elif k == 3:
            return (y - 0.5) * numpy.log(y / (1 - y))
        elif k == 4:
            return y - 0.5
        elif k % 2 == 1:
            return pow(y - 0.5, (k - 1) / 2)
        else:
            return pow(y - 0.5, k / 2 - 1) * numpy.log(y / (1 - y))

    def quantile(self, y):
        value = 0
        for k in range(0, len(self.alpha)):
            value += self.alpha[k] * Metalog.quantile_kth_term(y, k + 1)
        return value

    def sample(self):
        rng = random.random()
        while rng == 0:
            rng = random.random()
        return self.quantile(rng)

    @staticmethod
    def get_quantile_vector(x):
        x = numpy.sort(x, kind="quicksort")
        Y = numpy.zeros(len(x))
        for i in range(0, len(x)):
            Y[i] = (i + 0.5) / (len(x) + 1.0)
        return x, Y

    @staticmethod
    def get_X_lstsqr(Y, dim):
        X = numpy.zeros((len(Y), dim))
        for i in range(0, len(Y)):
            for k in range(0, dim):
                X[i][k] = Metalog.quantile_kth_term(Y[i], k + 1)
        return X

    def fit(self, x):
        x, Y = Metalog.get_quantile_vector(x)
        X = Metalog.get_X_lstsqr(Y, self.dim)
        self.alpha = numpy.linalg.lstsq(X, x, rcond=None)[0]
