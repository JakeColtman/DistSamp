import pickle
from typing import Union


class Distribution:
    """
    A base class for distributions.
    Should be subclassed into concrete exponential families
    e.g. Gaussian, Gamma
    """

    def __truediv__(self, other: 'Distribution'):
        if self.family != other.family:
            raise ValueError("Operations only meaningful between distributions in the same family, found {} and {}".format(self.family, other.family))
        return Distribution(self.family, self.eta - other.eta, self.llambda - other.llambda)

    def __mul__(self, other: Union[float, 'Distribution']):
        raise NotImplementedError("")

    def __eq__(self, other: 'Distribution'):
        raise NotImplementedError("")

    def serialize(self):
        return pickle.dumps(self)

    def to_dict(self):
        raise NotImplementedError("")


def deserialize_distribution(serialization: bytes) -> Distribution:
    return pickle.loads(serialization)
