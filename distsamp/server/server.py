from functools import reduce
import operator

from distsamp.server.api.spark import ServerAPI


class Server:
    """
    Encapsulates the posterior server, the component which combines the information from the sites together
    Responsible for:
        - Maintaining an approximation to the global likihood
        - Calculating the site cavities
    """

    def __init__(self, api: ServerAPI):
        self.api = api

    @staticmethod
    def updated_shared_state(worker_states):
        worker_states = [x for x in worker_states.values() if x is not None]

        if len(worker_states) == 0:
            return

        return reduce(operator.mul, worker_states)

    def store_updated_state(self, updated_state, worker_states):
        self.api.set_shared_state(updated_state)
        for w_id, w_state in worker_states.items():
            if w_id == "prior":
                continue
            if w_state is None:
                self.api.set_worker_cavity(w_id, updated_state)
            else:
                worker_cavity = updated_state / w_state
                self.api.set_worker_cavity(w_id, worker_cavity)

    def set_new_worker_cavities(self, updated_state):
        worker_ids = self.api.get_worker_ids()
        new_worker_ids = {x for x in worker_ids if self.api.get_worker_cavity(x) is None}
        for w_id in new_worker_ids:
            self.api.set_worker_cavity(w_id, updated_state)

    def run(self):
        print("Monitoring server")
        shared_state = self.api.get_shared_state()
        while True:
            worker_ids = self.api.get_worker_ids()
            worker_states = {w_id: self.api.get_worker_state(w_id) for w_id in worker_ids}
            updated_state = self.updated_shared_state(worker_states)
            if shared_state is not None and updated_state == shared_state:
                self.set_new_worker_cavities(updated_state)
                continue
            if updated_state is None:
                continue
            shared_state = updated_state
            self.store_updated_state(updated_state, worker_states)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Parse args")
    parser.add_argument("model_name", type=str)
    args = parser.parse_args()
    model_name = args.model_name

    from distsamp.server.api.spark import get_server_api

    server_api = get_server_api(model_name)

    server = Server(server_api)
    server.run()
