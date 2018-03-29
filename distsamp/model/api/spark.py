from collections import namedtuple
import redis
from typing import Mapping

from distsamp.distributions.state import State
from distsamp.server.api.spark import get_server_api
from distsamp.worker.api.spark import get_worker_api

POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)

ModelAPI = namedtuple("ModelAPI", ["server_api", "worker_apis"])


def get_model_api(model_name):
    s_api = get_server_api(model_name)
    w_ids = s_api.get_worker_ids()
    w_apis = {w_id: get_worker_api(model_name, w_id) for w_id in w_ids}
    return ModelAPI(s_api, w_apis)


def unregister_model(model_name):
    r = redis.StrictRedis(connection_pool=POOL)
    for key in r.scan_iter("{}:*".format(model_name)):
        r.delete(key)


def serialize_model(m_api: ModelAPI) -> Mapping[str, State]:
    output = dict()
    output["shared"] = m_api.server_api.get_shared_state()
    for w_id in m_api.worker_apis:
        output[w_id] = m_api.worker_apis[w_id].get_worker_cavity()
    return output


def restore_model(model_name: str, serialized_model: Mapping[str, State]) -> ModelAPI:
    from distsamp.worker.api.spark import register_named_worker
    from distsamp.server.api.spark import get_server_api

    s_api = get_server_api(model_name)

    w_apis = {}

    for key, value in serialized_model.items():
        if key == "shared":
            s_api.set_shared_state(value)
        else:
            w_apis[key] = register_named_worker(model_name, key)
            w_apis[key].set_worker_state(value)

    return s_api, w_apis
