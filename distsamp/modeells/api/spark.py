import os
import redis
import pandas as pd

from collections import namedtuple
from distsamp.server.expectationpropagation import ExpectationPropagationModel
from distsamp.server.api.spark import register_model, unregister_model
from multiprocessing import Process

POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
modelS = {}


def get_sqlContext():
    import findspark
    python_path = os.environ.get('PYSPARK_PYTHON', None)
    findspark.init(python_path=python_path)
    from pyspark.sql import SparkSession, SQLContext
    from pyspark import SparkConf
    conf = SparkConf()
    builder = SparkSession.builder.enableHiveSupport().config(conf=conf)
    session = builder.getOrCreate()
    _sc = session.sparkContext
    return SQLContext(_sc, sparkSession=session)


def run_job(sqlContext, model):
    def loop(data):
        model.run()

    sdf = sqlContext.createDataFrame(pd.DataFrame({"a": [1]})).rdd.repartition(1)
    sqlContext._sc.runJob(sdf, loop)


def add_model(sqlContext, model_name, prior):
    s_api = register_model(model_name, prior)
    model = ExpectationPropagationModel(s_api)
    modelS[model_name] = {"api": s_api, "process": Process(target=run_job, args=(sqlContext, model,))}


def get_model(model_name):
    return modelS[model_name]


def start_model(model_name):
    modelS[model_name]["process"].start()


def stop_model(model_name):
    modelS[model_name]["process"].terminate()


def clear_model(model_name):
    unregister_model(model_name)


ModelAPI = namedtuple("ModelAPI", ["add_model", "get_model", "start_model", "stop_model", "clear_model"])


def get_model_api(sqlContext=None):

    if sqlContext is None:
        sqlContext = get_sqlContext()

    return ModelAPI(lambda model_name, prior: add_model(sqlContext, model_name, prior),
                     lambda model_name: get_model(model_name),
                     lambda model_name: start_model(model_name),
                     lambda model_name: stop_model(model_name),
                     lambda model_name: clear_model(model_name))
