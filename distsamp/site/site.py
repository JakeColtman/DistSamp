from distsamp.api.redis import SiteAPI
from distsamp.distributions.distribution import Distribution
from distsamp.distributions.state import State


class Site:

    def __init__(self, site_api: SiteAPI, damping: float=0.02):
        self.api = site_api
        self.damping = damping

    @staticmethod
    def updated_distribution(worker_distribution: Distribution, site_distribution: Distribution, damping: float):
        updated_eta = damping * site_distribution.eta + (1 - damping) * worker_distribution.eta
        updated_llambda = damping * site_distribution.llambda + (1 - damping) * worker_distribution.llambda
        return Distribution(eta=updated_eta, llambda=updated_llambda)

    @staticmethod
    def updated_state(worker_state: State, site_state: State, damping: float):
        variables = worker_state.variables
        return State({v: Site.updated_distribution(worker_state[v], site_state[v], damping) for v in variables})

    def run(self):
        while True:
            worker_state = self.api.get_worker_state()
            site_site = self.api.get_site_state()
            updated_state = self.updated_state(worker_state, site_site)
            self.api.set_site_state(updated_state)
