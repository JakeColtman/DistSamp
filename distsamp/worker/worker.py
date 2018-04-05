from collections import OrderedDict
from typing import Callable, Iterable

from distsamp.distributions.state import State, state_from_samples
from distsamp.worker.api.spark import WorkerAPI


class Worker:
    """
    Encapsulates a site in the overall likihood function
    Handles the process of coordinating with the server and approximating the tilted distribution

    Attributes
    ---------
    api: distsamp.worker.api.spark.WorkerAPI
                API to allow the worker to interact with the rest of the system
    f_run: (data, cavity) -> distribution
           Method to produce an approximation to the tilted distribution.
           Returns the _site_ approximation, not the whole likihood
    """
    def __init__(self, api: WorkerAPI, f_run: Callable[[Iterable, State], State]):
        self.api = api
        self.f_run = f_run
        self.shared_variables = self.api.get_site_cavity().variables

    def run(self, data):

        for _ in range(5):
            cavity = self.api.get_site_cavity()
            tilted_approx = self.f_run(data, cavity)
            own_updated_state = tilted_approx / cavity
            self.api.set_worker_state(own_updated_state)
            yield own_updated_state


class StanWorker:
    """
    Encapsulates a site in the overall likihood function
    Handles the process of coordinating with the server and approximating the tilted distribution

    Attributes
    ---------
    api: distsamp.worker.api.spark.WorkerAPI
                API to allow the worker to interact with the rest of the system
    f_run: (data, cavity) -> distribution
           Method to produce an approximation to the tilted distribution.
           Returns the _site_ approximation, not the whole likihood
    """
    def __init__(self, api: WorkerAPI, f_run: Callable[[Iterable, State], OrderedDict]):
        self.api = api
        self.f_run = f_run
        self.shared_variables = self.api.get_site_cavity().variables

    def run(self, data):

        for _ in range(5):
            cavity = self.api.get_site_cavity()
            samples = self.f_run(data, cavity)
            tilted_approx = state_from_samples(samples, self.shared_variables)
            own_updated_state = tilted_approx / cavity
            self.api.set_worker_state(own_updated_state)
            yield own_updated_state
