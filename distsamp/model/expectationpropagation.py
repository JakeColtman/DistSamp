from distsamp.model.model import Model
import operator

from functools import reduce


class ExpectationPropagationModel(Model):

    def __init__(self, combiner_api):
        Model.__init__(self, combiner_api)

    def updated_shared_state(self, worker_states):
        worker_ids = set(worker_states.keys())

        if len(worker_states) == 0 or 0 not in worker_ids:
            return

        worker_states = {x for x in worker_states.values() if x is not None}

        return reduce(operator.mul, worker_states)
