import pickle
from typing import Mapping

import numpy as np


def convert_to_natural_parameters(mean: np.ndarray, variance: np.ndarray):
    llambda = np.linalg.inv(variance)
    eta = np.dot(llambda, mean)
    return eta, llambda


def convert_to_expectation_parameters(eta: np.ndarray, llambda: np.ndarray):
    variance = np.linalg.inv(llambda)
    mean = np.dot(variance, eta)
    return mean, variance


class Distribution(object):

    def __init__(self, mean=None, variance=None, eta=None, llambda=None):
        if eta is not None and mean is not None:
            self.mean, self.variance, self.eta, self.llambda = mean, variance, eta, llambda
        elif eta is None:
            self.mean, self.variance = mean, variance
            self.eta, self.llambda = convert_to_natural_parameters(mean, variance)
        elif mean is None:
            self.eta, self.llambda = eta, llambda
            self.mean, self.variance = convert_to_expectation_parameters(eta, llambda)
        else:
            print(mean, variance, eta, llambda)
            raise ValueError("Distribution requires either expectation or natural parameters")

    def __truediv__(self, other):
        return Distribution(eta=self.eta - other.eta, llambda=self.llambda - other.llambda)

    def __mul__(self, other):
        return Distribution(eta=self.eta + other.eta, llambda=self.llambda + other.llambda)

    def to_dict(self) -> Mapping[str, Mapping[str, float]]:
        return vars(self)

    def __eq__(self, other: 'Distribution'):
        return np.all(self.mean == other.mean) and np.all(self.variance == other.variance)

    def serialize(self):
        return pickle.dumps(self)


def deserialize_distribution(serialization: bytes) -> Distribution:
    return pickle.loads(serialization)


def distribution_from_samples(samples: np.ndarray) -> Distribution:
    mean = np.mean(samples, axis=0)
    covar = np.cov(samples, rowvar=False)
    return Distribution(mean, covar)
