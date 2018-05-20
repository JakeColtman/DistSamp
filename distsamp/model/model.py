import pickle
from typing import Iterable

import redis

from distsamp.api.redis import get_model_api, get_server_api, ModelAPI, register_named_site
from distsamp.site.site import Site
from distsamp.state.state import State

POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)


class Model:
    """
    Represents the whole model
    Ties together multiple data sources into a coherent whole.
    In particular:
        * setting of prior
        * bringing together multiple data sources

    Parameters
    ---------
    model_name: str
           the name of the model - can be arbitrary str as long as it's consistent across all elements of the model
    prior: distsamp.state.state.State
           Prior distributions for all variables in the model
    sites: List[distsamp.site.site.Site]
           A list of sites used in the model.
           There's no requirement that this is either exhaustive or immutable although either makes running the model easier
    """

    def __init__(self, model_name: str, prior: State, sites: List[Site]):
        self.model_name = model_name
        self.prior = prior
        self.sites = sites
        self.model_api = get_model_api(model_name)
        self.set_prior(model_name, prior)
        self.running = False

    @staticmethod
    def set_prior(model_name: str, prior: State) -> None:
        prior_api = register_named_site(model_name, "prior")
        prior_api.set_site_state(prior)

    def run_iterations(self, n_iter:int =5):
        for _ in range(n_iter):
            self.run_iteration()

    def run_iteration(self):
        raise NotImplementedError("")

    def serialize(self) -> bytes:
        return pickle.dumps(self)

    def serialize_complete_model(self) -> bytes:
        site_ids = self.model_api.server_api.get_site_ids()
        output_dict = {
                    "settings": {"model_name": self.model_name},
                    "shared": self.model_api.server_api.get_shared_state(),
                    "sites": {site_id: self.model_api.site_apis[site_id].get_site_state() for site_id in site_ids},
                    "cavities": {site_id: self.model_api.server_api.get_site_cavity(site_id) for site_id in site_ids}
                  }
        return pickle.dumps(output_dict)

    @staticmethod
    def restore_model(serialized_model: bytes) -> ModelAPI:

        model_dict = pickle.loads(serialized_model)
        model_name = model_dict["settings"]["name"]

        s_api = get_server_api(model_name)
        s_api.set_shared_state(model_dict["shared"])

        site_apis = {}

        for site_id in model_dict["sites"]:
            site_api = register_named_site(model_name, site_id)
            site_api.set_site_state(model_dict["sites"][site_id])
            site_apis[site_id] = site_api
            s_api.set_site_cavity(site_id, model_dict["cavity"][site_id])

        return ModelAPI(s_api, site_apis)

    def is_converged(self, tolerance=0.1) -> bool:
        updated_state = self.model_api.server_api.get_shared_state()
        new_state = self.model_api.server_api.get_shared_state(offset=1)
        for variable in updated_state.variables:
            if updated_state[variable].distance_from(new_state[variable]) > tolerance:
                print("{} not converged".format(variable))
                return False
        else:
            return True

    def run_until_converged(self, tolerance: float=0.1) -> None:
        self.run_iterations(2)
        while not self.is_converged(tolerance):
            self.run_iteration()
