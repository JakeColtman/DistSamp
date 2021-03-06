from collections import namedtuple

import redis

from distsamp.state.state import deserialize_state


POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)

SiteAPI = namedtuple("SiteAPI", ["get_site_state", "get_site_cavity", "set_site_state", "get_shared_state"])
ServerAPI = namedtuple("ServerAPI", ["get_site_ids", "get_site_state", "get_site_cavity", "set_site_cavity", "get_shared_state", "set_shared_state"])
ModelAPI = namedtuple("ModelAPI", ["server_api", "site_apis"])


def get_site_ids(model_name):
    r = redis.StrictRedis(connection_pool=POOL)
    site_ids = r.smembers("{}:{}".format(model_name, "sites"))
    return [x.decode() for x in site_ids]


def get_site_state(model_name, site_id, offset: int=0):
    r = redis.StrictRedis(connection_pool=POOL)
    message = r.lindex("{}:site:{}".format(model_name, site_id), offset)
    return deserialize_state(message)


def set_site_state(model_name, site_id, state):
    r = redis.StrictRedis(connection_pool=POOL)
    r.lpush("{}:site:{}".format(model_name, site_id), state.serialize())


def get_site_cavity(model_name, site_id, offset: int=0):
    r = redis.StrictRedis(connection_pool=POOL)
    message = r.lindex("{}:cavity:{}".format(model_name, site_id), offset)
    return deserialize_state(message)


def set_site_cavity(model_name, site_id, state):
    r = redis.StrictRedis(connection_pool=POOL)
    r.lpush("{}:cavity:{}".format(model_name, site_id), state.serialize())


def get_shared_state(model_name, offset: int=0):
    r = redis.StrictRedis(connection_pool=POOL)
    message = r.lindex("{}:{}".format(model_name, "shared"), offset)
    return deserialize_state(message)


def set_shared_state(model_name, state):
    r = redis.StrictRedis(connection_pool=POOL)
    r.lpush("{}:shared".format(model_name), state.serialize())


def get_server_api(model_name):
    return ServerAPI(lambda: get_site_ids(model_name),
                     lambda site_id, offset=0: get_site_state(model_name, site_id, offset),
                     lambda site_id, offset=0: get_site_cavity(model_name, site_id, offset),
                     lambda site_id, state: set_site_cavity(model_name, site_id, state),
                     lambda offset=0: get_shared_state(model_name, offset),
                     lambda state: set_shared_state(model_name, state))


def get_site_api(model_name, site_id):
    return SiteAPI(lambda offset=0: get_site_state(model_name, site_id, offset),
                   lambda offset=0: get_site_cavity(model_name, site_id, offset),
                   lambda state: set_site_state(model_name, site_id, state),
                   lambda: get_shared_state(model_name))


def get_model_api(model_name):
    s_api = get_server_api(model_name)
    site_ids = s_api.get_site_ids()
    site_apis = {site_id: get_site_api(model_name, site_id) for site_id in site_ids}
    return ModelAPI(s_api, site_apis)


def register_site(model_name):
    r = redis.StrictRedis(connection_pool=POOL)
    site_id = r.incr("{}:siteids".format(model_name), 1)
    r.sadd("{}:sites".format(model_name), str(site_id))
    return get_site_api(model_name, site_id)


def register_named_site(model_name: str, site_id: str):
    r = redis.StrictRedis(connection_pool=POOL)
    r.incr("{}:siteids".format(model_name), 1)
    r.sadd("{}:sites".format(model_name), site_id)
    return get_site_api(model_name, site_id)
