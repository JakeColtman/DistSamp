import pickle

import numpy as np


class Distribution:

    def __init__(self, family, eta, llambda):
        self.family = family
        self.eta, self.llambda = eta, llambda

    def __truediv__(self, other: 'Distribution'):
        return Distribution(self.family, self.eta - other.eta, self.llambda - other.llambda)

    def __mul__(self, other: 'Distribution'):
        return Distribution(self.family, self.eta + other.eta, self.llambda + other.llambda)

    def __eq__(self, other: 'Distribution'):
        return np.all(self.eta == other.eta) and np.all(self.llambda == other.llambda)

    def serialize(self):
        return pickle.dumps(self)

    def to_dict(self):
        return {"family": self.family, "eta": self.eta, "llambda": self.llambda}


def deserialize_distribution(serialization: bytes) -> Distribution:
    return pickle.loads(serialization)


def gaussian_convert_to_natural_parameters(mean: np.ndarray, variance: np.ndarray):
    llambda = np.linalg.inv(variance)
    eta = np.dot(llambda, mean)
    return eta, llambda


def gaussian_convert_to_expectation_parameters(eta: np.ndarray, llambda: np.ndarray):
    variance = np.linalg.inv(llambda)
    mean = np.dot(variance, eta)
    return mean, variance


def gaussian_distribution_from_samples(samples: np.ndarray) -> Distribution:
    if len(samples.shape) == 1:
        mean = np.mean(samples).reshape(1,)
        covar = np.var(samples).reshape(1, 1)
    else:
        mean = np.mean(samples, axis=0)
        covar = np.cov(samples, rowvar=False).reshape((mean.shape[0], mean.shape[0]))
    eta, llambda = gaussian_convert_to_natural_parameters(mean, covar)
    return Distribution("gaussian", eta, llambda)


def gaussian_distribution_from_expectation_parameters(mean, covar) -> Distribution:
    eta, llambda = gaussian_convert_to_natural_parameters(mean, covar)
    return Distribution("gaussian", eta, llambda)


def gamma_natural_parameters_from_samples(samples):
    mean, variance = np.mean(samples), np.var(samples)
    beta = mean / variance
    alpha = mean * beta
    return alpha - 1, beta


def gamma_distribution_from_samples(samples: np.ndarray) -> Distribution:
    eta, llambda = gamma_natural_parameters_from_samples(samples)
    return Distribution("gamma", eta, llambda)
