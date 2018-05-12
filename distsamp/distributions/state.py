import pickle
from typing import Mapping

from distsamp.distributions.distribution import Distribution, distribution_from_samples


class State:

    def __init__(self, distributions: Mapping[str, Distribution]):
        self.distributions = distributions
        self.variables = set(self.distributions.keys())

    def __truediv__(self, other: 'State'):
        if self.variables != other.variables:
            raise ValueError("State operations only valid with matching variables, found: {}, expected: {}".format(other.variables, self.variables))

        new_distributions = {}
        for variable in self.variables:
            new_distributions[variable] = self.distributions[variable] / other.distributions[variable]

        return State(new_distributions)

    def __mul__(self, other: 'State'):
        if self.variables != other.variables:
            raise ValueError("State operations only valid with matching variables, found: {}, expected: {}".format(other.variables, self.variables))

        new_distributions = {}
        for variable in self.variables:
            new_distributions[variable] = self.distributions[variable] * other.distributions[variable]

        return State(new_distributions)

    def __getitem__(self, item):
        return self.distributions[item]

    def __str__(self):
        message_dict = {key: self.distributions[key].to_dict() for key in self.variables}
        return str(message_dict)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other: 'State'):
        if self.variables != other.variables:
            return False

        for var in self.variables:
            if self.distributions[var] != other.distributions[var]:
                return False
        else:
            return True

    def serialize(self):
        return pickle.dumps(self)


def deserialize_state(message: bytes):

    if message is None:
        return None

    return pickle.loads(message)


def state_from_samples(samples, shared_variables: None) -> State:
    distributions_dict = {}

    all_distrs = set(samples.keys())
    if shared_variables is not None:
        shared_distrs = [x for x in all_distrs if x in shared_variables]
    else:
        shared_distrs = all_distrs

    for distr in shared_distrs:
        if distr == "lp__":
            continue
        distributions_dict[distr] = distribution_from_samples(samples[distr])
    return State(distributions_dict)
