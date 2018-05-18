from multiprocessing import Pool, Process

from typing import Any, Callable, Iterable

from distsamp.api.redis import get_server_api, register_site
from distsamp.model.model import Model
from distsamp.server.server import Server
from distsamp.site.site import Site
from distsamp.state.state import State


def sites_from_local_dataframe(model_name, dataframe: Any, partition_key: str, f_approximate_tilted: Callable[[Iterable, State], State], damping):
    partition_values = dataframe[partition_key].unique()
    partition_dataframes = [dataframe[dataframe[partition_key] == key] for key in partition_values]
    site_apis = [register_site(model_name) for _ in partition_values]
    return [Site(site_api, data, f_approximate_tilted, damping) for (site_api, data) in zip(partition_dataframes, site_apis)]


class LocalModel(Model):

    @staticmethod
    def f_run_server(model_name):
        server_api = get_server_api(model_name)
        server = Server(server_api)
        server.run()

    def ensure_server_running(self):
        if not self.running:
            server_process = Process(target=self.f_run_server, args=(self.model_name,))
            server_process.start()

    def run_iterations(self, n_iter=5):
        for _ in range(n_iter):

            with Pool(len(self.sites)) as p:
                p.map(lambda site: site.run_iteration(), self.sites)


class SerialLocalModel(Model):

    @staticmethod
    def f_run_server(model_name):
        server_api = get_server_api(model_name)
        server = Server(server_api)
        server.run()

    def ensure_server_running(self):
        if not self.running:
            server_process = Process(target=self.f_run_server, args=(self.model_name,))
            server_process.start()

    def run_iterations(self, n_iter=5):

        for _ in range(n_iter):
            list([site.run_iteration() for site in self.sites])
