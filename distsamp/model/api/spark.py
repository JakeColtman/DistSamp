from collections import namedtuple
import redis

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
