from functools import reduce
import operator

from distsamp.api.redis import ServerAPI


class Server:
    """
    Encapsulates the posterior server, the component which combines the information from the sites together
    Responsible for:
        - Maintaining an approximation to the global likihood
        - Calculating the site cavities
        - Handling new sites as they come online
    """

    def __init__(self, api: ServerAPI):
        self.api = api

    @staticmethod
    def updated_shared_state(site_states):
        site_states = [x for x in site_states.values() if x is not None]

        if len(site_states) == 0:
            return

        return reduce(operator.mul, site_states)

    def store_updated_state(self, updated_state, site_states):
        self.api.set_shared_state(updated_state)
        for w_id, w_state in site_states.items():
            if w_id == "prior":
                continue
            if w_state is None:
                self.api.set_site_cavity(w_id, updated_state)
            else:
                site_cavity = updated_state / w_state
                self.api.set_site_cavity(w_id, site_cavity)

    def set_new_site_cavities(self, updated_state):
        site_ids = self.api.get_site_ids()
        new_site_ids = {x for x in site_ids if self.api.get_site_cavity(x) is None}
        for w_id in new_site_ids:
            self.api.set_site_cavity(w_id, updated_state)

    def run_step(self):
        shared_state = self.api.get_shared_state()
        site_ids = self.api.get_site_ids()
        site_states = {site_id: self.api.get_site_state(site_id) for site_id in site_ids}
        updated_state = self.updated_shared_state(site_states)
        if updated_state is None:
            return
        if shared_state is None:
            self.store_updated_state(updated_state, site_states)
        elif updated_state == shared_state:
            self.set_new_site_cavities(updated_state)
        else:
            self.store_updated_state(updated_state, site_states)

    def run(self):
        print("Monitoring server")
        while True:
            self.run_step()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Parse args")
    parser.add_argument("model_name", type=str)
    args = parser.parse_args()
    model_name = args.model_name

    from distsamp.api.redis import get_server_api

    server_api = get_server_api(model_name)

    server = Server(server_api)
    server.run()
