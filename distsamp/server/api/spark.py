from collections import namedtuple

import redis

from distsamp.distributions.state import deserialize_state


POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
SERVERS = {}


def get_worker_ids(server_name):
    r = redis.StrictRedis(connection_pool=POOL)
    worker_ids = r.smembers("{}:{}".format(server_name, "workers"))
    return [x.decode() for x in worker_ids]


def get_worker_state(server_name, worker_id):
    r = redis.StrictRedis(connection_pool=POOL)
    message = r.get("{}:worker:{}".format(server_name, worker_id))
    return deserialize_state(message)


def set_worker_cavity(server_name, worker_id, state):
    r = redis.StrictRedis(connection_pool=POOL)
    r.lpush("{}:cavity:{}".format(server_name, worker_id), state.serialize())


def set_shared_state(server_name, state):
    r = redis.StrictRedis(connection_pool=POOL)
    r.lpush("{}:shared".format(server_name), state.serialize())


def set_prior(server_name, state):
    r = redis.StrictRedis(connection_pool=POOL)
    r.set("{}:worker:{}".format(server_name, 0), state.serialize())


def get_shared_state(server_name):
    r = redis.StrictRedis(connection_pool=POOL)
    message = r.lindex("{}:{}".format(server_name, "shared"), 0)
    return deserialize_state(message)


ServerAPI = namedtuple("ServerAPI", ["get_worker_ids", "get_worker_state", "set_worker_cavity", "get_shared_state", "set_shared_state"])


def get_server_api(server_name):
    return ServerAPI(lambda: get_worker_ids(server_name),
                     lambda worker_id: get_worker_state(server_name, worker_id),
                     lambda worker_id, state: set_worker_cavity(server_name, worker_id, state),
                     lambda: get_shared_state(server_name),
                     lambda state: set_shared_state(server_name, state))
