import redis

from distsamp.distributions.state import parse_state

from collections import namedtuple

POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)


def get_shared_state(model_name):
    r = redis.StrictRedis(connection_pool=POOL)
    return parse_state(r.get("{}:{}".format(model_name, "shared")).decode())


def get_worker_cavity(model_name, worker_id):
    r = redis.StrictRedis(connection_pool=POOL)
    message = r.lindex("{}:cavity:{}".format(model_name, worker_id), 0)
    if message is None:
        return get_shared_state(model_name)
    return parse_state(message.decode())


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
    r.sadd("{}:workers", str(worker_id))
    return get_worker_api(model_name, worker_id)


def register_named_worker(model_name: str, worker_id: str):
    r = redis.StrictRedis(connection_pool=POOL)
    r.incr("{}:workers".format(model_name), 1)
    r.sadd("{}:workers", worker_id)
    return get_worker_api(model_name, worker_id)
