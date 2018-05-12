from copy import copy
from multiprocessing import Pool
from typing import Any, Callable, List

from distsamp.server.server import get_server_api, Server
from distsamp.worker.worker import Worker


class LocalData:

    def __init__(self, dataframe, partition_key, n_partitions, f_worker: Callable[Any, Worker]):
        self.dataframe = dataframe
        self.partition_key = partition_key
        self.f_worker = f_worker
        self.n_partitions = n_partitions

    def run(self):

        partition_values = self.dataframe[self.partition_key].unique()

        partition_dataframes = [self.dataframe[self.dataframe[self.partition_key == key]] for key in partition_values]

        with Pool(len(partition_dataframes)) as p:
            p.map(lambda x: self.f_worker(x).run(x), partition_dataframes)


class LocalModel:

    def __init__(self, model_name: str, data_list: List[LocalData]):
        self.model_name = model_name
        self.data_list = data_list
        server_api = get_server_api(model_name)
        self.server = Server(server_api)

    def run(self):
        for data in self.data_list:
            data.run()
