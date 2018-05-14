from typing import Union

import numpy as np

from distsamp.distributions.distribution import Distribution


class GaussianDistribution(Distribution):

    def __init__(self, eta, llambda):
        self.family = "gaussian"
        self.eta, self.llambda = eta, llambda
        self.mu, self.var = None, None

    def to_dict(self):
        return {"family": self.family, "eta": self.eta, "llambda": self.llambda}

    @property
    def mean(self):
        if self.mu is None:
            self.set_expectation_parameters()
        return self.mu

    @property
    def variance(self):
        if self.var is None:
            self.set_expectation_parameters()
        return self.var

    def set_expectation_parameters(self):
        self.var = 1.0 / self.llambda
        self.mu = self.var * self.eta

    @staticmethod
    def from_expectation_parameters(mean: float, variance: float) -> 'GaussianDistribution':
        llambda = 1.0 / variance
        eta = mean / variance
        return GaussianDistribution(eta, llambda)

    @staticmethod
    def from_samples(samples: np.ndarray) -> 'GaussianDistribution':
        mean = np.mean(samples)
        variance = np.var(samples)
        return GaussianDistribution.from_expectation_parameters(mean, variance)

    def __eq__(self, other):
        if self.family != other.family:
            raise ValueError("Operations only meaningful between distributions in the same family, found {} and {}".format(self.family, other.family))
        return self.eta == other.eta and self.llambda == other.llambda

    def __truediv__(self, other: 'GaussianDistribution'):
        if self.family != other.family:
            raise ValueError("Operations only meaningful between distributions in the same family, found {} and {}".format(self.family, other.family))
        return GaussianDistribution(self.eta - other.eta, self.llambda - other.llambda)

    def __mul__(self, other: Union[float, 'GaussianDistribution']):
        if type(other) == float:
            return GaussianDistribution(self.eta * other, self.llambda * other)

        if self.family != other.family:
            raise ValueError("Operations only meaningful between distributions in the same family, found {} and {}".format(self.family, other.family))
        return GaussianDistribution(self.eta + other.eta, self.llambda + other.llambda)

    def to_scipy(self):
        from scipy.stats import norm
        return norm(self.mean, self.variance)
