
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