import numpy as np


def trace_to_constants(shared_parameters, trace):
    return {np.mean(trace[param] for param in shared_parameters)}

