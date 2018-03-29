from typing import Mapping

from distsamp.model.api.spark import ModelAPI
from distsamp.distributions.state import State


class Model:

    def __init__(self, api: ModelAPI):
        self.api = api

    def serialize(self) -> Mapping[str, State]:
        output = dict()
        output["shared"] = self.api.server_api.get_shared_state()
        for w_id in self.api.worker_apis:
            output[w_id] = self.api.worker_apis[w_id].get_worker_cavity()
        return output


def restore_model(model_name: str, serialized_model: Mapping[str, State]) -> Model:
    from distsamp.worker.api.spark import register_named_worker
    from distsamp.server.api.spark import register_server

    s_api = register_server(model_name)

    w_apis = {}

    for key, value in serialized_model.items():
        if key == "shared":
            s_api.set_shared_state(value)
        else:
            w_apis[key] = register_named_worker(model_name, key)
            w_apis[key].set_worker_state(value)

    m_api = ModelAPI(s_api, w_apis)
    return m_api
