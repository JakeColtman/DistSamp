from distsamp.model.model import Model
import operator

from functools import reduce


class ExpectationPropagationModel(Model):

    def __init__(self, combiner_api):
        Model.__init__(self, combiner_api)

    @staticmethod
    def updated_shared_state(worker_states):
        worker_ids = set(worker_states.keys())
        worker_states = {x for x in worker_states.values() if x is not None}

        if len(worker_states) == 0 or 0 not in worker_ids:
            return

        shared_state = reduce(operator.mul, worker_states)
        return shared_state
