import pymc3 as pm


class PymcRunner:

    def __init__(self, model, data, settings):
        self.settings = settings
        self.data = data
        self.model = model
        self.trace = None

    def run_epoch(self):
        with self.model as model:
            self.trace = pm.sampling(self.settings["n_samples"])

    def result(self):
        return self.trace