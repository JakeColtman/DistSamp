
class TwoWayWorker:

    def __init__(self, worker_api, f_run):
        self.api = worker_api
        self.f_run = f_run

    def run(self, data):
        for _ in range(10):
            state = self.api.get_shared_state()
            updated_state = self.f_run(data, state)
            self.api.set_worker_state(updated_state)
