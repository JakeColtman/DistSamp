import json
import redis
from collections import namedtuple

POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)


def get_worker_state(model_name, worker_id):
    r = redis.StrictRedis(connection_pool=POOL)
    message = r.get("{}:shared:{}".format(model_name, worker_id))
    if message is None:
        return None
    else:
        return json.loads(message)


def get_shared_state(model_name):
    r = redis.StrictRedis(connection_pool=POOL)
    message = r.get("{}:shared".format(model_name))
    if message is None:
        return None
    else:
        return json.loads(message)


def set_worker_state(model_name, worker_id, state):
    r = redis.StrictRedis(connection_pool=POOL)
    r.set("{}:worker:{}".format(model_name, worker_id), json.dumps(state))


WorkerAPI = namedtuple("WorkerAPI", ["get_worker_state", "get_shared_state", "set_worker_state"])


def get_worker_api(model_name, worker_id):
    return WorkerAPI(lambda: get_worker_state(model_name, worker_id),
                     lambda: get_shared_state(model_name),
                     lambda state: set_worker_state(model_name, worker_id, state))


def register_worker(model_name):
    r = redis.StrictRedis(connection_pool=POOL)
    worker_id = r.incr("{}:workers".format(model_name), 1)
    return get_worker_api(model_name, worker_id)
