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


def deserialize_distribution(serialization: bytes) -> Distribution:
    return pickle.loads(serialization)
