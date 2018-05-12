from collections import OrderedDict
from typing import Callable, Iterable

from distsamp.distributions.distribution import Distribution
from distsamp.distributions.state import State
from distsamp.api.redis import WorkerAPI


class Worker:
    """
    Encapsulates the actual crunch of the system.
    Reads a cavity from the server and generates an approximation to the tilted distribution

    Isn't concerned with mechanisms necessary for the overall health of the approximation

    Attributes
    ---------
    api: distsamp.worker.api.spark.WorkerAPI
                API to allow the worker to interact with the rest of the system
    f_run: (data, cavity) -> distribution
           Method to produce an approximation to the tilted distribution.
           Returns the _site_ approximation, not the whole likihood
    """
    def __init__(self, api: WorkerAPI, f_run: Callable[[Iterable, State], State], damping: float):
        self.api = api
        self.f_run = f_run
        self.damping = damping

    @staticmethod
    def updated_distribution(worker_distribution: Distribution, site_distribution: Distribution, damping: float):
        updated_eta = damping * site_distribution.eta + (1 - damping) * worker_distribution.eta
        updated_llambda = damping * site_distribution.llambda + (1 - damping) * worker_distribution.llambda
        return Distribution(family="gaussian", eta=updated_eta, llambda=updated_llambda)

    @staticmethod
    def updated_state(worker_state: State, site_state: State, damping: float):
        variables = worker_state.variables
        return State({v: Worker.updated_distribution(worker_state[v], site_state[v], damping) for v in variables})

    def run(self, data):
        for _ in range(5):
            cavity = self.api.get_site_cavity()
            site_state = self.api.get_site_state()
            tilted_approx = self.f_run(data, cavity)
            worker_state = tilted_approx / cavity
            updated_state = self.updated_state(worker_state, site_state, self.damping)
            self.api.set_site_state(updated_state)
            yield updated_state
