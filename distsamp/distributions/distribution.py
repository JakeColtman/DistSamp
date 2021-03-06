import pickle
from typing import Union


class Distribution:
    """
    A base class for distributions.
    Should be subclassed into concrete exponential families
    e.g. Gaussian, Gamma
    """

    def __truediv__(self, other: 'Distribution') -> 'Distribution':
        raise NotImplementedError("")

    def __mul__(self, other: Union[float, 'Distribution']) -> 'Distribution':
        raise NotImplementedError("")

    def __eq__(self, other: 'Distribution') -> 'Distribution':
        raise NotImplementedError("")

    def serialize(self) -> bytes:
        return pickle.dumps(self)

    def to_dict(self):
        raise NotImplementedError("")

    def to_scipy(self):
        raise NotImplementedError("")


def deserialize_distribution(serialization: bytes) -> Distribution:
    return pickle.loads(serialization)
