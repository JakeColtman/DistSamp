import numpy as np

from distsamp.model.model import Model
from distsamp.distributions.gaussian import convert_to_expectation_parameters, convert_to_natural_parameters


class ExpectationPropagationModel(Model):

    def __init__(self, combiner_api):
        Model.__init__(self, combiner_api)

    @staticmethod
    def updated_shared_state(worker_states):
        worker_states = {x[0]: x[1] for x in worker_states.items() if x[1] is not None}

        if len(worker_states) == 0 or 0 not in worker_states:
            return

        keys = worker_states[0].keys()
        shared_state = {}

        for key in keys:
            worker_values = [x[key] for x in worker_states.values()]
            natural_params = [convert_to_natural_parameters(x["mean"], x["variance"]) for x in worker_values]

            combined_eta = np.sum([x[0] for x in natural_params])
            combined_llambda = np.sum([x[1] for x in natural_params])

            mean, variance = convert_to_expectation_parameters(combined_eta, combined_llambda)

            shared_state[key] = {"mean": mean, "variance": variance}

        return shared_state
