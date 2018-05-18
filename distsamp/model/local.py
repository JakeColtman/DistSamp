from multiprocessing import Pool, Process

from distsamp.api.redis import get_server_api
from distsamp.model.model import Model
from distsamp.server.server import Server


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

    def run_iterations(self, n_iter=5):
        server_api = get_server_api(self.model_name)
        server = Server(server_api)

        for _ in range(n_iter):
            for site in self.sites:
                site.run_iteration()
                server.run_step()
