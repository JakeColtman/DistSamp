from multiprocessing import Pool, Process

from typing import Any, Callable

from distsamp.api.redis import get_server_api
from distsamp.server.server import Server
from distsamp.worker.worker import Worker
from distsamp.model.model import Data, Model


class LocalData(Data):

    def __init__(self, dataframe, partition_key, n_partitions, f_worker: Callable[[Any], Worker]):
        self.dataframe = dataframe
        self.partition_key = partition_key
        self.f_worker = f_worker
        self.n_partitions = n_partitions

    @staticmethod
    def run_partition(f_worker, dataframe):
        f_worker(dataframe).run(dataframe)

    def run(self):
        partition_values = self.dataframe[self.partition_key].unique()
        partition_dataframes = [self.dataframe[self.dataframe[self.partition_key] == key] for key in partition_values]
        with Pool(len(partition_dataframes)) as p:
            arguments = zip([self.f_worker for _ in range(self.n_partitions)], partition_dataframes)
            p.starmap(self.run_partition, arguments)


class LocalModel(Model):

    @staticmethod
    def run_server(model_name):
        server_api = get_server_api(model_name)
        server = Server(server_api)
        server.run()

    def run(self):
        server_process = Process(target=self.run_server, args=(self.model_name,))
        server_process.start()

        for data in self.data_list:
            data.run()
