
class OneWayWorker:

    def __init__(self, worker_api, f_runner):
        self.api = worker_api
        self.f_runner = f_runner

    def run(self, data):
        runner = self.f_runner(data)
        runner.run_epoch()
        state = runner.get_state()
        self.api.set_worker_state(state)
