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
        worker_states = {x for x in worker_states.values() if x is not None}

        if len(worker_states) == 0:
            return

        return reduce(operator.mul, worker_states)

    def run(self):
        print("Monitoring server")
        while True:
            worker_ids = self.api.get_worker_ids()
            worker_states = {w_id: self.api.get_worker_state(w_id) for w_id in worker_ids}
            updated_state = self.updated_shared_state(worker_states)
            self.api.set_shared_state(updated_state)
            for w_id, w_state in worker_states.items():
                if w_id == 0:
                    continue
                if w_state is None:
                    self.api.set_worker_cavity(w_id, updated_state)
                else:
                    worker_cavity = updated_state / w_state
                    self.api.set_worker_cavity(w_id, worker_cavity)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Parse args")
    parser.add_argument("model_name", type=str)
    args = parser.parse_args()
    model_name = args.model_name

    from distsamp.server.api.spark import register_server

    server_api = register_server(model_name)

    server = Server(server_api)
    server.run()
