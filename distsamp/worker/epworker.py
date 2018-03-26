
class EPWorker:

    def __init__(self, worker_api, f_run):
        self.api = worker_api
        self.f_run = f_run
        self.state = None

    def run(self, data):
        for _ in range(5):
            shared_state = self.api.get_shared_state()
            self.update_own_state()
            if self.state is None:
                cavity = shared_state
            else:
                cavity = shared_state / self.state
            updated_state = self.f_run(data, cavity)
            own_updated_state = updated_state / cavity
            self.api.set_worker_state(own_updated_state)
            yield own_updated_state

    def update_own_state(self):
        state_from_model = self.api.get_worker_state()
        if state_from_model is None:
            return
        else:
            self.state = state_from_model
