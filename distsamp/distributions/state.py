import json
from typing import Mapping
from distsamp.distributions.distribution import Distribution


class State:

    def __init__(self, distributions: Mapping[str, Distribution]):
        self.distributions = distributions
        self.variables = set(self.distributions.keys())

    def __div__(self, other: 'State'):
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
        return json.dumps(message_dict)

    def __repr__(self):
        return self.__str__()


def parse_state_dictionary(message: Mapping[str, Mapping[str, float]]):
    return State({key: Distribution(**message[key]) for key in message})


def parse_state(message_str: str):

    if message_str is None:
        return None

    try:
        message = json.loads(message_str)
    except:
        print("Failed on, ", message_str)
        return None
    return parse_state_dictionary(message)
