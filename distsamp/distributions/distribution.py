import pickle
from typing import Union

import numpy as np


class Distribution:

    def __init__(self, family, eta, llambda):
        self.family = family
        self.eta, self.llambda = eta, llambda

    def __truediv__(self, other: 'Distribution'):
        if self.family != other.family:
            raise ValueError("Operations only meaningful between distributions in the same family, found {} and {}".format(self.family, other.family))
        return Distribution(self.family, self.eta - other.eta, self.llambda - other.llambda)

    def __mul__(self, other: 'Distribution'):
        if self.family != other.family:
            raise ValueError("Operations only meaningful between distributions in the same family, found {} and {}".format(self.family, other.family))
        return Distribution(self.family, self.eta + other.eta, self.llambda + other.llambda)

    def __eq__(self, other: 'Distribution'):
        if self.family != other.family:
            raise ValueError("Operations only meaningful between distributions in the same family, found {} and {}".format(self.family, other.family))
        return np.all(self.eta == other.eta) and np.all(self.llambda == other.llambda)

    def serialize(self):
        return pickle.dumps(self)

    def to_dict(self):
        return {"family": self.family, "eta": self.eta, "llambda": self.llambda}


class GammaDistribution(Distribution):

    def __init__(self, eta, llambda):
        self.family = "gamma"
        self.eta, self.llambda = eta, llambda

    def serialize(self):
        return pickle.dumps(self)

    def to_dict(self):
        return {"family": self.family, "eta": self.eta, "llambda": self.llambda}


class GaussianDistribution(Distribution):

    def __init__(self, eta, llambda):
        self.family = "gaussian"
        self.eta, self.llambda = eta, llambda
        self.mu, self.var = None, None

    def serialize(self):
        return pickle.dumps(self)

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


class MultivariateGaussianDistribution(Distribution):

    def __init__(self, eta, llambda):
        self.family = "multivariate_gaussian"
        self.eta, self.llambda = eta, llambda
        self.mu, self.cov = None, None

    def serialize(self):
        return pickle.dumps(self)

    def to_dict(self):
        return {"family": self.family, "eta": self.eta, "llambda": self.llambda}

    @property
    def mean(self):
        if self.mu is None:
            self.set_expectation_parameters()
        return self.mu

    @property
    def covariance(self):
        if self.cov is None:
            self.set_expectation_parameters()
        return self.cov

    def set_expectation_parameters(self):
        self.cov = np.linalg.inv(self.llambda)
        self.mu = np.dot(self.cov, self.eta)

    @staticmethod
    def from_expectation_parameters(mean: np.ndarray, covariance: np.ndarray) -> 'MultivariateGaussianDistribution':
        llambda = np.linalg.inv(covariance)
        eta = np.dot(llambda, mean)
        return MultivariateGaussianDistribution(eta, llambda)

    def __truediv__(self, other: 'MultivariateGaussianDistribution'):
        if self.family != other.family:
            raise ValueError("Operations only meaningful between distributions in the same family, found {} and {}".format(self.family, other.family))
        return MultivariateGaussianDistribution(self.eta - other.eta, self.llambda - other.llambda)

    def __mul__(self, other: 'MultivariateGaussianDistribution'):
        if self.family != other.family:
            raise ValueError("Operations only meaningful between distributions in the same family, found {} and {}".format(self.family, other.family))
        return MultivariateGaussianDistribution(self.eta + other.eta, self.llambda + other.llambda)


def deserialize_distribution(serialization: bytes) -> Distribution:
    return pickle.loads(serialization)


def gaussian_distribution_from_samples(samples: np.ndarray) -> GaussianDistribution:
    mean = np.mean(samples)
    variance = np.var(samples)
    return GaussianDistribution.from_expectation_parameters(mean, variance)


def multivariate_gaussian_distribution_from_samples(samples: np.ndarray) -> MultivariateGaussianDistribution:
    mean = np.mean(samples, axis=0)
    covariance = np.cov(samples, rowvar=False).reshape((mean.shape[0], mean.shape[0]))
    return MultivariateGaussianDistribution.from_expectation_parameters(mean, covariance)


def gamma_natural_parameters_from_samples(samples):
    mean, variance = np.mean(samples), np.var(samples)
    beta = mean / variance
    alpha = mean * beta
    return alpha - 1, beta


def gamma_distribution_from_samples(samples: np.ndarray) -> Distribution:
    eta, llambda = gamma_natural_parameters_from_samples(samples)
    return Distribution("gamma", eta, llambda)
