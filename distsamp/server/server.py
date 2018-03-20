import abc


class Server:

    def __init__(self, server_api):
        self.api = server_api

    @abc.abstractmethod
    def updated_shared_state(self, worker_states):
        pass

    def run(self):
        print("Monitoring model")
        while True:
            worker_ids = self.api.get_worker_ids()
            worker_states = {w_id: self.api.get_worker_state(w_id) for w_id in worker_ids}
            updated_state = self.updated_shared_state(worker_states)
            self.api.set_shared_state(updated_state)
            for w_id, w_state in worker_states.items():
                self.api.set_worker_state(w_id, w_state)
