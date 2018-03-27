
class Worker:
    """
    Encapsulates a site in the overall likihood function
    Handles the process of coordinating with the server and approximating the tilted distribution

    Attributes
    ---------
    worker_api: distsamp.worker.api.spark.WorkerAPI
                API to allow the worker to interact with the rest of the system
    f_run: (data, cavity) -> distribution
           Method to produce an approximation to the tilted distribution.
           Returns the _site_ approximation, not the whole likihood
    """
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
