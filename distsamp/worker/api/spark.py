import redis

from distsamp.distributions.state import parse_state

from collections import namedtuple

POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)


def get_shared_state(model_name):
    r = redis.StrictRedis(connection_pool=POOL)
    return parse_state(r.get("{}:{}".format(model_name, "shared")))


def get_worker_cavity(model_name, worker_id):
    r = redis.StrictRedis(connection_pool=POOL)
    message = r.get("{}:cavity:{}".format(model_name, worker_id))
    if message is None:
        return get_shared_state(model_name)
    return parse_state(message)


def set_worker_state(model_name, worker_id, state):
    r = redis.StrictRedis(connection_pool=POOL)
    r.set("{}:worker:{}".format(model_name, worker_id), str(state))


WorkerAPI = namedtuple("WorkerAPI", ["get_worker_cavity", "set_worker_state"])


def get_worker_api(model_name, worker_id):
    return WorkerAPI(lambda: get_worker_cavity(model_name, worker_id),
                     lambda state: set_worker_state(model_name, worker_id, state))


def register_worker(model_name):
    r = redis.StrictRedis(connection_pool=POOL)
    worker_id = r.incr("{}:workers".format(model_name), 1)
    return get_worker_api(model_name, worker_id)
