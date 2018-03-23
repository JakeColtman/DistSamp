import redis
import pandas as pd

from collections import namedtuple
from distsamp.model.expectationpropagation import ExpectationPropagationModel
from distsamp.model.api.spark import register_model, unregister_model
from multiprocessing import Process

POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
SERVERS = {}


def run_job(sqlContext, server):
    def loop():
        server.run()

    sdf = sqlContext.registerDataFrame(pd.DataFrame({"a": [1]}))
    sqlContext.runJob(sdf, loop)


def add_server(model_name, prior):
    s_api = register_model(model_name, prior)
    server = ExpectationPropagationModel(s_api)
    SERVERS[model_name] = {"api": s_api, "process": Process(target=run_job, args=(server,))}


def start_server(model_name):
    SERVERS[model_name]["process"].start()


def stop_server(model_name):
    SERVERS[model_name]["process"].terminate()


def clear_server(model_name):
    unregister_model(model_name)


ServerAPI = namedtuple("ServerAPI", ["add_server", "start_server", "stop_server", "clear_server"])


def get_server_api():
    return ServerAPI(add_server, start_server, stop_server, clear_server)
