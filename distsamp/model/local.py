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

    def run_iteration(self):
        self.ensure_server_running()
        print("Running iteration")
        with Pool(len(self.sites)) as p:
            serialized_sites = [s.serialize() for s in self.sites]
            p.map(self.run_site_iteration, serialized_sites)

    @staticmethod
    def run_site_iteration(serialized_site):
        import dill as pickle
        site = pickle.loads(serialized_site)
        site.run_iteration()


class SerialLocalModel(Model):

    def run_iteration(self):
        server_api = get_server_api(self.model_name)
        server = Server(server_api)
        server.run_step()

        for site in self.sites:
            site.run_iteration()

    def run_iterations(self, n_iter=5):
        for _ in range(n_iter):
            self.run_iteration()
