from typing import Mapping, Union

import numpy as np

from distsamp.distributions.distribution import Distribution


class GammaDistribution(Distribution):

    def __init__(self, alpha: float, beta: float):
        self.family = "gamma"
        self.a, self.b = alpha, beta

    def distance_from(self, other: 'GammaDistribution') -> float:
        return abs(self.to_scipy().mean() - other.to_scipy().mean())

    def __truediv__(self, other: 'GammaDistribution') -> 'GammaDistribution':
        if self.family != other.family:
            raise ValueError("Operations only meaningful between distributions in the same family, found {} and {}".format(self.family, other.family))
        return GammaDistribution(self.a - other.a, self.b - other.b)

    def __mul__(self, other: Union[float, 'GammaDistribution']) -> 'GammaDistribution':
        if type(other) == float:
            return GammaDistribution(self.a * other, self.b * other)

        if self.family != other.family:
            raise ValueError("Operations only meaningful between distributions in the same family, found {} and {}".format(self.family, other.family))
        return GammaDistribution(self.a + other.a, self.b + other.b)

    def __eq__(self, other: 'GammaDistribution') -> bool:
        if self.family != other.family:
            raise ValueError("Operations only meaningful between distributions in the same family, found {} and {}".format(self.family, other.family))
        return self.a == other.a and self.b == other.b

    @staticmethod
    def from_expectation_parameters(alpha: float, llambda: float) -> 'GammaDistribution':
        return GammaDistribution(alpha - 1, 1.0 / llambda)

    @staticmethod
    def from_samples(samples: np.ndarray) -> 'GammaDistribution':
        mean, variance = np.mean(samples), np.var(samples)
        beta = mean / variance
        alpha = (mean * beta) - 1
        return GammaDistribution(alpha - 1, beta)

    @staticmethod
    def from_scipy(scipy_distribution) -> 'GammaDistribution':
        return GammaDistribution.from_expectation_parameters(scipy_distribution.args[0], scipy_distribution.kwds["scale"])

    @property
    def alpha(self) -> float:
        return self.a + 1

    @property
    def llambda(self) -> float:
        return 1.0 / self.b

    def to_scipy(self):
        from scipy.stats import gamma
        return gamma(self.alpha, scale=self.llambda)

    def to_dict(self) -> Mapping[str, Union[float, str]]:
        return {"family": self.family, "alpha": self.a, "beta": self.b}
