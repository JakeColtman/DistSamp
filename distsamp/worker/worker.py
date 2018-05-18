from typing import Callable, Iterable

from distsamp.distributions import Distribution
from distsamp.state.state import State
from distsamp.api.redis import WorkerAPI


class Worker:
    """
    Encapsulates a site within the overall model
    Primarily focused on approximating the site distribution given the cavity provided by the Server


    Attributes
    ---------
    api: distsamp.worker.api.spark.WorkerAPI
                API to allow the worker to interact with the rest of the system
    f_run: (data, cavity) -> distribution
           Method to produce an approximation to the tilted distribution.
           Returns the _site_ approximation, not the whole likihood
    """
    def __init__(self, api: WorkerAPI, f_approximate_tilted: Callable[[Iterable, State], State], damping: float):
        self.api = api
        self.f_approximate_tilted = f_approximate_tilted
        self.damping = damping

    @staticmethod
    def updated_distribution(worker_distribution: Distribution, site_distribution: Distribution, damping: float):
        if site_distribution is None:
            return worker_distribution
        return (site_distribution * damping) * (worker_distribution * (1 - damping))

    @staticmethod
    def updated_state(worker_state: State, site_state: State, damping: float):
        if site_state is None:
            return worker_state
        variables = worker_state.variables
        return State({v: Worker.updated_distribution(worker_state[v], site_state[v], damping) for v in variables})

    def block_until_model_ready(self):
        cavity = self.api.get_site_cavity()
        while cavity is None:
            cavity = self.api.get_site_cavity()

    def run_iteration(self, data):

        self.block_until_model_ready()

        for _ in range(5):
            cavity = self.api.get_site_cavity()
            site_state = self.api.get_site_state()
            tilted_approx = self.f_approximate_tilted(data, cavity)
            worker_state = tilted_approx / cavity
            updated_state = self.updated_state(worker_state, site_state, self.damping)
            self.api.set_site_state(updated_state)
