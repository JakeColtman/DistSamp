import pickle

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

    def serialize(self):
        return pickle.dumps(self)

    def to_dict(self):
        return {"family": self.family, "eta": self.eta, "llambda": self.llambda}

    def expectation_parameters(self):
        variance = np.linalg.inv(self.llambda)
        mean = np.dot(variance, self.eta)
        return {"mean": mean, "variance": variance}

    @staticmethod
    def from_expectation_parameters(mean: float, variance: float) -> 'GaussianDistribution':
        llambda = np.linalg.inv(variance)
        eta = np.dot(llambda, mean)
        return GaussianDistribution(eta, llambda)


class MultivariateGaussianDistribution(Distribution):

    def __init__(self, eta, llambda):
        self.family = "multivariate_gaussian"
        self.eta, self.llambda = eta, llambda

    def serialize(self):
        return pickle.dumps(self)

    def to_dict(self):
        return {"family": self.family, "eta": self.eta, "llambda": self.llambda}

    def expectation_parameters(self):
        variance = np.linalg.inv(self.llambda)
        mean = np.dot(variance, self.eta)
        return {"mean": mean, "variance": variance}

    @staticmethod
    def from_expectation_parameters(mean: np.ndarray, covariance: np.ndarray) -> 'MultivariateGaussianDistribution':
        llambda = np.linalg.inv(covariance)
        eta = np.dot(llambda, mean)
        return MultivariateGaussianDistribution(eta, llambda)


def deserialize_distribution(serialization: bytes) -> Distribution:
    return pickle.loads(serialization)


def gaussian_distribution_from_samples(samples: np.ndarray) -> GaussianDistribution:
    mean = np.mean(samples).reshape(1,)
    variance = np.var(samples).reshape(1, 1)
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
