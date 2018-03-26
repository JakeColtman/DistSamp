from collections import namedtuple

import json
import redis

from distsamp.distributions.state import parse_state


POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
SERVERS = {}


def get_worker_ids(model_name):
    r = redis.StrictRedis(connection_pool=POOL)
    max_id = json.loads(r.get("{}:{}".format(model_name, "workers")))
    return range(0, max_id + 1)


def get_worker_state(model_name, worker_id):
    r = redis.StrictRedis(connection_pool=POOL)
    message = r.get("{}:worker:{}".format(model_name, worker_id))
    return parse_state(message)


def set_worker_cavity(model_name, worker_id, state):
    r = redis.StrictRedis(connection_pool=POOL)
    r.set("{}:cavity:{}".format(model_name, worker_id), str(state))


def set_shared_state(model_name, state):
    r = redis.StrictRedis(connection_pool=POOL)
    r.set("{}:shared".format(model_name), str(state))


def set_prior(model_name, state):
    r = redis.StrictRedis(connection_pool=POOL)
    r.set("{}:worker:{}".format(model_name, 0), str(state))


def get_shared_state(model_name):
    r = redis.StrictRedis(connection_pool=POOL)
    return parse_state(r.get("{}:{}".format(model_name, "shared")))


ModelAPI = namedtuple("ModelAPI", ["get_worker_ids", "get_worker_state", "set_worker_cavity", "get_shared_state", "set_shared_state"])


def get_model_api(model_name):
    return ModelAPI(lambda: get_worker_ids(model_name),
                    lambda worker_id: get_worker_state(model_name, worker_id),
                    lambda worker_id, state: set_worker_cavity(model_name, worker_id, state),
                    lambda: get_shared_state(model_name),
                    lambda state: set_shared_state(model_name, state))


def register_model(model_name, prior):
    r = redis.StrictRedis(connection_pool=POOL)
    r.set("{}:workers".format(model_name), 0)
    set_prior(model_name, prior)
    return get_model_api(model_name)


def connect_to_model(model_name):
    return get_model_api(model_name)


def unregister_model(model_name):
    r = redis.StrictRedis(connection_pool=POOL)
    for key in r.scan_iter("{}:*".format(model_name)):
        r.delete(key)
