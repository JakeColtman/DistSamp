from functools import reduce
import operator
from typing import Mapping

from distsamp.api.redis import ServerAPI
from distsamp.state.state import State


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
    def updated_shared_state(site_states: Mapping[str, State]) -> State:
        site_states = [x for x in site_states.values() if x is not None]
        return reduce(operator.mul, site_states)

    def store_updated_state(self, updated_state: State, site_states: Mapping[str, State]) -> None:
        self.api.set_shared_state(updated_state)
        for s_id, site_state in site_states.items():
            if s_id == "prior":
                continue
            if site_state is None:
                self.api.set_site_cavity(s_id, updated_state)
            else:
                site_cavity = updated_state / site_state
                self.api.set_site_cavity(s_id, site_cavity)

    def set_new_site_cavities(self, updated_state: State) -> None:
        site_ids = self.api.get_site_ids()
        new_site_ids = {x for x in site_ids if self.api.get_site_cavity(x) is None}
        for s_id in new_site_ids:
            self.api.set_site_cavity(s_id, updated_state)

    def run_step(self) -> None:
        shared_state = self.api.get_shared_state()
        site_ids = self.api.get_site_ids()
        if len(site_ids) == 0:
            return

        site_states = {site_id: self.api.get_site_state(site_id) for site_id in site_ids}
        updated_state = self.updated_shared_state(site_states)

        if shared_state is None:
            self.store_updated_state(updated_state, site_states)
        elif updated_state == shared_state:
            self.set_new_site_cavities(updated_state)
        else:
            self.store_updated_state(updated_state, site_states)

    def run(self) -> None:
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
