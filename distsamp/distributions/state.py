import json

from distsamp.distributions.distribution import Distribution


class State:

    def __init__(self, distributions):
        self.distributions = distributions
        self.variables = set(self.keys())

    def __div__(self, other):
        if self.variables != self.other.variables:
            raise ValueError("State operations only valid with matching variables, found: {}, expected: {}".format(self.other.variables, self.variables))

        new_distributions = {}
        for variable in self.variables:
            new_distributions[variable] = self.distributions[variable] / other.distributions[variable]

        return State(new_distributions)

    def __getitem__(self, item):
        return self.distributions[item]

    def __str__(self):
        message_dict = {key: {"mean": self[key].mean, "variance": self[key].variance} for key in self.variables}
        return json.dump(message_dict)


def parse_state(message_str):

    if message_str is None:
        return None

    message = json.loads(message_str)
    return {key: Distribution(**message[key]) for key in message}
