from typing import Union

import numpy as np

from distsamp.distributions.distribution import Distribution


class MultivariateGaussianDistribution(Distribution):

    def __init__(self, eta: np.ndarray, llambda: np.ndarray):
        self.family = "multivariate_gaussian"
        self.eta, self.llambda = eta, llambda
        self.mu, self.cov = None, None

    def distance_from(self, other: 'MultivariateGaussianDistribution') -> float:
        return np.power(np.sum(np.power(self.mean - other.mean, 2)), 0.5)

    def to_dict(self):
        return {"family": self.family, "eta": self.eta, "llambda": self.llambda}

    @property
    def mean(self) -> np.ndarray:
        if self.mu is None:
            self.set_expectation_parameters()
        return self.mu

    @property
    def covariance(self) -> np.ndarray:
        if self.cov is None:
            self.set_expectation_parameters()
        return self.cov

    def set_expectation_parameters(self) -> None:
        self.cov = np.linalg.inv(self.llambda)
        self.mu = np.dot(self.cov, self.eta)

    def to_scipy(self):
        from scipy.stats import multivariate_normal
        return multivariate_normal(self.mean, self.covariance)

    @staticmethod
    def from_expectation_parameters(mean: np.ndarray, covariance: np.ndarray) -> 'MultivariateGaussianDistribution':
        llambda = np.linalg.inv(covariance)
        eta = np.dot(llambda, mean)
        return MultivariateGaussianDistribution(eta, llambda)

    @staticmethod
    def from_samples(samples: np.ndarray) -> 'MultivariateGaussianDistribution':
        mean = np.mean(samples, axis=0)
        covariance = np.cov(samples, rowvar=False).reshape((mean.shape[0], mean.shape[0]))
        return MultivariateGaussianDistribution.from_expectation_parameters(mean, covariance)

    def __eq__(self, other: 'MultivariateGaussianDistribution') -> bool:
        if self.family != other.family:
            raise ValueError("Operations only meaningful between distributions in the same family, found {} and {}".format(self.family, other.family))
        return np.all(self.eta == other.eta) and np.all(self.llambda == other.llambda)

    def __truediv__(self, other: 'MultivariateGaussianDistribution') -> 'MultivariateGaussianDistribution':
        if self.family != other.family:
            raise ValueError("Operations only meaningful between distributions in the same family, found {} and {}".format(self.family, other.family))
        return MultivariateGaussianDistribution(self.eta - other.eta, self.llambda - other.llambda)

    def __mul__(self, other: Union[float, 'MultivariateGaussianDistribution']) -> 'MultivariateGaussianDistribution':
        if type(other) == float:
            return MultivariateGaussianDistribution(self.eta * other, self.llambda * other)

        if self.family != other.family:
            raise ValueError("Operations only meaningful between distributions in the same family, found {} and {}".format(self.family, other.family))
        return MultivariateGaussianDistribution(self.eta + other.eta, self.llambda + other.llambda)
