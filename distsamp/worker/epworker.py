
class EPWorker:

    def __init__(self, worker_api, f_run):
        self.api = worker_api
        self.f_run = f_run

    def run(self, data):
        for _ in range(5):
            cavity = self.api.get_worker_cavity()
            tilted_approx = self.f_run(data, cavity)
            own_updated_state = tilted_approx / cavity
            self.api.set_worker_state(own_updated_state)
            yield own_updated_state
