import redis

from distsamp.distributions.state import deserialize_state

from collections import namedtuple

POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)

WorkerAPI = namedtuple("WorkerAPI", ["get_worker_state", "get_site_state", "get_site_cavity", "set_site_state", "get_shared_state"])
ServerAPI = namedtuple("ServerAPI", ["get_site_ids", "get_site_state", "get_site_cavity", "set_site_cavity", "get_shared_state", "set_shared_state"])
ModelAPI = namedtuple("ModelAPI", ["server_api", "site_apis"])


def get_site_ids(model_name):
    r = redis.StrictRedis(connection_pool=POOL)
    worker_ids = r.smembers("{}:{}".format(model_name, "sites"))
    return [x.decode() for x in worker_ids]


def get_worker_state(model_name, site_id):
    r = redis.StrictRedis(connection_pool=POOL)
    message = r.get("{}:worker:{}".format(model_name, site_id))
    return deserialize_state(message)


def set_worker_state(model_name, worker_id, state):
    r = redis.StrictRedis(connection_pool=POOL)
    r.set("{}:worker:{}".format(model_name, worker_id), state.serialize())


def get_site_state(model_name, site_id):
    r = redis.StrictRedis(connection_pool=POOL)
    message = r.get("{}:site:{}".format(model_name, site_id))
    return deserialize_state(message)


def set_site_state(model_name, site_id, state):
    r = redis.StrictRedis(connection_pool=POOL)
    r.lpush("{}:site:{}".format(model_name, site_id), state.serialize())


def get_site_cavity(model_name, worker_id):
    r = redis.StrictRedis(connection_pool=POOL)
    message = r.lindex("{}:cavity:{}".format(model_name, worker_id), 0)
    return deserialize_state(message)


def set_site_cavity(model_name, worker_id, state):
    r = redis.StrictRedis(connection_pool=POOL)
    r.lpush("{}:cavity:{}".format(model_name, worker_id), state.serialize())


def get_shared_state(model_name):
    r = redis.StrictRedis(connection_pool=POOL)
    return deserialize_state(r.get("{}:{}".format(model_name, "shared")))


def set_shared_state(model_name, state):
    r = redis.StrictRedis(connection_pool=POOL)
    r.lpush("{}:shared".format(model_name), state.serialize())


def get_server_api(model_name):
    return ServerAPI(lambda: get_site_ids(model_name),
                     lambda worker_id: get_site_state(model_name, worker_id),
                     lambda worker_id: get_site_cavity(model_name, worker_id),
                     lambda worker_id, state: set_site_cavity(model_name, worker_id, state),
                     lambda: get_shared_state(model_name),
                     lambda state: set_shared_state(model_name, state))


def get_worker_api(model_name, site_id):
    return WorkerAPI(lambda: get_worker_state(model_name, site_id),
                   lambda: get_site_state(model_name, site_id),
                   lambda: get_site_cavity(model_name, worker_id),
                   lambda state: set_site_state(model_name, site_id, state),
                   lambda: get_shared_state(model_name))


def get_model_api(model_name):
    s_api = get_server_api(model_name)
    site_ids = s_api.get_site_ids()
    site_apis = {} # {site_ids: get_site_api(model_name, site_id) for site_id in site_ids}
    return ModelAPI(s_api, site_apis)


def register_worker(model_name):
    r = redis.StrictRedis(connection_pool=POOL)
    worker_id = r.incr("{}:workerids".format(model_name), 1)
    r.sadd("{}:workers", str(worker_id))
    return get_worker_api(model_name, worker_id)


def register_named_worker(model_name: str, worker_id: str):
    r = redis.StrictRedis(connection_pool=POOL)
    r.incr("{}:workerids".format(model_name), 1)
    r.sadd("{}:workers".format(model_name), worker_id)
    return get_worker_api(model_name, worker_id)