from typing import Union

import numpy as np

from distsamp.distributions.distribution import Distribution


class GammaDistribution(Distribution):

    def __init__(self, alpha, beta):
        self.family = "gamma"
        self.a, self.b = alpha, beta

    def to_dict(self):
        return {"family": self.family, "alpha": self.a, "beta": self.b}

    def __truediv__(self, other: 'GammaDistribution'):
        if self.family != other.family:
            raise ValueError("Operations only meaningful between distributions in the same family, found {} and {}".format(self.family, other.family))
        return GammaDistribution(self.a - other.a, self.b - other.b)

    def __mul__(self, other: Union[float, 'GammaDistribution']):
        if type(other) == float:
            return GammaDistribution(self.a * other, self.b * other)

        if self.family != other.family:
            raise ValueError("Operations only meaningful between distributions in the same family, found {} and {}".format(self.family, other.family))
        return GammaDistribution(self.a + other.a, self.b + other.b)

    def __eq__(self, other: 'GammaDistribution'):
        if self.family != other.family:
            raise ValueError("Operations only meaningful between distributions in the same family, found {} and {}".format(self.family, other.family))
        return np.all(self.a == other.a) and np.all(self.b == other.b)

    @staticmethod
    def from_expectation_parameters(alpha, llambda):
        return GammaDistribution(alpha - 1, 1.0 / llambda)

    @staticmethod
    def from_samples(samples):
        mean, variance = np.mean(samples), np.var(samples)
        beta = mean / variance
        alpha = (mean * beta) - 1
        return GammaDistribution(alpha - 1, beta)


    @property
    def alpha(self):
        return self.a + 1

    @property
    def llambda(self):
        return 1.0 / self.b

    def to_scipy(self):
        from scipy.stats import gamma
        return gamma(self.alpha, scale=self.llambda)
