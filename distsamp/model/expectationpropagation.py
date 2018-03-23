from distsamp.model.model import Model
import operator

from functools import reduce


class ExpectationPropagationModel(Model):

    def __init__(self, combiner_api):
        Model.__init__(self, combiner_api)

    @staticmethod
    def updated_shared_state(worker_states):
        worker_states = {x[1] for x in worker_states.items() if x[1] is not None}

        if len(worker_states) == 0 or 0 not in worker_states:
            return

        shared_state = reduce(operator.mul, worker_states)
        return shared_state
