from distsamp.distributions.gaussian import cavity_distribution


def cavity_state(shared_state, own_state):
    cavity = {}
    for key in shared_state.keys():
        try:
            cavity[key] = cavity_distribution(shared_state[key], own_state[key])
        except:
            cavity[key] = shared_state[key]
    return cavity


class EPWorker:

    def __init__(self, worker_api, f_run):
        self.api = worker_api
        self.f_run = f_run

    def run(self, data):
        for _ in range(5):
            shared_state = self.api.get_shared_state()
            own_state = self.api.get_worker_state()
            cavity = cavity_state(shared_state, own_state)
            updated_state = self.f_run(data, cavity)
            own_updated_state = cavity_state(updated_state, cavity)
            self.api.set_worker_state(own_updated_state)
            yield own_updated_state
