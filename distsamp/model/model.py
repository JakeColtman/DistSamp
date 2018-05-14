import pickle
from typing import Any, Callable, Iterable

import redis

from distsamp.api.redis import ModelAPI
from distsamp.state.state import State
from distsamp.worker.worker import Worker
from distsamp.api.redis import get_model_api, get_server_api, register_named_worker

POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)


class Data:
    """
    Encapsulates a data source within the model
    Specifies how a data source should be converted into Workers

    Parameters
    ----------
    dataframe - the data source to use in the model
    partition_key - str - which column should be used to break up the dataframe into chunks
    n_partitions - int - the number of chunks to make
    f_worker - method to create a worker from a chunk

    """

    def __init__(self, dataframe: Any, partition_key: str, n_partitions: int, f_worker: Callable[[Any], Worker]):
        self.dataframe = dataframe
        self.partition_key = partition_key
        self.f_worker = f_worker
        self.n_partitions = n_partitions

    def run(self):
        raise NotImplementedError("")


class Model:
    """
        Represents the whole model
        Ties together multiple data sources into a coherent whole.
        In particular:
            * setting of prior
            * bringing together multiple data sources

        Parameters
        ----------
        model_name - the name of the model, will be used in all serialization
        prior - State - prior distributions for all variables in model
                        hard requirement that all variables be present
        data_list - all of the data sources to be used in the model
                    purely convenience, other data sources can be dynamically added during the model run

    """

    def __init__(self, model_name: str, prior: State, data_list: Iterable[Data]):
        self.model_name = model_name
        self.prior = prior
        self.data_list = data_list
        self.model_api = get_model_api(model_name)
        self.set_prior(model_name, prior)

    @staticmethod
    def set_prior(model_name: str, state: State):
        prior_api = register_named_worker(model_name, "prior")
        prior_api.set_site_state(state)

    def run(self):
        raise NotImplementedError("")

    def serialize(self):
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
            site_api = register_named_worker(model_name, site_id)
            site_api.set_site_state(model_dict["sites"][site_id])
            site_apis[site_id] = site_api
            s_api.set_site_cavity(site_id, model_dict["cavity"][site_id])

        return ModelAPI(s_api, site_apis)
