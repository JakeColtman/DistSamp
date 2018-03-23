

def convert_to_natural_parameters(mean, variance):
    l = 1.0 / variance
    e = l * mean
    return e, l


def convert_to_expectation_parameters(eta, llambda):
    variance = 1.0 / llambda
    mean = eta / llambda
    return mean, variance


def cavity_distribution(full_distribution, site_distribution):
    full_eta, full_lambda = convert_to_natural_parameters(**full_distribution)
    site_eta, site_ll = convert_to_natural_parameters(**site_distribution)

    mu, var = convert_to_expectation_parameters(full_eta - site_eta, full_lambda - site_ll)
    return {"mean": mu, "variance": var}


class Distribution:

    def __init__(self, mean=None, variance=None, eta=None, llambda=None):
        if eta is not None and mean is not None:
            self.mean, self.variance, self.eta, self.ll = mean, variance, eta, llambda
        if eta is None:
            self.mean, self.variance = mean, variance
            self.eta, self.llambda = convert_to_natural_parameters(mean, variance)
        if mean is None:
            self.eta, self.llambda = eta, llambda
            self.mean, self.variance = convert_to_expectation_parameters(eta, llambda)
        else:
            raise ValueError("Distribution requires either expectation or natural parameters")

    def __div__(self, other):
        return Distribution(eta=self.eta - other.eta, llambda=self.llambda - other.llambda)

    def __mul__(self, other):
        return Distribution(eta=self.eta + other.eta, llambda=self.llambda + other.llambda)
