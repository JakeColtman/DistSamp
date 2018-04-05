import pickle

import redis

from distsamp.api.redis import ModelAPI
from distsamp.distributions.state import State
from distsamp.api.redis import register_named_worker
from distsamp.api.redis import get_server_api

POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)


def set_prior(model_name: str, state: State):
    prior_api = register_named_worker(model_name, "prior")
    prior_api.set_worker_state(state)


def unregister_model(model_name):
    r = redis.StrictRedis(connection_pool=POOL)
    for key in r.scan_iter("{}:*".format(model_name)):
        r.delete(key)


def serialize_model(model_name: str, m_api: ModelAPI) -> bytes:
    site_ids = m_api.server_api.get_site_ids()
    output_dict = {
                "settings": {"model_name": model_name},
                "shared": m_api.server_api.get_shared_state(),
                "sites": {site_id: m_api.site_apis[site_id].get_site_state() for site_id in site_ids},
                "cavities": {site_id: m_api.server_api.get_site_cavity(site_id) for site_id in site_ids}
              }
    return pickle.dumps(output_dict)


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
