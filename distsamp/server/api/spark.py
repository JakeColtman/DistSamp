from collections import namedtuple

import json
import redis

from distsamp.distributions.state import parse_state


POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
SERVERS = {}


def get_worker_ids(server_name):
    r = redis.StrictRedis(connection_pool=POOL)
    max_id = json.loads(r.get("{}:{}".format(server_name, "workers")))
    return range(0, max_id + 1)


def get_worker_state(server_name, worker_id):
    r = redis.StrictRedis(connection_pool=POOL)
    message = r.get("{}:worker:{}".format(server_name, worker_id))
    return parse_state(message)


def set_worker_cavity(server_name, worker_id, state):
    r = redis.StrictRedis(connection_pool=POOL)
    r.set("{}:cavity:{}".format(server_name, worker_id), str(state))


def set_shared_state(server_name, state):
    r = redis.StrictRedis(connection_pool=POOL)
    r.set("{}:shared".format(server_name), str(state))


def set_prior(server_name, state):
    r = redis.StrictRedis(connection_pool=POOL)
    r.set("{}:worker:{}".format(server_name, 0), str(state))


def get_shared_state(server_name):
    r = redis.StrictRedis(connection_pool=POOL)
    return parse_state(r.get("{}:{}".format(server_name, "shared")))


ServerAPI = namedtuple("ServerAPI", ["get_worker_ids", "get_worker_state", "set_worker_cavity", "get_shared_state", "set_shared_state"])


def get_server_api(server_name):
    return ServerAPI(lambda: get_worker_ids(server_name),
                     lambda worker_id: get_worker_state(server_name, worker_id),
                     lambda worker_id, state: set_worker_cavity(server_name, worker_id, state),
                     lambda: get_shared_state(server_name),
                     lambda state: set_shared_state(server_name, state))


def register_server(server_name, prior):
    r = redis.StrictRedis(connection_pool=POOL)
    r.set("{}:workers".format(server_name), 0)
    set_prior(server_name, prior)
    return get_server_api(server_name)


def connect_to_server(server_name):
    return get_server_api(server_name)


def unregister_server(server_name):
    r = redis.StrictRedis(connection_pool=POOL)
    for key in r.scan_iter("{}:*".format(server_name)):
        r.delete(key)
