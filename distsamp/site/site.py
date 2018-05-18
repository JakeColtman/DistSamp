from typing import Any, Callable, Iterable

from distsamp.api.redis import SiteAPI
from distsamp.distributions import Distribution
from distsamp.state.state import State


class Site:
    """
    Encapsulates a site within the overall model
    Primarily focused on approximating the site distribution given the cavity provided by the Server


    Attributes
    ---------
    api: distsamp.site.api.spark.SiteAPI
                API to allow the site to interact with the rest of the system
    f_run: (data, cavity) -> distribution
           Method to produce an approximation to the tilted distribution.
           Returns the _site_ approximation, not the whole likihood
    """
    def __init__(self, api: SiteAPI, data: Any, f_approximate_tilted: Callable[[Iterable, State], State], damping: float):
        self.api = api
        self.f_approximate_tilted = f_approximate_tilted
        self.damping = damping
        self.data = data

    @staticmethod
    def updated_distribution(current_distribution: Distribution, new_distribution: Distribution, damping: float):
        if current_distribution is None:
            return new_distribution
        return (current_distribution * damping) * (new_distribution* (1 - damping))

    @staticmethod
    def updated_state(current_state: State, new_state: State, damping: float):
        if current_state is None:
            return current_state
        variables = current_state.variables
        return State({v: Site.updated_distribution(current_state[v], new_state[v], damping) for v in variables})

    def block_until_model_ready(self):
        cavity = self.api.get_site_cavity()
        while cavity is None:
            cavity = self.api.get_site_cavity()

    def run_iteration(self):

        self.block_until_model_ready()

        for _ in range(5):
            cavity = self.api.get_site_cavity()
            current_state = self.api.get_site_state()
            tilted_approx = self.f_approximate_tilted(self.data, cavity)
            new_state = tilted_approx / cavity
            updated_state = self.updated_state(current_state, new_state, self.damping)
            self.api.set_site_state(updated_state)
