from multiprocessing import Pool, Process

from typing import Any, Callable

from distsamp.api.redis import get_server_api
from distsamp.server.server import Server
from distsamp.model.model import Data, Model


class LocalData(Data):

    @staticmethod
    def run_partition(f_site, dataframe):
        f_site(dataframe).run(dataframe)

    def run_iteration(self):
        partition_values = self.dataframe[self.partition_key].unique()
        partition_dataframes = [self.dataframe[self.dataframe[self.partition_key] == key] for key in partition_values]
        with Pool(len(partition_dataframes)) as p:
            arguments = zip([self.f_site for _ in range(self.n_partitions)], partition_dataframes)
            p.starmap(self.run_partition, arguments)


class LocalModel(Model):

    @staticmethod
    def run_server(model_name):
        server_api = get_server_api(model_name)
        server = Server(server_api)
        server.run()

    def run_iterations(self, n_iter=5):
        server_process = Process(target=self.run_server, args=(self.model_name,))
        server_process.start()

        for _ in range(n_iter):
            list([x.run_iteration() for x in self.data_list])
