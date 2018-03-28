from typing import Mapping

def convert_to_natural_parameters(mean: float, variance: float):
    l = 1.0 / variance
    e = l * mean
    return e, l


def convert_to_expectation_parameters(eta: float, llambda: float):
    variance = 1.0 / llambda
    mean = eta / llambda
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

    def __div__(self, other):
        return Distribution(eta=self.eta - other.eta, llambda=self.llambda - other.llambda)

    def __mul__(self, other):
        return Distribution(eta=self.eta + other.eta, llambda=self.llambda + other.llambda)

    def to_dict(self) -> Mapping[str, Mapping[str, float]]:
        return vars(self)
