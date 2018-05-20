from typing import Union

import numpy as np

from distsamp.distributions.distribution import Distribution


class GaussianDistribution(Distribution):

    def __init__(self, eta: float, llambda: float):
        self.family = "gaussian"
        self.eta, self.llambda = eta, llambda
        self.mu, self.var = None, None

    def to_dict(self):
        return {"family": self.family, "eta": self.eta, "llambda": self.llambda}

    def distance_from(self, other: 'GaussianDistribution') -> float:
        return abs(self.mean - other.mean)

    @property
    def mean(self) -> float:
        if self.mu is None:
            self.set_expectation_parameters()
        return self.mu

    @property
    def variance(self) -> float:
        if self.var is None:
            self.set_expectation_parameters()
        return self.var

    def set_expectation_parameters(self) -> None:
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

    @staticmethod
    def from_scipy(scipy_distribution) -> 'GaussianDistribution':
        mean, sigma = scipy_distribution.args
        return GaussianDistribution.from_expectation_parameters(mean, np.power(sigma, 2))

    def __eq__(self, other: 'GaussianDistribution') -> bool:
        if self.family != other.family:
            raise ValueError("Operations only meaningful between distributions in the same family, found {} and {}".format(self.family, other.family))
        return self.eta == other.eta and self.llambda == other.llambda

    def __truediv__(self, other: 'GaussianDistribution') -> 'GaussianDistribution':
        if self.family != other.family:
            raise ValueError("Operations only meaningful between distributions in the same family, found {} and {}".format(self.family, other.family))
        return GaussianDistribution(self.eta - other.eta, self.llambda - other.llambda)

    def __mul__(self, other: Union[float, 'GaussianDistribution']) -> 'GaussianDistribution':
        if type(other) == float:
            return GaussianDistribution(self.eta * other, self.llambda * other)

        if self.family != other.family:
            raise ValueError("Operations only meaningful between distributions in the same family, found {} and {}".format(self.family, other.family))
        return GaussianDistribution(self.eta + other.eta, self.llambda + other.llambda)

    def to_scipy(self):
        from scipy.stats import norm
        return norm(self.mean, np.power(self.variance, 0.5))
