from copy import copy
from typing import List

from distsamp.server.server import get_server_api, Server
from distsamp.worker.worker import Worker


class SparkData:

    def __init__(self, dataframe, partition_key, n_partitions, worker: Worker):
        self.dataframe = dataframe
        self.partition_key = partition_key
        self.worker = worker
        self.n_partitions = n_partitions

    def run(self):
        self.dataframe.partitionBy(self.partition_key, self.n_partitions).mapPartitions("DO SOMETHING")


class SparkModel:

    def __init__(self, model_name: str, data_list: List[SparkData]):
        self.model_name = model_name
        self.data_list = data_list
        server_api = get_server_api(model_name)
        self.server = Server(server_api)

    def run(self):
        self.server.run()
        for data in self.data_list:
            data.run()
